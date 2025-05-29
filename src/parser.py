# ai_code_review_agent/src/parser.py
import os
import glob
import zipfile

def parse_input(input_path):
    """Parse input path, extracting ZIP if provided."""
    if input_path.endswith(".zip"):
        extract_path = "input"
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        return extract_path
    return input_path

def categorize_files(input_path, exclude_files):
    """Categorize Python files, excluding specified patterns."""
    files = glob.glob(f"{input_path}/**/*.py", recursive=True)
    return [f for f in files if not any(glob.fnmatch.fnmatch(f, ex) for ex in exclude_files)]

def get_dependencies(input_path):
    """Retrieve dependencies from requirements.txt."""
    req_file = os.path.join(input_path, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []