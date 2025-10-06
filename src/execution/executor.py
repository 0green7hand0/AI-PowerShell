"""
命令执行器模块

本模块实现 PowerShell 命令的执行功能，包括：
- PowerShell 版本检测（PowerShell Core 和 Windows PowerShell）
- 同步和异步命令执行
- 超时控制和错误处理
- 执行结果封装
"""

import subprocess
import asyncio
import platform
import shutil
from typing import Optional, Any
from datetime import datetime
import time

from ..interfaces.base import (
    ExecutorInterface,
    ExecutionResult,
    ExecutionStatus,
    Context
)


class CommandExecutor(ExecutorInterface):
    """命令执行器主类
    
    负责 PowerShell 命令的实际执行，支持同步和异步执行模式。
    自动检测可用的 PowerShell 版本（pwsh 或 powershell）。
    """
    
    def __init__(self, encoding: str = "utf-8", default_timeout: int = 30):
        """初始化执行器
        
        Args:
            encoding: 输出编码，Windows 默认使用 gbk，其他平台使用 utf-8
            default_timeout: 默认超时时间（秒）
        """
        self.encoding = encoding
        self.default_timeout = default_timeout
        self.powershell_cmd = self._detect_powershell()
        self.platform_name = platform.system()
        
        # Windows 平台自动使用 gbk 编码
        if self.platform_name == "Windows" and encoding == "utf-8":
            self.encoding = "gbk"
    
    def _detect_powershell(self) -> Optional[str]:
        """检测可用的 PowerShell 版本
        
        优先检测 PowerShell Core (pwsh)，然后检测 Windows PowerShell。
        
        Returns:
            str: PowerShell 命令名称 ('pwsh' 或 'powershell')，如果都不可用则返回 None
        """
        # 1. 尝试 PowerShell Core (跨平台)
        if shutil.which('pwsh'):
            try:
                result = subprocess.run(
                    ['pwsh', '-Command', 'echo "test"'],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
                return 'pwsh'
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        # 2. 尝试 Windows PowerShell (仅 Windows)
        if platform.system() == "Windows":
            if shutil.which('powershell'):
                try:
                    result = subprocess.run(
                        ['powershell', '-Command', 'echo "test"'],
                        capture_output=True,
                        timeout=5,
                        check=True
                    )
                    return 'powershell'
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    pass
        
        return None
    
    def is_available(self) -> bool:
        """检查 PowerShell 是否可用
        
        Returns:
            bool: PowerShell 是否在系统中可用
        """
        return self.powershell_cmd is not None
    
    def execute(self, command: str, timeout: Optional[int] = None) -> ExecutionResult:
        """执行 PowerShell 命令（同步）
        
        Args:
            command: 要执行的 PowerShell 命令
            timeout: 超时时间（秒），如果为 None 则使用默认超时时间
            
        Returns:
            ExecutionResult: 包含执行结果的对象
            
        Raises:
            RuntimeError: 当 PowerShell 不可用时
        """
        if not self.is_available():
            return ExecutionResult(
                success=False,
                command=command,
                error="PowerShell 不可用，请安装 PowerShell Core (pwsh) 或 Windows PowerShell",
                return_code=-1,
                status=ExecutionStatus.FAILED,
                timestamp=datetime.now()
            )
        
        if timeout is None:
            timeout = self.default_timeout
        
        start_time = time.time()
        
        try:
            # 构建命令
            full_cmd = [self.powershell_cmd, '-Command', command]
            
            # 执行命令
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding=self.encoding,
                errors='ignore'  # 忽略编码错误
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                command=command,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                status=ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
                timestamp=datetime.now(),
                metadata={
                    'powershell_version': self.powershell_cmd,
                    'platform': self.platform_name,
                    'encoding': self.encoding
                }
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                output="",
                error=f"命令执行超时 ({timeout} 秒)",
                return_code=-1,
                execution_time=execution_time,
                status=ExecutionStatus.TIMEOUT,
                timestamp=datetime.now(),
                metadata={
                    'powershell_version': self.powershell_cmd,
                    'platform': self.platform_name,
                    'timeout': timeout
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                output="",
                error=f"执行错误: {str(e)}",
                return_code=-1,
                execution_time=execution_time,
                status=ExecutionStatus.FAILED,
                timestamp=datetime.now(),
                metadata={
                    'powershell_version': self.powershell_cmd,
                    'platform': self.platform_name,
                    'exception': type(e).__name__
                }
            )
    
    async def execute_async(self, command: str, timeout: Optional[int] = None) -> ExecutionResult:
        """异步执行 PowerShell 命令
        
        Args:
            command: 要执行的 PowerShell 命令
            timeout: 超时时间（秒），如果为 None 则使用默认超时时间
            
        Returns:
            ExecutionResult: 包含执行结果的对象
        """
        if not self.is_available():
            return ExecutionResult(
                success=False,
                command=command,
                error="PowerShell 不可用",
                return_code=-1,
                status=ExecutionStatus.FAILED,
                timestamp=datetime.now()
            )
        
        if timeout is None:
            timeout = self.default_timeout
        
        start_time = time.time()
        
        try:
            # 构建命令
            full_cmd = [self.powershell_cmd, '-Command', command]
            
            # 异步执行命令
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 等待命令完成（带超时）
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                execution_time = time.time() - start_time
                return ExecutionResult(
                    success=False,
                    command=command,
                    output="",
                    error=f"命令执行超时 ({timeout} 秒)",
                    return_code=-1,
                    execution_time=execution_time,
                    status=ExecutionStatus.TIMEOUT,
                    timestamp=datetime.now()
                )
            
            execution_time = time.time() - start_time
            
            # 解码输出
            output = stdout.decode(self.encoding, errors='ignore')
            error = stderr.decode(self.encoding, errors='ignore')
            
            return ExecutionResult(
                success=process.returncode == 0,
                command=command,
                output=output,
                error=error,
                return_code=process.returncode,
                execution_time=execution_time,
                status=ExecutionStatus.SUCCESS if process.returncode == 0 else ExecutionStatus.FAILED,
                timestamp=datetime.now(),
                metadata={
                    'powershell_version': self.powershell_cmd,
                    'platform': self.platform_name,
                    'encoding': self.encoding,
                    'async': True
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                output="",
                error=f"异步执行错误: {str(e)}",
                return_code=-1,
                execution_time=execution_time,
                status=ExecutionStatus.FAILED,
                timestamp=datetime.now(),
                metadata={
                    'powershell_version': self.powershell_cmd,
                    'platform': self.platform_name,
                    'exception': type(e).__name__,
                    'async': True
                }
            )
    
    def get_powershell_version(self) -> Optional[str]:
        """获取 PowerShell 版本信息
        
        Returns:
            str: PowerShell 版本字符串，如果不可用则返回 None
        """
        if not self.is_available():
            return None
        
        try:
            result = subprocess.run(
                [self.powershell_cmd, '-Command', '$PSVersionTable.PSVersion.ToString()'],
                capture_output=True,
                text=True,
                timeout=5,
                encoding=self.encoding,
                errors='ignore'
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except Exception:
            pass
        
        return None
    
    def execute_script_file(self, script_path: str, timeout: Optional[int] = None) -> ExecutionResult:
        """执行 PowerShell 脚本文件
        
        Args:
            script_path: 脚本文件路径
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        if not self.is_available():
            return ExecutionResult(
                success=False,
                command=f"Execute script: {script_path}",
                error="PowerShell 不可用",
                return_code=-1,
                status=ExecutionStatus.FAILED,
                timestamp=datetime.now()
            )
        
        if timeout is None:
            timeout = self.default_timeout
        
        start_time = time.time()
        
        try:
            # 构建命令
            full_cmd = [self.powershell_cmd, '-File', script_path]
            
            # 执行脚本
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding=self.encoding,
                errors='ignore'
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                command=f"Execute script: {script_path}",
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                status=ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
                timestamp=datetime.now(),
                metadata={
                    'powershell_version': self.powershell_cmd,
                    'platform': self.platform_name,
                    'script_path': script_path
                }
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=f"Execute script: {script_path}",
                output="",
                error=f"脚本执行超时 ({timeout} 秒)",
                return_code=-1,
                execution_time=execution_time,
                status=ExecutionStatus.TIMEOUT,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=f"Execute script: {script_path}",
                output="",
                error=f"脚本执行错误: {str(e)}",
                return_code=-1,
                execution_time=execution_time,
                status=ExecutionStatus.FAILED,
                timestamp=datetime.now()
            )
