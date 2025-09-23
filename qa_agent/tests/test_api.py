"""
API Tests
Tests backend APIs using Python requests library for response validation, status codes, and data integrity
"""

import requests
import json
import time
from urllib.parse import urljoin
from typing import Dict, Any, List


def run_tests(base_url: str, reporter, data_generator):
    """
    Run all API tests
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance for logging results
        data_generator: TestDataGenerator instance for test data
    """
    print("🔌 Testing APIs...")
    
    try:
        # Test 1: Test API discovery
        test_api_discovery(base_url, reporter)
        
        # Test 2: Test common API endpoints
        test_common_api_endpoints(base_url, reporter)
        
        # Test 3: Test API response validation
        test_api_response_validation(base_url, reporter, data_generator)
        
        # Test 4: Test API error handling
        test_api_error_handling(base_url, reporter, data_generator)
        
        # Test 5: Test API security
        test_api_security(base_url, reporter, data_generator)
        
        # Test 6: Test API performance
        test_api_performance(base_url, reporter)
        
        # Test 7: Test API authentication
        test_api_authentication(base_url, reporter, data_generator)
        
        # Test 8: Test API data validation
        test_api_data_validation(base_url, reporter, data_generator)
        
    except Exception as e:
        reporter.log_test_result(
            "API Test Setup",
            "FAIL",
            f"Failed to setup API tests: {e}",
            "API",
            "High"
        )


def test_api_discovery(base_url: str, reporter):
    """
    Test API discovery and common endpoints
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        # Common API endpoints to test
        api_endpoints = [
            '/api',
            '/api/v1',
            '/api/v2',
            '/api/docs',
            '/api/swagger',
            '/api/health',
            '/api/status',
            '/api/users',
            '/api/auth',
            '/api/login',
            '/api/register'
        ]
        
        discovered_apis = []
        
        for endpoint in api_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    discovered_apis.append(endpoint)
                elif response.status_code in [401, 403, 405]:
                    # These status codes indicate the endpoint exists but requires auth or different method
                    discovered_apis.append(f"{endpoint} (requires auth/method)")
                    
            except requests.exceptions.RequestException:
                continue
        
        if discovered_apis:
            reporter.log_test_result(
                "API Discovery",
                "PASS",
                f"Discovered {len(discovered_apis)} API endpoints: {', '.join(discovered_apis[:5])}",
                "API",
                "Low"
            )
        else:
            reporter.log_test_result(
                "API Discovery",
                "BUG",
                "No API endpoints discovered. This might indicate missing API documentation or endpoints.",
                "API",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "API Discovery",
            "FAIL",
            f"Error during API discovery: {e}",
            "API",
            "High"
        )


def test_common_api_endpoints(base_url: str, reporter):
    """
    Test common API endpoints for basic functionality
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        # Test health/status endpoints
        health_endpoints = ['/api/health', '/api/status', '/health', '/status']
        
        for endpoint in health_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    reporter.log_test_result(
                        "API Health Check",
                        "PASS",
                        f"Health endpoint {endpoint} returns 200 OK",
                        "API",
                        "Low"
                    )
                    return
                    
            except requests.exceptions.RequestException:
                continue
        
        # Test user-related endpoints
        user_endpoints = ['/api/users', '/api/user', '/users', '/user']
        
        for endpoint in user_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                response = requests.get(url, timeout=10)
                
                if response.status_code in [200, 401, 403]:
                    reporter.log_test_result(
                        "API User Endpoints",
                        "PASS",
                        f"User endpoint {endpoint} responds with status {response.status_code}",
                        "API",
                        "Low"
                    )
                    break
                    
            except requests.exceptions.RequestException:
                continue
        else:
            reporter.log_test_result(
                "API User Endpoints",
                "BUG",
                "No user-related API endpoints found or accessible",
                "API",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "API Common Endpoints",
            "FAIL",
            f"Error testing common API endpoints: {e}",
            "API",
            "High"
        )


