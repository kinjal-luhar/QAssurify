import os
import threading
import queue
import time
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, send_file

from main import StrictQAAgent
from utils.reporter import QAReporter


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Shared state
    state: Dict[str, Any] = {
        "is_running": False,
        "progress": 0,
        "summary": None,
        "started_at": None,
        "ended_at": None,
        "last_report_file": None,
        "errors": [],
        "results": [],
        "recommendations": [],
        "base_url": None,
        "mode": "full",  # Track current test mode
    }

    # Background worker thread
    worker_thread: Optional[threading.Thread] = None
    agent_instance: Optional[StrictQAAgent] = None

    def run_agent(base_url: str, save_dir: Optional[str], fast_mode: bool = False):
        # Initialize state
        state["is_running"] = True
        state["progress"] = 0
        state["summary"] = None
        state["started_at"] = datetime.now()
        state["ended_at"] = None
        state["errors"].clear()
        state["results"] = []
        state["recommendations"] = []
        state["base_url"] = base_url
        state["mode"] = "fast" if fast_mode else "full"
        state["cancel_requested"] = False

        # Set up report directory
        report_dir = save_dir or "reports"
        if fast_mode:
            report_dir = os.path.join(report_dir, "fast_mode")
            
        def on_progress(pct: int):
            state["progress"] = max(0, min(100, int(pct)))

        try:
            # Create and configure reporter
            reporter = QAReporter(report_dir=report_dir)
            reporter.set_progress_callback(on_progress)
            
            # Create QA agent with proper parameters
            nonlocal agent_instance
            agent_instance = StrictQAAgent(
                base_url=base_url,
                mode="fast" if fast_mode else "full",
                headless=True,  # Always run headless in web UI
                reporter=reporter
            )
            
            # Run tests and collect results
            summary = agent_instance.run_all_tests()
            
            if not state["cancel_requested"]:
                state["results"] = list(reporter.test_results)
                state["summary"] = {
                    "total_tests": reporter.total_tests,
                    "passed": reporter.pass_count,
                    "failed": reporter.fail_count,
                    "bugs_found": reporter.bug_count,
                    "execution_time": summary.get("execution_time", 0)
                }
                
                # Generate recommendations if available
                try:
                    state["recommendations"] = reporter._create_recommendations()
                except Exception:
                    state["recommendations"] = []
                
                # Generate report file
                safe_host = base_url.replace("http://", "").replace("https://", "").replace("/", "-")
                date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                mode_str = "_fast" if fast_mode else ""
                fname = f"{safe_host}_qa{mode_str}_{date_str}_P{reporter.pass_count}_F{reporter.fail_count}_B{reporter.bug_count}.xlsx"
                state["last_report_file"] = reporter.generate_excel_report(filename=fname, tested_host=safe_host)
                
        except Exception as e:
            state["errors"].append(str(e))
            
        finally:
            state["ended_at"] = datetime.now()
            state["progress"] = 100
            state["is_running"] = False

    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/history")
    def history():
        return render_template("history.html")

    @app.route("/insights")
    def insights():
        return render_template("insights.html")

    @app.route("/run", methods=["POST"])
    def run_tests():
        nonlocal worker_thread
        if state["is_running"]:
            return jsonify({"ok": False, "message": "A run is already in progress."}), 409

        # Get request parameters with defaults
        data = request.get_json(silent=True) or {}
        base_url = data.get("baseUrl") or "http://127.0.0.1:8000"
        save_dir = data.get("saveDir")
        
        # Handle test mode parameter
        test_mode = data.get("mode", "full").lower()
        if test_mode not in ["fast", "full"]:
            test_mode = "full"  # Default to full mode if invalid
        fast_mode = (test_mode == "fast")

        # Ensure save directory exists
        if save_dir:
            try:
                os.makedirs(save_dir, exist_ok=True)
            except Exception as e:
                return jsonify({"ok": False, "message": f"Cannot create save directory: {e}"}), 400

        # Reset and initialize state
        state["is_running"] = True
        state["progress"] = 1
        state["mode"] = test_mode
        state["summary"] = None
        state["errors"].clear()
        state["results"] = []
        state["started_at"] = datetime.now()
        state["ended_at"] = None
        state["base_url"] = base_url
        state["cancel_requested"] = False

        # Start background worker
        worker_thread = threading.Thread(target=run_agent, args=(base_url, save_dir, fast_mode), daemon=True)
        worker_thread.start()
        return jsonify({"ok": True})

    @app.route("/status")
    def status():
        # Get agent status if it exists
        agent_status = None
        if agent_instance and agent_instance.reporter:
            agent_status = agent_instance.reporter.get_status()

        status_obj = {
            "status": "cancelled" if state.get("cancel_requested", False) else 
                     "running" if state["is_running"] else "idle",
            "mode": state["mode"],
            "total_tests": agent_status["total_tests"] if agent_status else 0,
            "completed_tests": agent_status["completed_tests"] if agent_status else 0,
            "percent": agent_status["percent"] if agent_status else 0,
            "progress": state["progress"],
            "summary": state["summary"],
            "startedAt": agent_status["start_time"] if agent_status else 
                        (state["started_at"].isoformat() if state["started_at"] else None),
            "endedAt": agent_status["end_time"] if agent_status else 
                      (state["ended_at"].isoformat() if state["ended_at"] else None),
            "errors": state["errors"],
            "lastReportFile": state["last_report_file"],
            "results": state["results"],
            "recommendations": state["recommendations"]
        }
        return jsonify(status_obj)

    @app.route("/cancel", methods=["POST"])
    def cancel():
        state["cancel_requested"] = True
        if agent_instance:
            agent_instance.request_cancel()
        return jsonify({"ok": True, "status": "cancelled"})

    @app.route("/reports")
    def list_reports():
        # Default reports directory
        reports_dir = request.args.get("dir") or "reports"
        try:
            files = []
            if os.path.isdir(reports_dir):
                for name in sorted(os.listdir(reports_dir), reverse=True):
                    if name.lower().endswith((".xlsx", ".csv")):
                        path = os.path.join(reports_dir, name)
                        files.append({
                            "name": name,
                            "path": path,
                            "size": os.path.getsize(path),
                            "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
                        })
            return jsonify({"ok": True, "files": files, "dir": reports_dir})
        except Exception as e:
            return jsonify({"ok": False, "message": str(e)}), 500

    @app.route("/download")
    def download():
        path = request.args.get("path")
        if not path or not os.path.isfile(path):
            return jsonify({"ok": False, "message": "File not found"}), 404
        return send_file(path, as_attachment=True)

    @app.route("/export", methods=["POST"])
    def export():
        data = request.get_json(silent=True) or {}
        fmt = (data.get("format") or "csv").lower()
        directory = data.get("directory") or (state.get("last_report_file") and os.path.dirname(state["last_report_file"]) or "reports")
        filename = data.get("filename")  # optional, when not provided we auto-name

        os.makedirs(directory, exist_ok=True)

        # Build dataframe from current results
        try:
            import pandas as pd
            rows = state.get("results") or []
            if not rows:
                return jsonify({"ok": False, "message": "No results available to export"}), 400
            df = pd.DataFrame(rows)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not filename:
                filename = f"qassurify_results_{timestamp}.{ 'xlsx' if fmt=='excel' else 'csv'}"
            path = os.path.join(directory, filename)
            if fmt == 'excel':
                df.to_excel(path, index=False)
            else:
                df.to_csv(path, index=False)
            return jsonify({"ok": True, "path": path})
        except Exception as e:
            return jsonify({"ok": False, "message": str(e)}), 500

    @app.route("/tested-data")
    def tested_data():
        # Return actual results from the latest real run — no dummy examples
        try:
            results = state.get("results") or []
            summary = state.get("summary")
            base_url = state.get("base_url")

            weaknesses = [r for r in results if str(r.get("Result")).upper() in ("BUG", "FAIL")]

            return jsonify({
                "ok": True,
                "data": {
                    "base_url": base_url,
                    "summary": summary,
                    "results": results,
                    "weaknesses": weaknesses
                }
            })
        except Exception as e:
            return jsonify({"ok": False, "message": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    # Disable debug auto-reloader to avoid interfering with background threads on Windows
    app.run(host="0.0.0.0", port=5001, debug=False)


