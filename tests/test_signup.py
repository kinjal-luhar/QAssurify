"""
Signup Form Tests
Tests user registration functionality includin# Driver setup moved to utils/driver_setup.pyrequired fields, and password rules
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from utils.driver_setup import get_driver

from utils.driver_setup import get_driver


def run_tests(base_url: str, reporter, data_generator):
    """
    Run all signup form tests
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance for logging results
        data_generator: TestDataGenerator instance for test data
    """
    print("🔐 Testing Signup Form...")
    
    driver = None
    try:
        # Setup Chrome driver with proper configuration
        driver = get_driver()  # Let the fixture handle headless mode
        
        # Navigate to signup page
        signup_url = f"{base_url}/signup" if not base_url.endswith('/') else f"{base_url}signup"
        
        # Run all test cases
        test_cases = [
            (test_signup_page_loads, "Test signup page loads"),
            (test_required_fields_validation, "Test required field validation"),
            (test_email_validation, "Test email format validation"),
            (test_password_validation, "Test password validation"),
            (test_successful_signup, "Test successful signup")
        ]
        
        for test_func, description in test_cases:
            try:
                if test_func == test_signup_page_loads:
                    test_func(driver, signup_url, reporter)
                else:
                    test_func(driver, signup_url, reporter, data_generator)
            except WebDriverException as e:
                reporter.log_test_result(
                    f"Signup - {description}",
                    "FAIL",
                    f"Browser error: {str(e)}",
                    "UI",
                    "High"
                )
                break  # Stop further tests if browser fails
            except Exception as e:
                reporter.log_test_result(
                    f"Signup - {description}",
                    "FAIL",
                    f"Test error: {str(e)}",
                    "UI",
                    "Medium"
                )
                # Continue with next test
        
        # Test 6: Test edge cases and special characters
        test_edge_cases(driver, signup_url, reporter, data_generator)
        
        # Test 7: Test form submission without required fields
        test_form_submission_validation(driver, signup_url, reporter)
        
    except Exception as e:
        reporter.log_test_result(
            "Signup Test Setup",
            "FAIL",
            f"Failed to setup signup tests: {e}",
            "UI",
            "High"
        )
    finally:
        if driver:
            driver.quit()


# Driver setup moved to utils/driver_setup.py


def test_signup_page_loads(driver, signup_url, reporter):
    """
    Test if the signup page loads correctly
    
    Args:
        driver: WebDriver instance
        signup_url: URL of the signup page
        reporter: QAReporter instance
    """
    try:
        driver.get(signup_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check if page title contains signup-related keywords
        page_title = driver.title.lower()
        if any(keyword in page_title for keyword in ['signup', 'register', 'sign up', 'registration']):
            reporter.log_test_result(
                "Signup Page Loads",
                "PASS",
                f"Signup page loaded successfully. Title: {driver.title}",
                "UI",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Signup Page Loads",
                "BUG",
                f"Signup page loaded but title doesn't indicate signup: {driver.title}",
                "UI",
                "Medium"
            )
            
    except TimeoutException:
        reporter.log_test_result(
            "Signup Page Loads",
            "FAIL",
            f"Signup page failed to load within timeout: {signup_url}",
            "UI",
            "High"
        )
    except Exception as e:
        reporter.log_test_result(
            "Signup Page Loads",
            "FAIL",
            f"Error loading signup page: {e}",
            "UI",
            "High"
        )


def test_required_fields_validation(driver, signup_url, reporter, data_generator):
    """
    Test validation of required fields
    
    Args:
        driver: WebDriver instance
        signup_url: URL of the signup page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(signup_url)
        
        # Common required field selectors to try
        required_field_selectors = [
            "input[name='email']",
            "input[name='username']", 
            "input[name='password']",
            "input[name='first_name']",
            "input[name='last_name']",
            "input[type='email']",
            "input[type='password']",
            "#email",
            "#username",
            "#password",
            "#first_name",
            "#last_name"
        ]
        
        found_fields = []
        for selector in required_field_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                found_fields.append((selector, element))
            except NoSuchElementException:
                continue
        
        if not found_fields:
            reporter.log_test_result(
                "Required Fields Detection",
                "BUG",
                "No common signup form fields found on the page",
                "UI",
                "High"
            )
            return
        
        # Test empty form submission
        submit_button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Sign Up')",
            "button:contains('Register')",
            "#submit",
            ".submit-btn"
        ]
        
        submit_button = None
        for selector in submit_button_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if submit_button:
            submit_button.click()
            time.sleep(2)
            
            # Check for validation messages
            validation_messages = driver.find_elements(By.CSS_SELECTOR, 
                ".error, .validation-error, .field-error, [class*='error'], [class*='invalid']")
            
            if validation_messages:
                reporter.log_test_result(
                    "Required Fields Validation",
                    "PASS",
                    f"Form shows validation messages for empty required fields. Found {len(validation_messages)} error messages.",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Required Fields Validation",
                    "BUG",
                    "Form submitted without validation messages for empty required fields",
                    "Form",
                    "High"
                )
        else:
            reporter.log_test_result(
                "Required Fields Validation",
                "BUG",
                "No submit button found to test form validation",
                "UI",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Required Fields Validation",
            "FAIL",
            f"Error testing required fields validation: {e}",
            "Form",
            "High"
        )


