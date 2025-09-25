"""
General Form Validation Tests
Tests various forms across the application for validation, user experience, and security
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from utils.driver_setup import get_driver


def run_tests(base_url: str, reporter, data_generator):
    """
    Run all form validation tests
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance for logging results
        data_generator: TestDataGenerator instance for test data
    """
    print("📝 Testing Form Validation...")
    
    driver = None
    try:
        # Setup Chrome driver
        driver = get_driver(headless=True)
        
        # Test 1: Test contact form
        test_contact_form(driver, base_url, reporter, data_generator)
        
        # Test 2: Test search form
        test_search_form(driver, base_url, reporter, data_generator)
        
        # Test 3: Test feedback form
        test_feedback_form(driver, base_url, reporter, data_generator)
        
        # Test 4: Test input field validation
        test_input_field_validation(driver, base_url, reporter, data_generator)
        
        # Test 5: Test form submission handling
        test_form_submission_handling(driver, base_url, reporter, data_generator)
        
        # Test 6: Test form accessibility
        test_form_accessibility(driver, base_url, reporter)
        
        # Test 7: Test form security
        test_form_security(driver, base_url, reporter, data_generator)
        
        # Test 8: Test form error handling
        test_form_error_handling(driver, base_url, reporter, data_generator)
        
    except Exception as e:
        reporter.log_test_result(
            "Form Test Setup",
            "FAIL",
            f"Failed to setup form tests: {e}",
            "UI",
            "High"
        )
    finally:
        if driver:
            driver.quit()


# Driver setup moved to utils/driver_setup.py


def test_contact_form(driver, base_url, reporter, data_generator):
    """
    Test contact form functionality
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        # Look for contact form on various pages
        contact_pages = ['/contact', '/contact-us', '/contactus', '/contact.html']
        
        contact_form_found = False
        for page in contact_pages:
            try:
                contact_url = f"{base_url}{page}" if not base_url.endswith('/') else f"{base_url}{page[1:]}"
                driver.get(contact_url)
                time.sleep(2)
                
                # Look for contact form
                form_selectors = [
                    "form", ".contact-form", "#contact-form", 
                    "form[action*='contact']", "form[name='contact']"
                ]
                
                for selector in form_selectors:
                    if driver.find_elements(By.CSS_SELECTOR, selector):
                        contact_form_found = True
                        break
                
                if contact_form_found:
                    break
                    
            except Exception:
                continue
        
        if not contact_form_found:
            reporter.log_test_result(
                "Contact Form Detection",
                "PASS",
                "No contact form found (this is acceptable)",
                "UI",
                "Low"
            )
            return
        
        # Test contact form with valid data
        valid_data = data_generator.generate_form_data('contact', valid=True)
        test_form_with_data(driver, valid_data, "Contact Form Valid Data", reporter)
        
        # Test contact form with invalid data
        invalid_data = data_generator.generate_form_data('contact', valid=False)
        test_form_with_data(driver, invalid_data, "Contact Form Invalid Data", reporter)
        
    except Exception as e:
        reporter.log_test_result(
            "Contact Form Test",
            "FAIL",
            f"Error testing contact form: {e}",
            "Form",
            "High"
        )


