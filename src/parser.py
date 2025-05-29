# src/parser.py
import argparse
import os
import zipfile
import git
import tempfile
import shutil

class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="AI Code Review Agent")
        self.parser.add_argument(
            "input_path", help="Path to codebase (folder, ZIP, or Git URL)"
        )
        self.parser.add_argument(
            "--output_path", default="output", help="Path for improved files"
        )
        self.parser.add_argument(
            "--report_path", default="reports", help="Path for reports"
        )
        self.parser.add_argument(
            "--priority", choices=["security", "performance", "readability"],
            default="readability", help="Review priority"
        )
        self.parser.add_argument(
            "--exclude", nargs="*", default=[], help="Files/directories to exclude"
        )
        self.parser.add_argument(
            "--aggressiveness", type=int, choices=[1, 2, 3], default=2,
            help="Improvement aggressiveness (1=low, 3=high)"
        )
        self.parser.add_argument(
            "--languages", nargs="*", default=["python", "javascript"],
            help="Languages to analyze"
        )

    def parse_args(self):
        """Parse and process input path, returning args and temp dir if needed."""
        args = self.parser.parse_args()
        temp_dir = None

        if args.input_path.endswith(".zip"):
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(args.input_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            args.input_path = temp_dir
        elif args.input_path.startswith(("http://", "https://", "git@")):
            temp_dir = tempfile.mkdtemp()
            git.Repo.clone_from(args.input_path, temp_dir)
            args.input_path = temp_dir

        return args, temp_dir

    def cleanup(self, temp_dir):
        """Clean up temporary directory if used."""
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
