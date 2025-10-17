"""
Example script demonstrating file analyzer usage.
Run this to analyze the current project.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cleanup.file_analyzer import FileAnalyzer


def main():
    """Demonstrate file analyzer functionality"""
    print("=== AI-PowerShell Project File Analysis ===\n")
    
    # Initialize analyzer with project root
    project_root = Path(__file__).parent.parent
    analyzer = FileAnalyzer(str(project_root))
    
    # Scan all files
    print("Scanning project files...")
    results = analyzer.scan_directory()
    print(f"✓ Found {len(results)} files\n")
    
    # Generate summary
    summary = analyzer.generate_summary()
    print("=== Summary Statistics ===")
    print(f"Total files:          {summary['total']}")
    print(f"Documentation files:  {summary['doc']}")
    print(f"Configuration files:  {summary['config']}")
    print(f"Script files:         {summary['script']}")
    print(f"Temporary files:      {summary['temp']}")
    print(f"Other files:          {summary['other']}")
    print()
    
    # Show documentation files
    doc_files = analyzer.get_documentation_files()
    print(f"=== Documentation Files ({len(doc_files)}) ===")
    for doc in doc_files[:10]:
        print(f"  • {doc.file_path}")
    if len(doc_files) > 10:
        print(f"  ... and {len(doc_files) - 10} more")
    print()
    
    # Show configuration files
    config_files = analyzer.get_config_files()
    print(f"=== Configuration Files ({len(config_files)}) ===")
    for cfg in config_files[:10]:
        print(f"  • {cfg.file_path}")
    if len(config_files) > 10:
        print(f"  ... and {len(config_files) - 10} more")
    print()
    
    # Show script files
    script_files = analyzer.get_script_files()
    print(f"=== Script Files ({len(script_files)}) ===")
    for script in script_files:
        print(f"  • {script.file_path}")
    print()
    
    # Show temporary files
    temp_files = analyzer.get_temp_files()
    if temp_files:
        print(f"=== Temporary Files ({len(temp_files)}) ===")
        for temp in temp_files[:10]:
            print(f"  • {temp.file_path}")
        if len(temp_files) > 10:
            print(f"  ... and {len(temp_files) - 10} more")
        print()
    
    print("✓ Analysis complete!")
    print("\nNext steps:")
    print("  1. Review the file lists above")
    print("  2. Run task 2 to check file references")
    print("  3. Run task 3 to analyze web-ui documentation")


if __name__ == '__main__':
    main()