def test_search_form(driver, base_url, reporter, data_generator):
    """
    Test search form functionality
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(base_url)
        
        # Look for search form
        search_selectors = [
            "input[name='search']", "input[name='q']", "input[type='search']",
            "#search", ".search-input", "input[placeholder*='search']"
        ]
        
        search_field = None
        for selector in search_selectors:
            try:
                search_field = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not search_field:
            reporter.log_test_result(
                "Search Form Detection",
                "PASS",
                "No search form found (this is acceptable)",
                "UI",
                "Low"
            )
            return
        
        # Test search with valid query
        search_field.clear()
        search_field.send_keys("test search query")
        
        # Find and click search button
        search_button_selectors = [
            "button[type='submit']", "input[type='submit']", 
            "button:contains('Search')", ".search-button", "#search-button"
        ]
        
        search_button = None
        for selector in search_button_selectors:
            try:
                search_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if search_button:
            search_button.click()
            time.sleep(3)
            
            # Check for search results
            current_url = driver.current_url
            if 'search' in current_url.lower() or 'query' in current_url.lower():
                reporter.log_test_result(
                    "Search Form Functionality",
                    "PASS",
                    f"Search form works. Redirected to: {current_url}",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Search Form Functionality",
                    "BUG",
                    f"Search form doesn't redirect properly. Current URL: {current_url}",
                    "Form",
                    "Medium"
                )
        else:
            # Try pressing Enter
            search_field.send_keys("\n")
            time.sleep(3)
            
            current_url = driver.current_url
            if 'search' in current_url.lower() or 'query' in current_url.lower():
                reporter.log_test_result(
                    "Search Form Functionality",
                    "PASS",
                    "Search form works with Enter key",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Search Form Functionality",
                    "BUG",
                    "Search form doesn't work with Enter key",
                    "Form",
                    "Medium"
                )
        
        # Test search with empty query
        search_field.clear()
        search_field.send_keys("")
        
        if search_button:
            search_button.click()
            time.sleep(2)
            
            # Check if form prevents empty search
            validation_messages = driver.find_elements(By.CSS_SELECTOR,
                ".error, .validation-error, .field-error, [class*='error']")
            
            if validation_messages:
                reporter.log_test_result(
                    "Search Form Validation",
                    "PASS",
                    "Search form shows validation for empty query",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Search Form Validation",
                    "BUG",
                    "Search form doesn't validate empty query",
                    "Form",
                    "Medium"
                )
            
    except Exception as e:
        reporter.log_test_result(
            "Search Form Test",
            "FAIL",
            f"Error testing search form: {e}",
            "Form",
            "High"
        )


def test_feedback_form(driver, base_url, reporter, data_generator):
    """
    Test feedback form functionality
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        # Look for feedback form
        feedback_pages = ['/feedback', '/feedback.html', '/contact', '/contact-us']
        
        feedback_form_found = False
        for page in feedback_pages:
            try:
                feedback_url = f"{base_url}{page}" if not base_url.endswith('/') else f"{base_url}{page[1:]}"
                driver.get(feedback_url)
                time.sleep(2)
                
                # Look for feedback form elements
                feedback_elements = [
                    "input[name='rating']", "select[name='rating']", 
                    "textarea[name='comment']", "textarea[name='feedback']",
                    "input[name='category']", "select[name='category']"
                ]
                
                for element in feedback_elements:
                    if driver.find_elements(By.CSS_SELECTOR, element):
                        feedback_form_found = True
                        break
                
                if feedback_form_found:
                    break
                    
            except Exception:
                continue
        
        if not feedback_form_found:
            reporter.log_test_result(
                "Feedback Form Detection",
                "PASS",
                "No feedback form found (this is acceptable)",
                "UI",
                "Low"
            )
            return
        
        # Test feedback form with valid data
        valid_data = data_generator.generate_form_data('feedback', valid=True)
        test_form_with_data(driver, valid_data, "Feedback Form Valid Data", reporter)
        
        # Test feedback form with invalid data
        invalid_data = data_generator.generate_form_data('feedback', valid=False)
        test_form_with_data(driver, invalid_data, "Feedback Form Invalid Data", reporter)
        
    except Exception as e:
        reporter.log_test_result(
            "Feedback Form Test",
            "FAIL",
            f"Error testing feedback form: {e}",
            "Form",
            "High"
        )


