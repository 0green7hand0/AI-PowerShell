"""
命令白名单验证

实现第一层安全验证：检查命令是否在白名单中，识别危险命令模式。
"""

import re
from typing import List, Dict, Set
from src.interfaces.base import ValidationResult, RiskLevel


class CommandWhitelist:
    """命令白名单验证器
    
    负责检查命令的安全性，识别危险命令模式和安全命令前缀。
    """
    
    # 危险命令模式（正则表达式）
    DANGEROUS_PATTERNS = [
        # 文件系统危险操作
        (r"Remove-Item.*-Recurse.*-Force", "递归强制删除文件", RiskLevel.CRITICAL),
        (r"Remove-Item.*C:\\Windows", "删除系统目录", RiskLevel.CRITICAL),
        (r"Remove-Item.*C:\\Program Files", "删除程序目录", RiskLevel.CRITICAL),
        (r"Format-Volume", "格式化磁盘", RiskLevel.CRITICAL),
        (r"Clear-Disk", "清空磁盘", RiskLevel.CRITICAL),
        (r"Remove-Item.*\*.*-Recurse", "递归删除所有文件", RiskLevel.HIGH),
        
        # 系统控制
        (r"Stop-Computer", "关闭计算机", RiskLevel.HIGH),
        (r"Restart-Computer", "重启计算机", RiskLevel.HIGH),
        (r"Stop-Service.*-Force", "强制停止服务", RiskLevel.HIGH),
        (r"Disable-WindowsOptionalFeature", "禁用系统功能", RiskLevel.HIGH),
        
        # 注册表操作
        (r"Remove-Item.*HKLM:", "删除注册表项（系统级）", RiskLevel.HIGH),
        (r"Remove-ItemProperty.*HKLM:", "删除注册表值（系统级）", RiskLevel.HIGH),
        (r"Set-ItemProperty.*HKLM:.*-Force", "强制修改注册表（系统级）", RiskLevel.MEDIUM),
        
        # 网络和防火墙
        (r"Disable-NetAdapter", "禁用网络适配器", RiskLevel.HIGH),
        (r"Set-NetFirewallProfile.*-Enabled\s+False", "禁用防火墙", RiskLevel.HIGH),
        (r"New-NetFirewallRule.*-Action\s+Allow", "添加防火墙规则", RiskLevel.MEDIUM),
        
        # 进程和任务
        (r"Stop-Process.*-Force", "强制终止进程", RiskLevel.MEDIUM),
        (r"Stop-Process.*-Name\s+explorer", "终止资源管理器", RiskLevel.HIGH),
        (r"Stop-Process.*-Name\s+winlogon", "终止登录进程", RiskLevel.CRITICAL),
        
        # 用户和权限
        (r"Remove-LocalUser", "删除本地用户", RiskLevel.HIGH),
        (r"Disable-LocalUser", "禁用本地用户", RiskLevel.MEDIUM),
        (r"Add-LocalGroupMember.*Administrators", "添加管理员", RiskLevel.HIGH),
        
        # 脚本执行
        (r"Set-ExecutionPolicy.*Unrestricted", "设置脚本执行策略为无限制", RiskLevel.HIGH),
        (r"Invoke-Expression", "执行动态代码", RiskLevel.MEDIUM),
        (r"Invoke-Command.*-ScriptBlock", "远程执行脚本", RiskLevel.MEDIUM),
        
        # 数据下载和执行
        (r"Invoke-WebRequest.*\|\s*Invoke-Expression", "下载并执行代码", RiskLevel.CRITICAL),
        (r"wget.*\|\s*iex", "下载并执行代码（简写）", RiskLevel.CRITICAL),
        (r"curl.*\|\s*iex", "下载并执行代码（简写）", RiskLevel.CRITICAL),
        (r"Invoke-WebRequest.*-OutFile", "下载文件", RiskLevel.MEDIUM),
        (r"Start-Process.*powershell.*-ArgumentList.*-e", "执行编码命令", RiskLevel.HIGH),
        (r"powershell.*-ExecutionPolicy.*Bypass", "绕过执行策略", RiskLevel.HIGH),
        (r"powershell.*-ep.*bypass", "绕过执行策略", RiskLevel.HIGH),
    ]
    
    # 安全命令前缀（只读操作）
    SAFE_PREFIXES = [
        "Get-", "Show-", "Test-", "Find-", "Search-",
        "Select-", "Where-", "Sort-", "Group-", "Measure-",
        "Compare-", "Format-", "Out-", "ConvertTo-", "ConvertFrom-",
        "Export-", "Import-",  # 导入导出通常是安全的
        "Write-Host", "Write-Output", "echo",
    ]
    
    # 管道后的危险命令（即使前面是安全命令，管道后出现这些也是危险的）
    PIPELINE_DANGEROUS_COMMANDS = [
        "Stop-Process",
        "Remove-Item",
        "Stop-Service",
        "Restart-Service",
        "Stop-Computer",
        "Restart-Computer",
        "Disable-NetAdapter",
        "Clear-",
        "Format-Volume",
        "Set-ExecutionPolicy",
        "Invoke-Expression",
        "Invoke-Command",
    ]
    
    # 需要确认的命令前缀（修改操作）
    CONFIRMATION_PREFIXES = [
        "Set-", "New-", "Remove-", "Clear-", "Reset-",
        "Start-", "Stop-", "Restart-", "Enable-", "Disable-",
        "Add-", "Update-", "Install-", "Uninstall-",
        "Copy-", "Move-", "Rename-",
    ]
    
    def __init__(self, config: dict = None):
        """初始化白名单验证器
        
        Args:
            config: 配置字典，可包含：
                - whitelist_mode: "strict" 或 "permissive"
                - custom_dangerous_patterns: 自定义危险模式列表
                - custom_safe_commands: 自定义安全命令列表
                - safe_prefixes: 自定义安全前缀列表
        """
        self.config = config or {}
        self.whitelist_mode = self.config.get('whitelist_mode', 'strict')
        
        # 加载自定义规则
        self.custom_dangerous_patterns = self.config.get('custom_dangerous_patterns', [])
        # 兼容测试配置中的dangerous_patterns键
        if 'dangerous_patterns' in self.config:
            self.custom_dangerous_patterns.extend(self.config['dangerous_patterns'])
        self.custom_safe_commands = set(self.config.get('custom_safe_commands', []))
        # 加载自定义安全前缀
        self.custom_safe_prefixes = self.config.get('safe_prefixes', [])
        
        # 编译正则表达式以提高性能
        self._compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), desc, risk)
            for pattern, desc, risk in self.DANGEROUS_PATTERNS
        ]
        
        # 添加自定义危险模式
        for pattern in self.custom_dangerous_patterns:
            if isinstance(pattern, str):
                try:
                    # 处理转义序列问题
                    compiled_pattern = re.compile(pattern, re.IGNORECASE)
                    self._compiled_patterns.append(
                        (compiled_pattern, "自定义危险模式", RiskLevel.HIGH)
                    )
                except re.error as e:
                    # 如果正则表达式编译失败，跳过该模式
                    import logging
                    logging.warning(f"自定义危险模式编译失败: {pattern}, 错误: {e}")
    
    def validate(self, command: str) -> ValidationResult:
        """验证命令是否安全
        
        Args:
            command: 待验证的 PowerShell 命令
            
        Returns:
            ValidationResult: 验证结果
        """
        command = command.strip()
        
        # 检查是否在自定义安全命令列表中
        if command in self.custom_safe_commands:
            return ValidationResult(
                is_valid=True,
                risk_level=RiskLevel.SAFE,
                requires_confirmation=False
            )
        
        # 检查危险模式
        for pattern, description, risk_level in self._compiled_patterns:
            if pattern.search(command):
                return ValidationResult(
                    is_valid=False,
                    risk_level=risk_level,
                    blocked_reasons=[f"检测到危险命令: {description}"],
                    requires_confirmation=False
                )
        
        # 检查管道中是否有危险命令
        if '|' in command:
            parts = command.split('|')
            for part in parts:
                part = part.strip()
                for dangerous_cmd in self.PIPELINE_DANGEROUS_COMMANDS:
                    if part.startswith(dangerous_cmd):
                        return ValidationResult(
                            is_valid=True,
                            risk_level=RiskLevel.HIGH,
                            requires_confirmation=True,
                            warnings=[f"管道中包含危险命令: {dangerous_cmd}"]
                        )
        
        # 检查安全前缀
        if self._starts_with_safe_prefix(command):
            return ValidationResult(
                is_valid=True,
                risk_level=RiskLevel.SAFE,
                requires_confirmation=False
            )
        
        # 检查需要确认的前缀
        if self._starts_with_confirmation_prefix(command):
            return ValidationResult(
                is_valid=True,
                risk_level=RiskLevel.MEDIUM,
                requires_confirmation=True,
                warnings=["此命令会修改系统状态，建议仔细确认"]
            )
        
        # 严格模式：未知命令需要确认
        if self.whitelist_mode == 'strict':
            return ValidationResult(
                is_valid=True,
                risk_level=RiskLevel.LOW,
                requires_confirmation=True,
                warnings=["未识别的命令，建议确认后执行"]
            )
        
        # 宽松模式：允许执行
        return ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.LOW,
            requires_confirmation=False
        )
    
    def is_dangerous(self, command: str) -> bool:
        """判断命令是否危险
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 是否为危险命令
        """
        for pattern, _, risk_level in self._compiled_patterns:
            if pattern.search(command):
                return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        return False
    
    def get_risk_level(self, command: str) -> RiskLevel:
        """获取命令的风险等级
        
        Args:
            command: PowerShell 命令
            
        Returns:
            RiskLevel: 风险等级
        """
        # 检查危险模式
        for pattern, _, risk_level in self._compiled_patterns:
            if pattern.search(command):
                return risk_level
        
        # 检查安全前缀
        if self._starts_with_safe_prefix(command):
            return RiskLevel.SAFE
        
        # 检查需要确认的前缀
        if self._starts_with_confirmation_prefix(command):
            return RiskLevel.MEDIUM
        
        # 默认为低风险
        return RiskLevel.LOW
    
    def add_custom_rule(self, pattern: str, description: str = "", risk_level: RiskLevel = RiskLevel.HIGH):
        """添加自定义危险模式
        
        Args:
            pattern: 正则表达式模式
            description: 模式描述
            risk_level: 风险等级
        """
        compiled = re.compile(pattern, re.IGNORECASE)
        self._compiled_patterns.append((compiled, description or "自定义规则", risk_level))
    
    def add_safe_command(self, command: str):
        """添加自定义安全命令
        
        Args:
            command: 安全命令
        """
        self.custom_safe_commands.add(command)
    
    def _starts_with_safe_prefix(self, command: str) -> bool:
        """检查命令是否以安全前缀开头
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 是否以安全前缀开头
        """
        # 首先检查管道后是否有危险命令
        if '|' in command:
            # 分割管道，检查每个部分
            parts = command.split('|')
            for part in parts:
                part = part.strip()
                # 检查管道后的命令是否是危险的
                for dangerous_cmd in self.PIPELINE_DANGEROUS_COMMANDS:
                    if part.startswith(dangerous_cmd):
                        return False  # 管道后有危险命令，不是安全的
        
        # 检查硬编码的安全前缀
        if any(command.startswith(prefix) for prefix in self.SAFE_PREFIXES):
            return True
        # 检查配置文件中定义的安全前缀
        if any(command.startswith(prefix) for prefix in self.custom_safe_prefixes):
            return True
        return False
    
    def _starts_with_confirmation_prefix(self, command: str) -> bool:
        """检查命令是否以需要确认的前缀开头
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 是否以需要确认的前缀开头
        """
        return any(command.startswith(prefix) for prefix in self.CONFIRMATION_PREFIXES)
