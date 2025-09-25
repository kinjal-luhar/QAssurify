"""
WebDriver setup utility for QAssurify
Provides optimized browser configuration for testing
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException


def get_driver(headless: bool = False, ci_mode: bool = False) -> webdriver.Chrome:
    """
    Get a configured Chrome WebDriver instance optimized for performance.
    If successful, returns a WebDriver instance that MUST be quit() after use.
    
    Args:
        headless: Run browser in headless mode
        ci_mode: Run with CI/CD optimized settings
        
    Returns:
        WebDriver: Configured Chrome WebDriver instance
        
    Raises:
        WebDriverException: If browser cannot be started
    """
    options = webdriver.ChromeOptions()
    
    # Performance optimizations
    options.add_argument('--start-maximized')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Speed optimizations
    options.add_argument('--disable-images')  # Don't load images
    options.add_argument('--disable-javascript-harmony-shipping')  # Disable experimental JS
    options.add_argument('--disable-breakpad')  # Disable crash reporting
    options.add_argument('--disable-logging')  # Disable logging
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Always run headless in CI mode
    if headless or ci_mode:
        options.add_argument('--headless=new')
    
    # Configure browser preferences for optimal performance
    content_settings = {
        'cookies': 1,
        'images': 2,
        'javascript': 1,
        'plugins': 2,
        'popups': 2,
        'geolocation': 2,
        'notifications': 2,
        'auto_select_certificate': 2,
        'fullscreen': 2,
        'mouselock': 2,
        'mixed_script': 2,
        'media_stream': 2,
        'media_stream_mic': 2,
        'media_stream_camera': 2,
        'protocol_handlers': 2,
        'ppapi_broker': 2,
        'automatic_downloads': 2,
        'midi_sysex': 2,
        'push_messaging': 2,
        'ssl_cert_decisions': 2
    }
    
    prefs = {
        'profile.managed_default_content_settings.images': 2,
        'disk-cache-size': 4096,
        'profile.default_content_setting_values': content_settings
    }
    
    options.add_experimental_option('prefs', prefs)
    
    try:
        # Use ChromeDriverManager for automatic webdriver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Set reasonable timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        return driver
        
    except Exception as e:
        # Ensure any partially initialized driver is cleaned up
        try:
            if 'driver' in locals():
                driver.quit()
        except Exception:
            pass
        raise WebDriverException(f"Failed to initialize Chrome driver: {str(e)}")