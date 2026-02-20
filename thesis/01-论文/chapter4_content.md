### 第4章 系统总体设计

本章介绍AI PowerShell智能助手系统的总体设计方案。基于第3章的需求分析，本章详细阐述系统的架构设计、核心模块设计、数据模型设计、接口设计和安全设计，为后续的详细设计与实现奠定基础。

#### 4.1 系统架构设计

系统架构设计是软件系统设计的核心，决定了系统的整体结构、模块划分和交互方式。本节介绍系统的整体架构、模块划分、接口驱动开发方法和数据流设计。

##### 4.1.1 整体架构

本系统采用分层的模块化架构设计，遵循高内聚低耦合的设计原则，将系统划分为三个主要层次：用户接口层、核心处理层和支持模块层。

**架构层次说明**：

```
┌─────────────────────────────────────────────────────────────┐
│                      用户接口层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  CLI命令行   │  │  交互式模式  │  │  Python API  │      │
│  │    接口      │  │    接口      │  │    接口      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      核心处理层                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              主控制器 (PowerShellAssistant)          │  │
│  │         协调各模块工作，处理用户请求                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ AI引擎   │  │ 安全引擎 │  │ 执行引擎 │  │ 上下文   │  │
│  │          │  │          │  │          │  │ 管理器   │  │
│  │ 自然语言 │  │ 三层安全 │  │ 跨平台   │  │          │  │
│  │ 到命令   │  │ 验证机制 │  │ 命令执行 │  │ 会话历史 │  │
│  │ 转换     │  │          │  │          │  │ 管理     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      支持模块层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 配置管理 │  │ 日志引擎 │  │ 存储引擎 │  │ 工具模块 │  │
│  │          │  │          │  │          │  │          │  │
│  │ 配置加载 │  │ 结构化   │  │ 文件存储 │  │ 平台检测 │  │
│  │ 验证     │  │ 日志     │  │ 缓存管理 │  │ 编码处理 │  │
│  │ 热重载   │  │ 审计追踪 │  │ 持久化   │  │ 格式化   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**1. 用户接口层**

用户接口层提供多种方式供用户与系统交互：

- **CLI命令行接口**：通过命令行参数直接执行翻译和命令
  ```bash
  ai-powershell translate "显示当前时间"
  ai-powershell execute "Get-Date"
  ```

- **交互式模式**：提供类似Shell的交互式环境，支持连续对话
  ```bash
  ai-powershell interactive
  >>> 显示当前时间
  [AI] 翻译结果: Get-Date
  [AI] 是否执行? (y/n): y
  [执行结果] 2024-01-15 14:30:25
  ```

- **Python API接口**：供其他Python程序调用
  ```python
  from ai_powershell import PowerShellAssistant
  
  assistant = PowerShellAssistant()
  result = assistant.process_request("显示当前时间")
  ```

**2. 核心处理层**

核心处理层包含系统的主要业务逻辑：

- **主控制器（PowerShellAssistant）**：
  - 协调各个模块的工作
  - 处理用户请求的完整流程
  - 管理系统状态和生命周期
  - 实现依赖注入和模块组装

- **AI引擎（AIEngine）**：
  - 自然语言理解和意图识别
  - 规则匹配和AI模型翻译
  - 翻译结果验证和优化
  - 缓存管理和性能优化

- **安全引擎（SecurityEngine）**：
  - 命令白名单验证
  - 动态权限检查
  - 沙箱隔离执行
  - 风险等级评估

- **执行引擎（CommandExecutor）**：
  - 跨平台命令执行
  - 输出捕获和格式化
  - 超时控制和错误处理
  - 进程管理

- **上下文管理器（ContextManager）**：
  - 会话管理
  - 命令历史记录
  - 上下文信息维护
  - 历史查询和导出

**3. 支持模块层**

支持模块层提供基础设施服务：

- **配置管理（ConfigManager）**：
  - 配置文件加载和解析
  - 配置验证和默认值处理
  - 配置热重载
  - 多层级配置合并

- **日志引擎（LogEngine）**：
  - 结构化日志记录
  - 敏感信息过滤
  - 日志级别控制
  - 审计追踪

- **存储引擎（StorageEngine）**：
  - 文件存储和读取
  - 缓存管理（LRU）
  - 数据持久化
  - 备份和恢复

- **工具模块（Utils）**：
  - 平台检测和适配
  - 编码转换和处理
  - 输出格式化
  - 通用工具函数

##### 4.1.2 模块划分和职责

系统采用模块化设计，每个模块具有明确的职责和边界。

**模块职责表**：

| 模块名称 | 主要职责 | 输入 | 输出 | 依赖模块 |
|---------|---------|------|------|---------|
| PowerShellAssistant | 主控制器，协调各模块 | 用户请求 | 执行结果 | 所有核心模块 |
| AIEngine | 自然语言到命令转换 | 中文描述 | PowerShell命令 | ConfigManager, StorageEngine |
| SecurityEngine | 安全验证 | PowerShell命令 | 验证结果 | ConfigManager, LogEngine |
| CommandExecutor | 命令执行 | PowerShell命令 | 执行结果 | LogEngine, Utils |
| ContextManager | 上下文和历史管理 | 命令条目 | 历史记录 | StorageEngine |
| ConfigManager | 配置管理 | 配置文件路径 | 配置对象 | 无 |
| LogEngine | 日志记录 | 日志消息 | 无 | ConfigManager |
| StorageEngine | 数据存储 | 键值对 | 存储数据 | ConfigManager |

**模块间依赖关系**：

```
PowerShellAssistant (主控制器)
    ├── AIEngine (AI引擎)
    │   ├── ConfigManager
    │   └── StorageEngine
    ├── SecurityEngine (安全引擎)
    │   ├── ConfigManager
    │   └── LogEngine
    ├── CommandExecutor (执行引擎)
    │   ├── LogEngine
    │   └── Utils
    ├── ContextManager (上下文管理)
    │   └── StorageEngine
    ├── ConfigManager (配置管理)
    ├── LogEngine (日志引擎)
    │   └── ConfigManager
    └── StorageEngine (存储引擎)
        └── ConfigManager
