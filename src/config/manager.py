"""
配置管理器

负责加载、验证和管理应用配置
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import ValidationError

from .models import AppConfig


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
        """
        self.config_path = config_path
        self._config: Optional[AppConfig] = None
        self._default_config_paths = [
            "config/default.yaml",
            "config.yaml",
            os.path.expanduser("~/.ai-powershell/config.yaml"),
        ]
    
    def load_config(self, config_path: Optional[str] = None) -> AppConfig:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            AppConfig: 应用配置对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置验证失败
            yaml.YAMLError: YAML 解析失败
        """
        # 确定配置文件路径
        path = config_path or self.config_path
        
        if path:
            # 使用指定的配置文件
            config_data = self._load_yaml_file(path)
        else:
            # 尝试默认路径
            config_data = self._load_from_default_paths()
        
        # 验证并创建配置对象
        try:
            self._config = AppConfig(**config_data)
            return self._config
        except ValidationError as e:
            # 直接重新抛出原始的 ValidationError
            raise
    
    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """
        加载 YAML 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 配置数据字典
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 解析失败: {e}")
    
    def _load_from_default_paths(self) -> Dict[str, Any]:
        """
        从默认路径加载配置
        
        Returns:
            Dict: 配置数据字典
        """
        for path in self._default_config_paths:
            try:
                return self._load_yaml_file(path)
            except FileNotFoundError:
                continue
        
        # 如果所有默认路径都不存在，返回空字典（使用默认配置）
        return {}
    
    def get_config(self) -> AppConfig:
        """
        获取当前配置
        
        Returns:
            AppConfig: 应用配置对象
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def save_config(self, config: AppConfig, file_path: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            config: 应用配置对象
            file_path: 保存路径，如果为 None 则使用当前配置路径
        """
        path = file_path or self.config_path or self._default_config_paths[0]
        path_obj = Path(path)
        
        # 确保目录存在
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为字典
        config_dict = config.model_dump()
        
        # 保存为 YAML
        with open(path_obj, 'w', encoding='utf-8') as f:
            yaml.dump(
                config_dict,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
        
        self._config = config
        self.config_path = str(path_obj)
    
    def update_config(self, updates: Dict[str, Any]) -> AppConfig:
        """
        更新配置
        
        Args:
            updates: 要更新的配置项字典
            
        Returns:
            AppConfig: 更新后的配置对象
        """
        current_config = self.get_config()
        config_dict = current_config.model_dump()
        
        # 深度更新配置
        self._deep_update(config_dict, updates)
        
        # 验证并创建新配置
        self._config = AppConfig(**config_dict)
        return self._config
    
    def _deep_update(self, base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """
        深度更新字典
        
        Args:
            base: 基础字典
            updates: 更新字典
        """
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def reset_to_defaults(self) -> AppConfig:
        """
        重置为默认配置
        
        Returns:
            AppConfig: 默认配置对象
        """
        self._config = AppConfig()
        return self._config
    
    def validate_config(self, config_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证配置数据
        
        Args:
            config_data: 配置数据字典
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        try:
            AppConfig(**config_data)
            return True, None
        except ValidationError as e:
            return False, str(e)
    
    @staticmethod
    def create_default_config_file(file_path: str) -> None:
        """
        创建默认配置文件
        
        Args:
            file_path: 配置文件路径
        """
        default_config = AppConfig()
        manager = ConfigManager()
        manager.save_config(default_config, file_path)
