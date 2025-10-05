# 🎯 AI PowerShell Assistant 实践指南

这个指南将带你从零开始，逐步了解和掌握这个项目。

## 📖 学习路径

### 阶段1：理解项目概念（30分钟）

#### 1.1 阅读核心文档
```bash
# 按顺序阅读这些文件
1. README.md                    # 项目总览
2. docs/README.md              # 文档导航
3. .kiro/specs/ai-powershell-assistant/requirements.md  # 需求文档
4. .kiro/specs/ai-powershell-assistant/design.md        # 设计文档
```

#### 1.2 运行学习示例
```bash
# 运行我为你准备的学习示例
cd learning/
python 01_basic_example.py      # 基础概念
python 02_component_tour.py     # 组件导览
python 03_integration_demo.py   # 集成演示
```

### 阶段2：探索代码结构（45分钟）

#### 2.1 核心接口理解
```bash
# 查看基础接口定义
src/interfaces/base.py          # 所有组件的基础接口

# 关键概念：
# - Platform: 支持的操作系统平台
# - UserRole: 用户角色和权限
# - CommandContext: 命令执行上下文
# - ExecutionResult: 执行结果格式
```

#### 2.2 组件深入了解
```bash
# 按重要性顺序查看：
1. src/mcp_server/server.py     # MCP服务器主类
2. src/ai_engine/engine.py      # AI引擎主类
3. src/security/engine.py       # 安全引擎主类
4. src/execution/executor.py    # 执行引擎主类
5. src/log_engine/engine.py     # 日志引擎主类
```

#### 2.3 数据模型理解
```bash
# 查看数据结构定义
src/mcp_server/schemas.py       # MCP工具的请求/响应格式
src/config/models.py            # 配置数据模型
src/context/models.py           # 上下文数据模型
```

### 阶段3：运行和测试（60分钟）

#### 3.1 环境准备
```bash
# 1. 创建Python虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt
pip install -e .

# 3. 检查环境
python -c "import src; print('环境准备完成')"
```

#### 3.2 运行单元测试
```bash
# 运行所有测试，了解各组件功能
python -m pytest src/ -v

# 运行特定组件测试
python -m pytest src/ai_engine/test_engine.py -v
python -m pytest src/security/test_engine.py -v
python -m pytest src/execution/test_executor.py -v
```

#### 3.3 启动完整系统
```bash
# 方法1：直接运行主集成文件
python -m src.main_integration

# 方法2：使用启动系统
python -m src.startup_system

# 方法3：运行开发服务器
python -m src.main_integration --dev
```

### 阶段4：实际使用体验（45分钟）

#### 4.1 API测试
```bash
# 启动服务后，在另一个终端测试API

# 1. 健康检查
curl http://localhost:8000/health

# 2. 自然语言翻译
curl -X POST http://localhost:8000/natural_language_to_powershell \
  -H "Content-Type: application/json" \
  -d '{"input_text": "显示所有正在运行的进程", "session_id": "test"}'

# 3. 命令执行
curl -X POST http://localhost:8000/execute_powershell_command \
  -H "Content-Type: application/json" \
  -d '{"command": "Get-Process | Select-Object -First 3", "session_id": "test"}'
```

#### 4.2 Python客户端测试
```python
# 创建 test_client.py
import requests

class TestClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session_id = "learning_session"
    
    def test_translation(self):
        response = requests.post(f"{self.base_url}/natural_language_to_powershell", 
            json={"input_text": "列出当前目录的文件", "session_id": self.session_id})
        return response.json()
    
    def test_execution(self, command):
        response = requests.post(f"{self.base_url}/execute_powershell_command",
            json={"command": command, "session_id": self.session_id, "use_sandbox": True})
        return response.json()

# 使用客户端
client = TestClient()
result = client.test_translation()
print(f"翻译结果: {result}")

if result.get('success'):
    exec_result = client.test_execution(result['generated_command'])
    print(f"执行结果: {exec_result}")
```

### 阶段5：深入定制（可选，60分钟）

