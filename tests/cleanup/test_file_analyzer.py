"""
Unit tests for file analyzer module.
"""
import pytest
from pathlib import Path
import tempfile
import os
from src.cleanup.file_analyzer import FileAnalyzer, FileAnalysisResult


class TestFileAnalysisResult:
    """测试 FileAnalysisResult 数据结构"""
    
    def test_create_file_analysis_result(self):
        """测试创建文件分析结果"""
        result = FileAnalysisResult(
            file_path='test.md',
            file_type='doc',
            is_used=True,
            reason='Test file'
        )
        
        assert result.file_path == 'test.md'
        assert result.file_type == 'doc'
        assert result.is_used is True
        assert result.references == []
        assert result.referenced_by == []
        assert result.risk_level == 'safe'
        assert result.recommendation == 'review'
        assert result.reason == 'Test file'
    
    def test_file_analysis_result_with_references(self):
        """测试带引用的文件分析结果"""
        result = FileAnalysisResult(
            file_path='test.md',
            file_type='doc',
            is_used=True,
            references=['file1.md', 'file2.md'],
            referenced_by=['main.md'],
            risk_level='low',
            recommendation='keep'
        )
        
        assert len(result.references) == 2
        assert len(result.referenced_by) == 1
        assert result.risk_level == 'low'
        assert result.recommendation == 'keep'


class TestFileAnalyzer:
    """测试 FileAnalyzer 类"""
    
    @pytest.fixture
    def temp_project(self):
        """创建临时项目目录用于测试"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # 创建测试文件结构
            (project_path / 'README.md').write_text('# Test Project')
            (project_path / 'config.yaml').write_text('key: value')
            (project_path / 'script.sh').write_text('#!/bin/bash\necho "test"')
            
            # 创建子目录
            docs_dir = project_path / 'docs'
            docs_dir.mkdir()
            (docs_dir / 'guide.md').write_text('# Guide')
            
            # 创建临时文件
            cache_dir = project_path / '__pycache__'
            cache_dir.mkdir()
            (cache_dir / 'test.pyc').write_text('compiled')
            
            yield project_path
    
    def test_file_analyzer_initialization(self, temp_project):
        """测试文件分析器初始化"""
        analyzer = FileAnalyzer(str(temp_project))
        
        assert analyzer.project_root == temp_project
        assert len(analyzer.analysis_results) == 0
        assert '.md' in analyzer.doc_extensions
        assert '.yaml' in analyzer.config_extensions
        assert '.sh' in analyzer.script_extensions
    
    def test_classify_file_type_doc(self, temp_project):
        """测试文档文件分类"""
        analyzer = FileAnalyzer(str(temp_project))
        
        assert analyzer.classify_file_type(Path('test.md')) == 'doc'
        assert analyzer.classify_file_type(Path('README.txt')) == 'doc'
        assert analyzer.classify_file_type(Path('guide.rst')) == 'doc'
    
    def test_classify_file_type_config(self, temp_project):
        """测试配置文件分类"""
        analyzer = FileAnalyzer(str(temp_project))
        
        assert analyzer.classify_file_type(Path('config.yaml')) == 'config'
        assert analyzer.classify_file_type(Path('settings.json')) == 'config'
        assert analyzer.classify_file_type(Path('.env')) == 'config'
        assert analyzer.classify_file_type(Path('Dockerfile')) == 'config'
        assert analyzer.classify_file_type(Path('Makefile')) == 'config'
    
    def test_classify_file_type_script(self, temp_project):
        """测试脚本文件分类"""
        analyzer = FileAnalyzer(str(temp_project))
        
        assert analyzer.classify_file_type(Path('install.sh')) == 'script'
        assert analyzer.classify_file_type(Path('build.ps1')) == 'script'
        assert analyzer.classify_file_type(Path('run.bat')) == 'script'
    
    def test_classify_file_type_temp(self, temp_project):
        """测试临时文件分类"""
        analyzer = FileAnalyzer(str(temp_project))
        
        assert analyzer.classify_file_type(Path('__pycache__/test.pyc')) == 'temp'
        assert analyzer.classify_file_type(Path('.pytest_cache/data')) == 'temp'
        assert analyzer.classify_file_type(Path('node_modules/package')) == 'temp'
    
    def test_scan_directory(self, temp_project):
        """测试目录扫描功能"""
        analyzer = FileAnalyzer(str(temp_project))
        results = analyzer.scan_directory()
        
        # 应该找到文件（排除 __pycache__）
        assert len(results) > 0
        
        # 验证文件路径是相对路径
        for result in results:
            assert not result.file_path.startswith('/')
            assert not result.file_path.startswith('\\')
    
    def test_get_files_by_type(self, temp_project):
        """测试按类型获取文件"""
        analyzer = FileAnalyzer(str(temp_project))
        analyzer.scan_directory()
        
        doc_files = analyzer.get_documentation_files()
        config_files = analyzer.get_config_files()
        script_files = analyzer.get_script_files()
        
        # 验证文档文件
        assert len(doc_files) >= 2  # README.md and docs/guide.md
        assert all(f.file_type == 'doc' for f in doc_files)
        
        # 验证配置文件
        assert len(config_files) >= 1  # config.yaml
        assert all(f.file_type == 'config' for f in config_files)
        
        # 验证脚本文件
        assert len(script_files) >= 1  # script.sh
        assert all(f.file_type == 'script' for f in script_files)
    
    def test_generate_summary(self, temp_project):
        """测试生成统计摘要"""
        analyzer = FileAnalyzer(str(temp_project))
        analyzer.scan_directory()
        
        summary = analyzer.generate_summary()
        
        assert 'total' in summary
        assert 'doc' in summary
        assert 'config' in summary
        assert 'script' in summary
        assert 'temp' in summary
        assert 'other' in summary
        
        # 验证总数等于各类型之和
        assert summary['total'] == (
            summary['doc'] + 
            summary['config'] + 
            summary['script'] + 
            summary['temp'] + 
            summary['other']
        )
        
        # 验证至少有一些文件
        assert summary['total'] > 0
        assert summary['doc'] >= 2
        assert summary['config'] >= 1
        assert summary['script'] >= 1