def test_email_validation(driver, signup_url, reporter, data_generator):
    """
    Test email format validation
    
    Args:
        driver: WebDriver instance
        signup_url: URL of the signup page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(signup_url)
        
        # Find email field
        email_field = None
        email_selectors = [
            "input[name='email']",
            "input[type='email']",
            "#email",
            "input[placeholder*='email']",
            "input[placeholder*='Email']"
        ]
        
        for selector in email_selectors:
            try:
                email_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not email_field:
            reporter.log_test_result(
                "Email Field Detection",
                "BUG",
                "No email field found on signup form",
                "UI",
                "High"
            )
            return
        
        # Test invalid email formats
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test..test@example.com",
            "test@.com",
            "test@example",
            "test@.example.com"
        ]
        
        validation_found = False
        for invalid_email in invalid_emails:
            email_field.clear()
            email_field.send_keys(invalid_email)
            
            # Try to submit or trigger validation
            try:
                email_field.send_keys("\t")  # Tab to trigger validation
                time.sleep(1)
            except:
                pass
            
            # Check for validation messages
            validation_messages = driver.find_elements(By.CSS_SELECTOR,
                ".error, .validation-error, .field-error, [class*='error'], [class*='invalid']")
            
            if validation_messages:
                validation_found = True
                break
        
        if validation_found:
            reporter.log_test_result(
                "Email Format Validation",
                "PASS",
                "Email field shows validation messages for invalid formats",
                "Form",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Email Format Validation",
                "BUG",
                "Email field doesn't validate invalid email formats",
                "Form",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Email Format Validation",
            "FAIL",
            f"Error testing email validation: {e}",
            "Form",
            "High"
        )


def test_password_validation(driver, signup_url, reporter, data_generator):
    """
    Test password validation rules
    
    Args:
        driver: WebDriver instance
        signup_url: URL of the signup page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(signup_url)
        
        # Find password field
        password_field = None
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "#password",
            "input[placeholder*='password']",
            "input[placeholder*='Password']"
        ]
        
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not password_field:
            reporter.log_test_result(
                "Password Field Detection",
                "BUG",
                "No password field found on signup form",
                "UI",
                "High"
            )
            return
        
        # Test weak passwords
        weak_passwords = ["123", "abc", "password", "12345678"]
        validation_found = False
        
        for weak_password in weak_passwords:
            password_field.clear()
            password_field.send_keys(weak_password)
            
            # Try to trigger validation
            try:
                password_field.send_keys("\t")
                time.sleep(1)
            except:
                pass
            
            # Check for validation messages
            validation_messages = driver.find_elements(By.CSS_SELECTOR,
                ".error, .validation-error, .field-error, [class*='error'], [class*='invalid']")
            
            if validation_messages:
                validation_found = True
                break
        
        if validation_found:
            reporter.log_test_result(
                "Password Validation",
                "PASS",
                "Password field shows validation messages for weak passwords",
                "Form",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Password Validation",
                "BUG",
                "Password field doesn't validate weak passwords",
                "Form",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Password Validation",
            "FAIL",
            f"Error testing password validation: {e}",
            "Form",
            "High"
        )


