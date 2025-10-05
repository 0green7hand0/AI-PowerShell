#!/usr/bin/env python3
"""Test Runner for AI PowerShell Assistant

This script runs all tests and generates comprehensive coverage reports.
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time
import json
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))


class TestRunner:
    """Comprehensive test runner with coverage reporting"""
    
    def __init__(self):
        self.src_dir = Path(__file__).parent
        self.test_results = {}
        self.coverage_data = {}
        
    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run all unit tests"""
        print("=" * 60)
        print("RUNNING UNIT TESTS")
        print("=" * 60)
        
        unit_test_files = [
            # AI Engine Tests
            "ai_engine/test_engine.py",
            "ai_engine/test_providers.py", 
            "ai_engine/test_translation.py",
            "ai_engine/test_error_detection.py",
            
            # Security Engine Tests
            "security/test_engine.py",
            "security/test_whitelist.py",
            "security/test_permissions.py",
            "security/test_sandbox.py",
            "security/test_confirmation.py",
            
            # Execution Engine Tests
            "execution/test_executor.py",
            "execution/test_command_execution.py",
            "execution/test_platform_adaptation.py",
            "execution/test_output_formatter.py",
            "execution/test_platform_adapter.py",
            
            # Context Management Tests
            "context/test_manager.py",
            "context/test_history.py",
            
            # Storage Tests
            "storage/test_storage.py",
            
            # Configuration Tests
            "config/test_manager.py",
            
            # Logging Tests
            "log_engine/test_engine.py",
        ]
        
        results = {}
        total_passed = 0
        total_failed = 0
        
        for test_file in unit_test_files:
            print(f"\nRunning {test_file}...")
            
            cmd = [
                sys.executable, "-m", "pytest", 
                str(self.src_dir / test_file),
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            end_time = time.time()
            
            # Parse results
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            errors = result.stdout.count(" ERROR")
            
            results[test_file] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "output": result.stdout if verbose else "",
                "stderr": result.stderr if result.stderr else ""
            }
            
            total_passed += passed
            total_failed += failed + errors
            
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"  {status}: {passed} passed, {failed} failed, {errors} errors ({end_time - start_time:.2f}s)")
            
            if result.returncode != 0 and not verbose:
                print(f"  Error output: {result.stderr}")
        
        print(f"\nUnit Tests Summary: {total_passed} passed, {total_failed} failed")
        return results
    
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run all integration tests"""
        print("\n" + "=" * 60)
        print("RUNNING INTEGRATION TESTS")
        print("=" * 60)
        
        integration_test_files = [
            "test_end_to_end.py",
            "test_mcp_integration.py", 
            "test_mcp_tools_simple.py",
            "test_error_handling.py",
            "test_startup_system.py"
        ]
        
        results = {}
        total_passed = 0
        total_failed = 0
        
        for test_file in integration_test_files:
            print(f"\nRunning {test_file}...")
            
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.src_dir / test_file),
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            end_time = time.time()
            
            # Parse results
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            errors = result.stdout.count(" ERROR")
            
            results[test_file] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "output": result.stdout if verbose else "",
                "stderr": result.stderr if result.stderr else ""
            }
            
            total_passed += passed
            total_failed += failed + errors
            
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"  {status}: {passed} passed, {failed} failed, {errors} errors ({end_time - start_time:.2f}s)")
            
            if result.returncode != 0 and not verbose:
                print(f"  Error output: {result.stderr}")
        
        print(f"\nIntegration Tests Summary: {total_passed} passed, {total_failed} failed")
        return results
    
    def run_security_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run security penetration tests"""
        print("\n" + "=" * 60)
        print("RUNNING SECURITY PENETRATION TESTS")
        print("=" * 60)
        
        security_test_files = [
            "test_security_penetration.py"
        ]
        
        results = {}
        total_passed = 0
        total_failed = 0
        
        for test_file in security_test_files:
            print(f"\nRunning {test_file}...")
            
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.src_dir / test_file),
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            end_time = time.time()
            
            # Parse results
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            errors = result.stdout.count(" ERROR")
            
            results[test_file] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "output": result.stdout if verbose else "",
                "stderr": result.stderr if result.stderr else ""
            }
            
            total_passed += passed
            total_failed += failed + errors
            
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"  {status}: {passed} passed, {failed} failed, {errors} errors ({end_time - start_time:.2f}s)")
        
        print(f"\nSecurity Tests Summary: {total_passed} passed, {total_failed} failed")
        return results
    
    def run_cross_platform_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run cross-platform compatibility tests"""
        print("\n" + "=" * 60)
        print("RUNNING CROSS-PLATFORM COMPATIBILITY TESTS")
        print("=" * 60)
        
        cross_platform_test_files = [
            "test_cross_platform_compatibility.py"
        ]
        
        results = {}
        total_passed = 0
        total_failed = 0
        
        for test_file in cross_platform_test_files:
            print(f"\nRunning {test_file}...")
            
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.src_dir / test_file),
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            end_time = time.time()
            
            # Parse results
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            errors = result.stdout.count(" ERROR")
            
            results[test_file] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "output": result.stdout if verbose else "",
                "stderr": result.stderr if result.stderr else ""
            }
            
            total_passed += passed
            total_failed += failed + errors
            
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"  {status}: {passed} passed, {failed} failed, {errors} errors ({end_time - start_time:.2f}s)")
        
        print(f"\nCross-Platform Tests Summary: {total_passed} passed, {total_failed} failed")
        return results
    
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance benchmarks"""
        print("\n" + "=" * 60)
        print("RUNNING PERFORMANCE BENCHMARKS")
        print("=" * 60)
        
        performance_test_files = [
            "test_performance_benchmarks.py"
        ]
        
        results = {}
        total_passed = 0
        total_failed = 0
        
        for test_file in performance_test_files:
            print(f"\nRunning {test_file}...")
            
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.src_dir / test_file),
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header",
                "-s"  # Don't capture output for performance tests
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            end_time = time.time()
            
            # Parse results
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            errors = result.stdout.count(" ERROR")
            
            results[test_file] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "output": result.stdout if verbose else "",
                "stderr": result.stderr if result.stderr else ""
            }
            
            total_passed += passed
            total_failed += failed + errors
            
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"  {status}: {passed} passed, {failed} failed, {errors} errors ({end_time - start_time:.2f}s)")
        
        print(f"\nPerformance Tests Summary: {total_passed} passed, {total_failed} failed")
        return results
    
    def run_workflow_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run comprehensive workflow tests"""
        print("\n" + "=" * 60)
        print("RUNNING COMPREHENSIVE WORKFLOW TESTS")
        print("=" * 60)
        
        workflow_test_files = [
            "test_comprehensive_workflows.py"
        ]
        
        results = {}
        total_passed = 0
        total_failed = 0
        
        for test_file in workflow_test_files:
            print(f"\nRunning {test_file}...")
            
            cmd = [
                sys.executable, "-m", "pytest",
                str(self.src_dir / test_file),
                "-v" if verbose else "-q",
                "--tb=short",
                "--no-header"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            end_time = time.time()
            
            # Parse results
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            errors = result.stdout.count(" ERROR")
            
            results[test_file] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "duration": end_time - start_time,
                "return_code": result.returncode,
                "output": result.stdout if verbose else "",
                "stderr": result.stderr if result.stderr else ""
            }
            
            total_passed += passed
            total_failed += failed + errors
            
            status = "PASS" if result.returncode == 0 else "FAIL"
            print(f"  {status}: {passed} passed, {failed} failed, {errors} errors ({end_time - start_time:.2f}s)")
        
        print(f"\nWorkflow Tests Summary: {total_passed} passed, {total_failed} failed")
        return results
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate test coverage report"""
        print("\n" + "=" * 60)
        print("GENERATING COVERAGE REPORT")
        print("=" * 60)
        
        try:
            # Run coverage analysis
            cmd = [
                sys.executable, "-m", "coverage", "run", "--source=.", "-m", "pytest",
                "--tb=no", "-q"
            ]
            
            print("Running coverage analysis...")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            
            if result.returncode != 0:
                print(f"Coverage run failed: {result.stderr}")
                return {"error": "Coverage analysis failed"}
            
            # Generate coverage report
            cmd = [sys.executable, "-m", "coverage", "report", "--show-missing"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.src_dir)
            
            if result.returncode != 0:
                print(f"Coverage report failed: {result.stderr}")
                return {"error": "Coverage report generation failed"}
            
            print("Coverage Report:")
            print(result.stdout)
            
            # Extract coverage percentage
            lines = result.stdout.split('\n')
            total_line = [line for line in lines if line.startswith('TOTAL')]
            
            coverage_percentage = 0
            if total_line:
                parts = total_line[0].split()
                if len(parts) >= 4:
                    coverage_str = parts[3].rstrip('%')
                    try:
                        coverage_percentage = float(coverage_str)
                    except ValueError:
                        pass
            
            return {
                "coverage_percentage": coverage_percentage,
                "report": result.stdout,
                "meets_target": coverage_percentage >= 90.0
            }
            
        except Exception as e:
            print(f"Coverage analysis error: {e}")
            return {"error": str(e)}
    
    def print_final_summary(self, all_results: Dict[str, Dict[str, Any]], coverage_data: Dict[str, Any]):
        """Print final test summary"""
        print("\n" + "=" * 80)
        print("FINAL TEST SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        total_duration = 0
        
        for test_category, results in all_results.items():
            category_passed = sum(r["passed"] for r in results.values())
            category_failed = sum(r["failed"] + r["errors"] for r in results.values())
            category_duration = sum(r["duration"] for r in results.values())
            
            total_passed += category_passed
            total_failed += category_failed
            total_duration += category_duration
            
            status = "PASS" if category_failed == 0 else "FAIL"
            print(f"{test_category:30} {status:>6} ({category_passed:3} passed, {category_failed:3} failed, {category_duration:6.2f}s)")
        
        print("-" * 80)
        overall_status = "PASS" if total_failed == 0 else "FAIL"
        print(f"{'OVERALL':30} {overall_status:>6} ({total_passed:3} passed, {total_failed:3} failed, {total_duration:6.2f}s)")
        
        if "coverage_percentage" in coverage_data:
            coverage_status = "PASS" if coverage_data["meets_target"] else "FAIL"
            print(f"{'TEST COVERAGE':30} {coverage_status:>6} ({coverage_data['coverage_percentage']:5.1f}% - target: 90%)")
        
        print("=" * 80)
        
        if total_failed == 0 and coverage_data.get("meets_target", False):
            print("🎉 ALL TESTS PASSED WITH ADEQUATE COVERAGE!")
        elif total_failed == 0:
            print("✅ All tests passed, but coverage below target")
        else:
            print("❌ Some tests failed")
        
        return total_failed == 0 and coverage_data.get("meets_target", False)
    
    def run_all_tests(self, verbose: bool = False, skip_performance: bool = False) -> bool:
        """Run all test suites"""
        print("AI PowerShell Assistant - Comprehensive Test Suite")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all test categories
        all_results = {}
        
        all_results["Unit Tests"] = self.run_unit_tests(verbose)
        all_results["Integration Tests"] = self.run_integration_tests(verbose)
        all_results["Security Tests"] = self.run_security_tests(verbose)
        all_results["Cross-Platform Tests"] = self.run_cross_platform_tests(verbose)
        all_results["Workflow Tests"] = self.run_workflow_tests(verbose)
        
        if not skip_performance:
            all_results["Performance Tests"] = self.run_performance_tests(verbose)
        
        # Generate coverage report
        coverage_data = self.generate_coverage_report()
        
        end_time = time.time()
        
        # Print final summary
        success = self.print_final_summary(all_results, coverage_data)
        
        print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
        
        return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run AI PowerShell Assistant test suite")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance tests")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--security-only", action="store_true", help="Run only security tests")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.unit_only:
        results = runner.run_unit_tests(args.verbose)
        success = all(r["return_code"] == 0 for r in results.values())
    elif args.integration_only:
        results = runner.run_integration_tests(args.verbose)
        success = all(r["return_code"] == 0 for r in results.values())
    elif args.security_only:
        results = runner.run_security_tests(args.verbose)
        success = all(r["return_code"] == 0 for r in results.values())
    elif args.performance_only:
        results = runner.run_performance_tests(args.verbose)
        success = all(r["return_code"] == 0 for r in results.values())
    else:
        success = runner.run_all_tests(args.verbose, args.skip_performance)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()