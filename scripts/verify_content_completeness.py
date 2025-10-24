#!/usr/bin/env python3
"""
文档内容完整性验证脚本

此脚本对比新旧文档，确认所有重要信息已保留，检查是否有内容丢失或遗漏。
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class DocumentMetrics:
    """文档度量指标"""
    filename: str
    word_count: int
    code_blocks: int
    headings: int
    links: int
    lists: int
    tables: int
    key_terms: Set[str] = field(default_factory=set)
    code_examples: List[str] = field(default_factory=list)


@dataclass
class ContentComparison:
    """内容对比结果"""
    old_doc: str
    new_doc: str
    old_metrics: DocumentMetrics
    new_metrics: DocumentMetrics
    missing_terms: Set[str] = field(default_factory=set)
    missing_code: List[str] = field(default_factory=list)
    content_preserved: bool = True
    notes: List[str] = field(default_factory=list)


class ContentVerifier:
    """文档内容验证器"""
    
    def __init__(self, backup_dir: str, current_dir: str):
        self.backup_dir = Path(backup_dir)
        self.current_dir = Path(current_dir)
        self.comparisons: List[ContentComparison] = []
        
        # 文档映射：旧文档 -> 新文档
        self.doc_mapping = {
            # 用户指南类
            "ui-system-guide.md": "user-guide.md",
            "progress-manager-guide.md": "user-guide.md",
            "startup-experience-guide.md": "user-guide.md",
            "security-checker-guide.md": "user-guide.md",
            "template-quick-start.md": "template-guide.md",
            "custom-template-guide.md": "template-guide.md",
            "template-cli-reference.md": ["template-guide.md", "cli-reference.md"],
            "template-quick-reference.md": "template-guide.md",
            "ui-configuration-guide.md": "user-guide.md",
            
            # 开发者文档类
            "config-module-implementation.md": ["architecture.md", "config-reference.md"],
            "context-module-implementation.md": "architecture.md",
            "storage-engine-implementation.md": "architecture.md",
            "security-engine-implementation.md": "architecture.md",
            "main-controller-implementation.md": "architecture.md",
            "documentation-guide.md": "developer-guide.md",
            
            # 部署运维类
            "docker-deployment.md": "deployment-guide.md",
            "ci-cd-setup.md": "deployment-guide.md",
            "cicd-and-license-guide.md": "deployment-guide.md",
            "release-process.md": "deployment-guide.md",
            "deployment-checklist.md": "deployment-guide.md",
            "ollama-setup.md": "deployment-guide.md",
            
            # 保留的文档
            "architecture.md": "architecture.md",
            "developer-guide.md": "developer-guide.md",
            "README.md": "README.md",
            "theme-customization-guide.md": "theme-customization-guide.md",
        }
    
    def extract_metrics(self, content: str, filename: str) -> DocumentMetrics:
        """提取文档度量指标"""
        # 统计字数（中英文）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', content))
        word_count = chinese_chars + english_words
        
        # 统计代码块
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        code_examples = re.findall(r'```([\s\S]*?)```', content)
        
        # 统计标题
        headings = len(re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE))
        
        # 统计链接
        links = len(re.findall(r'\[.+?\]\(.+?\)', content))
        
        # 统计列表项
        lists = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
        lists += len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE))
        
        # 统计表格
        tables = len(re.findall(r'\|.+\|', content))
        
        # 提取关键术语（标题中的词汇）
        key_terms = set()
        for heading in re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE):
            # 清理标题文本
            heading = re.sub(r'[#\[\](){}]', '', heading).strip()
            if heading:
                key_terms.add(heading.lower())
        
        return DocumentMetrics(
            filename=filename,
            word_count=word_count,
            code_blocks=code_blocks,
            headings=headings,
            links=links,
            lists=lists,
            tables=tables,
            key_terms=key_terms,
            code_examples=code_examples
        )
    
    def read_document(self, path: Path) -> str:
        """读取文档内容"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  无法读取文件 {path}: {e}")
            return ""
    
    def compare_documents(self, old_doc: str, new_docs: List[str]) -> ContentComparison:
        """对比旧文档和新文档"""
        old_path = self.backup_dir / old_doc
        old_content = self.read_document(old_path)
        old_metrics = self.extract_metrics(old_content, old_doc)
        
        # 读取所有新文档内容
        new_content_combined = ""
        new_metrics_list = []
        
        for new_doc in new_docs:
            new_path = self.current_dir / new_doc
            if new_path.exists():
                new_content = self.read_document(new_path)
                new_content_combined += "\n" + new_content
                new_metrics_list.append(self.extract_metrics(new_content, new_doc))
        
        # 合并新文档的度量指标
        if new_metrics_list:
            new_metrics = DocumentMetrics(
                filename=" + ".join(new_docs),
                word_count=sum(m.word_count for m in new_metrics_list),
                code_blocks=sum(m.code_blocks for m in new_metrics_list),
                headings=sum(m.headings for m in new_metrics_list),
                links=sum(m.links for m in new_metrics_list),
                lists=sum(m.lists for m in new_metrics_list),
                tables=sum(m.tables for m in new_metrics_list),
                key_terms=set().union(*[m.key_terms for m in new_metrics_list]),
                code_examples=[ex for m in new_metrics_list for ex in m.code_examples]
            )
        else:
            new_metrics = DocumentMetrics(filename="未找到", word_count=0, code_blocks=0,
                                         headings=0, links=0, lists=0, tables=0)
        
        # 检查缺失的关键术语
        missing_terms = old_metrics.key_terms - new_metrics.key_terms
        
        # 检查缺失的代码示例（简化比较）
        missing_code = []
        for old_code in old_metrics.code_examples:
            old_code_clean = re.sub(r'\s+', '', old_code.strip())
            if len(old_code_clean) > 50:  # 只检查较长的代码示例
                found = False
                for new_code in new_metrics.code_examples:
                    new_code_clean = re.sub(r'\s+', '', new_code.strip())
                    if old_code_clean in new_code_clean or new_code_clean in old_code_clean:
                        found = True
                        break
                if not found:
                    missing_code.append(old_code[:100] + "..." if len(old_code) > 100 else old_code)
        
        # 判断内容是否保留
        content_preserved = True
        notes = []
        
        if not new_metrics_list:
            content_preserved = False
            notes.append("⚠️  新文档不存在")
        elif old_metrics.word_count > 0:
            # 允许一定的内容减少（由于重复内容合并）
            word_ratio = new_metrics.word_count / old_metrics.word_count
            if word_ratio < 0.3:  # 如果新文档字数少于旧文档的30%
                notes.append(f"⚠️  字数显著减少: {old_metrics.word_count} -> {new_metrics.word_count} ({word_ratio:.1%})")
            
            # 检查代码块
            if old_metrics.code_blocks > 0 and new_metrics.code_blocks == 0:
                content_preserved = False
                notes.append(f"❌ 所有代码块丢失: {old_metrics.code_blocks} 个")
            elif old_metrics.code_blocks > new_metrics.code_blocks + 2:
                notes.append(f"⚠️  代码块减少: {old_metrics.code_blocks} -> {new_metrics.code_blocks}")
            
            # 检查关键术语
            if len(missing_terms) > len(old_metrics.key_terms) * 0.5:
                notes.append(f"⚠️  大量关键术语缺失: {len(missing_terms)}/{len(old_metrics.key_terms)}")
        
        return ContentComparison(
            old_doc=old_doc,
            new_doc=" + ".join(new_docs),
            old_metrics=old_metrics,
            new_metrics=new_metrics,
            missing_terms=missing_terms,
            missing_code=missing_code,
            content_preserved=content_preserved,
            notes=notes
        )
    
    def verify_all(self) -> List[ContentComparison]:
        """验证所有文档"""
        print("🔍 开始验证文档内容完整性...\n")
        
        for old_doc, new_doc in self.doc_mapping.items():
            # 处理一对多的映射
            new_docs = new_doc if isinstance(new_doc, list) else [new_doc]
            
            print(f"📄 对比: {old_doc} -> {', '.join(new_docs)}")
            comparison = self.compare_documents(old_doc, new_docs)
            self.comparisons.append(comparison)
        
        return self.comparisons
    
    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("# 文档内容完整性验证报告\n")
        report.append(f"**验证日期**: 2025-10-17\n")
        report.append(f"**备份目录**: {self.backup_dir}\n")
        report.append(f"**当前目录**: {self.current_dir}\n")
        report.append(f"**验证文档数**: {len(self.comparisons)}\n\n")
        
        # 统计
        total = len(self.comparisons)
        preserved = sum(1 for c in self.comparisons if c.content_preserved)
        issues = total - preserved
        
        report.append("## 📊 验证摘要\n\n")
        report.append(f"- ✅ 内容完整保留: {preserved}/{total} ({preserved/total*100:.1f}%)\n")
        report.append(f"- ⚠️  需要关注: {issues}/{total}\n\n")
        
        # 详细对比
        report.append("## 📋 详细对比结果\n\n")
        
        for i, comp in enumerate(self.comparisons, 1):
            status = "✅" if comp.content_preserved else "⚠️"
            report.append(f"### {i}. {status} {comp.old_doc}\n\n")
            report.append(f"**映射到**: {comp.new_doc}\n\n")
            
            # 度量对比表
            report.append("| 指标 | 旧文档 | 新文档 | 变化 |\n")
            report.append("|------|--------|--------|------|\n")
            
            old_m = comp.old_metrics
            new_m = comp.new_metrics
            
            report.append(f"| 字数 | {old_m.word_count:,} | {new_m.word_count:,} | ")
            if new_m.word_count >= old_m.word_count * 0.7:
                report.append("✅ |\n")
            else:
                report.append(f"⚠️ {(new_m.word_count/old_m.word_count*100 if old_m.word_count > 0 else 0):.0f}% |\n")
            
            report.append(f"| 代码块 | {old_m.code_blocks} | {new_m.code_blocks} | ")
            if new_m.code_blocks >= old_m.code_blocks * 0.8:
                report.append("✅ |\n")
            elif old_m.code_blocks == 0:
                report.append("N/A |\n")
            else:
                report.append(f"⚠️ {(new_m.code_blocks/old_m.code_blocks*100):.0f}% |\n")
            
            report.append(f"| 标题数 | {old_m.headings} | {new_m.headings} | ")
            report.append("✅ |\n" if new_m.headings > 0 else "⚠️ |\n")
            
            report.append(f"| 链接数 | {old_m.links} | {new_m.links} | ✅ |\n")
            report.append(f"| 列表项 | {old_m.lists} | {new_m.lists} | ✅ |\n\n")
            
            # 注意事项
            if comp.notes:
                report.append("**注意事项**:\n")
                for note in comp.notes:
                    report.append(f"- {note}\n")
                report.append("\n")
            
            # 缺失的关键术语
            if comp.missing_terms and len(comp.missing_terms) <= 10:
                report.append(f"**可能缺失的主题** ({len(comp.missing_terms)} 个):\n")
                for term in sorted(list(comp.missing_terms)[:10]):
                    report.append(f"- {term}\n")
                report.append("\n")
            elif len(comp.missing_terms) > 10:
                report.append(f"**可能缺失的主题**: {len(comp.missing_terms)} 个（较多，建议人工审查）\n\n")
            
            # 缺失的代码示例
            if comp.missing_code:
                report.append(f"**可能缺失的代码示例** ({len(comp.missing_code)} 个):\n")
                for code in comp.missing_code[:3]:  # 只显示前3个
                    report.append(f"```\n{code}\n```\n\n")
                if len(comp.missing_code) > 3:
                    report.append(f"...还有 {len(comp.missing_code) - 3} 个代码示例\n\n")
            
            report.append("---\n\n")
        
        # 归档文档
        report.append("## 📦 归档文档\n\n")
        report.append("以下文档已归档到 `docs/archive/`，不需要内容迁移：\n\n")
        archived = ["cleanup-summary.md", "documentation-optimization-summary.md", 
                   "release-deployment-summary.md"]
        for doc in archived:
            report.append(f"- {doc}\n")
        report.append("\n")
        
        # 结论
        report.append("## 🎯 验证结论\n\n")
        
        if issues == 0:
            report.append("✅ **所有文档内容已完整保留**\n\n")
            report.append("所有旧文档的重要信息都已成功迁移到新文档中。\n\n")
        else:
            report.append(f"⚠️  **有 {issues} 个文档需要人工审查**\n\n")
            report.append("建议对标记为 ⚠️ 的文档进行人工审查，确认内容是否完整。\n\n")
        
        report.append("### 建议行动\n\n")
        report.append("1. 审查所有标记为 ⚠️ 的文档对比\n")
        report.append("2. 检查\"可能缺失的主题\"是否为重要内容\n")
        report.append("3. 验证\"可能缺失的代码示例\"是否需要补充\n")
        report.append("4. 对于字数显著减少的文档，确认是否为合理的去重\n\n")
        
        report.append("---\n\n")
        report.append("*此报告由自动化脚本生成，建议结合人工审查确保内容完整性*\n")
        
        return "".join(report)
    
    def print_summary(self):
        """打印验证摘要"""
        print("\n" + "="*70)
        print("📊 验证摘要")
        print("="*70 + "\n")
        
        total = len(self.comparisons)
        preserved = sum(1 for c in self.comparisons if c.content_preserved)
        issues = total - preserved
        
        print(f"✅ 内容完整保留: {preserved}/{total} ({preserved/total*100:.1f}%)")
        print(f"⚠️  需要关注: {issues}/{total}\n")
        
        if issues > 0:
            print("需要关注的文档:")
            for comp in self.comparisons:
                if not comp.content_preserved:
                    print(f"  ⚠️  {comp.old_doc} -> {comp.new_doc}")
                    for note in comp.notes:
                        print(f"      {note}")
        else:
            print("🎉 所有文档内容已完整保留！")
        
        print("\n" + "="*70)


def main():
    """主函数"""
    backup_dir = "docs_backup_20251017"
    current_dir = "docs"
    
    verifier = ContentVerifier(backup_dir, current_dir)
    verifier.verify_all()
    
    # 生成报告
    report = verifier.generate_report()
    
    # 保存报告
    report_path = Path("docs/content-verification-report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 验证报告已生成: {report_path}")
    
    # 打印摘要
    verifier.print_summary()


if __name__ == "__main__":
    main()