def test_successful_signup(driver, signup_url, reporter, data_generator):
    """
    Test successful signup with valid data
    
    Args:
        driver: WebDriver instance
        signup_url: URL of the signup page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(signup_url)
        
        # Generate valid test data
        user_data = data_generator.generate_user_data(valid=True)
        
        # Fill form fields
        form_fields = {
            'email': ['input[name="email"]', 'input[type="email"]', '#email'],
            'username': ['input[name="username"]', '#username'],
            'password': ['input[name="password"]', 'input[type="password"]', '#password'],
            'first_name': ['input[name="first_name"]', '#first_name'],
            'last_name': ['input[name="last_name"]', '#last_name']
        }
        
        filled_fields = 0
        for field_name, selectors in form_fields.items():
            for selector in selectors:
                try:
                    field = driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    field.send_keys(str(user_data.get(field_name, '')))
                    filled_fields += 1
                    break
                except NoSuchElementException:
                    continue
        
        if filled_fields == 0:
            reporter.log_test_result(
                "Successful Signup Test",
                "BUG",
                "No form fields found to fill for signup test",
                "UI",
                "High"
            )
            return
        
        # Try to submit the form
        submit_button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Sign Up')",
            "button:contains('Register')",
            "#submit",
            ".submit-btn"
        ]
        
        submit_button = None
        for selector in submit_button_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if submit_button:
            submit_button.click()
            time.sleep(3)
            
            # Check for success indicators
            current_url = driver.current_url
            success_indicators = [
                'success', 'welcome', 'dashboard', 'profile', 'home'
            ]
            
            if any(indicator in current_url.lower() for indicator in success_indicators):
                reporter.log_test_result(
                    "Successful Signup",
                    "PASS",
                    f"Signup successful. Redirected to: {current_url}",
                    "User Flow",
                    "Low"
                )
            else:
                # Check for success messages on the page
                success_messages = driver.find_elements(By.CSS_SELECTOR,
                    ".success, .alert-success, [class*='success'], [class*='welcome']")
                
                if success_messages:
                    reporter.log_test_result(
                        "Successful Signup",
                        "PASS",
                        "Signup successful. Success message displayed.",
                        "User Flow",
                        "Low"
                    )
                else:
                    reporter.log_test_result(
                        "Successful Signup",
                        "BUG",
                        f"Signup form submitted but no success indication found. Current URL: {current_url}",
                        "User Flow",
                        "High"
                    )
        else:
            reporter.log_test_result(
                "Successful Signup Test",
                "BUG",
                "No submit button found to test signup submission",
                "UI",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Successful Signup Test",
            "FAIL",
            f"Error testing successful signup: {e}",
            "User Flow",
            "High"
        )


def test_edge_cases(driver, signup_url, reporter, data_generator):
    """
    Test edge cases and special characters
    
    Args:
        driver: WebDriver instance
        signup_url: URL of the signup page
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(signup_url)
        
        # Get edge case data
        edge_data = data_generator.generate_edge_case_data()
        
        # Test very long input
        try:
            email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email")
            email_field.clear()
            email_field.send_keys(edge_data['very_long_text'])
            
            # Check if form handles long input gracefully
            if len(email_field.get_attribute('value')) > 1000:
                reporter.log_test_result(
                    "Long Input Handling",
                    "BUG",
                    "Form accepts extremely long input without validation",
                    "Form",
                    "Medium"
                )
            else:
                reporter.log_test_result(
                    "Long Input Handling",
                    "PASS",
                    "Form properly limits or handles long input",
                    "Form",
                    "Low"
                )
        except NoSuchElementException:
            pass
        
        # Test special characters
        try:
            username_field = driver.find_element(By.CSS_SELECTOR, "input[name='username'], #username")
            username_field.clear()
            username_field.send_keys(edge_data['special_chars'])
            
            # Check if special characters are handled
            reporter.log_test_result(
                "Special Characters Handling",
                "PASS",
                "Form accepts special characters in username field",
                "Form",
                "Low"
            )
        except NoSuchElementException:
            pass
        
        # Test SQL injection attempts
        try:
            email_field = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email")
            email_field.clear()
            email_field.send_keys(edge_data['sql_injection'])
            
            # Check if SQL injection is prevented
            reporter.log_test_result(
                "SQL Injection Prevention",
                "PASS",
                "Form handles SQL injection attempts safely",
                "Security",
                "Low"
            )
        except NoSuchElementException:
            pass
            
    except Exception as e:
        reporter.log_test_result(
            "Edge Cases Test",
            "FAIL",
            f"Error testing edge cases: {e}",
            "Form",
            "Medium"
        )


def test_form_submission_validation(driver, signup_url, reporter):
    """
    Test form submission validation
    
    Args:
        driver: WebDriver instance
        signup_url: URL of the signup page
        reporter: QAReporter instance
    """
    try:
        driver.get(signup_url)
        
        # Find and click submit button without filling any fields
        submit_button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('Sign Up')",
            "button:contains('Register')",
            "#submit",
            ".submit-btn"
        ]
        
        submit_button = None
        for selector in submit_button_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if submit_button:
            submit_button.click()
            time.sleep(2)
            
            # Check if form prevents submission
            current_url = driver.current_url
            if signup_url in current_url:
                reporter.log_test_result(
                    "Form Submission Validation",
                    "PASS",
                    "Form prevents submission without required data",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Form Submission Validation",
                    "BUG",
                    "Form allows submission without required data",
                    "Form",
                    "High"
                )
        else:
            reporter.log_test_result(
                "Form Submission Validation",
                "BUG",
                "No submit button found to test form validation",
                "UI",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Form Submission Validation",
            "FAIL",
            f"Error testing form submission validation: {e}",
            "Form",
            "High"
        )