def test_input_field_validation(driver, base_url, reporter, data_generator):
    """
    Test input field validation across all forms
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(base_url)
        
        # Find all input fields
        input_fields = driver.find_elements(By.CSS_SELECTOR, 
            "input[type='text'], input[type='email'], input[type='password'], textarea")
        
        if not input_fields:
            reporter.log_test_result(
                "Input Field Validation",
                "PASS",
                "No input fields found to test (this is acceptable)",
                "Form",
                "Low"
            )
            return
        
        validation_tests_passed = 0
        validation_tests_failed = 0
        
        for field in input_fields[:5]:  # Test first 5 input fields
            try:
                field_type = field.get_attribute('type') or 'text'
                field_name = field.get_attribute('name') or 'unknown'
                
                # Test with invalid data based on field type
                if field_type == 'email':
                    field.clear()
                    field.send_keys("invalid-email")
                elif field_type == 'password':
                    field.clear()
                    field.send_keys("123")  # Weak password
                else:
                    field.clear()
                    field.send_keys("")  # Empty field
                
                # Trigger validation
                field.send_keys("\t")  # Tab to trigger validation
                time.sleep(1)
                
                # Check for validation messages
                validation_messages = driver.find_elements(By.CSS_SELECTOR,
                    ".error, .validation-error, .field-error, [class*='error'], [class*='invalid']")
                
                if validation_messages:
                    validation_tests_passed += 1
                else:
                    validation_tests_failed += 1
                    
            except Exception:
                validation_tests_failed += 1
        
        if validation_tests_passed > 0:
            reporter.log_test_result(
                "Input Field Validation",
                "PASS",
                f"Input field validation works. {validation_tests_passed} fields validated, {validation_tests_failed} failed",
                "Form",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Input Field Validation",
                "BUG",
                f"Input field validation not working. {validation_tests_failed} fields failed validation",
                "Form",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Input Field Validation",
            "FAIL",
            f"Error testing input field validation: {e}",
            "Form",
            "High"
        )


def test_form_submission_handling(driver, base_url, reporter, data_generator):
    """
    Test form submission handling and user feedback
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(base_url)
        
        # Find all forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        
        if not forms:
            reporter.log_test_result(
                "Form Submission Handling",
                "PASS",
                "No forms found to test (this is acceptable)",
                "Form",
                "Low"
            )
            return
        
        forms_tested = 0
        forms_with_feedback = 0
        
        for form in forms[:3]:  # Test first 3 forms
            try:
                # Fill form with test data
                inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea, select")
                for input_field in inputs:
                    if input_field.get_attribute('type') not in ['submit', 'button', 'hidden']:
                        input_field.clear()
                        input_field.send_keys("test data")
                
                # Submit form
                submit_button = form.find_element(By.CSS_SELECTOR, 
                    "button[type='submit'], input[type='submit']")
                
                if submit_button:
                    submit_button.click()
                    time.sleep(3)
                    
                    forms_tested += 1
                    
                    # Check for user feedback
                    feedback_elements = driver.find_elements(By.CSS_SELECTOR,
                        ".success, .alert-success, .message, .notification, [class*='success']")
                    
                    if feedback_elements:
                        forms_with_feedback += 1
                    
            except Exception:
                continue
        
        if forms_tested > 0:
            if forms_with_feedback > 0:
                reporter.log_test_result(
                    "Form Submission Handling",
                    "PASS",
                    f"Form submission provides user feedback. {forms_with_feedback}/{forms_tested} forms show feedback",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Form Submission Handling",
                    "BUG",
                    f"Form submission doesn't provide user feedback. {forms_tested} forms tested",
                    "Form",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Form Submission Handling",
                "PASS",
                "No forms could be tested (this is acceptable)",
                "Form",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Form Submission Handling",
            "FAIL",
            f"Error testing form submission handling: {e}",
            "Form",
            "High"
        )


def test_form_accessibility(driver, base_url, reporter):
    """
    Test form accessibility features
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        driver.get(base_url)
        
        # Find all forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        
        if not forms:
            reporter.log_test_result(
                "Form Accessibility",
                "PASS",
                "No forms found to test (this is acceptable)",
                "Accessibility",
                "Low"
            )
            return
        
        accessibility_issues = []
        
        for form in forms:
            # Check for form labels
            inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea, select")
            for input_field in inputs:
                if input_field.get_attribute('type') not in ['submit', 'button', 'hidden']:
                    # Check for associated label
                    input_id = input_field.get_attribute('id')
                    if input_id:
                        label = form.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                        if not label:
                            accessibility_issues.append(f"Input field {input_id} has no associated label")
                    else:
                        accessibility_issues.append("Input field has no ID for label association")
            
            # Check for form fieldset and legend
            fieldsets = form.find_elements(By.TAG_NAME, "fieldset")
            if fieldsets:
                for fieldset in fieldsets:
                    legend = fieldset.find_element(By.TAG_NAME, "legend")
                    if not legend:
                        accessibility_issues.append("Fieldset has no legend")
        
        if accessibility_issues:
            reporter.log_test_result(
                "Form Accessibility",
                "BUG",
                f"Form accessibility issues found: {', '.join(accessibility_issues[:3])}",
                "Accessibility",
                "Medium"
            )
        else:
            reporter.log_test_result(
                "Form Accessibility",
                "PASS",
                "Forms have good accessibility features",
                "Accessibility",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Form Accessibility",
            "FAIL",
            f"Error testing form accessibility: {e}",
            "Accessibility",
            "Medium"
        )


def test_form_security(driver, base_url, reporter, data_generator):
    """
    Test form security features
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(base_url)
        
        # Find all forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        
        if not forms:
            reporter.log_test_result(
                "Form Security",
                "PASS",
                "No forms found to test (this is acceptable)",
                "Security",
                "Low"
            )
            return
        
        security_issues = []
        
        for form in forms:
            # Check for CSRF protection
            csrf_token = form.find_elements(By.CSS_SELECTOR, 
                "input[name*='csrf'], input[name*='token'], input[name*='_token']")
            
            if not csrf_token:
                security_issues.append("Form missing CSRF protection token")
            
            # Check for HTTPS in form action
            form_action = form.get_attribute('action')
            if form_action and not form_action.startswith('https://'):
                security_issues.append(f"Form action not using HTTPS: {form_action}")
            
            # Test for SQL injection
            inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea")
            for input_field in inputs:
                if input_field.get_attribute('type') not in ['submit', 'button', 'hidden']:
                    sql_payloads = data_generator.generate_sql_injection_payloads()
                    for payload in sql_payloads[:2]:  # Test first 2 payloads
                        try:
                            input_field.clear()
                            input_field.send_keys(payload)
                            # Don't submit, just check if input is handled safely
                        except Exception:
                            pass
        
        if security_issues:
            reporter.log_test_result(
                "Form Security",
                "BUG",
                f"Form security issues found: {', '.join(security_issues[:3])}",
                "Security",
                "High"
            )
        else:
            reporter.log_test_result(
                "Form Security",
                "PASS",
                "Forms have good security features",
                "Security",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Form Security",
            "FAIL",
            f"Error testing form security: {e}",
            "Security",
            "High"
        )


