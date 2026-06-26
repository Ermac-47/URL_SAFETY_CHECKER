import tensorflow as tf

from backend.models.architecture.embedding import build_embedding
from backend.models.architecture.cnn_encoder import build_cnn_encoder

VOCAB = 90

embedding = build_embedding(VOCAB)

inputs = tf.keras.Input(shape=(200,))

x = embedding(inputs)

outputs = build_cnn_encoder(x)

print()

print(outputs.shape)

model = tf.keras.Model(inputs, outputs)

model.summary()