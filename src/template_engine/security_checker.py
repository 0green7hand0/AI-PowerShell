"""
安全检查器模块

提供模板安全验证功能，检测危险命令、路径遍历攻击和网络访问。
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SecurityIssue:
    """安全问题"""
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'dangerous_command', 'path_traversal', 'network_access'
    message: str
    line_number: int = 0
    code_snippet: str = ""


@dataclass
class SecurityCheckResult:
    """安全检查结果"""
    is_safe: bool
    issues: List[SecurityIssue]
    
    def __bool__(self):
        return self.is_safe


class SecurityChecker:
    """模板安全检查器"""
    
    # 危险命令模式
    DANGEROUS_COMMANDS = {
        'critical': [
            r'Remove-Item\s+.*-Recurse.*-Force',  # 递归强制删除
            r'Format-Volume',  # 格式化卷
            r'Clear-Disk',  # 清除磁盘
            r'Remove-Partition',  # 删除分区
            r'Set-Partition',  # 修改分区
            r'Initialize-Disk',  # 初始化磁盘
            r'Stop-Computer',  # 关机
            r'Restart-Computer',  # 重启
            r'Disable-ComputerRestore',  # 禁用系统还原
            r'Remove-Computer',  # 从域中删除计算机
        ],
        'high': [
            r'Remove-Item\s+.*-Force',  # 强制删除
            r'Remove-Item\s+.*\$env:',  # 删除环境变量路径
            r'Remove-Item\s+.*C:\\Windows',  # 删除Windows目录
            r'Remove-Item\s+.*C:\\Program Files',  # 删除程序文件
            r'Set-ExecutionPolicy\s+Unrestricted',  # 设置不受限执行策略
            r'Invoke-Expression',  # 执行表达式（可能执行恶意代码）
            r'iex\s+',  # Invoke-Expression别名
            r'Invoke-Command\s+.*-ScriptBlock',  # 远程执行命令
            r'New-Service',  # 创建服务
            r'Set-Service',  # 修改服务
            r'Stop-Service\s+.*-Force',  # 强制停止服务
        ],
        'medium': [
            r'Remove-Item',  # 删除项
            r'Clear-Content',  # 清除内容
            r'Clear-RecycleBin\s+.*-Force',  # 清空回收站
            r'Disable-NetAdapter',  # 禁用网络适配器
            r'Set-NetFirewallProfile',  # 修改防火墙配置
            r'Set-MpPreference',  # 修改Windows Defender设置
            r'Add-MpPreference\s+.*-ExclusionPath',  # 添加排除路径
        ]
    }
    
    # 网络访问命令模式
    NETWORK_COMMANDS = {
        'high': [
            r'Invoke-WebRequest',  # Web请求
            r'Invoke-RestMethod',  # REST API调用
            r'wget\s+',  # wget别名
            r'curl\s+',  # curl别名
            r'Start-BitsTransfer',  # BITS传输
            r'New-WebServiceProxy',  # Web服务代理
            r'Send-MailMessage',  # 发送邮件
        ],
        'medium': [
            r'Test-Connection',  # Ping
            r'Test-NetConnection',  # 网络连接测试
            r'Resolve-DnsName',  # DNS解析
            r'New-NetFirewallRule',  # 创建防火墙规则
            r'Set-NetConnectionProfile',  # 设置网络连接配置
        ]
    }
    
    # 路径遍历模式
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\.[/\\]',  # ../或..\
        r'%\.\.%',  # URL编码的..
        r'\.\.%2[fF]',  # URL编码的../
        r'\.\.%5[cC]',  # URL编码的..\
    ]
    
    # 敏感路径模式
    SENSITIVE_PATHS = [
        r'C:\\Windows\\System32',
        r'C:\\Windows\\SysWOW64',
        r'\$env:SystemRoot',
        r'\$env:windir',
        r'C:\\Program Files',
        r'C:\\Program Files \(x86\)',
        r'HKLM:',  # 注册表HKEY_LOCAL_MACHINE
        r'HKCU:',  # 注册表HKEY_CURRENT_USER
    ]
    
    def __init__(self):
        """初始化安全检查器"""
        self.issues: List[SecurityIssue] = []
    
    def check_template(self, script_content: str) -> SecurityCheckResult:
        """
        执行完整的安全检查
        
        Args:
            script_content: 脚本内容
            
        Returns:
            SecurityCheckResult: 安全检查结果
        """
        self.issues = []
        
        # 检查危险命令
        self._check_dangerous_commands(script_content)
        
        # 检查网络访问
        self._check_network_access(script_content)
        
        # 检查路径安全
        self._check_path_security(script_content)
        
        # 判断是否安全（没有critical或high级别的问题）
        critical_issues = [
            issue for issue in self.issues 
            if issue.severity in ['critical', 'high']
        ]
        
        return SecurityCheckResult(
            is_safe=len(critical_issues) == 0,
            issues=self.issues
        )
    
    def check_dangerous_commands(self, script_content: str) -> List[SecurityIssue]:
        """
        检测危险命令模式
        
        Args:
            script_content: 脚本内容
            
        Returns:
            List[SecurityIssue]: 发现的安全问题列表
        """
        issues = []
        lines = script_content.split('\n')
        
        for severity, patterns in self.DANGEROUS_COMMANDS.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    # 跳过注释行
                    if line.strip().startswith('#'):
                        continue
                    
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(SecurityIssue(
                            severity=severity,
                            category='dangerous_command',
                            message=f"检测到危险命令: {pattern}",
                            line_number=line_num,
                            code_snippet=line.strip()
                        ))
        
        return issues
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        验证文件路径安全性
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[bool, str]: (是否安全, 错误消息)
        """
        # 检查路径遍历
        for pattern in self.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, file_path):
                return False, f"检测到路径遍历攻击模式: {pattern}"
        
        # 检查敏感路径
        for pattern in self.SENSITIVE_PATHS:
            if re.search(pattern, file_path, re.IGNORECASE):
                return False, f"访问敏感路径: {pattern}"
        
        # 检查绝对路径是否在允许的范围内
        try:
            # 规范化路径
            normalized = os.path.normpath(file_path)
            
            # 检查是否包含..
            if '..' in Path(normalized).parts:
                return False, "路径包含父目录引用(..)"
            
        except Exception as e:
            return False, f"路径验证失败: {str(e)}"
        
        return True, ""
    
    def check_network_access(self, script_content: str) -> List[SecurityIssue]:
        """
        检测网络访问命令
        
        Args:
            script_content: 脚本内容
            
        Returns:
            List[SecurityIssue]: 发现的安全问题列表
        """
        issues = []
        lines = script_content.split('\n')
        
        for severity, patterns in self.NETWORK_COMMANDS.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    # 跳过注释行
                    if line.strip().startswith('#'):
                        continue
                    
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(SecurityIssue(
                            severity=severity,
                            category='network_access',
                            message=f"检测到网络访问命令: {pattern}",
                            line_number=line_num,
                            code_snippet=line.strip()
                        ))
        
        return issues
    
    def _check_dangerous_commands(self, script_content: str):
        """内部方法：检查危险命令"""
        self.issues.extend(self.check_dangerous_commands(script_content))
    
    def _check_network_access(self, script_content: str):
        """内部方法：检查网络访问"""
        self.issues.extend(self.check_network_access(script_content))
    
    def _check_path_security(self, script_content: str):
        """内部方法：检查路径安全"""
        lines = script_content.split('\n')
        
        # 提取所有可能的路径
        path_patterns = [
            r'["\']([A-Za-z]:\\[^"\']+)["\']',  # Windows绝对路径
            r'["\'](\.\.[/\\][^"\']+)["\']',  # 相对路径
            r'-Path\s+["\']?([^"\'\s]+)["\']?',  # -Path参数
            r'-LiteralPath\s+["\']?([^"\'\s]+)["\']?',  # -LiteralPath参数
        ]
        
        for line_num, line in enumerate(lines, 1):
            # 跳过注释行
            if line.strip().startswith('#'):
                continue
            
            for pattern in path_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    path = match.group(1)
                    is_safe, error_msg = self.validate_file_path(path)
                    
                    if not is_safe:
                        self.issues.append(SecurityIssue(
                            severity='high',
                            category='path_traversal',
                            message=error_msg,
                            line_number=line_num,
                            code_snippet=line.strip()
                        ))
