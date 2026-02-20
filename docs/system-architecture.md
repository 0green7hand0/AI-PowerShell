# AI PowerShell 智能助手 - 系统架构图

## 整体系统架构

```mermaid
graph TB
    %% 用户界面层
    subgraph "用户界面层 (Presentation Layer)"
        WebUI[🌐 Web界面<br/>Vue.js + TypeScript]
        CLI[💻 命令行界面<br/>Rich CLI]
        API[🔌 REST API<br/>Flask + SocketIO]
    end
    
    %% 业务逻辑层
    subgraph "业务逻辑层 (Business Logic Layer)"
        MainController[🎯 主控制器<br/>PowerShellAssistant]
        
        subgraph "核心引擎 (Core Engines)"
            AIEngine[🤖 AI引擎<br/>AI Engine]
            SecurityEngine[🔒 安全引擎<br/>Security Engine]
            ExecutionEngine[⚡ 执行引擎<br/>Execution Engine]
        end
        
        subgraph "支持服务 (Support Services)"
            ConfigManager[⚙️ 配置管理<br/>Config Manager]
            LogEngine[📝 日志引擎<br/>Log Engine]
            StorageEngine[💾 存储引擎<br/>Storage Engine]
            ContextManager[🧠 上下文管理<br/>Context Manager]
            UISystem[🎨 UI系统<br/>UI System]
        end
    end
    
    %% 数据访问层
    subgraph "数据访问层 (Data Access Layer)"
        FileStorage[📁 文件存储<br/>JSON/YAML Files]
        CacheStorage[⚡ 缓存存储<br/>Memory Cache]
        LogStorage[📋 日志存储<br/>Log Files]
        ConfigStorage[⚙️ 配置存储<br/>Config Files]
    end
    
    %% 外部服务层
    subgraph "外部服务层 (External Services)"
        OllamaService[🦙 Ollama服务<br/>Local AI Models]
        APIService[🌐 API服务<br/>OpenAI Compatible]
        PowerShellEngine[⚙️ PowerShell引擎<br/>pwsh/powershell]
        DockerEngine[🐳 Docker引擎<br/>Sandbox Environment]
    end
    
    %% 连接关系
    WebUI --> API
    CLI --> MainController
    API --> MainController
    
    MainController --> AIEngine
    MainController --> SecurityEngine
    MainController --> ExecutionEngine
    MainController --> ConfigManager
    MainController --> LogEngine
    MainController --> StorageEngine
    MainController --> ContextManager
    MainController --> UISystem
    
    AIEngine --> OllamaService
    AIEngine --> APIService
    ExecutionEngine --> PowerShellEngine
    ExecutionEngine --> DockerEngine
    
    ConfigManager --> ConfigStorage
    LogEngine --> LogStorage
    StorageEngine --> FileStorage
    StorageEngine --> CacheStorage
    
    %% 样式定义
    classDef presentation fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef business fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef controller fill:#ffebee,stroke:#d32f2f,stroke-width:3px
    
    class WebUI,CLI,API presentation
    class MainController controller
    class AIEngine,SecurityEngine,ExecutionEngine,ConfigManager,LogEngine,StorageEngine,ContextManager,UISystem business
    class FileStorage,CacheStorage,LogStorage,ConfigStorage data
    class OllamaService,APIService,PowerShellEngine,DockerEngine external
```

## 分层架构详解

### 🌐 用户界面层 (Presentation Layer)

#### Web界面 (Vue.js + TypeScript)
```mermaid
graph LR
    subgraph "Web前端架构"
        Vue[Vue 3 Framework]
        Router[Vue Router]
        Store[Pinia Store]
        UI[Element Plus UI]
        
        subgraph "页面组件"
            Chat[💬 对话页面]
            History[📋 历史页面]
            Templates[📝 模板页面]
            Logs[📊 日志页面]
            Settings[⚙️ 设置页面]
        end
        
        subgraph "核心服务"
            APIClient[API客户端]
            WebSocket[WebSocket连接]
            StateManager[状态管理]
        end
    end
    
    Vue --> Router
    Vue --> Store
    Vue --> UI
    Router --> Chat
    Router --> History
    Router --> Templates
    Router --> Logs
    Router --> Settings
    
    Chat --> APIClient
    History --> APIClient
    Templates --> APIClient
    Logs --> WebSocket
    Settings --> APIClient
    
    APIClient --> StateManager
    WebSocket --> StateManager
    Store --> StateManager
```

#### 命令行界面 (Rich CLI)
- **Rich库**: 提供彩色输出和进度条
- **交互式输入**: 支持命令补全和历史
- **实时反馈**: 显示执行进度和结果

#### REST API (Flask + SocketIO)
- **RESTful接口**: 标准HTTP API
- **WebSocket**: 实时日志推送
- **认证授权**: JWT令牌验证
- **CORS支持**: 跨域资源共享

### 🎯 业务逻辑层 (Business Logic Layer)

