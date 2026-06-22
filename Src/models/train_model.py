import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from Src.utils.feature_extractor import extract_url_features


# ---------------- LOAD DATA ----------------
df = pd.read_csv("data/urls.csv")

X = []
y = []

feature_keys = None

for _, row in df.iterrows():
    url = row["url"]
    label = row["label"]

    try:
        features = extract_url_features(url)

        # remove non-numeric
        features.pop("domain", None)

        # fix feature order ONCE
        if feature_keys is None:
            feature_keys = sorted(features.keys())

        X.append([features[k] for k in feature_keys])
        y.append(label)

    except Exception as e:
        print(f"Skipping {url} due to error: {e}")
        continue


# ---------------- TRAIN ----------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# ---------------- SAVE ----------------
joblib.dump(model, "Src/models/phishing_model.pkl")
joblib.dump(feature_keys, "Src/models/feature_keys.pkl")

print("✅ Model trained and saved!")