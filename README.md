# AI Code Review Agent

This is an AI-powered code review tool that analyzes Python codebases, identifies issues (syntax errors, security vulnerabilities, style violations, complexity), and generates improved code with formatted output and detailed reports. The tool meets the requirements of a Functional Requirements Document (FRD) for an AI Code Review Agent.

## Features
- **Input Processing**: Accepts folder paths or ZIP files, categorizes Python files, and parses dependencies.
- **Code Analysis**: Uses Pylint (syntax), Flake8 (style), Bandit (security), and Radon (complexity).
- **Code Improvement**: Formats code with Black, replaces hardcoded secrets, and adds docstrings.
- **Output Generation**: Creates an output folder with improved code and an HTML report with metrics and charts.
- **Configuration**: Supports user-defined priorities and file exclusions via `config.yaml`.
- **CLI**: Command-line interface with progress indicators using `tqdm`.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai_code_review_agent.git
   cd ai_code_review_agent
## Documentation
- [Gaps and Challenges](GAPS_AND_CHALLENGES.md): Details gaps in my skills relative to the FRD and solutions.
- [Approach and Tools](APPROACH_AND_TOOLS.md): Explains my hands-on coding approach and use of internet resources to resolve doubts.
