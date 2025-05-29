# /home/uzumaki007/ai_code_review_agent/src/analyzer.py
import subprocess
import json
from pylint.lint import Run
from pylint.reporters import CollectingReporter
from bandit.core import manager as bandit_manager
from bandit.core import config as bandit_config
from radon.complexity import cc_visit

class Analyzer:
    @staticmethod
    def analyze_file(file_path):
        """Analyze a Python file for issues using Ruff, Pylint, Bandit, and Radon."""
        issues = []
        # Ruff
        try:
            result = subprocess.run(
                ["ruff", "check", file_path, "--output-format=json", "--select=F,W,C,D,UP", "--extend-select=UP031", "--no-cache"],
                capture_output=True,
                text=True,
                check=False
            )
            stats = []
            if result.stdout.strip():
                try:
                    ruff_issues = json.loads(result.stdout)
                    for issue in ruff_issues:
                        stats.append(f"{issue['location']['row']}:{issue['location']['column']}:{issue['code']} {issue['message']}")
                except json.JSONDecodeError:
                    issues.append(f"Ruff error: Invalid JSON output for {file_path}")
            issues.extend([f"{file_path}:{stat}" for stat in stats])
        except Exception as e:
            issues.append(f"Ruff error: {str(e)}")

        # Pylint
        try:
            reporter = CollectingReporter()
            Run([file_path], reporter=reporter, exit=False)
            issues.extend([f"{file_path}:{msg.line}:{msg.msg_id} {msg.msg}" for msg in reporter.messages])
        except Exception as e:
            issues.append(f"Pylint error: {str(e)}")

        # Bandit
        try:
            b_config = bandit_config.BanditConfig()
            b_mgr = bandit_manager.BanditManager(config=b_config, agg_type='file')
            b_mgr.discover_files([file_path], recursive=False)
            b_mgr.run_tests()
            issues.extend([f"{file_path}:{issue.test_id}:{issue.severity}:{issue.text}" for issue in b_mgr.get_issue_list()])
        except Exception as e:
            issues.append(f"Bandit error: {str(e)}")

        # Radon
        try:
            with open(file_path, "r") as f:
                code = f.read()
            complexity = cc_visit(code)
            issues.append(f"Complexity: {complexity}")
        except Exception as e:
            issues.append(f"Radon error: {str(e)}")

        # Print issues
        for issue in issues:
            print(issue)
        return issues
