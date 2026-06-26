from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_groq import ChatGroq

from utils.feature_extractor import extract_url_features
from utils.risk_engine import compute_risk_score
from models.inference.predict import predict_url

import json
import os
import re
import socket
from urllib.parse import urlparse

# -------------------- LLM INIT --------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = None
if GROQ_API_KEY:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY
    )

# -------------------- LLM ANALYSIS --------------------
def get_llm_analysis(url, features, ml_score, rule_score, reasons):
    if not llm:
        return {
            "explanation": "LLM not configured",
            "llm_score": 0.0
        }

    prompt = f"""
You are a cybersecurity expert specialized in phishing detection.

Analyze this URL: {url}

ML Score: {ml_score}
Rule Score: {rule_score}

Features:
{features}

Reasons:
{reasons}

IMPORTANT:
- Detect fake domains like go0gle, paypa1, faceb00k
- Detect impersonation of real brands
- Even small spelling changes (0 instead of o) are HIGH RISK
- Use your own reasoning

Return STRICT JSON:
{{
  "explanation": "clear reasoning",
  "llm_score": number between 0 and 1
}}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content

        match = re.search(r'\{.*\}', content, re.DOTALL)
        parsed = json.loads(match.group())

        return parsed

    except Exception as e:
        return {
            "explanation": f"LLM failed: {str(e)}",
            "llm_score": 0.0
        }

# -------------------- APP INIT --------------------
app = Flask(__name__)
CORS(app)

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# -------------------- SIGNUP --------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()

    if username in users:
        return jsonify({"status": "fail", "message": "User already exists"})

    users[username] = password
    save_users(users)

    return jsonify({"status": "success", "message": "Account created!"})

# -------------------- LOGIN --------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()

    if username in users and users[username] == password:
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "fail", "message": "Invalid credentials"})

# -------------------- CORE ANALYSIS --------------------
def analyze_url(url):
    # ---------------- FEATURE EXTRACTION ----------------
    features = extract_url_features(url)

    # ---------------- RULE ENGINE ----------------
    rule_result = compute_risk_score(features)
    rule_score = rule_result["risk_score"]

    # ---------------- DEEP LEARNING ----------------
    dl_result = predict_url(url)

    ml_score = dl_result["probability"]
    ml_prediction = dl_result["prediction"]
    ml_confidence = dl_result["confidence"]

    # ---- LLM ----
    llm_result = get_llm_analysis(
        url,
        features,
        ml_score,
        rule_score,
        rule_result["reasons"]
    )

    try:
        llm_score = float(llm_result.get("llm_score", 0))
    except:
        llm_score = 0.0

    # ---- FINAL HYBRID SCORE ----
    final_score = (
        (rule_score * 0.45) +
        (ml_score * 0.25) +
        (llm_score * 0.30)
    )

    # Strong Rule Override
    if any(
        "Possible impersonation" in reason or
        "Suspicious use of numbers" in reason
        for reason in rule_result["reasons"]
    ):
        final_score = max(final_score, 0.80)
    # ---------------- TRUSTED DOMAIN FIX ----------------
    TRUSTED_DOMAINS = ["google.com", "livechat.com", "amazon.com", "paypal.com"]

    if any(td in url for td in TRUSTED_DOMAINS):
        final_score *= 0.5

    final_score = max(min(final_score, 1.0), 0.0)

    # ---- VERDICT ----
    if final_score < 0.3:
        verdict = "SAFE"
    elif final_score < 0.7:
        verdict = "SUSPICIOUS"
    else:
        verdict = "PHISHING"

    # ---------------- FIXED DOMAIN + IP ----------------
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    ip_address = "Unavailable"

    try:
        if hostname:
            ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Unavailable"

    return {
        "url": url,
        "domain": hostname,
        "ip_address": ip_address,
        "domain_age_days": features.get("domain_age_days", -1),

        "final_score": round(final_score, 2),
        "verdict": verdict,

        "reasons": rule_result["reasons"],
        "ml_score": round(ml_score, 4),

        "deep_learning": {
            "prediction": ml_prediction,
            "probability": round(ml_score, 4),
            "confidence": round(ml_confidence, 4)
        },

        "rule_score": round(rule_score, 2),
        "llm_score": round(llm_score, 2),
        "llm_explanation": llm_result.get("explanation", "")
    }

# -------------------- SINGLE URL --------------------
@app.route("/check", methods=["POST"])
def check_url():
    data = request.json
    url = data.get("url")

    return jsonify(analyze_url(url))

# -------------------- MULTI URL --------------------
@app.route("/check-batch", methods=["POST"])
def check_batch():
    data = request.json
    urls = data.get("urls", [])

    results = []

    for url in urls:
        try:
            results.append(analyze_url(url))
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })

    return jsonify({
        "results": results
    })

# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(debug=True)