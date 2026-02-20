"""
测试运行脚本

运行所有测试用例并收集测试数据，为生成测试报告做准备。
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_results = {}
        self.test_directory = Path("tests/integration")
        self.output_directory = Path("test_results")
        self.output_directory.mkdir(exist_ok=True)
    
    def run_test(self, test_file: str) -> Dict[str, Any]:
        """运行单个测试文件"""
        print(f"\n运行测试: {test_file}")
        print("=" * 60)
        
        start_time = time.time()
        
        # 构建测试命令
        test_path = self.test_directory / test_file
        output_file = Path("test_output.txt")
        
        # 使用文件重定向来捕获完整的测试输出
        command = f"{sys.executable} -m pytest {test_path} -v -s --no-cov > {output_file} 2>&1"
        
        # 执行测试
        result = subprocess.run(
            command,
            shell=True,
            cwd=Path.cwd()
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 读取完整的测试输出
        if output_file.exists():
            with open(output_file, "r", encoding="utf-8", errors="replace") as f:
                output = f.read()
            output_file.unlink()  # 删除临时文件
        else:
            output = "无法捕获测试输出"
        
        passed = result.returncode == 0
        
        # 提取关键信息
        test_info = {
            "file": test_file,
            "passed": passed,
            "execution_time": execution_time,
            "output": output,
            "returncode": result.returncode
        }
        
        print(f"测试完成: {'通过' if passed else '失败'}")
        print(f"执行时间: {execution_time:.2f}秒")
        print("=" * 60)
        
        return test_info
    
    def run_all_tests(self):
        """运行所有测试"""
        test_files = [
            "test_command_translation_accuracy.py",
            "test_response_time.py",
            "test_dangerous_command_blocking.py",
            "test_chinese_language_support.py",
            "test_resource_usage.py"
        ]
        
        print("开始运行所有测试")
        print("=" * 80)
        
        total_start_time = time.time()
        
        for test_file in test_files:
            if (self.test_directory / test_file).exists():
                test_info = self.run_test(test_file)
                self.test_results[test_file] = test_info
            else:
                print(f"测试文件不存在: {test_file}")
                self.test_results[test_file] = {
                    "file": test_file,
                    "passed": False,
                    "error": "File not found"
                }
        
        total_end_time = time.time()
        total_execution_time = total_end_time - total_start_time
        
        print("\n" + "=" * 80)
        print("所有测试运行完成")
        print(f"总执行时间: {total_execution_time:.2f}秒")
        
        # 保存测试结果
        self.save_results()
        
        return self.test_results
    
    def save_results(self):
        """保存测试结果到文件"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = self.output_directory / f"test_results_{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"测试结果已保存到: {output_file}")
        
        # 同时保存为最新结果
        latest_file = self.output_directory / "test_results_latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        summary = {
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for info in self.test_results.values() if info.get("passed", False)),
            "failed_tests": sum(1 for info in self.test_results.values() if not info.get("passed", False)),
            "test_details": {}
        }
        
        for test_file, info in self.test_results.items():
            summary["test_details"][test_file] = {
                "passed": info.get("passed", False),
                "execution_time": info.get("execution_time", 0)
            }
        
        return summary

def main():
    """主函数"""
    runner = TestRunner()
    runner.run_all_tests()
    
    # 生成摘要
    summary = runner.generate_summary()
    print("\n测试摘要:")
    print("=" * 60)
    print(f"总测试数: {summary['total_tests']}")
    print(f"通过测试数: {summary['passed_tests']}")
    print(f"失败测试数: {summary['failed_tests']}")
    print()
    
    for test_file, details in summary['test_details'].items():
        status = "通过" if details['passed'] else "失败"
        exec_time = details['execution_time']
        print(f"{test_file}: {status} ({exec_time:.2f}秒)")
    
    print("\n测试运行完成！")

if __name__ == "__main__":
    main()
