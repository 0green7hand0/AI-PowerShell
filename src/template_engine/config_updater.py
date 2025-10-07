"""
配置文件更新器模块

提供配置文件的读写、备份、恢复和并发控制功能。
"""

import os
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import yaml

from .exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateConflictError
)


class ConfigUpdater:
    """配置文件更新器
    
    负责管理 templates.yaml 配置文件的读写操作，
    包括添加、更新、删除模板配置，以及备份和恢复功能。
    """
    
    def __init__(self, config_path: str = "config/templates.yaml"):
        """初始化配置更新器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.backup_dir = self.config_path.parent / ".backups"
        self._lock = threading.Lock()
        
        # 确保配置文件存在
        if not self.config_path.exists():
            raise TemplateError(f"配置文件不存在: {self.config_path}")
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件
        
        Returns:
            配置字典
            
        Raises:
            TemplateError: 配置文件读取或解析失败
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config if config else {}
        except yaml.YAMLError as e:
            raise TemplateError(f"配置文件解析失败: {e}")
        except Exception as e:
            raise TemplateError(f"配置文件读取失败: {e}")
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置文件
        
        Args:
            config: 配置字典
            
        Raises:
            TemplateError: 配置文件保存失败
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2
                )
        except Exception as e:
            raise TemplateError(f"配置文件保存失败: {e}")
    
    def add_template_config(
        self,
        template_id: str,
        category: str,
        config: Dict[str, Any]
    ) -> bool:
        """添加模板配置
        
        Args:
            template_id: 模板ID
            category: 模板分类
            config: 模板配置字典
            
        Returns:
            是否添加成功
            
        Raises:
            TemplateConflictError: 模板已存在
            TemplateError: 添加失败
        """
        with self._lock:
            try:
                # 加载当前配置
                full_config = self._load_config()
                
                # 确保 templates 键存在
                if 'templates' not in full_config:
                    full_config['templates'] = {}
                
                # 确保分类存在
                if category not in full_config['templates']:
                    full_config['templates'][category] = {}
                
                # 检查模板是否已存在
                if template_id in full_config['templates'][category]:
                    raise TemplateConflictError(
                        f"模板 '{template_id}' 在分类 '{category}' 中已存在"
                    )
                
                # 添加模板配置
                full_config['templates'][category][template_id] = config
                
                # 保存配置
                self._save_config(full_config)
                
                return True
                
            except (TemplateConflictError, TemplateError):
                raise
            except Exception as e:
                raise TemplateError(f"添加模板配置失败: {e}")
    
    def update_template_config(
        self,
        template_id: str,
        category: str,
        config: Dict[str, Any]
    ) -> bool:
        """更新模板配置
        
        Args:
            template_id: 模板ID
            category: 模板分类
            config: 新的模板配置字典
            
        Returns:
            是否更新成功
            
        Raises:
            TemplateNotFoundError: 模板不存在
            TemplateError: 更新失败
        """
        with self._lock:
            try:
                # 加载当前配置
                full_config = self._load_config()
                
                # 检查模板是否存在
                if ('templates' not in full_config or
                    category not in full_config['templates'] or
                    template_id not in full_config['templates'][category]):
                    raise TemplateNotFoundError(
                        f"模板 '{template_id}' 在分类 '{category}' 中不存在"
                    )
                
                # 更新模板配置
                full_config['templates'][category][template_id] = config
                
                # 保存配置
                self._save_config(full_config)
                
                return True
                
            except (TemplateNotFoundError, TemplateError):
                raise
            except Exception as e:
                raise TemplateError(f"更新模板配置失败: {e}")
    
    def remove_template_config(
        self,
        template_id: str,
        category: str
    ) -> bool:
        """移除模板配置
        
        Args:
            template_id: 模板ID
            category: 模板分类
            
        Returns:
            是否移除成功
            
        Raises:
            TemplateNotFoundError: 模板不存在
            TemplateError: 移除失败
        """
        with self._lock:
            try:
                # 加载当前配置
                full_config = self._load_config()
                
                # 检查模板是否存在
                if ('templates' not in full_config or
                    category not in full_config['templates'] or
                    template_id not in full_config['templates'][category]):
                    raise TemplateNotFoundError(
                        f"模板 '{template_id}' 在分类 '{category}' 中不存在"
                    )
                
                # 移除模板配置
                del full_config['templates'][category][template_id]
                
                # 如果分类为空，可选择移除分类（保留以维持结构）
                # if not full_config['templates'][category]:
                #     del full_config['templates'][category]
                
                # 保存配置
                self._save_config(full_config)
                
                return True
                
            except (TemplateNotFoundError, TemplateError):
                raise
            except Exception as e:
                raise TemplateError(f"移除模板配置失败: {e}")
    
    def backup_config(self) -> str:
        """创建配置文件备份
        
        Returns:
            备份文件路径
            
        Raises:
            TemplateError: 备份失败
        """
        try:
            # 生成备份文件名（包含微秒以避免冲突）
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            microseconds = now.microsecond
            backup_filename = f"templates_{timestamp}_{microseconds}.yaml"
            backup_path = self.backup_dir / backup_filename
            
            # 复制配置文件
            shutil.copy2(self.config_path, backup_path)
            
            return str(backup_path)
            
        except Exception as e:
            raise TemplateError(f"配置文件备份失败: {e}")
    
    def restore_config(self, backup_path: str) -> bool:
        """从备份恢复配置文件
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否恢复成功
            
        Raises:
            TemplateError: 恢复失败
        """
        with self._lock:
            try:
                backup_file = Path(backup_path)
                
                # 检查备份文件是否存在
                if not backup_file.exists():
                    raise TemplateError(f"备份文件不存在: {backup_path}")
                
                # 验证备份文件格式
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise TemplateError(f"备份文件格式无效: {e}")
                
                # 创建当前配置的备份（以防恢复失败）
                safety_backup = self.backup_config()
                
                try:
                    # 恢复配置文件
                    shutil.copy2(str(backup_file), str(self.config_path))
                    return True
                    
                except Exception as e:
                    # 恢复失败，回滚到安全备份
                    shutil.copy2(str(safety_backup), str(self.config_path))
                    raise TemplateError(f"配置文件恢复失败，已回滚: {e}")
                
            except TemplateError:
                raise
            except Exception as e:
                raise TemplateError(f"配置文件恢复失败: {e}")
    
    def get_template_config(
        self,
        template_id: str,
        category: str
    ) -> Optional[Dict[str, Any]]:
        """获取模板配置
        
        Args:
            template_id: 模板ID
            category: 模板分类
            
        Returns:
            模板配置字典，如果不存在返回 None
        """
        with self._lock:
            try:
                full_config = self._load_config()
                
                if ('templates' in full_config and
                    category in full_config['templates'] and
                    template_id in full_config['templates'][category]):
                    return full_config['templates'][category][template_id]
                
                return None
                
            except Exception:
                return None
    
    def list_backups(self) -> list[str]:
        """列出所有备份文件
        
        Returns:
            备份文件路径列表（按时间倒序）
        """
        try:
            backups = list(self.backup_dir.glob("templates_*.yaml"))
            # 按修改时间倒序排序
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return [str(b) for b in backups]
        except Exception:
            return []
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """清理旧的备份文件
        
        Args:
            keep_count: 保留的备份数量
            
        Returns:
            删除的备份文件数量
        """
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return 0
            
            # 删除多余的备份
            deleted_count = 0
            for backup_path in backups[keep_count:]:
                try:
                    Path(backup_path).unlink()
                    deleted_count += 1
                except Exception:
                    pass
            
            return deleted_count
            
        except Exception:
            return 0
    
    def move_template_config(
        self,
        template_id: str,
        from_category: str,
        to_category: str,
        config: Dict[str, Any]
    ) -> bool:
        """移动模板配置到另一个分类
        
        这是一个原子操作，要么全部成功，要么全部失败。
        
        Args:
            template_id: 模板ID
            from_category: 源分类
            to_category: 目标分类
            config: 模板配置字典
            
        Returns:
            是否移动成功
            
        Raises:
            TemplateNotFoundError: 源模板不存在
            TemplateConflictError: 目标位置已存在
            TemplateError: 移动失败
        """
        with self._lock:
            try:
                # 加载当前配置
                full_config = self._load_config()
                
                # 检查源模板是否存在
                if ('templates' not in full_config or
                    from_category not in full_config['templates'] or
                    template_id not in full_config['templates'][from_category]):
                    raise TemplateNotFoundError(
                        f"模板 '{template_id}' 在分类 '{from_category}' 中不存在"
                    )
                
                # 确保目标分类存在
                if to_category not in full_config['templates']:
                    full_config['templates'][to_category] = {}
                
                # 检查目标位置是否已存在
                if template_id in full_config['templates'][to_category]:
                    raise TemplateConflictError(
                        f"模板 '{template_id}' 在目标分类 '{to_category}' 中已存在"
                    )
                
                # 移动配置：先添加到目标，再从源删除
                full_config['templates'][to_category][template_id] = config
                del full_config['templates'][from_category][template_id]
                
                # 保存配置
                self._save_config(full_config)
                
                return True
                
            except (TemplateNotFoundError, TemplateConflictError, TemplateError):
                raise
            except Exception as e:
                raise TemplateError(f"移动模板配置失败: {e}")