```

**模块设计原则**：

1. **单一职责**：每个模块只负责一个明确的功能领域
2. **依赖倒置**：模块依赖抽象接口而非具体实现
3. **开闭原则**：对扩展开放，对修改关闭
4. **接口隔离**：提供专门的接口，避免臃肿的通用接口
5. **最小知识**：模块只与直接依赖的模块交互

##### 4.1.3 接口驱动开发方法

系统采用接口驱动开发（Interface-Driven Development）方法，通过定义清晰的接口来解耦模块之间的依赖。

**接口定义层次**：

```python
# 1. 定义接口（抽象基类）
from abc import ABC, abstractmethod

class AIEngineInterface(ABC):
    """AI引擎接口"""
    
    @abstractmethod
    def translate(self, user_input: str, context: Context) -> Suggestion:
        """将用户输入翻译为PowerShell命令"""
        pass
    
    @abstractmethod
    def validate_command(self, command: str) -> bool:
        """验证命令的有效性"""
        pass

class SecurityEngineInterface(ABC):
    """安全引擎接口"""
    
    @abstractmethod
    def validate(self, command: str, context: Context) -> ValidationResult:
        """验证命令的安全性"""
        pass
    
    @abstractmethod
    def check_permissions(self, command: str) -> bool:
        """检查命令所需权限"""
        pass

class ExecutorInterface(ABC):
    """执行器接口"""
    
    @abstractmethod
    def execute(self, command: str, timeout: int) -> ExecutionResult:
        """执行PowerShell命令"""
        pass
    
    @abstractmethod
    def execute_async(self, command: str) -> AsyncTask:
        """异步执行命令"""
        pass
```

**接口实现**：

```python
# 2. 实现接口
class AIEngine(AIEngineInterface):
    """AI引擎实现"""
    
    def __init__(self, config: AIConfig, storage: StorageInterface):
        self.config = config
        self.storage = storage
        self.translator = self._create_translator()
    
    def translate(self, user_input: str, context: Context) -> Suggestion:
        # 实现翻译逻辑
        pass
    
    def validate_command(self, command: str) -> bool:
        # 实现验证逻辑
        pass
```

**依赖注入**：

```python
# 3. 通过依赖注入组装系统
class PowerShellAssistant:
    def __init__(
        self,
        ai_engine: AIEngineInterface,
        security_engine: SecurityEngineInterface,
        executor: ExecutorInterface,
        context_manager: ContextManager,
        config_manager: ConfigManager,
        log_engine: LogEngine
    ):
        self.ai_engine = ai_engine
        self.security_engine = security_engine
        self.executor = executor
        self.context_manager = context_manager
        self.config_manager = config_manager
        self.log_engine = log_engine
```

**接口驱动开发的优势**：

1. **解耦**：模块之间通过接口交互，降低耦合度
2. **可测试**：可以使用Mock对象进行单元测试
3. **可替换**：可以轻松替换接口的实现
4. **可扩展**：新增功能只需实现接口即可
5. **并行开发**：不同团队可以并行开发不同模块

##### 4.1.4 数据流设计

系统的数据流设计描述了数据在各模块间的流动过程。

**主要数据流程**：

```
用户输入
    ↓
[1] 主控制器接收请求
    ↓
[2] 构建上下文（ContextManager）
    - 获取当前会话信息
    - 获取命令历史
    - 获取环境变量
    ↓
[3] AI引擎翻译（AIEngine）
    - 检查缓存
    - 规则匹配
    - AI模型生成
    - 返回Suggestion对象
    ↓
[4] 安全引擎验证（SecurityEngine）
    - 命令白名单检查
    - 风险等级评估
    - 权限检查
    - 返回ValidationResult对象
    ↓
[5] 用户确认（如需要）
    - 显示命令和风险信息
    - 等待用户确认
    ↓
[6] 执行引擎执行（CommandExecutor）
    - 平台适配
    - 命令执行
    - 输出捕获
    - 返回ExecutionResult对象
    ↓
[7] 结果处理
    - 格式化输出
    - 记录历史（ContextManager）
    - 记录日志（LogEngine）
    - 更新缓存（StorageEngine）
    ↓
返回结果给用户
```

**数据流图（DFD）**：

```
┌──────────┐
│  用户    │
└────┬─────┘
     │ 中文描述
     ↓
┌────────────────┐
│  主控制器      │
└────┬───────────┘
     │ 用户输入 + 上下文
     ↓
┌────────────────┐      ┌──────────────┐
│  AI引擎        │←────→│  缓存存储    │
└────┬───────────┘      └──────────────┘
     │ PowerShell命令 + 置信度
     ↓
┌────────────────┐      ┌──────────────┐
│  安全引擎      │←────→│  规则配置    │
└────┬───────────┘      └──────────────┘
     │ 验证结果 + 风险等级
     ↓
┌────────────────┐
│  用户确认      │
└────┬───────────┘
     │ 确认的命令
     ↓
┌────────────────┐      ┌──────────────┐
│  执行引擎      │←────→│  平台适配器  │
└────┬───────────┘      └──────────────┘
     │ 执行结果
     ↓
┌────────────────┐      ┌──────────────┐
│  结果处理      │────→│  历史存储    │
└────┬───────────┘      └──────────────┘
     │                  ┌──────────────┐
     │                 →│  日志记录    │
     │                  └──────────────┘
     ↓
