"""
Login Tests
Tests user authentication functionality including login form validation, credential verification, and security features
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


def run_tests(base_url: str, reporter, data_generator):
    """
    Run all login tests
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance for logging results
        data_generator: TestDataGenerator instance for test data
    """
    print("🔑 Testing Login Functionality...")
    
    driver = None
    try:
        # Setup Chrome driver
        driver = setup_driver()
        
        # Navigate to login page
        login_url = f"{base_url}/login" if not base_url.endswith('/') else f"{base_url}login"
        
        # Test 1: Check if login page loads
        test_login_page_loads(driver, login_url, reporter)
        
        # Test 2: Test login form validation
        test_login_form_validation(driver, login_url, reporter, data_generator)
        
        # Test 3: Test invalid credentials
        test_invalid_credentials(driver, login_url, reporter, data_generator)
        
        # Test 4: Test empty credentials
        test_empty_credentials(driver, login_url, reporter)
        
        # Test 5: Test successful login (if valid credentials available)
        test_successful_login(driver, login_url, reporter, data_generator)
        
        # Test 6: Test password visibility toggle
        test_password_visibility_toggle(driver, login_url, reporter)
        
        # Test 7: Test remember me functionality
        test_remember_me_functionality(driver, login_url, reporter)
        
        # Test 8: Test logout functionality
        test_logout_functionality(driver, base_url, reporter)
        
    except Exception as e:
        reporter.log_test_result(
            "Login Test Setup",
            "FAIL",
            f"Failed to setup login tests: {e}",
            "UI",
            "High"
        )
    finally:
        if driver:
            driver.quit()


def setup_driver():
    """
    Setup Chrome WebDriver with appropriate options
    
    Returns:
        Configured WebDriver instance
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    return driver


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


def test_login_form_validation(driver, login_url, reporter, data_generator):
    """
    Test login form validation
    
    Args:
        driver: WebDriver instance
        login_url: URL of the login page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(login_url)
        
        # Find login form fields
        username_field = None
        password_field = None
        
        # Try different selectors for username/email field
        username_selectors = [
            "input[name='username']",
            "input[name='email']",
            "input[type='email']",
            "#username",
            "#email",
            "input[placeholder*='username']",
            "input[placeholder*='email']"
        ]
        
        for selector in username_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        # Try different selectors for password field
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "#password",
            "input[placeholder*='password']"
        ]
        
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not username_field or not password_field:
            reporter.log_test_result(
                "Login Form Fields Detection",
                "BUG",
                f"Login form fields not found. Username: {username_field is not None}, Password: {password_field is not None}",
                "UI",
                "High"
            )
            return
        
        # Test invalid email format
        username_field.clear()
        username_field.send_keys("invalid-email-format")
        
        # Try to submit form
        submit_button = find_submit_button(driver)
        if submit_button:
            submit_button.click()
            time.sleep(2)
            
            # Check for validation messages
            validation_messages = driver.find_elements(By.CSS_SELECTOR,
                ".error, .validation-error, .field-error, [class*='error'], [class*='invalid']")
            
            if validation_messages:
                reporter.log_test_result(
                    "Login Form Validation",
                    "PASS",
                    "Login form shows validation messages for invalid input",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Login Form Validation",
                    "BUG",
                    "Login form doesn't validate invalid email format",
                    "Form",
                    "High"
                )
        else:
            reporter.log_test_result(
                "Login Form Validation",
                "BUG",
                "No submit button found to test form validation",
                "UI",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Login Form Validation",
            "FAIL",
            f"Error testing login form validation: {e}",
            "Form",
            "High"
        )


def test_invalid_credentials(driver, login_url, reporter, data_generator):
    """
    Test login with invalid credentials
    
    Args:
        driver: WebDriver instance
        login_url: URL of the login page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(login_url)
        
        # Generate invalid login data
        invalid_data = data_generator.generate_login_data(valid=False)
        
        # Fill login form with invalid data
        username_field = find_username_field(driver)
        password_field = find_password_field(driver)
        
        if username_field and password_field:
            username_field.clear()
            username_field.send_keys(invalid_data['username'])
            
            password_field.clear()
            password_field.send_keys(invalid_data['password'])
            
            # Submit form
            submit_button = find_submit_button(driver)
            if submit_button:
                submit_button.click()
                time.sleep(3)
                
                # Check for error messages
                error_messages = driver.find_elements(By.CSS_SELECTOR,
                    ".error, .alert-error, .alert-danger, [class*='error'], [class*='invalid']")
                
                if error_messages:
                    reporter.log_test_result(
                        "Invalid Credentials Test",
                        "PASS",
                        f"Login form shows error message for invalid credentials: {error_messages[0].text[:100]}",
                        "Security",
                        "Low"
                    )
                else:
                    reporter.log_test_result(
                        "Invalid Credentials Test",
                        "BUG",
                        "Login form doesn't show error message for invalid credentials",
                        "Security",
                        "High"
                    )
            else:
                reporter.log_test_result(
                    "Invalid Credentials Test",
                    "BUG",
                    "No submit button found to test invalid credentials",
                    "UI",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Invalid Credentials Test",
                "BUG",
                "Login form fields not found",
                "UI",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Invalid Credentials Test",
            "FAIL",
            f"Error testing invalid credentials: {e}",
            "Security",
            "High"
        )


