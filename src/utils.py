# src/utils.py
import os
import shutil
import subprocess
import glob

def backup_codebase(input_path, backup_path):
    """Backup codebase before processing."""
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)
    shutil.copytree(input_path, backup_path)

def run_tests(path):
    """Run unit tests in path."""
    try:
        test_files = glob.glob(os.path.join(path, "tests/test_*.py"))
        if test_files:
            result = subprocess.run(
                ["pytest", *test_files, "--verbose"],
                capture_output=True, text=True
            )
            return result.stdout
        return "No tests found"
    except Exception as e:
        return f"Test error: {str(e)}"

def parse_dependencies(path):
    """Parse dependencies (FR-1.4)."""
    req_file = os.path.join(path, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, "r") as f:
            return f.read().splitlines()
    return []
