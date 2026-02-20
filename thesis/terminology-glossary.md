# 毕业论文术语表

## 文档说明

本术语表列出了AI PowerShell智能助手毕业设计论文中使用的所有专业术语、技术名词和缩写，提供统一的中英文对照和定义，确保全文术语使用的一致性和规范性。

**使用规则：**
1. 术语首次出现时必须提供中英文对照
2. 全文使用统一的中文翻译
3. 缩写首次出现时给出全称
4. 专有名词保持原文（如PowerShell、Docker）

**版本信息：**
- 版本：v1.0
- 创建日期：2024年
- 最后更新：2024年

---

## 1. 人工智能与机器学习

### 1.1 基础概念

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 人工智能 | Artificial Intelligence | AI | 研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门技术科学 |
| 机器学习 | Machine Learning | ML | 使计算机系统能够从数据中学习并改进性能的人工智能分支 |
| 深度学习 | Deep Learning | DL | 基于人工神经网络的机器学习方法，使用多层网络结构学习数据的层次化表示 |
| 自然语言处理 | Natural Language Processing | NLP | 研究如何让计算机理解、处理和生成人类语言的技术领域 |
| 自然语言理解 | Natural Language Understanding | NLU | 自然语言处理的子领域，专注于让计算机理解人类语言的含义 |
| 自然语言生成 | Natural Language Generation | NLG | 自然语言处理的子领域，专注于让计算机生成人类可读的文本 |

### 1.2 神经网络

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 神经网络 | Neural Network | NN | 模拟生物神经系统的计算模型，由大量相互连接的节点组成 |
| 卷积神经网络 | Convolutional Neural Network | CNN | 专门用于处理网格结构数据（如图像）的神经网络 |
| 循环神经网络 | Recurrent Neural Network | RNN | 具有循环连接的神经网络，适合处理序列数据 |
| 长短期记忆网络 | Long Short-Term Memory | LSTM | 一种特殊的循环神经网络，能够学习长期依赖关系 |
| 门控循环单元 | Gated Recurrent Unit | GRU | LSTM的简化变体，具有更少的参数 |
| 注意力机制 | Attention Mechanism | - | 允许模型在处理输入时动态关注不同部分的机制 |
| 自注意力机制 | Self-Attention | - | 计算序列内部元素之间关系的注意力机制 |

### 1.3 大语言模型

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 大语言模型 | Large Language Model | LLM | 在大规模文本数据上训练的、具有数十亿参数的语言模型 |
| 预训练模型 | Pre-trained Model | - | 在大规模数据上预先训练好的模型，可用于下游任务 |
| 微调 | Fine-tuning | - | 在预训练模型基础上，使用特定任务数据进行进一步训练 |
| 提示工程 | Prompt Engineering | - | 设计和优化输入提示以获得更好模型输出的技术 |
| 上下文学习 | In-Context Learning | ICL | 模型通过输入中的示例学习任务，无需参数更新 |
| 零样本学习 | Zero-Shot Learning | - | 模型在没有见过任何示例的情况下执行任务 |
| 少样本学习 | Few-Shot Learning | - | 模型仅使用少量示例就能学习新任务 |

### 1.4 具体模型

| 中文术语 | 英文术语 | 缩写 | 说明 |
|---------|---------|------|------|
| Transformer模型 | Transformer Model | - | 基于自注意力机制的神经网络架构，是现代大语言模型的基础 |
| BERT | Bidirectional Encoder Representations from Transformers | BERT | Google开发的双向Transformer编码器模型 |
| GPT | Generative Pre-trained Transformer | GPT | OpenAI开发的生成式预训练Transformer模型 |
| LLaMA | Large Language Model Meta AI | LLaMA | Meta开发的开源大语言模型系列 |
| Codex | - | - | OpenAI开发的代码生成模型，GitHub Copilot的基础 |

---

## 2. PowerShell相关术语

