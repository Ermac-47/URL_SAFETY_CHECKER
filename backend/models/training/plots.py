"""
Generate Training Graphs
"""

import os
import matplotlib.pyplot as plt

SAVE_DIR = "backend/models/trained_models/plots"

os.makedirs(SAVE_DIR, exist_ok=True)


def plot_history(history):

    # ---------------- Accuracy ----------------

    plt.figure(figsize=(8,5))

    plt.plot(history.history["accuracy"], label="Train")

    plt.plot(history.history["val_accuracy"], label="Validation")

    plt.title("Accuracy")

    plt.xlabel("Epoch")

    plt.ylabel("Accuracy")

    plt.legend()

    plt.tight_layout()

    plt.savefig(os.path.join(SAVE_DIR, "accuracy.png"))

    plt.close()

    # ---------------- Loss ----------------

    plt.figure(figsize=(8,5))

    plt.plot(history.history["loss"], label="Train")

    plt.plot(history.history["val_loss"], label="Validation")

    plt.title("Loss")

    plt.xlabel("Epoch")

    plt.ylabel("Loss")

    plt.legend()

    plt.tight_layout()

    plt.savefig(os.path.join(SAVE_DIR, "loss.png"))

    plt.close()

    print("\nTraining graphs saved.")