"""
Embedding Layer
---------------

Converts URL characters into dense vector representations.

Input:
(batch, sequence_length)

Output:
(batch, sequence_length, embedding_dim)
"""

import tensorflow as tf

from ..core.config import (
    EMBEDDING_DIM,
    MAX_URL_LENGTH
)


def build_embedding(vocab_size):

    embedding = tf.keras.layers.Embedding(

        input_dim=vocab_size,

        output_dim=EMBEDDING_DIM,

        input_length=MAX_URL_LENGTH,

        name="CharacterEmbedding"

    )

    return embedding