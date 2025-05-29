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
