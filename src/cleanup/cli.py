"""
CLI tool for file analysis.
"""
import argparse
import json
from pathlib import Path
from .file_analyzer import FileAnalyzer


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Analyze project files for cleanup'
    )
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for analysis results (JSON format)'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=['doc', 'config', 'script', 'temp', 'all'],
        default='all',
        help='Filter by file type'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary statistics only'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    print(f"Analyzing project at: {args.project_root}")
    analyzer = FileAnalyzer(args.project_root)
    
    # Scan directory
    print("Scanning files...")
    results = analyzer.scan_directory()
    print(f"Found {len(results)} files")
    
    # Show summary if requested
    if args.summary:
        summary = analyzer.generate_summary()
        print("\n=== File Analysis Summary ===")
        print(f"Total files: {summary['total']}")
        print(f"Documentation files: {summary['doc']}")
        print(f"Configuration files: {summary['config']}")
        print(f"Script files: {summary['script']}")
        print(f"Temporary files: {summary['temp']}")
        print(f"Other files: {summary['other']}")
        return
    
    # Filter by type if specified
    if args.type != 'all':
        results = analyzer.get_files_by_type(args.type)
        print(f"\nFiltered to {len(results)} {args.type} files")
    
    # Display results
    print("\n=== Analysis Results ===")
    for result in results[:20]:  # Show first 20
        print(f"\n{result.file_path}")
        print(f"  Type: {result.file_type}")
        print(f"  Recommendation: {result.recommendation}")
        print(f"  Reason: {result.reason}")
    
    if len(results) > 20:
        print(f"\n... and {len(results) - 20} more files")
    
    # Save to file if requested
    if args.output:
        output_data = {
            'summary': analyzer.generate_summary(),
            'files': [
                {
                    'path': r.file_path,
                    'type': r.file_type,
                    'is_used': r.is_used,
                    'risk_level': r.risk_level,
                    'recommendation': r.recommendation,
                    'reason': r.reason
                }
                for r in results
            ]
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {args.output}")


if __name__ == '__main__':
    main()