### 2.1 基础概念

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| PowerShell | PowerShell | PS | 微软开发的任务自动化和配置管理框架，包含命令行Shell和脚本语言 |
| PowerShell Core | PowerShell Core | - | PowerShell的跨平台版本，基于.NET Core |
| Windows PowerShell | Windows PowerShell | - | PowerShell的Windows专用版本，基于.NET Framework |
| Cmdlet | Command-let | - | PowerShell中的轻量级命令，遵循"动词-名词"命名规范 |
| 管道 | Pipeline | - | 将一个命令的输出作为另一个命令的输入的机制 |
| 对象 | Object | - | PowerShell中的基本数据单元，包含属性和方法 |
| 参数 | Parameter | - | 传递给Cmdlet的输入值，用于控制命令行为 |
| 别名 | Alias | - | Cmdlet或函数的简短替代名称 |

### 2.2 高级概念

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| PowerShell模块 | PowerShell Module | - | 包含Cmdlet、函数、变量等的可重用代码包 |
| PowerShell脚本 | PowerShell Script | - | 包含PowerShell命令的文本文件，扩展名为.ps1 |
| PowerShell提供程序 | PowerShell Provider | - | 使数据存储可以像文件系统一样访问的适配器 |
| PowerShell驱动器 | PowerShell Drive | PSDrive | 通过提供程序访问的数据存储位置 |
| 远程处理 | Remoting | - | 在远程计算机上执行PowerShell命令的功能 |
| 执行策略 | Execution Policy | - | 控制PowerShell脚本执行权限的安全设置 |

---

## 3. 软件架构与设计

### 3.1 架构模式

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 模块化架构 | Modular Architecture | - | 将系统划分为独立、可替换模块的架构设计方法 |
| 分层架构 | Layered Architecture | - | 将系统组织为层次结构，每层提供特定功能的架构模式 |
| 微服务架构 | Microservices Architecture | - | 将应用程序构建为一组小型、独立服务的架构风格 |
| 面向服务架构 | Service-Oriented Architecture | SOA | 通过服务接口提供功能的软件设计方法 |
| 事件驱动架构 | Event-Driven Architecture | EDA | 基于事件的产生、检测和响应来组织系统的架构模式 |
| 插件架构 | Plugin Architecture | - | 允许通过插件扩展核心功能的架构设计 |

### 3.2 设计原则

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 高内聚 | High Cohesion | - | 模块内部元素紧密相关、共同完成单一功能的设计原则 |
| 低耦合 | Low Coupling | - | 模块之间依赖关系最小化的设计原则 |
| 单一职责原则 | Single Responsibility Principle | SRP | 一个类或模块应该只有一个引起变化的原因 |
| 开闭原则 | Open-Closed Principle | OCP | 软件实体应该对扩展开放，对修改关闭 |
| 里氏替换原则 | Liskov Substitution Principle | LSP | 子类应该能够替换其基类 |
| 接口隔离原则 | Interface Segregation Principle | ISP | 客户端不应该依赖它不需要的接口 |
| 依赖倒置原则 | Dependency Inversion Principle | DIP | 高层模块不应该依赖低层模块，两者都应该依赖抽象 |

### 3.3 设计模式

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 设计模式 | Design Pattern | - | 软件设计中常见问题的可重用解决方案 |
| 单例模式 | Singleton Pattern | - | 确保一个类只有一个实例的创建型模式 |
| 工厂模式 | Factory Pattern | - | 定义创建对象接口，让子类决定实例化哪个类的创建型模式 |
| 策略模式 | Strategy Pattern | - | 定义一系列算法，将每个算法封装起来并使它们可互换的行为型模式 |
| 观察者模式 | Observer Pattern | - | 定义对象间一对多依赖关系的行为型模式 |
| 装饰器模式 | Decorator Pattern | - | 动态地给对象添加额外职责的结构型模式 |
| 适配器模式 | Adapter Pattern | - | 将一个类的接口转换为客户期望的另一个接口的结构型模式 |
| 依赖注入 | Dependency Injection | DI | 将依赖关系从代码中移除，通过外部注入的设计模式 |


---

## 4. 系统安全

