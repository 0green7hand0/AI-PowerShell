# AI PowerShell 智能助手 - 数据流图

## 0级数据流图 (Context Diagram)

```mermaid
graph TB
    %% 外部实体
    User[👤 用户<br/>User]
    Admin[👤 管理员<br/>Administrator]
    AIService[🤖 AI服务<br/>AI Service]
    PowerShell[⚙️ PowerShell引擎<br/>PowerShell Engine]
    
    %% 系统
    System[🎯 AI PowerShell<br/>智能助手系统<br/>AI PowerShell Assistant]
    
    %% 数据流
    User -->|自然语言输入<br/>Natural Language Input| System
    System -->|PowerShell命令<br/>PowerShell Commands| User
    System -->|执行结果<br/>Execution Results| User
    
    Admin -->|配置参数<br/>Configuration| System
    System -->|系统状态<br/>System Status| Admin
    
    System -->|翻译请求<br/>Translation Request| AIService
    AIService -->|生成命令<br/>Generated Commands| System
    
    System -->|PowerShell命令<br/>PowerShell Commands| PowerShell
    PowerShell -->|执行结果<br/>Execution Results| System
    
    %% 样式
    classDef external fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef system fill:#ffebee,stroke:#d32f2f,stroke-width:3px
    
    class User,Admin,AIService,PowerShell external
    class System system
```

## 1级数据流图 (Level 1 DFD)

```mermaid
graph TB
    %% 外部实体
    User[👤 用户]
    Admin[👤 管理员]
    AIService[🤖 AI服务]
    PowerShell[⚙️ PowerShell引擎]
    
    %% 主要处理过程
    P1[1.0<br/>🔤 自然语言翻译<br/>Natural Language<br/>Translation]
    P2[2.0<br/>🔒 安全验证<br/>Security<br/>Validation]
    P3[3.0<br/>⚡ 命令执行<br/>Command<br/>Execution]
    P4[4.0<br/>📊 结果处理<br/>Result<br/>Processing]
    P5[5.0<br/>⚙️ 配置管理<br/>Configuration<br/>Management]
    P6[6.0<br/>📝 日志记录<br/>Log<br/>Recording]
    
    %% 数据存储
    D1[(D1<br/>📋 历史记录<br/>History)]
    D2[(D2<br/>📝 模板库<br/>Templates)]
    D3[(D3<br/>⚙️ 配置文件<br/>Config)]
    D4[(D4<br/>📊 日志文件<br/>Logs)]
    D5[(D5<br/>⚡ 缓存<br/>Cache)]
    
    %% 用户数据流
    User -->|1. 自然语言输入| P1
    P1 -->|2. PowerShell命令| P2
    P2 -->|3. 验证通过的命令| P3
    P3 -->|4. 执行结果| P4
    P4 -->|5. 格式化结果| User
    
    %% AI服务数据流
    P1 -->|翻译请求| AIService
    AIService -->|生成的命令| P1
    
    %% PowerShell数据流
    P3 -->|PowerShell命令| PowerShell
    PowerShell -->|原始结果| P3
    
    %% 管理员数据流
    Admin -->|配置更新| P5
    P5 -->|系统状态| Admin
    
    %% 数据存储交互
    P1 -.->|读取模板| D2
    P1 -.->|读取缓存| D5
    P1 -.->|写入缓存| D5
    
    P2 -.->|读取安全策略| D3
    
    P4 -.->|保存历史| D1
    P4 -.->|读取历史| D1
    
    P5 -.->|读写配置| D3
    
    P6 -.->|写入日志| D4
    P1 -.->|记录翻译日志| P6
    P2 -.->|记录安全日志| P6
    P3 -.->|记录执行日志| P6
    
    %% 样式
    classDef external fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef datastore fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class User,Admin,AIService,PowerShell external
    class P1,P2,P3,P4,P5,P6 process
    class D1,D2,D3,D4,D5 datastore
```

## 2级数据流图 - 自然语言翻译过程

```mermaid
graph TB
    %% 输入输出
    Input[自然语言输入<br/>Natural Language Input]
    Output[PowerShell命令<br/>PowerShell Command]
    
    %% 子过程
    P11[1.1<br/>📋 规则匹配<br/>Rule Matching]
    P12[1.2<br/>🤖 AI翻译<br/>AI Translation]
    P13[1.3<br/>🔄 结果合并<br/>Result Merging]
    P14[1.4<br/>✅ 命令验证<br/>Command Validation]
    
    %% 数据存储
    D21[(规则库<br/>Rule Base)]
    D22[(翻译缓存<br/>Translation Cache)]
    D23[(模板库<br/>Template Library)]
    
    %% 外部服务
    AIService[🤖 AI服务]
    
    %% 数据流
    Input --> P11
    Input --> P12
    
    P11 -.->|查询规则| D21
    P11 -->|规则匹配结果| P13
    
    P12 -.->|检查缓存| D22
    P12 -->|AI请求| AIService
    AIService -->|AI响应| P12
    P12 -.->|更新缓存| D22
    P12 -->|AI翻译结果| P13
    
    P13 -.->|使用模板| D23
    P13 -->|候选命令| P14
    P14 -->|验证后命令| Output
    
    %% 样式
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef datastore fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef external fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    
    class P11,P12,P13,P14 process
    class D21,D22,D23 datastore
    class AIService external
```

