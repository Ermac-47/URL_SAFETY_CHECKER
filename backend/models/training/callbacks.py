"""
Training Callbacks
------------------

This module creates all callbacks used during training.

Includes:
- EarlyStopping
- ReduceLROnPlateau
- ModelCheckpoint
- CSVLogger
"""

import os

import tensorflow as tf


SAVE_DIR = "backend/models/trained_models"

os.makedirs(SAVE_DIR, exist_ok=True)


def get_callbacks():

    callbacks = [

        # --------------------------------------------------

        tf.keras.callbacks.EarlyStopping(

            monitor="val_loss",

            patience=5,

            restore_best_weights=True,

            verbose=1

        ),

        # --------------------------------------------------

        tf.keras.callbacks.ReduceLROnPlateau(

            monitor="val_loss",

            factor=0.5,

            patience=2,

            verbose=1,

            min_lr=1e-6

        ),

        # --------------------------------------------------

        tf.keras.callbacks.ModelCheckpoint(

            filepath=os.path.join(

                SAVE_DIR,

                "url_detector.keras"

            ),

            monitor="val_accuracy",

            save_best_only=True,

            verbose=1

        ),

        # --------------------------------------------------

        tf.keras.callbacks.CSVLogger(

            os.path.join(

                SAVE_DIR,

                "training_log.csv"

            )

        )

    ]

    return callbacks