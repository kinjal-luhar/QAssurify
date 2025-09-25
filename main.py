"""
Strict QA Agent - Main Entry Point
Automated QA testing framework for web applications

This is the main entry point that runs all test suites in sequence.
The agent will test a complete web project hosted on localhost.
"""

import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.reporter import QAReporter
from utils.data_generator import TestDataGenerator
from urllib.parse import urlparse


def _normalize_base_url(raw_url: Optional[str]) -> str:
    """
    Normalize user-provided base URL inputs.
    - Trims whitespace and surrounding quotes
    - Removes accidental leading '@'
    - Adds a default scheme (https) if missing
    - Avoids trailing spaces
    """
    default_url = "http://127.0.0.1:8000"
    if not raw_url:
        return default_url
    url = str(raw_url).strip().strip("'\"")
    # Remove a single leading '@' if present (copy/paste artifact)
    if url.startswith('@'):
        url = url[1:]
    # Add scheme if missing
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)
    # Basic sanity: require netloc after normalization
    if not parsed.netloc:
        return default_url
    return url


class StrictQAAgent:
    """
    Main QA Agent class that orchestrates all testing activities
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", progress_callback: Optional[Callable[[int], None]] = None):
        """
        Initialize the QA Agent
        
        Args:
            base_url: Base URL of the web application to test
        """
        self.base_url = _normalize_base_url(base_url)
        self.reporter = QAReporter()
        self.data_generator = TestDataGenerator()
        self.start_time = None
        self.end_time = None
        self.stop_requested = False
        self.progress_callback = progress_callback
        
        # Default test modules (full E2E)
        self.test_modules = [
            'tests.test_signup',
            'tests.test_login', 
            'tests.test_navigation',
            'tests.test_forms',
            'tests.test_api'
        ]

    def configure_suite(self, test_type: str = "e2e", include_api: bool = True, include_security: bool = False) -> None:
        """
        Configure which test modules to run based on requested strategy.
        test_type: 'e2e' | 'smoke' | 'integration'
        include_api: include API-related tests
        include_security: currently piggybacks on forms/API suites (lightweight)
        """
        test_type = (test_type or "e2e").lower().strip()
        modules_e2e = [
            'tests.test_signup',
            'tests.test_login',
            'tests.test_navigation',
            'tests.test_forms',
        ]
        modules_smoke = [
            'tests.test_navigation',
            'tests.test_forms',
        ]
        modules_integration = [
            'tests.test_api',
        ]
        chosen: List[str]
        if test_type == 'smoke':
            chosen = modules_smoke[:]
        elif test_type == 'integration':
            chosen = modules_integration[:]
        else:
            chosen = modules_e2e[:]
        if include_api and 'tests.test_api' not in chosen:
            chosen.append('tests.test_api')
        # Security flag can later toggle dedicated suites; for now it keeps defaults.
        self.test_modules = chosen
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test suites in sequence
        
        Returns:
            Dictionary with test execution summary
        """
        print("🚀 Starting Strict QA Agent...")
        print(f"🎯 Target URL: {self.base_url}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        self.start_time = time.time()
        
        total_modules = len(self.test_modules)
        # Run each test module
        for index, module_name in enumerate(self.test_modules, start=1):
            if self.stop_requested:
                print("⏹️  Stop requested. Halting remaining tests.")
                break
            # Update progress before running module
            try:
                if self.progress_callback and total_modules > 0:
                    percent = int(((index - 1) / total_modules) * 100)
                    self.progress_callback(percent)
            except Exception:
                pass
            try:
                print(f"\n📋 Running {module_name}...")
                self._run_test_module(module_name)
            except ImportError as e:
                print(f"⚠️  Module {module_name} not found: {e}")
                self.reporter.log_test_result(
                    f"Import {module_name}",
                    "FAIL",
                    f"Module not found: {e}",
                    "System",
                    "High"
                )
            except Exception as e:
                print(f"❌ Error running {module_name}: {e}")
                self.reporter.log_test_result(
                    f"Execute {module_name}",
                    "FAIL", 
                    f"Execution error: {e}",
                    "System",
                    "High"
                )
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        # Ensure progress shows 100% at end
        try:
            if self.progress_callback:
                self.progress_callback(100)
        except Exception:
            pass
        
        # Generate final report
        self._generate_final_report(execution_time)
        
        return self._get_execution_summary(execution_time)
    
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
            if self.stop_requested:
                print("⏹️  Stop requested. Halting remaining tests.")
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
        """Signal the agent to stop running further tests."""
        self.stop_requested = True


def main():
    """
    Main function - entry point for the QA Agent
    """
    try:
        print("🔍 STRICT QA AGENT")
    except Exception:
        print("STRICT QA AGENT")
    print("=" * 50)
    print("Automated QA testing framework for web applications")
    print("=" * 50)
    
    # Get base URL from command line argument or use default
    base_url = "http://127.0.0.1:8000"
    if len(sys.argv) > 1:
        base_url = _normalize_base_url(sys.argv[1])
    
    # Create and run the QA Agent
    agent = StrictQAAgent(base_url)
    
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
