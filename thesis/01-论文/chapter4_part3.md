#### 4.5 安全设计

安全设计是系统的关键部分，本节详细说明三层安全机制的设计原理、危险命令识别算法、权限管理策略和沙箱隔离方案。

##### 4.5.1 三层安全机制详细设计

系统采用创新的三层安全机制，提供全面的安全保护。

**第一层：命令白名单验证**

第一层安全机制通过模式匹配识别危险命令，评估风险等级。

**设计原理**：

1. **危险模式库**：维护一个包含30+种危险命令模式的数据库
2. **正则表达式匹配**：使用正则表达式匹配命令中的危险模式
3. **风险评分**：根据匹配的模式计算风险分数
4. **风险等级分类**：将命令分为5个风险等级

**实现流程**：

```
输入命令
    ↓
遍历危险模式库
    ↓
正则表达式匹配
    ↓
计算风险分数
    ↓
确定风险等级
    ↓
生成警告信息
    ↓
返回验证结果
```

**风险评分算法**：

```python
def calculate_risk_score(command: str, patterns: List[DangerousPattern]) -> float:
    """
    计算命令的风险分数
    
    Args:
        command: PowerShell命令
        patterns: 危险模式列表
        
    Returns:
        float: 风险分数 (0.0-1.0)
    """
    score = 0.0
    matched_patterns = []
    
    for pattern in patterns:
        if re.search(pattern.regex, command, re.IGNORECASE):
            # 累加风险分数
            score += pattern.weight
            matched_patterns.append(pattern)
    
    # 检查命令组合（管道、分号等）
    if "|" in command:
        pipe_count = command.count("|")
        score += 0.05 * pipe_count  # 每个管道增加5%风险
    
    if ";" in command:
        semicolon_count = command.count(";")
        score += 0.1 * semicolon_count  # 每个分号增加10%风险
    
    # 检查命令长度（过长的命令可能是混淆攻击）
    if len(command) > 500:
        score += 0.2
    
    # 归一化到0-1范围
    score = min(score, 1.0)
    
    return score, matched_patterns
```

**风险等级映射**：

```python
def map_score_to_level(score: float) -> RiskLevel:
    """将风险分数映射到风险等级"""
    if score >= 0.9:
        return RiskLevel.CRITICAL
    elif score >= 0.7:
        return RiskLevel.HIGH
    elif score >= 0.4:
        return RiskLevel.MEDIUM
    elif score >= 0.1:
        return RiskLevel.LOW
    else:
        return RiskLevel.SAFE
```

**危险模式分类**：

| 类别 | 示例模式 | 风险权重 | 说明 |
|------|---------|---------|------|
| 删除操作 | `Remove-Item.*-Recurse.*-Force` | 0.8 | 递归强制删除 |
| 磁盘操作 | `Format-Volume`, `Clear-Disk` | 1.0 | 格式化磁盘 |
| 注册表修改 | `Set-ItemProperty.*HKLM:` | 0.7 | 修改系统注册表 |
| 网络下载执行 | `iwr.*\|.*iex` | 1.0 | 下载并执行代码 |
| 系统关机 | `Stop-Computer.*-Force` | 0.8 | 强制关机 |
| 用户管理 | `New-LocalUser`, `Remove-LocalUser` | 0.7 | 用户账户操作 |
| 权限提升 | `Add-LocalGroupMember.*Administrators` | 0.9 | 添加管理员 |
| 执行策略 | `Set-ExecutionPolicy.*Unrestricted` | 0.6 | 放宽执行策略 |

**第二层：动态权限检查**

第二层安全机制检查命令所需的权限，并在必要时请求权限提升。

**设计原理**：

1. **管理员命令识别**：识别需要管理员权限的命令
2. **当前权限检测**：检测当前进程的权限级别
3. **权限提升请求**：在需要时请求权限提升
4. **用户确认流程**：要求用户明确确认高风险操作

**权限检测实现**：

```python
class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.admin_commands = self._load_admin_commands()
    
    def requires_admin(self, command: str) -> bool:
        """判断命令是否需要管理员权限"""
        # 提取命令的Cmdlet名称
        cmdlet = self._extract_cmdlet(command)
        
        # 检查是否在管理员命令列表中
        if cmdlet in self.admin_commands:
            return True
        
        # 检查特定参数（如-Force）
        if re.search(r'-Force\b', command):
            return True
        
        # 检查注册表路径
        if re.search(r'HKLM:', command):
            return True
        
        return False
    
    def check_permission(self, command: str) -> bool:
        """检查当前用户是否有执行命令的权限"""
        if not self.requires_admin(command):
            return True
        
        # 检查当前是否有管理员权限
        return self._is_admin()
    
    def _is_admin(self) -> bool:
        """检查当前进程是否有管理员权限"""
        if sys.platform == 'win32':
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:
            # Linux/macOS
            return os.geteuid() == 0
```

**用户确认流程设计**：

