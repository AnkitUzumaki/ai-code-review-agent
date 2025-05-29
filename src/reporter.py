# src/reporter.py
import json
import difflib
import os
from weasyprint import HTML

class Reporter:
    def generate_report(self, results, report_path, config):
        """Generate HTML and PDF reports with diffs and metrics."""
        report_data = []
        for result in results:
            if result:
                diff = self._generate_diff(result["original"], result["improved"])
                metrics = self._calculate_metrics(result["original"], result["improved"])
                report_data.append({
                    "file": result["file"],
                    "category": result["category"],
                    "issues": result["issues"],
                    "diff": diff,
                    "metrics": metrics
                })

        # HTML report
        html_content = f"""
        <html>
        <head><title>AI Code Review Report</title></head>
        <body>
        <h1>Code Review Report</h1>
        {''.join([f'''
        <h2>{data['file']} ({data['category']})</h2>
        <h3>Issues</h3>
        <ul>{''.join([f'<li>{issue}</li>' for issue in data['issues']])}</ul>
        <h3>Diff</h3>
        <pre>{data['diff']}</pre>
        <h3>Metrics</h3>
        <p>{json.dumps(data['metrics'], indent=2)}</p>
        ''' for data in report_data])}
        </body>
        </html>
        """
        with open(os.path.join(report_path, "report.html"), "w") as f:
            f.write(html_content)

        # PDF report
        HTML(string=html_content).write_pdf(os.path.join(report_path, "report.pdf"))

        # JSON report
        with open(os.path.join(report_path, "report.json"), "w") as f:
            json.dump(report_data, f, indent=2)

    def _generate_diff(self, original, improved):
        return '\n'.join(difflib.unified_diff(
            original.splitlines(), improved.splitlines(),
            lineterm=""
        ))

    def _calculate_metrics(self, original, improved):
        return {
            "original_lines": len(original.splitlines()),
            "improved_lines": len(improved.splitlines()),
            "complexity_reduction": len(original) - len(improved)
        }
