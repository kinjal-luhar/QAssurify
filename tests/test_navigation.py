"""
Ultra-light smoke test for basic site navigation.
Only checks if homepage loads and has a title.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils.driver_setup import get_driver

def test_homepage_load(driver, base_url, test_options):
    """Check if homepage loads with a valid title."""
    # Set aggressive timeout for smoke tests
    if test_options.get('short_timeout'):
        driver.set_page_load_timeout(3)
    
    try:
        driver.get(base_url)
        
        # Wait max 3s for title to be non-empty
        WebDriverWait(driver, 3).until(
            lambda x: x.title and len(x.title.strip()) > 0
        )
        
        assert driver.title.strip(), "Homepage should have non-empty title"
        return True, "Homepage loads successfully"
        
    except Exception as e:
        return False, f"Homepage failed to load: {str(e)}"

def run_tests(base_url: str, reporter, test_options=None):
    """
    Run ultra-light smoke test for navigation
    
    Args:
        base_url: Base URL of the web application
        reporter: QAReporter instance for logging results
        test_options: Dictionary of test options for smoke test configuration
    """
    print("🔥 Running Ultra-Light Navigation Smoke Test...")
    
    driver = None
    try:
        driver = get_driver(headless=True)
        
        # Single test: Check if homepage loads
        success, message = test_homepage_load(driver, base_url, test_options or {})
        reporter.add_result("Homepage Load", success, message)
        
        # Test 4: Test internal links
        test_internal_links(driver, base_url, reporter)
        
        # Test 5: Test broken links
        test_broken_links(driver, base_url, reporter)
        
        # Test 6: Test back/forward navigation
        test_browser_navigation(driver, base_url, reporter)
        
        # Test 7: Test responsive navigation
        test_responsive_navigation(driver, base_url, reporter)
        
        # Test 8: Test breadcrumb navigation
        test_breadcrumb_navigation(driver, base_url, reporter)
        
    except Exception as e:
        reporter.log_test_result(
            "Navigation Test Setup",
            "FAIL",
            f"Failed to setup navigation tests: {e}",
            "UI",
            "High"
        )
    finally:
        if driver:
            driver.quit()


# Driver setup moved to utils/driver_setup.py


def test_homepage_navigation(driver, base_url, reporter):
    """
    Test homepage navigation and loading
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        # Test homepage loading
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check if homepage loads successfully
        page_title = driver.title
        if page_title and len(page_title.strip()) > 0:
            reporter.log_test_result(
                "Homepage Navigation",
                "PASS",
                f"Homepage loaded successfully. Title: {page_title}",
                "Navigation",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Homepage Navigation",
                "BUG",
                "Homepage loaded but has no title",
                "Navigation",
                "Medium"
            )
        
        # Check for common homepage elements
        homepage_elements = [
            "header", "nav", "main", "footer",
            "h1", "h2", "h3", "p", "a", "img"
        ]
        
        found_elements = []
        for element in homepage_elements:
            if driver.find_elements(By.TAG_NAME, element):
                found_elements.append(element)
        
        if len(found_elements) >= 3:
            reporter.log_test_result(
                "Homepage Content",
                "PASS",
                f"Homepage contains essential elements: {', '.join(found_elements)}",
                "UI",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Homepage Content",
                "BUG",
                f"Homepage missing essential elements. Found only: {', '.join(found_elements)}",
                "UI",
                "Medium"
            )
            
    except TimeoutException:
        reporter.log_test_result(
            "Homepage Navigation",
            "FAIL",
            f"Homepage failed to load within timeout: {base_url}",
            "Navigation",
            "High"
        )
    except Exception as e:
        reporter.log_test_result(
            "Homepage Navigation",
            "FAIL",
            f"Error testing homepage navigation: {e}",
            "Navigation",
            "High"
        )


