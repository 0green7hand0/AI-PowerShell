"""
AI 提供商模块

定义 AI 提供商的抽象接口和具体实现。
支持 Ollama 本地部署和直接 API 调用。
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
        # 使用非常严格的提示词，强制只输出命令
        prompt = f"""Convert to PowerShell command. Output ONLY the command, no explanation.

{text}

Command:"""
        
        return prompt
    
    def _parse_result(self, result: str, original_input: str) -> Suggestion:
        """解析 AI 模型返回的结果
        
        Args:
            result: AI 模型返回的原始结果
            original_input: 用户原始输入
            
        Returns:
            Suggestion: 解析后的建议
            
        Raises:
            ValueError: 当 AI 返回空结果时
        """
        # 清理结果
        command = result.strip()
        
        # 检查是否为空
        if not command:
            print(f"调试: AI 返回空字符串")
            raise ValueError(f"AI 模型返回空结果，原始输入: {original_input}")
        
        # 处理思考模式输出 - 查找 "...done thinking." 后的内容
        if '...done thinking.' in command:
            parts = command.split('...done thinking.')
            if len(parts) > 1:
                command = parts[1].strip()
        
        # 移除思考过程标记
        thinking_markers = ['Thinking...', '思考中...', '嗯，', '首先，', '不过，', '所以']
        for marker in thinking_markers:
            if command.startswith(marker):
                # 跳过思考部分，查找实际命令
                lines = command.split('\n')
                for line in lines:
                    line = line.strip()
                    # 查找看起来像 PowerShell 命令的行
                    if line and (line.startswith('Get-') or line.startswith('Set-') or 
                                line.startswith('Test-') or line.startswith('New-') or
                                line.startswith('Remove-') or line.startswith('Start-') or
                                line.startswith('Stop-')):
                        command = line
                        break
        
        # 移除可能的代码块标记
        if command.startswith('```'):
            lines = command.split('\n')
            command = '\n'.join(lines[1:-1]) if len(lines) > 2 else command
            command = command.strip()
        
        # 移除 powershell 标记
        if command.lower().startswith('powershell'):
            command = command[10:].strip()
        
        # 移除"输出:"等前缀
        prefixes = ['输出:', '输出：', 'Output:', '命令:', '命令：', 'Command:']
        for prefix in prefixes:
            if command.startswith(prefix):
                command = command[len(prefix):].strip()
        
        # 提取第一行作为主命令
        main_command = command.split('\n')[0].strip()
        
        # 再次检查清理后的命令是否为空
        if not main_command:
            print(f"调试: 清理后命令为空，原始响应: {result[:200]}")
            raise ValueError(f"AI 模型返回的命令为空，原始响应: {result[:200]}")
        
        # 验证是否是有效的 PowerShell 命令
        valid_starts = ['Get-', 'Set-', 'Test-', 'New-', 'Remove-', 'Start-', 'Stop-', 
                       'Add-', 'Clear-', 'Copy-', 'Move-', 'Invoke-', 'Select-', 
                       'Where-', 'Sort-', 'Measure-', 'Format-', 'Out-', 'Write-',
                       'Read-', 'Show-', 'Find-', 'Search-']
        
        if not any(main_command.startswith(prefix) for prefix in valid_starts):
            # 可能不是有效的 PowerShell 命令
            print(f"调试: 命令不是有效的 PowerShell 命令: {main_command}")
            raise ValueError(f"AI 返回的不是有效的 PowerShell 命令: {main_command}")
        
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
        
        # 使用 HTTP 请求而不是客户端库
        import requests
        import json
        
        try:
            print(f"[DEBUG] 发送提示词: {prompt}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "raw": True,  # 使用原始模式，禁用思考
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 256,
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"[DEBUG] 完整响应: {result}")
            
            # qwen3:30b 模型会把内容放在 'thinking' 字段而不是 'response' 字段
            generated_text = result.get('response', '')
            if not generated_text and 'thinking' in result:
                generated_text = result.get('thinking', '')
                print(f"[DEBUG] 使用 thinking 字段")
            
            print(f"[DEBUG] 提取的文本: '{generated_text[:200]}'")
            print(f"[DEBUG] 文本长度: {len(generated_text)}")
            
        except Exception as e:
            print(f"[DEBUG] HTTP 请求失败: {e}")
            raise RuntimeError(f"Ollama HTTP 请求失败: {e}")
        
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
