"""
Deep Learning Prediction Module

This module loads the trained URLShieldNet model
and predicts whether a URL is safe or phishing.
"""

import os
import joblib
import numpy as np
import tensorflow as tf

from models.architecture.attention import BahdanauAttention
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from models.core.config import MAX_URL_LENGTH


# ============================================
# PATHS
# ============================================

MODEL_PATH = "backend/models/trained_models/url_detector.keras"
TOKENIZER_PATH = "backend/models/trained_models/tokenizer.pkl"


# ============================================
# LOAD MODEL
# ============================================

print("Loading URLShieldNet...")

model = load_model(
    MODEL_PATH,
    compile=False,
    custom_objects={
        "BahdanauAttention": BahdanauAttention
    }
)

print("Model Loaded Successfully.")


# ============================================
# LOAD TOKENIZER
# ============================================

tokenizer = joblib.load(TOKENIZER_PATH)

print("Tokenizer Loaded Successfully.")


# ============================================
# PREPROCESS URL
# ============================================

def preprocess_url(url):

    sequence = tokenizer.texts_to_sequences([url])

    padded = pad_sequences(
        sequence,
        maxlen=MAX_URL_LENGTH,
        padding="post",
        truncating="post"
    )

    return padded


# ============================================
# PREDICT
# ============================================

def predict_url(url):

    X = preprocess_url(url)

    probability = float(
        model.predict(
            X,
            verbose=0
        )[0][0]
    )

    prediction = "PHISHING" if probability >= 0.5 else "SAFE"

    confidence = probability if prediction == "PHISHING" else (1 - probability)

    return {

        "url": url,

        "prediction": prediction,

        "probability": probability,

        "confidence": confidence

    }


# ============================================
# BATCH PREDICTION
# ============================================

def predict_batch(urls):

    results = []

    for url in urls:

        results.append(

            predict_url(url)

        )

    return results


# ============================================
# TEST
# ============================================

if __name__ == "__main__":

    test_urls = [

        "https://google.com",

        "https://go0gle-login.com",

        "https://paypal.com",

        "http://192.168.1.5/login"

    ]

    predictions = predict_batch(test_urls)

    for result in predictions:

        print()

        print(result)