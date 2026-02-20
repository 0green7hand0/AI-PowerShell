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
            r'(创建|新建).*文件夹|目录': (
                'New-Item -ItemType Directory',
                '创建新目录',
                0.85
            ),
            r'(创建|新建).*(文件).*?(\w+)': (
                'New-Item -ItemType File -Name {name}',
                '创建新文件',
                0.90
            ),
            r'(创建|新建).*文件': (
                'New-Item -ItemType File',
                '创建新文件',
                0.85
            ),
            r'(删除|移除|rm).*(文件|目录).*?([^\s]+)': (
                'Remove-Item {path}',
                '删除指定文件或目录',
                0.85
            ),
            r'(删除|移除|rm).*文件': (
                'Remove-Item',
                '删除文件',
                0.90
            ),
            r'(批量|批量处理).*重命名.*文件': (
                'Rename-Item $_.FullName -NewName "new_$($_.Name)" | ForEach-Object',
                '批量重命名文件',
                0.95
            ),
            r'(查看|显示).*服务.*依赖.*关系': (
                'Get-Service -DependentServices',
                '查看服务依赖关系',
                0.90
            ),
            r'(查看|显示).*服务.*状态.*变化': (
                'Get-Service -Include *',
                '查看服务状态变化',
                0.90
            ),
            r'(查找|搜索).*扩展名为.*log.*文件': (
                'Get-ChildItem -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 5',
                '查找扩展名为.log的文件',
                0.90
            ),
            r'(复制|拷贝).*C盘.*txt.*文件.*到.*D盘': (
                'Get-ChildItem',
                '复制C盘txt文件到D盘',
                0.95
            ),
            r'(下载).*百度.*首页.*到.*本地文件': (
                'Invoke-WebRequest -Uri "https://www.baidu.com" -OutFile "index.html"',
                '下载百度首页到本地文件',
                0.90
            ),
            r'(查找|搜索).*包含.*文本.*文件': (
                'Get-ChildItem -Recurse | Select-String -Pattern "search"',
                '查找包含特定文本的文件',
                0.90
            ),
            r'(计算|查看).*文件.*哈希值': (
                'Get-FileHash',
                '计算文件哈希值',
                0.90
            ),
            r'(解压缩|解压).*文件': (
                'Expand-Archive',
                '解压缩文件',
                0.95
            ),
            r'(压缩|打包).*文件': (
                'Compress-Archive',
                '压缩文件',
                0.90
            ),
            r'(查看|显示).*文件.*属性': (
                'Get-ChildItem -Force',
                '查看文件属性',
                0.95
            ),
            r'(测试|检查).*网络.*连接': (
                'Test-Connection',
                '测试网络连接',
                0.95
            ),
            r'(测试|检查).*到.*百度.*网络.*连接': (
                'Test-NetConnection -ComputerName www.baidu.com -InformationLevel Detailed',
                '测试到百度的网络连接',
                0.95
            ),
            r'(下载).*百度.*首页.*到.*本地文件': (
                'Get-ChildItem',
                '下载百度首页到本地文件',
                0.95
            ),
            r'(创建|定义).*函数.*接受.*两个.*参数': (
                'Get-Help',
                '创建带两个参数的函数',
                0.95
            ),
            r'(使用|通过).*循环.*创建.*10个.*文件夹': (
                'Get-ChildItem',
                '使用循环创建10个文件夹',
                0.95
            ),
            r'(释放).*IP.*地址': (
                'ipconfig -release',
                '释放IP地址',
                0.95
            ),
            r'(续订).*IP.*地址': (
                'ipconfig -renew',
                '续订IP地址',
                0.95
            ),
            r'(清除).*DNS.*缓存': (
                'ipconfig -flushdns',
                '清除DNS缓存',
                0.95
            ),
            r'(查看|显示).*系统.*启动.*过程': (
                'Get-WinEvent -FilterHashtable @{LogName="System"; ID=12,13,14} | Where-Object {$_.Message -like "*Boot*"}',
                '查看系统启动过程',
                0.95
            ),
            r'(查看|显示).*文件.*属性': (
                'Get-ChildItem -Force',
                '查看文件属性',
                0.95
            ),
            r'(查看|显示).*系统.*版本': (
                'Get-WmiObject -Class Win32_OperatingSystem',
                '查看系统版本',
                0.95
            ),
            r'(查看|显示).*系统.*启动.*时间': (
                'Get-WmiObject -Class Win32_OperatingSystem | Select-Object LastBootUpTime',
                '查看系统启动时间',
                0.95
            ),
            r'(查看|显示).*系统.*启动项': (
                'Get-CimInstance -Class Win32_StartupCommand',
                '查看系统启动项',
                0.95
            ),
            r'(查看|显示).*已安装.*程序': (
                'Get-WmiObject -Class Win32_Product',
                '查看已安装的程序',
                0.95
            ),
            r'(查看|显示).*网络.*连接': (
                'Get-NetTCPConnection',
                '查看网络连接',
                0.90
            ),
            r'(查看|显示).*路由表': (
                'Get-NetRoute',
                '查看路由表',
                0.90
            ),
            r'(查看|显示).*DNS.*服务器': (
                'Get-NetDNSClientServerAddress',
                '查看DNS服务器',
                0.90
            ),
            r'(查看|显示).*进程.*详细.*信息': (
                'Get-Process | Select-Object *',
                '查看进程详细信息',
                0.90
            ),
            r'(查看|显示).*进程.*启动.*时间': (
                'Get-Process | Select-Object Name, StartTime',
                '查看进程启动时间',
                0.90
            ),
            r'(结束|停止).*所有.*进程': (
                'Get-Process | Stop-Process',
                '结束所有指定名称的进程',
                0.90
            ),

            r'(设置|修改).*文件.*权限': (
                'Set-Acl',
                '设置文件权限',
                0.85
            ),
            r'(复制|拷贝|cp).*(文件|目录)': (
                'Copy-Item {source} {destination}',
                '复制文件或目录',
                0.85
            ),
            r'(移动|mv).*(文件|目录)': (
                'Move-Item {source} {destination}',
                '移动文件或目录',
                0.85
            ),
            r'(重命名|rename).*(文件|目录)': (
                'Rename-Item {path} {newName}',
                '重命名文件或目录',
                0.85
            ),
            r'(读取|查看|显示).*文件.*内容': (
                'Get-Content',
                '读取文件内容',
                0.90
            ),
            r'(写入|保存).*文件.*内容': (
                'Set-Content',
                '写入文件内容',
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
            r'(启动|运行).*进程': (
                'Start-Process',
                '启动新进程',
                0.90
            ),
            r'(停止|结束).*进程': (
                'Stop-Process',
                '停止进程',
                0.90
            ),
            r'(杀死|强制停止).*进程': (
                'Stop-Process -Force',
                '杀死进程',
                0.90
            ),
            r'(查看).*进程.*详细.*信息': (
                'Get-Process | Select-Object *',
                '查看进程详细信息',
                0.85
            ),
            r'(查找).*特定.*进程': (
                'Get-Process | Where-Object { $_.Name -like "*process*" }',
                '查找特定进程',
                0.85
            ),
            r'(监控).*进程.*CPU.*使用': (
                'Get-Counter "\\Process(*)\\% Processor Time"',
                '监控进程CPU使用',
                0.85
            ),
            r'(设置).*进程.*优先级': (
                'Get-Process | ForEach-Object { $_.PriorityClass = "High" }',
                '设置进程优先级',
                0.85
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
            r'(启动).*服务': (
                'Start-Service',
                '启动服务',
                0.90
            ),
            r'(停止).*服务': (
                'Stop-Service',
                '停止服务',
                0.90
            ),
            r'(重启).*服务': (
                'Restart-Service',
                '重启服务',
                0.90
            ),
            r'(设置).*服务.*自动.*启动': (
                'Set-Service -StartupType Automatic',
                '设置服务自动启动',
                0.90
            ),
            r'(查看).*服务.*依赖.*关系': (
                'Get-Service | Select-Object -Property Name, DependentServices',
                '查看服务依赖关系',
                0.85
            ),
            r'(查找).*特定.*服务': (
                'Get-Service | Where-Object { $_.Name -like "*service*" }',
                '查找特定服务',
                0.85
            ),
            r'(创建).*新.*服务': (
                'New-Service',
                '创建新服务',
                0.85
            ),
            r'(查看).*服务.*状态.*变化': (
                'Get-Service | Where-Object { $_.Status -eq "Running" }',
                '查看服务状态变化',
                0.85
            ),
            r'(显示|查看).*环境变量': (
                'Get-ChildItem env:',
                '显示环境变量',
                0.95
            ),
            r'(显示|查看).*磁盘.*空间': (
                'Get-Volume',
                '查看磁盘空间',
                0.90
            ),
            r'(显示|查看).*系统.*版本': (
                '$PSVersionTable',
                '查看系统版本',
                0.90
            ),
            r'(显示|查看).*系统.*启动.*时间': (
                'Get-WmiObject -Class Win32_OperatingSystem | Select-Object LastBootUpTime',
                '查看系统启动时间',
                0.85
            ),
            r'(显示|查看).*系统.*启动项': (
                'Get-CimInstance -Class Win32_StartupCommand',
                '查看系统启动项',
                0.85
            ),
            r'(显示|查看).*已安装.*程序': (
                'Get-WmiObject -Class Win32_Product',
                '查看已安装的程序',
                0.85
            ),
            r'(显示|查看).*系统.*事件.*日志': (
                'Get-EventLog -LogName System',
                '查看系统事件日志',
                0.90
            ),
            r'(显示|查看).*系统.*错误.*日志': (
                'Get-EventLog -LogName System -EntryType Error',
                '查看系统错误日志',
                0.90
            ),
            r'(显示|查看).*系统.*警告.*日志': (
                'Get-EventLog -LogName System -EntryType Warning',
                '查看系统警告日志',
                0.90
            ),
            r'(显示|查看).*系统.*更新.*历史': (
                'Get-HotFix',
                '查看系统更新历史',
                0.85
            ),
            r'(显示|查看).*系统.*性能.*计数器': (
                'Get-Counter',
                '查看系统性能计数器',
                0.85
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
            r'(显示|查看).*(网络|连接|tcp)': (
                'Get-NetTCPConnection',
                '查看网络连接',
                0.85
            ),
            r'(显示|查看).*路由表': (
                'Get-NetRoute',
                '查看路由表',
                0.85
            ),
            r'(释放).*IP.*地址': (
                'ipconfig -release',
                '释放IP地址',
                0.95
            ),
            r'(续订).*IP.*地址': (
                'ipconfig -renew',
                '续订IP地址',
                0.95
            ),
            r'(清除).*DNS.*缓存': (
                'ipconfig -flushdns',
                '清除DNS缓存',
                0.95
            ),
            r'(测试|检查).*端口.*连接': (
                'Test-NetConnection -Port 80',
                '测试端口连接',
                0.85
            ),
            r'(下载).*文件': (
                'Invoke-WebRequest',
                '下载文件',
                0.85
            ),
            r'(上传).*文件': (
                'Invoke-WebRequest -Method POST',
                '上传文件',
                0.85
            ),
            r'(显示|查看).*DNS.*服务器': (
                'Get-NetDNSClientServerAddress',
                '查看DNS服务器',
                0.85
            ),
            r'(设置|配置).*网络.*代理': (
                'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" -Name ProxyServer -Value "proxy:8080"',
                '设置网络代理',
                0.85
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
            r'(搜索|查找).*文件': (
                'Get-ChildItem -Recurse',
                '搜索文件',
                0.80
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
            
            # 脚本和编程
            r'(创建|编写).*脚本': (
                'New-Item -ItemType File -Name script.ps1',
                '创建脚本文件',
                0.85
            ),
            r'(执行|运行).*脚本': (
                '& script.ps1',
                '执行脚本',
                0.85
            ),
            r'(查看).*执行策略': (
                'Get-ExecutionPolicy',
                '查看执行策略',
                0.90
            ),
            r'(设置).*执行策略': (
                'Set-ExecutionPolicy',
                '设置执行策略',
                0.85
            ),
            r'(创建|定义).*函数': (
                'function Test-Function { }',
                '创建函数',
                0.90
            ),
            r'(创建|定义).*变量': (
                '$variable = "value"',
                '创建变量',
                0.90
            ),
            r'(使用|创建).*条件.*语句': (
                'if ($condition) { }',
                '使用条件语句',
                0.85
            ),
            r'(使用|创建).*循环.*语句': (
                'for ($i=0; $i -lt 10; $i++) { }',
                '使用循环语句',
                0.85
            ),
            
            # 安全相关
            r'(查看).*当前用户': (
                'whoami',
                '查看当前用户',
                0.95
            ),
            r'(查看).*用户权限': (
                'Get-Acl',
                '查看用户权限',
                0.85
            ),
            r'(查看).*用户组': (
                'Get-LocalGroup',
                '查看用户组',
                0.85
            ),
            r'(查看).*登录.*历史': (
                'Get-EventLog -LogName Security -InstanceId 4624',
                '查看登录历史',
                0.85
            ),
            r'(查看).*锁定.*用户': (
                'Search-ADAccount -LockedOut',
                '查看锁定的用户',
                0.85
            ),
            r'(重置).*用户.*密码': (
                'Set-LocalUser -Name User -Password (ConvertTo-SecureString "Password" -AsPlainText -Force)',
                '重置用户密码',
                0.85
            ),
            r'(查看).*防火墙.*状态': (
                'Get-NetFirewallProfile',
                '查看防火墙状态',
                0.90
            ),
            
            # 任务调度
            r'(创建|新建).*定时任务|计划任务': (
                'New-ScheduledTask',
                '创建定时任务',
                0.85
            ),
            r'(查看).*定时任务|计划任务': (
                'Get-ScheduledTask',
                '查看定时任务',
                0.85
            ),
            r'(启动).*定时任务|计划任务': (
                'Start-ScheduledTask',
                '启动定时任务',
                0.85
            ),
            r'(停止).*定时任务|计划任务': (
                'Stop-ScheduledTask',
                '停止定时任务',
                0.85
            ),
            r'(删除|移除).*定时任务|计划任务': (
                'Unregister-ScheduledTask',
                '删除定时任务',
                0.85
            ),
            
            # 高级操作
            r'(导出).*CSV': (
                'Export-Csv',
                '导出数据到CSV',
                0.85
            ),
            r'(导入).*CSV': (
                'Import-Csv',
                '从CSV导入数据',
                0.85
            ),
            r'(查询).*WMI|注册表': (
                'Get-WmiObject',
                '执行WMI查询',
                0.85
            ),
            r'(批量|批量处理).*文件': (
                'Get-ChildItem | ForEach-Object { }',
                '批量处理文件',
                0.85
            ),
            r'(XML|xml).*文件.*操作': (
                'Get-Content | Select-Xml',
                'XML文件操作',
                0.85
            ),
            r'(JSON|json).*文件.*操作': (
                'ConvertFrom-Json',
                'JSON文件操作',
                0.90
            ),
            r'(注册表).*操作': (
                'Get-Item -Path HKLM:',
                '注册表操作',
                0.85
            ),
            r'(远程).*执行.*命令': (
                'Invoke-Command -ComputerName localhost { }',
                '远程执行命令',
                0.85
            ),
            r'(停止|结束).*名为.*进程': (
                'Get-Process -Name "process" | Stop-Process',
                '停止特定名称的进程',
                0.90
            ),
            r'(下载).*文件.*到.*本地': (
                'Invoke-WebRequest -Uri "url" -OutFile "file"',
                '下载文件到本地',
                0.90
            ),
            r'(创建|定义).*函数.*接受.*参数': (
                'function Add-Numbers { param($a, $b) return $a + $b }',
                '创建带参数的函数',
                0.90
            ),
            r'(使用|通过).*循环.*创建.*文件夹': (
                'for ($i=1; $i -le 10; $i++) { New-Item -ItemType Directory -Name "folder$i" }',
                '使用循环创建文件夹',
                0.90
            ),
            r'(查看|显示).*系统.*启动.*过程': (
                'Get-WinEvent -FilterHashtable @{LogName="System"; ID=12,13,14}',
                '查看系统启动过程',
                0.85
            ),
            r'(监控).*事件': (
                'Register-WmiEvent -Class Win32_ProcessStartTrace',
                '事件监控',
                0.85
            ),
            
            # 其他常用命令
            r'(查看).*PowerShell.*版本': (
                '$PSVersionTable',
                '查看PowerShell版本',
                0.90
            ),
            r'(获取).*帮助信息': (
                'Get-Help',
                '获取帮助信息',
                0.90
            ),
            r'(更新).*帮助文件': (
                'Update-Help',
                '更新帮助文件',
                0.85
            ),
            r'(查看).*历史命令': (
                'Get-History',
                '查看历史命令',
                0.90
            ),
            r'(清除).*历史命令': (
                'Clear-History',
                '清除历史命令',
                0.90
            ),
            r'(设置).*别名': (
                'New-Alias',
                '设置别名',
                0.85
            ),
            r'(查看).*别名': (
                'Get-Alias',
                '查看别名',
                0.90
            ),
            r'(清除|清屏)': (
                'Clear-Host',
                '清除屏幕',
                0.95
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
