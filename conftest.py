"""
QAssurify pytest configuration and fixtures
"""

import pytest

def pytest_addoption(parser):
    """Add QAssurify-specific command line options."""
    parser.addoption(
        "--base-url",
        action="store",
        default="http://127.0.0.1:8000",
        help="Base URL of the application under test"
    )
    parser.addoption(
        "--headless",
        action="store",
        type=str,
        default="false",
        help="Run browser in headless mode (true/false)"
    )

@pytest.fixture
def base_url(request):
    """Get base URL from command line option."""
    return request.config.getoption("--base-url")

@pytest.fixture
def headless(request):
    """Get headless mode from command line option."""
    return request.config.getoption("--headless").lower() == "true"