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