┌──────────┐
│  用户    │
└──────────┘
```

**关键数据对象**：

1. **Context（上下文）**：
   - session_id：会话ID
   - user_id：用户ID
   - working_directory：工作目录
   - environment_vars：环境变量
   - command_history：命令历史

2. **Suggestion（命令建议）**：
   - generated_command：生成的命令
   - confidence_score：置信度
   - explanation：命令解释
   - alternatives：备选命令

3. **ValidationResult（验证结果）**：
   - is_valid：是否有效
   - risk_level：风险等级
   - warnings：警告信息
   - requires_confirmation：是否需要确认
   - requires_admin：是否需要管理员权限

4. **ExecutionResult（执行结果）**：
   - success：是否成功
   - output：输出内容
   - error：错误信息
   - return_code：返回码
   - execution_time：执行时间

**数据流的特点**：

1. **单向流动**：数据主要沿着一个方向流动，避免循环依赖
2. **转换明确**：每个模块对数据进行明确的转换
3. **状态隔离**：模块之间不共享可变状态
4. **异常处理**：每个环节都有错误处理机制
5. **可追踪**：通过日志可以追踪数据流动过程



#### 4.2 核心模块设计

核心模块是系统的主要功能实现部分，包括主控制器、AI引擎、安全引擎和执行引擎。本节详细介绍各核心模块的设计。

##### 4.2.1 主控制器设计

主控制器（PowerShellAssistant）是系统的核心协调者，负责整合各个模块，处理用户请求的完整流程。

**主控制器的职责**：

1. **模块初始化和组装**：
   - 创建和初始化所有子模块
   - 通过依赖注入组装系统
   - 管理模块的生命周期

2. **请求处理流程**：
   - 接收用户输入
   - 协调各模块完成翻译、验证、执行
   - 处理异常和错误
   - 返回结果给用户

3. **状态管理**：
   - 维护系统运行状态
   - 管理会话信息
   - 处理系统配置变更

**主控制器类图**：

```
┌─────────────────────────────────────────┐
│      PowerShellAssistant                │
├─────────────────────────────────────────┤
│ - ai_engine: AIEngineInterface          │
│ - security_engine: SecurityEngineInterface│
│ - executor: ExecutorInterface           │
│ - context_manager: ContextManager       │
│ - config_manager: ConfigManager         │
│ - log_engine: LogEngine                 │
│ - storage: StorageInterface             │
├─────────────────────────────────────────┤
│ + __init__(dependencies)                │
│ + process_request(user_input): Result   │
│ + interactive_mode(): void              │
│ + translate_only(user_input): Suggestion│
│ + execute_command(command): ExecutionResult│
│ - _build_context(): Context             │
│ - _handle_error(error): ErrorResponse   │
└─────────────────────────────────────────┘
```

**主要方法设计**：

```python
class PowerShellAssistant:
    """主控制器"""
    
    def process_request(self, user_input: str) -> ProcessResult:
        """
        处理用户请求的完整流程
        
        Args:
            user_input: 用户的中文输入
            
        Returns:
            ProcessResult: 包含翻译、验证、执行结果的完整响应
        """
        try:
            # 1. 构建上下文
            context = self._build_context()
            
            # 2. AI翻译
            suggestion = self.ai_engine.translate(user_input, context)
            
            # 3. 安全验证
            validation = self.security_engine.validate(
                suggestion.generated_command, 
                context
            )
            
            # 4. 用户确认（如需要）
            if validation.requires_confirmation:
                if not self._get_user_confirmation(suggestion, validation):
                    return ProcessResult(status="cancelled")
            
            # 5. 执行命令
            execution_result = self.executor.execute(
                suggestion.generated_command,
                timeout=self.config_manager.get_config().execution.timeout
            )
            
            # 6. 记录历史
            self._record_history(user_input, suggestion, execution_result)
            
            # 7. 返回结果
            return ProcessResult(
                status="success",
                suggestion=suggestion,
                validation=validation,
                execution=execution_result
            )
            
        except Exception as e:
            self.log_engine.error(f"Error processing request: {e}")
            return self._handle_error(e)
    
    def interactive_mode(self):
        """交互式模式"""
        print("AI PowerShell Assistant - Interactive Mode")
        print("Type 'exit' to quit, 'help' for help\n")
        
        while True:
            try:
                user_input = input(">>> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'exit':
                    break
                    
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                result = self.process_request(user_input)
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
```

**时序图（用户请求处理）**：

```
用户 → 主控制器 → 上下文管理器 → AI引擎 → 安全引擎 → 执行引擎
 │        │            │              │          │           │
 │ 输入   │            │              │          │           │
 ├───────→│            │              │          │           │
 │        │ 获取上下文 │              │          │           │
 │        ├───────────→│              │          │           │
 │        │←───────────┤              │          │           │
 │        │  Context   │              │          │           │
 │        │            │              │          │           │
 │        │ 翻译命令   │              │          │           │
 │        ├────────────┼─────────────→│          │           │
 │        │            │              │          │           │
 │        │←───────────┼──────────────┤          │           │
 │        │            │  Suggestion  │          │           │
 │        │            │              │          │           │
 │        │ 安全验证   │              │          │           │
 │        ├────────────┼──────────────┼─────────→│           │
 │        │            │              │          │           │
 │        │←───────────┼──────────────┼──────────┤           │
 │        │            │              │ ValidationResult     │
 │        │            │              │          │           │
 │ 确认？ │            │              │          │           │
 │←───────┤            │              │          │           │
 │ Yes    │            │              │          │           │
 ├───────→│            │              │          │           │
 │        │ 执行命令   │              │          │           │
 │        ├────────────┼──────────────┼──────────┼──────────→│
 │        │            │              │          │           │
 │        │←───────────┼──────────────┼──────────┼───────────┤
 │        │            │              │          │ ExecutionResult
 │        │            │              │          │           │
 │ 结果   │            │              │          │           │
 │←───────┤            │              │          │           │
```

##### 4.2.2 AI引擎设计

AI引擎负责将用户的中文自然语言描述转换为PowerShell命令，是系统的核心智能模块。

**AI引擎的组成**：

```
┌─────────────────────────────────────────┐
│           AIEngine                      │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐ │
│  │   Translator (翻译器)             │ │
│  │  - RuleBasedTranslator            │ │
│  │  - AIModelTranslator              │ │
│  │  - HybridTranslator               │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │   AI Provider (AI提供商)          │ │
│  │  - OllamaProvider                 │ │
│  │  - LocalModelProvider             │ │
│  │  - OpenAIProvider (可选)          │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │   Error Detector (错误检测器)     │ │
│  │  - SyntaxChecker                  │ │
│  │  - CommandValidator               │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │   Cache Manager (缓存管理器)      │ │
│  │  - LRU Cache                      │ │
│  │  - TTL Support                    │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**混合翻译策略**：

系统采用创新的混合翻译策略，结合规则匹配和AI模型生成，兼顾速度和准确性。

```python
class HybridTranslator:
    """混合翻译器"""
    
    def translate(self, user_input: str, context: Context) -> Suggestion:
        """
        混合翻译策略：
        1. 检查缓存
        2. 尝试规则匹配（快速路径）
        3. 使用AI模型生成
        4. 错误检测和修正
        5. 缓存结果
        """
        # 1. 检查缓存
        cache_key = self._generate_cache_key(user_input, context)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 2. 尝试规则匹配
        rule_result = self.rule_translator.translate(user_input)
        if rule_result and rule_result.confidence_score > 0.9:
            self.cache.set(cache_key, rule_result)
            return rule_result
        
        # 3. 使用AI模型生成
        ai_result = self.ai_translator.translate(user_input, context)
        
        # 4. 错误检测
        if not self.error_detector.validate(ai_result.generated_command):
            # 尝试修正
            ai_result = self._try_fix_command(ai_result)
        
        # 5. 缓存结果
        if ai_result.confidence_score > 0.7:
            self.cache.set(cache_key, ai_result)
        
        return ai_result
```

**规则匹配翻译器**：

```python
class RuleBasedTranslator:
    """基于规则的翻译器"""
    
    def __init__(self, rules: List[TranslationRule]):
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)
    
    def translate(self, user_input: str) -> Optional[Suggestion]:
        """使用规则匹配进行翻译"""
        for rule in self.rules:
            match = re.match(rule.pattern, user_input, re.IGNORECASE)
            if match:
                command = rule.template.format(**match.groupdict())
                return Suggestion(
                    generated_command=command,
                    confidence_score=0.95,
                    explanation=rule.explanation,
                    alternatives=[],
                    metadata={"method": "rule_based", "rule_id": rule.id}
                )
        return None
```

**规则示例**：

```yaml
# 翻译规则配置
rules:
  - id: "show_time"
    priority: 100
    pattern: "^(显示|查看|获取)?(当前)?时间$"
    template: "Get-Date"
    explanation: "显示当前系统时间"
    
  - id: "list_processes"
    priority: 90
    pattern: "^(显示|列出|查看)(所有)?进程$"
    template: "Get-Process"
    explanation: "列出所有正在运行的进程"
    
  - id: "top_cpu_processes"
    priority: 85
    pattern: "^(显示|查看)CPU(使用率)?(最高|占用最多)的(?P<count>\\d+)个进程$"
    template: "Get-Process | Sort-Object CPU -Descending | Select-Object -First {count}"
    explanation: "显示CPU使用率最高的进程"
```

**AI模型翻译器**：

```python
class AIModelTranslator:
    """基于AI模型的翻译器"""
    
    def __init__(self, provider: AIProviderInterface, config: AIConfig):
        self.provider = provider
        self.config = config
        self.prompt_template = self._load_prompt_template()
    
    def translate(self, user_input: str, context: Context) -> Suggestion:
        """使用AI模型进行翻译"""
        # 构建提示词
        prompt = self._build_prompt(user_input, context)
        
        # 调用AI模型
        response = self.provider.generate(
            prompt=prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        # 解析响应
        command = self._parse_response(response)
        
        # 生成解释
        explanation = self._generate_explanation(command)
        
        return Suggestion(
            generated_command=command,
            confidence_score=0.85,
            explanation=explanation,
            alternatives=[],
            metadata={"method": "ai_model", "model": self.config.model}
        )
    
    def _build_prompt(self, user_input: str, context: Context) -> str:
        """构建提示词"""
        return self.prompt_template.format(
            user_input=user_input,
            working_directory=context.working_directory,
            platform=context.platform,
            recent_commands=self._format_recent_commands(context.command_history)
        )
```

**提示词模板**：

```python
PROMPT_TEMPLATE = """你是一个PowerShell命令专家。将用户的中文描述转换为PowerShell命令。

要求：
1. 只输出PowerShell命令，不要添加解释
2. 使用PowerShell Core兼容的命令
3. 使用完整的命令名称，避免别名
4. 考虑命令的安全性

当前环境：
- 工作目录：{working_directory}
- 操作系统：{platform}

最近的命令：
{recent_commands}

用户描述：{user_input}
PowerShell命令："""
```

**AI提供商接口**：

```python
class AIProviderInterface(ABC):
    """AI提供商接口"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用"""
        pass

class OllamaProvider(AIProviderInterface):
    """Ollama提供商实现"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.base_url = config.ollama_url or "http://localhost:11434"
        self.model = config.model or "llama2"
    
    def generate(self, prompt: str, **kwargs) -> str:
        """调用Ollama API生成文本"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 256),
                "stream": False
            }
        )
        return response.json()["response"]
    
    def is_available(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
```

##### 4.2.3 安全引擎设计

安全引擎实现三层安全保护机制，确保系统的安全性。

**三层安全架构**：

```
┌─────────────────────────────────────────────────────────┐
│                第一层：命令白名单验证                    │
│  ┌───────────────────────────────────────────────────┐ │
│  │  - 危险命令模式匹配（30+种模式）                  │ │
│  │  - 风险等级评估（SAFE/LOW/MEDIUM/HIGH/CRITICAL）  │ │
│  │  - 命令分类和标记                                 │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                第二层：动态权限检查                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │  - 管理员命令识别                                 │ │
│  │  - 当前权限检测（Windows UAC / Linux sudo）       │ │
│  │  - 权限提升请求                                   │ │
│  │  - 用户确认流程                                   │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                第三层：沙箱隔离执行（可选）              │
│  ┌───────────────────────────────────────────────────┐ │
│  │  - Docker容器隔离                                 │ │
│  │  - 资源限制（CPU、内存、网络）                    │ │
│  │  - 文件系统隔离                                   │ │
│  │  - 自动清理                                       │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**安全引擎类设计**：

```python
class SecurityEngine(SecurityEngineInterface):
    """安全引擎"""
    
    def __init__(self, config: SecurityConfig, log_engine: LogEngine):
        self.config = config
        self.log_engine = log_engine
        
        # 初始化三层验证器
        self.whitelist_validator = WhitelistValidator(config)
        self.permission_checker = PermissionChecker(config)
        self.sandbox_executor = SandboxExecutor(config) if config.enable_sandbox else None
    
    def validate(self, command: str, context: Context) -> ValidationResult:
        """
        三层安全验证
        
        Returns:
            ValidationResult: 验证结果，包含风险等级和建议
        """
        # 第一层：命令白名单验证
        whitelist_result = self.whitelist_validator.validate(command)
        
        if whitelist_result.risk_level == RiskLevel.CRITICAL:
            self.log_engine.warning(
                f"Critical risk command blocked: {command}",
                extra={"user_id": context.user_id, "command": command}
            )
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.CRITICAL,
                warnings=["此命令具有严重风险，已被拒绝执行"],
                requires_confirmation=False,
                requires_admin=False
            )
        
        # 第二层：权限检查
        requires_admin = self.permission_checker.requires_admin(command)
        has_permission = self.permission_checker.check_permission(command)
        
        # 确定是否需要用户确认
        requires_confirmation = (
            whitelist_result.risk_level >= RiskLevel.MEDIUM or
            requires_admin and not has_permission
        )
        
        return ValidationResult(
            is_valid=True,
            risk_level=whitelist_result.risk_level,
            warnings=whitelist_result.warnings,
            requires_confirmation=requires_confirmation,
            requires_admin=requires_admin
        )
