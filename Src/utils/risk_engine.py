#------- Risk Engine which analysis and gives reasons using inference -----# 


def compute_risk_score(features):
    score = 0
    reasons = []

    # ---------------- URL FEATURES ----------------
    if features.get("url_length", 0) > 75:
        score += 1
        reasons.append("URL is unusually long")

    if features.get("has_at_symbol", 0):
        score += 2
        reasons.append("Contains '@' symbol (used in phishing)")

    if features.get("has_hyphen", 0):
        score += 1
        reasons.append("Contains hyphens (common in fake domains)")

    if features.get("num_dots", 0) > 3:
        score += 1
        reasons.append("Too many subdomains")

    if not features.get("uses_https", 1):
        score += 3
        reasons.append("Does not use HTTPS")

    if features.get("has_ip", 0):
        score += 3
        reasons.append("Uses IP address instead of domain")

    if features.get("has_suspicious_keyword", 0):
        score += 3
        reasons.append("Contains suspicious keywords (login/verify/bank)")

    # ---------------- DOMAIN FEATURES ----------------
    age = features.get("domain_age_days", -1)

    if age != -1:
        if age < 30:
            score += 3
            reasons.append("Domain is very new (< 30 days)")
        elif age < 180:
            score += 2
            reasons.append("Domain is relatively new (< 6 months)")
    else:
        pass

    if not features.get("ssl_valid", 1):
        score += 2
        reasons.append("SSL certificate issue")

    # ---------------- CONTENT FEATURES ----------------
    if features.get("has_login_form", 0):
        score += 2
        reasons.append("Login form detected (possible phishing)")

    if features.get("num_iframes", 0) > 2:
        score += 1
        reasons.append("Contains multiple iframes")

    if features.get("title_mismatch", 0):
        score += 1
        reasons.append("Page title does not match domain")

    # ---------------- NORMALIZATION ----------------
    max_score = 20  # adjust if needed
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