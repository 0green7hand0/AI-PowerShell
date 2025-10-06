"""
安全引擎主类

实现三层安全验证机制：
1. 命令白名单验证
2. 权限检查
3. 沙箱执行（可选）
"""

from typing import Optional
from src.interfaces.base import (
    SecurityEngineInterface,
    ValidationResult,
    Context,
    RiskLevel
)


class SecurityEngine(SecurityEngineInterface):
    """安全引擎主类
    
    协调三层安全验证，确保命令执行的安全性。
    """
    
    def __init__(self, config: Optional[dict] = None):
        """初始化安全引擎
        
        Args:
            config: 安全配置字典，包含：
                - whitelist_mode: 白名单模式 ("strict" 或 "permissive")
                - require_confirmation: 是否需要用户确认
                - sandbox_enabled: 是否启用沙箱执行
        """
        self.config = config or {}
        
        # 延迟导入以避免循环依赖
        from src.security.whitelist import CommandWhitelist
        from src.security.permissions import PermissionChecker
        from src.security.sandbox import SandboxExecutor
        
        # 初始化三层验证组件
        self.whitelist = CommandWhitelist(self.config)
        self.permission_checker = PermissionChecker()
        self.sandbox = SandboxExecutor(self.config) if self.config.get('sandbox_enabled', False) else None
        
        # 配置选项
        self.require_confirmation = self.config.get('require_confirmation', True)
    
    def validate_command(self, command: str, context: Context) -> ValidationResult:
        """验证命令的安全性（三层验证）
        
        Args:
            command: 待验证的 PowerShell 命令
            context: 当前上下文信息
            
        Returns:
            ValidationResult: 包含验证结果和风险评估的对象
        """
        if not command or not command.strip():
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.SAFE,
                blocked_reasons=["命令为空"]
            )
        
        # 第一层：白名单验证
        whitelist_result = self.whitelist.validate(command)
        if not whitelist_result.is_valid:
            return whitelist_result
        
        # 第二层：权限检查
        requires_elevation = self.permission_checker.requires_admin(command)
        has_permission = self.permission_checker.check_current_permissions()
        
        # 如果需要管理员权限但当前没有
        if requires_elevation and not has_permission:
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.HIGH,
                blocked_reasons=["命令需要管理员权限，但当前用户权限不足"],
                requires_elevation=True
            )
        
        # 合并白名单结果和权限检查结果
        result = ValidationResult(
            is_valid=True,
            risk_level=whitelist_result.risk_level,
            blocked_reasons=[],
            requires_confirmation=self._should_confirm(whitelist_result.risk_level),
            requires_elevation=requires_elevation,
            warnings=whitelist_result.warnings
        )
        
        return result
    
    def check_permissions(self, command: str) -> bool:
        """检查命令所需的权限
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 当前用户是否有足够权限执行该命令
        """
        requires_admin = self.permission_checker.requires_admin(command)
        has_permission = self.permission_checker.check_current_permissions()
        
        # 如果不需要管理员权限，或者需要且拥有，则返回 True
        return not requires_admin or has_permission
    
    def is_dangerous_command(self, command: str) -> bool:
        """判断命令是否危险
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 命令是否被认为是危险的
        """
        return self.whitelist.is_dangerous(command)
    
    def get_user_confirmation(self, command: str, risk_level: RiskLevel) -> bool:
        """获取用户确认
        
        Args:
            command: 待执行的命令
            risk_level: 风险等级
            
        Returns:
            bool: 用户是否确认执行
        """
        risk_emoji = {
            RiskLevel.SAFE: "✅",
            RiskLevel.LOW: "ℹ️",
            RiskLevel.MEDIUM: "⚠️",
            RiskLevel.HIGH: "🚨",
            RiskLevel.CRITICAL: "💀"
        }
        
        risk_text = {
            RiskLevel.SAFE: "安全",
            RiskLevel.LOW: "低风险",
            RiskLevel.MEDIUM: "中等风险",
            RiskLevel.HIGH: "高风险",
            RiskLevel.CRITICAL: "严重风险"
        }
        
        print(f"\n{risk_emoji.get(risk_level, '❓')} 风险等级: {risk_text.get(risk_level, '未知')}")
        print(f"📝 待执行命令: {command}")
        
        response = input("🤔 是否执行此命令? (y/N): ").strip().lower()
        return response in ['y', 'yes', '是']
    
    def _should_confirm(self, risk_level: RiskLevel) -> bool:
        """判断是否需要用户确认
        
        Args:
            risk_level: 风险等级
            
        Returns:
            bool: 是否需要确认
        """
        # 如果配置要求所有命令都确认
        if self.require_confirmation:
            return True
        
        # 中等及以上风险需要确认
        return risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