```python
class UserConfirmation:
    """用户确认流程"""
    
    def request_confirmation(
        self,
        suggestion: Suggestion,
        validation: ValidationResult
    ) -> bool:
        """
        请求用户确认
        
        Returns:
            bool: 用户是否确认执行
        """
        # 显示命令信息
        self._display_command_info(suggestion, validation)
        
        # 根据风险等级确定确认方式
        if validation.risk_level == RiskLevel.HIGH:
            return self._request_double_confirmation()
        elif validation.risk_level == RiskLevel.MEDIUM:
            return self._request_simple_confirmation()
        else:
            return True
    
    def _display_command_info(
        self,
        suggestion: Suggestion,
        validation: ValidationResult
    ):
        """显示命令信息"""
        print("\n" + "="*60)
        print("命令信息")
        print("="*60)
        print(f"原始输入: {suggestion.user_input}")
        print(f"生成命令: {suggestion.generated_command}")
        print(f"置信度: {suggestion.confidence_score:.2%}")
        print(f"风险等级: {validation.risk_level.name}")
        
        if validation.warnings:
            print("\n警告:")
            for warning in validation.warnings:
                print(f"  ⚠ {warning}")
        
        if validation.requires_admin:
            print("\n⚡ 此命令需要管理员权限")
        
        print("="*60 + "\n")
    
    def _request_simple_confirmation(self) -> bool:
        """简单确认"""
        while True:
            response = input("是否执行此命令? (y/n): ").strip().lower()
            if response in ['y', 'yes', '是', '确认']:
                return True
            elif response in ['n', 'no', '否', '取消']:
                return False
            else:
                print("请输入 y 或 n")
    
    def _request_double_confirmation(self) -> bool:
        """双重确认（用于高风险命令）"""
        print("⚠ 警告：此命令具有高风险！")
        
        # 第一次确认
        if not self._request_simple_confirmation():
            return False
        
        # 第二次确认
        print("\n请再次确认：")
        confirmation_text = "我确认执行"
        user_input = input(f"请输入 '{confirmation_text}' 以确认: ").strip()
        
        return user_input == confirmation_text
```

**第三层：沙箱隔离执行**

第三层安全机制提供可选的沙箱隔离执行环境，使用Docker容器技术。

**设计原理**：

1. **容器隔离**：在独立的Docker容器中执行命令
2. **资源限制**：限制容器的CPU、内存、网络等资源
3. **文件系统隔离**：容器与主系统的文件系统隔离
4. **自动清理**：执行完成后自动删除容器

**沙箱架构**：

```
┌─────────────────────────────────────────┐
│          主系统                          │
│  ┌───────────────────────────────────┐  │
│  │    AI PowerShell Assistant        │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐ │  │
│  │  │   Sandbox Executor          │ │  │
│  │  │                             │ │  │
│  │  │   Docker Client             │ │  │
│  │  └──────────┬──────────────────┘ │  │
│  └─────────────┼────────────────────┘  │
└────────────────┼───────────────────────┘
                 │ Docker API
                 ↓
┌─────────────────────────────────────────┐
│          Docker Engine                   │
│  ┌───────────────────────────────────┐  │
│  │   PowerShell Container            │  │
│  │                                   │  │
│  │   ┌───────────────────────────┐  │  │
│  │   │  PowerShell Core          │  │  │
│  │   │                           │  │  │
│  │   │  执行用户命令              │  │  │
│  │   │                           │  │  │
│  │   └───────────────────────────┘  │  │
│  │                                   │  │
│  │   资源限制:                       │  │
│  │   - CPU: 50%                     │  │
│  │   - Memory: 512MB                │  │
│  │   - Network: Disabled            │  │
│  │   - Filesystem: Isolated         │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**沙箱执行实现**：

```python
class SandboxExecutor:
    """沙箱执行器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.docker_client = docker.from_env()
        self._ensure_image_available()
    
    def execute_in_sandbox(
        self,
        command: str,
        timeout: int = None
    ) -> ExecutionResult:
        """
        在沙箱中执行命令
        
        Args:
            command: PowerShell命令
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        if timeout is None:
            timeout = self.config.sandbox_timeout
        
        start_time = time.time()
        
        try:
            # 创建并运行容器
            container = self.docker_client.containers.run(
                image=self.config.sandbox_image,
                command=["pwsh", "-Command", command],
                
                # 资源限制
                mem_limit=self.config.sandbox_memory_limit,
                cpu_quota=self.config.sandbox_cpu_quota,
                
                # 网络隔离
                network_disabled=True,
                
                # 文件系统
                read_only=True,
                tmpfs={'/tmp': 'size=100M'},
                
                # 安全选项
                security_opt=['no-new-privileges'],
                cap_drop=['ALL'],
                
                # 执行选项
                detach=True,
                remove=False  # 手动删除以获取日志
            )
            
            # 等待容器完成或超时
            try:
                result = container.wait(timeout=timeout)
                return_code = result['StatusCode']
                
                # 获取输出
                logs = container.logs(stdout=True, stderr=True)
                output = logs.decode('utf-8', errors='replace')
                
            except Exception as e:
                # 超时或其他错误
                container.kill()
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"沙箱执行失败: {str(e)}",
                    return_code=-1,
                    execution_time=time.time() - start_time
                )
            
            finally:
                # 清理容器
                try:
                    container.remove(force=True)
                except:
                    pass
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=(return_code == 0),
                output=output,
                error="",
                return_code=return_code,
                execution_time=execution_time
            )
            
        except docker.errors.ImageNotFound:
            return ExecutionResult(
                success=False,
                output="",
                error=f"沙箱镜像未找到: {self.config.sandbox_image}",
                return_code=-1,
                execution_time=0
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"沙箱执行错误: {str(e)}",
                return_code=-1,
                execution_time=time.time() - start_time
            )
    
    def _ensure_image_available(self):
        """确保沙箱镜像可用"""
        try:
            self.docker_client.images.get(self.config.sandbox_image)
        except docker.errors.ImageNotFound:
            # 自动拉取镜像
            print(f"正在拉取沙箱镜像: {self.config.sandbox_image}")
            self.docker_client.images.pull(self.config.sandbox_image)
