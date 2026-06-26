"""
Multi-Scale CNN Encoder

This encoder preserves sequence information.

Input:
(batch, sequence_length, embedding_dim)

Output:
(batch, sequence_length, filters*4)

The BiLSTM will learn relationships across the sequence,
and the Attention layer will decide which positions matter.
"""

import tensorflow as tf

from ..core.config import CNN_FILTERS


def cnn_block(inputs, kernel_size):

    x = tf.keras.layers.Conv1D(
        filters=CNN_FILTERS,
        kernel_size=kernel_size,
        padding="same",
        activation="relu"
    )(inputs)

    x = tf.keras.layers.BatchNormalization()(x)

    return x


def build_cnn_encoder(inputs):

    branch3 = cnn_block(inputs, 3)

    branch5 = cnn_block(inputs, 5)

    branch7 = cnn_block(inputs, 7)

    branch9 = cnn_block(inputs, 9)

    output = tf.keras.layers.Concatenate(
        axis=-1,
        name="MultiScaleCNN"
    )([
        branch3,
        branch5,
        branch7,
        branch9
    ])

    return output