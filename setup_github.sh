#!/bin/bash

# setup_github.sh
# Automates setup and push of AI Code Review Agent to GitHub
# Run: bash setup_github.sh

# Exit on error
set -e

# Project directory
PROJECT_DIR="/home/uzumaki007/ai_code_review_agent"
REPO_URL="https://github.com/AnkitUzumaki/ai-code-review-agent.git"

# Navigate to project
cd "$PROJECT_DIR" || { echo "Directory $PROJECT_DIR not found"; exit 1; }

# Create .gitignore
cat << 'EOF' > .gitignore
# Python
*.pyc
__pycache__/
*.pyo
*.pyd
.Python
env/
.venv*/
venv/
*.egg-info/
dist/
build/
*.egg

# PyCharm
.idea/

# Outputs
output/
reports/

# Misc
*.log
*.swp
.DS_Store
EOF
echo "Created .gitignore"

# Create .ruff.toml
cat << 'EOF' > .ruff.toml
[tool.ruff]
select = ["F", "W", "C", "D", "UP"]
extend-select = ["UP031"]
EOF
echo "Created .ruff.toml"

# Create GitHub Actions workflow
mkdir -p .github/workflows
cat << 'EOF' > .github/workflows/ci.yml
name: CI for AI Code Review Agent

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install --no-cache-dir autopep8 ruff pylint bandit radon
    - name: Run AI Code Review Agent
      run: |
        python src/main.py input/ --output_path output --report_path reports
    - name: Check outputs
      run: |
        ls -l output/
        ls -l reports/
        cat output/test.py
        cat output/test2.py
        cat output/test3.py
    - name: Upload output files
      uses: actions/upload-artifact@v4
      with:
        name: output-files
        path: output/
    - name: Upload report
      uses: actions/upload-artifact@v4
      with:
        name: report
        path: reports/report.html
EOF
echo "Created .github/workflows/ci.yml"

# Update improver.py
cat << 'EOF' > src/improver.py
# /home/uzumaki007/ai_code_review_agent/src/improver.py
import autopep8
import ast
import re
import os

class Improver:
    def improve_file(self, input_path, output_path):
        """Improve a Python file by formatting and fixing issues."""
        try:
            with open(input_path, "r") as f:
                code = f.read()

            # Format with autopep8 to ensure f-strings
            formatted = autopep8.fix_code(
                code,
                options={
                    "experimental": True,
                    "max_line_length": 88,
                    "aggressive": 2
                }
            )

            # Fallback regex for f-strings
            def convert_to_fstring(code):
                pattern = r'print\("([^"]+)"\s*\+\s*(\w+)\)'
                replacement = r'print(f"\1{\2}")'
                code = re.sub(pattern, replacement, code)
                pattern = r'print\("([^"]+)"\s*\+\s*(\w+)\s*\+\s*"([^"]+)"\)'
                replacement = r'print(f"\1{\2}\3")'
                return re.sub(pattern, replacement, code)
            formatted = convert_to_fstring(formatted)

            # Parse AST for docstrings and unused variables
            tree = ast.parse(formatted)
            modified = False

            # Identify unused variables
            assignments = {}
            uses = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assignments[target.id] = node
                if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Store):
                    uses.add(node.id)

            # Remove unused variables
            unused = set(assignments.keys()) - uses
            if unused:
                new_body = []
                for node in tree.body:
                    if isinstance(node, ast.Assign) and any(target.id in unused for target in node.targets if isinstance(target, ast.Name)):
                        continue
                    new_body.append(node)
                tree.body = new_body
                modified = True

            # Add docstrings
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not ast.get_docstring(node):
                    node.body.insert(0, ast.Expr(ast.Constant(value=f"Docstring for {node.name}")))
                    modified = True
            if not ast.get_docstring(tree):
                tree.body.insert(0, ast.Expr(ast.Constant(value="Module docstring")))
                modified = True

            # Security fix for hardcoded secrets
            formatted = ast.unparse(tree) if modified else formatted
            formatted = re.sub(r'(password|api_key)\s*=\s*["\'][\w]+["\']', r'\1 = os.getenv("\1".upper())', formatted)

            # Add import os only if os.getenv is used
            if "os.getenv" in formatted:
                tree = ast.parse(formatted)
                if not any(isinstance(node, ast.Import) and any(alias.name == "os" for alias in node.names) for node in tree.body):
                    tree.body.insert(0, ast.Import(names=[ast.alias(name="os")]))
                    formatted = ast.unparse(tree)

            # Ensure trailing newline
            if not formatted.endswith("\n"):
                formatted += "\n"

            # Write output
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(formatted)
        except Exception as e:
            print(f"Error improving {input_path}: {str(e)}")
