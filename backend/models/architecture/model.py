"""
Complete Hybrid Deep Learning Model

Architecture:

Input
    │
Embedding
    │
Multi-Scale CNN
    │
BiLSTM
    │
Bahdanau Attention
    │
Dense Network
    │
Sigmoid
"""

import tensorflow as tf

from .embedding import build_embedding
from .cnn_encoder import build_cnn_encoder
from .attention import BahdanauAttention

from ..core.config import (
    MAX_URL_LENGTH,
    EMBEDDING_DIM
)


def build_model(vocab_size):

    # ---------------------------------------------------
    # Input
    # ---------------------------------------------------

    inputs = tf.keras.Input(
        shape=(MAX_URL_LENGTH,),
        name="URL_Input"
    )

    # ---------------------------------------------------
    # Character Embedding
    # ---------------------------------------------------

    embedding = build_embedding(vocab_size)

    x = embedding(inputs)

    # ---------------------------------------------------
    # Multi-Scale CNN
    # ---------------------------------------------------

    x = build_cnn_encoder(x)

    # ---------------------------------------------------
    # Bidirectional LSTM
    # ---------------------------------------------------

    x = tf.keras.layers.Bidirectional(

        tf.keras.layers.LSTM(

            128,

            return_sequences=True,

            dropout=0.30,

            recurrent_dropout=0.20

        ),

        name="BiLSTM"

    )(x)

    # ---------------------------------------------------
    # Bahdanau Attention
    # ---------------------------------------------------

    context_vector, attention_weights = BahdanauAttention(

        128

    )(x)

    # ---------------------------------------------------
    # Fully Connected Classifier
    # ---------------------------------------------------

    x = tf.keras.layers.Dense(

        256,

        activation="relu"

    )(context_vector)

    x = tf.keras.layers.Dropout(

        0.40

    )(x)

    x = tf.keras.layers.Dense(

        128,

        activation="relu"

    )(x)

    x = tf.keras.layers.Dropout(

        0.30

    )(x)

    x = tf.keras.layers.Dense(

        64,

        activation="relu"

    )(x)

    outputs = tf.keras.layers.Dense(

        1,

        activation="sigmoid",

        name="Prediction"

    )(x)

    # ---------------------------------------------------

    model = tf.keras.Model(

        inputs,

        outputs,

        name="URLShieldNet"

    )

    return model