```

**危险命令模式库**：

```python
DANGEROUS_PATTERNS = [
    # 删除操作
    {
        "pattern": r"Remove-Item.*-Recurse.*-Force",
        "risk_level": RiskLevel.HIGH,
        "description": "递归强制删除文件或目录"
    },
    {
        "pattern": r"Format-Volume",
        "risk_level": RiskLevel.CRITICAL,
        "description": "格式化磁盘卷"
    },
    {
        "pattern": r"Clear-Disk",
        "risk_level": RiskLevel.CRITICAL,
        "description": "清除磁盘数据"
    },
    
    # 系统修改
    {
        "pattern": r"Set-ItemProperty.*HKLM:",
        "risk_level": RiskLevel.HIGH,
        "description": "修改系统注册表"
    },
    {
        "pattern": r"Set-ExecutionPolicy.*Unrestricted",
        "risk_level": RiskLevel.MEDIUM,
        "description": "设置脚本执行策略为不受限"
    },
    
    # 网络操作
    {
        "pattern": r"Invoke-WebRequest.*\|.*Invoke-Expression",
        "risk_level": RiskLevel.CRITICAL,
        "description": "从网络下载并执行代码"
    },
    {
        "pattern": r"iwr.*\|.*iex",
        "risk_level": RiskLevel.CRITICAL,
        "description": "从网络下载并执行代码（使用别名）"
    },
    
    # 进程操作
    {
        "pattern": r"Stop-Process.*-Force",
        "risk_level": RiskLevel.MEDIUM,
        "description": "强制终止进程"
    },
    {
        "pattern": r"Stop-Computer.*-Force",
        "risk_level": RiskLevel.HIGH,
        "description": "强制关机"
    },
    
    # 用户和权限
    {
        "pattern": r"New-LocalUser",
        "risk_level": RiskLevel.HIGH,
        "description": "创建本地用户"
    },
    {
        "pattern": r"Add-LocalGroupMember.*Administrators",
        "risk_level": RiskLevel.HIGH,
        "description": "将用户添加到管理员组"
    }
]
```

**风险等级评估算法**：

```python
class WhitelistValidator:
    """命令白名单验证器"""
    
    def validate(self, command: str) -> WhitelistValidationResult:
        """验证命令并评估风险等级"""
        risk_level = RiskLevel.SAFE
        warnings = []
        
        # 遍历所有危险模式
        for pattern_info in DANGEROUS_PATTERNS:
            if re.search(pattern_info["pattern"], command, re.IGNORECASE):
                # 取最高风险等级
                if pattern_info["risk_level"] > risk_level:
                    risk_level = pattern_info["risk_level"]
                
                warnings.append(
                    f"检测到危险操作：{pattern_info['description']}"
                )
        
        # 检查命令组合
        if "|" in command:
            pipe_count = command.count("|")
            if pipe_count > 3:
                warnings.append("命令管道过长，可能存在风险")
                risk_level = max(risk_level, RiskLevel.LOW)
        
        return WhitelistValidationResult(
            risk_level=risk_level,
            warnings=warnings
        )
