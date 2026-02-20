"""
自然语言翻译器

负责将中文自然语言转换为 PowerShell 命令。
使用规则匹配和 AI 模型的混合策略。
"""

import re
from typing import Dict, List, Optional, Tuple
from ..interfaces.base import Suggestion, Context


class NaturalLanguageTranslator:
    """自然语言翻译器
    
    使用规则匹配（快速路径）和 AI 模型（慢速路径）的混合策略。
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化翻译器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.rules = self._load_rules()
        self.command_templates = self._load_command_templates()
        self._ai_provider = None
    
    @property
    def ai_provider(self):
        """懒加载 AI 提供商"""
        if self._ai_provider is None and self.config.get('use_ai_provider', False):
            from .providers import get_provider
            provider_name = self.config.get('provider', 'local')
            self._ai_provider = get_provider(provider_name, self.config)
        return self._ai_provider
    
    def translate(self, text: str, context: Context) -> Suggestion:
        """翻译自然语言到 PowerShell 命令
        
        Args:
            text: 用户输入的自然语言
            context: 当前上下文
            
        Returns:
            Suggestion: 翻译建议
        """
        text = text.strip()
        
        # 检查是否是重新生成请求（带有反馈）
        print(f"[调试] context.feedback: {context.feedback}")
        print(f"[调试] context.feedback is not None: {context.feedback is not None}")
        if context.feedback is not None:
            print(f"[调试] context.feedback.get('feedback'): {context.feedback.get('feedback')}")
        is_regeneration = context.feedback is not None and context.feedback.get('feedback') == 'incorrect'
        print(f"[调试] is_regeneration: {is_regeneration}")
        
        if is_regeneration:
            print(f"[重新生成] 输入: {text}, 反馈: {context.feedback}")
            # 尝试使用不同的策略重新生成
            return self._regenerate_with_feedback(text, context)
        
        # 1. 尝试规则匹配（快速路径）
        rule_result = self._match_rules(text)
        if rule_result:
            command, explanation, confidence = rule_result
            print(f"[规则匹配] 命令: {command}, 置信度: {confidence}")
            return Suggestion(
                original_input=text,
                generated_command=command,
                confidence_score=confidence,
                explanation=explanation,
                alternatives=self._generate_alternatives(text, command)
            )
        
        # 2. 尝试使用 AI 模型（慢速路径）
        if self.ai_provider:
            try:
                print(f"[AI 翻译] 输入: {text}")
                return self.ai_provider.generate(text, context)
            except Exception as e:
                # AI 生成失败，记录错误并回退到基本翻译
                print(f"[AI 翻译失败] {e}")
        
        # 3. 回退到基本翻译
        return self._fallback_translation(text)
    
    def explain_command(self, command: str) -> str:
        """解释 PowerShell 命令
        
        Args:
            command: PowerShell 命令
            
        Returns:
            str: 命令解释
        """
        # 提取主命令
        main_cmd = command.split()[0] if command.split() else ""
        
        # 查找命令说明
        explanations = {
            'Get-ChildItem': '列出目录中的文件和文件夹',
            'Get-Location': '显示当前工作目录',
            'Get-Date': '获取当前日期和时间',
            'Get-Process': '列出正在运行的进程',
            'Get-Service': '列出系统服务',
            'Test-NetConnection': '测试网络连接',
            'Get-Content': '读取文件内容',
            'Set-Location': '更改当前目录',
            'Remove-Item': '删除文件或目录',
            'Copy-Item': '复制文件或目录',
            'Move-Item': '移动文件或目录',
            'New-Item': '创建新文件或目录',
        }
        
        base_explanation = explanations.get(main_cmd, f'执行 {main_cmd} 命令')
        
        # 添加参数说明
        if '|' in command:
            base_explanation += '，并通过管道处理结果'
        if 'Sort-Object' in command:
            base_explanation += '，按指定属性排序'
        if 'Select-Object' in command or 'Select ' in command:
            base_explanation += '，选择特定属性或数量'
        if 'Where-Object' in command or 'Where ' in command:
            base_explanation += '，过滤符合条件的项'
        
        return base_explanation
    
    def _load_rules(self) -> Dict[str, Tuple[str, str, float]]:
        """加载翻译规则
        
        Returns:
            Dict: 规则字典，键为正则表达式模式，值为 (命令模板, 解释, 置信度)
        """
        return {
            # 文件和目录操作 - 注意顺序很重要，更具体的规则应该在前面
            # 只匹配简单的盘符查询，复杂查询（如包含特定文件类型）让 AI 处理
            r'([a-zA-Z])盘有什么$': (
                'Get-ChildItem {drive}:\\',
                '列出指定盘符的文件和文件夹',
                0.95
            ),
            r'([a-zA-Z])盘有什么文件$': (
                'Get-ChildItem {drive}:\\',
                '列出指定盘符的文件和文件夹',
                0.95
            ),
            r'(显示|查看|列出)([a-zA-Z])盘$': (
                'Get-ChildItem {drive}:\\',
                '列出指定盘符的文件和文件夹',
                0.95
            ),
            r'(显示|查看|列出)([a-zA-Z])盘(文件|内容)$': (
                'Get-ChildItem {drive}:\\',
                '列出指定盘符的文件和文件夹',
                0.95
            ),
            r'(显示|查看).*(当前|现在).*(目录|位置|路径)': (
                'Get-Location',
                '显示当前工作目录',
                0.95
            ),
            r'^pwd$': (
                'Get-Location',
                '显示当前工作目录',
                0.95
            ),
            r'(显示|列出|查看|ls).*(文件|目录|内容)': (
                'Get-ChildItem',
                '列出当前目录的文件和文件夹',
                0.95
            ),
            r'(进入|切换|cd).*(目录|文件夹).*?([A-Za-z]:\\[^\s]+|[./][^\s]+|\w+)': (
                'Set-Location {path}',
                '切换到指定目录',
                0.90
            ),
            r'(创建|新建).*(文件夹|目录).*?(\w+)': (
                'New-Item -ItemType Directory -Name {name}',
                '创建新目录',
                0.90
            ),
            r'(删除|移除|rm).*(文件|目录).*?([^\s]+)': (
                'Remove-Item {path}',
                '删除指定文件或目录',
                0.85
            ),
            r'(复制|拷贝|cp).*(文件|目录)': (
                'Copy-Item {source} {destination}',
                '复制文件或目录',
                0.85
            ),
            
            # 系统信息
            r'(显示|查看|获取).*(时间|日期)': (
                'Get-Date',
                '获取当前日期和时间',
                0.95
            ),
            r'(当前|现在).*(内存|memory).*(占用|使用)': (
                'Get-Counter "\\Memory\\% Committed Bytes In Use"',
                '显示当前内存占用率',
                0.95
            ),
            r'(显示|查看).*(内存|memory).*(占用|使用)': (
                'Get-Counter "\\Memory\\Available MBytes"',
                '显示可用内存',
                0.90
            ),
            r'(显示|查看).*(CPU|处理器|cpu).*使用率.*最高.*(\d+)': (
                'Get-Process | Sort-Object CPU -Descending | Select-Object -First {count}',
                '显示CPU使用率最高的进程',
                0.90
            ),
            r'(显示|查看).*(CPU|处理器|cpu).*最高.*(\d+)': (
                'Get-Process | Sort-Object CPU -Descending | Select-Object -First {count}',
                '显示CPU使用率最高的进程',
                0.90
            ),
            r'(显示|查看).*(系统|电脑).*(信息|配置)': (
                'Get-ComputerInfo',
                '显示系统信息',
                0.90
            ),
            r'(显示|查看|列出).*(进程|任务)': (
                'Get-Process',
                '列出所有运行中的进程',
                0.95
            ),
            r'(显示|查看).*(内存|memory).*使用率.*最高.*?(\d+)': (
                'Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First {count}',
                '显示内存使用最多的进程',
                0.90
            ),
            r'(显示|查看|列出).*(服务|service)': (
                'Get-Service',
                '列出所有系统服务',
                0.95
            ),
            
            # 网络相关
            r'(当前|现在).*(网速|网络速度|下载速度|上传速度)': (
                'Get-NetAdapterStatistics | Select-Object Name, ReceivedBytes, SentBytes',
                '显示网络适配器统计信息',
                0.85
            ),
            r'(测试|检查).*(网速|网络速度)': (
                'Test-NetConnection -ComputerName www.baidu.com -InformationLevel Detailed',
                '测试网络连接速度',
                0.85
            ),
            r'(测试|检查|ping).*(网络|连接).*?([^\s]+)': (
                'Test-NetConnection {host}',
                '测试到指定主机的网络连接',
                0.90
            ),
            r'(显示|查看).*(IP|ip|网络).*(地址|配置)': (
                'Get-NetIPAddress',
                '显示网络IP地址配置',
                0.90
            ),
            r'(显示|查看).*(网卡|网络适配器)': (
                'Get-NetAdapter',
                '显示网络适配器信息',
                0.90
            ),
            
            # 文件内容操作
            r'(显示|查看|读取|cat).*(文件|内容).*?([^\s]+)': (
                'Get-Content {file}',
                '读取并显示文件内容',
                0.90
            ),
            r'(搜索|查找|grep).*文件.*?([^\s]+)': (
                'Select-String -Path {pattern} -Pattern {search}',
                '在文件中搜索指定内容',
                0.85
            ),
            
            # 文件大小查询
            r'([a-zA-Z])盘.*?([^\s]+).*?(占用|大小|空间)': (
                'Get-ChildItem {drive}:\\{name} -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum',
                '计算指定文件夹的总大小',
                0.90
            ),
            r'(查看|显示).*?([^\s]+).*?(占用|大小|空间)': (
                'Get-ChildItem {name} -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum',
                '计算指定文件夹的总大小',
                0.85
            ),
        }
    
    def _load_command_templates(self) -> Dict[str, str]:
        """加载命令模板
        
        Returns:
            Dict: 命令模板字典
        """
        return {
            'list_files': 'Get-ChildItem',
            'current_dir': 'Get-Location',
            'change_dir': 'Set-Location {path}',
            'get_date': 'Get-Date',
            'list_process': 'Get-Process',
            'list_service': 'Get-Service',
            'test_connection': 'Test-NetConnection {host}',
            'read_file': 'Get-Content {file}',
            'create_dir': 'New-Item -ItemType Directory -Name {name}',
            'remove_item': 'Remove-Item {path}',
            'copy_item': 'Copy-Item {source} {destination}',
        }
    
    def _match_rules(self, text: str) -> Optional[Tuple[str, str, float]]:
        """匹配翻译规则
        
        Args:
            text: 用户输入文本
            
        Returns:
            Optional[Tuple]: (命令, 解释, 置信度) 或 None
        """
        for pattern, (command_template, explanation, confidence) in self.rules.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 提取参数
                command = self._fill_template(command_template, match, text)
                return command, explanation, confidence
        
        return None
    
    def _fill_template(self, template: str, match: re.Match, text: str) -> str:
        """填充命令模板
        
        Args:
            template: 命令模板
            match: 正则匹配对象
            text: 原始文本
            
        Returns:
            str: 填充后的命令
        """
        command = template
        
        # 提取盘符参数
        if '{drive}' in template:
            drive = self._extract_drive(text, match)
            command = command.replace('{drive}', drive)
        
        # 提取路径参数
        if '{path}' in template:
            path = self._extract_path(text, match)
            command = command.replace('{path}', path)
        
        # 提取名称参数
        if '{name}' in template:
            name = self._extract_name(text, match)
            command = command.replace('{name}', name)
        
        # 提取数量参数
        if '{count}' in template:
            count = self._extract_count(text, match)
            command = command.replace('{count}', count)
        
        # 提取主机参数
        if '{host}' in template:
            host = self._extract_host(text, match)
            command = command.replace('{host}', host)
        
        # 提取文件参数
        if '{file}' in template:
            file = self._extract_file(text, match)
            command = command.replace('{file}', file)
        
        return command
    
    def _extract_drive(self, text: str, match: re.Match) -> str:
        """从文本中提取盘符"""
        # 尝试从匹配组中提取
        groups = match.groups()
        for group in groups:
            if group and len(group) == 1 and group.isalpha():
                return group.upper()
        
        # 尝试查找盘符模式
        drive_match = re.search(r'([a-zA-Z])盘', text)
        if drive_match:
            return drive_match.group(1).upper()
        
        return 'C'
    
    def _extract_path(self, text: str, match: re.Match) -> str:
        """从文本中提取路径"""
        # 尝试从匹配组中提取
        groups = match.groups()
        for group in groups:
            if group and ('\\' in group or '/' in group or group.startswith('.')):
                return group
        
        # 尝试查找路径模式
        path_match = re.search(r'[A-Za-z]:\\[^\s]+|[./][^\s]+', text)
        if path_match:
            return path_match.group()
        
        return '.'
    
    def _extract_name(self, text: str, match: re.Match) -> str:
        """从文本中提取名称"""
        groups = match.groups()
        
        # 尝试从匹配组中提取名称（通常是第二个非盘符的组）
        for i, group in enumerate(groups):
            if group and len(group) > 1 and not group in ['显示', '查看', '列出', '占用', '大小', '空间', '有什么', '什么', '文件', '内容']:
                return group
        
        # 尝试从文本中提取文件夹名称（排除常见的动词和名词）
        import re
        # 移除盘符部分
        text_without_drive = re.sub(r'[a-zA-Z]盘', '', text)
        # 移除常见词汇
        text_clean = re.sub(r'(显示|查看|列出|占用|大小|空间|有什么|什么|文件|内容|多大)', '', text_without_drive)
        # 提取剩余的有意义的词
        words = text_clean.strip().split()
        if words:
            return words[0]
        
        return '*'
    
    def _extract_count(self, text: str, match: re.Match) -> str:
        """从文本中提取数量"""
        # 查找数字
        number_match = re.search(r'\d+', text)
        if number_match:
            return number_match.group()
        return '5'
    
    def _extract_host(self, text: str, match: re.Match) -> str:
        """从文本中提取主机名或IP"""
        # 查找IP地址或域名
        ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', text)
        if ip_match:
            return ip_match.group()
        
        domain_match = re.search(r'[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}', text)
        if domain_match:
            return domain_match.group()
        
        return 'localhost'
    
    def _extract_file(self, text: str, match: re.Match) -> str:
        """从文本中提取文件名"""
        # 查找文件路径
        file_match = re.search(r'[^\s]+\.[a-zA-Z0-9]+', text)
        if file_match:
            return file_match.group()
        
        return '*.*'
    
    def _generate_alternatives(self, text: str, primary_command: str) -> List[str]:
        """生成备选命令
        
        Args:
            text: 用户输入
            primary_command: 主要命令
            
        Returns:
            List[str]: 备选命令列表
        """
        alternatives = []
        
        # 基于主命令生成变体
        if 'Get-ChildItem' in primary_command:
            alternatives.append('Get-ChildItem -Recurse')
            alternatives.append('Get-ChildItem | Format-Table')
        elif 'Get-Process' in primary_command:
            alternatives.append('Get-Process | Format-Table Name, CPU, WorkingSet')
            alternatives.append('Get-Process | Where-Object {$_.CPU -gt 10}')
        
        return alternatives[:3]  # 最多返回3个备选
    
    def _fallback_translation(self, text: str) -> Suggestion:
        """回退翻译策略
        
        当规则匹配和 AI 模型都不可用时使用。
        
        Args:
            text: 用户输入
            
        Returns:
            Suggestion: 基本的翻译建议
        """
        # 简单的关键词匹配
        if any(word in text for word in ['文件', '目录', '列出', '显示']):
            command = 'Get-ChildItem'
            explanation = '列出当前目录的文件和文件夹'
            confidence = 0.60
        elif any(word in text for word in ['进程', '任务']):
            command = 'Get-Process'
            explanation = '列出所有运行中的进程'
            confidence = 0.60
        elif any(word in text for word in ['时间', '日期']):
            command = 'Get-Date'
            explanation = '获取当前日期和时间'
            confidence = 0.60
        else:
            command = 'Get-Help'
            explanation = '无法识别命令，显示帮助信息'
            confidence = 0.30
        
        return Suggestion(
            original_input=text,
            generated_command=command,
            confidence_score=confidence,
            explanation=explanation,
            alternatives=[]
        )
    
    def _regenerate_with_feedback(self, text: str, context: Context) -> Suggestion:
        """根据反馈重新生成命令
        
        Args:
            text: 用户输入
            context: 包含反馈的上下文
            
        Returns:
            Suggestion: 重新生成的翻译建议
        """
        feedback = context.feedback
        previous_command = feedback.get('previousCommand', '') if feedback else ''
        
        print(f"[重新生成] 之前的命令: {previous_command}")
        
        # 根据用户输入和之前的命令，尝试生成更准确的命令
        # 这里使用更智能的规则匹配
        
        # 检查是否是"新建文件"相关的请求
        if '新建' in text or '创建' in text:
            if '文件' in text:
                # 提取文件名
                file_name = self._extract_file_name(text)
                if file_name:
                    command = f'New-Item -ItemType File -Path "{file_name}"'
                    explanation = f'创建新文件: {file_name}'
                    confidence = 0.90
                else:
                    command = 'New-Item -ItemType File'
                    explanation = '创建新文件'
                    confidence = 0.85
            elif '文件夹' in text or '目录' in text:
                dir_name = self._extract_dir_name(text)
                if dir_name:
                    command = f'New-Item -ItemType Directory -Path "{dir_name}"'
                    explanation = f'创建新目录: {dir_name}'
                    confidence = 0.90
                else:
                    command = 'New-Item -ItemType Directory'
                    explanation = '创建新目录'
                    confidence = 0.85
            else:
                command = 'New-Item'
                explanation = '创建新项目'
                confidence = 0.80
        
        # 检查是否是"C盘"相关的请求
        elif 'c盘' in text.lower() or 'C盘' in text:
            if '新建' in text or '创建' in text:
                file_name = self._extract_file_name(text)
                if file_name:
                    command = f'New-Item -ItemType File -Path "C:\\{file_name}"'
                    explanation = f'在C盘创建新文件: {file_name}'
                    confidence = 0.90
                else:
                    command = 'New-Item -ItemType File -Path "C:\\newfile.txt"'
                    explanation = '在C盘创建新文件'
                    confidence = 0.85
            else:
                command = 'Get-ChildItem C:\\'
                explanation = '列出C盘的文件和文件夹'
                confidence = 0.95
        
        # 检查是否是盘符相关的请求
        elif re.search(r'([a-zA-Z])盘', text):
            drive = self._extract_drive(text, None)
            if '新建' in text or '创建' in text:
                file_name = self._extract_file_name(text)
                if file_name:
                    command = f'New-Item -ItemType File -Path "{drive}:\\{file_name}"'
                    explanation = f'在{drive}盘创建新文件: {file_name}'
                    confidence = 0.90
                else:
                    command = f'New-Item -ItemType File -Path "{drive}:\\newfile.txt"'
                    explanation = f'在{drive}盘创建新文件'
                    confidence = 0.85
            else:
                command = f'Get-ChildItem {drive}:\\'
                explanation = f'列出{drive}盘的文件和文件夹'
                confidence = 0.95
        
        # 其他情况，尝试使用更智能的匹配
        else:
            # 尝试使用 AI 模型
            if self.ai_provider:
                try:
                    print(f"[AI 重新生成] 输入: {text}")
                    return self.ai_provider.generate(text, context)
                except Exception as e:
                    print(f"[AI 重新生成失败] {e}")
            
            # 回退到基本翻译
            return self._fallback_translation(text)
        
        print(f"[重新生成] 新命令: {command}, 置信度: {confidence}")
        
        return Suggestion(
            original_input=text,
            generated_command=command,
            confidence_score=confidence,
            explanation=explanation,
            alternatives=self._generate_alternatives(text, command)
        )
    
    def _extract_file_name(self, text: str) -> str:
        """从文本中提取文件名"""
        # 移除常见词汇
        text_clean = re.sub(r'(新建|创建|文件|在|盘|c|C)', '', text)
        # 提取剩余的有意义的词
        words = text_clean.strip().split()
        if words:
            file_name = words[0]
            # 如果没有扩展名，添加默认扩展名
            if '.' not in file_name:
                file_name += '.txt'
            return file_name
        return 'newfile.txt'
    
    def _extract_dir_name(self, text: str) -> str:
        """从文本中提取目录名"""
        # 移除常见词汇
        text_clean = re.sub(r'(新建|创建|文件夹|目录|在|盘|c|C)', '', text)
        # 提取剩余的有意义的词
        words = text_clean.strip().split()
        if words:
            return words[0]
        return 'newfolder'
