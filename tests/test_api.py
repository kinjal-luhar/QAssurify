"""
Ultra-light smoke test for API health check.
Only tests a single endpoint for 200 status.
Runtime: ~1-2s
"""

import requests
from typing import Dict, Any, Tuple

def test_api_health(base_url: str, test_options: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if a single API endpoint is reachable."""
    # Hardcode single endpoint for ultra-fast smoke test
    endpoint = "/api/users"  # Adjust this to match your API
    
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=3)
        
        # Only check for 200 status in smoke test
        if response.status_code == 200:
            return True, f"API endpoint {endpoint} is reachable"
        else:
            return False, f"API endpoint {endpoint} returned status {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return False, f"API request failed: {str(e)}"

def run_tests(base_url: str, reporter, test_options=None):
    """
    Run ultra-light API smoke test
    
    Args:
        base_url: Base URL of the API
        reporter: QAReporter instance for logging results
        test_options: Dictionary of test options for smoke test configuration
    """
    print("🔥 Running Ultra-Light API Smoke Test...")
    
    # Single test: Check if API endpoint responds
    success, message = test_api_health(base_url, test_options or {})
    reporter.add_result("API Health Check", success, message)