```

##### 4.2.4 执行引擎设计

执行引擎负责跨平台的PowerShell命令执行。

**执行引擎架构**：

```
┌─────────────────────────────────────────┐
│        CommandExecutor                  │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐ │
│  │  Platform Adapter (平台适配器)    │ │
│  │  - WindowsAdapter                 │ │
│  │  - LinuxAdapter                   │ │
│  │  - MacOSAdapter                   │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  Process Manager (进程管理器)     │ │
│  │  - 进程创建和控制                 │ │
│  │  - 超时管理                       │ │
│  │  - 输出捕获                       │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  Output Formatter (输出格式化器)  │ │
│  │  - 文本格式化                     │ │
│  │  - 编码转换                       │ │
│  │  - 结果解析                       │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**平台适配器设计**：

```python
class PlatformAdapter(ABC):
    """平台适配器接口"""
    
    @abstractmethod
    def get_powershell_command(self) -> List[str]:
        """获取PowerShell可执行文件路径"""
        pass
    
    @abstractmethod
    def prepare_command(self, command: str) -> List[str]:
        """准备要执行的命令"""
        pass
    
    @abstractmethod
    def get_encoding(self) -> str:
        """获取系统编码"""
        pass

class WindowsAdapter(PlatformAdapter):
    """Windows平台适配器"""
    
    def get_powershell_command(self) -> List[str]:
        """优先使用PowerShell Core，回退到Windows PowerShell"""
        if shutil.which("pwsh"):
            return ["pwsh", "-NoProfile", "-Command"]
        return ["powershell", "-NoProfile", "-Command"]
    
    def prepare_command(self, command: str) -> List[str]:
        """准备Windows命令"""
        ps_cmd = self.get_powershell_command()
        return ps_cmd + [command]
    
    def get_encoding(self) -> str:
        """Windows使用UTF-8"""
        return "utf-8"

class LinuxAdapter(PlatformAdapter):
    """Linux平台适配器"""
    
    def get_powershell_command(self) -> List[str]:
        """Linux使用pwsh"""
        return ["pwsh", "-NoProfile", "-Command"]
    
    def prepare_command(self, command: str) -> List[str]:
        """准备Linux命令"""
        return self.get_powershell_command() + [command]
    
    def get_encoding(self) -> str:
        """Linux使用UTF-8"""
        return "utf-8"
```

