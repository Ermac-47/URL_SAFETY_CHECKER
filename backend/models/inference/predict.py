# backend/models/inference/predict.py
import pickle
import numpy as np
import os

_model = None
_scaler = None

def _load():
    global _model, _scaler
    model_path = os.path.join(os.path.dirname(__file__), 
                              '../../trained_models/rf_model.pkl')
    # fallback to root data folder
    if not os.path.exists(model_path):
        model_path = 'data/models/rf_model.pkl'
    scaler_path = model_path.replace('rf_model', 'scaler')
    
    if _model is None and os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            _model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            _scaler = pickle.load(f)

def predict_url(url: str) -> dict:
    try:
        _load()
        if _model is None:
            return {"prediction": "UNKNOWN", "probability": 0.5, "confidence": 0.0}
        
        from utils.feature_extractor import extract_url_features
        features = extract_url_features(url)
        
        feat_vec = np.array([
            features.get('url_length', 0),
            features.get('domain_length', 0),
            features.get('dot_count', 0),
            features.get('hyphen_count', 0),
            features.get('at_count', 0),
            features.get('double_slash', 0),
            features.get('slash_count', 0),
            features.get('query_count', 0),
            features.get('query_length', 0),
            features.get('has_ip', 0),
            features.get('has_https', 0),
            features.get('subdomain_depth', 0),
            features.get('path_depth', 0),
            features.get('digit_count', 0),
            features.get('is_shortener', 0),
        ]).reshape(1, -1)
        
        scaled = _scaler.transform(feat_vec)
        pred = _model.predict(scaled)[0]
        proba = _model.predict_proba(scaled)[0]
        
        return {
            "prediction": "PHISHING" if pred == 1 else "SAFE",
            "probability": float(max(proba)),
            "confidence": float(max(proba))
        }
    except Exception as e:
        return {"prediction": "UNKNOWN", "probability": 0.5, "confidence": 0.0}
