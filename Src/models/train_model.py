import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier

from Src.utils.feature_extractor import extract_url_features


# ---------------- LOAD DATA ----------------
df = pd.read_csv("data/urls.csv")
total_rows = len(df)

X = []
y = []

feature_keys = None
skipped = 0

for i, (_, row) in enumerate(df.iterrows(), start=1):
    url = row["url"]
    label = row["label"]

    print(f"[{i}/{total_rows}] Processing {url} ...", flush=True)

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
        skipped += 1
        print(f"  Skipping {url} due to error: {e}", flush=True)
        continue

print(f"\nDone extracting features. Used {len(X)} rows, skipped {skipped} rows.\n", flush=True)

if len(X) < 10:
    raise RuntimeError(
        f"Only {len(X)} usable rows after feature extraction — too few to train. "
        "Check network access / WHOIS rate limits."
    )

# ---------------- MODEL CONFIG ----------------
# max_depth / min_samples_* constrain how deeply each tree can grow,
# which reduces overfitting on a small (few hundred row) dataset.
# class_weight="balanced" guards against skew if the safe/phishing
# split isn't exactly 50/50 after feature extraction skips some rows.
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=6,
    min_samples_leaf=4,
    min_samples_split=8,
    class_weight="balanced",
    random_state=42,
)

# ---------------- CROSS-VALIDATION (more honest estimate than 1 split) ----------------
print("Running 5-fold cross-validation...", flush=True)
cv_scores = cross_val_score(model, X, y, cv=5)
print(f"CV fold scores: {[round(s, 3) for s in cv_scores]}", flush=True)
print(f"Mean CV accuracy: {cv_scores.mean():.3f}  (+/- {cv_scores.std():.3f})\n", flush=True)

# ---------------- FINAL TRAIN/TEST SPLIT (for the saved model + a readable number) ----------------
print("Splitting into train/test sets...", flush=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training final RandomForestClassifier on the train split...", flush=True)
model.fit(X_train, y_train)

train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)
print(f"Train accuracy: {train_acc:.3f}  |  Test accuracy: {test_acc:.3f}", flush=True)

# Refit on ALL data before saving, so the shipped model uses every available row
# (the train/test split above is only for reporting honest metrics).
print("Refitting on full dataset for final saved model...", flush=True)
model.fit(X, y)

# ---------------- SAVE ----------------
joblib.dump(model, "Src/models/phishing_model.pkl")
joblib.dump(feature_keys, "Src/models/feature_keys.pkl")

print("✅ Model trained and saved!")c