## 2级数据流图 - 安全验证过程

```mermaid
graph TB
    %% 输入输出
    Input[PowerShell命令<br/>PowerShell Command]
    Output[验证结果<br/>Validation Result]
    
    %% 子过程
    P21[2.1<br/>📋 白名单检查<br/>Whitelist Check]
    P22[2.2<br/>⚠️ 危险模式检测<br/>Dangerous Pattern Detection]
    P23[2.3<br/>🔐 权限验证<br/>Permission Validation]
    P24[2.4<br/>📊 风险评估<br/>Risk Assessment]
    P25[2.5<br/>🎯 决策制定<br/>Decision Making]
    
    %% 数据存储
    D31[(安全策略<br/>Security Policies)]
    D32[(白名单<br/>Whitelist)]
    D33[(危险模式<br/>Dangerous Patterns)]
    D34[(权限配置<br/>Permission Config)]
    
    %% 数据流
    Input --> P21
    Input --> P22
    Input --> P23
    
    P21 -.->|查询白名单| D32
    P21 -->|白名单结果| P24
    
    P22 -.->|匹配模式| D33
    P22 -->|危险检测结果| P24
    
    P23 -.->|检查权限| D34
    P23 -->|权限验证结果| P24
    
    P24 -.->|应用策略| D31
    P24 -->|风险评分| P25
    P25 -->|最终决策| Output
    
    %% 样式
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef datastore fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class P21,P22,P23,P24,P25 process
    class D31,D32,D33,D34 datastore
```

## 2级数据流图 - 命令执行过程

```mermaid
graph TB
    %% 输入输出
    Input[验证通过的命令<br/>Validated Command]
    Output[执行结果<br/>Execution Result]
    
    %% 子过程
    P31[3.1<br/>🎯 执行环境选择<br/>Environment Selection]
    P32[3.2<br/>⚡ 命令执行<br/>Command Execution]
    P33[3.3<br/>📊 结果收集<br/>Result Collection]
    P34[3.4<br/>❌ 错误处理<br/>Error Handling]
    P35[3.5<br/>🧹 环境清理<br/>Environment Cleanup]
    
    %% 数据存储
    D41[(执行配置<br/>Execution Config)]
    D42[(环境状态<br/>Environment State)]
    
    %% 外部服务
    LocalPS[💻 本地PowerShell]
    DockerPS[🐳 Docker容器]
    
    %% 数据流
    Input --> P31
    P31 -.->|读取配置| D41
    P31 -->|选择环境| P32
    
    P32 -->|本地执行| LocalPS
    P32 -->|容器执行| DockerPS
    LocalPS -->|本地结果| P33
    DockerPS -->|容器结果| P33
    
    P32 -.->|更新状态| D42
    P33 -->|正常结果| Output
    P33 -->|异常情况| P34
    P34 -->|错误处理后| Output
    
    P32 -->|需要清理| P35
    P35 -.->|清理状态| D42
    
    %% 样式
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef datastore fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef external fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    
    class P31,P32,P33,P34,P35 process
    class D41,D42 datastore
    class LocalPS,DockerPS external
```

## Web界面数据流图

```mermaid
graph TB
    %% 前端组件
    subgraph "前端 (Vue.js)"
        ChatUI[💬 对话界面]
        HistoryUI[📋 历史界面]
        TemplateUI[📝 模板界面]
        SettingsUI[⚙️ 设置界面]
        LogsUI[📊 日志界面]
    end
    
    %% API层
    subgraph "API层 (Flask)"
        CommandAPI[🔤 命令API]
        HistoryAPI[📋 历史API]
        TemplateAPI[📝 模板API]
        ConfigAPI[⚙️ 配置API]
        LogsWS[📊 日志WebSocket]
    end
    
    %% 后端服务
    subgraph "后端服务"
        AIEngine[🤖 AI引擎]
        SecurityEngine[🔒 安全引擎]
        ExecutionEngine[⚡ 执行引擎]
        StorageEngine[💾 存储引擎]
    end
    
    %% 数据流
    ChatUI -->|POST /api/command/translate| CommandAPI
    CommandAPI --> AIEngine
    AIEngine --> SecurityEngine
    SecurityEngine --> ExecutionEngine
    ExecutionEngine --> CommandAPI
    CommandAPI -->|JSON响应| ChatUI
    
    HistoryUI -->|GET /api/history| HistoryAPI
    HistoryAPI --> StorageEngine
    StorageEngine --> HistoryAPI
    HistoryAPI -->|历史数据| HistoryUI
    
    TemplateUI -->|CRUD /api/templates| TemplateAPI
    TemplateAPI --> StorageEngine
    StorageEngine --> TemplateAPI
    TemplateAPI -->|模板数据| TemplateUI
    
    SettingsUI -->|PUT /api/config| ConfigAPI
    ConfigAPI --> StorageEngine
    StorageEngine --> ConfigAPI
    ConfigAPI -->|配置数据| SettingsUI
    
    LogsUI -->|WebSocket连接| LogsWS
    LogsWS -->|实时日志| LogsUI
    
    %% 样式
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef api fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef backend fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class ChatUI,HistoryUI,TemplateUI,SettingsUI,LogsUI frontend
    class CommandAPI,HistoryAPI,TemplateAPI,ConfigAPI,LogsWS api
    class AIEngine,SecurityEngine,ExecutionEngine,StorageEngine backend
```

