import joblib

model = joblib.load("Src/models/phishing_model.pkl")
feature_keys = joblib.load("Src/models/feature_keys.pkl")


def predict_url(features):
    features.pop("domain", None)

    x = [features[k] for k in feature_keys]

    prob = model.predict_proba([x])[0][1]  # phishing probability
    return prob