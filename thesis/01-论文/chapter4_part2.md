#### 4.4 接口设计

接口设计定义了模块间的交互方式和外部调用接口。本节介绍模块间接口和外部接口的设计。

##### 4.4.1 模块间接口

模块间通过定义良好的接口进行交互，确保松耦合和高内聚。

**1. AI引擎接口**

```python
class AIEngineInterface(ABC):
    """AI引擎接口"""
    
    @abstractmethod
    def translate(self, user_input: str, context: Context) -> Suggestion:
        """
        将用户输入翻译为PowerShell命令
        
        Args:
            user_input: 用户的中文输入
            context: 执行上下文
            
        Returns:
            Suggestion: 命令建议，包含生成的命令和置信度
            
        Raises:
            TranslationError: 翻译失败时抛出
        """
        pass
    
    @abstractmethod
    def validate_command(self, command: str) -> bool:
        """
        验证命令的语法有效性
        
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
```

**2. 安全引擎接口**

```python
class SecurityEngineInterface(ABC):
    """安全引擎接口"""
    
    @abstractmethod
    def validate(self, command: str, context: Context) -> ValidationResult:
        """
        验证命令的安全性
        
        Args:
            command: PowerShell命令
            context: 执行上下文
            
        Returns:
            ValidationResult: 验证结果，包含风险等级和警告
        """
        pass
    
    @abstractmethod
    def check_permissions(self, command: str) -> bool:
        """
        检查当前用户是否有执行命令的权限
        
        Args:
            command: PowerShell命令
            
        Returns:
            bool: 是否有权限
        """
        pass
    
    @abstractmethod
    def execute_in_sandbox(self, command: str, timeout: int) -> ExecutionResult:
        """
        在沙箱环境中执行命令
        
        Args:
            command: PowerShell命令
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
```

**3. 执行器接口**

```python
class ExecutorInterface(ABC):
    """执行器接口"""
    
    @abstractmethod
    def execute(self, command: str, timeout: int = None) -> ExecutionResult:
        """
        执行PowerShell命令
        
        Args:
            command: PowerShell命令
            timeout: 超时时间（秒），None表示使用默认值
            
        Returns:
            ExecutionResult: 执行结果
            
        Raises:
            ExecutionError: 执行失败时抛出
        """
        pass
    
    @abstractmethod
    def execute_async(self, command: str, callback: Callable = None) -> AsyncTask:
        """
        异步执行命令
        
        Args:
            command: PowerShell命令
            callback: 完成时的回调函数
            
        Returns:
            AsyncTask: 异步任务对象
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
```

**4. 存储接口**

```python
class StorageInterface(ABC):
    """存储接口"""
    
    @abstractmethod
    def save(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        保存数据
        
        Args:
            key: 键
            value: 值
            ttl: 过期时间（秒），None表示永不过期
            
        Returns:
            bool: 是否保存成功
        """
        pass
    
    @abstractmethod
    def load(self, key: str, default: Any = None) -> Any:
        """
        加载数据
        
        Args:
            key: 键
            default: 默认值
            
        Returns:
            Any: 存储的值，如果不存在则返回default
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        删除数据
        
        Args:
            key: 键
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键
            
        Returns:
            bool: 键是否存在
        """
        pass
```

##### 4.4.2 外部接口

系统提供多种外部接口供用户和其他程序调用。

**1. Python API接口**

```python
class PowerShellAssistant:
    """Python API接口"""
    
    def __init__(self, config_path: str = None):
        """
        初始化助手
        
        Args:
            config_path: 配置文件路径，None表示使用默认配置
        """
        pass
    
    def translate(self, user_input: str) -> Suggestion:
        """
        翻译用户输入为PowerShell命令
        
        Args:
            user_input: 用户的中文输入
            
        Returns:
            Suggestion: 命令建议
            
        Example:
            >>> assistant = PowerShellAssistant()
            >>> result = assistant.translate("显示当前时间")
            >>> print(result.generated_command)
            Get-Date
        """
        pass
    
    def execute(self, command: str, confirm: bool = True) -> ExecutionResult:
        """
        执行PowerShell命令
        
        Args:
            command: PowerShell命令
            confirm: 是否需要确认（对于危险命令）
            
        Returns:
            ExecutionResult: 执行结果
            
        Example:
            >>> assistant = PowerShellAssistant()
            >>> result = assistant.execute("Get-Date")
            >>> print(result.output)
            2024-01-15 14:30:25
        """
        pass
    
    def process(self, user_input: str, auto_execute: bool = False) -> ProcessResult:
        """
        处理用户请求（翻译+验证+执行）
        
        Args:
            user_input: 用户的中文输入
            auto_execute: 是否自动执行（跳过确认）
            
        Returns:
            ProcessResult: 完整的处理结果
            
        Example:
            >>> assistant = PowerShellAssistant()
            >>> result = assistant.process("显示当前时间", auto_execute=True)
            >>> print(result.execution.output)
            2024-01-15 14:30:25
        """
        pass
    
    def get_history(self, limit: int = 10) -> List[CommandEntry]:
        """
        获取命令历史
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            List[CommandEntry]: 命令历史列表
        """
        pass
    
    def clear_history(self) -> bool:
        """
        清空命令历史
        
        Returns:
            bool: 是否成功
        """
        pass
```

