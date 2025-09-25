"""
Driver Setup Utility
Provides a consistent way to create Chrome WebDriver instances across all tests
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Get a configured Chrome WebDriver instance
    
    Args:
        headless: Whether to run Chrome in headless mode
        
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    options = Options()
    
    # Basic stability and security options
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Add headless mode if requested (using new headless mode)
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    
    # Get ChromeDriver service with automatic binary management
    service = Service(ChromeDriverManager().install())
    
    # Create and return the WebDriver instance
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    
    return driver