### 4.1 安全概念

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 信息安全 | Information Security | InfoSec | 保护信息免受未授权访问、使用、披露、破坏、修改或销毁的实践 |
| 网络安全 | Cybersecurity | - | 保护计算机系统和网络免受信息泄露、盗窃或损坏的实践 |
| 应用安全 | Application Security | AppSec | 在应用程序开发和部署过程中采取的安全措施 |
| 命令注入 | Command Injection | - | 通过在应用程序中注入恶意命令来执行未授权操作的攻击方式 |
| 代码注入 | Code Injection | - | 将恶意代码注入应用程序以改变其执行流程的攻击方式 |
| SQL注入 | SQL Injection | SQLi | 通过在SQL查询中注入恶意代码来攻击数据库的方式 |
| 跨站脚本攻击 | Cross-Site Scripting | XSS | 在网页中注入恶意脚本的攻击方式 |

### 4.2 访问控制

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 访问控制 | Access Control | AC | 限制对资源访问的安全机制 |
| 身份认证 | Authentication | AuthN | 验证用户或系统身份的过程 |
| 授权 | Authorization | AuthZ | 确定用户或系统可以访问哪些资源的过程 |
| 权限管理 | Permission Management | - | 管理用户或系统访问权限的过程 |
| 基于角色的访问控制 | Role-Based Access Control | RBAC | 根据用户角色分配权限的访问控制方法 |
| 最小权限原则 | Principle of Least Privilege | PoLP | 用户或进程只应拥有完成任务所需的最小权限 |
| 特权提升 | Privilege Escalation | - | 获得比授权更高权限的行为 |

### 4.3 隔离技术

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 沙箱 | Sandbox | - | 提供隔离执行环境以限制程序访问系统资源的安全机制 |
| 容器 | Container | - | 操作系统级虚拟化技术，提供轻量级的应用隔离 |
| 虚拟机 | Virtual Machine | VM | 模拟完整计算机系统的软件实现 |
| 虚拟化 | Virtualization | - | 创建资源的虚拟版本的技术 |
| 命名空间 | Namespace | - | Linux内核提供的资源隔离机制 |
| 控制组 | Control Groups | cgroups | Linux内核提供的资源限制和监控机制 |

### 4.4 审计与监控

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 审计日志 | Audit Log | - | 记录系统活动和事件的日志，用于安全审计 |
| 日志记录 | Logging | - | 记录系统事件和活动的过程 |
| 监控 | Monitoring | - | 持续观察系统状态和性能的过程 |
| 追踪 | Tracing | - | 跟踪请求或事务在系统中的执行路径 |
| 告警 | Alerting | - | 在检测到异常情况时发出通知的机制 |

---

## 5. 软件开发

### 5.1 开发方法

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 敏捷开发 | Agile Development | - | 强调迭代、协作和快速响应变化的软件开发方法 |
| 测试驱动开发 | Test-Driven Development | TDD | 先编写测试再编写代码的开发方法 |
| 行为驱动开发 | Behavior-Driven Development | BDD | 基于系统行为描述的开发方法 |
| 持续集成 | Continuous Integration | CI | 频繁地将代码集成到主分支的实践 |
| 持续交付 | Continuous Delivery | CD | 确保代码随时可以发布到生产环境的实践 |
| 持续部署 | Continuous Deployment | CD | 自动将代码部署到生产环境的实践 |
| DevOps | Development and Operations | DevOps | 开发和运维团队协作的文化和实践 |

### 5.2 代码质量

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 代码审查 | Code Review | CR | 由其他开发者检查代码质量的过程 |
| 重构 | Refactoring | - | 在不改变外部行为的前提下改进代码结构的过程 |
| 技术债务 | Technical Debt | - | 为了快速交付而采取的次优解决方案带来的长期成本 |
| 代码覆盖率 | Code Coverage | - | 测试执行时覆盖的代码比例 |
| 静态代码分析 | Static Code Analysis | - | 不执行代码而分析代码质量的技术 |
| 代码规范 | Coding Standards | - | 团队约定的代码编写规则和风格 |

