"""
AI 提供商模块

定义 AI 提供商的抽象接口和具体实现。
支持多种本地 AI 模型（LLaMA、Ollama 等）。
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..interfaces.base import Suggestion, Context


class AIProvider(ABC):
    """AI 提供商抽象基类
    
    定义所有 AI 提供商必须实现的接口。
    """
    
    @abstractmethod
    def generate(self, text: str, context: Context) -> Suggestion:
        """生成命令建议
        
        Args:
            text: 用户输入的自然语言
            context: 当前上下文
            
        Returns:
            Suggestion: 生成的命令建议
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供商是否可用
        
        Returns:
            bool: 提供商是否可用
        """
        pass
    
    def _build_prompt(self, text: str, context: Context) -> str:
        """构建提示词
        
        Args:
            text: 用户输入
            context: 上下文
            
        Returns:
            str: 构建的提示词
        """
        prompt = f"""你是一个 PowerShell 命令专家。请将中文描述转换为标准的 PowerShell 命令。

用户输入: {text}

重要规则:
1. 只返回一行 PowerShell 命令，不要有任何解释或说明
2. 必须使用真实存在的 PowerShell cmdlet
3. 命令必须可以直接在 Windows PowerShell 中执行
4. 不要编造不存在的命令

常用 PowerShell 命令参考:
- 查看进程: Get-Process
- 查看内存: Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
- 查看服务: Get-Service
- 查看文件: Get-ChildItem
- 查看时间: Get-Date
- 查看系统信息: Get-ComputerInfo
- 查看磁盘: Get-PSDrive
- 查看网络: Get-NetAdapter
- 测试连接: Test-NetConnection

"""
        
        # 添加历史上下文
        if context.command_history:
            recent = context.get_recent_commands(3)
            prompt += f"最近执行的命令:\n"
            for cmd in recent:
                prompt += f"- {cmd}\n"
            prompt += "\n"
        
        prompt += "请直接返回 PowerShell 命令:"
        
        return prompt
    
    def _parse_result(self, result: str, original_input: str) -> Suggestion:
        """解析 AI 模型返回的结果
        
        Args:
            result: AI 模型返回的原始结果
            original_input: 用户原始输入
            
        Returns:
            Suggestion: 解析后的建议
        """
        # 清理结果
        command = result.strip()
        
        # 移除可能的代码块标记
        if command.startswith('```'):
            lines = command.split('\n')
            command = '\n'.join(lines[1:-1]) if len(lines) > 2 else command
            command = command.strip()
        
        # 移除 powershell 标记
        if command.lower().startswith('powershell'):
            command = command[10:].strip()
        
        # 提取第一行作为主命令
        main_command = command.split('\n')[0].strip()
        
        return Suggestion(
            original_input=original_input,
            generated_command=main_command,
            confidence_score=0.80,  # AI 生成的默认置信度
            explanation=f"AI 生成的命令: {main_command}",
            alternatives=[]
        )


class LocalLLaMAProvider(AIProvider):
    """本地 LLaMA 模型提供商
    
    使用 llama-cpp-python 运行本地 LLaMA 模型。
    """
    
    def __init__(self, config: Dict):
        """初始化 LLaMA 提供商
        
        Args:
            config: 配置字典，包含模型路径等信息
        """
        self.config = config
        self.model_path = config.get('model_path', '')
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化 LLaMA 模型"""
        try:
            from llama_cpp import Llama
            
            if not self.model_path:
                return
            
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0  # CPU 模式
            )
        except ImportError:
            print("警告: llama-cpp-python 未安装，LLaMA 提供商不可用")
        except Exception as e:
            print(f"警告: 初始化 LLaMA 模型失败: {e}")
    
    def is_available(self) -> bool:
        """检查 LLaMA 是否可用"""
        return self.model is not None
    
    def generate(self, text: str, context: Context) -> Suggestion:
        """使用 LLaMA 生成命令
        
        Args:
            text: 用户输入
            context: 上下文
            
        Returns:
            Suggestion: 生成的建议
        """
        if not self.is_available():
            raise RuntimeError("LLaMA 模型不可用")
        
        prompt = self._build_prompt(text, context)
        
        # 生成命令
        result = self.model(
            prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9,
            stop=["\n\n", "用户输入:"]
        )
        
        generated_text = result['choices'][0]['text']
        
        return self._parse_result(generated_text, text)


class OllamaProvider(AIProvider):
    """Ollama 模型提供商
    
    使用 Ollama 运行本地 AI 模型。
    """
    
    def __init__(self, config: Dict):
        """初始化 Ollama 提供商
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.model_name = config.get('model_name', 'llama2')
        self.base_url = config.get('ollama_url', 'http://localhost:11434')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化 Ollama 客户端"""
        try:
            import ollama
            self.client = ollama.Client(host=self.base_url)
        except ImportError:
            print("警告: ollama 包未安装，Ollama 提供商不可用")
        except Exception as e:
            print(f"警告: 初始化 Ollama 客户端失败: {e}")
    
    def is_available(self) -> bool:
        """检查 Ollama 是否可用"""
        if not self.client:
            return False
        
        try:
            # 尝试列出模型来检查连接
            self.client.list()
            return True
        except:
            return False
    
    def generate(self, text: str, context: Context) -> Suggestion:
        """使用 Ollama 生成命令
        
        Args:
            text: 用户输入
            context: 上下文
            
        Returns:
            Suggestion: 生成的建议
        """
        if not self.is_available():
            raise RuntimeError("Ollama 服务不可用")
        
        prompt = self._build_prompt(text, context)
        
        # 生成命令
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 256
            }
        )
        
        generated_text = response['response']
        
        return self._parse_result(generated_text, text)


class MockProvider(AIProvider):
    """模拟 AI 提供商
    
    用于测试和开发，不依赖实际的 AI 模型。
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化模拟提供商"""
        self.config = config or {}
    
    def is_available(self) -> bool:
        """模拟提供商始终可用"""
        return True
    
    def generate(self, text: str, context: Context) -> Suggestion:
        """生成模拟的命令建议
        
        Args:
            text: 用户输入
            context: 上下文
            
        Returns:
            Suggestion: 模拟的建议
        """
        # 简单的关键词匹配
        command_map = {
            '文件': 'Get-ChildItem',
            '目录': 'Get-ChildItem',
            '进程': 'Get-Process',
            '时间': 'Get-Date',
            '服务': 'Get-Service',
            '网络': 'Test-NetConnection localhost',
        }
        
        command = 'Get-Help'
        for keyword, cmd in command_map.items():
            if keyword in text:
                command = cmd
                break
        
        return Suggestion(
            original_input=text,
            generated_command=command,
            confidence_score=0.75,
            explanation=f"模拟 AI 生成的命令",
            alternatives=[]
        )


def get_provider(provider_name: str, config: Dict) -> AIProvider:
    """获取 AI 提供商实例
    
    Args:
        provider_name: 提供商名称 ('local', 'ollama', 'mock')
        config: 配置字典
        
    Returns:
        AIProvider: AI 提供商实例
        
    Raises:
        ValueError: 当提供商名称无效时
    """
    providers = {
        'local': LocalLLaMAProvider,
        'llama': LocalLLaMAProvider,
        'ollama': OllamaProvider,
        'mock': MockProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"未知的 AI 提供商: {provider_name}")
    
    return provider_class(config)
