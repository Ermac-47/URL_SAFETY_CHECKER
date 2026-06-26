"""
Save and Load Training History
"""

import os
import pickle

SAVE_DIR = "backend/models/trained_models"

os.makedirs(SAVE_DIR, exist_ok=True)


def save_history(history):

    history_path = os.path.join(
        SAVE_DIR,
        "history.pkl"
    )

    with open(history_path, "wb") as f:
        pickle.dump(history.history, f)

    print(f"\nHistory saved -> {history_path}")


def load_history():

    history_path = os.path.join(
        SAVE_DIR,
        "history.pkl"
    )

    with open(history_path, "rb") as f:
        history = pickle.load(f)

    return history