### 5.3 版本控制

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 版本控制系统 | Version Control System | VCS | 管理文件变更历史的系统 |
| Git | Git | - | 分布式版本控制系统 |
| 仓库 | Repository | Repo | 存储项目文件和版本历史的位置 |
| 提交 | Commit | - | 将更改保存到版本控制系统的操作 |
| 分支 | Branch | - | 代码库的独立开发线 |
| 合并 | Merge | - | 将不同分支的更改合并到一起的操作 |
| 拉取请求 | Pull Request | PR | 请求将代码合并到主分支的机制 |

---

## 6. 测试相关

### 6.1 测试类型

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 单元测试 | Unit Test | UT | 测试单个代码单元（如函数或方法）的测试 |
| 集成测试 | Integration Test | IT | 测试多个组件协同工作的测试 |
| 系统测试 | System Test | ST | 测试完整系统功能的测试 |
| 端到端测试 | End-to-End Test | E2E | 从用户角度测试完整业务流程的测试 |
| 性能测试 | Performance Test | - | 测试系统性能指标的测试 |
| 负载测试 | Load Test | - | 测试系统在高负载下表现的测试 |
| 压力测试 | Stress Test | - | 测试系统在极限条件下表现的测试 |
| 安全测试 | Security Test | - | 测试系统安全性的测试 |
| 回归测试 | Regression Test | - | 确保新更改不影响现有功能的测试 |

### 6.2 测试概念

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 测试用例 | Test Case | TC | 描述测试条件、输入和预期结果的文档 |
| 测试套件 | Test Suite | - | 一组相关测试用例的集合 |
| 测试框架 | Test Framework | - | 提供测试编写和执行支持的软件框架 |
| 断言 | Assertion | - | 验证预期结果是否正确的语句 |
| 模拟对象 | Mock Object | Mock | 模拟真实对象行为的测试替身 |
| 桩 | Stub | - | 提供预定义响应的简化实现 |
| 测试覆盖率 | Test Coverage | - | 测试执行时覆盖的代码或功能比例 |

---

## 7. 系统与网络

### 7.1 操作系统

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 操作系统 | Operating System | OS | 管理计算机硬件和软件资源的系统软件 |
| Windows | Windows | - | 微软开发的操作系统系列 |
| Linux | Linux | - | 开源的类Unix操作系统 |
| macOS | macOS | - | 苹果公司开发的操作系统 |
| 进程 | Process | - | 正在执行的程序实例 |
| 线程 | Thread | - | 进程内的执行单元 |
| 文件系统 | File System | FS | 组织和存储文件的方法 |
| 环境变量 | Environment Variable | - | 影响进程行为的动态值 |

### 7.2 网络概念

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 超文本传输协议 | Hypertext Transfer Protocol | HTTP | 用于传输网页的应用层协议 |
| 安全超文本传输协议 | HTTP Secure | HTTPS | HTTP的安全版本，使用TLS/SSL加密 |
| 传输控制协议 | Transmission Control Protocol | TCP | 提供可靠、有序数据传输的传输层协议 |
| 用户数据报协议 | User Datagram Protocol | UDP | 提供无连接数据传输的传输层协议 |
| 互联网协议 | Internet Protocol | IP | 网络层协议，负责数据包路由 |
| 域名系统 | Domain Name System | DNS | 将域名转换为IP地址的系统 |
| 应用程序接口 | Application Programming Interface | API | 软件组件之间交互的接口定义 |
| RESTful API | Representational State Transfer API | REST | 基于HTTP的Web服务架构风格 |

---

## 8. 数据与存储

### 8.1 数据格式

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| JavaScript对象表示法 | JavaScript Object Notation | JSON | 轻量级的数据交换格式 |
| 可扩展标记语言 | Extensible Markup Language | XML | 用于存储和传输数据的标记语言 |
| YAML | YAML Ain't Markup Language | YAML | 人类可读的数据序列化格式 |
| 逗号分隔值 | Comma-Separated Values | CSV | 使用逗号分隔字段的文本文件格式 |
| 二进制JSON | Binary JSON | BSON | JSON的二进制编码格式 |