**使用示例**：

```python
from ai_powershell import PowerShellAssistant

# 创建助手实例
assistant = PowerShellAssistant()

# 翻译命令
suggestion = assistant.translate("显示CPU最高的5个进程")
print(f"命令: {suggestion.generated_command}")
print(f"置信度: {suggestion.confidence_score}")
print(f"解释: {suggestion.explanation}")

# 执行命令
result = assistant.execute(suggestion.generated_command)
if result.success:
    print(f"输出:\n{result.output}")
else:
    print(f"错误: {result.error}")

# 一步完成（翻译+执行）
result = assistant.process("显示当前时间", auto_execute=True)
print(result.execution.output)

# 查看历史
history = assistant.get_history(limit=5)
for entry in history:
    print(f"{entry.timestamp}: {entry.user_input} -> {entry.translated_command}")
```

**2. CLI命令行接口**

```bash
# 翻译命令（不执行）
ai-powershell translate "显示当前时间"

# 执行命令
ai-powershell execute "Get-Date"

# 翻译并执行
ai-powershell run "显示当前时间"

# 交互式模式
ai-powershell interactive

# 查看历史
ai-powershell history --limit 10

# 导出历史
ai-powershell history --export history.json

# 清空历史
ai-powershell history --clear

# 查看配置
ai-powershell config --show

# 修改配置
ai-powershell config --set ai.model=llama2

# 查看帮助
ai-powershell --help
```

**CLI参数设计**：

```python
import argparse

def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="ai-powershell",
        description="AI PowerShell智能助手",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 全局选项
    parser.add_argument(
        "--config",
        type=str,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # translate子命令
    translate_parser = subparsers.add_parser(
        "translate",
        help="翻译中文描述为PowerShell命令"
    )
    translate_parser.add_argument(
        "input",
        type=str,
        help="中文描述"
    )
    translate_parser.add_argument(
        "--explain",
        action="store_true",
        help="显示命令解释"
    )
    
    # execute子命令
    execute_parser = subparsers.add_parser(
        "execute",
        help="执行PowerShell命令"
    )
    execute_parser.add_argument(
        "command",
        type=str,
        help="PowerShell命令"
    )
    execute_parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="超时时间（秒）"
    )
    
    # run子命令
    run_parser = subparsers.add_parser(
        "run",
        help="翻译并执行命令"
    )
    run_parser.add_argument(
        "input",
        type=str,
        help="中文描述"
    )
    run_parser.add_argument(
        "--yes",
        action="store_true",
        help="跳过确认，自动执行"
    )
    
    # interactive子命令
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="进入交互式模式"
    )
    
    # history子命令
    history_parser = subparsers.add_parser(
        "history",
        help="管理命令历史"
    )
    history_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="显示的记录数"
    )
    history_parser.add_argument(
        "--export",
        type=str,
        help="导出历史到文件"
    )
    history_parser.add_argument(
        "--clear",
        action="store_true",
        help="清空历史"
    )
    
    # config子命令
    config_parser = subparsers.add_parser(
        "config",
        help="管理配置"
    )
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="显示当前配置"
    )
    config_parser.add_argument(
        "--set",
        type=str,
        help="设置配置项（格式：key=value）"
    )
    
    return parser
```

**3. REST API接口（可选扩展）**

为了支持Web界面或远程调用，系统可以提供REST API接口：

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI PowerShell API")

class TranslateRequest(BaseModel):
    user_input: str
    context: Optional[Dict[str, Any]] = None

class TranslateResponse(BaseModel):
    generated_command: str
    confidence_score: float
    explanation: str
    alternatives: List[str]

class ExecuteRequest(BaseModel):
    command: str
    timeout: int = 30

class ExecuteResponse(BaseModel):
    success: bool
    output: str
    error: str
    return_code: int
    execution_time: float

@app.post("/api/v1/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """翻译API端点"""
    try:
        assistant = PowerShellAssistant()
        suggestion = assistant.translate(request.user_input)
        return TranslateResponse(
            generated_command=suggestion.generated_command,
            confidence_score=suggestion.confidence_score,
            explanation=suggestion.explanation,
            alternatives=suggestion.alternatives
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """执行API端点"""
    try:
        assistant = PowerShellAssistant()
        result = assistant.execute(request.command)
        return ExecuteResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            return_code=result.return_code,
            execution_time=result.execution_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/history")
async def get_history(limit: int = 10):
    """获取历史API端点"""
    try:
        assistant = PowerShellAssistant()
        history = assistant.get_history(limit=limit)
        return [entry.to_dict() for entry in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**API使用示例**：

```bash
# 翻译命令
curl -X POST http://localhost:8000/api/v1/translate \
  -H "Content-Type: application/json" \
  -d '{"user_input": "显示当前时间"}'

# 执行命令
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "Get-Date", "timeout": 30}'

# 获取历史
curl http://localhost:8000/api/v1/history?limit=5
```