def test_main_navigation_menu(driver, base_url, reporter):
    """
    Test main navigation menu functionality
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        driver.get(base_url)
        
        # Look for main navigation menu
        nav_selectors = [
            "nav", ".navbar", ".navigation", ".menu", ".nav-menu",
            "header nav", ".main-nav", "#navigation", "#nav"
        ]
        
        nav_element = None
        for selector in nav_selectors:
            try:
                nav_element = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not nav_element:
            reporter.log_test_result(
                "Main Navigation Menu",
                "BUG",
                "No main navigation menu found on the page",
                "UI",
                "High"
            )
            return
        
        # Find navigation links
        nav_links = nav_element.find_elements(By.TAG_NAME, "a")
        
        if not nav_links:
            reporter.log_test_result(
                "Main Navigation Menu",
                "BUG",
                "Navigation menu found but contains no links",
                "UI",
                "High"
            )
            return
        
        # Test navigation links
        working_links = 0
        broken_links = 0
        
        for link in nav_links[:5]:  # Test first 5 navigation links
            try:
                href = link.get_attribute('href')
                if href and not href.startswith('javascript:'):
                    # Click the link
                    original_url = driver.current_url
                    link.click()
                    time.sleep(2)
                    
                    new_url = driver.current_url
                    
                    # Check if navigation was successful
                    if new_url != original_url:
                        working_links += 1
                        
                        # Check if new page loads properly
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )
                        except TimeoutException:
                            broken_links += 1
                    else:
                        broken_links += 1
                    
                    # Go back to original page
                    driver.back()
                    time.sleep(1)
                    
            except Exception as e:
                broken_links += 1
        
        if working_links > 0:
            reporter.log_test_result(
                "Main Navigation Menu",
                "PASS",
                f"Navigation menu works. {working_links} working links, {broken_links} broken links",
                "Navigation",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Main Navigation Menu",
                "BUG",
                f"All navigation links are broken ({broken_links} tested)",
                "Navigation",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Main Navigation Menu",
            "FAIL",
            f"Error testing main navigation menu: {e}",
            "Navigation",
            "High"
        )


def test_footer_links(driver, base_url, reporter):
    """
    Test footer links functionality
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        driver.get(base_url)
        
        # Look for footer
        footer_selectors = [
            "footer", ".footer", "#footer", ".site-footer"
        ]
        
        footer_element = None
        for selector in footer_selectors:
            try:
                footer_element = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not footer_element:
            reporter.log_test_result(
                "Footer Links",
                "PASS",
                "No footer found (this is acceptable)",
                "UI",
                "Low"
            )
            return
        
        # Find footer links
        footer_links = footer_element.find_elements(By.TAG_NAME, "a")
        
        if not footer_links:
            reporter.log_test_result(
                "Footer Links",
                "PASS",
                "Footer found but contains no links (this is acceptable)",
                "UI",
                "Low"
            )
            return
        
        # Test footer links
        working_links = 0
        broken_links = 0
        
        for link in footer_links[:3]:  # Test first 3 footer links
            try:
                href = link.get_attribute('href')
                if href and not href.startswith('javascript:'):
                    # Test if link is accessible
                    original_url = driver.current_url
                    link.click()
                    time.sleep(2)
                    
                    new_url = driver.current_url
                    
                    if new_url != original_url:
                        working_links += 1
                        driver.back()
                        time.sleep(1)
                    else:
                        broken_links += 1
                        
            except Exception as e:
                broken_links += 1
        
        if working_links > 0 or broken_links == 0:
            reporter.log_test_result(
                "Footer Links",
                "PASS",
                f"Footer links work. {working_links} working links, {broken_links} broken links",
                "Navigation",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Footer Links",
                "BUG",
                f"Footer links have issues. {working_links} working, {broken_links} broken",
                "Navigation",
                "Medium"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Footer Links",
            "FAIL",
            f"Error testing footer links: {e}",
            "Navigation",
            "Medium"
        )


