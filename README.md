# QAssurify Agent — CLI and Web UI

A comprehensive, automated QA testing framework for web applications. You can run it via the Command Line (CLI) or from a lightweight Web UI. The agent acts like a real QA tester with strict validation and automated execution.

## 🎯 Features

- **Complete Web Testing**: Tests entire web projects hosted on localhost
- **Comprehensive Coverage**: Form validations, user flows, edge cases, UI/UX checks, API testing, and performance monitoring
- **Automated Reporting**: Generates detailed Excel reports with test results and bug tracking
- **Realistic Test Data**: Uses Faker library to generate realistic test data
- **Multiple Test Suites**: Signup, Login, Navigation, Forms, and API testing
- **Strict Validation**: Catches bugs that manual testing might miss

## 📁 Project Structure

```
.
├── app.py                 # Web UI server (Flask)
├── main.py                # CLI entry point - runs all tests
├── requirements.txt       # Python dependencies
├── templates/             # UI templates (dashboard, results, tested data)
├── static/                # UI assets (CSS)
├── tests/                 # Test modules
│   ├── test_signup.py     # Signup form tests
│   ├── test_login.py      # Login functionality tests
│   ├── test_navigation.py # Page navigation tests
│   ├── test_forms.py      # General form validation tests
│   └── test_api.py        # API testing with requests
├── utils/                 # Utility modules
│   ├── reporter.py        # Excel logging and console output
│   └── data_generator.py  # Faker-based test data generation
└── reports/               # Generated test reports (Excel/CSV)
```

## 🚀 Quick Start

### 1) Installation

```bash
# From the project root (this folder)

# Create and activate a virtualenv
python -m venv .venv

# Windows PowerShell
. .venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Optional (Windows) if script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2) Run via CLI

```bash
# Run all tests on default http://127.0.0.1:8000
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

- Exit codes: 0 when no bugs found; non‑zero when bugs are found (for CI gating).

### 3) Run via Web UI

Start the Web UI and operate tests from a browser.

```bash
# From the project root
python app.py
```

- UI will start at http://127.0.0.1:5000 (or http://localhost:5000)
- In the UI, enter your Base URL (e.g., http://localhost:3000) and click Start Tests
- Progress, charts, and results will appear when the run completes

### 4) View Results

- CLI: Real-time test results in the console with colored status indicators
- Web UI: Results Overview (status/type charts) and Latest Results table
- Reports: Excel/CSV saved in `reports/` with host-prefixed filenames

### 5) UI Panels and API Endpoints

- Start tests (UI): enter Base URL and click Start Tests
- Status polling: UI uses `/status` to refresh progress and results
- Tested Data panel: UI calls `/tested-data` and shows only real data from the latest run:
  - summary: overall run summary
  - results: all log entries
  - weaknesses: only BUG/FAIL findings
  - Empty sections are hidden; only available items are shown

Primary endpoints served by `app.py`:

- `/` Dashboard
- `/run` Start a run (POST JSON: `{ baseUrl: "http://localhost:3000" }`)
- `/status` Current progress, results, summary
- `/tested-data` Real tested data and weaknesses from the last run
- `/export` Export current results to CSV/Excel
- `/download?path=...` Download generated files

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

### Web UI Behavior (Tested Data)

- The Tested Data panel shows only data actually produced by your run. If only a few items exist, only those appear with centered section titles. No placeholders are shown.

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
   - Check the correct port number and protocol (http vs https)
   - Ensure the URL is accessible from the machine running the agent

5. **UI Not Starting**
   - Ensure Flask is installed (already included in requirements)
   - Run `python app.py` from the project root
   - Check port 5000 usage; change the port in `app.py` if needed

6. **Empty Tested Data**
   - Run a fresh test from the UI or CLI; `/tested-data` reflects the latest run only
   - If your site has no applicable forms/APIs, only summary/weaknesses may appear

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

The Strict QA Agent helps you catch bugs before they reach production and ensures your web application meets high quality standards — whether you prefer the CLI or the simple Web UI.
