"""
沙箱执行模块

实现第三层安全验证：在隔离的 Docker 容器中执行命令，提供资源限制和超时控制。
"""

import logging
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
        self.read_only = self.config.get('read_only', True)
        
        # Docker 客户端（延迟初始化）
        self._docker_client = None
        self._docker_available = None
    
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
        
        try:
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
                
                return ExecutionResult(
                    success=(return_code == 0),
                    command=command,
                    output=output,
                    error=error,
                    return_code=return_code,
                    execution_time=execution_time,
                    status=ExecutionStatus.SUCCESS if return_code == 0 else ExecutionStatus.FAILED,
                    metadata={
                        'sandbox': True,
                        'container_id': container.id[:12],
                        'image': self.docker_image
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
                self.logger.error(f"沙箱执行超时: {command}")
                return ExecutionResult(
                    success=False,
                    command=command,
                    error=f"执行超时（{timeout}秒）",
                    execution_time=time.time() - start_time,
                    status=ExecutionStatus.TIMEOUT
                )
            else:
                self.logger.error(f"沙箱执行失败: {e}")
                return ExecutionResult(
                    success=False,
                    command=command,
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
        
        # 网络隔离
        if self.network_disabled:
            config['network_mode'] = 'none'
        
        # 只读文件系统
        if self.read_only:
            config['read_only'] = True
            # 添加临时目录挂载点
            config['tmpfs'] = {'/tmp': 'rw,noexec,nosuid,size=100m'}
        
        # 安全选项
        config['security_opt'] = ['no-new-privileges:true']
        
        # 资源限制
        config['pids_limit'] = 100  # 限制进程数
        
        return config
    
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
            'read_only': self.read_only
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
