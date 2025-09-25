"""
Strict QA Agent - Main Entry Point
Automated QA testing framework for web applications

This is the main entry point that runs test suites in parallel with optimized performance.
"""

import sys
import os
import time
import subprocess
import argparse
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from threading import Event

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.reporter import QAReporter
from utils.data_generator import TestDataGenerator


class StrictQAAgent:
    """
    Main QA Agent class that orchestrates parallel test execution with optimizations
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000",
                 mode: str = "full",
                 headless: bool = False,
                 reporter: Optional[QAReporter] = None,
                 data_generator: Optional[TestDataGenerator] = None,
                 max_workers: Optional[int] = None):
        """
        Initialize the QA Agent
        
        Args:
            base_url: Base URL of the web application to test
            mode: Test mode - one of "fast", "smoke", "integration", "full", "e2e"
            headless: Run browsers in headless mode
            reporter: QAReporter instance for result tracking
            data_generator: TestDataGenerator instance
            max_workers: Maximum number of parallel test processes
        """
        self.base_url = base_url
        self.mode = "full" if mode.lower() == "e2e" else mode.lower()
        self.headless = headless
        self.reporter = reporter or QAReporter()
        self.data_generator = data_generator or TestDataGenerator()
        self.cancel_requested = False
        
        # Determine optimal number of workers
        self.max_workers = max_workers or min(
            multiprocessing.cpu_count(),
            5  # Cap at 5 browsers to avoid resource exhaustion
        )
        
        # Define test module mappings based on mode
        MODE_TEST_MAP = {
            "smoke": {  # Ultra-light smoke tests (~7s)
                "modules": [
                    "tests.test_navigation",  # Just homepage load
                    "tests.test_api"         # One fast API call
                ],
                "options": {
                    "ultra_light": True,        # Minimal checks only
                    "short_timeout": True,      # Use 3s timeouts
                    "skip_validation": True,    # Skip all validation
                    "skip_discovery": True,     # No endpoint discovery
                    "max_results": 3,          # Stop after 3 results
                }
            },
            "fast": {  # Basic regression subset (~2min)
                "modules": [
                    "tests.test_login",
                    "tests.test_navigation",
                    "tests.test_api"
                ],
                "options": {
                    "skip_validation": True,
                    "skip_edge_cases": True,
                    "quick_mode": True
                }
            },
            "integration": {  # Integration tests (~5min)
                "modules": [
                    "tests.test_signup",
                    "tests.test_login",
                    "tests.test_api",
                    "tests.test_forms"
                ],
                "options": {
                    "skip_performance": True
                }
            },
            "full": {  # Complete regression (~15min)
                "modules": [
                    "tests.test_signup",
                    "tests.test_login",
                    "tests.test_navigation",
                    "tests.test_forms",
                    "tests.test_api",
                    "tests.test_security",
                    "tests.test_performance"
                ],
                "options": {}
            }
        }
        
        # Set test modules and options based on mode
        mode_config = MODE_TEST_MAP.get(self.mode, MODE_TEST_MAP["full"])
        self.test_modules = mode_config["modules"]
        self.test_options = mode_config["options"]

    def request_cancel(self):
        """Request cancellation of the current test run"""
        self.cancel_requested = True

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test modules based on current mode
        
        Returns:
            Dict with test execution summary
        """
        print("🚀 Starting Strict QA Agent...")
        print(f"🎯 Target URL: {self.base_url}")
        print(f"⚙️  Mode: {self.mode}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Initialize test run
        self.reporter.start_run()
        self.reporter.set_total_tests(len(self.test_modules))
        self.start_time = time.time()
        total_bugs = 0
        
        try:
            for module_name in self.test_modules:
                # Check for cancellation request
                if self.cancel_requested:
                    print("⏹️  Test execution cancelled by user")
                    self.reporter.log_test_result(
                        "Test Suite",
                        "CANCELLED",
                        "Test execution cancelled by user",
                        "System",
                        "Info"
                    )
                    success = False
                    break
                
                print(f"\n📋 Running {module_name}...")
                try:
                    # Run the test module
                    if not self._run_test_module(module_name):
                        total_bugs += 1
                    
                    # Increment completed tests
                    self.reporter.increment_completed()
                    
                except Exception as e:
                    total_bugs += 1
                    self.reporter.log_test_result(
                        f"Execute {module_name}",
                        "FAIL",
                        f"Module execution failed: {str(e)}",
                        "System",
                        "High"
                    )
            
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            
            # Finalize run
            self.reporter.finish_run()
            
            # Generate report if any tests were run
            if total_bugs > 0 or not self.cancel_requested:
                self._generate_final_report(execution_time)
            
            return {
                "success": total_bugs == 0 and not self.cancel_requested,
                "bugs_found": total_bugs,
                "execution_time": execution_time,
                "cancelled": self.cancel_requested,
                "mode": self.mode
            }
            
        except Exception as e:
            self.reporter.log_test_result(
                "Test Suite",
                "FAIL",
                f"Test suite execution failed: {str(e)}",
                "System",
                "High"
            )
            self.reporter.finish_run()
            return {
                "success": False,
                "bugs_found": total_bugs + 1,
                "error": str(e),
                "cancelled": self.cancel_requested,
                "mode": self.mode
            }

    def _run_test_module(self, module: str) -> bool:
        """
        Run a single test module
        
        Args:
            module: Module path (e.g., 'tests.test_signup')
            
        Returns:
            bool: True if tests passed, False if failed
        """
        try:
            # Import the module
            module = __import__(module, fromlist=['run_tests'])
            
            # Check if the module has a run_tests function
            if hasattr(module, 'run_tests'):
                # Run the tests with the agent's context
                module.run_tests(
                    base_url=self.base_url,
                    reporter=self.reporter,
                    data_generator=self.data_generator,
                    headless=self.headless
                )
                return True
            else:
                self.reporter.log_test_result(
                    f"Module {module}",
                    "FAIL",
                    "Module doesn't have run_tests function",
                    "System",
                    "Medium"
                )
                return False
                
        except Exception as e:
            self.reporter.log_test_result(
                f"Module {module}",
                "FAIL",
                f"Module execution error: {str(e)}",
                "System", 
                "High"
            )
            return False
    
    def request_cancel(self):
        """Signal the agent to cancel running further tests."""
        self.cancel_requested = True

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test modules based on current mode
        
        Returns:
            Dict with test execution summary
        """
        print("🚀 Starting Strict QA Agent...")
        print(f"🎯 Target URL: {self.base_url}")
        print(f"⚙️  Mode: {self.mode}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Initialize test run
        self.reporter.start_run()
        self.reporter.set_total_tests(len(self.test_modules))
        self.start_time = time.time()
        total_bugs = 0
        was_cancelled = False
        
        try:
            for index, module_name in enumerate(self.test_modules, 1):
                # Check for cancellation request
                if self.cancel_requested:
                    print("⏹️  Test execution cancelled by user")
                    self.reporter.log_test_result(
                        "Test Suite",
                        "CANCELLED",
                        "Test execution cancelled by user",
                        "System",
                        "Info"
                    )
                    was_cancelled = True
                    break
                
                print(f"\n📋 Running {module_name}...")
                try:
                    # Run the test module
                    if not self._run_test_module(module_name):
                        total_bugs += 1
                    
                    # Increment completed tests
                    self.reporter.increment_completed()
                    
                except Exception as e:
                    total_bugs += 1
                    self.reporter.log_test_result(
                        f"Execute {module_name}",
                        "FAIL",
                        f"Module execution failed: {str(e)}",
                        "System",
                        "High"
                    )
            
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            
            # Finalize run
            self.reporter.finish_run()
            
            # Generate report if any tests were run
            if total_bugs > 0 or not was_cancelled:
                self._generate_final_report(execution_time)
            
            return {
                "success": total_bugs == 0 and not was_cancelled,
                "bugs_found": total_bugs,
                "execution_time": execution_time,
                "cancelled": was_cancelled,
                "mode": self.mode
            }
            
        except Exception as e:
            self.reporter.log_test_result(
                "Test Suite",
                "FAIL",
                f"Test suite execution failed: {str(e)}",
                "System",
                "High"
            )
            self.reporter.finish_run()
            return {
                "success": False,
                "bugs_found": total_bugs + 1,
                "error": str(e),
                "cancelled": self.cancel_requested,
                "mode": self.mode
            }
    
    def _run_test_module(self, module_name: str):
        """
        Run a specific test module
        
        Args:
            module_name: Name of the test module to run
        """
        try:
            # Import the module
            module = __import__(module_name, fromlist=['run_tests'])
            
            # Check if the module has a run_tests function
            if hasattr(module, 'run_tests'):
                # Run the tests with the agent's context
                module.run_tests(self.base_url, self.reporter, self.data_generator)
            else:
                print(f"⚠️  Module {module_name} doesn't have a run_tests function")
                self.reporter.log_test_result(
                    f"Module {module_name}",
                    "FAIL",
                    "Module doesn't have run_tests function",
                    "System",
                    "Medium"
                )
                
        except Exception as e:
            print(f"❌ Error in module {module_name}: {e}")
            self.reporter.log_test_result(
                f"Module {module_name}",
                "FAIL",
                f"Module execution error: {e}",
                "System", 
                "High"
            )
    
    def _generate_final_report(self, execution_time: float):
        """
        Generate the final test report
        
        Args:
            execution_time: Total execution time in seconds
        """
        print("\n" + "="*80)
        print("📊 GENERATING FINAL REPORT")
        print("="*80)
        
        # Print summary to console
        self.reporter.print_summary()
        
        # Generate Excel report
        report_file = self.reporter.generate_excel_report()
        
        # Print execution time
        print(f"\n⏱️  Total Execution Time: {execution_time:.2f} seconds")
        print(f"📁 Report saved to: {report_file}")
        
        # Print bug summary if any bugs found
        bugs = self.reporter.get_bug_summary()
        if bugs:
            print(f"\n🐛 BUGS FOUND ({len(bugs)}):")
            for i, bug in enumerate(bugs, 1):
                print(f"  {i}. {bug['Test Case']} - {bug['Details']}")
    
    def _get_execution_summary(self, execution_time: float) -> Dict[str, Any]:
        """
        Get execution summary
        
        Args:
            execution_time: Total execution time in seconds
            
        Returns:
            Dictionary with execution summary
        """
        return {
            'total_tests': len(self.reporter.test_results),
            'passed': self.reporter.pass_count,
            'failed': self.reporter.fail_count,
            'bugs_found': self.reporter.bug_count,
            'execution_time': execution_time,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'base_url': self.base_url
        }
    
    def run_specific_tests(self, test_modules: List[str]) -> Dict[str, Any]:
        """
        Run only specific test modules
        
        Args:
            test_modules: List of test module names to run
            
        Returns:
            Dictionary with test execution summary
        """
        print(f"🎯 Running specific tests: {', '.join(test_modules)}")
        
        self.start_time = time.time()
        
        total_modules = len(test_modules)
        for index, module_name in enumerate(test_modules, start=1):
            if self.cancel_requested:
                print("⏹️  Cancel requested. Halting remaining tests.")
                break
            try:
                if self.progress_callback and total_modules > 0:
                    percent = int(((index - 1) / total_modules) * 100)
                    self.progress_callback(percent)
            except Exception:
                pass
            if module_name in self.test_modules:
                try:
                    print(f"\n📋 Running {module_name}...")
                    self._run_test_module(module_name)
                except Exception as e:
                    print(f"❌ Error running {module_name}: {e}")
            else:
                print(f"⚠️  Unknown test module: {module_name}")
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        # Ensure progress shows 100% at end
        try:
            if self.progress_callback:
                self.progress_callback(100)
        except Exception:
            pass
        self._generate_final_report(execution_time)
        return self._get_execution_summary(execution_time)

    def request_stop(self):
        """Signal the agent to stop running further tests (alias for request_cancel)."""
        self.request_cancel()


def main():
    """
    Main function - entry point for the QA Agent
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Strict QA Agent - Automated web testing framework')
    parser.add_argument("base_url", help="Base URL of the site to test", nargs='?', default="http://127.0.0.1:8000")
    parser.add_argument("--mode", choices=["fast", "full"], default="full", help="Run mode (fast=smoke tests only, full=all tests)")
    parser.add_argument("--headless", action="store_true", help="Run tests in headless mode")
    args = parser.parse_args()
    
    try:
        print("🔍 STRICT QA AGENT")
    except Exception:
        print("STRICT QA AGENT")
    print("=" * 50)
    print("Automated QA testing framework for web applications")
    print("=" * 50)
    print(f"Mode: {args.mode}")
    print(f"Target: {args.base_url}")
    
    # Create and run the QA Agent with parsed arguments
    agent = StrictQAAgent(
        base_url=args.base_url,
        mode=args.mode,
        headless=args.headless
    )
    
    try:
        # Run all tests
        summary = agent.run_all_tests()
        
        # Exit with appropriate code
        if summary['bugs_found'] > 0:
            try:
                print(f"\n⚠️  QA Agent completed with {summary['bugs_found']} bugs found!")
            except Exception:
                print(f"\nQA Agent completed with {summary['bugs_found']} bugs found!")
            sys.exit(1)  # Exit with error code if bugs found
        else:
            try:
                print(f"\n✅ QA Agent completed successfully! No bugs found.")
            except Exception:
                print("\nQA Agent completed successfully! No bugs found.")
            sys.exit(0)  # Exit with success code
            
    except KeyboardInterrupt:
        try:
            print("\n\n⏹️  QA Agent stopped by user")
            agent.request_cancel()  # Ensure clean shutdown
        except Exception:
            print("\n\nQA Agent stopped by user")
        sys.exit(130)
    except Exception as e:
        try:
            print(f"\n❌ QA Agent failed with error: {e}")
        except Exception:
            print(f"\nQA Agent failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