### 8.2 数据库

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 数据库 | Database | DB | 组织、存储和管理数据的系统 |
| 关系型数据库 | Relational Database | RDB | 使用表格存储数据的数据库 |
| 非关系型数据库 | Non-Relational Database | NoSQL | 不使用传统表格关系的数据库 |
| 结构化查询语言 | Structured Query Language | SQL | 用于管理关系型数据库的语言 |
| 对象关系映射 | Object-Relational Mapping | ORM | 在对象模型和关系数据库之间转换数据的技术 |
| 缓存 | Cache | - | 临时存储频繁访问数据以提高性能的机制 |
| 键值存储 | Key-Value Store | KV | 使用键值对存储数据的数据库类型 |

---

## 9. 开发工具与技术

### 9.1 编程语言

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| Python | Python | - | 高级、解释型、通用编程语言 |
| JavaScript | JavaScript | JS | 主要用于Web开发的脚本语言 |
| TypeScript | TypeScript | TS | JavaScript的超集，添加了静态类型 |
| Shell脚本 | Shell Script | - | 在命令行解释器中执行的脚本 |
| Bash | Bourne Again Shell | Bash | Unix/Linux系统的默认Shell |

### 9.2 开发工具

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 集成开发环境 | Integrated Development Environment | IDE | 提供代码编辑、调试等功能的软件应用 |
| 代码编辑器 | Code Editor | - | 用于编写和编辑代码的文本编辑器 |
| 调试器 | Debugger | - | 用于查找和修复代码错误的工具 |
| 包管理器 | Package Manager | - | 管理软件包安装、更新和依赖的工具 |
| 构建工具 | Build Tool | - | 自动化编译、测试和部署过程的工具 |

### 9.3 容器与编排

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| Docker | Docker | - | 开源的容器化平台 |
| Docker镜像 | Docker Image | - | 包含应用程序及其依赖的只读模板 |
| Docker容器 | Docker Container | - | Docker镜像的运行实例 |
| Dockerfile | Dockerfile | - | 定义Docker镜像构建步骤的文本文件 |
| Kubernetes | Kubernetes | K8s | 开源的容器编排平台 |
| 容器编排 | Container Orchestration | - | 自动化容器部署、扩展和管理的技术 |

---

## 10. 性能与优化

### 10.1 性能指标

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 响应时间 | Response Time | RT | 系统处理请求所需的时间 |
| 吞吐量 | Throughput | - | 单位时间内系统处理的请求数量 |
| 延迟 | Latency | - | 请求发送到接收响应之间的时间延迟 |
| 并发 | Concurrency | - | 同时处理多个任务的能力 |
| 可扩展性 | Scalability | - | 系统处理增长负载的能力 |
| 可用性 | Availability | - | 系统正常运行的时间比例 |
| 可靠性 | Reliability | - | 系统在规定条件下正常运行的能力 |

### 10.2 优化技术

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 缓存 | Caching | - | 存储频繁访问数据以提高性能的技术 |
| 负载均衡 | Load Balancing | LB | 在多个服务器间分配工作负载的技术 |
| 异步处理 | Asynchronous Processing | - | 不阻塞主线程的处理方式 |
| 并行处理 | Parallel Processing | - | 同时执行多个任务的处理方式 |
| 懒加载 | Lazy Loading | - | 延迟加载资源直到需要时的技术 |
| 预加载 | Preloading | - | 提前加载可能需要的资源的技术 |

---

## 11. 项目特定术语

### 11.1 系统组件

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| AI引擎 | AI Engine | - | 负责自然语言到PowerShell命令转换的模块 |
| 安全引擎 | Security Engine | - | 负责命令安全验证的模块 |
| 执行引擎 | Execution Engine | - | 负责跨平台命令执行的模块 |
| 配置管理器 | Configuration Manager | - | 负责系统配置加载和验证的模块 |
| 日志引擎 | Log Engine | - | 负责结构化日志记录的模块 |
| 存储引擎 | Storage Engine | - | 负责数据持久化和缓存的模块 |
| 上下文管理器 | Context Manager | - | 负责会话和历史管理的模块 |
| 主控制器 | Main Controller | - | 协调所有模块工作的核心组件 |

### 11.2 功能特性

