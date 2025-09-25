import os
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, send_file

from main import StrictQAAgent
from main import _normalize_base_url
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
    }

    # Background worker thread
    worker_thread: Optional[threading.Thread] = None

    def run_agent(base_url: str, save_dir: Optional[str]):
        state["is_running"] = True
        state["progress"] = 0
        state["summary"] = None
        state["started_at"] = datetime.now()
        state["ended_at"] = None
        state["errors"].clear()
        state["results"] = []  # ensure dashboard shows only current run
        state["recommendations"] = []
        state["base_url"] = base_url

        # Integrate a reporter that saves into chosen directory if provided
        reporter = QAReporter(report_dir=save_dir or "reports")

        def on_progress(pct: int):
            state["progress"] = max(0, min(100, int(pct)))

        agent = StrictQAAgent(base_url=base_url, progress_callback=on_progress)
        # Inject our reporter so UI and CLI share logic
        agent.reporter = reporter
        # Apply strategy if provided by UI
        try:
            strat = state.get("strategy") or {}
            agent.configure_suite(
                test_type=strat.get("test_type", "e2e"),
                include_api=bool(strat.get("include_api", True)),
                include_security=bool(strat.get("include_security", False)),
            )
        except Exception:
            pass

        try:
            summary = agent.run_all_tests()
            state["summary"] = summary
            state["results"] = list(reporter.test_results)
            try:
                # Best-effort: generate recommendations from reporter
                state["recommendations"] = reporter._create_recommendations()
            except Exception:
                state["recommendations"] = []
            # Build a readable filename for long-term history
            safe_host = base_url.replace("http://", "").replace("https://", "").replace("/", "-")
            date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
            fname = f"{safe_host}_qa_{date_str}_P{reporter.pass_count}_F{reporter.fail_count}_B{reporter.bug_count}.xlsx"
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

        data = request.get_json(silent=True) or {}
        base_url = _normalize_base_url(data.get("baseUrl") or "http://127.0.0.1:8000")
        test_type = (data.get("testType") or "e2e").lower()
        include_api = bool(data.get("includeApi", True))
        include_security = bool(data.get("includeSecurity", False))
        save_dir = data.get("saveDir")

        # Ensure save dir exists if provided
        if save_dir:
            try:
                os.makedirs(save_dir, exist_ok=True)
            except Exception as e:
                return jsonify({"ok": False, "message": f"Cannot create save directory: {e}"}), 400

        # Set immediate running state so the UI sees progress instantly
        state["is_running"] = True
        state["progress"] = 1
        state["summary"] = None
        state["errors"].clear()
        state["results"] = []
        state["started_at"] = datetime.now()
        state["ended_at"] = None
        state["base_url"] = base_url

        # Attach chosen strategy to state so runner can pick modules accordingly
        state["strategy"] = {
            "test_type": test_type,
            "include_api": include_api,
            "include_security": include_security,
        }
        worker_thread = threading.Thread(target=run_agent, args=(base_url, save_dir), daemon=True)
        worker_thread.start()
        return jsonify({"ok": True})

    @app.route("/status")
    def status():
        return jsonify({
            "running": state["is_running"],
            "progress": state["progress"],
            "summary": state["summary"],
            "startedAt": state["started_at"].isoformat() if state["started_at"] else None,
            "endedAt": state["ended_at"].isoformat() if state["ended_at"] else None,
            "errors": state["errors"],
            "lastReportFile": state["last_report_file"],
            "results": state["results"],
            "recommendations": state["recommendations"],
        })

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
    app.run(host="0.0.0.0", port=5000, debug=False)


