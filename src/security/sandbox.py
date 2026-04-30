"""
沙箱执行模块

实现第三层安全验证：在隔离的 Docker 容器中执行命令，提供资源限制和超时控制。
"""

import logging
import platform
import time
from typing import Optional, Dict, Any
from src.interfaces.base import ExecutionResult, ExecutionStatus


class SandboxExecutor:
    """沙箱执行器
    
    使用 Docker 容器隔离执行 PowerShell 命令，提供额外的安全保护。
    """
    
    def __init__(self, config: dict = None):
        """初始化沙箱执行器
        
        Args:
            config: 配置字典，可包含：
                - docker_image: Docker 镜像名称
                - memory_limit: 内存限制（如 "512m"）
                - cpu_limit: CPU 限制（如 0.5）
                - timeout: 超时时间（秒）
                - network_disabled: 是否禁用网络
                - read_only: 是否只读文件系统
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 配置选项
        self.docker_image = self.config.get('docker_image', 'mcr.microsoft.com/powershell:latest')
        self.memory_limit = self.config.get('memory_limit', '512m')
        self.cpu_limit = self.config.get('cpu_limit', 0.5)
        self.timeout = self.config.get('timeout', 30)
        self.network_disabled = self.config.get('network_disabled', True)
        self.read_only = self.config.get('read_only', False)  # 默认改为 False 以支持文件操作
        
        # Docker 客户端（延迟初始化）
        self._docker_client = None
        self._docker_available = None
        
        # 检测是否是 Windows 系统
        self.is_windows = platform.system() == 'Windows'
    
    @property
    def docker_client(self):
        """获取 Docker 客户端（延迟初始化）"""
        if self._docker_client is None:
            try:
                import docker
                self._docker_client = docker.from_env()
                self._docker_available = True
                self.logger.info("Docker 客户端初始化成功")
            except ImportError:
                self.logger.error("docker-py 未安装，无法使用沙箱功能")
                self._docker_available = False
            except Exception as e:
                self.logger.error(f"Docker 客户端初始化失败: {e}")
                self._docker_available = False
        
        return self._docker_client
    
    def is_available(self) -> bool:
        """检查沙箱是否可用
        
        Returns:
            bool: Docker 是否可用
        """
        if self._docker_available is None:
            # 触发延迟初始化
            _ = self.docker_client
        
        return self._docker_available
    
    def execute(self, command: str, timeout: Optional[int] = None) -> ExecutionResult:
        """在沙箱中执行命令
        
        Args:
            command: 要执行的 PowerShell 命令
            timeout: 超时时间（秒），如果为 None 则使用配置的默认值
            
        Returns:
            ExecutionResult: 执行结果
        """
        if not self.is_available():
            return ExecutionResult(
                success=False,
                command=command,
                error="Docker 不可用，无法使用沙箱执行",
                status=ExecutionStatus.FAILED
            )
        
        timeout = timeout or self.timeout
        start_time = time.time()
        
        # 保存原始命令
        original_command = command
        
        try:
            # Windows 系统：转换路径
            if self.is_windows:
                command = self._convert_windows_path_to_container(command)
                self.logger.info(f"路径转换: {original_command} -> {command}")
            
            # 构建 Docker 运行参数
            container_config = self._build_container_config(command)
            
            self.logger.info(f"在沙箱中执行命令: {command}")
            
            # 运行容器
            container = self.docker_client.containers.run(
                **container_config,
                detach=True
            )
            
            try:
                # 等待容器执行完成
                result = container.wait(timeout=timeout)
                
                # 获取输出
                output = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
                error = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
                
                execution_time = time.time() - start_time
                return_code = result.get('StatusCode', -1)
                
                # 构建详细的输出信息
                detailed_output = output
                if not output and not error:
                    # 如果没有输出，添加沙箱执行说明
                    if return_code == 0:
                        detailed_output = f"[沙箱执行成功]\n" \
                            f"容器ID: {container.id[:12]}\n" \
                            f"镜像: {self.docker_image}\n" \
                            f"执行时间: {execution_time:.3f}s\n" \
                            f"注意: 命令在隔离容器中执行，不会影响宿主机文件系统。"
                    else:
                        detailed_output = f"[沙箱执行完成，返回码: {return_code}]"
                elif return_code != 0 and error:
                    # 如果有错误，添加错误说明
                    error_lower = error.lower()
                    if "permission denied" in error_lower or "access" in error_lower and "denied" in error_lower:
                        error = f"[沙箱保护] 操作被拒绝 - 文件系统为只读模式\n" \
                            f"原始错误: {error}\n" \
                            f"说明: 沙箱模式保护了您的系统，文件未被修改。\n" \
                            f"如果确实需要执行此操作，请关闭沙箱模式后重试。"
                
                return ExecutionResult(
                    success=(return_code == 0),
                    command=original_command,  # 返回原始命令
                    output=detailed_output,
                    error=error,
                    return_code=return_code,
                    execution_time=execution_time,
                    status=ExecutionStatus.SUCCESS if return_code == 0 else ExecutionStatus.FAILED,
                    metadata={
                        'sandbox': True,
                        'container_id': container.id[:12],
                        'image': self.docker_image,
                        'converted_command': command if command != original_command else None
                    }
                )
            
            finally:
                # 清理容器
                try:
                    container.remove(force=True)
                except Exception as e:
                    self.logger.warning(f"清理容器失败: {e}")
        
        except Exception as e:
            if "timeout" in str(e).lower():
                self.logger.error(f"沙箱执行超时: {original_command}")
                return ExecutionResult(
                    success=False,
                    command=original_command,
                    error=f"执行超时（{timeout}秒）",
                    execution_time=time.time() - start_time,
                    status=ExecutionStatus.TIMEOUT
                )
            else:
                self.logger.error(f"沙箱执行失败: {e}")
                return ExecutionResult(
                    success=False,
                    command=original_command,
                    error=f"沙箱执行失败: {str(e)}",
                    execution_time=time.time() - start_time,
                    status=ExecutionStatus.FAILED
                )
    
    def _build_container_config(self, command: str) -> Dict[str, Any]:
        """构建容器配置
        
        Args:
            command: 要执行的命令
            
        Returns:
            dict: Docker 容器配置
        """
        config = {
            'image': self.docker_image,
            'command': ['pwsh', '-Command', command],
            'remove': False,  # 手动清理以便获取日志
            'mem_limit': self.memory_limit,
            'nano_cpus': int(self.cpu_limit * 1e9),  # 转换为纳秒
        }
        
        # Windows 系统：挂载文件系统（只读模式，保护宿主机）
        if self.is_windows:
            import os
            # 挂载用户目录到容器（只读）
            user_home = os.path.expanduser('~')
            config['volumes'] = {
                user_home: {
                    'bind': '/mnt/host/home',
                    'mode': 'ro'  # 只读模式，保护宿主机
                },
                'C:\\': {
                    'bind': '/mnt/host/c',
                    'mode': 'ro'  # 只读模式，保护宿主机
                }
            }
            self.logger.info(f"Windows 挂载（只读）: {user_home} -> /mnt/host/home, C:\\ -> /mnt/host/c")
        
        # 网络隔离
        if self.network_disabled:
            config['network_mode'] = 'none'
        
        # 只读文件系统（仅在非 Windows 或不需要文件操作时启用）
        if self.read_only and not self.is_windows:
            config['read_only'] = True
            # 添加临时目录挂载点
            config['tmpfs'] = {'/tmp': 'rw,noexec,nosuid,size=100m'}
        
        # 安全选项
        config['security_opt'] = ['no-new-privileges:true']
        
        # 资源限制
        config['pids_limit'] = 100  # 限制进程数
        
        return config
    
    def _convert_windows_path_to_container(self, command: str) -> str:
        """将 Windows 路径转换为容器内的路径
        
        Args:
            command: 包含 Windows 路径的命令
            
        Returns:
            str: 转换后的命令
        """
        if not self.is_windows:
            return command
        
        import re
        
        # 转换 C:\Users\xxx -> /mnt/host/c/Users/xxx
        command = re.sub(
            r'([A-Za-z]):\\',
            lambda m: f'/mnt/host/{m.group(1).lower()}/',
            command
        )
        
        # 转换反斜杠为正斜杠（在路径中）
        # 但要小心不要转换转义字符
        # 这里简单处理：转换路径中的反斜杠
        
        return command
    
    def pull_image(self) -> bool:
        """拉取 Docker 镜像
        
        Returns:
            bool: 是否成功拉取镜像
        """
        if not self.is_available():
            return False
        
        try:
            self.logger.info(f"拉取 Docker 镜像: {self.docker_image}")
            self.docker_client.images.pull(self.docker_image)
            self.logger.info("镜像拉取成功")
            return True
        except Exception as e:
            self.logger.error(f"拉取镜像失败: {e}")
            return False
    
    def check_image_exists(self) -> bool:
        """检查镜像是否存在
        
        Returns:
            bool: 镜像是否存在
        """
        if not self.is_available():
            return False
        
        try:
            self.docker_client.images.get(self.docker_image)
            return True
        except Exception:
            return False
    
    def get_sandbox_info(self) -> Dict[str, Any]:
        """获取沙箱信息
        
        Returns:
            dict: 沙箱配置信息
        """
        return {
            'available': self.is_available(),
            'image': self.docker_image,
            'image_exists': self.check_image_exists() if self.is_available() else False,
            'memory_limit': self.memory_limit,
            'cpu_limit': self.cpu_limit,
            'timeout': self.timeout,
            'network_disabled': self.network_disabled,
            'read_only': self.read_only,
            'is_windows': self.is_windows
        }
    
    def cleanup_containers(self) -> int:
        """清理所有停止的容器
        
        Returns:
            int: 清理的容器数量
        """
        if not self.is_available():
            return 0
        
        try:
            containers = self.docker_client.containers.list(
                all=True,
                filters={'status': 'exited'}
            )
            
            count = 0
            for container in containers:
                try:
                    container.remove()
                    count += 1
                except Exception as e:
                    self.logger.warning(f"清理容器 {container.id[:12]} 失败: {e}")
            
            self.logger.info(f"清理了 {count} 个停止的容器")
            return count
        
        except Exception as e:
            self.logger.error(f"清理容器失败: {e}")
            return 0
