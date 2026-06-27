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
import tldextract

# -------------------- LLM INIT --------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = None
if GROQ_API_KEY:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY
    )

# -------------------- TRUSTED DOMAINS (comprehensive) --------------------
# BUG FIX 1: Proper full list — matched by exact registered domain+suffix
TRUSTED_APEX_DOMAINS = {
    # Search
    "google.com", "bing.com", "duckduckgo.com", "yahoo.com",
    # Apple
    "apple.com", "icloud.com",
    # Microsoft
    "microsoft.com", "microsoftonline.com", "office.com",
    "live.com", "outlook.com", "azure.com", "windows.com",
    # Google services
    "gmail.com", "youtube.com", "blogger.com",
    # Amazon
    "amazon.com", "amazon.in", "aws.amazon.com", "primevideo.com",
    # Meta
    "facebook.com", "instagram.com", "whatsapp.com",
    "messenger.com", "threads.net",
    # Social
    "x.com", "twitter.com", "linkedin.com", "reddit.com",
    "discord.com", "telegram.org", "snapchat.com", "pinterest.com",
    # Payments
    "paypal.com", "stripe.com", "razorpay.com", "paytm.com", "phonepe.com",
    # Banking
    "hdfcbank.com", "icicibank.com", "sbi.co.in", "axisbank.com", "kotak.com",
    # Dev
    "github.com", "gitlab.com", "stackoverflow.com", "bitbucket.org",
    # Streaming
    "netflix.com", "spotify.com", "disneyplus.com", "hotstar.com",
    # AI
    "openai.com", "anthropic.com", "claude.ai", "chatgpt.com", "perplexity.ai",
    # Security
    "virustotal.com", "cloudflare.com", "cisco.com",
    # Education
    "coursera.org", "udemy.com", "khanacademy.org",
    # Communication
    "zoom.us", "slack.com",
    # Knowledge
    "wikipedia.org",
    # Shopping
    "flipkart.com", "ebay.com", "etsy.com",
    # Gov / standards
    "nist.gov", "cisa.gov",
}

def is_trusted_domain(url):
    """
    BUG FIX 2: Extract the registered domain properly and check exact match.
    Prevents 'fake-apple.com.evil.xyz' from matching 'apple.com'.
    """
    try:
        ext = tldextract.extract(url)
        registered = f"{ext.domain}.{ext.suffix}".lower()
        return registered in TRUSTED_APEX_DOMAINS
    except:
        return False

# -------------------- LLM ANALYSIS --------------------
def get_llm_analysis(url, features, ml_score, rule_score, reasons):
    if not llm:
        return {"explanation": "LLM not configured", "llm_score": 0.0}

    prompt = f"""
You are a cybersecurity expert specialized in phishing detection.

Analyze this URL: {url}

ML Score: {ml_score}
Rule Score: {rule_score}

Features:
{features}

Reasons flagged by rule engine:
{reasons}

IMPORTANT RULES:
- If the domain is a well-known brand (apple.com, google.com, amazon.com etc.) return llm_score 0.05
- Detect fake domains like go0gle, paypa1, faceb00k — these are HIGH RISK
- Digit substitution (0 for o, 1 for l) in domain names is HIGH RISK
- Subdomains of trusted domains (accounts.google.com) are SAFE
- URL paths containing words like /login or /account on real trusted domains are NORMAL

Return STRICT JSON only:
{{
  "explanation": "clear 1-2 sentence reasoning",
  "llm_score": <number between 0.0 and 1.0>
}}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content
        match = re.search(r'\{.*\}', content, re.DOTALL)
        parsed = json.loads(match.group())
        return parsed
    except Exception as e:
        return {"explanation": f"LLM failed: {str(e)}", "llm_score": 0.0}


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

    # Step 1: Check trusted domain FIRST (exact match)
    trusted = is_trusted_domain(url)

    # Step 2: Feature extraction
    features = extract_url_features(url)
    features["trusted_domain"] = int(trusted)   # pass to risk engine

    # Step 3: Rule engine
    rule_result = compute_risk_score(features)
    rule_score = rule_result["risk_score"]

    # Step 4: Deep Learning
    dl_result = predict_url(url)
    ml_score = dl_result["probability"]
    ml_prediction = dl_result["prediction"]
    ml_confidence = dl_result["confidence"]

    # Step 5: LLM
    llm_result = get_llm_analysis(
        url, features, ml_score, rule_score, rule_result["reasons"]
    )
    try:
        llm_score = float(llm_result.get("llm_score", 0))
    except:
        llm_score = 0.0

    # ---- FINAL HYBRID SCORE ----
    if trusted:
        # BUG FIX 3: Trusted domains get a heavily discounted score
        # Rule engine may still flag paths (/login, /account) — ignore that for trusted domains
        final_score = min(
            (rule_score * 0.10) +
            (ml_score  * 0.10) +
            (llm_score * 0.10),
            0.25   # cap at 0.25 so trusted domains always show SAFE
        )
    else:
        final_score = (
            (rule_score * 0.45) +
            (ml_score   * 0.25) +
            (llm_score  * 0.30)
        )

        # BUG FIX 4: Strong override only on DOMAIN-level signals, not URL path
        # Only trigger if impersonation or digit-mixing was detected IN THE DOMAIN
        domain_reasons = rule_result.get("reasons", [])
        if any(
            "Possible impersonation" in r or
            "Suspicious use of numbers in domain" in r
            for r in domain_reasons
        ):
            final_score = max(final_score, 0.80)

    final_score = max(min(final_score, 1.0), 0.0)

    # ---- VERDICT ----
    if final_score < 0.30:
        verdict = "SAFE"
    elif final_score < 0.70:
        verdict = "SUSPICIOUS"
    else:
        verdict = "PHISHING"

    # ---- DOMAIN + IP ----
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
        "trusted_domain": trusted,
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
            results.append({"url": url, "error": str(e)})
    return jsonify({"results": results})


# -------------------- RUN --------------------
if __name__ == "__main__":
    app.run(debug=True)