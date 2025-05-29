# /home/uzumaki007/ai_code_review_agent/src/reporter.py
import os
import jinja2
import matplotlib.pyplot as plt

class Reporter:
    def generate_report(self, issues, dependencies, config, report_path, input_path, output_path):
        # Get project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(project_root, "template.html")

        # Load template
        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())

        # Generate chart
        plt.figure()
        plt.bar(["Issues", "Dependencies"], [len(issues), len(dependencies)])
        plt.xlabel("Metrics")
        plt.ylabel("Count")
        plt.title("Code Analysis Summary")
        chart_path = os.path.join(report_path, "complexity_chart.png")
        plt.savefig(chart_path)
        plt.close()

        # Render report
        os.makedirs(report_path, exist_ok=True)
        with open(os.path.join(report_path, "report.html"), "w") as f:
            f.write(template.render(issues=issues, dependencies=dependencies))