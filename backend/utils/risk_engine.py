import math
import re
import difflib
from urllib.parse import urlparse

IMPORTANT_BRANDS = [
    "google", "apple", "amazon", "facebook", "microsoft",
    "paypal", "netflix", "instagram", "youtube", "samsung",
    "github", "linkedin", "openai", "chatgpt", "twitter",
    "x", "whatsapp", "telegram", "flipkart", "paytm",
    "hdfc", "icici", "sbi", "axis", "kotak"
]

PHISHING_SUFFIXES = [
    "login", "secure", "verify", "account", "update",
    "signin", "support", "auth", "portal", "web",
    "bank", "payment", "wallet", "confirm"
]

URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl",
    "ow.ly", "short.link", "rb.gy", "is.gd"
}

HOMOGLYPHS = {
    '0': 'o', '1': 'l', '3': 'e',
    '4': 'a', '5': 's', '6': 'g',
    '7': 't', '@': 'a', '8': 'b'
}


def calculate_entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(s)]
    return -sum(p * math.log2(p) for p in prob)


def decode_homoglyphs(text):
    """Convert go0gle → google, paypa1 → paypal"""
    result = text.lower()
    for fake, real in HOMOGLYPHS.items():
        result = result.replace(fake, real)
    return result


def check_typosquatting(domain_base):
    """
    Check for character substitution attacks.
    Returns (is_typosquat, brand_name, method)
    """
    base = domain_base.lower()

    # Method 1: Homoglyph substitution (go0gle, paypa1, amaz0n)
    decoded = decode_homoglyphs(base)
    if decoded != base:  # only check if there were substitutions
        for brand in IMPORTANT_BRANDS:
            if decoded == brand:
                return True, brand, "homoglyph"

    # Method 2: Levenshtein distance (gooogle, paypaI)
    for brand in IMPORTANT_BRANDS:
        if base == brand:
            return False, None, None  # exact match = legit
        # Simple edit distance
        sim = difflib.SequenceMatcher(None, base, brand).ratio()
        if sim >= 0.82 and len(base) >= 4:
            return True, brand, "similarity"

    return False, None, None


def compute_risk_score(features):
    score = 0
    reasons = []

    trusted = features.get("trusted_domain", 0)

    # Get domain parts
    domain_full = features.get("domain", "")
    url = features.get("url", "")

    # Extract base domain (first part before first dot)
    try:
        if url:
            hostname = urlparse(url).hostname or domain_full
        else:
            hostname = domain_full
        domain_base = hostname.split(".")[0].lower()
    except Exception:
        domain_base = domain_full.split(".")[0].lower()
        hostname = domain_full

    # ── TYPOSQUATTING CHECK (runs first, highest priority) ──────
    if not trusted:
        is_typo, brand, method = check_typosquatting(domain_base)
        if is_typo:
            score += 22  # enough to push past MALICIOUS threshold
            if method == "homoglyph":
                reasons.append(
                    f"⚠️ Typosquatting: '{domain_base}' mimics "
                    f"'{brand}' using character substitution "
                    f"(e.g. '0' for 'o', '1' for 'l')"
                )
            else:
                reasons.append(
                    f"⚠️ Possible typosquatting: '{domain_base}' "
                    f"closely resembles '{brand}'"
                )

    # ── IP ADDRESS ───────────────────────────────────────────────
    if features.get("has_ip", 0):
        score += 12
        reasons.append("IP address used as host — classic phishing pattern")

    # ── HTTPS ────────────────────────────────────────────────────
    if not features.get("uses_https", 1):
        score += 4
        reasons.append("No HTTPS encryption")

    # ── URL LENGTH ───────────────────────────────────────────────
    if features.get("url_length", 0) > 100:
        score += 3
        reasons.append("URL is excessively long")
    elif features.get("url_length", 0) > 75:
        score += 1
        reasons.append("URL is unusually long")

    # ── @ SYMBOL ────────────────────────────────────────────────
    if features.get("has_at_symbol", 0):
        score += 4
        reasons.append("@ symbol in URL hides true destination")

    # ── SUBDOMAINS ───────────────────────────────────────────────
    if features.get("num_dots", 0) > 4:
        score += 2
        reasons.append("Excessive subdomain depth")

    # ── HYPHENS (skip trusted) ───────────────────────────────────
    if features.get("has_hyphen", 0) and not trusted:
        score += 1
        reasons.append("Hyphens in domain name")

    # ── SUSPICIOUS KEYWORDS (skip trusted) ──────────────────────
    if features.get("has_suspicious_keyword", 0) and not trusted:
        score += 3
        reasons.append("Suspicious keywords in URL")

    # ── URL SHORTENER ─────────────────────────────────────────────
    if any(s in hostname for s in URL_SHORTENERS):
        score += 4
        reasons.append(f"URL shortening service detected")

    # ── DOMAIN AGE ───────────────────────────────────────────────
    age = features.get("domain_age_days", -1)
    if age != -1 and not trusted:
        if age < 30:
            score += 5
            reasons.append("Very new domain (< 30 days old)")
        elif age < 180:
            score += 2
            reasons.append("Recently registered domain (< 6 months)")

    # ── RISKY TLD ─────────────────────────────────────────────────
    RISKY_TLDS = [
        ".xyz", ".tk", ".ml", ".ga", ".cf",
        ".gq", ".top", ".info", ".click", ".example"
    ]
    if any(domain_full.endswith(tld) for tld in RISKY_TLDS) and not trusted:
        score += 5
        reasons.append(f"High-risk TLD: .{domain_full.split('.')[-1]}")

    # ── CONTENT SIGNALS ──────────────────────────────────────────
    if features.get("has_login_form", 0) and not trusted:
        score += 2
        reasons.append("Login form detected")

    if features.get("num_iframes", 0) > 2:
        score += 2
        reasons.append("Multiple hidden iframes")

    if features.get("title_mismatch", 0) and not trusted:
        score += 1
        reasons.append("Page title does not match domain")

    # ── DIGIT MIXING IN DOMAIN ───────────────────────────────────
    if re.search(r"[A-Za-z]+\d+[A-Za-z]*", domain_base) and not trusted:
        if not any("Typosquatting" in r or "typosquat" in r for r in reasons):
            score += 4
            reasons.append("Suspicious digit mixing in domain name")

    # ── ENTROPY ──────────────────────────────────────────────────
    entropy = calculate_entropy(domain_base)
    if entropy > 3.5 and not trusted:
        score += 3
        reasons.append("Domain appears randomly generated")

    # ── NORMALIZE TO 0-1 ─────────────────────────────────────────
    MAX_SCORE = 35
    risk_score = min(score / MAX_SCORE, 1.0)

    # Trusted domains always capped low
    if trusted:
        risk_score = min(risk_score, 0.15)

    # ── VERDICT ──────────────────────────────────────────────────
    if risk_score < 0.30:
        verdict = "SAFE"
    elif risk_score < 0.65:
        verdict = "SUSPICIOUS"
    else:
        verdict = "PHISHING"

    if not reasons:
        reasons.append("No suspicious patterns detected")

    return {
        "risk_score": round(risk_score, 2),
        "verdict": verdict,
        "reasons": reasons
    }