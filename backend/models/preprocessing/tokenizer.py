"""
Tokenizer module for URL Safety Checker

Responsibilities:
1. Build character-level tokenizer
2. Convert URLs into padded sequences
3. Save tokenizer
4. Load tokenizer
"""

import os
import joblib

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from backend.models.core.config import (
    CHAR_LEVEL,
    MAX_URL_LENGTH,
    TOKENIZER_PATH
)


class URLTokenizer:

    def __init__(self):
        self.tokenizer = Tokenizer(
            char_level=CHAR_LEVEL,
            lower=True,
            filters=""          # Don't remove URL characters
        )

    # --------------------------------------------------
    # Train tokenizer
    # --------------------------------------------------

    def fit(self, urls):
        self.tokenizer.fit_on_texts(urls)

    # --------------------------------------------------
    # Convert URLs to sequences
    # --------------------------------------------------

    def transform(self, urls):

        sequences = self.tokenizer.texts_to_sequences(urls)

        padded = pad_sequences(
            sequences,
            maxlen=MAX_URL_LENGTH,
            padding="post",
            truncating="post"
        )

        return padded

    # --------------------------------------------------
    # Fit + Transform
    # --------------------------------------------------

    def fit_transform(self, urls):

        self.fit(urls)

        return self.transform(urls)

    # --------------------------------------------------
    # Save tokenizer
    # --------------------------------------------------

    def save(self):

        os.makedirs(os.path.dirname(TOKENIZER_PATH), exist_ok=True)

        joblib.dump(
            self.tokenizer,
            TOKENIZER_PATH
        )

        print(f"✅ Tokenizer saved to {TOKENIZER_PATH}")

    # --------------------------------------------------
    # Load tokenizer
    # --------------------------------------------------

    @classmethod
    def load(cls):

        tokenizer = cls()

        tokenizer.tokenizer = joblib.load(
            TOKENIZER_PATH
        )

        print("✅ Tokenizer loaded")

        return tokenizer

    # --------------------------------------------------
    # Vocabulary size
    # --------------------------------------------------

    @property
    def vocab_size(self):

        return len(self.tokenizer.word_index) + 1