```

##### 4.5.2 安全策略配置

系统提供灵活的安全策略配置，允许用户根据需求调整安全级别。

**安全策略级别**：

```python
class SecurityPolicy(Enum):
    """安全策略级别"""
    STRICT = "strict"       # 严格模式：拒绝所有中高风险命令
    BALANCED = "balanced"   # 平衡模式：中高风险命令需要确认
    PERMISSIVE = "permissive"  # 宽松模式：只拒绝严重风险命令
    DISABLED = "disabled"   # 禁用模式：不进行安全检查（不推荐）
```

**策略配置示例**：

```yaml
security:
  # 安全策略级别
  policy: "balanced"
  
  # 严格模式配置
  strict:
    block_levels: ["MEDIUM", "HIGH", "CRITICAL"]
    enable_sandbox: true
    require_double_confirmation: true
  
  # 平衡模式配置
  balanced:
    block_levels: ["CRITICAL"]
    require_confirmation_levels: ["MEDIUM", "HIGH"]
    enable_sandbox: false
    require_double_confirmation: false
  
  # 宽松模式配置
  permissive:
    block_levels: ["CRITICAL"]
    require_confirmation_levels: ["HIGH"]
    enable_sandbox: false
    require_double_confirmation: false
```

##### 4.5.3 审计日志设计

系统实现完整的审计日志功能，记录所有安全相关的操作。

**审计日志内容**：

```python
@dataclass
class AuditLogEntry:
    """审计日志条目"""
    
    timestamp: datetime         # 时间戳
    session_id: str            # 会话ID
    user_id: Optional[str]     # 用户ID
    event_type: str            # 事件类型
    command: str               # 执行的命令
    risk_level: RiskLevel      # 风险等级
    action_taken: str          # 采取的行动
    success: bool              # 是否成功
    details: Dict[str, Any]    # 详细信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "command": self.command,
            "risk_level": self.risk_level.name,
            "action_taken": self.action_taken,
            "success": self.success,
            "details": self.details
        }
```

**审计事件类型**：

- `COMMAND_TRANSLATED`: 命令翻译
- `COMMAND_VALIDATED`: 命令验证
- `COMMAND_BLOCKED`: 命令被拒绝
- `COMMAND_EXECUTED`: 命令执行
- `PERMISSION_ELEVATED`: 权限提升
- `SANDBOX_EXECUTED`: 沙箱执行
- `USER_CONFIRMED`: 用户确认
- `USER_CANCELLED`: 用户取消

**审计日志示例**：

```json
{
  "timestamp": "2024-01-15T14:30:25.123456",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "admin",
  "event_type": "COMMAND_BLOCKED",
  "command": "Remove-Item -Recurse -Force C:\\",
  "risk_level": "CRITICAL",
  "action_taken": "BLOCKED",
  "success": false,
  "details": {
    "reason": "Critical risk command detected",
    "matched_patterns": ["recursive_delete"],
    "warnings": ["递归强制删除文件或目录"]
  }
}
```

---

**本章小结**

本章详细介绍了AI PowerShell智能助手系统的总体设计方案。首先，在系统架构设计中，阐述了分层的模块化架构，包括用户接口层、核心处理层和支持模块层，以及模块划分、接口驱动开发方法和数据流设计。其次，在核心模块设计中，详细设计了主控制器、AI引擎、安全引擎和执行引擎的结构和功能，特别是创新的混合翻译策略和三层安全机制。第三，在数据模型设计中，定义了核心数据结构和配置数据模型，确保数据的规范性和一致性。第四，在接口设计中，定义了模块间接口和外部接口，包括Python API、CLI和REST API，提供了灵活的调用方式。最后，在安全设计中，详细说明了三层安全机制的设计原理、危险命令识别算法、权限管理策略和沙箱隔离方案，以及安全策略配置和审计日志设计。

这些设计方案遵循软件工程的最佳实践，采用模块化、接口驱动的设计方法，确保系统具有良好的可维护性、可扩展性和安全性。本章的设计为后续的详细设计与实现提供了清晰的指导和坚实的基础。