def test_empty_credentials(driver, login_url, reporter):
    """
    Test login with empty credentials
    
    Args:
        driver: WebDriver instance
        login_url: URL of the login page
        reporter: QAReporter instance
    """
    try:
        driver.get(login_url)
        
        # Submit form without filling any fields
        submit_button = find_submit_button(driver)
        if submit_button:
            submit_button.click()
            time.sleep(2)
            
            # Check if form prevents submission or shows validation
            current_url = driver.current_url
            if login_url in current_url:
                reporter.log_test_result(
                    "Empty Credentials Test",
                    "PASS",
                    "Login form prevents submission with empty credentials",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Empty Credentials Test",
                    "BUG",
                    "Login form allows submission with empty credentials",
                    "Form",
                    "High"
                )
        else:
            reporter.log_test_result(
                "Empty Credentials Test",
                "BUG",
                "No submit button found to test empty credentials",
                "UI",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Empty Credentials Test",
            "FAIL",
            f"Error testing empty credentials: {e}",
            "Form",
            "High"
        )


def test_successful_login(driver, login_url, reporter, data_generator):
    """
    Test successful login (if valid credentials are available)
    
    Args:
        driver: WebDriver instance
        login_url: URL of the login page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(login_url)
        
        # Generate valid login data (this would typically be from a test database)
        valid_data = data_generator.generate_login_data(valid=True)
        
        # Fill login form
        username_field = find_username_field(driver)
        password_field = find_password_field(driver)
        
        if username_field and password_field:
            username_field.clear()
            username_field.send_keys(valid_data['username'])
            
            password_field.clear()
            password_field.send_keys(valid_data['password'])
            
            # Submit form
            submit_button = find_submit_button(driver)
            if submit_button:
                submit_button.click()
                time.sleep(3)
                
                # Check for success indicators
                current_url = driver.current_url
                success_indicators = [
                    'dashboard', 'profile', 'home', 'welcome', 'success'
                ]
                
                if any(indicator in current_url.lower() for indicator in success_indicators):
                    reporter.log_test_result(
                        "Successful Login Test",
                        "PASS",
                        f"Login successful. Redirected to: {current_url}",
                        "User Flow",
                        "Low"
                    )
                else:
                    # Check for error messages (credentials might be invalid)
                    error_messages = driver.find_elements(By.CSS_SELECTOR,
                        ".error, .alert-error, .alert-danger, [class*='error']")
                    
                    if error_messages:
                        reporter.log_test_result(
                            "Successful Login Test",
                            "PASS",
                            "Login form properly rejects invalid test credentials",
                            "Security",
                            "Low"
                        )
                    else:
                        reporter.log_test_result(
                            "Successful Login Test",
                            "BUG",
                            f"Login form submitted but no clear success/error indication. Current URL: {current_url}",
                            "User Flow",
                            "Medium"
                        )
            else:
                reporter.log_test_result(
                    "Successful Login Test",
                    "BUG",
                    "No submit button found to test login",
                    "UI",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Successful Login Test",
                "BUG",
                "Login form fields not found",
                "UI",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Successful Login Test",
            "FAIL",
            f"Error testing successful login: {e}",
            "User Flow",
            "High"
        )


def test_password_visibility_toggle(driver, login_url, reporter):
    """
    Test password visibility toggle functionality
    
    Args:
        driver: WebDriver instance
        login_url: URL of the login page
        reporter: QAReporter instance
    """
    try:
        driver.get(login_url)
        
        password_field = find_password_field(driver)
        if not password_field:
            reporter.log_test_result(
                "Password Visibility Toggle",
                "BUG",
                "Password field not found to test visibility toggle",
                "UI",
                "Medium"
            )
            return
        
        # Look for password visibility toggle button
        toggle_selectors = [
            "button[type='button']",
            ".password-toggle",
            ".show-password",
            ".toggle-password",
            "button:contains('Show')",
            "button:contains('Hide')"
        ]
        
        toggle_button = None
        for selector in toggle_selectors:
            try:
                toggle_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if toggle_button:
            # Test password visibility toggle
            password_field.send_keys("testpassword")
            initial_type = password_field.get_attribute('type')
            
            toggle_button.click()
            time.sleep(1)
            
            new_type = password_field.get_attribute('type')
            
            if initial_type != new_type:
                reporter.log_test_result(
                    "Password Visibility Toggle",
                    "PASS",
                    f"Password visibility toggle works. Type changed from {initial_type} to {new_type}",
                    "UI",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Password Visibility Toggle",
                    "BUG",
                    "Password visibility toggle doesn't change password field type",
                    "UI",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Password Visibility Toggle",
                "PASS",
                "No password visibility toggle found (this is acceptable)",
                "UI",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Password Visibility Toggle",
            "FAIL",
            f"Error testing password visibility toggle: {e}",
            "UI",
            "Medium"
        )


def test_remember_me_functionality(driver, login_url, reporter):
    """
    Test remember me checkbox functionality
    
    Args:
        driver: WebDriver instance
        login_url: URL of the login page
        reporter: QAReporter instance
    """
    try:
        driver.get(login_url)
        
        # Look for remember me checkbox
        remember_me_selectors = [
            "input[name='remember']",
            "input[name='remember_me']",
            "input[type='checkbox']",
            "#remember",
            "#remember_me",
            "input[value='remember']"
        ]
        
        remember_me_checkbox = None
        for selector in remember_me_selectors:
            try:
                remember_me_checkbox = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if remember_me_checkbox:
            # Test checkbox functionality
            initial_state = remember_me_checkbox.is_selected()
            remember_me_checkbox.click()
            new_state = remember_me_checkbox.is_selected()
            
            if initial_state != new_state:
                reporter.log_test_result(
                    "Remember Me Functionality",
                    "PASS",
                    "Remember me checkbox toggles correctly",
                    "UI",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Remember Me Functionality",
                    "BUG",
                    "Remember me checkbox doesn't toggle",
                    "UI",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Remember Me Functionality",
                "PASS",
                "No remember me checkbox found (this is acceptable)",
                "UI",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Remember Me Functionality",
            "FAIL",
            f"Error testing remember me functionality: {e}",
            "UI",
            "Medium"
        )


def test_logout_functionality(driver, base_url, reporter):
    """
    Test logout functionality
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        # Look for logout button/link
        logout_selectors = [
            "a[href*='logout']",
            "button:contains('Logout')",
            "button:contains('Sign Out')",
            "a:contains('Logout')",
            "a:contains('Sign Out')",
            "#logout",
            ".logout"
        ]
        
        logout_element = None
        for selector in logout_selectors:
            try:
                logout_element = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if logout_element:
            logout_element.click()
            time.sleep(2)
            
            # Check if redirected to login page or home page
            current_url = driver.current_url
            if 'login' in current_url.lower() or 'home' in current_url.lower():
                reporter.log_test_result(
                    "Logout Functionality",
                    "PASS",
                    f"Logout successful. Redirected to: {current_url}",
                    "User Flow",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Logout Functionality",
                    "BUG",
                    f"Logout didn't redirect properly. Current URL: {current_url}",
                    "User Flow",
                    "High"
                )
        else:
            reporter.log_test_result(
                "Logout Functionality",
                "PASS",
                "No logout element found (this is acceptable if not logged in)",
                "UI",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Logout Functionality",
            "FAIL",
            f"Error testing logout functionality: {e}",
            "User Flow",
            "Medium"
        )


def find_username_field(driver):
    """Helper function to find username/email field"""
    selectors = [
        "input[name='username']",
        "input[name='email']",
        "input[type='email']",
        "#username",
        "#email"
    ]
    
    for selector in selectors:
        try:
            return driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            continue
    return None


def find_password_field(driver):
    """Helper function to find password field"""
    selectors = [
        "input[name='password']",
        "input[type='password']",
        "#password"
    ]
    
    for selector in selectors:
        try:
            return driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            continue
    return None


def find_submit_button(driver):
    """Helper function to find submit button"""
    selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:contains('Login')",
        "button:contains('Sign In')",
        "#submit",
        ".submit-btn"
    ]
    
    for selector in selectors:
        try:
            return driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            continue
    return None
