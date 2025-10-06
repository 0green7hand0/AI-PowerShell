"""
错误检测模块

负责检测生成的 PowerShell 命令中的语法错误和常见问题，
并提供自动修正建议。
"""

import re
from typing import List, Tuple, Optional
from ..interfaces.base import Suggestion


class ErrorDetector:
    """错误检测器
    
    检测 PowerShell 命令中的常见错误并提供修正建议。
    """
    
    def __init__(self):
        """初始化错误检测器"""
        self.common_errors = self._load_common_errors()
        self.syntax_patterns = self._load_syntax_patterns()
    
    def has_errors(self, command: str) -> bool:
        """检查命令是否有错误
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 是否存在错误
        """
        if not command or not command.strip():
            return True
        
        errors = self.detect_errors(command)
        return len(errors) > 0
    
    def detect_errors(self, command: str) -> List[Tuple[str, str]]:
        """检测命令中的错误
        
        Args:
            command: PowerShell 命令
            
        Returns:
            List[Tuple[str, str]]: 错误列表，每项为 (错误类型, 错误描述)
        """
        errors = []
        
        # 1. 检查空命令
        if not command or not command.strip():
            errors.append(('empty', '命令为空'))
            return errors
        
        command = command.strip()
        
        # 2. 检查引号匹配
        if not self._check_quotes(command):
            errors.append(('quotes', '引号不匹配'))
        
        # 3. 检查括号匹配
        if not self._check_brackets(command):
            errors.append(('brackets', '括号不匹配'))
        
        # 4. 检查管道语法
        if not self._check_pipe_syntax(command):
            errors.append(('pipe', '管道语法错误'))
        
        # 5. 检查参数格式
        if not self._check_parameter_format(command):
            errors.append(('parameter', '参数格式错误'))
        
        # 6. 检查常见拼写错误
        spelling_errors = self._check_spelling(command)
        errors.extend(spelling_errors)
        
        return errors
    
    def fix(self, suggestion: Suggestion) -> Suggestion:
        """修正命令中的错误
        
        Args:
            suggestion: 原始建议
            
        Returns:
            Suggestion: 修正后的建议
        """
        command = suggestion.generated_command
        errors = self.detect_errors(command)
        
        if not errors:
            return suggestion
        
        # 尝试修正每个错误
        fixed_command = command
        for error_type, error_desc in errors:
            fixed_command = self._fix_error(fixed_command, error_type)
        
        # 如果修正后仍有错误，返回原建议
        if self.has_errors(fixed_command):
            return suggestion
        
        # 返回修正后的建议
        return Suggestion(
            original_input=suggestion.original_input,
            generated_command=fixed_command,
            confidence_score=suggestion.confidence_score * 0.9,  # 降低置信度
            explanation=f"{suggestion.explanation} (已自动修正)",
            alternatives=suggestion.alternatives,
            timestamp=suggestion.timestamp
        )
    
    def _check_quotes(self, command: str) -> bool:
        """检查引号是否匹配
        
        Args:
            command: 命令字符串
            
        Returns:
            bool: 引号是否匹配
        """
        single_quotes = command.count("'")
        double_quotes = command.count('"')
        
        return single_quotes % 2 == 0 and double_quotes % 2 == 0
    
    def _check_brackets(self, command: str) -> bool:
        """检查括号是否匹配
        
        Args:
            command: 命令字符串
            
        Returns:
            bool: 括号是否匹配
        """
        stack = []
        pairs = {'(': ')', '{': '}', '[': ']'}
        
        for char in command:
            if char in pairs.keys():
                stack.append(char)
            elif char in pairs.values():
                if not stack:
                    return False
                if pairs[stack[-1]] != char:
                    return False
                stack.pop()
        
        return len(stack) == 0
    
    def _check_pipe_syntax(self, command: str) -> bool:
        """检查管道语法
        
        Args:
            command: 命令字符串
            
        Returns:
            bool: 管道语法是否正确
        """
        # 检查管道符号前后是否有内容
        if '|' in command:
            parts = command.split('|')
            for part in parts:
                if not part.strip():
                    return False
        
        return True
    
    def _check_parameter_format(self, command: str) -> bool:
        """检查参数格式
        
        Args:
            command: 命令字符串
            
        Returns:
            bool: 参数格式是否正确
        """
        # 对于基本的 PowerShell cmdlet，不进行严格的参数检查
        # 只检查明显的错误格式
        
        # 查找所有参数
        params = re.findall(r'-\S+', command)
        
        for param in params:
            # 检查参数名是否有效 - 只检查明显错误
            # 如果参数后面跟着非字母数字字符（除了空格），可能是错误
            if re.match(r'-[^A-Za-z0-9]', param):
                return False
        
        return True
    
    def _check_spelling(self, command: str) -> List[Tuple[str, str]]:
        """检查常见拼写错误
        
        Args:
            command: 命令字符串
            
        Returns:
            List[Tuple[str, str]]: 拼写错误列表
        """
        errors = []
        
        # 只检查完整单词匹配，避免误报
        for wrong, correct in self.common_errors.items():
            # 使用单词边界匹配
            if re.search(r'\b' + re.escape(wrong) + r'\b', command):
                errors.append(('spelling', f'可能的拼写错误: {wrong} -> {correct}'))
        
        return errors
    
    def _fix_error(self, command: str, error_type: str) -> str:
        """修正特定类型的错误
        
        Args:
            command: 命令字符串
            error_type: 错误类型
            
        Returns:
            str: 修正后的命令
        """
        if error_type == 'quotes':
            return self._fix_quotes(command)
        elif error_type == 'brackets':
            return self._fix_brackets(command)
        elif error_type == 'pipe':
            return self._fix_pipe(command)
        elif error_type == 'spelling':
            return self._fix_spelling(command)
        
        return command
    
    def _fix_quotes(self, command: str) -> str:
        """修正引号问题
        
        Args:
            command: 命令字符串
            
        Returns:
            str: 修正后的命令
        """
        # 简单策略：如果单引号或双引号数量为奇数，在末尾添加一个
        if command.count("'") % 2 == 1:
            command += "'"
        if command.count('"') % 2 == 1:
            command += '"'
        
        return command
    
    def _fix_brackets(self, command: str) -> str:
        """修正括号问题
        
        Args:
            command: 命令字符串
            
        Returns:
            str: 修正后的命令
        """
        # 统计各类括号
        open_paren = command.count('(')
        close_paren = command.count(')')
        open_brace = command.count('{')
        close_brace = command.count('}')
        open_bracket = command.count('[')
        close_bracket = command.count(']')
        
        # 添加缺失的闭括号
        if open_paren > close_paren:
            command += ')' * (open_paren - close_paren)
        if open_brace > close_brace:
            command += '}' * (open_brace - close_brace)
        if open_bracket > close_bracket:
            command += ']' * (open_bracket - close_bracket)
        
        return command
    
    def _fix_pipe(self, command: str) -> str:
        """修正管道问题
        
        Args:
            command: 命令字符串
            
        Returns:
            str: 修正后的命令
        """
        # 移除空的管道段
        parts = [part.strip() for part in command.split('|')]
        parts = [part for part in parts if part]
        
        return ' | '.join(parts)
    
    def _fix_spelling(self, command: str) -> str:
        """修正拼写错误
        
        Args:
            command: 命令字符串
            
        Returns:
            str: 修正后的命令
        """
        fixed = command
        
        for wrong, correct in self.common_errors.items():
            fixed = fixed.replace(wrong, correct)
        
        return fixed
    
    def _load_common_errors(self) -> dict:
        """加载常见错误映射
        
        Returns:
            dict: 错误映射字典 {错误: 正确}
        """
        return {
            # 常见命令拼写错误
            'Get-Childs': 'Get-ChildItem',
            'Get-Child': 'Get-ChildItem',
            'Get-Dir': 'Get-ChildItem',
            'Get-Procs': 'Get-Process',
            'Get-Proc': 'Get-Process',
            'Get-Svc': 'Get-Service',
            
            # 参数拼写错误
            '-Recursive': '-Recurse',
            '-Forced': '-Force',
        }
    
    def _load_syntax_patterns(self) -> dict:
        """加载语法模式
        
        Returns:
            dict: 语法模式字典
        """
        return {
            'cmdlet': r'^[A-Z][a-z]+-[A-Z][a-z]+',
            'parameter': r'-[A-Z][a-zA-Z]*',
            'variable': r'\$[a-zA-Z_][a-zA-Z0-9_]*',
            'pipe': r'\s*\|\s*',
        }
    
    def suggest_improvements(self, command: str) -> List[str]:
        """建议命令改进
        
        Args:
            command: PowerShell 命令
            
        Returns:
            List[str]: 改进建议列表
        """
        suggestions = []
        
        # 建议添加错误处理
        if 'Remove-Item' in command and '-ErrorAction' not in command:
            suggestions.append('考虑添加 -ErrorAction 参数处理错误')
        
        # 建议添加确认
        if 'Remove-Item' in command and '-Confirm' not in command:
            suggestions.append('考虑添加 -Confirm 参数以确认删除操作')
        
        # 建议使用 -WhatIf 进行测试
        if any(cmd in command for cmd in ['Remove-Item', 'Move-Item', 'Set-']):
            if '-WhatIf' not in command:
                suggestions.append('可以使用 -WhatIf 参数预览操作结果')
        
        # 建议格式化输出
        if 'Get-' in command and 'Format-' not in command and '|' not in command:
            suggestions.append('可以使用 | Format-Table 或 | Format-List 格式化输出')
        
        return suggestions
