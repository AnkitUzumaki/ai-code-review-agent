# src/api.py
from flask import Flask, request, jsonify
import os
from src.main import main as run_review

app = Flask(__name__)

@app.route("/review", methods=["POST"])
def review_codebase():
    data = request.json
    input_path = data.get("input_path")
    output_path = data.get("output_path", "output")
    report_path = data.get("report_path", "reports")
    if not input_path:
        return jsonify({"error": "input_path required"}), 400
    try:
        os.system(f"python src/main.py {input_path} --output_path {output_path} --report_path {report_path}")
        return jsonify({"status": "Review completed", "report": f"{report_path}/report.html"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)
