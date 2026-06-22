from utils.feature_extractor import extract_url_features
from models.predict import predict_url
from utils.risk_engine import  compute_risk_score

url = "http://secure-login-bank.com"

features = extract_url_features(url)

# Rule-based score
rule_result = compute_risk_score(features)
rule_score = rule_result["risk_score"]

# ML score
ml_score = predict_url(features)

# Final hybrid score
final_score = (rule_score * 0.4) + (ml_score * 0.6)

# Final verdict
if final_score < 0.3:
    verdict = "Safe"
elif final_score < 0.7:
    verdict = "Suspicious"
else:
    verdict = "Phishing"

# Print everything
print("Rule Score:", rule_score)
print("ML Score:", ml_score)
print("Final Score:", round(final_score, 2))
print("Verdict:", verdict)
print("Reasons:", rule_result["reasons"])