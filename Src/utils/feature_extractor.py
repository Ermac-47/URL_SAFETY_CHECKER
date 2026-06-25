# Feature Extractor

import re
import requests
import tldextract
import whois
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

WHOIS_TIMEOUT_SECONDS = 4
HTTP_TIMEOUT_SECONDS = 3


def _safe_whois_lookup(domain, timeout_seconds=WHOIS_TIMEOUT_SECONDS):
    """Run whois.whois(domain) with a hard wall-clock timeout.

    WHOIS (port 43) is frequently slow, rate-limited, or blocked by
    networks/firewalls. The whois library doesn't reliably honor
    timeouts on every platform, so we enforce one ourselves using a
    background thread we simply abandon if it's too slow.
    """
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(whois.whois, domain)
    try:
        result = future.result(timeout=timeout_seconds)
        executor.shutdown(wait=False)
        return result
    except FutureTimeoutError:
        executor.shutdown(wait=False)
        return None
    except Exception:
        executor.shutdown(wait=False)
        return None


def extract_url_features(url):
    features = {}

    # ----------------------- url basic features -----------------------

    features["url_length"] = len(url)
    features["has_at_symbol"] = int("@" in url)
    features["has_hyphen"] = int("-" in url)
    features["num_dots"] = url.count(".")
    features["uses_https"] = int(url.startswith("https"))
    features["has_ip"] = int(bool(re.search(r"\d+\.\d+\.\d+\.\d+", url)))

    # Suspicious Keywords
    suspicious_keywords = ["login", "verify", "secure", "account", "bank", "update", "confirm", "password"]
    features["has_suspicious_keyword"] = int(any(word in url.lower() for word in suspicious_keywords))

    # --------------------- Domain Features -----------------------------------------

    ext = tldextract.extract(url)
    domain = ext.domain + "." + ext.suffix

    features["domain"] = domain

    w = _safe_whois_lookup(domain)
    if w is not None:
        try:
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            age_days = (datetime.now() - creation_date).days
            features["domain_age_days"] = age_days
        except Exception:
            features["domain_age_days"] = -1
    else:
        features["domain_age_days"] = -1  # unknown / lookup timed out or failed

    # ---------------------- SSL Certificate ------------------ #
    if url.startswith("https"):
        features["ssl_valid"] = 1
    else:
        features["ssl_valid"] = 0

    # ---------------------- Content Features -------------------#
    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else ""
        features["has_login_form"] = int(bool(soup.find("input", {"type": "password"})))
        features["num_iframes"] = len(soup.find_all("iframe"))

        # title-domain mismatch
        features["title_mismatch"] = int(domain.split(".")[0] not in (title or "").lower())

    except Exception:
        features["has_login_form"] = 0
        features["num_iframes"] = 0
        features["title_mismatch"] = 0

    return features