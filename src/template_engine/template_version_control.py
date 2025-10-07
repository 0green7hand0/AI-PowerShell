"""
模板版本控制模块

提供模板的版本管理功能，包括版本创建、列表、恢复和清理。
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from .exceptions import TemplateError, TemplateNotFoundError


@dataclass
class TemplateVersion:
    """模板版本信息"""
    template_id: str
    version_number: int
    timestamp: datetime
    content: str
    config: Dict[str, Any]
    change_description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateVersion':
        """从字典创建"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class TemplateVersionControl:
    """模板版本控制器"""
    
    def __init__(self, history_dir: str = "templates/.history", max_versions: int = 10):
        """
        初始化版本控制器
        
        Args:
            history_dir: 历史版本存储目录
            max_versions: 每个模板保留的最大版本数
        """
        self.history_dir = Path(history_dir)
        self.max_versions = max_versions
        self._ensure_history_dir()
    
    def _ensure_history_dir(self) -> None:
        """确保历史目录存在"""
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_template_history_dir(self, template_id: str) -> Path:
        """获取模板的历史目录"""
        template_dir = self.history_dir / template_id
        template_dir.mkdir(parents=True, exist_ok=True)
        return template_dir
    
    def _get_next_version_number(self, template_id: str) -> int:
        """获取下一个版本号"""
        versions = self.list_versions(template_id)
        if not versions:
            return 1
        return max(v.version_number for v in versions) + 1
    
    def _get_version_filename(self, version_number: int, timestamp: datetime) -> str:
        """生成版本文件名"""
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"v{version_number}_{timestamp_str}.json"
    
    def create_version(
        self,
        template_id: str,
        content: str,
        config: Dict[str, Any],
        change_description: str = ""
    ) -> TemplateVersion:
        """
        创建新版本
        
        Args:
            template_id: 模板ID
            content: 模板内容
            config: 模板配置
            change_description: 变更描述
            
        Returns:
            创建的版本对象
            
        Raises:
            TemplateError: 创建版本失败
        """
        try:
            template_dir = self._get_template_history_dir(template_id)
            version_number = self._get_next_version_number(template_id)
            timestamp = datetime.now()
            
            # 创建版本对象
            version = TemplateVersion(
                template_id=template_id,
                version_number=version_number,
                timestamp=timestamp,
                content=content,
                config=config,
                change_description=change_description
            )
            
            # 保存版本文件
            version_file = template_dir / self._get_version_filename(version_number, timestamp)
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version.to_dict(), f, ensure_ascii=False, indent=2)
            
            # 清理旧版本
            self.cleanup_old_versions(template_id)
            
            return version
            
        except Exception as e:
            raise TemplateError(f"创建版本失败: {str(e)}")
    
    def list_versions(self, template_id: str) -> List[TemplateVersion]:
        """
        列出模板的所有历史版本
        
        Args:
            template_id: 模板ID
            
        Returns:
            版本列表，按版本号降序排列
        """
        template_dir = self._get_template_history_dir(template_id)
        versions = []
        
        # 读取所有版本文件
        for version_file in template_dir.glob("v*.json"):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = TemplateVersion.from_dict(data)
                    versions.append(version)
            except Exception as e:
                # 跳过损坏的版本文件
                print(f"警告: 无法读取版本文件 {version_file}: {str(e)}")
                continue
        
        # 按版本号降序排列
        versions.sort(key=lambda v: v.version_number, reverse=True)
        return versions
    
    def get_version(self, template_id: str, version_number: int) -> Optional[TemplateVersion]:
        """
        获取特定版本的内容
        
        Args:
            template_id: 模板ID
            version_number: 版本号
            
        Returns:
            版本对象，如果不存在则返回None
        """
        versions = self.list_versions(template_id)
        for version in versions:
            if version.version_number == version_number:
                return version
        return None
    
    def restore_version(
        self,
        template_id: str,
        version_number: int,
        target_file: str,
        config_updater: Optional[Any] = None
    ) -> TemplateVersion:
        """
        恢复到指定版本
        
        Args:
            template_id: 模板ID
            version_number: 要恢复的版本号
            target_file: 目标模板文件路径
            config_updater: 配置更新器（可选，用于更新配置文件）
            
        Returns:
            恢复的版本对象
            
        Raises:
            TemplateNotFoundError: 版本不存在
            TemplateError: 恢复失败
        """
        # 获取指定版本
        version = self.get_version(template_id, version_number)
        if not version:
            raise TemplateNotFoundError(
                f"版本不存在: {template_id} v{version_number}"
            )
        
        try:
            # 在恢复前创建当前版本的备份
            if os.path.exists(target_file):
                with open(target_file, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                # 如果有配置更新器，获取当前配置
                current_config = {}
                if config_updater:
                    try:
                        current_config = config_updater.get_template_config(template_id)
                    except:
                        pass
                
                # 创建当前版本的备份
                self.create_version(
                    template_id=template_id,
                    content=current_content,
                    config=current_config,
                    change_description=f"恢复前的自动备份 (恢复到 v{version_number})"
                )
            
            # 恢复模板文件
            target_path = Path(target_file)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(version.content)
            
            # 如果提供了配置更新器，更新配置
            if config_updater:
                config_updater.update_template_config(template_id, version.config)
            
            return version
            
        except Exception as e:
            raise TemplateError(f"恢复版本失败: {str(e)}")
    
    def cleanup_old_versions(self, template_id: str) -> int:
        """
        删除超过限制的旧版本
        
        Args:
            template_id: 模板ID
            
        Returns:
            删除的版本数量
        """
        versions = self.list_versions(template_id)
        
        if len(versions) <= self.max_versions:
            return 0
        
        # 保留最新的 max_versions 个版本，删除其余的
        versions_to_delete = versions[self.max_versions:]
        deleted_count = 0
        
        template_dir = self._get_template_history_dir(template_id)
        
        for version in versions_to_delete:
            # 查找并删除对应的文件
            for version_file in template_dir.glob(f"v{version.version_number}_*.json"):
                try:
                    version_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"警告: 无法删除版本文件 {version_file}: {str(e)}")
        
        return deleted_count
    
    def delete_all_versions(self, template_id: str) -> bool:
        """
        删除模板的所有历史版本
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否成功删除
        """
        try:
            template_dir = self._get_template_history_dir(template_id)
            if template_dir.exists():
                shutil.rmtree(template_dir)
            return True
        except Exception as e:
            print(f"警告: 无法删除历史目录 {template_dir}: {str(e)}")
            return False
    
    def get_version_diff(
        self,
        template_id: str,
        version1: int,
        version2: int
    ) -> Optional[Dict[str, Any]]:
        """
        比较两个版本的差异
        
        Args:
            template_id: 模板ID
            version1: 第一个版本号
            version2: 第二个版本号
            
        Returns:
            差异信息字典，如果版本不存在则返回None
        """
        v1 = self.get_version(template_id, version1)
        v2 = self.get_version(template_id, version2)
        
        if not v1 or not v2:
            return None
        
        return {
            'version1': version1,
            'version2': version2,
            'content_changed': v1.content != v2.content,
            'config_changed': v1.config != v2.config,
            'timestamp1': v1.timestamp.isoformat(),
            'timestamp2': v2.timestamp.isoformat(),
            'description1': v1.change_description,
            'description2': v2.change_description
        }
