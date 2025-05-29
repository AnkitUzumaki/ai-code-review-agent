# src/improver.py
import autopep8
import ast
import re
import os
from memory_profiler import profile

class Improver:
    def __init__(self, aggressiveness=2):
        self.aggressiveness = aggressiveness

    @profile
    def improve_file(self, input_path, output_path, language="python"):
        """Improve a file, preserving functionality."""
        try:
            with open(input_path, "r") as f:
                code = f.read()

            if language == "python":
                improved = self._improve_python(code)
            elif language == "javascript":
                improved = self._improve_javascript(code)
            else:
                improved = code

            # Security fixes
            improved = self._secure_code(improved, language)

            # Optimize performance
            improved = self._optimize_performance(improved, language)

            # Ensure trailing newline
            if not improved.endswith("\n"):
                improved += "\n"

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(improved)

            return code, improved  # Return original and improved for diff
        except Exception as e:
            print(f"Error improving {input_path}: {str(e)}")
            return code, code

    def _improve_python(self, code):
        # Format with autopep8
        formatted = autopep8.fix_code(
            code,
            options={
                "experimental": True,
                "max_line_length": 88,
                "aggressive": self.aggressiveness
            }
        )

        # F-string regex fallback
        def convert_to_fstring(code):
            pattern = r'print\("([^"]+)"\s*\+\s*(\w+)\)'
            replacement = r'print(f"\1{\2}")'
            code = re.sub(pattern, replacement, code)
            pattern = r'print\("([^"]+)"\s*\+\s*(\w+)\s*\+\s*"([^"]+)"\)'
            replacement = r'print(f"\1{\2}\3")'
            return re.sub(pattern, replacement, code)
        formatted = convert_to_fstring(formatted)

        # AST-based improvements
        tree = ast.parse(formatted)
        modified = False

        # Remove unused variables
        assignments = {}
        uses = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = node
            if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Store):
                uses.add(node.id)
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

        return ast.unparse(tree) if modified else formatted

    def _improve_javascript(self, code):
        # Use ESLint for formatting
        try:
            with open("temp.js", "w") as f:
                f.write(code)
            subprocess.run(["eslint", "--fix", "temp.js"], check=False)
            with open("temp.js", "r") as f:
                formatted = f.read()
            os.remove("temp.js")
            return formatted
        except Exception:
            return code

    def _secure_code(self, code, language):
        if language == "python":
            code = re.sub(r'(password|api_key)\s*=\s*["\'][\w]+["\']', r'\1 = os.getenv("\1".upper())', code)
            code = re.sub(r'input\(', 'input_secure(', code)  # Mitigate eval risks
        elif language == "javascript":
            code = re.sub(r'console\.log\(.*(password|api_key).*\)', 'console.log("REDACTED")', code)
        return code

    def _optimize_performance(self, code, language):
        if language == "python":
            # Replace loops with comprehensions
            code = re.sub(r'for\s+(\w+)\s+in\s+(\w+):\s*\n\s+(\w+)\.append\(\1\)', r'\3 = [\1 for \1 in \2]', code)
        return code
