"""
Model Evaluation
----------------

Evaluates the trained URLShieldNet model
on the test dataset.

Outputs

• Accuracy
• Precision
• Recall
• F1 Score
• ROC-AUC
• Confusion Matrix
• Classification Report

Also saves:

metrics.json
confusion_matrix.png
roc_curve.png
classification_report.txt
"""

import os
import json
import joblib
import numpy as np
import matplotlib.pyplot as plt
from backend.models.architecture.attention import BahdanauAttention

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    RocCurveDisplay,
    ConfusionMatrixDisplay
)

from tensorflow.keras.models import load_model

from backend.models.preprocessing.dataset import URLDataset


SAVE_DIR = "backend/models/trained_models"
PLOT_DIR = os.path.join(SAVE_DIR, "plots")

os.makedirs(PLOT_DIR, exist_ok=True)


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

print("\nLoading Dataset...\n")

dataset = URLDataset()

(
    X_train,
    X_valid,
    X_test,
    y_train,
    y_valid,
    y_test,
    vocab_size

) = dataset.prepare()


# --------------------------------------------------
# Load Model
# --------------------------------------------------

print("Loading trained model...\n")

model = load_model(
    os.path.join(
        SAVE_DIR,
        "url_detector.keras"
    ),
    compile=False,
    custom_objects={
        "BahdanauAttention": BahdanauAttention
    }
)


# --------------------------------------------------
# Predict
# --------------------------------------------------

print("Running Predictions...\n")

probabilities = model.predict(

    X_test,

    verbose=1

)

predictions = (probabilities > 0.5).astype(int)


# --------------------------------------------------
# Metrics
# --------------------------------------------------

accuracy = accuracy_score(

    y_test,

    predictions

)

precision = precision_score(

    y_test,

    predictions

)

recall = recall_score(

    y_test,

    predictions

)

f1 = f1_score(

    y_test,

    predictions

)

auc = roc_auc_score(

    y_test,

    probabilities

)


metrics = {

    "accuracy": float(accuracy),

    "precision": float(precision),

    "recall": float(recall),

    "f1_score": float(f1),

    "roc_auc": float(auc)

}


print("\n")

for key, value in metrics.items():

    print(f"{key:15}: {value:.4f}")


# --------------------------------------------------
# Save Metrics
# --------------------------------------------------

with open(

    os.path.join(

        SAVE_DIR,

        "metrics.json"

    ),

    "w"

) as f:

    json.dump(

        metrics,

        f,

        indent=4

    )


# --------------------------------------------------
# Classification Report
# --------------------------------------------------

report = classification_report(

    y_test,

    predictions

)

print("\n")

print(report)

with open(

    os.path.join(

        SAVE_DIR,

        "classification_report.txt"

    ),

    "w"

) as f:

    f.write(report)


# --------------------------------------------------
# Confusion Matrix
# --------------------------------------------------

cm = confusion_matrix(

    y_test,

    predictions

)

disp = ConfusionMatrixDisplay(cm)

disp.plot()

plt.tight_layout()

plt.savefig(

    os.path.join(

        PLOT_DIR,

        "confusion_matrix.png"

    )

)

plt.close()


# --------------------------------------------------
# ROC Curve
# --------------------------------------------------

RocCurveDisplay.from_predictions(

    y_test,

    probabilities

)

plt.tight_layout()

plt.savefig(

    os.path.join(

        PLOT_DIR,

        "roc_curve.png"

    )

)

plt.close()


print("\n")

print("=" * 60)

print("EVALUATION COMPLETED")

print("=" * 60)