#### 主控制器 (PowerShellAssistant)
```python
class PowerShellAssistant:
    """主控制器 - 协调各个引擎的工作"""
    
    def __init__(self):
        self.ai_engine = AIEngine()
        self.security_engine = SecurityEngine()
        self.execution_engine = ExecutionEngine()
        self.config_manager = ConfigManager()
        self.log_engine = LogEngine()
        self.storage_engine = StorageEngine()
        self.context_manager = ContextManager()
        self.ui_system = UISystem()
    
    def process_request(self, text: str) -> ProcessResult:
        """处理用户请求的主要流程"""
        # 1. 翻译自然语言
        # 2. 安全验证
        # 3. 执行命令
        # 4. 记录历史
        # 5. 返回结果
```

#### AI引擎架构
```mermaid
graph TB
    subgraph "AI引擎 (AI Engine)"
        Translator[🔤 自然语言翻译器<br/>NaturalLanguageTranslator]
        ErrorDetector[🔍 错误检测器<br/>ErrorDetector]
        
        subgraph "AI提供商 (AI Providers)"
            OllamaProvider[🦙 Ollama提供商<br/>OllamaProvider]
            APIProvider[🌐 API提供商<br/>DirectAPIProvider]
            MockProvider[🎭 模拟提供商<br/>MockProvider]
        end
        
        subgraph "翻译策略"
            RuleEngine[📋 规则引擎<br/>Rule Matching]
            AIGeneration[🤖 AI生成<br/>AI Generation]
            Fallback[🔄 回退策略<br/>Fallback Strategy]
        end
    end
    
    Translator --> RuleEngine
    Translator --> AIGeneration
    Translator --> Fallback
    
    AIGeneration --> OllamaProvider
    AIGeneration --> APIProvider
    AIGeneration --> MockProvider
    
    ErrorDetector --> OllamaProvider
    ErrorDetector --> APIProvider
```

#### 安全引擎架构
```mermaid
graph TB
    subgraph "安全引擎 (Security Engine)"
        Validator[🔍 命令验证器<br/>CommandValidator]
        PolicyEngine[📜 策略引擎<br/>PolicyEngine]
        RiskAssessor[⚠️ 风险评估器<br/>RiskAssessor]
        
        subgraph "安全策略"
            Whitelist[✅ 白名单检查<br/>Whitelist Check]
            DangerousPattern[⚠️ 危险模式检测<br/>Dangerous Pattern]
            PermissionCheck[🔐 权限检查<br/>Permission Check]
        end
        
        subgraph "执行模式"
            DirectExecution[⚡ 直接执行<br/>Direct Execution]
            SandboxExecution[🏖️ 沙箱执行<br/>Sandbox Execution]
            BlockedExecution[🚫 阻止执行<br/>Blocked Execution]
        end
    end
    
    Validator --> Whitelist
    Validator --> DangerousPattern
    Validator --> PermissionCheck
    
    PolicyEngine --> DirectExecution
    PolicyEngine --> SandboxExecution
    PolicyEngine --> BlockedExecution
    
    RiskAssessor --> PolicyEngine
```

#### 执行引擎架构
```mermaid
graph TB
    subgraph "执行引擎 (Execution Engine)"
        Executor[⚡ 命令执行器<br/>CommandExecutor]
        ResultProcessor[📊 结果处理器<br/>ResultProcessor]
        
        subgraph "执行环境"
            LocalPS[💻 本地PowerShell<br/>Local PowerShell]
            DockerPS[🐳 Docker容器<br/>Docker Container]
            RemotePS[🌐 远程PowerShell<br/>Remote PowerShell]
        end
        
        subgraph "结果处理"
            OutputFormatter[📝 输出格式化<br/>Output Formatter]
            ErrorHandler[❌ 错误处理<br/>Error Handler]
            LogRecorder[📋 日志记录<br/>Log Recorder]
        end
    end
    
    Executor --> LocalPS
    Executor --> DockerPS
    Executor --> RemotePS
    
    ResultProcessor --> OutputFormatter
    ResultProcessor --> ErrorHandler
    ResultProcessor --> LogRecorder
```

### 💾 数据访问层 (Data Access Layer)

#### 存储架构
```mermaid
graph TB
    subgraph "存储架构"
        subgraph "文件存储"
            ConfigFiles[⚙️ 配置文件<br/>YAML/JSON]
            HistoryFiles[📋 历史文件<br/>JSON]
            TemplateFiles[📝 模板文件<br/>YAML]
            LogFiles[📊 日志文件<br/>LOG]
        end
        
        subgraph "内存存储"
            ConfigCache[⚙️ 配置缓存<br/>Config Cache]
            TranslationCache[🔤 翻译缓存<br/>Translation Cache]
            SessionCache[🧠 会话缓存<br/>Session Cache]
        end
        
        subgraph "存储接口"
            FileInterface[📁 文件接口<br/>File Interface]
            CacheInterface[⚡ 缓存接口<br/>Cache Interface]
            DatabaseInterface[🗄️ 数据库接口<br/>Database Interface]
        end
    end
    
    FileInterface --> ConfigFiles
    FileInterface --> HistoryFiles
    FileInterface --> TemplateFiles
    FileInterface --> LogFiles
    
    CacheInterface --> ConfigCache
    CacheInterface --> TranslationCache
    CacheInterface --> SessionCache
```

