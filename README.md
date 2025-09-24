# Strict QA Agent (CLI Only)

A comprehensive, automated QA testing framework for web applications, now focused on a CLI-only workflow. The Strict QA Agent acts like a real QA tester but with stricter validation and automated execution.

## 🎯 Features

- **Complete Web Testing**: Tests entire web projects hosted on localhost
- **Comprehensive Coverage**: Form validations, user flows, edge cases, UI/UX checks, API testing, and performance monitoring
- **Automated Reporting**: Generates detailed Excel reports with test results and bug tracking
- **Realistic Test Data**: Uses Faker library to generate realistic test data
- **Multiple Test Suites**: Signup, Login, Navigation, Forms, and API testing
- **Strict Validation**: Catches bugs that manual testing might miss

## 📁 Project Structure

```
qa_agent/
├── main.py                 # Entry point - runs all tests
├── requirements.txt        # Python dependencies
├── tests/                  # Test modules
│   ├── test_signup.py     # Signup form tests
│   ├── test_login.py      # Login functionality tests
│   ├── test_navigation.py # Page navigation tests
│   ├── test_forms.py      # General form validation tests
│   └── test_api.py        # API testing with requests
├── reports/               # Generated test reports
│   └── qa_report_*.xlsx  # Auto-generated Excel reports
└── utils/                 # Utility modules
    ├── reporter.py        # Excel logging and console output
    └── data_generator.py  # Faker-based test data generation
```

## 🚀 Quick Start (CLI)

### 1. Installation

```bash
# Clone or download the project
cd qa_agent

# Install dependencies
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

# Run CLI
python main.py
```

### 2. Basic Usage

```bash
# Run all tests on default localhost:8000
python main.py

# Run tests on custom URL
python main.py http://localhost:3000

# Run specific test modules
python -c "
from main import StrictQAAgent
agent = StrictQAAgent('http://localhost:8000')
agent.run_specific_tests(['tests.test_signup', 'tests.test_login'])
"
```

### 3. View Results

- **Console Output**: Real-time test results with colored status indicators
- **Excel/CSV Reports**: Detailed reports saved in `reports/` with host-prefixed filenames
  
Note: The previous Web UI has been removed to keep the project focused and lightweight.

### 4. CLI Notes

- Use the exit code for CI gating (non-zero when bugs are found)
- Reports are written to `reports/` with host-prefixed filenames

## 🔍 Test Coverage

### 1. Form Validations
- ✅ Required field validation
- ✅ Email format validation
- ✅ Password strength validation
- ✅ Input length validation
- ✅ Special character handling

### 2. User Flows
- ✅ Signup process
- ✅ Login/Logout functionality
- ✅ Profile updates
- ✅ Navigation across pages
- ✅ Form submissions

### 3. Edge Cases
- ✅ Long input handling
- ✅ Special characters
- ✅ SQL injection attempts
- ✅ XSS payload testing
- ✅ Boundary value testing

### 4. UI/UX Checks
- ✅ Button clickability
- ✅ Error message visibility
- ✅ Broken link detection
- ✅ Missing image detection
- ✅ Responsive design testing

### 5. API Testing
- ✅ Endpoint discovery
- ✅ Response validation
- ✅ Status code verification
- ✅ Authentication testing
- ✅ Security header checks
- ✅ Performance monitoring

### 6. Performance Checks
- ✅ Page load times
- ✅ API response times
- ✅ Form submission delays

## 📊 Reporting

The QA Agent generates comprehensive reports including:

- **Test Results**: Pass/Fail/Bug status for each test
- **Bug Summary**: Detailed list of all bugs found
- **Performance Metrics**: Response times and execution statistics
- **Test Coverage**: Breakdown by test type and severity
- **Timestamps**: When each test was executed

### Report Structure

| Test Case | Result | Details | Test Type | Severity | Timestamp |
|-----------|--------|---------|-----------|----------|-----------|
| Signup Page Loads | PASS | Page loaded successfully | UI | Low | 2024-01-20 10:30:15 |
| Email Validation | BUG | Email field doesn't validate format | Form | High | 2024-01-20 10:30:45 |

## 🛠️ Configuration

### Customizing Test Data

Edit `utils/data_generator.py` to customize test data generation:

```python
# Generate custom user data
user_data = data_generator.generate_user_data(valid=True)

# Generate edge case data
edge_data = data_generator.generate_edge_case_data()

# Generate API test data
api_data = data_generator.generate_api_test_data()
```

### Adding New Tests

1. Create a new test file in `tests/` directory
2. Implement a `run_tests(base_url, reporter, data_generator)` function
3. Add the module to `main.py` in the `test_modules` list (or select it in the UI when running specific tests)

Example:
```python
# tests/test_custom.py
def run_tests(base_url: str, reporter, data_generator):
    # Your custom tests here
    reporter.log_test_result(
        "Custom Test",
        "PASS",
        "Test description",
        "Custom",
        "Low"
    )
```

## 🔧 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**
   - The agent automatically downloads ChromeDriver
   - Ensure Chrome browser is installed
   - Check internet connection for driver download

2. **Connection Refused**
   - Verify your web application is running
   - Check the correct port number
   - Ensure the URL is accessible

3. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

4. **Permission Errors**
   - Ensure write permissions for `reports/` directory
   - Run with appropriate user permissions

### Debug Mode

Enable debug mode by modifying `main.py`:

```python
# Add this to see more detailed output
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Best Practices

1. **Run Tests Regularly**: Integrate into your CI/CD pipeline
2. **Review Reports**: Always check the Excel report for detailed findings
3. **Fix Critical Bugs**: Address High and Critical severity bugs immediately
4. **Customize Tests**: Adapt tests to your specific application needs
5. **Monitor Performance**: Track response times over time

## 🤝 Contributing

To add new test types or improve existing ones:

1. Fork the repository
2. Create a feature branch
3. Add your tests following the existing pattern
4. Update documentation
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the Excel report for detailed error information
3. Check console output for real-time feedback
4. Ensure all dependencies are properly installed

---

**Happy Testing! 🧪✨**

The Strict QA Agent will help you catch bugs before they reach production and ensure your web application meets the highest quality standards.
