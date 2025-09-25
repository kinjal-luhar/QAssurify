"""
Login Tests
Tests user authentication functionality including login form validation, credential verification, and security features
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from utils.driver_setup import get_driver


def run_tests(base_url: str, reporter, data_generator):
    """
    Run login tests for SauceDemo
    
    Args:
        base_url: Base URL of the web application (should be https://www.saucedemo.com)
        reporter: QAReporter instance for logging results
        data_generator: TestDataGenerator instance (not used as we use fixed credentials)
    """
    print("🔑 Testing SauceDemo Login Functionality...")
    
    driver = None
    try:
        # Setup Chrome driver with proper configuration
        driver = get_driver(headless=True)
        wait = WebDriverWait(driver, 10)
        
        # Test empty credentials first
        test_empty_credentials(driver, base_url, reporter, wait)
        
        # Test invalid credentials
        test_invalid_credentials(driver, base_url, reporter, wait)
        
        # Test successful login with valid credentials
        try:
            driver.get(base_url)
            
            # Wait for and fill in login form
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "user-name"))
            )
            password_field = wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            login_button = wait.until(
                EC.element_to_be_clickable((By.ID, "login-button"))
            )
            
            username_field.send_keys("standard_user")
            password_field.send_keys("secret_sauce")
            login_button.click()
            
            # Verify successful login
            inventory_list = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
            )
            
            reporter.log_test_result(
                "SauceDemo Login Test",
                "PASS",
                "Successfully logged in with standard_user credentials",
                "Authentication",
                "Low"
            )
            
            # Test logout functionality
            menu_button = wait.until(
                EC.element_to_be_clickable((By.ID, "react-burger-menu-btn"))
            )
            menu_button.click()
            
            logout_link = wait.until(
                EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))
            )
            logout_link.click()
            
            # Verify we're back at login page
            wait.until(
                EC.presence_of_element_located((By.ID, "user-name"))
            )
            
            reporter.log_test_result(
                "SauceDemo Logout Test",
                "PASS",
                "Successfully logged out and returned to login page",
                "Authentication",
                "Low"
            )
            
        except TimeoutException as e:
            reporter.log_test_result(
                "SauceDemo Login Test",
                "FAIL",
                f"Login failed - timeout waiting for elements: {str(e)}",
                "Authentication",
                "High"
            )
        except Exception as e:
            reporter.log_test_result(
                "SauceDemo Login Test",
                "FAIL",
                f"Login failed with unexpected error: {str(e)}",
                "Authentication",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "SauceDemo Login Test Setup",
            "FAIL",
            f"Failed to setup or run login tests: {e}",
            "UI",
            "High"
        )
    finally:
        if driver:
            driver.quit()


# Remove the setup_driver function as we'll use get_driver directly


def test_login_page_loads(driver, login_url, reporter):
    """
    Test if the login page loads correctly
    
    Args:
        driver: WebDriver instance
        login_url: URL of the login page
        reporter: QAReporter instance
    """
    try:
        driver.get(login_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check if page title contains login-related keywords
        page_title = driver.title.lower()
        if any(keyword in page_title for keyword in ['login', 'sign in', 'signin', 'authentication']):
            reporter.log_test_result(
                "Login Page Loads",
                "PASS",
                f"Login page loaded successfully. Title: {driver.title}",
                "UI",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Login Page Loads",
                "BUG",
                f"Login page loaded but title doesn't indicate login: {driver.title}",
                "UI",
                "Medium"
            )
            
    except TimeoutException:
        reporter.log_test_result(
            "Login Page Loads",
            "FAIL",
            f"Login page failed to load within timeout: {login_url}",
            "UI",
            "High"
        )
    except Exception as e:
        reporter.log_test_result(
            "Login Page Loads",
            "FAIL",
            f"Error loading login page: {e}",
            "UI",
            "High"
        )


def test_invalid_credentials(driver, base_url, reporter, wait):
    """Test login with invalid credentials for SauceDemo"""
    try:
        driver.get(base_url)
        
        # Get form elements
        username_field = wait.until(EC.presence_of_element_located((By.ID, "user-name")))
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "login-button")
        
        # Try invalid credentials
        username_field.send_keys("wrong_user")
        password_field.send_keys("wrong_pass")
        login_button.click()
        
        # Check for error message
        error_message = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='error']"))
        )
        
        if error_message and error_message.is_displayed():
            reporter.log_test_result(
                "SauceDemo Invalid Login",
                "PASS",
                f"Login correctly rejected invalid credentials: {error_message.text}",
                "Security",
                "Low"
            )
        else:
            reporter.log_test_result(
                "SauceDemo Invalid Login",
                "FAIL",
                "No error message shown for invalid credentials",
                "Security",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "SauceDemo Invalid Login",
            "FAIL",
            f"Error testing invalid credentials: {e}",
            "Security",
            "High"
        )


def test_empty_credentials(driver, base_url, reporter, wait):
    """Test login with empty credentials for SauceDemo"""
    try:
        driver.get(base_url)
        
        # Get login button and click without entering credentials
        login_button = wait.until(
            EC.presence_of_element_located((By.ID, "login-button"))
        )
        login_button.click()
        
        # Check for error message
        error_message = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='error']"))
        )
        
        if error_message and "Username is required" in error_message.text:
            reporter.log_test_result(
                "SauceDemo Empty Login",
                "PASS",
                "Login correctly requires username field",
                "Form",
                "Low"
            )
        else:
            reporter.log_test_result(
                "SauceDemo Empty Login",
                "FAIL",
                "No validation message for empty credentials",
                "Form",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "SauceDemo Empty Login",
            "FAIL",
            f"Error testing empty credentials: {e}",
            "Form",
            "High"
        )


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
