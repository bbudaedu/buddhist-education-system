import argparse
import os
import json
import subprocess

def run_command(command, cwd=None):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def get_git_branch():
    return run_command("git rev-parse --abbrev-ref HEAD")

def generate_pr_description(title, body, report_path):
    """Generates the PR description content."""
    
    description = f"# {title}\n\n"
    description += f"{body}\n\n"
    
    description += "## 🔍 Static Analysis Report\n"
    if os.path.exists(report_path):
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            status_icon = "✅" if report.get("summary") == "Passed" else "❌"
            description += f"- **Status**: {status_icon} {report.get('summary')}\n"
            description += f"- **Timestamp**: {report.get('timestamp')}\n"
            
            if not report.get("lint", {}).get("success"):
                description += "\n<details><summary>Lint Errors</summary>\n\n```\n"
                description += report["lint"]["output"][-1000:] # Limit output size
                description += "\n```\n</details>\n"
                
            if not report.get("type_check", {}).get("success"):
                description += "\n<details><summary>Type Check Errors</summary>\n\n```\n"
                description += report["type_check"]["output"][-1000:] # Limit output size
                description += "\n```\n</details>\n"
                
        except Exception as e:
            description += f"Failed to read report: {str(e)}\n"
    else:
        description += "No static analysis report found.\n"
        
    return description

def main():
    parser = argparse.ArgumentParser(description="Generate PR Description and Create PR")
    parser.add_argument("--title", required=True, help="PR Title")
    parser.add_argument("--body", required=True, help="PR Body/Description")
    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("--dry-run", action="store_true", help="Print description without creating PR")
    
    args = parser.parse_args()
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    report_path = os.path.join(project_root, "reports", "static_analysis_report.json")
    
    current_branch = get_git_branch()
    
    full_description = generate_pr_description(args.title, args.body, report_path)
    
    if args.dry_run:
        print("--- PR Description Preview ---")
        print(full_description)
        print("------------------------------")
    else:
        # Try to use gh cli if available
        # This is a simplified implementation. In a real scenario, we might use the GitHub API directly
        # or assume the user will copy-paste if gh is not installed.
        # For this agent, we will print the content for the agent to use in the `create_pull_request` tool.
        print("PR_TITLE_START")
        print(args.title)
        print("PR_TITLE_END")
        
        print("PR_BODY_START")
        print(full_description)
        print("PR_BODY_END")
        
        print(f"SUGGESTED_COMMAND: gh pr create --title \"{args.title}\" --body-file - --base {args.base} --head {current_branch}")

if __name__ == "__main__":
    main()
