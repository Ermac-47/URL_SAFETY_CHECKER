import tensorflow as tf

from backend.models.architecture.embedding import build_embedding

VOCAB = 90

embedding = build_embedding(VOCAB)

x = tf.random.uniform(

    shape=(8,200),

    maxval=VOCAB,

    dtype=tf.int32

)

y = embedding(x)

print()

print("Input Shape")

print(x.shape)

print()

print("Output Shape")

print(y.shape)