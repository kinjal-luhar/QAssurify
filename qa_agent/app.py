"""
Strict QA Agent - Web UI Application
Modern web interface for the QA Agent with real-time testing and reporting
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_cors import CORS
import pandas as pd
from werkzeug.utils import secure_filename
# Plotly imports were unused; removed to reduce overhead
import requests

from main import StrictQAAgent
from utils.reporter import QAReporter
from utils.data_generator import TestDataGenerator

app = Flask(__name__)
app.secret_key = 'qa_agent_secret_key_2024'
CORS(app)

# Global variables for test execution
test_running = False
test_progress = 0
test_results = []
current_agent = None
test_thread = None
test_started_at = None
test_finished_at = None

# Configuration
UPLOAD_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/test_data_sample')
def test_data_sample():
    """Return sample generated test data to display in UI."""
    try:
        gen = TestDataGenerator()
        data = {
            'user_valid': gen.generate_user_data(True),
            'user_invalid': gen.generate_user_data(False),
            'login_valid': gen.generate_login_data(True),
            'login_invalid': gen.generate_login_data(False),
            'contact_valid': gen.generate_form_data('contact', True),
            'contact_invalid': gen.generate_form_data('contact', False),
            'edge_cases': gen.generate_edge_case_data(),
        }
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run_tests', methods=['POST'])
def run_tests():
    """Run QA tests with specified URL"""
    global test_running, test_progress, test_results, current_agent
    
    if test_running:
        return jsonify({'error': 'Tests are already running'}), 400
    
    data = request.get_json()
    target_url = data.get('url', 'http://127.0.0.1:8000')
    test_modules = data.get('modules', ['all'])
    
    def run_tests_thread():
        global test_running, test_progress, test_results, current_agent
        
        test_running = True
        test_progress = 0
        test_results = []
        # mark test window
        global test_started_at, test_finished_at
        test_started_at = time.time()
        test_finished_at = None
        
        try:
            def set_progress(pct: int):
                global test_progress
                test_progress = max(0, min(100, int(pct)))

            current_agent = StrictQAAgent(target_url, progress_callback=set_progress)
            
            # Normalize modules selection
            if (not test_modules) or ('all' in test_modules):
                summary = current_agent.run_all_tests()
            else:
                summary = current_agent.run_specific_tests(test_modules)
            
            test_results = current_agent.reporter.test_results
            test_progress = 100
            test_finished_at = time.time()
            
        except Exception as e:
            test_results.append({
                'Test Case': 'Test Execution',
                'Result': 'FAIL',
                'Details': f'Error: {str(e)}',
                'Test Type': 'System',
                'Severity': 'High',
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        finally:
            test_running = False
    
    # Start test execution in background thread
    global test_thread
    test_thread = threading.Thread(target=run_tests_thread)
    test_thread.daemon = True
    test_thread.start()
    
    return jsonify({'message': 'Tests started successfully'})

@app.route('/stop_tests', methods=['POST'])
def stop_tests():
    """Request to stop running tests"""
    global test_running, current_agent
    if not test_running:
        return jsonify({'message': 'No tests are running'})
    try:
        if current_agent:
            current_agent.request_stop()
        return jsonify({'message': 'Stop requested'})
    finally:
        # We mark running=false when the thread exits naturally
        pass

@app.route('/test_status')
def test_status():
    """Get current test execution status"""
    global test_running, test_progress, test_results
    
    return jsonify({
        'running': test_running,
        'progress': test_progress,
        'results': test_results
    })

@app.route('/test_results')
def get_test_results():
    """Get formatted test results with optional filtering and pagination"""
    global test_results

    # Early empty
    if not test_results:
        return jsonify({'results': [], 'summary': {}, 'page': 1, 'page_size': 0, 'total': 0})

    # Read filters
    status_filter = request.args.get('status')  # comma-separated
    type_filter = request.args.get('type')  # comma-separated
    severity_filter = request.args.get('severity')  # comma-separated
    search_query = request.args.get('search', '').strip().lower()
    try:
        page = max(1, int(request.args.get('page', '1')))
    except ValueError:
        page = 1
    try:
        page_size = max(1, min(500, int(request.args.get('page_size', '50'))))
    except ValueError:
        page_size = 50

    statuses = set([s.strip().upper() for s in status_filter.split(',')]) if status_filter else None
    types = set([t.strip() for t in type_filter.split(',')]) if type_filter else None
    severities = set([s.strip().capitalize() for s in severity_filter.split(',')]) if severity_filter else None

    # Apply filters
    def matches(r):
        if statuses and str(r.get('Result','')).upper() not in statuses:
            return False
        if types and str(r.get('Test Type','')) not in types:
            return False
        if severities and str(r.get('Severity','')).capitalize() not in severities:
            return False
        if search_query:
            blob = f"{r.get('Test Case','')} {r.get('Details','')} {r.get('Test Type','')} {r.get('Severity','')}".lower()
            if search_query not in blob:
                return False
        return True

    filtered = [r for r in test_results if matches(r)]

    # Calculate summary on filtered set
    total_tests = len(filtered)
    passed = sum(1 for r in filtered if r['Result'] == 'PASS')
    failed = sum(1 for r in filtered if r['Result'] == 'FAIL')
    bugs = sum(1 for r in filtered if r['Result'] == 'BUG')
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    security_tests = [r for r in filtered if r['Test Type'] == 'Security']
    security_passed = sum(1 for r in security_tests if r['Result'] == 'PASS')
    security_percentage = (security_passed / len(security_tests) * 100) if security_tests else 100

    # Execution time if available
    exec_seconds = None
    if test_started_at and test_finished_at:
        exec_seconds = max(0, test_finished_at - test_started_at)
    elif current_agent and current_agent.start_time and current_agent.end_time:
        exec_seconds = max(0, current_agent.end_time - current_agent.start_time)

    summary = {
        'total_tests': total_tests,
        'passed': passed,
        'failed': failed,
        'bugs': bugs,
        'pass_rate': round(pass_rate, 2),
        'security_percentage': round(security_percentage, 2),
        'execution_time': (round(exec_seconds, 2) if exec_seconds is not None else 'N/A')
    }

    # Pagination
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = filtered[start:end]

    return jsonify({
        'results': page_items,
        'summary': summary,
        'page': page,
        'page_size': page_size,
        'total': total
    })

@app.route('/download_report')
def download_report():
    """Download Excel report with custom filename"""
    filename = request.args.get('filename')
    suggested = filename
    
    # Derive a smart default filename based on tested site title/host if no filename provided
    if not suggested:
        site_title = None
        tested_host = 'localhost'
        try:
            from urllib.parse import urlparse
            if current_agent and current_agent.base_url:
                tested_host = urlparse(current_agent.base_url).hostname or 'localhost'
                # Try fetching HTML title for better naming
                try:
                    resp = requests.get(current_agent.base_url, timeout=5)
                    if resp.ok:
                        import re
                        m = re.search(r'<title[^>]*>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
                        if m:
                            site_title = m.group(1).strip()
                except Exception:
                    pass
        except Exception:
            tested_host = 'localhost'
        base_name = site_title or tested_host
        safe_base = ''.join(c if c.isalnum() or c in ('-', '_', ' ') else '-' for c in base_name).strip().replace(' ', '_')
        suggested = f"{safe_base}_qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filename = suggested if suggested.endswith('.xlsx') else f"{suggested}.xlsx"
    
    # Generate report
    if current_agent and current_agent.reporter.test_results:
        # Derive tested host for filename branding if not already present
        tested_host = ''
        try:
            from urllib.parse import urlparse
            tested_host = urlparse(current_agent.base_url).hostname or 'localhost'
        except Exception:
            tested_host = 'localhost'
        report_path = current_agent.reporter.generate_excel_report(filename, tested_host=tested_host)
        return send_file(report_path, as_attachment=True, download_name=filename)
    else:
        return jsonify({'error': 'No test results available'}), 400

@app.route('/download_csv')
def download_csv():
    """Download CSV report with custom filename"""
    filename = request.args.get('filename', f'qa_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    if not test_results:
        return jsonify({'error': 'No test results available'}), 400
    
    # Optional filtering via query params to honor UI filters
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    severity_filter = request.args.get('severity')
    search_query = request.args.get('search', '').strip().lower()

    filtered = test_results
    if status_filter or type_filter or severity_filter or search_query:
        statuses = set([s.strip().upper() for s in status_filter.split(',')]) if status_filter else None
        types = set([t.strip() for t in type_filter.split(',')]) if type_filter else None
        severities = set([s.strip().capitalize() for s in severity_filter.split(',')]) if severity_filter else None
        def matches(r):
            if statuses and str(r.get('Result','')).upper() not in statuses:
                return False
            if types and str(r.get('Test Type','')) not in types:
                return False
            if severities and str(r.get('Severity','')).capitalize() not in severities:
                return False
            if search_query:
                blob = f"{r.get('Test Case','')} {r.get('Details','')} {r.get('Test Type','')} {r.get('Severity','')}".lower()
                if search_query not in blob:
                    return False
            return True
        filtered = [r for r in test_results if matches(r)]

    # Create enhanced CSV with better formatting
    df = pd.DataFrame(filtered)
    
    # Add professional formatting
    def format_result(result):
        if result == 'PASS':
            return 'PASS'
        elif result == 'FAIL':
            return 'FAIL'
        elif result == 'BUG':
            return 'BUG'
        return result
    
    def format_severity(severity):
        if severity == 'High':
            return 'HIGH'
        elif severity == 'Medium':
            return 'MEDIUM'
        elif severity == 'Low':
            return 'LOW'
        elif severity == 'Critical':
            return 'CRITICAL'
        return severity
    
    # Apply formatting
    if not df.empty:
        df['Result'] = df['Result'].apply(format_result)
        df['Severity'] = df['Severity'].apply(format_severity)
    
    # Save to CSV
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    return send_file(csv_path, as_attachment=True, download_name=filename)

@app.route('/download_summary')
def download_summary():
    """Download comprehensive summary report"""
    filename = request.args.get('filename', f'qa_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    if not test_results:
        return jsonify({'error': 'No test results available'}), 400
    
    # Create comprehensive summary
    df = pd.DataFrame(test_results)
    
    # Calculate detailed statistics
    total_tests = len(test_results)
    passed = sum(1 for r in test_results if r['Result'] == 'PASS')
    failed = sum(1 for r in test_results if r['Result'] == 'FAIL')
    bugs = sum(1 for r in test_results if r['Result'] == 'BUG')
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    # Test type breakdown
    test_types = df['Test Type'].value_counts().to_dict()
    
    # Severity breakdown
    severity_counts = df['Severity'].value_counts().to_dict()
    
    # Security analysis
    security_tests = df[df['Test Type'] == 'Security']
    security_passed = len(security_tests[security_tests['Result'] == 'PASS'])
    security_percentage = (security_passed / len(security_tests) * 100) if len(security_tests) > 0 else 100
    
    # Create summary data
    summary_data = {
        'Metric': [
            'Total Tests Executed',
            'Tests Passed',
            'Tests Failed', 
            'Bugs Found',
            'Pass Rate (%)',
            'Security Tests',
            'Security Pass Rate (%)',
            'UI Tests',
            'API Tests',
            'Form Tests',
            'Navigation Tests'
        ],
        'Value': [
            total_tests,
            passed,
            failed,
            bugs,
            f"{pass_rate:.1f}%",
            len(security_tests),
            f"{security_percentage:.1f}%",
            test_types.get('UI', 0),
            test_types.get('API', 0),
            test_types.get('Form', 0),
            test_types.get('Navigation', 0)
        ]
    }
    
    # Create Excel file with multiple sheets
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Detailed results
        df.to_excel(writer, sheet_name='Test Results', index=False)
        
        # Bugs only
        bugs_df = df[df['Result'] == 'BUG']
        if not bugs_df.empty:
            bugs_df.to_excel(writer, sheet_name='Bugs Found', index=False)
        
        # Test type breakdown
        test_type_df = pd.DataFrame(list(test_types.items()), columns=['Test Type', 'Count'])
        test_type_df.to_excel(writer, sheet_name='Test Types', index=False)
        
        # Severity breakdown
        severity_df = pd.DataFrame(list(severity_counts.items()), columns=['Severity', 'Count'])
        severity_df.to_excel(writer, sheet_name='Severity Analysis', index=False)
    
    return send_file(report_path, as_attachment=True, download_name=filename)

@app.route('/download_csv_filtered', methods=['POST'])
def download_csv_filtered():
    """Download CSV for a provided result set (client-side filtered)."""
    data = request.get_json(silent=True) or {}
    rows = data.get('results') or []
    filename = data.get('filename') or f'qa_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    if not filename.endswith('.csv'):
        filename += '.csv'
    if not rows:
        return jsonify({'error': 'No results provided'}), 400
    df = pd.DataFrame(rows)
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    return send_file(csv_path, as_attachment=True, download_name=filename)

@app.route('/upload_report', methods=['POST'])
def upload_report():
    """Upload and analyze existing report"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read and analyze the file
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            # Convert to our format
            global test_results
            test_results = df.to_dict('records')
            # reset timing as this is an offline load
            global test_started_at, test_finished_at
            test_started_at = None
            test_finished_at = None
            
            return jsonify({'message': 'Report uploaded and analyzed successfully'})
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/charts_data')
def charts_data():
    """Get data for charts and visualizations"""
    if not test_results:
        return jsonify({})
    
    df = pd.DataFrame(test_results)
    
    # Test results pie chart
    result_counts = df['Result'].value_counts()
    results_pie = {
        'labels': result_counts.index.tolist(),
        'values': result_counts.values.tolist()
    }
    
    # Test types bar chart
    type_counts = df['Test Type'].value_counts()
    types_bar = {
        'x': type_counts.index.tolist(),
        'y': type_counts.values.tolist()
    }
    
    # Severity analysis
    severity_counts = df['Severity'].value_counts()
    severity_pie = {
        'labels': severity_counts.index.tolist(),
        'values': severity_counts.values.tolist()
    }
    
    # Timeline data
    try:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        timeline_data = df.groupby(df['Timestamp'].dt.date)['Result'].value_counts().unstack(fill_value=0)
        timeline = timeline_data.to_dict()
    except Exception:
        timeline = {}
    
    return jsonify({
        'results_pie': results_pie,
        'types_bar': types_bar,
        'severity_pie': severity_pie,
        'timeline': timeline
    })

@app.route('/clear_results', methods=['POST'])
def clear_results():
    """Clear all in-memory results and reset state."""
    global test_results, test_progress, test_running, current_agent, test_started_at, test_finished_at
    test_results = []
    test_progress = 0
    test_running = False
    current_agent = None
    test_started_at = None
    test_finished_at = None
    try:
        # Also clear reporter if available
        from utils.reporter import reporter as global_reporter
        global_reporter.clear_results()
    except Exception:
        pass
    return jsonify({'message': 'Results cleared'})

if __name__ == '__main__':
    # Create reports directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    print("🚀 Starting Strict QA Agent Web UI...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🎯 The UI will allow you to run tests, view results, and download reports!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