EOF
echo "Updated src/improver.py"

# Update analyzer.py
cat << 'EOF' > src/analyzer.py
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
EOF
echo "Updated src/analyzer.py"

# Create input files if they don't exist
mkdir -p input
cat << 'EOF' > input/test.py
def greet(name):
    print("Hello, " + name)
    password = "secret123"
EOF
cat << 'EOF' > input/test2.py
def calculate_sum(a, b):
    result = a + b
    very_long_variable_name_to_trigger_line_length_issue = 42
    return result

def greet_user(name):
    print("Hello, " + name + ", welcome!")
EOF
cat << 'EOF' > input/test3.py
def fetch_data_from_api(url, api_key="abc123"):
    import requests
    response = requests.get(url + "?key=" + api_key)
    unused_data = response.json()
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print("Error: Resource not found")
    else:
        raise Exception("API request failed with status: " + str(response.status_code))
EOF
echo "Created/updated input/test.py, input/test2.py, input/test3.py"

# Update documentation
cat << 'EOF' > APPROACH_AND_TOOLS.md
# Approach and Tools
## Overview
AI Code Review Agent automates code analysis and improvement using Ruff, Pylint, Bandit, and Radon.

## Tools Used
- **Ruff**: Linting and f-string detection (UP031).
- **autopep8**: Code formatting with f-string conversion.
- **Pylint**: Static analysis.
- **Bandit**: Security checks.
- **Radon**: Complexity analysis.

## Additional Doubts Resolved
- **F-string issue**: Used autopep8 with aggressive=2, added regex fallback.
- **Ruff**: Fixed UP031 with .ruff.toml and --no-cache.
- **GitHub**: Automated upload and CI setup.
EOF
cat << 'EOF' > GAPS_AND_CHALLENGES.md
# Gaps and Challenges
## 1. Advanced Code Review Expertise
**Progress**: Fixed f-strings with autopep8 and regex, added GitHub Actions CI.
**Remaining**: Further testing (~1 hour).
## 5. Scale and Performance
**Remaining**: Add multiprocessing (~2–3 hours).
EOF
echo "Updated APPROACH_AND_TOOLS.md and GAPS_AND_CHALLENGES.md"

# Verify Git setup
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    git init
    git branch -m main
fi

# Set up remote
if ! git remote get-url origin > /dev/null 2>&1; then
    git remote add origin "$REPO_URL"
fi

# Commit and push
git add .
git commit -m "Automated setup of AI Code Review Agent with f-string fixes and CI"
echo "Pushing to GitHub..."
git push -u origin main || {
    echo "Push failed. Please enter your GitHub credentials or use a Personal Access Token."
    echo "To generate a token: GitHub > Settings > Developer settings > Personal access tokens > Generate new token (select 'repo' scope)."
    exit 1
}

echo "Successfully pushed to $REPO_URL"
echo "Next steps:"
echo "1. Visit $REPO_URL/actions to monitor the CI workflow."
echo "2. Check logs for UP031 and download 'output-files' artifact to verify f-strings."
echo "3. Run locally to compare: /home/uzumaki007/ai_code_review_agent/.venv1/bin/python src/main.py input/ --output_path output --report_path reports"