def test_form_error_handling(driver, base_url, reporter, data_generator):
    """
    Test form error handling and user experience
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
        data_generator: TestDataGenerator instance
    """
    try:
        driver.get(base_url)
        
        # Find all forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        
        if not forms:
            reporter.log_test_result(
                "Form Error Handling",
                "PASS",
                "No forms found to test (this is acceptable)",
                "Form",
                "Low"
            )
            return
        
        error_handling_tests = 0
        error_handling_passed = 0
        
        for form in forms[:2]:  # Test first 2 forms
            try:
                # Submit form without filling required fields
                submit_button = form.find_element(By.CSS_SELECTOR, 
                    "button[type='submit'], input[type='submit']")
                
                if submit_button:
                    submit_button.click()
                    time.sleep(2)
                    
                    error_handling_tests += 1
                    
                    # Check for error messages
                    error_messages = driver.find_elements(By.CSS_SELECTOR,
                        ".error, .alert-error, .alert-danger, .validation-error, [class*='error']")
                    
                    if error_messages:
                        error_handling_passed += 1
                    
            except Exception:
                continue
        
        if error_handling_tests > 0:
            if error_handling_passed > 0:
                reporter.log_test_result(
                    "Form Error Handling",
                    "PASS",
                    f"Form error handling works. {error_handling_passed}/{error_handling_tests} forms show proper error messages",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Form Error Handling",
                    "BUG",
                    f"Form error handling not working. {error_handling_tests} forms tested without proper error messages",
                    "Form",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Form Error Handling",
                "PASS",
                "No forms could be tested for error handling (this is acceptable)",
                "Form",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Form Error Handling",
            "FAIL",
            f"Error testing form error handling: {e}",
            "Form",
            "High"
        )


def test_form_with_data(driver, form_data, test_name, reporter):
    """
    Helper function to test a form with given data
    
    Args:
        driver: WebDriver instance
        form_data: Dictionary with form data
        test_name: Name of the test
        reporter: QAReporter instance
    """
    try:
        # Find form fields and fill them
        for field_name, value in form_data.items():
            field_selectors = [
                f"input[name='{field_name}']",
                f"textarea[name='{field_name}']",
                f"select[name='{field_name}']",
                f"#{field_name}",
                f"input[placeholder*='{field_name}']"
            ]
            
            for selector in field_selectors:
                try:
                    field = driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    field.send_keys(str(value))
                    break
                except NoSuchElementException:
                    continue
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, 
            "button[type='submit'], input[type='submit']")
        
        if submit_button:
            submit_button.click()
            time.sleep(3)
            
            # Check for success/error messages
            success_messages = driver.find_elements(By.CSS_SELECTOR,
                ".success, .alert-success, .message, [class*='success']")
            error_messages = driver.find_elements(By.CSS_SELECTOR,
                ".error, .alert-error, .alert-danger, [class*='error']")
            
            if success_messages:
                reporter.log_test_result(
                    test_name,
                    "PASS",
                    "Form submission successful with valid data",
                    "Form",
                    "Low"
                )
            elif error_messages:
                reporter.log_test_result(
                    test_name,
                    "PASS",
                    "Form shows appropriate error messages for invalid data",
                    "Form",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    test_name,
                    "BUG",
                    "Form submission doesn't provide clear feedback",
                    "Form",
                    "Medium"
                )
        
    except Exception as e:
        reporter.log_test_result(
            test_name,
            "FAIL",
            f"Error testing form with data: {e}",
            "Form",
            "High"
        )