### 🌐 外部服务层 (External Services)

#### AI服务集成
```mermaid
graph LR
    subgraph "AI服务集成"
        subgraph "Ollama本地服务"
            OllamaAPI[Ollama API<br/>http://localhost:11434]
            Models[本地模型<br/>qwen3:30b, llama2, etc.]
        end
        
        subgraph "外部API服务"
            OpenAI[OpenAI API<br/>GPT-3.5/4]
            Claude[Claude API<br/>Anthropic]
            Custom[自定义API<br/>Compatible Endpoints]
        end
        
        subgraph "API适配器"
            OllamaAdapter[Ollama适配器]
            OpenAIAdapter[OpenAI适配器]
            GenericAdapter[通用适配器]
        end
    end
    
    OllamaAdapter --> OllamaAPI
    OpenAIAdapter --> OpenAI
    OpenAIAdapter --> Claude
    GenericAdapter --> Custom
```

## 数据流架构

```mermaid
sequenceDiagram
    participant User as 👤 用户
    participant WebUI as 🌐 Web界面
    participant API as 🔌 REST API
    participant Controller as 🎯 主控制器
    participant AI as 🤖 AI引擎
    participant Security as 🔒 安全引擎
    participant Execution as ⚡ 执行引擎
    participant PS as ⚙️ PowerShell
    
    User->>WebUI: 输入自然语言
    WebUI->>API: POST /api/command/translate
    API->>Controller: process_request()
    
    Controller->>AI: translate(text)
    AI->>AI: 规则匹配 + AI生成
    AI-->>Controller: PowerShell命令
    
    Controller->>Security: validate(command)
    Security->>Security: 安全检查
    Security-->>Controller: 验证结果
    
    alt 命令安全
        Controller->>Execution: execute(command)
        Execution->>PS: 执行PowerShell
        PS-->>Execution: 执行结果
        Execution-->>Controller: 处理后结果
        Controller-->>API: 成功响应
    else 命令危险
        Controller-->>API: 安全拒绝
    end
    
    API-->>WebUI: JSON响应
    WebUI-->>User: 显示结果
```

## 部署架构

```mermaid
graph TB
    subgraph "生产环境部署"
        subgraph "前端层"
            Nginx[🌐 Nginx<br/>反向代理 + 静态文件]
            WebApp[📱 Web应用<br/>Vue.js构建产物]
        end
        
        subgraph "应用层"
            Gunicorn[🦄 Gunicorn<br/>WSGI服务器]
            FlaskApp[🌶️ Flask应用<br/>Python后端]
        end
        
        subgraph "AI服务层"
            OllamaServer[🦙 Ollama服务<br/>本地AI模型]
            DockerRuntime[🐳 Docker运行时<br/>沙箱环境]
        end
        
        subgraph "存储层"
            FileSystem[📁 文件系统<br/>配置+日志+历史]
            Redis[🔴 Redis<br/>缓存+会话]
        end
    end
    
    Nginx --> WebApp
    Nginx --> Gunicorn
    Gunicorn --> FlaskApp
    FlaskApp --> OllamaServer
    FlaskApp --> DockerRuntime
    FlaskApp --> FileSystem
    FlaskApp --> Redis
```

## 技术栈总览

### 后端技术栈
- **Python 3.8+**: 主要编程语言
- **Flask**: Web框架
- **Flask-SocketIO**: WebSocket支持
- **Pydantic**: 数据验证
- **PyYAML**: 配置文件处理
- **Rich**: CLI美化
- **Ollama**: 本地AI模型
- **Docker**: 容器化和沙箱

### 前端技术栈
- **Vue 3**: 前端框架
- **TypeScript**: 类型安全
- **Vite**: 构建工具
- **Element Plus**: UI组件库
- **Pinia**: 状态管理
- **Axios**: HTTP客户端

### 基础设施
- **Nginx**: 反向代理
- **Gunicorn**: WSGI服务器
- **Redis**: 缓存存储
- **Docker**: 容器化部署
- **PowerShell Core**: 命令执行

## 设计原则

### 1. **模块化设计**
- 高内聚、低耦合
- 清晰的接口定义
- 可插拔的组件架构

### 2. **分层架构**
- 表现层、业务层、数据层分离
- 依赖倒置原则
- 单一职责原则

### 3. **安全优先**
- 多层安全验证
- 沙箱执行环境
- 最小权限原则

### 4. **可扩展性**
- 支持多种AI提供商
- 插件化架构
- 水平扩展能力

### 5. **用户体验**
- 响应式设计
- 实时反馈
- 错误友好提示

这个系统架构图展示了AI PowerShell智能助手的完整技术架构，从用户界面到底层服务的各个层次和组件关系。