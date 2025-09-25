import pytest
from typing import Dict, Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def pytest_addoption(parser):
    parser.addoption(
        "--fast",
        action="store_true",
        default=False,
        help="Run only smoke tests"
    )
    parser.addoption(
        "--ci",
        action="store_true",
        default=False,
        help="Run in CI/CD mode (always headless)"
    )

@pytest.fixture(scope="session")
def is_fast_mode(request):
    return request.config.getoption("--fast")

@pytest.fixture(scope="session")
def is_ci_mode(request):
    return request.config.getoption("--ci")

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Global test configuration"""
    return {
        'explicit_wait': 10,  # seconds to wait for elements
        'base_url': 'https://www.saucedemo.com',
        'test_users': {
            'standard': {
                'username': 'standard_user',
                'password': 'secret_sauce'
            }
        }
    }

# Custom wait conditions
def wait_for(driver, timeout: int = 10):
    """Create a WebDriverWait with common timeout"""
    return WebDriverWait(driver, timeout)