def test_api_response_validation(base_url: str, reporter, data_generator):
    """
    Test API response validation and structure
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        # Test API endpoints that might return JSON
        api_endpoints = ['/api', '/api/v1', '/api/users', '/api/health']
        
        for endpoint in api_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Check if response is valid JSON
                    try:
                        json_data = response.json()
                        
                        # Validate JSON structure
                        if isinstance(json_data, (dict, list)):
                            reporter.log_test_result(
                                "API Response Validation",
                                "PASS",
                                f"API endpoint {endpoint} returns valid JSON",
                                "API",
                                "Low"
                            )
                        else:
                            reporter.log_test_result(
                                "API Response Validation",
                                "BUG",
                                f"API endpoint {endpoint} returns invalid JSON structure",
                                "API",
                                "Medium"
                            )
                            
                    except json.JSONDecodeError:
                        # Check if response is HTML (might be API documentation)
                        content_type = response.headers.get('content-type', '')
                        if 'text/html' in content_type:
                            reporter.log_test_result(
                                "API Response Validation",
                                "PASS",
                                f"API endpoint {endpoint} returns HTML (likely documentation)",
                                "API",
                                "Low"
                            )
                        else:
                            reporter.log_test_result(
                                "API Response Validation",
                                "BUG",
                                f"API endpoint {endpoint} returns invalid JSON",
                                "API",
                                "Medium"
                            )
                    
                    break
                    
            except requests.exceptions.RequestException:
                continue
        else:
            reporter.log_test_result(
                "API Response Validation",
                "PASS",
                "No API endpoints found to test response validation",
                "API",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "API Response Validation",
            "FAIL",
            f"Error testing API response validation: {e}",
            "API",
            "High"
        )


def test_api_error_handling(base_url: str, reporter, data_generator):
    """
    Test API error handling and status codes
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        # Test non-existent endpoint
        non_existent_url = urljoin(base_url, '/api/nonexistent')
        response = requests.get(non_existent_url, timeout=10)
        
        if response.status_code == 404:
            reporter.log_test_result(
                "API Error Handling",
                "PASS",
                "API returns 404 for non-existent endpoint",
                "API",
                "Low"
            )
        elif response.status_code == 405:
            reporter.log_test_result(
                "API Error Handling",
                "PASS",
                "API returns 405 for non-existent endpoint (method not allowed)",
                "API",
                "Low"
            )
        else:
            reporter.log_test_result(
                "API Error Handling",
                "BUG",
                f"API returns unexpected status code {response.status_code} for non-existent endpoint",
                "API",
                "Medium"
            )
        
        # Test invalid HTTP method
        try:
            api_url = urljoin(base_url, '/api')
            response = requests.post(api_url, timeout=10)
            
            if response.status_code in [405, 400, 422]:
                reporter.log_test_result(
                    "API Method Validation",
                    "PASS",
                    f"API returns appropriate status code {response.status_code} for invalid method",
                    "API",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "API Method Validation",
                    "BUG",
                    f"API returns unexpected status code {response.status_code} for invalid method",
                    "API",
                    "Medium"
                )
        except requests.exceptions.RequestException:
            pass
            
    except Exception as e:
        reporter.log_test_result(
            "API Error Handling",
            "FAIL",
            f"Error testing API error handling: {e}",
            "API",
            "High"
        )


def test_api_security(base_url: str, reporter, data_generator):
    """
    Test API security features
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        # Test for CORS headers
        api_url = urljoin(base_url, '/api')
        response = requests.get(api_url, timeout=10)
        
        cors_headers = ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods', 'Access-Control-Allow-Headers']
        cors_found = any(header in response.headers for header in cors_headers)
        
        if cors_found:
            reporter.log_test_result(
                "API CORS Headers",
                "PASS",
                "API includes CORS headers",
                "Security",
                "Low"
            )
        else:
            reporter.log_test_result(
                "API CORS Headers",
                "BUG",
                "API missing CORS headers",
                "Security",
                "Medium"
            )
        
        # Test for security headers
        security_headers = ['X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection']
        security_found = any(header in response.headers for header in security_headers)
        
        if security_found:
            reporter.log_test_result(
                "API Security Headers",
                "PASS",
                "API includes security headers",
                "Security",
                "Low"
            )
        else:
            reporter.log_test_result(
                "API Security Headers",
                "BUG",
                "API missing security headers",
                "Security",
                "Medium"
            )
        
        # Test for HTTPS
        if base_url.startswith('https://'):
            reporter.log_test_result(
                "API HTTPS",
                "PASS",
                "API uses HTTPS",
                "Security",
                "Low"
            )
        else:
            reporter.log_test_result(
                "API HTTPS",
                "BUG",
                "API doesn't use HTTPS",
                "Security",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "API Security",
            "FAIL",
            f"Error testing API security: {e}",
            "Security",
            "High"
        )


def test_api_performance(base_url: str, reporter):
    """
    Test API performance and response times
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        # Test response time for API endpoints
        api_endpoints = ['/api', '/api/v1', '/api/health', '/api/status']
        
        response_times = []
        
        for endpoint in api_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    break
                    
            except requests.exceptions.RequestException:
                continue
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            if avg_response_time < 2.0:  # Less than 2 seconds
                reporter.log_test_result(
                    "API Performance",
                    "PASS",
                    f"API response time is good. Average: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s",
                    "Performance",
                    "Low"
                )
            elif avg_response_time < 5.0:  # Less than 5 seconds
                reporter.log_test_result(
                    "API Performance",
                    "PASS",
                    f"API response time is acceptable. Average: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s",
                    "Performance",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "API Performance",
                    "BUG",
                    f"API response time is slow. Average: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s",
                    "Performance",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "API Performance",
                "PASS",
                "No API endpoints found to test performance",
                "Performance",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "API Performance",
            "FAIL",
            f"Error testing API performance: {e}",
            "Performance",
            "High"
        )


