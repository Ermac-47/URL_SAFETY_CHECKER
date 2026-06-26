import math
import re
import difflib

# --------------------------------------------------
# IMPORTANT BRANDS
# --------------------------------------------------

IMPORTANT_BRANDS = [
    "google",
    "apple",
    "amazon",
    "facebook",
    "microsoft",
    "paypal",
    "netflix",
    "instagram",
    "youtube",
    "samsung",
    "github",
    "linkedin",
    "openai",
    "chatgpt",
    "twitter",
    "x",
    "whatsapp",
    "telegram"
]


# --------------------------------------------------
# COMMON PHISHING WORDS
# --------------------------------------------------

PHISHING_SUFFIXES = [
    "login",
    "secure",
    "verify",
    "account",
    "update",
    "signin",
    "support",
    "auth",
    "portal",
    "web",
    "bank",
    "payment",
    "wallet",
    "confirm"
]


# --------------------------------------------------
# ENTROPY
# --------------------------------------------------

def calculate_entropy(s):

    if not s:
        return 0

    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(s)]

    return -sum(p * math.log2(p) for p in prob)


# --------------------------------------------------
# NORMALIZE DOMAIN
# --------------------------------------------------

def normalize_domain(domain):

    domain = domain.lower()

    # Remove common phishing suffixes
    parts = re.split(r"[-_.]", domain)

    cleaned = []

    for part in parts:

        if part not in PHISHING_SUFFIXES:

            cleaned.append(part)

    return "".join(cleaned)


# --------------------------------------------------
# BRAND IMPERSONATION
# --------------------------------------------------

def is_similar_to_brand(domain):

    cleaned = normalize_domain(domain)

    best_similarity = 0
    detected_brand = None

    for brand in IMPORTANT_BRANDS:

        similarity = difflib.SequenceMatcher(

            None,

            cleaned,

            brand

        ).ratio()

        if similarity > best_similarity:

            best_similarity = similarity
            detected_brand = brand

    if best_similarity >= 0.75 and cleaned != detected_brand:

        return True, detected_brand, best_similarity

    return False, None, best_similarity


# --------------------------------------------------
# RISK ENGINE
# --------------------------------------------------

def compute_risk_score(features):

    score = 0
    reasons = []

    domain = features.get("domain", "").split(".")[0].lower()

    # --------------------------------------------------
    # BASIC FEATURES
    # --------------------------------------------------

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

        score += 5
        reasons.append("Uses IP address instead of domain")

    if features.get("has_suspicious_keyword", 0):

        score += 4
        reasons.append("Contains suspicious keywords")

    # --------------------------------------------------
    # DOMAIN AGE
    # --------------------------------------------------

    age = features.get("domain_age_days", -1)

    if age != -1:

        if age < 30:

            score += 4
            reasons.append("Very new domain")

        elif age < 180:

            score += 2
            reasons.append("Recently registered domain")

    # --------------------------------------------------
    # CONTENT FEATURES
    # --------------------------------------------------

    if features.get("has_login_form", 0):

        score += 2
        reasons.append("Login form detected")

    if features.get("num_iframes", 0) > 2:

        score += 2
        reasons.append("Multiple iframes detected")

    if features.get("title_mismatch", 0):

        score += 2
        reasons.append("Page title mismatch")

    # --------------------------------------------------
    # DIGIT MIXING
    # --------------------------------------------------

    if re.search(r"[A-Za-z]+\d+[A-Za-z]*", domain):

        score += 5
        reasons.append("Suspicious use of numbers in domain")

    # --------------------------------------------------
    # RANDOM LOOKING DOMAIN
    # --------------------------------------------------

    entropy = calculate_entropy(domain)

    if entropy > 3.5:

        score += 3
        reasons.append("Random-looking domain")

    # --------------------------------------------------
    # BRAND IMPERSONATION
    # --------------------------------------------------

    fake, brand, similarity = is_similar_to_brand(domain)

    if fake:

        score += 8

        reasons.append(

            f"Possible impersonation of '{brand}' "

            f"(similarity {similarity:.2f})"

        )

    # --------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------

    MAX_SCORE = 35

    risk_score = min(score / MAX_SCORE, 1.0)

    # --------------------------------------------------
    # VERDICT
    # --------------------------------------------------

    if risk_score < 0.30:

        verdict = "Safe"

    elif risk_score < 0.70:

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