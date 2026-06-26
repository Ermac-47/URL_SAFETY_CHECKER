import tensorflow as tf

from backend.models.architecture.attention import BahdanauAttention

batch = 8

sequence = 200

hidden = 256

x = tf.random.normal(

    (batch, sequence, hidden)

)

attention = BahdanauAttention(128)

context, weights = attention(x)

print()

print("Context Shape")

print(context.shape)

print()

print("Weights Shape")

print(weights.shape)