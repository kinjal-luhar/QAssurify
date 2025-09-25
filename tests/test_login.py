"""
Login Tests
Tests user authentication functionality including login form validation, credential verification, and security features
Supports both smoke test mode (quick validation) and full regression mode
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from utils.driver_setup import get_driver


def test_login_page_loads(driver, base_url, reporter, wait):
    """Core smoke test: Verify login page loads with required elements"""
    try:
        driver.get(base_url)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "user-name")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
        
        reporter.log_test_result(
            "Login Page Load",
            "PASS",
            "Login page loads with all required elements",
            "Login",
            "High"
        )
        return username_field, password_field, login_button
    except Exception as e:
        reporter.log_test_result(
            "Login Page Load",
            "FAIL",
            f"Login page failed to load: {str(e)}",
            "Login",
            "High"
        )
        return None

def test_valid_login(driver, base_url, reporter, wait, form_elements=None):
    """Core smoke test: Verify login works with valid credentials"""
    try:
        if not form_elements:
            form_elements = test_login_page_loads(driver, base_url, reporter, wait)
        if not form_elements:
            return False
            
        username_field, password_field, login_button = form_elements
        username_field.send_keys("standard_user")
        password_field.send_keys("secret_sauce")
        login_button.click()
        
        # Verify successful login
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "inventory_list")))
        
        reporter.log_test_result(
            "Valid Login",
            "PASS",
            "Successfully logged in with valid credentials",
            "Login",
            "High"
        )
        return True
    except Exception as e:
        reporter.log_test_result(
            "Valid Login",
            "FAIL",
            f"Valid login test failed: {str(e)}",
            "Login",
            "High"
        )
        return False

def test_empty_credentials(driver, base_url, reporter, wait):
    """Test login attempt with empty credentials (non-smoke)"""
    try:
        form_elements = test_login_page_loads(driver, base_url, reporter, wait)
        if not form_elements:
            return
        
        _, _, login_button = form_elements
        login_button.click()
        
        # Check for error message
        error = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message")))
        
        reporter.log_test_result(
            "Empty Credentials",
            "PASS",
            "Empty credentials properly rejected",
            "Login",
            "Medium"
        )
    except Exception as e:
        reporter.log_test_result(
            "Empty Credentials",
            "FAIL",
            f"Empty credentials test failed: {str(e)}",
            "Login",
            "Medium"
        )

def test_invalid_credentials(driver, base_url, reporter, wait):
    """Test invalid login scenarios (non-smoke)"""
    invalid_tests = [
        ("invalid_user", "invalid_pass", "Invalid username/password"),
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("locked_out_user", "secret_sauce", "User is locked out"),
    ]
    
    for username, password, expected_message in invalid_tests:
        try:
            form_elements = test_login_page_loads(driver, base_url, reporter, wait)
            if not form_elements:
                continue
                
            username_field, password_field, login_button = form_elements
            username_field.send_keys(username)
            password_field.send_keys(password)
            login_button.click()
            
            error = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message")))
            
            reporter.log_test_result(
                f"Invalid Login - {username or 'empty'}",
                "PASS",
                f"Invalid credentials properly rejected: {expected_message}",
                "Login",
                "Medium"
            )
        except Exception as e:
            reporter.log_test_result(
                f"Invalid Login - {username or 'empty'}",
                "FAIL",
                f"Invalid credentials test failed: {str(e)}",
                "Login",
                "Medium"
            )

def test_session_handling(driver, base_url, reporter, wait):
    """Test session management and logout (non-smoke)"""
    try:
        if not test_valid_login(driver, base_url, reporter, wait):
            return
            
        # Find and click logout
        logout = wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        logout.click()
        
        # Verify back at login page
        wait.until(EC.presence_of_element_located((By.ID, "login-button")))
        
        reporter.log_test_result(
            "Session Management",
            "PASS",
            "Logout functionality works correctly",
            "Login",
            "Medium"
        )
    except Exception as e:
        reporter.log_test_result(
            "Session Management",
            "FAIL",
            f"Session management test failed: {str(e)}",
            "Login",
            "Medium"
        )

def run_tests(base_url: str, reporter, data_generator, **options):
    """
    Run login test suite with configurable test levels
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance for logging results
        data_generator: TestDataGenerator instance
        options: Test configuration options including:
            - skip_validation: Skip extensive form validation
            - skip_edge_cases: Skip edge cases
            - quick_mode: Run minimal test set for smoke tests
    """
    print("🔑 Testing Login Functionality...")
    
    # Extract test options
    skip_validation = options.get('skip_validation', False)
    skip_edge_cases = options.get('skip_edge_cases', False)
    quick_mode = options.get('quick_mode', False)
    
    driver = None
    try:
        driver = get_driver(headless=True)
        wait = WebDriverWait(driver, 5 if quick_mode else 10)  # Shorter timeouts in smoke mode
        
        # Core smoke tests - always run these
        form_elements = test_login_page_loads(driver, base_url, reporter, wait)
        if not form_elements:
            return  # Stop if login page doesn't load
            
        if not test_valid_login(driver, base_url, reporter, wait, form_elements):
            return  # Stop if basic login fails
            
        # Additional tests based on mode
        if not quick_mode:
            test_empty_credentials(driver, base_url, reporter, wait)
            
        if not skip_edge_cases:
            test_invalid_credentials(driver, base_url, reporter, wait)
            
        if not skip_validation:
            test_session_handling(driver, base_url, reporter, wait)
            
    finally:
        if driver:
            driver.quit()


# Remove the setup_driver function as we'll use get_driver directly

def find_saucedemo_element(driver, element_id, wait_timeout=10):
    """
    Helper function to find SauceDemo elements with proper waiting
    
    Args:
        driver: WebDriver instance
        element_id: The ID of the element to find
        wait_timeout: How long to wait for element (seconds)
        
    Returns:
        The found element or None if not found
    """
    try:
        wait = WebDriverWait(driver, wait_timeout)
        return wait.until(
            EC.presence_of_element_located((By.ID, element_id))
        )
    except TimeoutException:
        return None
    except Exception:
        return None
