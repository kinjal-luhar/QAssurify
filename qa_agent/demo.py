"""
Demo script for Strict QA Agent
Shows how to use the QA Agent with different configurations
"""

import sys
import os
from main import StrictQAAgent

def demo_basic_usage():
    """Demonstrate basic usage of the QA Agent"""
    print("🚀 Strict QA Agent - Basic Demo")
    print("=" * 50)
    
    # Create QA Agent instance
    agent = StrictQAAgent("http://127.0.0.1:8000")
    
    print("📋 Running all test suites...")
    print("This will test:")
    print("  - Signup form validation")
    print("  - Login functionality")
    print("  - Page navigation")
    print("  - General form validation")
    print("  - API endpoints")
    print()
    
    # Run all tests
    summary = agent.run_all_tests()
    
    print("\n📊 Demo completed!")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Bugs found: {summary['bugs_found']}")
    print(f"Execution time: {summary['execution_time']:.2f} seconds")

def demo_specific_tests():
    """Demonstrate running specific test modules"""
    print("🎯 Strict QA Agent - Specific Tests Demo")
    print("=" * 50)
    
    agent = StrictQAAgent("http://127.0.0.1:8000")
    
    # Run only signup and login tests
    specific_tests = ['tests.test_signup', 'tests.test_login']
    
    print(f"📋 Running specific tests: {', '.join(specific_tests)}")
    print()
    
    summary = agent.run_specific_tests(specific_tests)
    
    print("\n📊 Specific tests completed!")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Bugs found: {summary['bugs_found']}")

def demo_custom_url():
    """Demonstrate testing a custom URL"""
    print("🌐 Strict QA Agent - Custom URL Demo")
    print("=" * 50)
    
    # Test a different URL
    custom_url = "http://localhost:3000"
    agent = StrictQAAgent(custom_url)
    
    print(f"📋 Testing custom URL: {custom_url}")
    print("Note: This will only work if you have a web app running on port 3000")
    print()
    
    try:
        summary = agent.run_all_tests()
        print("\n📊 Custom URL test completed!")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Bugs found: {summary['bugs_found']}")
    except Exception as e:
        print(f"❌ Error testing custom URL: {e}")
        print("This is expected if no app is running on port 3000")

def demo_data_generation():
    """Demonstrate test data generation"""
    print("🎲 Strict QA Agent - Data Generation Demo")
    print("=" * 50)
    
    from utils.data_generator import TestDataGenerator
    
    # Create data generator
    generator = TestDataGenerator()
    
    print("📋 Generating test data samples:")
    print()
    
    # Generate user data
    print("👤 User Data (Valid):")
    user_data = generator.generate_user_data(valid=True)
    for key, value in list(user_data.items())[:5]:  # Show first 5 fields
        print(f"  {key}: {value}")
    print()
    
    print("👤 User Data (Invalid):")
    invalid_user_data = generator.generate_user_data(valid=False)
    for key, value in list(invalid_user_data.items())[:5]:  # Show first 5 fields
        print(f"  {key}: {value}")
    print()
    
    # Generate edge case data
    print("🔍 Edge Case Data:")
    edge_data = generator.generate_edge_case_data()
    for key, value in list(edge_data.items())[:3]:  # Show first 3 fields
        print(f"  {key}: {str(value)[:50]}...")
    print()
    
    # Generate API test data
    print("🔌 API Test Data:")
    api_data = generator.generate_api_test_data()
    print(f"  Valid JSON: {api_data['valid_json']}")
    print(f"  Invalid JSON: {api_data['invalid_json']}")

def main():
    """Main demo function"""
    print("🔍 STRICT QA AGENT - DEMO")
    print("=" * 60)
    print("This demo shows different ways to use the Strict QA Agent")
    print("=" * 60)
    print()
    
    while True:
        print("Choose a demo:")
        print("1. Basic Usage (run all tests)")
        print("2. Specific Tests (signup + login only)")
        print("3. Custom URL (test localhost:3000)")
        print("4. Data Generation (show test data samples)")
        print("5. Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        print()
        
        if choice == '1':
            demo_basic_usage()
        elif choice == '2':
            demo_specific_tests()
        elif choice == '3':
            demo_custom_url()
        elif choice == '4':
            demo_data_generation()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
