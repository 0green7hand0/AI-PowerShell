"""
File analyzer module for project cleanup.
Scans and classifies files in the project.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set
import os
import re


@dataclass
class FileAnalysisResult:
    """文件分析结果数据结构"""
    file_path: str
    file_type: str  # 'doc', 'config', 'script', 'temp'
    is_used: bool
    references: List[str] = field(default_factory=list)  # 引用此文件的其他文件
    referenced_by: List[str] = field(default_factory=list)  # 此文件引用的其他文件
    risk_level: str = 'safe'  # 'safe', 'low', 'medium', 'high'
    recommendation: str = 'review'  # 'keep', 'delete', 'merge', 'review'
    reason: str = ''


class FileAnalyzer:
    """文件分析器 - 扫描和分类项目文件"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analysis_results: Dict[str, FileAnalysisResult] = {}
        
        # 文件类型分类规则
        self.doc_extensions = {'.md', '.txt', '.rst'}
        self.config_extensions = {'.yaml', '.yml', '.json', '.toml', '.ini', '.env', '.conf'}
        self.script_extensions = {'.sh', '.ps1', '.bat', '.cmd'}
        self.temp_patterns = {'__pycache__', '.pytest_cache', 'node_modules', '.cache', '.history', '.backups'}
        
        # 需要排除的目录
        self.exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv', '.venv'}
    
    def classify_file_type(self, file_path: Path) -> str:
        """分类文件类型"""
        # 检查是否是临时文件或目录
        for pattern in self.temp_patterns:
            if pattern in str(file_path):
                return 'temp'
        
        # 根据扩展名分类
        suffix = file_path.suffix.lower()
        if suffix in self.doc_extensions:
            return 'doc'
        elif suffix in self.config_extensions:
            return 'config'
        elif suffix in self.script_extensions:
            return 'script'
        elif file_path.name in {'.gitignore', '.dockerignore', 'Dockerfile', 'Makefile'}:
            return 'config'
        
        return 'other'
    
    def scan_directory(self, directory: Path = None) -> List[FileAnalysisResult]:
        """扫描目录中的所有文件"""
        if directory is None:
            directory = self.project_root
        
        results = []
        
        try:
            for item in directory.rglob('*'):
                # 跳过排除的目录
                if any(excluded in item.parts for excluded in self.exclude_dirs):
                    continue
                
                # 只处理文件
                if item.is_file():
                    relative_path = str(item.relative_to(self.project_root))
                    file_type = self.classify_file_type(item)
                    
                    result = FileAnalysisResult(
                        file_path=relative_path,
                        file_type=file_type,
                        is_used=True,  # 默认假设使用，后续分析会更新
                        reason=f'Classified as {file_type}'
                    )
                    
                    results.append(result)
                    self.analysis_results[relative_path] = result
        
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return results
    
    def get_files_by_type(self, file_type: str) -> List[FileAnalysisResult]:
        """获取指定类型的所有文件"""
        return [result for result in self.analysis_results.values() 
                if result.file_type == file_type]
    
    def get_documentation_files(self) -> List[FileAnalysisResult]:
        """获取所有文档文件"""
        return self.get_files_by_type('doc')
    
    def get_config_files(self) -> List[FileAnalysisResult]:
        """获取所有配置文件"""
        return self.get_files_by_type('config')
    
    def get_script_files(self) -> List[FileAnalysisResult]:
        """获取所有脚本文件"""
        return self.get_files_by_type('script')
    
    def get_temp_files(self) -> List[FileAnalysisResult]:
        """获取所有临时文件"""
        return self.get_files_by_type('temp')
    
    def generate_summary(self) -> Dict[str, int]:
        """生成文件统计摘要"""
        summary = {
            'total': len(self.analysis_results),
            'doc': len(self.get_documentation_files()),
            'config': len(self.get_config_files()),
            'script': len(self.get_script_files()),
            'temp': len(self.get_temp_files()),
            'other': len(self.get_files_by_type('other'))
        }
        return summary
