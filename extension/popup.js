chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    let url = tabs[0].url;

    fetch("http://127.0.0.1:5000/check", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {

        let verdict = data.verdict;
        let score = Math.round(data.final_score * 100);
        let reason = data.reasons[0] || "No issues detected";

        // Set text
        document.getElementById("verdict").innerText = verdict;
        document.getElementById("score").innerText = `Risk Score: ${score}%`;
        document.getElementById("reason").innerText = `Reason: ${reason}`;

        // Color logic
        let bgColor = "#00b894"; // green

        if (verdict === "PHISHING") bgColor = "red";
        else if (verdict === "SUSPICIOUS") bgColor = "orange";

        document.body.style.backgroundColor = bgColor;
        document.body.style.color = "white";

    })
    .catch(err => {
        document.getElementById("verdict").innerText = "Error";
    });
});


// 🔥 Open Streamlit Dashboard
document.getElementById("details").addEventListener("click", function() {
    chrome.tabs.create({
        url: "http://localhost:8501"
    });
});