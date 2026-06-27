import math
import re
import difflib

IMPORTANT_BRANDS = [
    "google", "apple", "amazon", "facebook", "microsoft",
    "paypal", "netflix", "instagram", "youtube", "samsung",
    "github", "linkedin", "openai", "chatgpt", "twitter",
    "x", "whatsapp", "telegram"
]

PHISHING_SUFFIXES = [
    "login", "secure", "verify", "account", "update",
    "signin", "support", "auth", "portal", "web",
    "bank", "payment", "wallet", "confirm"
]


def calculate_entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(s)]
    return -sum(p * math.log2(p) for p in prob)


def normalize_domain(domain):
    domain = domain.lower()
    parts = re.split(r"[-_.]", domain)
    cleaned = [p for p in parts if p not in PHISHING_SUFFIXES]
    return "".join(cleaned)


def is_similar_to_brand(domain):
    """
    BUG FIX: Only flag if the domain is SIMILAR but NOT IDENTICAL to a brand.
    'apple' == 'apple' → NOT impersonation, it IS apple.
    'appie' ~= 'apple' → IS impersonation.
    """
    cleaned = normalize_domain(domain)

    best_similarity = 0
    detected_brand = None

    for brand in IMPORTANT_BRANDS:
        sim = difflib.SequenceMatcher(None, cleaned, brand).ratio()
        if sim > best_similarity:
            best_similarity = sim
            detected_brand = brand

    # Must be similar but NOT an exact match to the brand
    if best_similarity >= 0.75 and cleaned != detected_brand:
        # Extra guard: if cleaned IS a known brand word, skip flagging
        if cleaned in IMPORTANT_BRANDS:
            return False, None, best_similarity
        return True, detected_brand, best_similarity

    return False, None, best_similarity


def compute_risk_score(features):
    score = 0
    reasons = []

    trusted = features.get("trusted_domain", 0)

    # Extract only the domain name part (no TLD) for analysis
    domain_full = features.get("domain", "")
    domain = domain_full.split(".")[0].lower()

    # ---- BASIC FEATURES ----

    if features.get("url_length", 0) > 75:
        score += 1
        reasons.append("URL is unusually long")

    if features.get("has_at_symbol", 0):
        score += 2
        reasons.append("Contains '@' symbol")

    # BUG FIX: Don't penalise hyphens on trusted domains (cdn-apple.com etc.)
    if features.get("has_hyphen", 0) and not trusted:
        score += 1
        reasons.append("Contains hyphens in URL")

    if features.get("num_dots", 0) > 4:
        score += 1
        reasons.append("Too many subdomains")

    if not features.get("uses_https", 1):
        score += 3
        reasons.append("Does not use HTTPS")

    if features.get("has_ip", 0):
        score += 5
        reasons.append("Uses IP address instead of domain")

    # BUG FIX: Don't penalise suspicious keywords on trusted domains
    # e.g. apple.com/account/login is perfectly normal
    if features.get("has_suspicious_keyword", 0) and not trusted:
        score += 3
        reasons.append("Contains suspicious keywords")

    # ---- DOMAIN AGE ----
    age = features.get("domain_age_days", -1)
    if age != -1 and not trusted:
        if age < 30:
            score += 4
            reasons.append("Very new domain (< 30 days)")
        elif age < 180:
            score += 2
            reasons.append("Recently registered domain (< 6 months)")

    # ---- CONTENT (skip for trusted) ----
    if features.get("has_login_form", 0) and not trusted:
        score += 2
        reasons.append("Login form detected")

    if features.get("num_iframes", 0) > 2:
        score += 2
        reasons.append("Multiple hidden iframes detected")

    if features.get("title_mismatch", 0) and not trusted:
        score += 1
        reasons.append("Page title does not match domain")

    # ---- DIGIT MIXING — DOMAIN ONLY, not path ----
    # BUG FIX: Only check the domain part, not the full URL
    if re.search(r"[A-Za-z]+\d+[A-Za-z]*", domain) and not trusted:
        score += 5
        reasons.append("Suspicious use of numbers in domain")

    # ---- ENTROPY ----
    entropy = calculate_entropy(domain)
    if entropy > 3.5 and not trusted:
        score += 3
        reasons.append("Domain looks randomly generated (high entropy)")

    # ---- BRAND IMPERSONATION ----
    if not trusted:
        fake, brand, similarity = is_similar_to_brand(domain)
        if fake:
            score += 8
            reasons.append(
                f"Possible impersonation of '{brand}' "
                f"(similarity {similarity:.2f})"
            )

    # ---- NORMALIZE ----
    MAX_SCORE = 35
    risk_score = min(score / MAX_SCORE, 1.0)

    # Trusted domains are always capped low
    if trusted:
        risk_score = min(risk_score, 0.20)

    # ---- VERDICT ----
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