**命令执行实现**：

```python
class CommandExecutor(ExecutorInterface):
    """命令执行器"""
    
    def __init__(self, config: ExecutionConfig, log_engine: LogEngine):
        self.config = config
        self.log_engine = log_engine
        self.adapter = self._create_adapter()
    
    def execute(self, command: str, timeout: int = None) -> ExecutionResult:
        """
        执行PowerShell命令
        
        Args:
            command: PowerShell命令
            timeout: 超时时间（秒），None表示使用配置的默认值
            
        Returns:
            ExecutionResult: 执行结果
        """
        if timeout is None:
            timeout = self.config.default_timeout
        
        start_time = time.time()
        
        try:
            # 准备命令
            cmd_list = self.adapter.prepare_command(command)
            
            # 执行命令
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding=self.adapter.get_encoding(),
                errors='replace'  # 处理编码错误
            )
            
            # 等待命令完成或超时
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"命令执行超时（{timeout}秒）",
                    return_code=-1,
                    execution_time=timeout
                )
            
            execution_time = time.time() - start_time
            
            # 记录日志
            self.log_engine.info(
                f"Command executed: {command}",
                extra={
                    "return_code": return_code,
                    "execution_time": execution_time
                }
            )
            
            return ExecutionResult(
                success=(return_code == 0),
                output=stdout,
                error=stderr,
                return_code=return_code,
                execution_time=execution_time
            )
            
        except Exception as e:
            self.log_engine.error(f"Execution error: {e}")
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                return_code=-1,
                execution_time=time.time() - start_time
            )
```



#### 4.3 数据模型设计

数据模型定义了系统中各种数据结构和它们之间的关系。本节介绍核心数据结构和配置数据模型的设计。

##### 4.3.1 核心数据结构

系统定义了多个核心数据结构，用于在模块间传递信息。

**1. Suggestion（命令建议）**

```python
@dataclass
class Suggestion:
    """命令建议数据结构"""
    
    generated_command: str          # 生成的PowerShell命令
    confidence_score: float         # 置信度分数 (0.0-1.0)
    explanation: str                # 命令的中文解释
    alternatives: List[str]         # 备选命令列表
    metadata: Dict[str, Any]        # 元数据（翻译方法、模型等）
    
    def __post_init__(self):
        """验证数据有效性"""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        if not self.generated_command:
            raise ValueError("Generated command cannot be empty")
```

**使用示例**：

```python
suggestion = Suggestion(
    generated_command="Get-Date",
    confidence_score=0.95,
    explanation="显示当前系统日期和时间",
    alternatives=["Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"],
    metadata={"method": "rule_based", "rule_id": "show_time"}
)
```

**2. ValidationResult（验证结果）**

```python
@dataclass
class ValidationResult:
    """安全验证结果"""
    
    is_valid: bool                  # 命令是否有效
    risk_level: RiskLevel           # 风险等级
    warnings: List[str]             # 警告信息列表
    requires_confirmation: bool     # 是否需要用户确认
    requires_admin: bool            # 是否需要管理员权限
    blocked_reason: Optional[str] = None  # 被拒绝的原因（如果被拒绝）
    
    def is_safe(self) -> bool:
        """判断命令是否安全"""
        return self.risk_level <= RiskLevel.LOW
    
    def should_warn_user(self) -> bool:
        """判断是否应该警告用户"""
        return len(self.warnings) > 0 or self.risk_level >= RiskLevel.MEDIUM
```

**风险等级枚举**：

