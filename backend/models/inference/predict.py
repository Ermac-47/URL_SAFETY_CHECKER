# backend/models/inference/predict.py
# Uses Random Forest fallback since CNN weights are not trained yet

import pickle
import numpy as np
import os
import sys

# Path to the trained RF model
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
MODEL_PATH  = os.path.join(ROOT, 'data', 'models', 'rf_model.pkl')
SCALER_PATH = os.path.join(ROOT, 'data', 'models', 'scaler.pkl')

_model  = None
_scaler = None

def _load():
    global _model, _scaler
    if _model is not None:
        return
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            _model = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            _scaler = pickle.load(f)

def predict_url(url: str) -> dict:
    try:
        _load()
        if _model is None:
            return {
                "prediction": "UNKNOWN",
                "probability": 0.5,
                "confidence": 0.0
            }

        # Build feature vector matching train_model.py
        from urllib.parse import urlparse
        import re

        parsed   = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        path     = parsed.path or ""

        URL_SHORTENERS = {
            "bit.ly","tinyurl.com","t.co",
            "goo.gl","ow.ly","short.link","rb.gy"
        }

        feat = np.array([
            len(url),
            len(hostname),
            url.count("."),
            url.count("-"),
            url.count("@"),
            url.count("//"),
            url.count("/"),
            url.count("?"),
            len(parsed.query),
            1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname) else 0,
            1 if parsed.scheme == "https" else 0,
            len(hostname.split(".")),
            len([p for p in path.split("/") if p]),
            sum(c.isdigit() for c in hostname),
            1 if any(s in hostname for s in URL_SHORTENERS) else 0
        ]).reshape(1, -1)

        scaled = _scaler.transform(feat)
        pred   = _model.predict(scaled)[0]
        proba  = _model.predict_proba(scaled)[0]

        return {
            "prediction": "PHISHING" if pred == 1 else "SAFE",
            "probability": float(max(proba)),
            "confidence":  float(max(proba))
        }

    except Exception as e:
        return {
            "prediction": "UNKNOWN",
            "probability": 0.5,
            "confidence": 0.0
        }