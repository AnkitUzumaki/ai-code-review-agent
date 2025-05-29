// web/app.js
async function startReview() {
    const inputPath = document.getElementById("inputPath").value;
    document.getElementById("progress").innerText = "Processing...";
    try {
        const response = await fetch("/review", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input_path: inputPath })
        });
        const data = await response.json();
        document.getElementById("progress").innerText = "Completed";
        document.getElementById("report").innerHTML = `<a href="${data.report}">View Report</a>`;
    } catch (error) {
        document.getElementById("progress").innerText = `Error: ${error}`;
    }
}