| 中文术语 | 英文术语 | 缩写 | 定义 |
|---------|---------|------|------|
| 混合翻译策略 | Hybrid Translation Strategy | - | 结合规则匹配和AI模型的翻译方法 |
| 三层安全机制 | Three-Tier Security Mechanism | - | 包含白名单、权限检查和沙箱的安全架构 |
| 规则匹配 | Rule Matching | - | 使用预定义规则进行命令翻译的方法 |
| 命令白名单 | Command Whitelist | - | 允许执行的安全命令列表 |
| 风险等级评估 | Risk Level Assessment | - | 评估命令危险程度的机制 |
| 沙箱执行 | Sandbox Execution | - | 在隔离环境中执行命令的安全措施 |
| 置信度评分 | Confidence Score | - | 表示翻译结果可靠性的数值 |

---

## 12. 缩写快速参考

### 12.1 常用缩写（可直接使用）

这些缩写在行业内广泛使用，可以在文中直接使用而无需每次都给出全称：

**人工智能：** AI, ML, DL, NLP, LLM, NN, CNN, RNN, LSTM, GRU

**系统架构：** API, CLI, GUI, SDK, IDE, SOA, DI, SRP, OCP, LSP, ISP, DIP

**安全相关：** RBAC, PoLP, XSS, SQLi, AuthN, AuthZ

**开发工具：** CI, CD, TDD, BDD, DevOps, VCS, PR, CR

**网络协议：** HTTP, HTTPS, TCP, UDP, IP, DNS, REST

**数据格式：** JSON, XML, YAML, CSV, SQL

**操作系统：** OS, VM, FS

**测试相关：** UT, IT, ST, E2E, TC

**其他：** CPU, GPU, RAM, ROM, URL, URI

### 12.2 需要说明的缩写

这些缩写首次出现时必须给出全称：

- ICL (In-Context Learning) - 上下文学习
- PoLP (Principle of Least Privilege) - 最小权限原则
- InfoSec (Information Security) - 信息安全
- AppSec (Application Security) - 应用安全
- cgroups (Control Groups) - 控制组
- K8s (Kubernetes) - Kubernetes
- KV (Key-Value) - 键值
- LB (Load Balancing) - 负载均衡
- RT (Response Time) - 响应时间

---

## 13. 术语使用检查清单

### 13.1 首次出现检查

- [ ] 所有专业术语首次出现时都有中英文对照
- [ ] 所有缩写首次出现时都给出了全称
- [ ] 专有名词保持了原文（如PowerShell、Docker）
- [ ] 术语定义清晰准确

### 13.2 一致性检查

- [ ] 同一术语在全文中使用统一的中文翻译
- [ ] 缩写使用一致（全大写或保持原格式）
- [ ] 没有同义词混用的情况
- [ ] 术语表中的术语与正文使用一致

### 13.3 规范性检查

- [ ] 使用了行业标准术语
- [ ] 避免了自造词汇
- [ ] 技术名词翻译准确
- [ ] 符合学术论文规范

---

## 附录：术语索引

### A-C
AI, API, AppSec, AuthN, AuthZ, Bash, BERT, BDD, BSON, Cache, CD, CI, CLI, CNN, Codex, CPU, CR, CSV, cgroups

### D-G
DB, DevOps, DI, DIP, DL, DNS, Docker, E2E, EDA, FS, Git, GPT, GPU, GRU, GUI, HTTP, HTTPS

### I-L
ICL, IDE, InfoSec, IP, ISP, IT, JSON, JS, K8s, KV, LB, Linux, LLaMA, LLM, LSTM, LSP

### M-P
macOS, ML, Mock, NN, NLG, NLP, NLU, NoSQL, OCP, ORM, OS, PoLP, PowerShell, PR, Python

### R-Z
RAM, RBAC, RDB, REST, RNN, ROM, RT, SOA, SQL, SQLi, SRP, ST, Stub, TC, TCP, TDD, TS, UDP, UT, VCS, VM, Windows, XML, XSS, YAML

---

**文档结束**

本术语表将随论文编写过程持续更新和完善。如发现遗漏或需要补充的术语，请及时添加。
