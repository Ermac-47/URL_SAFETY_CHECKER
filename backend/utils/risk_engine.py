import math
import re
import difflib

# Small but high-impact list (not huge, not hardcoded-heavy)
IMPORTANT_BRANDS = [
    "google", "apple", "amazon", "facebook",
    "microsoft", "paypal", "netflix", "instagram",
    "youtube", "samsung"
]

def calculate_entropy(s):
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum([p * math.log2(p) for p in prob])


def is_similar_to_brand(domain):
    for brand in IMPORTANT_BRANDS:
        similarity = difflib.SequenceMatcher(None, domain, brand).ratio()

        if similarity > 0.8 and domain != brand:
            return True, brand

    return False, None


def compute_risk_score(features):
    score = 0
    reasons = []

    domain = features.get("domain", "").split(".")[0]

    # ---------------- BASIC FEATURES ----------------
    if features.get("url_length", 0) > 75:
        score += 1
        reasons.append("URL is unusually long")

    if features.get("has_at_symbol", 0):
        score += 2
        reasons.append("Contains '@' symbol")

    if features.get("has_hyphen", 0):
        score += 1
        reasons.append("Contains hyphens")

    if features.get("num_dots", 0) > 3:
        score += 1
        reasons.append("Too many subdomains")

    if not features.get("uses_https", 1):
        score += 3
        reasons.append("Does not use HTTPS")

    if features.get("has_ip", 0):
        score += 3
        reasons.append("Uses IP instead of domain")

    if features.get("has_suspicious_keyword", 0):
        score += 3
        reasons.append("Contains suspicious keywords")

    # ---------------- DOMAIN AGE ----------------
    age = features.get("domain_age_days", -1)

    if age != -1:
        if age < 30:
            score += 3
            reasons.append("Very new domain")
        elif age < 180:
            score += 2
            reasons.append("Relatively new domain")

    # ---------------- CONTENT ----------------
    if features.get("has_login_form", 0):
        score += 2
        reasons.append("Login form detected")

    if features.get("num_iframes", 0) > 2:
        score += 1
        reasons.append("Multiple iframes")

    if features.get("title_mismatch", 0):
        score += 1
        reasons.append("Title mismatch")

    # ---------------- 🔥 ADVANCED DETECTION ----------------

    # 1. DIGIT MIXING (go0gle)
    if re.search(r'[a-zA-Z]+\d+[a-zA-Z]*', domain):
        score += 3
        reasons.append("Suspicious use of numbers in domain")

    # 2. ENTROPY
    entropy = calculate_entropy(domain)
    if entropy > 3.5:
        score += 3
        reasons.append("Domain looks randomly generated")

    # 3. SIMILARITY (🔥 KEY FIX)
    is_fake, brand = is_similar_to_brand(domain)
    if is_fake:
        score += 5
        reasons.append(f"Possible impersonation of '{brand}'")

    # ---------------- NORMALIZE ----------------
    max_score = 30
    risk_score = min(score / max_score, 1.0)

    # ---------------- VERDICT ----------------
    if risk_score < 0.3:
        verdict = "Safe"
    elif risk_score < 0.7:
        verdict = "Suspicious"
    else:
        verdict = "Phishing"

    if not reasons:
        reasons.append("No suspicious patterns detected")

    return {
        "risk_score": round(risk_score, 2),
        "verdict": verdict,
        "reasons": reasons
    }