def test_api_authentication(base_url: str, reporter, data_generator):
    """
    Test API authentication and authorization
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        # Test protected endpoints without authentication
        protected_endpoints = ['/api/users', '/api/profile', '/api/admin']
        
        for endpoint in protected_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                response = requests.get(url, timeout=10)
                
                if response.status_code == 401:
                    reporter.log_test_result(
                        "API Authentication",
                        "PASS",
                        f"Protected endpoint {endpoint} requires authentication (401)",
                        "Security",
                        "Low"
                    )
                    break
                elif response.status_code == 403:
                    reporter.log_test_result(
                        "API Authentication",
                        "PASS",
                        f"Protected endpoint {endpoint} requires authorization (403)",
                        "Security",
                        "Low"
                    )
                    break
                elif response.status_code == 200:
                    reporter.log_test_result(
                        "API Authentication",
                        "BUG",
                        f"Protected endpoint {endpoint} allows access without authentication",
                        "Security",
                        "High"
                    )
                    break
                    
            except requests.exceptions.RequestException:
                continue
        else:
            reporter.log_test_result(
                "API Authentication",
                "PASS",
                "No protected endpoints found to test authentication",
                "Security",
                "Low"
            )
        
        # Test login endpoint
        login_endpoints = ['/api/login', '/api/auth/login', '/api/authenticate']
        
        for endpoint in login_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                
                # Test with invalid credentials
                invalid_data = data_generator.generate_login_data(valid=False)
                response = requests.post(url, json=invalid_data, timeout=10)
                
                if response.status_code == 401:
                    reporter.log_test_result(
                        "API Login Validation",
                        "PASS",
                        f"Login endpoint {endpoint} rejects invalid credentials (401)",
                        "Security",
                        "Low"
                    )
                    break
                elif response.status_code == 400:
                    reporter.log_test_result(
                        "API Login Validation",
                        "PASS",
                        f"Login endpoint {endpoint} validates input (400)",
                        "Security",
                        "Low"
                    )
                    break
                    
            except requests.exceptions.RequestException:
                continue
        else:
            reporter.log_test_result(
                "API Login Validation",
                "PASS",
                "No login endpoints found to test authentication",
                "Security",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "API Authentication",
            "FAIL",
            f"Error testing API authentication: {e}",
            "Security",
            "High"
        )


def test_api_data_validation(base_url: str, reporter, data_generator):
    """
    Test API data validation and input handling
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        # Test API endpoints that might accept POST data
        post_endpoints = ['/api/users', '/api/register', '/api/contact', '/api/feedback']
        
        for endpoint in post_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                
                # Test with invalid JSON
                invalid_json = data_generator.generate_api_test_data()['invalid_json']
                response = requests.post(url, json=invalid_json, timeout=10)
                
                if response.status_code in [400, 422]:
                    reporter.log_test_result(
                        "API Data Validation",
                        "PASS",
                        f"API endpoint {endpoint} validates input data (status {response.status_code})",
                        "API",
                        "Low"
                    )
                    break
                elif response.status_code == 405:
                    reporter.log_test_result(
                        "API Data Validation",
                        "PASS",
                        f"API endpoint {endpoint} doesn't accept POST (405)",
                        "API",
                        "Low"
                    )
                    break
                elif response.status_code == 200:
                    reporter.log_test_result(
                        "API Data Validation",
                        "BUG",
                        f"API endpoint {endpoint} accepts invalid data without validation",
                        "API",
                        "High"
                    )
                    break
                    
            except requests.exceptions.RequestException:
                continue
        else:
            reporter.log_test_result(
                "API Data Validation",
                "PASS",
                "No POST endpoints found to test data validation",
                "API",
                "Low"
            )
        
        # Test with malformed JSON
        try:
            api_url = urljoin(base_url, '/api')
            malformed_json = data_generator.generate_api_test_data()['malformed_json']
            response = requests.post(api_url, data=malformed_json, 
                                  headers={'Content-Type': 'application/json'}, timeout=10)
            
            if response.status_code in [400, 422]:
                reporter.log_test_result(
                    "API JSON Validation",
                    "PASS",
                    f"API validates malformed JSON (status {response.status_code})",
                    "API",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "API JSON Validation",
                    "BUG",
                    f"API doesn't properly validate malformed JSON (status {response.status_code})",
                    "API",
                    "Medium"
                )
        except requests.exceptions.RequestException:
            pass
            
    except Exception as e:
        reporter.log_test_result(
            "API Data Validation",
            "FAIL",
            f"Error testing API data validation: {e}",
            "API",
            "High"
        )