#### 5.1 配置定制
```bash
# 查看配置文件
config/development.yaml         # 开发环境配置
config/production.yaml          # 生产环境配置

# 修改配置示例
# 1. 修改AI模型参数
# 2. 调整安全规则
# 3. 配置日志级别
```

#### 5.2 安全规则定制
```yaml
# 编辑安全规则文件
# config/security-rules.yaml

categories:
  my_safe_commands:
    action: "allow"
    patterns:
      - "^Get-"
      - "^Show-"
      - "^Test-"
  
  my_restricted_commands:
    action: "block"
    patterns:
      - "Remove-Item.*-Recurse"
      - "Format-Volume"
```

#### 5.3 添加自定义功能
```python
# 示例：添加自定义MCP工具
# 在 src/mcp_server/server.py 中添加

@self.app.tool()
async def my_custom_tool(request: dict) -> dict:
    """自定义工具示例"""
    return {
        "success": True,
        "message": "这是我的自定义工具",
        "data": request
    }
```

## 🔍 关键文件速查表

| 文件路径 | 作用 | 重要程度 |
|---------|------|----------|
| `src/interfaces/base.py` | 核心接口定义 | ⭐⭐⭐⭐⭐ |
| `src/main_integration.py` | 主集成入口 | ⭐⭐⭐⭐⭐ |
| `src/mcp_server/server.py` | MCP服务器 | ⭐⭐⭐⭐⭐ |
| `src/mcp_server/schemas.py` | 数据模型 | ⭐⭐⭐⭐ |
| `src/ai_engine/engine.py` | AI处理核心 | ⭐⭐⭐⭐ |
| `src/security/engine.py` | 安全验证 | ⭐⭐⭐⭐ |
| `src/execution/executor.py` | 命令执行 | ⭐⭐⭐⭐ |
| `src/config/models.py` | 配置管理 | ⭐⭐⭐ |
| `src/startup_system.py` | 启动系统 | ⭐⭐⭐ |

## 🛠️ 常用调试技巧

### 1. 日志调试
```python
# 在代码中添加调试日志
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("这是调试信息")
logger.info("这是普通信息")
logger.warning("这是警告信息")
```

### 2. 断点调试
```python
# 在关键位置添加断点
import pdb; pdb.set_trace()

# 或使用更现代的调试器
import ipdb; ipdb.set_trace()
```

### 3. 单元测试调试
```bash
# 运行特定测试并显示详细输出
python -m pytest src/ai_engine/test_engine.py::TestAIEngine::test_translate_natural_language -v -s

# 运行测试并在失败时进入调试器
python -m pytest src/ai_engine/test_engine.py --pdb
```

## 🎯 学习检查点

完成每个阶段后，检查你是否能够：

### 阶段1检查点
- [ ] 理解项目的核心目标和功能
- [ ] 知道项目的主要组件和架构
- [ ] 了解MCP协议的基本概念

### 阶段2检查点
- [ ] 能够阅读和理解核心接口定义
- [ ] 知道每个组件的职责和作用
- [ ] 理解数据在组件间的流转

### 阶段3检查点
- [ ] 能够成功运行项目
- [ ] 理解测试的作用和结果
- [ ] 能够启动完整的服务

### 阶段4检查点
- [ ] 能够通过API与系统交互
- [ ] 理解请求和响应的格式
- [ ] 能够编写简单的客户端代码

### 阶段5检查点
- [ ] 能够修改配置文件
- [ ] 理解如何定制安全规则
- [ ] 知道如何扩展系统功能

## 🆘 遇到问题时

1. **查看日志**: 检查 `logs/` 目录下的日志文件
2. **运行测试**: 确保所有测试都能通过
3. **查看文档**: 参考 `docs/` 目录下的详细文档
4. **检查配置**: 确认配置文件格式正确
5. **环境检查**: 确保Python版本和依赖都正确安装

## 🎉 恭喜！

完成这个学习指南后，你应该对AI PowerShell Assistant项目有了全面的了解，能够：
- 理解项目架构和设计思路
- 运行和测试项目功能
- 进行基本的配置和定制
- 为项目贡献代码或报告问题

继续探索项目的高级功能，或者开始为项目做贡献吧！