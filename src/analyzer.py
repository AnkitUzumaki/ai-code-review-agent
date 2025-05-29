# src/analyzer.py
import subprocess
import json
import os
import cProfile
import pstats
from pylint.lint import Run
from pylint.reporters import CollectingReporter
from bandit.core import manager as bandit_manager
from bandit.core import config as bandit_config
from radon.complexity import cc_visit

class Analyzer:
    def __init__(self, priority="readability"):
        self.priority = priority

    def analyze_file(self, file_path, languages=["python"]):
        """Analyze a file based on language, returning issues."""
        issues = []
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".py" and "python" in languages:
            issues.extend(self._analyze_python(file_path))
        elif file_ext == ".js" and "javascript" in languages:
            issues.extend(self._analyze_javascript(file_path))

        # Performance profiling
        profiler = cProfile.Profile()
        profiler.enable()
        self._analyze_python(file_path) if file_ext == ".py" else self._analyze_javascript(file_path)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("cumulative")
        issues.append(f"Performance profile for {file_path}: {stats.total_tt:.2f}s")

        return issues

    def _analyze_python(self, file_path):
        issues = []
        # Ruff
        try:
            result = subprocess.run(
                ["ruff", "check", file_path, "--output-format=json", "--select=F,W,C,D,UP", "--extend-select=UP031", "--no-cache"],
                capture_output=True, text=True, check=False
            )
            if result.stdout.strip():
                ruff_issues = json.loads(result.stdout)
                issues.extend([f"{file_path}:{issue['location']['row']}:{issue['location']['column']}:{issue['code']} {issue['message']}" for issue in ruff_issues])
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
            b_mgr = bandit_manager.BanditManager(config=b_config, agg_type="file")
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
            issues.append(f"Complexity for {file_path}: {complexity}")
        except Exception as e:
            issues.append(f"Radon error: {str(e)}")

        return issues

    def _analyze_javascript(self, file_path):
        issues = []
        try:
            result = subprocess.run(
                ["eslint", file_path, "--format=json"],
                capture_output=True, text=True, check=False
            )
            if result.stdout.strip():
                eslint_issues = json.loads(result.stdout)
                for issue in eslint_issues[0]["messages"]:
                    issues.append(f"{file_path}:{issue['line']}:{issue['column']}:{issue['ruleId']} {issue['message']}")
        except Exception as e:
            issues.append(f"ESLint error: {str(e)}")
        return issues

    def categorize_file(self, file_path):
        """Categorize file by functionality (FR-1.3)."""
        name = os.path.basename(file_path).lower()
        if "test" in name or name.startswith("test_"):
            return "test"
        elif "util" in name or "helper" in name:
            return "utility"
        else:
            return "core"
