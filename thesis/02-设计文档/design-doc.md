# AI PowerShell智能助手系统设计文档

**版本**: 1.0  
**日期**: 2025年11月  
**作者**: [学生姓名]  
**指导教师**: [教师姓名]

---

## 文档修订历史

| 版本 | 日期 | 修订内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2025-11 | 初始版本 | [学生姓名] |

---

## 目录

1. [概述](#1-概述)
   - 1.1 系统简介
   - 1.2 设计目标
   - 1.3 设计原则
2. [架构设计](#2-架构设计)
   - 2.1 整体架构
   - 2.2 层次划分
   - 2.3 模块关系
   - 2.4 数据流设计
3. [模块设计](#3-模块设计)
   - 3.1 主控制器
   - 3.2 AI引擎
   - 3.3 安全引擎
   - 3.4 执行引擎
   - 3.5 配置管理
   - 3.6 日志引擎
   - 3.7 存储引擎
   - 3.8 上下文管理
4. [数据设计](#4-数据设计)
   - 4.1 核心数据模型
   - 4.2 配置数据模型
   - 4.3 存储方案
   - 4.4 缓存策略
5. [接口设计](#5-接口设计)
   - 5.1 模块间接口
   - 5.2 外部接口
   - 5.3 API文档
   - 5.4 协议定义
6. [安全设计](#6-安全设计)
   - 6.1 安全架构
   - 6.2 威胁模型
   - 6.3 防护措施
   - 6.4 审计机制
7. [性能设计](#7-性能设计)
   - 7.1 性能目标
   - 7.2 优化策略
   - 7.3 资源管理
   - 7.4 监控方案
8. [部署设计](#8-部署设计)
   - 8.1 部署架构
   - 8.2 环境要求
   - 8.3 配置管理
   - 8.4 运维方案

---

## 1. 概述

### 1.1 系统简介

AI PowerShell智能助手是一个基于本地AI模型的智能命令行助手系统，旨在降低PowerShell的学习门槛，提高命令行操作效率，并保障系统安全。系统采用模块化架构设计，支持中文自然语言交互，能够将用户的自然语言描述智能转换为PowerShell命令，并提供三层安全保护机制。

**核心特性**：
- **智能翻译**：支持中文自然语言到PowerShell命令的智能转换
- **混合策略**：结合规则匹配和AI模型，兼顾速度和准确性
- **三层安全**：命令白名单、权限检查、沙箱执行的多层防护
- **跨平台支持**：支持Windows、Linux和macOS操作系统
- **本地处理**：基于本地AI模型，保护用户隐私
- **模块化架构**：高内聚低耦合，易于维护和扩展

**技术栈**：
- **编程语言**：Python 3.8+
- **AI框架**：LLaMA、Ollama、llama.cpp
- **配置管理**：YAML、Pydantic
- **容器技术**：Docker
- **测试框架**：pytest、pytest-cov
- **文档工具**：Markdown、Sphinx

### 1.2 设计目标

本系统的设计目标是构建一个高效、安全、易用的智能命令行助手，具体包括：

#### 1.2.1 功能目标

1. **准确的命令翻译**
   - 翻译准确率达到90%以上
   - 支持常见的PowerShell命令场景
   - 能够理解上下文和用户意图
   - 提供命令解释和备选方案

2. **全面的安全保护**
   - 识别并拦截危险命令
   - 实施权限检查和用户确认
   - 提供可选的沙箱隔离执行
   - 完整的审计日志追踪

3. **良好的用户体验**
   - 友好的命令行界面
   - 清晰的错误提示和帮助信息
   - 支持交互式和命令行两种模式
   - 完整的中文支持

4. **高效的性能表现**
   - 翻译响应时间小于2秒
   - 支持命令缓存和快速路径
   - 合理的资源占用
   - 支持并发请求处理

#### 1.2.2 非功能目标

1. **可靠性**
   - 系统可用性达到99%以上
   - 完善的错误处理和恢复机制
   - 数据持久化和备份

2. **可维护性**
   - 清晰的代码结构和注释
   - 完整的单元测试覆盖
   - 详细的技术文档

3. **可扩展性**
   - 支持添加新的AI提供商
   - 支持自定义安全规则
   - 支持插件机制
   - 支持多种存储后端

4. **安全性**
   - 多层安全防护机制
   - 敏感信息过滤和加密
   - 完整的审计追踪

### 1.3 设计原则

系统设计遵循以下核心原则：

#### 1.3.1 模块化设计

- **单一职责**：每个模块只负责一个明确的功能
- **高内聚低耦合**：模块内部紧密相关，模块之间松散耦合
- **接口驱动**：通过接口定义模块间的交互
- **依赖注入**：通过依赖注入实现模块解耦

#### 1.3.2 安全优先

- **纵深防御**：实施多层安全防护机制
- **最小权限**：遵循最小权限原则
- **默认拒绝**：对危险操作默认拒绝
- **审计追踪**：记录所有关键操作

#### 1.3.3 性能优化

- **缓存优先**：充分利用缓存减少重复计算
- **快速路径**：为常见场景提供快速处理路径
- **异步处理**：使用异步机制提高并发能力
- **资源控制**：合理控制资源占用

#### 1.3.4 用户体验

- **简单易用**：降低使用门槛，提供友好界面
- **清晰反馈**：提供明确的操作反馈和错误提示
- **容错设计**：对用户输入进行容错处理
- **渐进增强**：基础功能简单，高级功能可选

#### 1.3.5 可扩展性

- **插件架构**：支持通过插件扩展功能
- **配置驱动**：通过配置文件控制系统行为
- **抽象接口**：定义清晰的扩展点
- **开放标准**：使用开放的数据格式和协议

#### 1.3.6 跨平台兼容

- **平台抽象**：抽象平台差异，提供统一接口
- **编码规范**：统一使用UTF-8编码
- **路径处理**：使用跨平台的路径处理方法
- **依赖管理**：明确声明平台依赖

---

## 2. 架构设计

### 2.1 整体架构

系统采用分层架构设计，从上到下分为用户接口层、核心处理层和支持模块层三个层次。各层之间通过明确定义的接口进行交互，实现了高内聚低耦合的设计目标。

#### 2.1.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户接口层 (User Interface Layer)          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  CLI 界面    │  │  交互模式    │  │  Python API 接口     │  │
│  │  (CLI)       │  │  (Interactive)│  │  (API)               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      核心处理层 (Core Processing Layer)           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              主控制器 (PowerShellAssistant)               │  │
│  │         协调所有模块，处理用户请求，管理执行流程           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ AI引擎   │  │ 安全引擎 │  │ 执行引擎 │  │ 上下文管理   │  │
│  │(AIEngine)│  │(Security)│  │(Executor)│  │(Context)     │  │
│  │          │  │          │  │          │  │              │  │
│  │ 规则匹配 │  │ 白名单   │  │ 平台检测 │  │ 会话管理     │  │
│  │ AI翻译   │  │ 权限检查 │  │ 命令执行 │  │ 历史记录     │  │
│  │ 错误检测 │  │ 沙箱执行 │  │ 输出格式 │  │ 环境变量     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    支持模块层 (Support Module Layer)              │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ 配置管理 │  │ 日志引擎 │  │ 存储引擎 │  │ 模板引擎     │  │
│  │(Config)  │  │(Logging) │  │(Storage) │  │(Template)    │  │
│  │          │  │          │  │          │  │              │  │
│  │ YAML解析 │  │ 结构化   │  │ 文件存储 │  │ 规则模板     │  │
│  │ 验证     │  │ 过滤     │  │ 缓存     │  │ 提示词模板   │  │
│  │ 热重载   │  │ 审计     │  │ 历史     │  │ 输出模板     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      外部依赖 (External Dependencies)             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ PowerShell│  │ AI模型   │  │ Docker   │  │ 文件系统     │  │
│  │ Core      │  │(Ollama)  │  │ Engine   │  │(File System) │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 层次划分

#### 2.2.1 用户接口层 (User Interface Layer)

用户接口层负责与用户交互，接收用户输入并展示执行结果。

**主要组件**：

1. **CLI界面 (Command Line Interface)**
   - 提供命令行参数解析
   - 支持单次命令执行模式
   - 提供帮助和版本信息

2. **交互模式 (Interactive Mode)**
   - 提供REPL交互环境
   - 支持多轮对话
   - 提供命令历史和自动补全

3. **Python API接口**
   - 提供编程接口供其他Python程序调用
   - 支持同步和异步调用
   - 提供完整的类型提示

**设计特点**：
- 统一的输入输出处理
- 友好的错误提示
- 支持彩色输出和格式化
- 可配置的输出详细程度

#### 2.2.2 核心处理层 (Core Processing Layer)

核心处理层是系统的业务逻辑层，负责命令翻译、安全验证和执行控制。

**主要组件**：

1. **主控制器 (PowerShellAssistant)**
   - 协调所有核心模块
   - 管理请求处理流程
   - 处理异常和错误
   - 维护系统状态

2. **AI引擎 (AIEngine)**
   - 自然语言理解
   - 命令翻译和生成
   - 规则匹配和AI推理
   - 翻译结果验证

3. **安全引擎 (SecurityEngine)**
   - 命令安全验证
   - 风险等级评估
   - 权限检查
   - 沙箱执行管理

4. **执行引擎 (CommandExecutor)**
   - 跨平台命令执行
   - 进程管理
   - 输出捕获和格式化
   - 超时和资源控制

5. **上下文管理 (ContextManager)**
   - 会话状态管理
   - 命令历史记录
   - 环境变量管理
   - 工作目录跟踪

**设计特点**：
- 模块间通过接口交互
- 支持依赖注入
- 完整的错误处理
- 可测试性强

#### 2.2.3 支持模块层 (Support Module Layer)

支持模块层提供基础设施服务，支撑核心处理层的运行。

**主要组件**：

1. **配置管理 (ConfigManager)**
   - YAML配置文件解析
   - 配置验证和类型检查
   - 多层级配置合并
   - 配置热重载

2. **日志引擎 (LogEngine)**
   - 结构化日志记录
   - 敏感信息过滤
   - 日志级别控制
   - 审计追踪

3. **存储引擎 (StorageEngine)**
   - 文件存储管理
   - 缓存实现
   - 历史记录持久化
   - 数据序列化

4. **模板引擎 (TemplateEngine)**
   - 规则模板管理
   - AI提示词模板
   - 输出格式模板
   - 模板变量替换

**设计特点**：
- 提供通用的基础服务
- 支持多种实现方式
- 可配置和可扩展
- 独立于业务逻辑

### 2.3 模块关系

#### 2.3.1 依赖关系图

```
┌─────────────────────────────────────────────────────────────┐
│                         接口定义层                            │
│  (Interfaces: AIEngineInterface, SecurityEngineInterface,   │
│   ExecutorInterface, StorageInterface, etc.)                │
└─────────────────────────────────────────────────────────────┘
                              ↑
                              │ 依赖
                              │
┌─────────────────────────────────────────────────────────────┐
│                      PowerShellAssistant                     │
│                        (主控制器)                             │
└─────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓              ↓
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │AIEngine│    │Security│    │Executor│    │Context │
    └────────┘    └────────┘    └────────┘    └────────┘
         ↓              ↓              ↓              ↓
    ┌────────────────────────────────────────────────────┐
    │         Config, Logging, Storage, Template         │
    │                  (支持模块)                         │
    └────────────────────────────────────────────────────┘
```

#### 2.3.2 模块交互说明

1. **主控制器与核心模块**
   - 主控制器通过接口调用核心模块
   - 核心模块不直接相互调用，通过主控制器协调
   - 使用依赖注入实现模块解耦

2. **核心模块与支持模块**
   - 核心模块依赖支持模块提供的服务
   - 支持模块不依赖核心模块
   - 通过接口实现松耦合

3. **模块间通信**
   - 使用数据类(dataclass)传递数据
   - 通过返回值和异常处理错误
   - 支持同步和异步调用

### 2.4 数据流设计

#### 2.4.1 主要数据流程

```
用户输入
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. 输入处理                                              │
│    - 解析用户输入                                        │
│    - 验证输入格式                                        │
│    - 提取命令意图                                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 上下文构建                                            │
│    - 获取当前会话信息                                    │
│    - 加载命令历史                                        │
│    - 收集环境变量                                        │
│    - 确定工作目录                                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 3. AI翻译                                                │
│    - 检查翻译缓存                                        │
│    - 尝试规则匹配 (快速路径)                             │
│    - 调用AI模型生成 (如需要)                             │
│    - 错误检测和修正                                      │
│    - 生成命令建议                                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 安全验证                                              │
│    - 第一层: 命令白名单检查                              │
│    - 第二层: 权限验证                                    │
│    - 第三层: 沙箱执行决策 (可选)                         │
│    - 生成验证结果                                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 5. 用户确认                                              │
│    - 显示翻译结果                                        │
│    - 显示风险警告 (如有)                                 │
│    - 等待用户确认                                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 6. 命令执行                                              │
│    - 选择执行方式 (直接/沙箱)                            │
│    - 创建执行进程                                        │
│    - 捕获输出和错误                                      │
│    - 监控执行状态                                        │
│    - 处理超时和异常                                      │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ 7. 结果处理                                              │
│    - 格式化输出                                          │
│    - 保存到历史记录                                      │
│    - 更新缓存                                            │
│    - 记录审计日志                                        │
└─────────────────────────────────────────────────────────┘
    ↓
返回用户
```

#### 2.4.2 数据流特点

1. **流水线处理**
   - 每个阶段独立处理
   - 阶段间通过数据对象传递
   - 支持中断和回退

2. **错误传播**
   - 每个阶段可能产生错误
   - 错误向上传播到主控制器
   - 统一的错误处理机制

3. **性能优化**
   - 缓存检查在早期阶段
   - 快速路径优先
   - 异步处理耗时操作

4. **审计追踪**
   - 每个阶段记录日志
   - 关联ID追踪完整流程
   - 敏感信息过滤

---

## 3. 模块设计

### 3.1 主控制器 (PowerShellAssistant)

#### 3.1.1 模块职责

主控制器是系统的核心协调者，负责：
- 初始化和管理所有子模块
- 协调请求处理流程
- 管理系统生命周期
- 处理全局异常和错误
- 提供统一的对外接口

#### 3.1.2 类设计

```python
class PowerShellAssistant:
    """
    AI PowerShell智能助手主控制器
    
    协调AI引擎、安全引擎、执行引擎等模块，
    处理用户请求并返回执行结果。
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        ai_engine: Optional[AIEngineInterface] = None,
        security_engine: Optional[SecurityEngineInterface] = None,
        executor: Optional[ExecutorInterface] = None,
        context_manager: Optional[ContextManagerInterface] = None
    ):
        """初始化主控制器及所有子模块"""
        
    def process_request(
        self,
        user_input: str,
        context: Optional[Context] = None,
        auto_execute: bool = False
    ) -> ProcessResult:
        """
        处理用户请求的主流程
        
        Args:
            user_input: 用户输入的自然语言描述
            context: 可选的上下文信息
            auto_execute: 是否自动执行（跳过用户确认）
            
        Returns:
            ProcessResult: 包含翻译结果、验证结果和执行结果
        """
        
    def interactive_mode(self):
        """启动交互式模式"""
        
    def get_history(
        self,
        limit: int = 10,
        session_id: Optional[str] = None
    ) -> List[CommandEntry]:
        """获取命令历史"""
        
    def clear_cache(self):
        """清除翻译缓存"""
```

#### 3.1.3 时序图

```
用户 -> 主控制器: process_request(user_input)
主控制器 -> 上下文管理: build_context()
上下文管理 --> 主控制器: Context
主控制器 -> AI引擎: translate(user_input, context)
AI引擎 --> 主控制器: Suggestion
主控制器 -> 安全引擎: validate(command)
安全引擎 --> 主控制器: ValidationResult
主控制器 -> 用户: 显示命令和风险
用户 -> 主控制器: 确认执行
主控制器 -> 执行引擎: execute(command)
执行引擎 --> 主控制器: ExecutionResult
主控制器 -> 上下文管理: save_history(entry)
主控制器 --> 用户: ProcessResult
```

### 3.2 AI引擎 (AIEngine)

#### 3.2.1 模块职责

AI引擎负责自然语言到PowerShell命令的智能转换：
- 规则匹配处理
- AI模型推理
- 翻译结果验证
- 缓存管理
- 错误检测和修正

#### 3.2.2 组件架构

```
AIEngine
├── Translator (翻译器)
│   ├── RuleMatcher (规则匹配器)
│   ├── AIProvider (AI提供商)
│   └── ErrorDetector (错误检测器)
├── Cache (缓存管理)
└── TemplateManager (模板管理)
```

#### 3.2.3 类设计

```python
class AIEngine(AIEngineInterface):
    """AI引擎实现"""
    
    def __init__(
        self,
        config: AIConfig,
        storage: StorageInterface,
        logger: LoggerInterface
    ):
        """初始化AI引擎"""
        self.config = config
        self.rule_matcher = RuleMatcher(config.rules)
        self.ai_provider = self._create_ai_provider()
        self.error_detector = ErrorDetector()
        self.cache = TranslationCache(storage, config.cache_ttl)
        
    def translate(
        self,
        user_input: str,
        context: Optional[Context] = None
    ) -> Suggestion:
        """
        翻译用户输入为PowerShell命令
        
        处理流程:
        1. 检查缓存
        2. 尝试规则匹配
        3. 使用AI模型生成
        4. 错误检测
        5. 缓存结果
        """
        
    def _match_rules(self, user_input: str) -> Optional[str]:
        """规则匹配"""
        
    def _generate_with_ai(
        self,
        user_input: str,
        context: Optional[Context]
    ) -> str:
        """使用AI模型生成命令"""
        
    def _detect_errors(self, command: str) -> List[str]:
        """检测命令错误"""
```

#### 3.2.4 翻译策略

```
用户输入
    ↓
检查缓存 ──命中──→ 返回缓存结果
    ↓ 未命中
规则匹配 ──匹配──→ 返回规则结果
    ↓ 未匹配
AI模型生成
    ↓
错误检测 ──有错误──→ 尝试修正
    ↓ 无错误
缓存结果
    ↓
返回建议
```

### 3.3 安全引擎 (SecurityEngine)

#### 3.3.1 模块职责

安全引擎实施三层安全防护：
- 第一层：命令白名单验证
- 第二层：权限检查
- 第三层：沙箱执行（可选）
- 风险等级评估
- 审计日志记录

#### 3.3.2 三层架构

```
┌─────────────────────────────────────────┐
│         第一层：命令白名单验证            │
│  - 危险命令模式匹配                      │
│  - 风险等级评估                          │
│  - 基于规则的快速检查                    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         第二层：权限检查                 │
│  - 管理员权限检测                        │
│  - 用户确认流程                          │
│  - 权限提升请求                          │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         第三层：沙箱执行 (可选)          │
│  - Docker容器隔离                        │
│  - 资源限制                              │
│  - 网络隔离                              │
└─────────────────────────────────────────┘
```

#### 3.3.3 类设计

```python
class SecurityEngine(SecurityEngineInterface):
    """安全引擎实现"""
    
    def __init__(
        self,
        config: SecurityConfig,
        logger: LoggerInterface
    ):
        """初始化安全引擎"""
        self.config = config
        self.whitelist_checker = WhitelistChecker(config.dangerous_patterns)
        self.permission_checker = PermissionChecker()
        self.sandbox_manager = SandboxManager(config.sandbox)
        
    def validate(
        self,
        command: str,
        context: Optional[Context] = None
    ) -> ValidationResult:
        """
        验证命令安全性
        
        执行三层安全检查:
        1. 白名单检查
        2. 权限检查
        3. 沙箱决策
        """
        
    def check_whitelist(self, command: str) -> ValidationResult:
        """第一层：白名单检查"""
        
    def check_permissions(self, command: str) -> bool:
        """第二层：权限检查"""
        
    def execute_in_sandbox(
        self,
        command: str,
        timeout: int = 30
    ) -> ExecutionResult:
        """第三层：沙箱执行"""
```

#### 3.3.4 风险等级定义

```python
class RiskLevel(Enum):
    """命令风险等级"""
    SAFE = 0        # 安全命令，无风险
    LOW = 1         # 低风险，可直接执行
    MEDIUM = 2      # 中等风险，需要用户确认
    HIGH = 3        # 高风险，需要特殊确认
    CRITICAL = 4    # 极高风险，默认拒绝
```

### 3.4 执行引擎 (CommandExecutor)

#### 3.4.1 模块职责

执行引擎负责跨平台PowerShell命令执行：
- 平台检测和适配
- 进程创建和管理
- 输出捕获和格式化
- 超时控制
- 错误处理

#### 3.4.2 平台适配

```
CommandExecutor
├── WindowsExecutor (Windows平台)
│   ├── PowerShell 5.1
│   └── PowerShell Core
├── LinuxExecutor (Linux平台)
│   └── PowerShell Core
└── MacOSExecutor (macOS平台)
    └── PowerShell Core
```

#### 3.4.3 类设计

```python
class CommandExecutor(ExecutorInterface):
    """命令执行器"""
    
    def __init__(
        self,
        config: ExecutionConfig,
        logger: LoggerInterface
    ):
        """初始化执行器"""
        self.config = config
        self.platform = self._detect_platform()
        self.executor = self._create_platform_executor()
        
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        执行PowerShell命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            working_dir: 工作目录
            env: 环境变量
            
        Returns:
            ExecutionResult: 执行结果
        """
        
    def _detect_platform(self) -> Platform:
        """检测当前平台"""
        
    def _create_platform_executor(self) -> PlatformExecutor:
        """创建平台特定的执行器"""
        
    def format_output(
        self,
        output: str,
        format_type: str = 'text'
    ) -> str:
        """格式化输出"""
```

### 3.5 配置管理 (ConfigManager)

#### 3.5.1 模块职责

配置管理负责系统配置的加载、验证和管理：
- YAML配置文件解析
- 配置数据验证
- 多层级配置合并
- 配置热重载
- 默认值处理

#### 3.5.2 配置层次

```
配置优先级 (从高到低):
1. 命令行参数
2. 环境变量
3. 用户配置文件 (~/.ai-powershell/config.yaml)
4. 项目配置文件 (./config/default.yaml)
5. 默认配置 (代码中定义)
```

#### 3.5.3 类设计

```python
class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器"""
        self.config_path = config_path or self._get_default_path()
        self.config = self._load_config()
        
    def load_config(self, path: str) -> Config:
        """加载配置文件"""
        
    def validate_config(self, config_dict: Dict) -> Config:
        """验证配置数据"""
        
    def merge_configs(
        self,
        *configs: Dict
    ) -> Dict:
        """合并多个配置"""
        
    def reload(self):
        """重新加载配置"""
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
```

#### 3.5.4 配置模型

```python
class Config(BaseModel):
    """主配置模型"""
    ai: AIConfig
    security: SecurityConfig
    execution: ExecutionConfig
    logging: LoggingConfig
    storage: StorageConfig
    context: ContextConfig

class AIConfig(BaseModel):
    """AI引擎配置"""
    provider: str = Field(..., pattern='^(local|ollama|openai)$')
    model_name: str = 'llama2'
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(256, ge=1, le=4096)
    cache_enabled: bool = True
    cache_ttl: int = Field(3600, ge=0)
    rules_path: str = 'config/rules.yaml'
```

### 3.6 日志引擎 (LogEngine)

#### 3.6.1 模块职责

日志引擎提供结构化日志和审计追踪：
- 结构化日志记录
- 敏感信息过滤
- 日志级别控制
- 审计追踪
- 性能监控

#### 3.6.2 日志类型

```
日志类型:
├── 应用日志 (Application Log)
│   ├── DEBUG: 调试信息
│   ├── INFO: 一般信息
│   ├── WARNING: 警告信息
│   └── ERROR: 错误信息
├── 审计日志 (Audit Log)
│   ├── 用户请求
│   ├── 命令翻译
│   ├── 安全验证
│   └── 命令执行
└── 性能日志 (Performance Log)
    ├── 响应时间
    ├── 资源占用
    └── 缓存命中率
```

#### 3.6.3 类设计

```python
class LogEngine:
    """日志引擎"""
    
    def __init__(self, config: LoggingConfig):
        """初始化日志引擎"""
        self.config = config
        self.logger = self._setup_logger()
        self.filter = SensitiveDataFilter()
        
    def log_request(
        self,
        correlation_id: str,
        user_input: str,
        context: Context
    ):
        """记录用户请求"""
        
    def log_translation(
        self,
        correlation_id: str,
        user_input: str,
        command: str,
        confidence: float,
        method: str
    ):
        """记录翻译结果"""
        
    def log_validation(
        self,
        correlation_id: str,
        command: str,
        result: ValidationResult
    ):
        """记录安全验证"""
        
    def log_execution(
        self,
        correlation_id: str,
        command: str,
        result: ExecutionResult
    ):
        """记录命令执行"""
```

### 3.7 存储引擎 (StorageEngine)

#### 3.7.1 模块职责

存储引擎负责数据持久化和缓存：
- 文件存储管理
- 缓存实现
- 历史记录持久化
- 数据序列化
- 备份和恢复

#### 3.7.2 存储结构

```
~/.ai-powershell/
├── config/
│   └── user-config.yaml
├── data/
│   ├── history.jsonl
│   ├── cache.db
│   └── sessions/
│       ├── session-1.json
│       └── session-2.json
└── logs/
    ├── app.log
    ├── audit.log
    └── performance.log
```

#### 3.7.3 类设计

```python
class StorageEngine(StorageInterface):
    """存储引擎"""
    
    def __init__(self, config: StorageConfig):
        """初始化存储引擎"""
        self.config = config
        self.base_path = Path(config.base_path).expanduser()
        self._ensure_directories()
        
    def save_history(self, entry: CommandEntry) -> bool:
        """保存命令历史"""
        
    def load_history(
        self,
        limit: int = 100,
        session_id: Optional[str] = None
    ) -> List[CommandEntry]:
        """加载命令历史"""
        
    def save_cache(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ):
        """保存缓存"""
        
    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        
    def save_session(self, session: Session):
        """保存会话"""
        
    def load_session(self, session_id: str) -> Optional[Session]:
        """加载会话"""
```

### 3.8 上下文管理 (ContextManager)

#### 3.8.1 模块职责

上下文管理负责会话和环境管理：
- 会话生命周期管理
- 命令历史管理
- 环境变量跟踪
- 工作目录管理
- 上下文构建

#### 3.8.2 类设计

```python
class ContextManager(ContextManagerInterface):
    """上下文管理器"""
    
    def __init__(
        self,
        config: ContextConfig,
        storage: StorageInterface
    ):
        """初始化上下文管理器"""
        self.config = config
        self.storage = storage
        self.current_session = None
        
    def start_session(
        self,
        user_id: Optional[str] = None
    ) -> Session:
        """启动新会话"""
        
    def end_session(self):
        """结束当前会话"""
        
    def build_context(
        self,
        user_input: str
    ) -> Context:
        """构建请求上下文"""
        
    def add_command(self, entry: CommandEntry):
        """添加命令到历史"""
        
    def get_history(
        self,
        limit: int = 10
    ) -> List[CommandEntry]:
        """获取命令历史"""
```

---

## 4. 数据设计

### 4.1 核心数据模型

#### 4.1.1 Suggestion (命令建议)

命令建议是AI引擎翻译的输出结果，包含生成的命令及相关元数据。

```python
@dataclass
class Suggestion:
    """命令建议数据模型"""
    
    # 生成的PowerShell命令
    generated_command: str
    
    # 置信度分数 (0.0-1.0)
    confidence_score: float
    
    # 命令解释说明
    explanation: str
    
    # 备选命令列表
    alternatives: List[str] = field(default_factory=list)
    
    # 翻译方法 ('rule' | 'ai' | 'cache')
    translation_method: str = 'ai'
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 生成时间戳
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Suggestion':
        """从字典创建"""
```

**字段说明**：
- `generated_command`: 主要推荐的命令
- `confidence_score`: 翻译置信度，影响是否需要用户确认
- `explanation`: 对命令的中文解释，帮助用户理解
- `alternatives`: 其他可能的命令选项
- `translation_method`: 记录翻译来源，用于性能分析
- `metadata`: 扩展字段，存储额外信息

#### 4.1.2 ValidationResult (验证结果)

验证结果包含安全引擎的检查结果和风险评估。

```python
@dataclass
class ValidationResult:
    """安全验证结果"""
    
    # 是否通过验证
    is_valid: bool
    
    # 风险等级
    risk_level: RiskLevel
    
    # 警告信息列表
    warnings: List[str] = field(default_factory=list)
    
    # 是否需要用户确认
    requires_confirmation: bool = False
    
    # 是否需要管理员权限
    requires_admin: bool = False
    
    # 是否建议沙箱执行
    recommend_sandbox: bool = False
    
    # 匹配的危险模式
    matched_patterns: List[str] = field(default_factory=list)
    
    # 验证时间戳
    timestamp: datetime = field(default_factory=datetime.now)
```

**风险等级枚举**：
```python
class RiskLevel(Enum):
    """命令风险等级"""
    SAFE = 0        # 安全，可直接执行
    LOW = 1         # 低风险，记录日志
    MEDIUM = 2      # 中等风险，需要确认
    HIGH = 3        # 高风险，需要特殊确认
    CRITICAL = 4    # 极高风险，默认拒绝
```

#### 4.1.3 ExecutionResult (执行结果)

执行结果包含命令执行的输出和状态信息。

```python
@dataclass
class ExecutionResult:
    """命令执行结果"""
    
    # 是否执行成功
    success: bool
    
    # 标准输出
    output: str = ''
    
    # 错误输出
    error: str = ''
    
    # 返回码
    return_code: int = 0
    
    # 执行时间（秒）
    execution_time: float = 0.0
    
    # 执行方式 ('direct' | 'sandbox')
    execution_mode: str = 'direct'
    
    # 是否超时
    timed_out: bool = False
    
    # 执行时间戳
    timestamp: datetime = field(default_factory=datetime.now)
```

#### 4.1.4 Context (上下文)

上下文包含请求处理所需的环境信息。

```python
@dataclass
class Context:
    """请求上下文"""
    
    # 会话ID
    session_id: str
    
    # 用户ID（可选）
    user_id: Optional[str] = None
    
    # 工作目录
    working_directory: str = field(default_factory=os.getcwd)
    
    # 环境变量
    environment_vars: Dict[str, str] = field(default_factory=dict)
    
    # 命令历史（最近N条）
    command_history: List['CommandEntry'] = field(default_factory=list)
    
    # 平台信息
    platform: str = field(default_factory=lambda: sys.platform)
    
    # PowerShell版本
    powershell_version: Optional[str] = None
    
    # 关联ID（用于日志追踪）
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 创建时间戳
    timestamp: datetime = field(default_factory=datetime.now)
```

#### 4.1.5 CommandEntry (命令历史条目)

命令历史条目记录完整的命令执行信息。

```python
@dataclass
class CommandEntry:
    """命令历史条目"""
    
    # 命令ID
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 会话ID
    session_id: str = ''
    
    # 用户输入
    user_input: str = ''
    
    # 翻译后的命令
    translated_command: str = ''
    
    # 命令状态
    status: CommandStatus = CommandStatus.PENDING
    
    # 输出内容
    output: str = ''
    
    # 错误信息
    error: str = ''
    
    # 返回码
    return_code: int = 0
    
    # 执行时间
    execution_time: float = 0.0
    
    # 置信度分数
    confidence_score: float = 0.0
    
    # 风险等级
    risk_level: RiskLevel = RiskLevel.SAFE
    
    # 翻译方法
    translation_method: str = ''
    
    # 执行方式
    execution_mode: str = 'direct'
    
    # 时间戳
    timestamp: datetime = field(default_factory=datetime.now)
```

**命令状态枚举**：
```python
class CommandStatus(Enum):
    """命令执行状态"""
    PENDING = 'pending'         # 待执行
    TRANSLATING = 'translating' # 翻译中
    VALIDATING = 'validating'   # 验证中
    CONFIRMED = 'confirmed'     # 已确认
    EXECUTING = 'executing'     # 执行中
    SUCCESS = 'success'         # 成功
    FAILED = 'failed'           # 失败
    CANCELLED = 'cancelled'     # 已取消
    REJECTED = 'rejected'       # 已拒绝
```

#### 4.1.6 Session (会话)

会话管理用户的交互状态。

```python
@dataclass
class Session:
    """用户会话"""
    
    # 会话ID
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 用户ID
    user_id: Optional[str] = None
    
    # 会话状态
    status: SessionStatus = SessionStatus.ACTIVE
    
    # 命令历史
    command_history: List[CommandEntry] = field(default_factory=list)
    
    # 会话变量
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # 开始时间
    start_time: datetime = field(default_factory=datetime.now)
    
    # 结束时间
    end_time: Optional[datetime] = None
    
    # 最后活动时间
    last_activity: datetime = field(default_factory=datetime.now)
```

### 4.2 配置数据模型

#### 4.2.1 AIConfig (AI引擎配置)

```python
class AIConfig(BaseModel):
    """AI引擎配置"""
    
    # AI提供商 ('local' | 'ollama' | 'openai')
    provider: str = Field('ollama', pattern='^(local|ollama|openai)$')
    
    # 模型名称
    model_name: str = 'llama2'
    
    # 模型路径（本地模型）
    model_path: Optional[str] = None
    
    # API端点（远程模型）
    api_endpoint: Optional[str] = 'http://localhost:11434'
    
    # API密钥
    api_key: Optional[str] = None
    
    # 温度参数
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    
    # 最大生成令牌数
    max_tokens: int = Field(256, ge=1, le=4096)
    
    # 是否启用缓存
    cache_enabled: bool = True
    
    # 缓存TTL（秒）
    cache_ttl: int = Field(3600, ge=0)
    
    # 规则文件路径
    rules_path: str = 'config/rules.yaml'
    
    # 提示词模板路径
    prompt_template_path: str = 'config/prompts.yaml'
```

#### 4.2.2 SecurityConfig (安全引擎配置)

```python
class SecurityConfig(BaseModel):
    """安全引擎配置"""
    
    # 是否启用安全检查
    enabled: bool = True
    
    # 危险命令模式文件
    patterns_path: str = 'config/dangerous_patterns.yaml'
    
    # 默认风险等级阈值
    risk_threshold: RiskLevel = RiskLevel.MEDIUM
    
    # 是否自动拒绝高风险命令
    auto_reject_high_risk: bool = True
    
    # 是否启用沙箱
    sandbox_enabled: bool = False
    
    # 沙箱配置
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    
    # 是否记录审计日志
    audit_enabled: bool = True

class SandboxConfig(BaseModel):
    """沙箱配置"""
    
    # Docker镜像
    docker_image: str = 'mcr.microsoft.com/powershell:latest'
    
    # 内存限制（MB）
    memory_limit: int = Field(512, ge=128)
    
    # CPU配额（百分比）
    cpu_quota: int = Field(50, ge=1, le=100)
    
    # 是否禁用网络
    network_disabled: bool = True
    
    # 超时时间（秒）
    timeout: int = Field(30, ge=1)
```

#### 4.2.3 ExecutionConfig (执行引擎配置)

```python
class ExecutionConfig(BaseModel):
    """执行引擎配置"""
    
    # 默认超时时间（秒）
    default_timeout: int = Field(30, ge=1)
    
    # PowerShell可执行文件路径
    powershell_path: Optional[str] = None
    
    # 是否使用PowerShell Core
    use_pwsh: bool = True
    
    # 输出编码
    output_encoding: str = 'utf-8'
    
    # 是否捕获错误流
    capture_stderr: bool = True
    
    # 工作目录
    working_directory: Optional[str] = None
    
    # 环境变量
    environment: Dict[str, str] = Field(default_factory=dict)
```

#### 4.2.4 LoggingConfig (日志配置)

```python
class LoggingConfig(BaseModel):
    """日志配置"""
    
    # 日志级别
    level: str = Field('INFO', pattern='^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$')
    
    # 日志格式
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 日志文件路径
    log_file: Optional[str] = '~/.ai-powershell/logs/app.log'
    
    # 是否输出到控制台
    console_output: bool = True
    
    # 是否启用结构化日志
    structured: bool = True
    
    # 是否过滤敏感信息
    filter_sensitive: bool = True
    
    # 审计日志路径
    audit_log_file: Optional[str] = '~/.ai-powershell/logs/audit.log'
```

### 4.3 存储方案

#### 4.3.1 文件存储结构

```
~/.ai-powershell/                    # 用户数据目录
├── config/                          # 配置目录
│   ├── user-config.yaml            # 用户配置
│   ├── custom-rules.yaml           # 自定义规则
│   └── custom-patterns.yaml        # 自定义危险模式
├── data/                            # 数据目录
│   ├── history.jsonl               # 命令历史（JSONL格式）
│   ├── cache.db                    # 翻译缓存（SQLite）
│   └── sessions/                   # 会话数据
│       ├── active/                 # 活动会话
│       │   └── {session-id}.json
│       └── archived/               # 归档会话
│           └── {date}/
│               └── {session-id}.json
├── logs/                            # 日志目录
│   ├── app.log                     # 应用日志
│   ├── audit.log                   # 审计日志
│   └── performance.log             # 性能日志
└── backups/                         # 备份目录
    └── {date}/
        ├── history.jsonl
        └── cache.db
```

#### 4.3.2 数据持久化格式

**命令历史 (JSONL格式)**：
```jsonl
{"command_id": "uuid", "user_input": "显示时间", "translated_command": "Get-Date", ...}
{"command_id": "uuid", "user_input": "列出文件", "translated_command": "Get-ChildItem", ...}
```

**会话数据 (JSON格式)**：
```json
{
  "session_id": "uuid",
  "user_id": "user123",
  "status": "active",
  "command_history": [...],
  "variables": {},
  "start_time": "2025-11-11T10:00:00",
  "last_activity": "2025-11-11T10:30:00"
}
```

**翻译缓存 (SQLite)**：
```sql
CREATE TABLE translation_cache (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    confidence REAL,
    method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0
);

CREATE INDEX idx_expires_at ON translation_cache(expires_at);
```

### 4.4 缓存策略

#### 4.4.1 缓存层次

```
三级缓存架构:

L1: 内存缓存 (LRU Cache)
├── 容量: 1000条
├── TTL: 1小时
└── 命中率: ~80%

L2: 本地数据库缓存 (SQLite)
├── 容量: 无限制
├── TTL: 24小时
└── 命中率: ~15%

L3: 规则匹配 (快速路径)
├── 容量: 配置文件定义
├── TTL: 配置重载时更新
└── 命中率: ~5%
```

#### 4.4.2 缓存键生成

```python
def generate_cache_key(
    user_input: str,
    context: Optional[Context] = None
) -> str:
    """
    生成缓存键
    
    考虑因素:
    - 用户输入（标准化后）
    - 平台信息
    - PowerShell版本
    """
    normalized_input = normalize_input(user_input)
    platform = context.platform if context else sys.platform
    ps_version = context.powershell_version if context else 'default'
    
    key_parts = [normalized_input, platform, ps_version]
    key_string = '|'.join(key_parts)
    
    return hashlib.sha256(key_string.encode()).hexdigest()
```

#### 4.4.3 缓存失效策略

1. **基于时间的失效 (TTL)**
   - 内存缓存: 1小时
   - 数据库缓存: 24小时
   - 定期清理过期条目

2. **基于事件的失效**
   - 配置更新时清空相关缓存
   - 规则文件变更时清空规则缓存
   - 手动清除缓存命令

3. **基于容量的失效 (LRU)**
   - 内存缓存达到上限时淘汰最少使用的条目
   - 保留高频访问的条目

#### 4.4.4 缓存预热

```python
def warm_up_cache():
    """
    缓存预热
    
    在系统启动时预加载常用命令:
    - 从历史记录中提取高频命令
    - 预加载常用规则匹配结果
    - 提前初始化AI模型
    """
    common_commands = load_common_commands()
    for cmd in common_commands:
        cache.set(cmd.key, cmd.value)
```

---

## 5. 接口设计

### 5.1 模块间接口

模块间接口定义了系统内部各模块之间的交互规范，采用抽象基类(ABC)实现接口驱动开发。

#### 5.1.1 AIEngineInterface (AI引擎接口)

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class AIEngineInterface(ABC):
    """AI引擎接口定义"""
    
    @abstractmethod
    def translate(
        self,
        user_input: str,
        context: Optional[Context] = None
    ) -> Suggestion:
        """
        将用户输入翻译为PowerShell命令
        
        Args:
            user_input: 用户的自然语言输入
            context: 可选的上下文信息
            
        Returns:
            Suggestion: 命令建议对象
            
        Raises:
            TranslationError: 翻译失败时抛出
        """
        pass
    
    @abstractmethod
    def validate_command(self, command: str) -> bool:
        """
        验证命令语法是否正确
        
        Args:
            command: PowerShell命令
            
        Returns:
            bool: 命令是否有效
        """
        pass
    
    @abstractmethod
    def get_explanation(self, command: str) -> str:
        """
        获取命令的中文解释
        
        Args:
            command: PowerShell命令
            
        Returns:
            str: 命令的中文解释
        """
        pass
    
    @abstractmethod
    def clear_cache(self):
        """清除翻译缓存"""
        pass
```

#### 5.1.2 SecurityEngineInterface (安全引擎接口)

```python
class SecurityEngineInterface(ABC):
    """安全引擎接口定义"""
    
    @abstractmethod
    def validate(
        self,
        command: str,
        context: Optional[Context] = None
    ) -> ValidationResult:
        """
        验证命令的安全性
        
        Args:
            command: 要验证的PowerShell命令
            context: 可选的上下文信息
            
        Returns:
            ValidationResult: 验证结果对象
        """
        pass
    
    @abstractmethod
    def check_whitelist(self, command: str) -> ValidationResult:
        """
        检查命令是否在白名单中
        
        Args:
            command: PowerShell命令
            
        Returns:
            ValidationResult: 白名单检查结果
        """
        pass
    
    @abstractmethod
    def check_permissions(self, command: str) -> bool:
        """
        检查当前用户是否有执行权限
        
        Args:
            command: PowerShell命令
            
        Returns:
            bool: 是否有权限
        """
        pass
    
    @abstractmethod
    def execute_in_sandbox(
        self,
        command: str,
        timeout: int = 30
    ) -> ExecutionResult:
        """
        在沙箱中执行命令
        
        Args:
            command: PowerShell命令
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
```

#### 5.1.3 ExecutorInterface (执行器接口)

```python
class ExecutorInterface(ABC):
    """命令执行器接口定义"""
    
    @abstractmethod
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        执行PowerShell命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            working_dir: 工作目录
            env: 环境变量
            
        Returns:
            ExecutionResult: 执行结果
            
        Raises:
            ExecutionError: 执行失败时抛出
            TimeoutError: 超时时抛出
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        检查PowerShell是否可用
        
        Returns:
            bool: PowerShell是否可用
        """
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """
        获取PowerShell版本
        
        Returns:
            str: 版本字符串
        """
        pass
```

#### 5.1.4 StorageInterface (存储接口)

```python
class StorageInterface(ABC):
    """存储接口定义"""
    
    @abstractmethod
    def save_history(self, entry: CommandEntry) -> bool:
        """
        保存命令历史
        
        Args:
            entry: 命令历史条目
            
        Returns:
            bool: 是否保存成功
        """
        pass
    
    @abstractmethod
    def load_history(
        self,
        limit: int = 100,
        session_id: Optional[str] = None
    ) -> List[CommandEntry]:
        """
        加载命令历史
        
        Args:
            limit: 最大返回数量
            session_id: 可选的会话ID过滤
            
        Returns:
            List[CommandEntry]: 命令历史列表
        """
        pass
    
    @abstractmethod
    def save_cache(self, key: str, value: Any, ttl: int = 3600):
        """
        保存缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
        """
        pass
    
    @abstractmethod
    def get_cache(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值，不存在返回None
        """
        pass
```

#### 5.1.5 ContextManagerInterface (上下文管理接口)

```python
class ContextManagerInterface(ABC):
    """上下文管理器接口定义"""
    
    @abstractmethod
    def start_session(self, user_id: Optional[str] = None) -> Session:
        """
        启动新会话
        
        Args:
            user_id: 可选的用户ID
            
        Returns:
            Session: 会话对象
        """
        pass
    
    @abstractmethod
    def end_session(self):
        """结束当前会话"""
        pass
    
    @abstractmethod
    def build_context(self, user_input: str) -> Context:
        """
        构建请求上下文
        
        Args:
            user_input: 用户输入
            
        Returns:
            Context: 上下文对象
        """
        pass
    
    @abstractmethod
    def add_command(self, entry: CommandEntry):
        """
        添加命令到历史
        
        Args:
            entry: 命令历史条目
        """
        pass
```

### 5.2 外部接口

外部接口提供给用户和其他程序调用系统功能。

#### 5.2.1 Python API接口

**主要API类**：

```python
class PowerShellAssistant:
    """
    AI PowerShell智能助手主API
    
    示例:
        >>> assistant = PowerShellAssistant()
        >>> result = assistant.process("显示当前时间")
        >>> print(result.output)
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        **kwargs
    ):
        """
        初始化助手
        
        Args:
            config_path: 配置文件路径
            **kwargs: 其他配置参数
        """
        
    def process(
        self,
        user_input: str,
        auto_execute: bool = False,
        timeout: Optional[int] = None
    ) -> ProcessResult:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入的自然语言
            auto_execute: 是否自动执行（跳过确认）
            timeout: 超时时间
            
        Returns:
            ProcessResult: 处理结果
        """
        
    def translate_only(self, user_input: str) -> Suggestion:
        """
        仅翻译，不执行
        
        Args:
            user_input: 用户输入
            
        Returns:
            Suggestion: 翻译建议
        """
        
    def execute_command(
        self,
        command: str,
        validate: bool = True
    ) -> ExecutionResult:
        """
        直接执行PowerShell命令
        
        Args:
            command: PowerShell命令
            validate: 是否进行安全验证
            
        Returns:
            ExecutionResult: 执行结果
        """
        
    def get_history(self, limit: int = 10) -> List[CommandEntry]:
        """获取命令历史"""
        
    def interactive_mode(self):
        """启动交互式模式"""
```

**异步API支持**：

```python
class AsyncPowerShellAssistant:
    """异步版本的API"""
    
    async def process(
        self,
        user_input: str,
        auto_execute: bool = False
    ) -> ProcessResult:
        """异步处理请求"""
        
    async def translate_only(self, user_input: str) -> Suggestion:
        """异步翻译"""
        
    async def execute_command(self, command: str) -> ExecutionResult:
        """异步执行"""
```

#### 5.2.2 命令行接口 (CLI)

**命令格式**：

```bash
ai-powershell [OPTIONS] [COMMAND]
```

**主要命令**：

```bash
# 翻译并执行
ai-powershell "显示当前时间"

# 仅翻译，不执行
ai-powershell --translate-only "列出所有进程"

# 交互式模式
ai-powershell --interactive

# 查看历史
ai-powershell --history [--limit 20]

# 清除缓存
ai-powershell --clear-cache

# 显示版本
ai-powershell --version

# 显示帮助
ai-powershell --help
```

**选项参数**：

```
Options:
  -t, --translate-only      仅翻译，不执行
  -i, --interactive         启动交互式模式
  -y, --yes                 自动确认执行
  -s, --sandbox             在沙箱中执行
  --timeout SECONDS         设置超时时间
  --config PATH             指定配置文件
  --history                 显示命令历史
  --limit N                 历史记录数量限制
  --clear-cache             清除翻译缓存
  -v, --verbose             详细输出
  -q, --quiet               静默模式
  --version                 显示版本信息
  -h, --help                显示帮助信息
```

**退出码**：

```
0   - 成功
1   - 一般错误
2   - 翻译失败
3   - 验证失败
4   - 执行失败
5   - 超时
6   - 用户取消
```

#### 5.2.3 配置文件接口

**YAML配置格式**：

```yaml
# AI引擎配置
ai:
  provider: ollama
  model_name: llama2
  api_endpoint: http://localhost:11434
  temperature: 0.7
  max_tokens: 256
  cache_enabled: true
  cache_ttl: 3600
  rules_path: config/rules.yaml

# 安全引擎配置
security:
  enabled: true
  patterns_path: config/dangerous_patterns.yaml
  risk_threshold: MEDIUM
  auto_reject_high_risk: true
  sandbox_enabled: false
  sandbox:
    docker_image: mcr.microsoft.com/powershell:latest
    memory_limit: 512
    cpu_quota: 50
    network_disabled: true
    timeout: 30
  audit_enabled: true

# 执行引擎配置
execution:
  default_timeout: 30
  use_pwsh: true
  output_encoding: utf-8
  capture_stderr: true

# 日志配置
logging:
  level: INFO
  log_file: ~/.ai-powershell/logs/app.log
  console_output: true
  structured: true
  filter_sensitive: true
  audit_log_file: ~/.ai-powershell/logs/audit.log

# 存储配置
storage:
  base_path: ~/.ai-powershell
  history_max_entries: 1000
  cache_max_size: 10000
```

**规则文件格式**：

```yaml
# 翻译规则
rules:
  - pattern: "^显示(当前)?时间$"
    template: "Get-Date"
    confidence: 1.0
    
  - pattern: "^列出(所有)?文件$"
    template: "Get-ChildItem"
    confidence: 1.0
    
  - pattern: "^显示CPU最高的(\\d+)个进程$"
    template: "Get-Process | Sort-Object CPU -Descending | Select-Object -First {1}"
    confidence: 0.95
```

**危险模式文件格式**：

```yaml
# 危险命令模式
dangerous_patterns:
  - pattern: "Remove-Item.*-Recurse.*-Force"
    risk_level: CRITICAL
    description: "递归强制删除"
    
  - pattern: "Format-Volume"
    risk_level: CRITICAL
    description: "格式化磁盘"
    
  - pattern: "Stop-Computer.*-Force"
    risk_level: HIGH
    description: "强制关机"
```

### 5.3 API文档

#### 5.3.1 ProcessResult (处理结果)

```python
@dataclass
class ProcessResult:
    """完整的处理结果"""
    
    # 是否成功
    success: bool
    
    # 翻译建议
    suggestion: Optional[Suggestion] = None
    
    # 验证结果
    validation: Optional[ValidationResult] = None
    
    # 执行结果
    execution: Optional[ExecutionResult] = None
    
    # 错误信息
    error: Optional[str] = None
    
    # 处理时间（秒）
    processing_time: float = 0.0
```

#### 5.3.2 使用示例

**基本使用**：

```python
from ai_powershell import PowerShellAssistant

# 创建助手实例
assistant = PowerShellAssistant()

# 处理请求
result = assistant.process("显示当前时间")

if result.success:
    print(f"命令: {result.suggestion.generated_command}")
    print(f"输出: {result.execution.output}")
else:
    print(f"错误: {result.error}")
```

**仅翻译**：

```python
# 仅翻译，不执行
suggestion = assistant.translate_only("列出所有进程")

print(f"命令: {suggestion.generated_command}")
print(f"解释: {suggestion.explanation}")
print(f"置信度: {suggestion.confidence_score}")
```

**自定义配置**：

```python
# 使用自定义配置
assistant = PowerShellAssistant(
    config_path="my-config.yaml"
)

# 或通过参数配置
assistant = PowerShellAssistant(
    ai_provider="ollama",
    model_name="llama2",
    sandbox_enabled=True
)
```

**异步使用**：

```python
import asyncio
from ai_powershell import AsyncPowerShellAssistant

async def main():
    assistant = AsyncPowerShellAssistant()
    result = await assistant.process("显示系统信息")
    print(result.execution.output)

asyncio.run(main())
```

### 5.4 协议定义

#### 5.4.1 错误处理协议

**异常层次结构**：

```python
class PowerShellAssistantError(Exception):
    """基础异常类"""
    pass

class TranslationError(PowerShellAssistantError):
    """翻译错误"""
    pass

class ValidationError(PowerShellAssistantError):
    """验证错误"""
    pass

class ExecutionError(PowerShellAssistantError):
    """执行错误"""
    pass

class ConfigurationError(PowerShellAssistantError):
    """配置错误"""
    pass

class TimeoutError(PowerShellAssistantError):
    """超时错误"""
    pass
```

**错误响应格式**：

```python
@dataclass
class ErrorResponse:
    """错误响应"""
    
    # 错误代码
    error_code: str
    
    # 错误消息
    error_message: str
    
    # 详细信息
    details: Optional[Dict[str, Any]] = None
    
    # 建议操作
    suggestions: List[str] = field(default_factory=list)
```

#### 5.4.2 日志协议

**结构化日志格式**：

```json
{
  "timestamp": "2025-11-11T10:30:00.123Z",
  "level": "INFO",
  "correlation_id": "uuid",
  "module": "ai_engine",
  "event": "translation_completed",
  "data": {
    "user_input": "显示时间",
    "command": "Get-Date",
    "confidence": 0.95,
    "method": "rule",
    "duration_ms": 5
  }
}
```

#### 5.4.3 审计协议

**审计日志格式**：

```json
{
  "timestamp": "2025-11-11T10:30:00.123Z",
  "correlation_id": "uuid",
  "session_id": "session-uuid",
  "user_id": "user123",
  "event_type": "command_executed",
  "command": "Get-Date",
  "risk_level": "SAFE",
  "execution_mode": "direct",
  "success": true,
  "duration_ms": 150
}
```

---

## 6. 安全设计

### 6.1 安全架构

系统采用纵深防御策略，实施三层安全防护机制，确保命令执行的安全性。

#### 6.1.1 三层防护架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户输入                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  第一层：命令白名单验证 (Whitelist Validation)               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ • 危险命令模式匹配                                     │  │
│  │ • 风险等级评估 (SAFE/LOW/MEDIUM/HIGH/CRITICAL)        │  │
│  │ • 基于规则的快速检查                                   │  │
│  │ • 30+种危险模式识别                                    │  │
│  └───────────────────────────────────────────────────────┘  │
│  决策: 拒绝 CRITICAL 级别命令                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  第二层：权限检查 (Permission Check)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ • 管理员权限检测                                       │  │
│  │ • 用户确认流程                                         │  │
│  │ • 风险警告展示                                         │  │
│  │ • 操作审计记录                                         │  │
│  └───────────────────────────────────────────────────────┘  │
│  决策: HIGH/MEDIUM 级别需要用户确认                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  第三层：沙箱执行 (Sandbox Execution) [可选]                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ • Docker容器隔离                                       │  │
│  │ • 资源限制 (CPU/内存/网络)                             │  │
│  │ • 文件系统隔离                                         │  │
│  │ • 超时控制                                             │  │
│  └───────────────────────────────────────────────────────┘  │
│  决策: 高风险命令在隔离环境中执行                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    安全执行
```

#### 6.1.2 安全设计原则

1. **纵深防御 (Defense in Depth)**
   - 多层安全机制，任何一层失效不会导致系统完全暴露
   - 每层独立工作，互为补充

2. **最小权限 (Least Privilege)**
   - 默认以普通用户权限运行
   - 仅在必要时请求管理员权限
   - 沙箱环境限制资源访问

3. **默认拒绝 (Deny by Default)**
   - 对未知或高风险命令默认拒绝
   - 需要明确的用户确认才能执行
   - 白名单优于黑名单

4. **审计追踪 (Audit Trail)**
   - 记录所有命令执行
   - 追踪安全事件
   - 支持事后分析

### 6.2 威胁模型

#### 6.2.1 威胁识别

**T1: 恶意命令注入**
- **描述**: 攻击者通过构造特殊输入注入危险命令
- **影响**: 数据丢失、系统破坏、权限提升
- **可能性**: 中等
- **严重性**: 高

**T2: 权限提升攻击**
- **描述**: 利用系统漏洞获取管理员权限
- **影响**: 完全控制系统
- **可能性**: 低
- **严重性**: 极高

**T3: 资源耗尽攻击**
- **描述**: 执行消耗大量资源的命令导致系统不可用
- **影响**: 拒绝服务
- **可能性**: 中等
- **严重性**: 中等

**T4: 信息泄露**
- **描述**: 通过命令输出泄露敏感信息
- **影响**: 隐私泄露、凭证暴露
- **可能性**: 中等
- **严重性**: 中等

**T5: 配置篡改**
- **描述**: 修改系统配置或安全规则
- **影响**: 绕过安全机制
- **可能性**: 低
- **严重性**: 高

#### 6.2.2 威胁矩阵

| 威胁 | 可能性 | 严重性 | 风险等级 | 缓解措施 |
|------|--------|--------|----------|----------|
| T1: 恶意命令注入 | 中 | 高 | 高 | 白名单验证、模式匹配 |
| T2: 权限提升 | 低 | 极高 | 高 | 权限检查、用户确认 |
| T3: 资源耗尽 | 中 | 中 | 中 | 超时控制、资源限制 |
| T4: 信息泄露 | 中 | 中 | 中 | 敏感信息过滤 |
| T5: 配置篡改 | 低 | 高 | 中 | 配置文件权限控制 |

### 6.3 防护措施

#### 6.3.1 第一层：命令白名单验证

**危险命令模式库**：

```python
DANGEROUS_PATTERNS = [
    # 文件删除类
    {
        'pattern': r'Remove-Item.*-Recurse.*-Force',
        'risk_level': RiskLevel.CRITICAL,
        'description': '递归强制删除文件',
        'reason': '可能导致重要数据丢失'
    },
    {
        'pattern': r'rm\s+-rf\s+/',
        'risk_level': RiskLevel.CRITICAL,
        'description': '删除根目录',
        'reason': '会破坏整个系统'
    },
    
    # 磁盘操作类
    {
        'pattern': r'Format-Volume',
        'risk_level': RiskLevel.CRITICAL,
        'description': '格式化磁盘',
        'reason': '会清除所有数据'
    },
    {
        'pattern': r'Clear-Disk.*-RemoveData',
        'risk_level': RiskLevel.CRITICAL,
        'description': '清除磁盘数据',
        'reason': '不可恢复的数据丢失'
    },
    
    # 系统控制类
    {
        'pattern': r'Stop-Computer.*-Force',
        'risk_level': RiskLevel.HIGH,
        'description': '强制关机',
        'reason': '可能导致数据丢失'
    },
    {
        'pattern': r'Restart-Computer.*-Force',
        'risk_level': RiskLevel.HIGH,
        'description': '强制重启',
        'reason': '可能中断重要任务'
    },
    
    # 注册表操作类
    {
        'pattern': r'Remove-ItemProperty.*HKLM:',
        'risk_level': RiskLevel.HIGH,
        'description': '删除系统注册表项',
        'reason': '可能导致系统不稳定'
    },
    {
        'pattern': r'Set-ItemProperty.*HKLM:.*-Force',
        'risk_level': RiskLevel.MEDIUM,
        'description': '修改系统注册表',
        'reason': '可能影响系统配置'
    },
    
    # 网络操作类
    {
        'pattern': r'Invoke-WebRequest.*\|\s*Invoke-Expression',
        'risk_level': RiskLevel.CRITICAL,
        'description': '下载并执行远程脚本',
        'reason': '可能执行恶意代码'
    },
    {
        'pattern': r'iwr.*\|\s*iex',
        'risk_level': RiskLevel.CRITICAL,
        'description': '下载并执行远程脚本（简写）',
        'reason': '可能执行恶意代码'
    },
    
    # 进程操作类
    {
        'pattern': r'Stop-Process.*-Force.*-Name\s+\*',
        'risk_level': RiskLevel.HIGH,
        'description': '强制终止所有进程',
        'reason': '会导致系统不稳定'
    },
    
    # 服务操作类
    {
        'pattern': r'Stop-Service.*-Force',
        'risk_level': RiskLevel.MEDIUM,
        'description': '强制停止服务',
        'reason': '可能影响系统功能'
    },
    
    # 防火墙操作类
    {
        'pattern': r'Set-NetFirewallProfile.*-Enabled\s+False',
        'risk_level': RiskLevel.HIGH,
        'description': '禁用防火墙',
        'reason': '降低系统安全性'
    }
]
```

**风险评分算法**：

```python
def calculate_risk_score(command: str) -> Tuple[RiskLevel, List[str]]:
    """
    计算命令的风险分数
    
    Returns:
        (风险等级, 匹配的模式列表)
    """
    max_risk = RiskLevel.SAFE
    matched_patterns = []
    
    for pattern_def in DANGEROUS_PATTERNS:
        if re.search(pattern_def['pattern'], command, re.IGNORECASE):
            matched_patterns.append(pattern_def['description'])
            if pattern_def['risk_level'].value > max_risk.value:
                max_risk = pattern_def['risk_level']
    
    # 检查命令组合（多个中等风险命令组合可能构成高风险）
    if len(matched_patterns) >= 2:
        max_risk = RiskLevel(min(max_risk.value + 1, RiskLevel.CRITICAL.value))
    
    return max_risk, matched_patterns
```

#### 6.3.2 第二层：权限检查

**权限检测**：

```python
def check_admin_required(command: str) -> bool:
    """检查命令是否需要管理员权限"""
    
    admin_required_patterns = [
        r'New-Service',
        r'Remove-Service',
        r'Set-Service',
        r'Install-Module',
        r'Set-ExecutionPolicy',
        r'New-NetFirewallRule',
        r'Set-ItemProperty.*HKLM:',
        r'Format-Volume',
        r'New-Partition'
    ]
    
    for pattern in admin_required_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    
    return False

def is_admin() -> bool:
    """检查当前用户是否有管理员权限"""
    
    if sys.platform == 'win32':
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:
        return os.geteuid() == 0
```

**用户确认流程**：

```python
def request_user_confirmation(
    command: str,
    risk_level: RiskLevel,
    warnings: List[str]
) -> bool:
    """
    请求用户确认
    
    根据风险等级显示不同的确认界面
    """
    
    if risk_level == RiskLevel.CRITICAL:
        print("⛔ 极高风险命令！")
        print(f"命令: {command}")
        print("警告:")
        for warning in warnings:
            print(f"  • {warning}")
        print("\n此命令可能造成严重后果，建议不要执行！")
        
        # 需要输入完整的确认短语
        confirmation = input("如果确定要执行，请输入 'I UNDERSTAND THE RISK': ")
        return confirmation == "I UNDERSTAND THE RISK"
        
    elif risk_level == RiskLevel.HIGH:
        print("⚠️  高风险命令")
        print(f"命令: {command}")
        print("警告:")
        for warning in warnings:
            print(f"  • {warning}")
        
        # 需要明确输入yes
        confirmation = input("确定要执行吗？(输入 'yes' 确认): ")
        return confirmation.lower() == 'yes'
        
    elif risk_level == RiskLevel.MEDIUM:
        print("⚡ 中等风险命令")
        print(f"命令: {command}")
        
        # 简单的y/n确认
        confirmation = input("确定要执行吗？(y/n): ")
        return confirmation.lower() in ['y', 'yes']
        
    else:
        # 低风险或安全命令，自动通过
        return True
```

#### 6.3.3 第三层：沙箱执行

**Docker沙箱配置**：

```python
class SandboxManager:
    """沙箱管理器"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.docker_client = docker.from_env()
        
    def execute_in_sandbox(
        self,
        command: str,
        timeout: int = 30
    ) -> ExecutionResult:
        """
        在Docker容器中执行命令
        
        安全特性:
        - 文件系统隔离
        - 网络隔离
        - 资源限制
        - 只读根文件系统
        """
        
        try:
            # 创建容器配置
            container_config = {
                'image': self.config.docker_image,
                'command': ['pwsh', '-Command', command],
                'detach': True,
                'remove': True,
                
                # 资源限制
                'mem_limit': f'{self.config.memory_limit}m',
                'cpu_quota': self.config.cpu_quota * 1000,
                'cpu_period': 100000,
                
                # 网络隔离
                'network_disabled': self.config.network_disabled,
                
                # 文件系统
                'read_only': True,
                'tmpfs': {'/tmp': 'size=100m'},
                
                # 安全选项
                'security_opt': ['no-new-privileges'],
                'cap_drop': ['ALL'],
                
                # 用户
                'user': 'nobody'
            }
            
            # 创建并启动容器
            container = self.docker_client.containers.run(**container_config)
            
            # 等待执行完成
            result = container.wait(timeout=timeout)
            
            # 获取输出
            output = container.logs(stdout=True, stderr=False).decode('utf-8')
            error = container.logs(stdout=False, stderr=True).decode('utf-8')
            
            return ExecutionResult(
                success=(result['StatusCode'] == 0),
                output=output,
                error=error,
                return_code=result['StatusCode'],
                execution_mode='sandbox'
            )
            
        except docker.errors.ContainerError as e:
            return ExecutionResult(
                success=False,
                error=f"容器执行错误: {str(e)}",
                execution_mode='sandbox'
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"沙箱执行失败: {str(e)}",
                execution_mode='sandbox'
            )
```

**资源限制策略**：

```yaml
sandbox:
  # 内存限制
  memory_limit: 512  # MB
  memory_swap: 512   # MB (总内存 = memory + swap)
  
  # CPU限制
  cpu_quota: 50      # 50% CPU
  cpu_shares: 512    # 相对权重
  
  # 磁盘限制
  storage_limit: 1024  # MB
  
  # 进程限制
  pids_limit: 100    # 最大进程数
  
  # 网络限制
  network_disabled: true
  
  # 超时限制
  timeout: 30        # 秒
```

### 6.4 审计机制

#### 6.4.1 审计日志记录

**审计事件类型**：

```python
class AuditEventType(Enum):
    """审计事件类型"""
    USER_REQUEST = 'user_request'           # 用户请求
    TRANSLATION = 'translation'             # 命令翻译
    VALIDATION = 'validation'               # 安全验证
    PERMISSION_CHECK = 'permission_check'   # 权限检查
    USER_CONFIRMATION = 'user_confirmation' # 用户确认
    COMMAND_EXECUTION = 'command_execution' # 命令执行
    SANDBOX_EXECUTION = 'sandbox_execution' # 沙箱执行
    SECURITY_VIOLATION = 'security_violation' # 安全违规
    ERROR = 'error'                         # 错误事件
```

**审计日志格式**：

```python
@dataclass
class AuditLog:
    """审计日志条目"""
    
    # 时间戳
    timestamp: datetime
    
    # 关联ID
    correlation_id: str
    
    # 会话ID
    session_id: str
    
    # 用户ID
    user_id: Optional[str]
    
    # 事件类型
    event_type: AuditEventType
    
    # 事件详情
    details: Dict[str, Any]
    
    # 风险等级
    risk_level: Optional[RiskLevel] = None
    
    # 是否成功
    success: bool = True
    
    # IP地址
    ip_address: Optional[str] = None
    
    # 用户代理
    user_agent: Optional[str] = None
```

**审计日志示例**：

```json
{
  "timestamp": "2025-11-11T10:30:00.123Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "session-123",
  "user_id": "user@example.com",
  "event_type": "command_execution",
  "details": {
    "user_input": "删除临时文件",
    "translated_command": "Remove-Item -Path $env:TEMP\\* -Recurse",
    "confidence_score": 0.92,
    "translation_method": "ai",
    "execution_mode": "direct",
    "execution_time_ms": 1250,
    "return_code": 0
  },
  "risk_level": "MEDIUM",
  "success": true,
  "ip_address": "192.168.1.100"
}
```

#### 6.4.2 安全事件监控

**实时监控指标**：

```python
class SecurityMetrics:
    """安全监控指标"""
    
    # 命令统计
    total_commands: int = 0
    safe_commands: int = 0
    risky_commands: int = 0
    blocked_commands: int = 0
    
    # 风险分布
    risk_distribution: Dict[RiskLevel, int] = {}
    
    # 沙箱使用
    sandbox_executions: int = 0
    sandbox_failures: int = 0
    
    # 权限请求
    admin_requests: int = 0
    admin_granted: int = 0
    admin_denied: int = 0
    
    # 用户确认
    confirmations_requested: int = 0
    confirmations_approved: int = 0
    confirmations_rejected: int = 0
    
    def get_risk_rate(self) -> float:
        """计算风险命令比率"""
        if self.total_commands == 0:
            return 0.0
        return self.risky_commands / self.total_commands
    
    def get_block_rate(self) -> float:
        """计算拦截率"""
        if self.total_commands == 0:
            return 0.0
        return self.blocked_commands / self.total_commands
```

**告警规则**：

```python
class SecurityAlertRule:
    """安全告警规则"""
    
    # 高风险命令频率告警
    HIGH_RISK_THRESHOLD = 5  # 5分钟内超过5次高风险命令
    
    # 拦截率异常告警
    BLOCK_RATE_THRESHOLD = 0.3  # 拦截率超过30%
    
    # 沙箱失败率告警
    SANDBOX_FAILURE_THRESHOLD = 0.1  # 沙箱失败率超过10%
    
    # 权限提升频率告警
    ADMIN_REQUEST_THRESHOLD = 10  # 1小时内超过10次权限请求
```

#### 6.4.3 合规性支持

**数据保留策略**：

```python
class DataRetentionPolicy:
    """数据保留策略"""
    
    # 审计日志保留期
    audit_log_retention_days: int = 90
    
    # 命令历史保留期
    command_history_retention_days: int = 30
    
    # 会话数据保留期
    session_data_retention_days: int = 7
    
    # 缓存数据保留期
    cache_retention_days: int = 1
    
    # 归档策略
    archive_enabled: bool = True
    archive_path: str = '~/.ai-powershell/archives'
```

**隐私保护**：

```python
class PrivacyProtection:
    """隐私保护措施"""
    
    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        r'\b\d{16}\b',                    # 信用卡号
        r'\b\d{3}-\d{2}-\d{4}\b',        # 社会安全号
        r'password\s*=\s*\S+',            # 密码
        r'api[_-]?key\s*=\s*\S+',        # API密钥
        r'token\s*=\s*\S+',               # 令牌
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # 邮箱
    ]
    
    @staticmethod
    def filter_sensitive_data(text: str) -> str:
        """过滤敏感信息"""
        filtered = text
        for pattern in PrivacyProtection.SENSITIVE_PATTERNS:
            filtered = re.sub(pattern, '[REDACTED]', filtered, flags=re.IGNORECASE)
        return filtered
```

---

## 7. 性能设计

### 7.1 性能目标

系统性能目标基于用户体验和资源效率的平衡考虑。

#### 7.1.1 响应时间目标

| 操作类型 | 目标响应时间 | 最大可接受时间 | 备注 |
|---------|-------------|---------------|------|
| 缓存命中翻译 | < 10ms | 50ms | 内存缓存查询 |
| 规则匹配翻译 | < 50ms | 200ms | 正则表达式匹配 |
| AI模型翻译 | < 2s | 5s | 本地模型推理 |
| 安全验证 | < 10ms | 50ms | 模式匹配 |
| 命令执行 | 取决于命令 | 30s (默认超时) | 可配置 |
| 沙箱启动 | < 3s | 10s | Docker容器创建 |

#### 7.1.2 吞吐量目标

| 指标 | 目标值 | 测试条件 |
|------|--------|----------|
| 并发请求处理 | 10 req/s | 单机部署 |
| 缓存命中率 | > 60% | 正常使用场景 |
| 翻译准确率 | > 90% | 常见命令场景 |

#### 7.1.3 资源占用目标

| 资源类型 | 目标值 | 峰值限制 |
|---------|--------|----------|
| 内存占用 | < 300MB | 512MB (不含AI模型) |
| CPU占用 | < 10% | 50% (空闲时) |
| 磁盘占用 | < 100MB | 500MB (含日志和缓存) |
| 启动时间 | < 2s | 5s |

### 7.2 优化策略

#### 7.2.1 缓存优化

**多级缓存架构**：

```python
class CacheStrategy:
    """缓存策略"""
    
    def __init__(self):
        # L1: 内存LRU缓存
        self.memory_cache = LRUCache(maxsize=1000)
        
        # L2: 本地数据库缓存
        self.db_cache = DatabaseCache(
            path='~/.ai-powershell/cache.db',
            ttl=86400  # 24小时
        )
        
        # L3: 规则缓存
        self.rule_cache = RuleCache()
        
    def get(self, key: str) -> Optional[Any]:
        """
        多级缓存查询
        
        查询顺序: L1 -> L2 -> L3 -> None
        """
        # 尝试L1缓存
        value = self.memory_cache.get(key)
        if value is not None:
            self.metrics.l1_hits += 1
            return value
        
        # 尝试L2缓存
        value = self.db_cache.get(key)
        if value is not None:
            self.metrics.l2_hits += 1
            # 回填L1缓存
            self.memory_cache.set(key, value)
            return value
        
        # 尝试L3规则缓存
        value = self.rule_cache.get(key)
        if value is not None:
            self.metrics.l3_hits += 1
            # 回填L1和L2缓存
            self.memory_cache.set(key, value)
            self.db_cache.set(key, value)
            return value
        
        self.metrics.cache_misses += 1
        return None
```

**缓存预热**：

```python
def warm_up_cache():
    """
    系统启动时预热缓存
    
    策略:
    1. 加载最近使用的命令
    2. 预加载高频命令
    3. 预编译规则模式
    """
    # 从历史记录加载高频命令
    history = load_recent_history(limit=100)
    command_freq = Counter(entry.user_input for entry in history)
    
    # 预加载前20个高频命令
    for user_input, _ in command_freq.most_common(20):
        key = generate_cache_key(user_input)
        # 预加载到缓存
        cache.warm_up(key)
    
    # 预编译规则
    rule_matcher.compile_patterns()
```

**智能缓存失效**：

```python
class SmartCacheInvalidation:
    """智能缓存失效"""
    
    def on_config_change(self, config_type: str):
        """配置变更时的缓存失效"""
        if config_type == 'rules':
            # 规则变更，清空规则相关缓存
            self.cache.invalidate_by_tag('rule')
        elif config_type == 'ai':
            # AI配置变更，清空AI生成的缓存
            self.cache.invalidate_by_tag('ai')
    
    def on_low_hit_rate(self):
        """缓存命中率低时的优化"""
        # 分析缓存使用模式
        patterns = self.analyze_cache_patterns()
        
        # 调整缓存大小
        if patterns['size_insufficient']:
            self.cache.resize(new_size=self.cache.size * 1.5)
        
        # 调整TTL
        if patterns['ttl_too_short']:
            self.cache.update_ttl(new_ttl=self.cache.ttl * 2)
```

#### 7.2.2 AI模型优化

**模型加载优化**：

```python
class LazyModelLoader:
    """延迟加载AI模型"""
    
    def __init__(self):
        self._model = None
        self._loading = False
        
    @property
    def model(self):
        """延迟加载模型"""
        if self._model is None and not self._loading:
            self._loading = True
            self._model = self._load_model()
            self._loading = False
        return self._model
    
    def _load_model(self):
        """
        加载模型
        
        优化措施:
        - 使用量化模型减少内存占用
        - 启用模型缓存
        - 预分配内存
        """
        return load_quantized_model(
            model_name=self.config.model_name,
            quantization='int8',
            cache_dir='~/.ai-powershell/models'
        )
```

**推理优化**：

```python
class OptimizedInference:
    """优化的推理引擎"""
    
    def __init__(self):
        self.batch_queue = Queue(maxsize=10)
        self.batch_size = 4
        self.batch_timeout = 0.1  # 100ms
        
    async def infer(self, prompt: str) -> str:
        """
        批量推理
        
        将多个请求合并为批次处理，提高GPU利用率
        """
        # 添加到批次队列
        future = asyncio.Future()
        self.batch_queue.put((prompt, future))
        
        # 等待批次处理
        return await future
    
    async def _batch_processor(self):
        """批次处理器"""
        while True:
            batch = []
            
            # 收集批次
            try:
                while len(batch) < self.batch_size:
                    item = await asyncio.wait_for(
                        self.batch_queue.get(),
                        timeout=self.batch_timeout
                    )
                    batch.append(item)
            except asyncio.TimeoutError:
                pass
            
            if batch:
                # 批量推理
                prompts = [item[0] for item in batch]
                results = self.model.batch_infer(prompts)
                
                # 返回结果
                for (_, future), result in zip(batch, results):
                    future.set_result(result)
```

**快速路径优先**：

```python
def translate_with_fast_path(user_input: str) -> Suggestion:
    """
    优先使用快速路径
    
    路径优先级:
    1. 缓存查询 (< 10ms)
    2. 规则匹配 (< 50ms)
    3. AI推理 (< 2s)
    """
    # 1. 检查缓存
    cache_key = generate_cache_key(user_input)
    cached = cache.get(cache_key)
    if cached:
        return Suggestion(
            generated_command=cached,
            confidence_score=1.0,
            translation_method='cache'
        )
    
    # 2. 尝试规则匹配
    rule_result = rule_matcher.match(user_input)
    if rule_result:
        return Suggestion(
            generated_command=rule_result.command,
            confidence_score=rule_result.confidence,
            translation_method='rule'
        )
    
    # 3. 使用AI模型
    ai_result = ai_model.generate(user_input)
    
    # 缓存结果
    cache.set(cache_key, ai_result.command)
    
    return Suggestion(
        generated_command=ai_result.command,
        confidence_score=ai_result.confidence,
        translation_method='ai'
    )
```

#### 7.2.3 并发处理优化

**异步处理架构**：

```python
class AsyncRequestHandler:
    """异步请求处理器"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.semaphore = asyncio.Semaphore(10)
        
    async def handle_request(self, user_input: str) -> ProcessResult:
        """
        异步处理请求
        
        使用信号量限制并发数，防止资源耗尽
        """
        async with self.semaphore:
            # 翻译阶段（可能耗时）
            suggestion = await self._async_translate(user_input)
            
            # 验证阶段（快速）
            validation = await self._async_validate(suggestion.generated_command)
            
            # 执行阶段（可能耗时）
            if validation.is_valid:
                execution = await self._async_execute(suggestion.generated_command)
            else:
                execution = None
            
            return ProcessResult(
                success=True,
                suggestion=suggestion,
                validation=validation,
                execution=execution
            )
    
    async def _async_translate(self, user_input: str) -> Suggestion:
        """异步翻译"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.ai_engine.translate,
            user_input
        )
```

**连接池管理**：

```python
class ConnectionPool:
    """连接池管理"""
    
    def __init__(self, max_connections: int = 10):
        self.pool = Queue(maxsize=max_connections)
        self.max_connections = max_connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.max_connections):
            conn = self._create_connection()
            self.pool.put(conn)
    
    @contextmanager
    def get_connection(self):
        """获取连接"""
        conn = self.pool.get()
        try:
            yield conn
        finally:
            self.pool.put(conn)
```

#### 7.2.4 数据库优化

**索引优化**：

```sql
-- 缓存表索引
CREATE INDEX idx_cache_key ON translation_cache(key);
CREATE INDEX idx_cache_expires ON translation_cache(expires_at);
CREATE INDEX idx_cache_created ON translation_cache(created_at);

-- 历史表索引
CREATE INDEX idx_history_session ON command_history(session_id);
CREATE INDEX idx_history_timestamp ON command_history(timestamp);
CREATE INDEX idx_history_user ON command_history(user_id);

-- 复合索引
CREATE INDEX idx_history_session_time ON command_history(session_id, timestamp);
```

**查询优化**：

```python
class OptimizedQueries:
    """优化的数据库查询"""
    
    def get_recent_history(
        self,
        limit: int = 10,
        session_id: Optional[str] = None
    ) -> List[CommandEntry]:
        """
        获取最近历史
        
        优化:
        - 使用索引
        - 限制返回字段
        - 批量加载
        """
        query = """
            SELECT 
                command_id, user_input, translated_command,
                timestamp, confidence_score
            FROM command_history
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        return self.db.execute(query, (session_id, limit)).fetchall()
    
    def batch_insert_history(self, entries: List[CommandEntry]):
        """
        批量插入历史记录
        
        优化: 使用批量插入减少数据库往返
        """
        query = """
            INSERT INTO command_history 
            (command_id, user_input, translated_command, ...)
            VALUES (?, ?, ?, ...)
        """
        
        data = [(e.command_id, e.user_input, e.translated_command, ...)
                for e in entries]
        
        self.db.executemany(query, data)
        self.db.commit()
```

### 7.3 资源管理

#### 7.3.1 内存管理

**内存监控**：

```python
class MemoryMonitor:
    """内存监控"""
    
    def __init__(self, threshold_mb: int = 400):
        self.threshold = threshold_mb * 1024 * 1024  # 转换为字节
        self.process = psutil.Process()
        
    def check_memory(self) -> Dict[str, Any]:
        """检查内存使用"""
        mem_info = self.process.memory_info()
        
        return {
            'rss': mem_info.rss,  # 实际物理内存
            'vms': mem_info.vms,  # 虚拟内存
            'percent': self.process.memory_percent(),
            'threshold_exceeded': mem_info.rss > self.threshold
        }
    
    def trigger_cleanup(self):
        """触发内存清理"""
        # 清理缓存
        self.cache.clear_expired()
        
        # 强制垃圾回收
        import gc
        gc.collect()
        
        # 清理临时数据
        self.temp_storage.clear()
```

**内存限制**：

```python
class MemoryLimiter:
    """内存限制器"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory = max_memory_mb * 1024 * 1024
        
    @contextmanager
    def limit_memory(self):
        """限制内存使用"""
        if sys.platform != 'win32':
            import resource
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, hard))
        
        try:
            yield
        finally:
            if sys.platform != 'win32':
                resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
```

#### 7.3.2 CPU管理

**CPU限制**：

```python
class CPULimiter:
    """CPU限制器"""
    
    def __init__(self, max_cpu_percent: int = 50):
        self.max_cpu_percent = max_cpu_percent
        
    def limit_cpu(self):
        """限制CPU使用"""
        if sys.platform != 'win32':
            import resource
            # 设置CPU时间限制
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (60, 120)  # 软限制60秒，硬限制120秒
            )
```

**负载均衡**：

```python
class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self.workers = []
        self.current_index = 0
        
    def get_worker(self) -> Worker:
        """
        获取工作进程
        
        使用轮询算法分配任务
        """
        worker = self.workers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.workers)
        return worker
```

#### 7.3.3 磁盘管理

**磁盘空间监控**：

```python
class DiskMonitor:
    """磁盘监控"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        
    def check_disk_usage(self) -> Dict[str, Any]:
        """检查磁盘使用"""
        usage = shutil.disk_usage(self.base_path)
        
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': (usage.used / usage.total) * 100
        }
    
    def cleanup_old_files(self, days: int = 30):
        """清理旧文件"""
        cutoff = datetime.now() - timedelta(days=days)
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    file_path.unlink()
```

### 7.4 监控方案

#### 7.4.1 性能指标收集

**指标定义**：

```python
@dataclass
class PerformanceMetrics:
    """性能指标"""
    
    # 响应时间
    translation_time: float = 0.0
    validation_time: float = 0.0
    execution_time: float = 0.0
    total_time: float = 0.0
    
    # 缓存统计
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    
    # 翻译方法分布
    rule_translations: int = 0
    ai_translations: int = 0
    cached_translations: int = 0
    
    # 资源使用
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # 错误统计
    translation_errors: int = 0
    validation_errors: int = 0
    execution_errors: int = 0
    
    def calculate_cache_hit_rate(self):
        """计算缓存命中率"""
        total = self.cache_hits + self.cache_misses
        if total > 0:
            self.cache_hit_rate = self.cache_hits / total
```

**指标收集器**：

```python
class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.start_time = None
        
    @contextmanager
    def measure_time(self, metric_name: str):
        """测量执行时间"""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            setattr(self.metrics, metric_name, duration)
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.metrics.cache_hits += 1
        self.metrics.calculate_cache_hit_rate()
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.metrics.cache_misses += 1
        self.metrics.calculate_cache_hit_rate()
    
    def export_metrics(self) -> Dict[str, Any]:
        """导出指标"""
        return asdict(self.metrics)
```

#### 7.4.2 实时监控

**监控仪表板**：

```python
class MonitoringDashboard:
    """监控仪表板"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        
    def display_metrics(self):
        """显示实时指标"""
        metrics = self.metrics_collector.export_metrics()
        
        print("=== 性能监控 ===")
        print(f"平均响应时间: {metrics['total_time']:.2f}s")
        print(f"缓存命中率: {metrics['cache_hit_rate']:.1%}")
        print(f"内存使用: {metrics['memory_usage_mb']:.1f}MB")
        print(f"CPU使用: {metrics['cpu_usage_percent']:.1f}%")
        
        # 检查告警
        self.check_alerts(metrics)
    
    def check_alerts(self, metrics: Dict[str, Any]):
        """检查告警条件"""
        if metrics['total_time'] > 5.0:
            self.alert_manager.trigger_alert(
                'HIGH_LATENCY',
                f"响应时间过长: {metrics['total_time']:.2f}s"
            )
        
        if metrics['cache_hit_rate'] < 0.5:
            self.alert_manager.trigger_alert(
                'LOW_CACHE_HIT_RATE',
                f"缓存命中率过低: {metrics['cache_hit_rate']:.1%}"
            )
```

#### 7.4.3 性能分析

**性能剖析**：

```python
import cProfile
import pstats

class PerformanceProfiler:
    """性能剖析器"""
    
    def profile_function(self, func, *args, **kwargs):
        """剖析函数性能"""
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        
        # 生成报告
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # 显示前20个最耗时的函数
        
        return result
```

**瓶颈分析**：

```python
class BottleneckAnalyzer:
    """瓶颈分析器"""
    
    def analyze(self, metrics: PerformanceMetrics) -> List[str]:
        """分析性能瓶颈"""
        bottlenecks = []
        
        # 检查翻译时间
        if metrics.translation_time > 2.0:
            bottlenecks.append(
                f"翻译时间过长 ({metrics.translation_time:.2f}s)，"
                "建议: 增加缓存、优化规则匹配"
            )
        
        # 检查缓存命中率
        if metrics.cache_hit_rate < 0.6:
            bottlenecks.append(
                f"缓存命中率低 ({metrics.cache_hit_rate:.1%})，"
                "建议: 增加缓存大小、延长TTL"
            )
        
        # 检查内存使用
        if metrics.memory_usage_mb > 400:
            bottlenecks.append(
                f"内存使用过高 ({metrics.memory_usage_mb:.1f}MB)，"
                "建议: 清理缓存、减少模型大小"
            )
        
        return bottlenecks
```

---

## 8. 部署设计

### 8.1 部署架构

系统支持多种部署方式，满足不同场景的需求。

#### 8.1.1 部署模式

**1. 单机部署 (Standalone)**

```
┌─────────────────────────────────────┐
│         用户工作站                   │
│  ┌───────────────────────────────┐  │
│  │  AI PowerShell Assistant      │  │
│  │  ├── Python Runtime           │  │
│  │  ├── AI Model (Ollama)        │  │
│  │  ├── PowerShell Core          │  │
│  │  └── SQLite Database          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**特点**：
- 完全本地运行，无需网络
- 数据隐私性最高
- 适合个人用户
- 资源占用较高

**2. Docker容器部署**

```
┌─────────────────────────────────────┐
│         Docker Host                  │
│  ┌───────────────────────────────┐  │
│  │  Container: ai-powershell     │  │
│  │  ├── Application              │  │
│  │  ├── AI Model                 │  │
│  │  ├── PowerShell               │  │
│  │  └── Volume: /data            │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │  Volume: ai-powershell-data   │  │
│  │  ├── config/                  │  │
│  │  ├── data/                    │  │
│  │  └── logs/                    │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**特点**：
- 环境隔离，易于管理
- 快速部署和迁移
- 资源限制和监控
- 适合开发和测试

**3. 客户端-服务器模式 (可选扩展)**

```
┌──────────────┐      ┌──────────────────────┐
│  Client 1    │      │   Server             │
│  (CLI)       │─────▶│  ┌────────────────┐  │
└──────────────┘      │  │  API Gateway   │  │
                      │  └────────────────┘  │
┌──────────────┐      │  ┌────────────────┐  │
│  Client 2    │─────▶│  │  AI Engine     │  │
│  (Web UI)    │      │  └────────────────┘  │
└──────────────┘      │  ┌────────────────┐  │
                      │  │  Database      │  │
┌──────────────┐      │  └────────────────┘  │
│  Client 3    │─────▶│                      │
│  (API)       │      └──────────────────────┘
└──────────────┘
```

**特点**：
- 集中管理和维护
- 支持多用户并发
- 资源共享，成本降低
- 需要网络连接

#### 8.1.2 推荐部署方案

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 个人开发者 | 单机部署 | 简单、隐私、无需额外配置 |
| 团队协作 | Docker部署 | 环境一致、易于分发 |
| 企业内部 | 客户端-服务器 | 集中管理、资源优化 |
| 测试环境 | Docker部署 | 快速搭建、易于清理 |

### 8.2 环境要求

#### 8.2.1 硬件要求

**最低配置**：
```
CPU: 2核心 2.0GHz
内存: 4GB RAM
磁盘: 10GB 可用空间
网络: 可选（仅用于下载模型）
```

**推荐配置**：
```
CPU: 4核心 3.0GHz
内存: 8GB RAM
磁盘: 20GB 可用空间 (SSD)
网络: 可选
```

**AI模型要求**：
```
小型模型 (7B参数):
  - 内存: +4GB
  - 磁盘: +4GB

中型模型 (13B参数):
  - 内存: +8GB
  - 磁盘: +8GB

大型模型 (70B参数):
  - 内存: +32GB
  - 磁盘: +40GB
  - GPU: 推荐 (CUDA支持)
```

#### 8.2.2 软件要求

**操作系统**：
- Windows 10/11 (x64)
- Ubuntu 20.04+ / Debian 11+
- macOS 11+ (Big Sur及以上)

**运行时环境**：
```
Python: 3.8 - 3.11
PowerShell: 7.0+ (PowerShell Core)
Docker: 20.10+ (可选，用于沙箱)
```

**依赖软件**：
```
# Python包
pyyaml >= 6.0
pydantic >= 2.0
psutil >= 5.9
docker >= 6.0 (可选)
ollama-python >= 0.1.0 (可选)

# 系统工具
git (用于安装)
curl/wget (用于下载)
```

#### 8.2.3 网络要求

**必需网络访问**：
- 无（完全离线运行）

**可选网络访问**：
- Ollama API: http://localhost:11434 (本地AI模型)
- Docker Hub: https://hub.docker.com (下载镜像)
- PyPI: https://pypi.org (安装依赖)
- GitHub: https://github.com (获取更新)

### 8.3 配置管理

#### 8.3.1 配置文件层次

```
配置优先级 (从高到低):
1. 命令行参数
2. 环境变量
3. 用户配置 (~/.ai-powershell/config.yaml)
4. 项目配置 (./config/default.yaml)
5. 默认配置 (代码内置)
```

#### 8.3.2 配置文件模板

**默认配置 (config/default.yaml)**：

```yaml
# AI引擎配置
ai:
  provider: ollama
  model_name: llama2
  api_endpoint: http://localhost:11434
  temperature: 0.7
  max_tokens: 256
  cache_enabled: true
  cache_ttl: 3600
  rules_path: config/rules.yaml
  prompt_template_path: config/prompts.yaml

# 安全引擎配置
security:
  enabled: true
  patterns_path: config/dangerous_patterns.yaml
  risk_threshold: MEDIUM
  auto_reject_high_risk: true
  sandbox_enabled: false
  sandbox:
    docker_image: mcr.microsoft.com/powershell:latest
    memory_limit: 512
    cpu_quota: 50
    network_disabled: true
    timeout: 30
  audit_enabled: true

# 执行引擎配置
execution:
  default_timeout: 30
  use_pwsh: true
  output_encoding: utf-8
  capture_stderr: true
  working_directory: null
  environment: {}

# 日志配置
logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  log_file: ~/.ai-powershell/logs/app.log
  console_output: true
  structured: true
  filter_sensitive: true
  audit_log_file: ~/.ai-powershell/logs/audit.log

# 存储配置
storage:
  base_path: ~/.ai-powershell
  history_max_entries: 1000
  cache_max_size: 10000
  backup_enabled: true
  backup_interval_days: 7

# 上下文配置
context:
  max_history_length: 10
  session_timeout_minutes: 30
  auto_save_session: true
```

**环境变量配置**：

```bash
# AI配置
export AI_POWERSHELL_AI_PROVIDER=ollama
export AI_POWERSHELL_MODEL_NAME=llama2
export AI_POWERSHELL_API_ENDPOINT=http://localhost:11434

# 安全配置
export AI_POWERSHELL_SANDBOX_ENABLED=false
export AI_POWERSHELL_RISK_THRESHOLD=MEDIUM

# 日志配置
export AI_POWERSHELL_LOG_LEVEL=INFO
export AI_POWERSHELL_LOG_FILE=/var/log/ai-powershell/app.log

# 存储配置
export AI_POWERSHELL_BASE_PATH=/opt/ai-powershell/data
```

#### 8.3.3 配置验证

```python
class ConfigValidator:
    """配置验证器"""
    
    def validate(self, config: Config) -> List[str]:
        """
        验证配置
        
        Returns:
            错误列表，空列表表示验证通过
        """
        errors = []
        
        # 验证AI配置
        if config.ai.provider not in ['local', 'ollama', 'openai']:
            errors.append(f"无效的AI提供商: {config.ai.provider}")
        
        if config.ai.temperature < 0 or config.ai.temperature > 2:
            errors.append(f"温度参数超出范围: {config.ai.temperature}")
        
        # 验证路径
        if not Path(config.ai.rules_path).exists():
            errors.append(f"规则文件不存在: {config.ai.rules_path}")
        
        # 验证沙箱配置
        if config.security.sandbox_enabled:
            if not self._check_docker_available():
                errors.append("沙箱已启用但Docker不可用")
        
        return errors
    
    def _check_docker_available(self) -> bool:
        """检查Docker是否可用"""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except:
            return False
```

### 8.4 运维方案

#### 8.4.1 安装部署

**自动安装脚本 (install.sh)**：

```bash
#!/bin/bash
# AI PowerShell Assistant 安装脚本

set -e

echo "=== AI PowerShell Assistant 安装程序 ==="

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 检查PowerShell
echo "检查PowerShell..."
if ! command -v pwsh &> /dev/null; then
    echo "警告: 未检测到PowerShell Core，请手动安装"
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建配置目录
echo "创建配置目录..."
mkdir -p ~/.ai-powershell/{config,data,logs}

# 复制配置文件
echo "复制配置文件..."
cp config/default.yaml ~/.ai-powershell/config/
cp config/rules.yaml ~/.ai-powershell/config/
cp config/dangerous_patterns.yaml ~/.ai-powershell/config/

# 创建命令别名
echo "创建命令别名..."
cat >> ~/.bashrc << 'EOF'
# AI PowerShell Assistant
alias ai-powershell='python3 /path/to/ai-powershell/src/main.py'
EOF

echo "安装完成！"
echo "请运行 'source ~/.bashrc' 或重新打开终端"
echo "然后运行 'ai-powershell --help' 查看帮助"
```

**Docker部署 (docker-compose.yml)**：

```yaml
version: '3.8'

services:
  ai-powershell:
    image: ai-powershell:latest
    container_name: ai-powershell
    
    # 资源限制
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    
    # 环境变量
    environment:
      - AI_POWERSHELL_LOG_LEVEL=INFO
      - AI_POWERSHELL_AI_PROVIDER=ollama
      - AI_POWERSHELL_MODEL_NAME=llama2
    
    # 数据卷
    volumes:
      - ai-powershell-config:/app/config
      - ai-powershell-data:/root/.ai-powershell
      - ai-powershell-logs:/app/logs
    
    # 网络
    networks:
      - ai-powershell-net
    
    # 健康检查
    healthcheck:
      test: ["CMD", "python3", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
    
    # 重启策略
    restart: unless-stopped

  # Ollama服务 (可选)
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - ai-powershell-net
    restart: unless-stopped

volumes:
  ai-powershell-config:
  ai-powershell-data:
  ai-powershell-logs:
  ollama-data:

networks:
  ai-powershell-net:
    driver: bridge
```

#### 8.4.2 启动和停止

**启动脚本 (start.sh)**：

```bash
#!/bin/bash
# 启动AI PowerShell Assistant

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
python3 -c "import yaml, pydantic, psutil" || {
    echo "错误: 依赖未安装"
    exit 1
}

# 启动应用
echo "启动AI PowerShell Assistant..."
python3 src/main.py --interactive

# 或作为后台服务
# nohup python3 src/main.py --daemon > /dev/null 2>&1 &
# echo $! > ~/.ai-powershell/ai-powershell.pid
```

**停止脚本 (stop.sh)**：

```bash
#!/bin/bash
# 停止AI PowerShell Assistant

PID_FILE=~/.ai-powershell/ai-powershell.pid

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "停止进程 $PID..."
        kill $PID
        rm "$PID_FILE"
        echo "已停止"
    else
        echo "进程不存在"
        rm "$PID_FILE"
    fi
else
    echo "PID文件不存在"
fi
```

#### 8.4.3 监控和维护

**健康检查脚本 (health-check.sh)**：

```bash
#!/bin/bash
# 健康检查脚本

# 检查进程
if ! pgrep -f "ai-powershell" > /dev/null; then
    echo "ERROR: 进程未运行"
    exit 1
fi

# 检查内存使用
memory_usage=$(ps aux | grep ai-powershell | awk '{sum+=$6} END {print sum/1024}')
if (( $(echo "$memory_usage > 500" | bc -l) )); then
    echo "WARNING: 内存使用过高: ${memory_usage}MB"
fi

# 检查磁盘空间
disk_usage=$(df -h ~/.ai-powershell | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 80 ]; then
    echo "WARNING: 磁盘使用率过高: ${disk_usage}%"
fi

# 检查日志文件大小
log_size=$(du -sm ~/.ai-powershell/logs | awk '{print $1}')
if [ "$log_size" -gt 100 ]; then
    echo "WARNING: 日志文件过大: ${log_size}MB"
fi

echo "OK: 系统运行正常"
exit 0
```

**日志轮转配置 (logrotate.conf)**：

```
/home/*/.ai-powershell/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user user
    sharedscripts
    postrotate
        # 重新加载应用（如果需要）
        # kill -HUP $(cat ~/.ai-powershell/ai-powershell.pid)
    endscript
}
```

**备份脚本 (backup.sh)**：

```bash
#!/bin/bash
# 数据备份脚本

BACKUP_DIR=~/.ai-powershell/backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ai-powershell-backup-${DATE}.tar.gz"

echo "开始备份..."

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    ~/.ai-powershell/config \
    ~/.ai-powershell/data \
    --exclude='*.log'

echo "备份完成: ${BACKUP_FILE}"

# 清理旧备份（保留最近7天）
find "$BACKUP_DIR" -name "ai-powershell-backup-*.tar.gz" -mtime +7 -delete

echo "清理完成"
```

**更新脚本 (update.sh)**：

```bash
#!/bin/bash
# 更新脚本

echo "=== AI PowerShell Assistant 更新程序 ==="

# 备份当前版本
echo "备份当前版本..."
./backup.sh

# 拉取最新代码
echo "拉取最新代码..."
git pull origin main

# 更新依赖
echo "更新依赖..."
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 迁移配置（如果需要）
echo "检查配置更新..."
python3 scripts/migrate_config.py

# 重启服务
echo "重启服务..."
./stop.sh
./start.sh

echo "更新完成！"
```

#### 8.4.4 故障排查

**诊断脚本 (diagnose.sh)**：

```bash
#!/bin/bash
# 诊断脚本

echo "=== AI PowerShell Assistant 诊断 ==="

# 检查Python环境
echo "1. Python环境:"
python3 --version
which python3

# 检查PowerShell
echo -e "\n2. PowerShell:"
pwsh --version 2>/dev/null || echo "PowerShell未安装"

# 检查依赖
echo -e "\n3. Python依赖:"
pip list | grep -E "pyyaml|pydantic|psutil|docker"

# 检查配置文件
echo -e "\n4. 配置文件:"
ls -lh ~/.ai-powershell/config/

# 检查日志
echo -e "\n5. 最近错误日志:"
tail -20 ~/.ai-powershell/logs/app.log | grep ERROR

# 检查进程
echo -e "\n6. 进程状态:"
ps aux | grep ai-powershell | grep -v grep

# 检查资源使用
echo -e "\n7. 资源使用:"
echo "内存: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "磁盘: $(df -h ~/.ai-powershell | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"

# 检查网络连接
echo -e "\n8. 网络连接:"
curl -s http://localhost:11434/api/version > /dev/null && \
    echo "Ollama: 可用" || echo "Ollama: 不可用"

echo -e "\n诊断完成"
```

**常见问题解决**：

```markdown
# 常见问题

## 1. 翻译速度慢
- 检查AI模型是否正确加载
- 增加缓存大小
- 使用更小的模型
- 检查CPU/内存资源

## 2. 命令执行失败
- 检查PowerShell是否安装
- 验证命令语法
- 查看错误日志
- 检查权限设置

## 3. 沙箱无法启动
- 检查Docker是否运行
- 验证Docker镜像
- 检查资源限制
- 查看Docker日志

## 4. 配置不生效
- 检查配置文件路径
- 验证YAML语法
- 检查环境变量
- 重启应用

## 5. 内存占用过高
- 清理缓存
- 减小缓存大小
- 使用更小的AI模型
- 检查内存泄漏
```

---

## 附录

### A. 术语表

| 术语 | 说明 |
|------|------|
| AI引擎 | 负责自然语言到PowerShell命令转换的模块 |
| 安全引擎 | 负责命令安全验证的模块 |
| 执行引擎 | 负责PowerShell命令执行的模块 |
| 沙箱 | 隔离的执行环境，用于安全地运行危险命令 |
| LRU缓存 | 最近最少使用缓存算法 |
| TTL | 生存时间，缓存条目的有效期 |
| 风险等级 | 命令的危险程度分类 |
| 置信度 | AI翻译结果的可信程度 |

### B. 参考资料

1. PowerShell官方文档: https://docs.microsoft.com/powershell/
2. Docker官方文档: https://docs.docker.com/
3. Ollama文档: https://ollama.ai/docs
4. Python异步编程: https://docs.python.org/3/library/asyncio.html
5. Pydantic文档: https://docs.pydantic.dev/

### C. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2025-11 | 初始版本 |

---

**文档结束**