def test_internal_links(driver, base_url, reporter):
    """
    Test internal links within the application
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        driver.get(base_url)
        
        # Find all internal links
        all_links = driver.find_elements(By.TAG_NAME, "a")
        internal_links = []
        
        for link in all_links:
            href = link.get_attribute('href')
            if href:
                # Check if it's an internal link
                if (href.startswith(base_url) or 
                    href.startswith('/') or 
                    href.startswith('./') or 
                    href.startswith('../')):
                    internal_links.append(link)
        
        if not internal_links:
            reporter.log_test_result(
                "Internal Links",
                "BUG",
                "No internal links found on the page",
                "Navigation",
                "Medium"
            )
            return
        
        # Test internal links
        working_links = 0
        broken_links = 0
        
        for link in internal_links[:5]:  # Test first 5 internal links
            try:
                href = link.get_attribute('href')
                original_url = driver.current_url
                
                link.click()
                time.sleep(2)
                
                new_url = driver.current_url
                
                # Check if navigation was successful
                if new_url != original_url:
                    working_links += 1
                    
                    # Check if page loads properly
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                    except TimeoutException:
                        broken_links += 1
                else:
                    broken_links += 1
                
                # Go back
                driver.back()
                time.sleep(1)
                
            except Exception as e:
                broken_links += 1
        
        if working_links > 0:
            reporter.log_test_result(
                "Internal Links",
                "PASS",
                f"Internal links work. {working_links} working links, {broken_links} broken links",
                "Navigation",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Internal Links",
                "BUG",
                f"All internal links are broken ({broken_links} tested)",
                "Navigation",
                "High"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Internal Links",
            "FAIL",
            f"Error testing internal links: {e}",
            "Navigation",
            "High"
        )


def test_broken_links(driver, base_url, reporter):
    """
    Test for broken links (404 errors)
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        driver.get(base_url)
        
        # Find all links
        all_links = driver.find_elements(By.TAG_NAME, "a")
        broken_links = []
        
        for link in all_links[:10]:  # Test first 10 links
            try:
                href = link.get_attribute('href')
                if href and not href.startswith('javascript:'):
                    original_url = driver.current_url
                    
                    link.click()
                    time.sleep(3)
                    
                    # Check for 404 or error indicators
                    current_url = driver.current_url
                    page_source = driver.page_source.lower()
                    
                    if ('404' in page_source or 
                        'not found' in page_source or 
                        'error' in page_source or
                        'page not found' in page_source):
                        broken_links.append(href)
                    
                    # Go back
                    driver.back()
                    time.sleep(1)
                    
            except Exception as e:
                broken_links.append(f"Error accessing link: {e}")
        
        if broken_links:
            reporter.log_test_result(
                "Broken Links",
                "BUG",
                f"Found {len(broken_links)} broken links: {', '.join(broken_links[:3])}",
                "Navigation",
                "High"
            )
        else:
            reporter.log_test_result(
                "Broken Links",
                "PASS",
                "No broken links found in tested links",
                "Navigation",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Broken Links",
            "FAIL",
            f"Error testing broken links: {e}",
            "Navigation",
            "High"
        )


