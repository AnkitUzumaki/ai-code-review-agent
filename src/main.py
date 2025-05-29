# ai_code_review_agent/src/main.py
import argparse
import os
import yaml
from src.parser import parse_input, categorize_files, get_dependencies
from src.analyzer import Analyzer
from src.improver import Improver
from src.reporter import Reporter
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description="Process input directory and generate output files and report.")
    parser.add_argument("input_path", help="Path to input directory or zip file")
    parser.add_argument("--output_path", type=str, default="output", help="Path to save improved files")
    parser.add_argument("--report_path", type=str, default="reports", help="Path to save report")
    args = parser.parse_args()

    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    exclude_files = config.get("exclude_files", [])

    # Create output and report directories
    os.makedirs(args.output_path, exist_ok=True)
    os.makedirs(args.report_path, exist_ok=True)

    # Parse input
    input_path = parse_input(args.input_path)
    files = categorize_files(input_path, exclude_files)
    dependencies = get_dependencies(input_path)

    # Analyze and improve files
    analyzer = Analyzer()
    improver = Improver()
    issues = []

    for file_path in tqdm(files, desc="Processing files"):
        file_issues = analyzer.analyze_file(file_path)
        issues.append((file_path, file_issues))

        # Copy to output and improve
        relative_path = os.path.relpath(file_path, input_path)
        output_file = os.path.join(args.output_path, relative_path)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        improver.improve_file(file_path, output_file)

    # Generate report
    reporter = Reporter()
    reporter.generate_report(issues, dependencies, config, args.report_path, args.input_path, args.output_path)

if __name__ == "__main__":
    main()