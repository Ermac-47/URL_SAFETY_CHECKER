"""
Main Training Script
"""

import os

import tensorflow as tf

from backend.models.preprocessing.dataset import URLDataset

from backend.models.architecture.model import build_model

from backend.models.training.callbacks import get_callbacks

from backend.models.training.metrics import get_metrics

from backend.models.training.history import save_history

from backend.models.training.plots import plot_history

from backend.models.core.config import (
    LEARNING_RATE,
    EPOCHS,
    BATCH_SIZE
)


# ==========================================
# GPU INFO
# ==========================================

print("=" * 60)
print("TensorFlow Version :", tf.__version__)
print("GPUs :", tf.config.list_physical_devices("GPU"))
print("=" * 60)


# ==========================================
# LOAD DATASET
# ==========================================

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


# ==========================================
# BUILD MODEL
# ==========================================

print("\nBuilding Model...\n")

model = build_model(vocab_size)

model.summary()


# ==========================================
# COMPILE
# ==========================================

print("\nCompiling Model...\n")

model.compile(

    optimizer=tf.keras.optimizers.Adam(

        learning_rate=LEARNING_RATE

    ),

    loss="binary_crossentropy",

    metrics=get_metrics()

)


# ==========================================
# CALLBACKS
# ==========================================

callbacks = get_callbacks()


# ==========================================
# TRAIN
# ==========================================

print("\nTraining Started...\n")

history = model.fit(

    X_train,

    y_train,

    validation_data=(

        X_valid,

        y_valid

    ),

    epochs=EPOCHS,

    batch_size=BATCH_SIZE,

    callbacks=callbacks,

    verbose=1

)


# ==========================================
# SAVE HISTORY
# ==========================================

save_history(history)


# ==========================================
# SAVE PLOTS
# ==========================================

plot_history(history)


# ==========================================
# EVALUATE
# ==========================================

print("\nEvaluating...\n")

results = model.evaluate(

    X_test,

    y_test,

    verbose=0

)

print("\n")

for metric, value in zip(

    model.metrics_names,

    results

):

    print(f"{metric:15} : {value:.4f}")


# ==========================================
# SAVE MODEL SUMMARY
# ==========================================

save_dir = "backend/models/trained_models"

os.makedirs(save_dir, exist_ok=True)

summary_file = os.path.join(

    save_dir,

    "model_summary.txt"

)

with open(summary_file, "w",encoding="utf-8") as f:

    model.summary(

        print_fn=lambda x: f.write(x + "\n")

    )

print("\nModel summary saved.")


print("\n")

print("=" * 60)

print("TRAINING COMPLETED SUCCESSFULLY")

print("=" * 60)