def test_browser_navigation(driver, base_url, reporter):
    """
    Test browser back/forward navigation
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        # Start from homepage
        driver.get(base_url)
        homepage_url = driver.current_url
        
        # Navigate to another page
        links = driver.find_elements(By.TAG_NAME, "a")
        if links:
            links[0].click()
            time.sleep(2)
            second_page_url = driver.current_url
            
            # Test back navigation
            driver.back()
            time.sleep(2)
            back_url = driver.current_url
            
            if back_url == homepage_url:
                reporter.log_test_result(
                    "Browser Back Navigation",
                    "PASS",
                    "Browser back navigation works correctly",
                    "Navigation",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Browser Back Navigation",
                    "BUG",
                    f"Browser back navigation failed. Expected: {homepage_url}, Got: {back_url}",
                    "Navigation",
                    "Medium"
                )
            
            # Test forward navigation
            driver.forward()
            time.sleep(2)
            forward_url = driver.current_url
            
            if forward_url == second_page_url:
                reporter.log_test_result(
                    "Browser Forward Navigation",
                    "PASS",
                    "Browser forward navigation works correctly",
                    "Navigation",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Browser Forward Navigation",
                    "BUG",
                    f"Browser forward navigation failed. Expected: {second_page_url}, Got: {forward_url}",
                    "Navigation",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Browser Navigation",
                "PASS",
                "No links found to test browser navigation (this is acceptable)",
                "Navigation",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Browser Navigation",
            "FAIL",
            f"Error testing browser navigation: {e}",
            "Navigation",
            "Medium"
        )


def test_responsive_navigation(driver, base_url, reporter):
    """
    Test responsive navigation (mobile menu)
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        # Test desktop navigation
        driver.set_window_size(1920, 1080)
        driver.get(base_url)
        
        desktop_nav = driver.find_elements(By.CSS_SELECTOR, "nav, .navbar, .navigation")
        
        # Test mobile navigation
        driver.set_window_size(375, 667)  # iPhone size
        time.sleep(2)
        
        mobile_nav = driver.find_elements(By.CSS_SELECTOR, 
            "nav, .navbar, .navigation, .mobile-nav, .hamburger, .menu-toggle")
        
        if mobile_nav:
            reporter.log_test_result(
                "Responsive Navigation",
                "PASS",
                "Navigation elements found in mobile view",
                "UI",
                "Low"
            )
        else:
            reporter.log_test_result(
                "Responsive Navigation",
                "BUG",
                "No navigation elements found in mobile view",
                "UI",
                "Medium"
            )
        
        # Reset to desktop size
        driver.set_window_size(1920, 1080)
        
    except Exception as e:
        reporter.log_test_result(
            "Responsive Navigation",
            "FAIL",
            f"Error testing responsive navigation: {e}",
            "UI",
            "Medium"
        )


def test_breadcrumb_navigation(driver, base_url, reporter):
    """
    Test breadcrumb navigation if present
    
    Args:
        driver: WebDriver instance
        base_url: Base URL of the web application
        reporter: QAReporter instance
    """
    try:
        driver.get(base_url)
        
        # Look for breadcrumb navigation
        breadcrumb_selectors = [
            ".breadcrumb", ".breadcrumbs", ".breadcrumb-nav", 
            "nav[aria-label='breadcrumb']", ".breadcrumb-trail"
        ]
        
        breadcrumb_element = None
        for selector in breadcrumb_selectors:
            try:
                breadcrumb_element = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not breadcrumb_element:
            reporter.log_test_result(
                "Breadcrumb Navigation",
                "PASS",
                "No breadcrumb navigation found (this is acceptable)",
                "UI",
                "Low"
            )
            return
        
        # Test breadcrumb links
        breadcrumb_links = breadcrumb_element.find_elements(By.TAG_NAME, "a")
        
        if breadcrumb_links:
            working_links = 0
            for link in breadcrumb_links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        original_url = driver.current_url
                        link.click()
                        time.sleep(2)
                        
                        if driver.current_url != original_url:
                            working_links += 1
                            driver.back()
                            time.sleep(1)
                except Exception:
                    pass
            
            if working_links > 0:
                reporter.log_test_result(
                    "Breadcrumb Navigation",
                    "PASS",
                    f"Breadcrumb navigation works. {working_links} working links",
                    "Navigation",
                    "Low"
                )
            else:
                reporter.log_test_result(
                    "Breadcrumb Navigation",
                    "BUG",
                    "Breadcrumb navigation links don't work",
                    "Navigation",
                    "Medium"
                )
        else:
            reporter.log_test_result(
                "Breadcrumb Navigation",
                "PASS",
                "Breadcrumb navigation found but contains no links (this is acceptable)",
                "UI",
                "Low"
            )
            
    except Exception as e:
        reporter.log_test_result(
            "Breadcrumb Navigation",
            "FAIL",
            f"Error testing breadcrumb navigation: {e}",
            "Navigation",
            "Medium"
        )
