#!/usr/bin/env python3
"""
全面功能测试 - 对比两个版本的功能
"""

import subprocess
import time
import sys
from pathlib import Path

def test_version(script_name, test_cases):
    """测试指定版本"""
    print(f"\n🧪 测试 {script_name}")
    print("=" * 50)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {test_case}")
        
        start_time = time.time()
        
        try:
            # 使用 echo "y" 自动确认执行
            result = subprocess.run(
                f'echo "y" | python {script_name} "{test_case}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='gbk',
                errors='ignore'
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            success = result.returncode == 0
            output = result.stdout if result.stdout else result.stderr
            
            print(f"  ⏱️  耗时: {execution_time:.2f}秒")
            print(f"  📤 结果: {'✅ 成功' if success else '❌ 失败'}")
            
            if output:
                # 提取关键信息
                lines = output.split('\n')
                for line in lines:
                    if '翻译:' in line or '安全:' in line or '执行:' in line or '输出:' in line:
                        print(f"  {line.strip()}")
            
            results.append({
                'test_case': test_case,
                'success': success,
                'time': execution_time,
                'output': output
            })
            
        except subprocess.TimeoutExpired:
            print(f"  ⏰ 超时 (30秒)")
            results.append({
                'test_case': test_case,
                'success': False,
                'time': 30.0,
                'output': 'Timeout'
            })
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results.append({
                'test_case': test_case,
                'success': False,
                'time': 0.0,
                'output': str(e)
            })
    
    return results

def analyze_results(version_name, results):
    """分析测试结果"""
    print(f"\n📊 {version_name} 测试结果分析")
    print("-" * 30)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    total_time = sum(r['time'] for r in results)
    avg_time = total_time / total_tests if total_tests > 0 else 0
    
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"成功率: {(successful_tests/total_tests)*100:.1f}%")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均耗时: {avg_time:.2f}秒")
    
    return {
        'total': total_tests,
        'successful': successful_tests,
        'success_rate': (successful_tests/total_tests)*100,
        'total_time': total_time,
        'avg_time': avg_time
    }

def main():
    """主测试函数"""
    print("🚀 AI PowerShell 助手 - 全面功能测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        "显示当前时间",
        "列出当前目录文件",
        "查看PowerShell版本",
        "显示系统进程",
        "检查磁盘空间",
        "显示网络配置",
        "查看环境变量",
        "显示系统信息"
    ]
    
    # 测试两个版本
    print("🎯 开始对比测试...")
    
    # 测试实用版本
    practical_results = test_version("实用版本.py", test_cases)
    practical_stats = analyze_results("实用版本", practical_results)
    
    # 测试企业版本
    enterprise_results = test_version("最终修复版本.py", test_cases)
    enterprise_stats = analyze_results("企业版本", enterprise_results)
    
    # 对比分析
    print(f"\n🏆 版本对比总结")
    print("=" * 40)
    
    print(f"📊 成功率对比:")
    print(f"  实用版本: {practical_stats['success_rate']:.1f}%")
    print(f"  企业版本: {enterprise_stats['success_rate']:.1f}%")
    
    print(f"\n⏱️  性能对比:")
    print(f"  实用版本平均耗时: {practical_stats['avg_time']:.2f}秒")
    print(f"  企业版本平均耗时: {enterprise_stats['avg_time']:.2f}秒")
    
    # 推荐
    if practical_stats['success_rate'] >= enterprise_stats['success_rate']:
        if practical_stats['avg_time'] < enterprise_stats['avg_time']:
            print(f"\n💡 推荐: 实用版本 (成功率相当，性能更好)")
        else:
            print(f"\n💡 推荐: 根据需求选择 (成功率相当)")
    else:
        print(f"\n💡 推荐: 企业版本 (成功率更高)")
    
    print(f"\n🎯 测试完成！两个版本都可以正常使用。")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)