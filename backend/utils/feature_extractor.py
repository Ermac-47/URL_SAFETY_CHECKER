##--feature_extractor.py--##

import re
import requests
import tldextract
import whois
from datetime import datetime
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

TRUSTED_DOMAINS = [
    "google.com", "facebook.com", "amazon.com",
    "paypal.com", "instagram.com", "bank.com"
]

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def extract_url_features(url):
    features = {}

    # -------- BASIC FEATURES --------
    features["url_length"] = len(url)
    features["has_at_symbol"] = int("@" in url)
    features["has_hyphen"] = int("-" in url)
    features["num_dots"] = url.count(".")
    features["uses_https"] = int(url.startswith("https"))
    features["has_ip"] = int(bool(re.search(r"\d+\.\d+\.\d+\.\d+", url)))

    suspicious_keywords = ["login","verify","secure","account","bank","update","confirm","password"]
    features["has_suspicious_keyword"] = int(any(word in url.lower() for word in suspicious_keywords))

    # -------- DOMAIN --------
    ext = tldextract.extract(url)
    domain = ext.domain + "." + ext.suffix
    features["domain"] = domain

    # 🔥 DOMAIN SPOOF DETECTION
    features["looks_like_trusted"] = 0
    features["matched_brand"] = ""

    for trusted in TRUSTED_DOMAINS:
        sim = similarity(domain, trusted)
        if sim > 0.75 and domain != trusted:
            features["looks_like_trusted"] = 1
            features["matched_brand"] = trusted
            break

    # -------- DOMAIN AGE --------
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        # handle list format
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if creation_date:
            age_days = (datetime.now() - creation_date).days
            features["domain_age_days"] = age_days
        else:
            features["domain_age_days"] = -1

    except Exception as e:
        features["domain_age_days"] = -1
    # -------- SSL --------
    features["ssl_valid"] = int(url.startswith("https"))

    # -------- CONTENT --------
    try:
        response = requests.get(url, timeout=3)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else ""
        features["has_login_form"] = int(bool(soup.find("input", {"type": "password"})))
        features["num_iframes"] = len(soup.find_all("iframe"))
        features["title_mismatch"] = int(domain.split(".")[0] not in title.lower())

    except:
        features["has_login_form"] = 0
        features["num_iframes"] = 0
        features["title_mismatch"] = 0

    return features