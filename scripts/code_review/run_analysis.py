import subprocess
import json
import os
import sys
from datetime import datetime

def run_command(command, cwd=None):
    """Run a shell command and return output."""
    try:
        # Force UTF-8 encoding and replace errors to avoid crashes on Windows
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    ts_project_path = os.path.join(project_root, "Line-bot-llm-mysql")
    report_dir = os.path.join(project_root, "reports")
    
    # Ensure report directory exists
    os.makedirs(report_dir, exist_ok=True)
    
    print(f"Starting Static Analysis in {ts_project_path}...")
    
    # 1. Run ESLint
    print("Running ESLint...")
    lint_result = run_command("npm run lint", cwd=ts_project_path)
    
    # 2. Run TypeScript Compiler (Type Check)
    print("Running Type Check...")
    tsc_result = run_command("npx tsc --noEmit", cwd=ts_project_path)
    
    # 3. Generate Report
    report = {
        "timestamp": datetime.now().isoformat(),
        "lint": {
            "success": lint_result["success"],
            "output": lint_result["stdout"] + lint_result["stderr"]
        },
        "type_check": {
            "success": tsc_result["success"],
            "output": tsc_result["stdout"] + tsc_result["stderr"]
        },
        "summary": "Passed" if lint_result["success"] and tsc_result["success"] else "Failed"
    }
    
    report_path = os.path.join(report_dir, "static_analysis_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"Analysis complete. Report saved to {report_path}")
    
    if not report["lint"]["success"]:
        print("Linting failed.")
    if not report["type_check"]["success"]:
        print("Type checking failed.")
        
    # Return exit code based on success
    sys.exit(0 if report["summary"] == "Passed" else 1)

if __name__ == "__main__":
    main()
