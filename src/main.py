# src/main.py
import os
import logging
from multiprocessing import Pool
from src.parser import Parser
from src.analyzer import Analyzer
from src.improver import Improver
from src.reporter import Reporter
from src.config import Config
from src.utils import backup_codebase, run_tests

logging.basicConfig(filename="code_review.log", level=logging.INFO)

def process_file(args):
    file_path, output_path, config = args
    analyzer = Analyzer(config.priority)
    improver = Improver(config.aggressiveness)
    category = analyzer.categorize_file(file_path)
    if any(excl in file_path for excl in config.exclude):
        logging.info(f"Skipping excluded file: {file_path}")
        return None
    issues = analyzer.analyze_file(file_path, config.languages)
    original, improved = improver.improve_file(file_path, output_path, file_path.endswith(".js") and "javascript" or "python")
    return {"file": file_path, "category": category, "issues": issues, "original": original, "improved": improved}

def main():
    parser = Parser()
    args, temp_dir = parser.parse_args()
    config = Config(args)
    reporter = Reporter()

    logging.info(f"Starting review for {args.input_path}")
    backup_codebase(args.input_path, "backup/")

    # Run original tests
    test_results = run_tests(args.input_path)
    logging.info(f"Original test results: {test_results}")

    os.makedirs(args.output_path, exist_ok=True)
    os.makedirs(args.report_path, exist_ok=True)

    files_to_process = []
    for root, _, files in os.walk(args.input_path):
        for file in files:
            if file.endswith((".py", ".js")):
                input_file = os.path.join(root, file)
                rel_path = os.path.relpath(input_file, args.input_path)
                output_file = os.path.join(args.output_path, rel_path)
                files_to_process.append((input_file, output_file, config))

    # Parallel processing
    with Pool() as pool:
        results = pool.map(process_file, files_to_process)

    # Generate report
    reporter.generate_report(results, args.report_path, config)

    # Run tests on improved code
    improved_test_results = run_tests(args.output_path)
    logging.info(f"Improved test results: {improved_test_results}")

    parser.cleanup(temp_dir)
    logging.info("Review completed")

if __name__ == "__main__":
    main()
