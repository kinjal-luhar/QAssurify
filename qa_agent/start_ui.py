"""
Start the Strict QA Agent Web UI
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🚀 Starting Strict QA Agent Web UI...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🎯 Professional UI with organized statistics and corporate-friendly reports!")
    print("=" * 70)
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