```python
class RiskLevel(Enum):
    """风险等级枚举"""
    SAFE = 0        # 安全，无风险
    LOW = 1         # 低风险，轻微警告
    MEDIUM = 2      # 中等风险，需要确认
    HIGH = 3        # 高风险，需要特殊确认
    CRITICAL = 4    # 严重风险，默认拒绝
    
    def __lt__(self, other):
        return self.value < other.value
    
    def __le__(self, other):
        return self.value <= other.value
    
    def __gt__(self, other):
        return self.value > other.value
    
    def __ge__(self, other):
        return self.value >= other.value
```

**3. ExecutionResult（执行结果）**

```python
@dataclass
class ExecutionResult:
    """命令执行结果"""
    
    success: bool                   # 执行是否成功
    output: str                     # 标准输出
    error: str                      # 错误输出
    return_code: int                # 返回码
    execution_time: float           # 执行时间（秒）
    
    def has_output(self) -> bool:
        """判断是否有输出"""
        return bool(self.output.strip())
    
    def has_error(self) -> bool:
        """判断是否有错误"""
        return bool(self.error.strip())
    
    def format_output(self) -> str:
        """格式化输出"""
        if self.success:
            return self.output
        else:
            return f"Error (code {self.return_code}): {self.error}"
```

**4. Context（上下文）**

```python
@dataclass
class Context:
    """执行上下文"""
    
    session_id: str                 # 会话ID
    user_id: Optional[str]          # 用户ID
    working_directory: str          # 当前工作目录
    environment_vars: Dict[str, str]  # 环境变量
    command_history: List['CommandEntry']  # 命令历史
    platform: str                   # 操作系统平台
    timestamp: datetime             # 时间戳
    
    @classmethod
    def create_new(cls, user_id: Optional[str] = None) -> 'Context':
        """创建新的上下文"""
        return cls(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            working_directory=os.getcwd(),
            environment_vars=dict(os.environ),
            command_history=[],
            platform=sys.platform,
            timestamp=datetime.now()
        )
    
    def add_command(self, entry: 'CommandEntry'):
        """添加命令到历史"""
        self.command_history.append(entry)
        # 限制历史记录数量
        if len(self.command_history) > 100:
            self.command_history.pop(0)
```

**5. CommandEntry（命令历史条目）**

```python
@dataclass
class CommandEntry:
    """命令历史条目"""
    
    command_id: str                 # 命令唯一ID
    user_input: str                 # 用户输入的中文描述
    translated_command: str         # 翻译后的PowerShell命令
    status: CommandStatus           # 命令状态
    output: str                     # 命令输出
    error: str                      # 错误信息
    return_code: int                # 返回码
    execution_time: float           # 执行时间
    confidence_score: float         # 翻译置信度
    risk_level: RiskLevel           # 风险等级
    timestamp: datetime             # 执行时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "command_id": self.command_id,
            "user_input": self.user_input,
            "translated_command": self.translated_command,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "return_code": self.return_code,
            "execution_time": self.execution_time,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level.value,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandEntry':
        """从字典创建"""
        return cls(
            command_id=data["command_id"],
            user_input=data["user_input"],
            translated_command=data["translated_command"],
            status=CommandStatus(data["status"]),
            output=data["output"],
            error=data["error"],
            return_code=data["return_code"],
            execution_time=data["execution_time"],
            confidence_score=data["confidence_score"],
            risk_level=RiskLevel(data["risk_level"]),
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
```

**命令状态枚举**：

```python
class CommandStatus(Enum):
    """命令状态枚举"""
    PENDING = "pending"         # 待执行
    EXECUTING = "executing"     # 执行中
    SUCCESS = "success"         # 执行成功
    FAILED = "failed"           # 执行失败
    CANCELLED = "cancelled"     # 用户取消
    TIMEOUT = "timeout"         # 执行超时
```

**数据结构关系图**：

```
┌─────────────┐
│   Context   │
└──────┬──────┘
       │ contains
       ↓
┌─────────────────┐
│ CommandEntry    │
│ (List)          │
└─────────────────┘

┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ User Input  │─────→│   Suggestion     │─────→│ ValidationResult│
└─────────────┘      └──────────────────┘      └────────┬────────┘
                                                         │
                                                         ↓
                                                  ┌──────────────┐
                                                  │ExecutionResult│
                                                  └──────────────┘
```

##### 4.3.2 配置数据模型

系统使用Pydantic进行配置数据的验证和管理。

**1. 主配置模型**

```python
class Config(BaseModel):
    """主配置模型"""
    
    ai: AIConfig                    # AI引擎配置
    security: SecurityConfig        # 安全引擎配置
    execution: ExecutionConfig      # 执行引擎配置
    logging: LoggingConfig          # 日志配置
    storage: StorageConfig          # 存储配置
    context: ContextConfig          # 上下文配置
    
    class Config:
        # Pydantic配置
        validate_assignment = True  # 赋值时验证
        extra = "forbid"            # 禁止额外字段
```

**2. AI引擎配置**

```python
class AIConfig(BaseModel):
    """AI引擎配置"""
    
    provider: str = Field(
        default="ollama",
        description="AI提供商：ollama, local, openai"
    )
    
    model: str = Field(
        default="llama2",
        description="模型名称"
    )
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度，控制随机性"
    )
    
    max_tokens: int = Field(
        default=256,
        ge=1,
        le=4096,
        description="最大生成token数"
    )
    
    ollama_url: Optional[str] = Field(
        default="http://localhost:11434",
        description="Ollama服务URL"
    )
    
    enable_cache: bool = Field(
        default=True,
        description="是否启用翻译缓存"
    )
    
    cache_size: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="缓存大小"
    )
    
    cache_ttl: int = Field(
        default=3600,
        ge=60,
        description="缓存过期时间（秒）"
    )
    
    rules_file: str = Field(
        default="config/translation_rules.yaml",
        description="翻译规则文件路径"
    )
    
    @validator('provider')
    def validate_provider(cls, v):
        """验证提供商"""
        allowed = ['ollama', 'local', 'openai']
        if v not in allowed:
            raise ValueError(f"Provider must be one of {allowed}")
        return v
```

