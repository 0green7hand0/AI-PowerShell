#!/usr/bin/env python3
"""
Documentation Link Verification Script
Checks all markdown links in the documentation for validity
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict


class LinkVerifier:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.broken_links = []
        self.checked_files = []
        
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the project"""
        md_files = []
        
        # Root level markdown files
        for file in self.root_dir.glob("*.md"):
            md_files.append(file)
        
        # docs directory
        docs_dir = self.root_dir / "docs"
        if docs_dir.exists():
            for file in docs_dir.rglob("*.md"):
                md_files.append(file)
        
        return md_files
    
    def extract_links(self, content: str, file_path: Path) -> List[Tuple[str, int]]:
        """Extract all markdown links from content"""
        links = []
        
        # Pattern for markdown links: [text](url)
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                link_url = match.group(2)
                # Skip external URLs, anchors, and mailto links
                if not link_url.startswith(('http://', 'https://', '#', 'mailto:')):
                    links.append((link_url, line_num))
        
        return links
    
    def resolve_link(self, link: str, source_file: Path) -> Path:
        """Resolve a relative link to an absolute path"""
        # Remove anchor if present
        link_path = link.split('#')[0]
        
        if not link_path:  # Pure anchor link
            return source_file
        
        # Resolve relative to source file's directory
        source_dir = source_file.parent
        target_path = (source_dir / link_path).resolve()
        
        return target_path
    
    def verify_file(self, file_path: Path) -> List[Dict]:
        """Verify all links in a single file"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            issues.append({
                'file': str(file_path),
                'line': 0,
                'link': '',
                'error': f'Failed to read file: {e}'
            })
            return issues
        
        links = self.extract_links(content, file_path)
        
        for link, line_num in links:
            target_path = self.resolve_link(link, file_path)
            
            if not target_path.exists():
                issues.append({
                    'file': str(file_path.relative_to(self.root_dir)),
                    'line': line_num,
                    'link': link,
                    'resolved': str(target_path.relative_to(self.root_dir)) if target_path.is_relative_to(self.root_dir) else str(target_path),
                    'error': 'File not found'
                })
        
        return issues
    
    def verify_all(self) -> Dict:
        """Verify all markdown files"""
        md_files = self.find_markdown_files()
        all_issues = []
        
        print(f"🔍 Checking {len(md_files)} markdown files...\n")
        
        for file_path in md_files:
            self.checked_files.append(file_path)
            issues = self.verify_file(file_path)
            all_issues.extend(issues)
        
        return {
            'total_files': len(md_files),
            'files_with_issues': len(set(issue['file'] for issue in all_issues)),
            'total_issues': len(all_issues),
            'issues': all_issues
        }
    
    def print_report(self, results: Dict):
        """Print verification report"""
        print("=" * 80)
        print("📊 LINK VERIFICATION REPORT")
        print("=" * 80)
        print(f"\n✅ Files checked: {results['total_files']}")
        print(f"❌ Files with broken links: {results['files_with_issues']}")
        print(f"🔗 Total broken links: {results['total_issues']}")
        
        if results['total_issues'] == 0:
            print("\n🎉 All links are valid!")
            return
        
        print("\n" + "=" * 80)
        print("BROKEN LINKS DETAILS")
        print("=" * 80)
        
        # Group by file
        issues_by_file = defaultdict(list)
        for issue in results['issues']:
            issues_by_file[issue['file']].append(issue)
        
        for file_path, issues in sorted(issues_by_file.items()):
            print(f"\n📄 {file_path}")
            print("-" * 80)
            for issue in issues:
                print(f"  Line {issue['line']}: {issue['link']}")
                print(f"    → Resolved to: {issue['resolved']}")
                print(f"    → Error: {issue['error']}")
        
        print("\n" + "=" * 80)


def main():
    verifier = LinkVerifier()
    results = verifier.verify_all()
    verifier.print_report(results)
    
    # Exit with error code if there are broken links
    if results['total_issues'] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