## 数据存储结构图

```mermaid
graph TB
    subgraph "数据存储层"
        subgraph "配置数据"
            DefaultConfig[default.yaml<br/>默认配置]
            UserConfig[user.yaml<br/>用户配置]
            TemplateConfig[templates.yaml<br/>模板配置]
        end
        
        subgraph "历史数据"
            CommandHistory[history.json<br/>命令历史]
            SessionData[sessions/<br/>会话数据]
            CacheData[cache/<br/>缓存数据]
        end
        
        subgraph "日志数据"
            AppLog[app.log<br/>应用日志]
            SecurityLog[security.log<br/>安全日志]
            AuditLog[audit.log<br/>审计日志]
        end
        
        subgraph "模板数据"
            SystemTemplates[system/<br/>系统模板]
            UserTemplates[user/<br/>用户模板]
            SharedTemplates[shared/<br/>共享模板]
        end
    end
    
    %% 数据关系
    DefaultConfig -.->|继承| UserConfig
    UserConfig -.->|应用到| CommandHistory
    TemplateConfig -.->|定义| SystemTemplates
    SystemTemplates -.->|扩展| UserTemplates
    
    CommandHistory -.->|记录到| AppLog
    AppLog -.->|安全事件| SecurityLog
    SecurityLog -.->|审计跟踪| AuditLog
    
    %% 样式
    classDef config fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef history fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef logs fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef templates fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class DefaultConfig,UserConfig,TemplateConfig config
    class CommandHistory,SessionData,CacheData history
    class AppLog,SecurityLog,AuditLog logs
    class SystemTemplates,UserTemplates,SharedTemplates templates
```

## 实时数据流 (WebSocket)

```mermaid
sequenceDiagram
    participant User as 👤 用户
    participant WebUI as 🌐 Web界面
    participant WebSocket as 🔌 WebSocket
    participant LogEngine as 📝 日志引擎
    participant AIEngine as 🤖 AI引擎
    participant ExecutionEngine as ⚡ 执行引擎
    
    User->>WebUI: 连接日志页面
    WebUI->>WebSocket: 建立WebSocket连接
    WebSocket-->>WebUI: 连接确认
    
    User->>WebUI: 提交命令翻译
    WebUI->>AIEngine: 翻译请求
    
    AIEngine->>LogEngine: 记录翻译开始
    LogEngine->>WebSocket: 推送日志
    WebSocket-->>WebUI: 实时日志显示
    
    AIEngine->>AIEngine: 执行翻译
    AIEngine->>LogEngine: 记录翻译完成
    LogEngine->>WebSocket: 推送日志
    WebSocket-->>WebUI: 更新日志显示
    
    AIEngine-->>WebUI: 返回翻译结果
    
    User->>WebUI: 确认执行命令
    WebUI->>ExecutionEngine: 执行请求
    
    ExecutionEngine->>LogEngine: 记录执行开始
    LogEngine->>WebSocket: 推送日志
    WebSocket-->>WebUI: 实时日志显示
    
    ExecutionEngine->>ExecutionEngine: 执行命令
    ExecutionEngine->>LogEngine: 记录执行结果
    LogEngine->>WebSocket: 推送日志
    WebSocket-->>WebUI: 更新日志显示
    
    ExecutionEngine-->>WebUI: 返回执行结果
```

## 数据流图符号说明

### 基本符号
- **圆角矩形**: 外部实体 (External Entity)
- **圆形**: 处理过程 (Process)
- **开口矩形**: 数据存储 (Data Store)
- **箭头**: 数据流 (Data Flow)

### 编号规则
- **0级**: 系统整体视图
- **1级**: 主要功能分解
- **2级**: 详细过程分解
- **D1, D2...**: 数据存储编号
- **1.0, 2.0...**: 主过程编号
- **1.1, 1.2...**: 子过程编号

### 数据流命名
- 使用名词短语
- 描述数据内容而非操作
- 中英文对照标注
- 保持简洁明确

这个数据流图完整展示了AI PowerShell系统中数据的流动过程，从用户输入到最终结果输出的各个环节，有助于理解系统的工作机制和数据处理逻辑。