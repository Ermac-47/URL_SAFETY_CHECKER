# Feature Extractor 

import re
import requests
import socket
import ssl
import tldextract
import whois
from datetime import datetime
from bs4 import BeautifulSoup

def extract_url_features(url):
    features = {}

    # -----------------------url basic features -----------------------

    features["url_length"]=len(url)
    features["has_at_symbol"]=int("@" in url)
    features["has_hyphen"]=int("-" in url)
    features["num_dots"]=url.count(".")
    features["uses_https"]=int(url.startswith("https"))
    features["has_ip"] = int(bool(re.search(r"\d+\.\d+\.\d+\.\d+", url)))

    #Supicious Keywords

    suspicious_keywords = ["login","verify","secure","account","bank","update","confirm","password"]
    features["has_suspicious_keyword"]=int(any(word in url.lower() for word in suspicious_keywords))

    #---------------------Domain Features-----------------------------------------

    ext = tldextract.extract(url)
    domain = ext.domain + "." + ext.suffix

    features["domain"]=domain

    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        age_days = (datetime.now() - creation_date).days
        features["domain_age_days"] = age_days
    except:
        features["domain_age_days"] = -1  # unknown

    # ----------------------    SSL Certificate ------------------ #
    if url.startswith("https"):
        features["ssl_valid"] = 1
    else:
        features["ssl_valid"] = 0
    # ---------------------- Content Features -------------------#
    try:
        response = requests.get(url, timeout=3)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else ""
        features["has_login_form"] = int(bool(soup.find("input", {"type": "password"})))
        features["num_iframes"] = len(soup.find_all("iframe"))

        # title-domain mismatch
        features["title_mismatch"] = int(domain.split(".")[0] not in title.lower())

    except:
        features["has_login_form"] = 0
        features["num_iframes"] = 0
        features["title_mismatch"] = 0

    return features
