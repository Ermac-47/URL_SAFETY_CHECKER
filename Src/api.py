from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.feature_extractor import extract_url_features
from utils.risk_engine import compute_risk_score
from models.predict import predict_url

app = Flask(__name__)
CORS(app)

@app.route("/check", methods=["POST"])
def check_url():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    features = extract_url_features(url)

    rule_result = compute_risk_score(features)
    rule_score = rule_result["risk_score"]

    ml_score = predict_url(features)

    final_score = (rule_score * 0.4) + (ml_score * 0.6)

    if final_score < 0.3:
        verdict = "SAFE"
    elif final_score < 0.7:
        verdict = "SUSPICIOUS"
    else:
        verdict = "PHISHING"

    return jsonify({
        "url": url,
        "final_score": final_score,
        "verdict": verdict,
        "reasons": rule_result["reasons"]
    })

if __name__ == "__main__":
    app.run(debug=True)