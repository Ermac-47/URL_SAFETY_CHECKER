import re
import requests
import tldextract
import whois

from datetime import datetime
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


# =====================================================
# TRUSTED BRANDS
# =====================================================

TRUSTED_DOMAINS = [

    "google.com",
    "facebook.com",
    "instagram.com",
    "amazon.com",
    "paypal.com",
    "microsoft.com",
    "github.com",
    "linkedin.com",
    "apple.com",
    "netflix.com",
    "youtube.com",
    "openai.com",
    "chatgpt.com",
    "twitter.com",
    "x.com",
    "whatsapp.com",
    "telegram.org"

]


# =====================================================
# SUSPICIOUS KEYWORDS
# =====================================================

SUSPICIOUS_KEYWORDS = [

    "login",
    "signin",
    "verify",
    "secure",
    "account",
    "update",
    "confirm",
    "password",
    "authenticate",
    "wallet",
    "payment",
    "invoice",
    "billing",
    "support",
    "unlock",
    "otp",
    "gift",
    "bonus",
    "reward",
    "free"

]


# =====================================================
# SIMILARITY
# =====================================================

def similarity(a, b):

    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# =====================================================
# FEATURE EXTRACTION
# =====================================================

def extract_url_features(url):

    features = {}

    # =================================================
    # BASIC URL FEATURES
    # =================================================

    features["url_length"] = len(url)

    features["has_at_symbol"] = int("@" in url)

    features["has_hyphen"] = int("-" in url)

    features["num_dots"] = url.count(".")

    features["uses_https"] = int(url.lower().startswith("https"))

    features["has_ip"] = int(

        bool(

            re.search(

                r"\b(?:\d{1,3}\.){3}\d{1,3}\b",

                url

            )

        )

    )

    features["has_suspicious_keyword"] = int(

        any(

            word in url.lower()

            for word in SUSPICIOUS_KEYWORDS

        )

    )

    # =================================================
    # DOMAIN
    # =================================================

    ext = tldextract.extract(url)

    domain = f"{ext.domain}.{ext.suffix}"

    features["domain"] = domain

    # =================================================
    # TRUSTED DOMAIN LOOKALIKE
    # =================================================

    features["looks_like_trusted"] = 0

    features["matched_brand"] = ""

    for trusted in TRUSTED_DOMAINS:

        sim = similarity(domain, trusted)

        if sim >= 0.75 and domain != trusted:

            features["looks_like_trusted"] = 1

            features["matched_brand"] = trusted

            break

    # =================================================
    # DOMAIN AGE
    # =================================================

    try:

        info = whois.whois(domain)

        creation_date = info.creation_date

        if isinstance(creation_date, list):

            creation_date = creation_date[0]

        if creation_date:

            age = (

                datetime.now()

                - creation_date

            ).days

            features["domain_age_days"] = age

        else:

            features["domain_age_days"] = -1

    except:

        features["domain_age_days"] = -1

    # =================================================
    # SSL
    # =================================================

    features["ssl_valid"] = int(

        url.lower().startswith("https")

    )

    # =================================================
    # CONTENT ANALYSIS
    # =================================================

    try:

        response = requests.get(

            url,

            timeout=5,

            allow_redirects=True,

            headers={

                "User-Agent":

                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) URLShieldNet"

            }

        )

        soup = BeautifulSoup(

            response.text,

            "html.parser"

        )

        # ---------------- TITLE ----------------

        title = ""

        if soup.title and soup.title.string:

            title = soup.title.string.lower()

        # ---------------- LOGIN FORM ----------------

        login_form = soup.find(

            "input",

            {

                "type": "password"

            }

        )

        features["has_login_form"] = int(

            login_form is not None

        )

        # ---------------- IFRAMES ----------------

        features["num_iframes"] = len(

            soup.find_all("iframe")

        )

        # ---------------- TITLE MISMATCH ----------------

        if title:

            features["title_mismatch"] = int(

                ext.domain.lower()

                not in title

            )

        else:

            features["title_mismatch"] = 0

    except:

        features["has_login_form"] = 0

        features["num_iframes"] = 0

        features["title_mismatch"] = 0

    return features