"""
Bahdanau Attention Layer
"""

import tensorflow as tf
from keras.saving import register_keras_serializable

@register_keras_serializable(package="URLShieldNet")
class BahdanauAttention(tf.keras.layers.Layer):

    def __init__(self, units,**kwargs):
        super().__init__()

        self.units = units

        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, values):

        """
        values shape

        (batch_size,
         sequence_length,
         hidden_size)
        """

        hidden_with_time_axis = tf.expand_dims(

            values[:, -1, :],

            1

        )

        score = self.V(

            tf.nn.tanh(

                self.W1(values)

                +

                self.W2(hidden_with_time_axis)

            )

        )

        attention_weights = tf.nn.softmax(

            score,

            axis=1

        )

        context_vector = attention_weights * values

        context_vector = tf.reduce_sum(

            context_vector,

            axis=1

        )

        return context_vector, attention_weights
    
    def get_config(self):
        config = super().get_config()

        config.update(
            {
                "units": self.units
            }
        )

        return config