"""
输出格式化模块

本模块实现命令输出的格式化功能，包括：
- 输出美化和着色
- 中文编码处理
- 输出截断和分页
- 表格格式化
- 错误信息格式化
"""

import re
from typing import Optional, List, Dict, Any
from ..interfaces.base import ExecutionResult, ExecutionStatus


class OutputFormatter:
    """输出格式化器类
    
    负责格式化命令执行结果，提供美化、着色、截断等功能。
    """
    
    def __init__(self, 
                 max_output_length: int = 5000,
                 enable_colors: bool = True,
                 truncate_long_lines: bool = True,
                 max_line_length: int = 200):
        """初始化输出格式化器
        
        Args:
            max_output_length: 最大输出长度，超过此长度将被截断
            enable_colors: 是否启用颜色输出
            truncate_long_lines: 是否截断过长的行
            max_line_length: 单行最大长度
        """
        self.max_output_length = max_output_length
        self.enable_colors = enable_colors
        self.truncate_long_lines = truncate_long_lines
        self.max_line_length = max_line_length
        
        # ANSI 颜色代码
        self.colors = {
            'reset': '\033[0m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'dim': '\033[2m',
        }
    
    def format_result(self, result: ExecutionResult) -> str:
        """格式化执行结果
        
        Args:
            result: 执行结果对象
            
        Returns:
            str: 格式化后的输出字符串
        """
        lines = []
        
        # 添加状态标题
        lines.append(self._format_status_header(result))
        lines.append("")
        
        # 添加命令信息
        lines.append(self._format_command_info(result))
        lines.append("")
        
        # 添加输出内容
        if result.has_output:
            lines.append(self._format_section_header("输出"))
            lines.append(self._format_output(result.output))
            lines.append("")
        
        # 添加错误信息
        if result.has_error:
            lines.append(self._format_section_header("错误"))
            lines.append(self._format_error(result.error))
            lines.append("")
        
        # 添加执行信息
        lines.append(self._format_execution_info(result))
        
        return "\n".join(lines)
    
    def _format_status_header(self, result: ExecutionResult) -> str:
        """格式化状态标题
        
        Args:
            result: 执行结果
            
        Returns:
            str: 格式化的状态标题
        """
        if result.status == ExecutionStatus.SUCCESS:
            icon = "✅"
            status_text = "执行成功"
            color = 'green'
        elif result.status == ExecutionStatus.FAILED:
            icon = "❌"
            status_text = "执行失败"
            color = 'red'
        elif result.status == ExecutionStatus.TIMEOUT:
            icon = "⏱️"
            status_text = "执行超时"
            color = 'yellow'
        elif result.status == ExecutionStatus.CANCELLED:
            icon = "🚫"
            status_text = "执行取消"
            color = 'yellow'
        else:
            icon = "❓"
            status_text = "未知状态"
            color = 'white'
        
        status_line = f"{icon} {status_text}"
        
        if self.enable_colors:
            return self._colorize(status_line, color, bold=True)
        return status_line
    
    def _format_command_info(self, result: ExecutionResult) -> str:
        """格式化命令信息
        
        Args:
            result: 执行结果
            
        Returns:
            str: 格式化的命令信息
        """
        command_text = f"📝 命令: {result.command}"
        
        if self.enable_colors:
            return self._colorize(command_text, 'cyan')
        return command_text
    
    def _format_section_header(self, title: str) -> str:
        """格式化章节标题
        
        Args:
            title: 标题文本
            
        Returns:
            str: 格式化的标题
        """
        header = f"{'─' * 10} {title} {'─' * 10}"
        
        if self.enable_colors:
            return self._colorize(header, 'blue', bold=True)
        return header
    
    def _format_output(self, output: str) -> str:
        """格式化标准输出
        
        Args:
            output: 原始输出
            
        Returns:
            str: 格式化的输出
        """
        # 清理输出
        cleaned = self._clean_output(output)
        
        # 截断过长的输出
        if len(cleaned) > self.max_output_length:
            cleaned = cleaned[:self.max_output_length]
            cleaned += f"\n\n... (输出已截断，总长度: {len(output)} 字符)"
        
        # 截断过长的行
        if self.truncate_long_lines:
            cleaned = self._truncate_long_lines(cleaned)
        
        return cleaned
    
    def _format_error(self, error: str) -> str:
        """格式化错误输出
        
        Args:
            error: 错误信息
            
        Returns:
            str: 格式化的错误信息
        """
        # 清理错误信息
        cleaned = self._clean_output(error)
        
        # 为错误信息添加颜色
        if self.enable_colors:
            cleaned = self._colorize(cleaned, 'red')
        
        return cleaned
    
    def _format_execution_info(self, result: ExecutionResult) -> str:
        """格式化执行信息
        
        Args:
            result: 执行结果
            
        Returns:
            str: 格式化的执行信息
        """
        info_lines = [
            f"⏱️  执行时间: {result.execution_time:.3f} 秒",
            f"🔢 返回码: {result.return_code}",
            f"🕐 时间戳: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        # 添加元数据信息
        if result.metadata:
            if 'powershell_version' in result.metadata:
                info_lines.append(f"🔧 PowerShell: {result.metadata['powershell_version']}")
            if 'platform' in result.metadata:
                info_lines.append(f"💻 平台: {result.metadata['platform']}")
        
        info_text = "\n".join(info_lines)
        
        if self.enable_colors:
            return self._colorize(info_text, 'dim')
        return info_text
    
    def _clean_output(self, text: str) -> str:
        """清理输出文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除多余的空白行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 移除行尾空白
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # 移除开头和结尾的空白
        text = text.strip()
        
        return text
    
    def _truncate_long_lines(self, text: str) -> str:
        """截断过长的行
        
        Args:
            text: 原始文本
            
        Returns:
            str: 截断后的文本
        """
        # 如果禁用了行截断，直接返回原文本
        if not self.truncate_long_lines:
            return text
        
        lines = text.split('\n')
        truncated_lines = []
        
        for line in lines:
            if len(line) > self.max_line_length:
                truncated_line = line[:self.max_line_length] + "... (行已截断)"
                truncated_lines.append(truncated_line)
            else:
                truncated_lines.append(line)
        
        return '\n'.join(truncated_lines)
    
    def _colorize(self, text: str, color: str, bold: bool = False) -> str:
        """为文本添加颜色
        
        Args:
            text: 原始文本
            color: 颜色名称
            bold: 是否加粗
            
        Returns:
            str: 带颜色的文本
        """
        if not self.enable_colors or color not in self.colors:
            return text
        
        color_code = self.colors[color]
        reset_code = self.colors['reset']
        
        if bold:
            color_code = self.colors['bold'] + color_code
        
        return f"{color_code}{text}{reset_code}"
    
    def format_simple(self, result: ExecutionResult) -> str:
        """简单格式化（仅输出内容）
        
        Args:
            result: 执行结果
            
        Returns:
            str: 简单格式化的输出
        """
        if result.success and result.has_output:
            return self._clean_output(result.output)
        elif result.has_error:
            return self._clean_output(result.error)
        else:
            return f"命令执行完成 (返回码: {result.return_code})"
    
    def format_json(self, result: ExecutionResult) -> Dict[str, Any]:
        """格式化为 JSON 格式
        
        Args:
            result: 执行结果
            
        Returns:
            Dict: JSON 格式的结果
        """
        return {
            'success': result.success,
            'command': result.command,
            'output': result.output,
            'error': result.error,
            'return_code': result.return_code,
            'execution_time': result.execution_time,
            'status': result.status.value,
            'timestamp': result.timestamp.isoformat(),
            'metadata': result.metadata
        }
    
    def format_table(self, data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
        """格式化为表格
        
        Args:
            data: 表格数据（字典列表）
            headers: 表头列表，如果为 None 则从数据中提取
            
        Returns:
            str: 格式化的表格
        """
        if not data:
            return "无数据"
        
        # 提取表头
        if headers is None:
            headers = list(data[0].keys())
        
        # 计算列宽
        col_widths = {}
        for header in headers:
            col_widths[header] = len(str(header))
            for row in data:
                if header in row:
                    col_widths[header] = max(col_widths[header], len(str(row[header])))
        
        # 构建表格
        lines = []
        
        # 表头
        header_line = " | ".join(str(h).ljust(col_widths[h]) for h in headers)
        lines.append(header_line)
        
        # 分隔线
        separator = "-+-".join("-" * col_widths[h] for h in headers)
        lines.append(separator)
        
        # 数据行
        for row in data:
            row_line = " | ".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers)
            lines.append(row_line)
        
        return "\n".join(lines)
    
    def format_list(self, items: List[str], numbered: bool = False) -> str:
        """格式化为列表
        
        Args:
            items: 列表项
            numbered: 是否使用编号
            
        Returns:
            str: 格式化的列表
        """
        if not items:
            return "无项目"
        
        lines = []
        for i, item in enumerate(items, 1):
            if numbered:
                lines.append(f"{i}. {item}")
            else:
                lines.append(f"• {item}")
        
        return "\n".join(lines)
    
    def strip_ansi_codes(self, text: str) -> str:
        """移除 ANSI 颜色代码
        
        Args:
            text: 包含 ANSI 代码的文本
            
        Returns:
            str: 移除 ANSI 代码后的文本
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def format_error_message(self, error: Exception, context: Optional[str] = None) -> str:
        """格式化异常错误信息
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            str: 格式化的错误信息
        """
        lines = [
            "❌ 发生错误",
            "",
            f"错误类型: {type(error).__name__}",
            f"错误信息: {str(error)}",
        ]
        
        if context:
            lines.append(f"上下文: {context}")
        
        error_text = "\n".join(lines)
        
        if self.enable_colors:
            return self._colorize(error_text, 'red')
        return error_text