**3. 安全引擎配置**

```python
class SecurityConfig(BaseModel):
    """安全引擎配置"""
    
    enable_whitelist: bool = Field(
        default=True,
        description="是否启用命令白名单验证"
    )
    
    dangerous_patterns_file: str = Field(
        default="config/dangerous_patterns.yaml",
        description="危险命令模式文件"
    )
    
    default_risk_level: str = Field(
        default="MEDIUM",
        description="未匹配命令的默认风险等级"
    )
    
    enable_permission_check: bool = Field(
        default=True,
        description="是否启用权限检查"
    )
    
    enable_sandbox: bool = Field(
        default=False,
        description="是否启用沙箱执行"
    )
    
    sandbox_image: str = Field(
        default="mcr.microsoft.com/powershell:latest",
        description="沙箱Docker镜像"
    )
    
    sandbox_memory_limit: str = Field(
        default="512m",
        description="沙箱内存限制"
    )
    
    sandbox_cpu_quota: int = Field(
        default=50000,
        ge=10000,
        le=100000,
        description="沙箱CPU配额（微秒）"
    )
    
    sandbox_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="沙箱执行超时（秒）"
    )
    
    require_confirmation_levels: List[str] = Field(
        default=["MEDIUM", "HIGH", "CRITICAL"],
        description="需要用户确认的风险等级"
    )
```

**4. 执行引擎配置**

```python
class ExecutionConfig(BaseModel):
    """执行引擎配置"""
    
    default_timeout: int = Field(
        default=30,
        ge=1,
        le=3600,
        description="默认命令执行超时（秒）"
    )
    
    max_output_size: int = Field(
        default=1048576,  # 1MB
        ge=1024,
        description="最大输出大小（字节）"
    )
    
    encoding: str = Field(
        default="utf-8",
        description="输出编码"
    )
    
    capture_stderr: bool = Field(
        default=True,
        description="是否捕获标准错误输出"
    )
    
    shell_options: List[str] = Field(
        default=["-NoProfile", "-NonInteractive"],
        description="PowerShell启动选项"
    )
```

**5. 日志配置**

```python
class LoggingConfig(BaseModel):
    """日志配置"""
    
    level: str = Field(
        default="INFO",
        description="日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    format: str = Field(
        default="json",
        description="日志格式：json, text"
    )
    
    output: str = Field(
        default="file",
        description="日志输出：console, file, both"
    )
    
    file_path: str = Field(
        default="logs/ai-powershell.log",
        description="日志文件路径"
    )
    
    max_file_size: int = Field(
        default=10485760,  # 10MB
        ge=1048576,
        description="单个日志文件最大大小（字节）"
    )
    
    backup_count: int = Field(
        default=5,
        ge=1,
        le=100,
        description="日志文件备份数量"
    )
    
    enable_audit: bool = Field(
        default=True,
        description="是否启用审计日志"
    )
    
    sensitive_patterns: List[str] = Field(
        default=[
            r"\b\d{16}\b",  # 信用卡号
            r"password\s*=\s*\S+",  # 密码
            r"api[_-]?key\s*=\s*\S+",  # API密钥
        ],
        description="敏感信息正则表达式模式"
    )
```

**6. 存储配置**

```python
class StorageConfig(BaseModel):
    """存储配置"""
    
    backend: str = Field(
        default="file",
        description="存储后端：file, sqlite, redis"
    )
    
    base_path: str = Field(
        default="~/.ai-powershell",
        description="存储基础路径"
    )
    
    history_file: str = Field(
        default="history.json",
        description="历史记录文件名"
    )
    
    cache_file: str = Field(
        default="cache.json",
        description="缓存文件名"
    )
    
    max_history_size: int = Field(
        default=1000,
        ge=10,
        le=100000,
        description="最大历史记录数"
    )
    
    enable_backup: bool = Field(
        default=True,
        description="是否启用自动备份"
    )
    
    backup_interval: int = Field(
        default=86400,  # 24小时
        ge=3600,
        description="备份间隔（秒）"
    )
```

**配置文件示例（YAML格式）**：

```yaml
# AI引擎配置
ai:
  provider: "ollama"
  model: "llama2"
  temperature: 0.7
  max_tokens: 256
  ollama_url: "http://localhost:11434"
  enable_cache: true
  cache_size: 1000
  cache_ttl: 3600
  rules_file: "config/translation_rules.yaml"

# 安全引擎配置
security:
  enable_whitelist: true
  dangerous_patterns_file: "config/dangerous_patterns.yaml"
  default_risk_level: "MEDIUM"
  enable_permission_check: true
  enable_sandbox: false
  sandbox_image: "mcr.microsoft.com/powershell:latest"
  sandbox_memory_limit: "512m"
  sandbox_cpu_quota: 50000
  sandbox_timeout: 30
  require_confirmation_levels:
    - "MEDIUM"
    - "HIGH"
    - "CRITICAL"

# 执行引擎配置
execution:
  default_timeout: 30
  max_output_size: 1048576
  encoding: "utf-8"
  capture_stderr: true
  shell_options:
    - "-NoProfile"
    - "-NonInteractive"

# 日志配置
logging:
  level: "INFO"
  format: "json"
  output: "both"
  file_path: "logs/ai-powershell.log"
  max_file_size: 10485760
  backup_count: 5
  enable_audit: true

# 存储配置
storage:
  backend: "file"
  base_path: "~/.ai-powershell"
  history_file: "history.json"
  cache_file: "cache.json"
  max_history_size: 1000
  enable_backup: true
  backup_interval: 86400
```

