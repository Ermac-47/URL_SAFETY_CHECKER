"""
Dataset Loader

Responsibilities:
1. Load dataset
2. Clean dataset
3. Shuffle dataset
4. Train/Validation/Test split
5. Tokenize URLs
6. Return tensors ready for training
"""

import pandas as pd

from sklearn.model_selection import train_test_split

from .tokenizer import URLTokenizer
from ..core.config import *


class URLDataset:

    def __init__(self):

        self.tokenizer = URLTokenizer()

    # ----------------------------------------------------
    # Load CSV
    # ----------------------------------------------------

    def load_dataset(self):

        print("Loading Dataset...")

        df = pd.read_csv(DATASET_PATH)

        print(f"Original Dataset Size : {len(df)}")

        return df

    # ----------------------------------------------------
    # Clean Dataset
    # ----------------------------------------------------

    def clean_dataset(self, df):

        print("Cleaning Dataset...")

        # Keep required columns
        df = df[["url", "label"]]

        # Remove missing values
        df = df.dropna()

        # Remove duplicate URLs
        df = df.drop_duplicates(subset="url")

        # Convert labels
        df["label"] = df["label"].astype(int)

        print(f"Dataset after cleaning : {len(df)}")

        return df

    # ----------------------------------------------------
    # Prepare Data
    # ----------------------------------------------------

    def prepare(self):

        df = self.load_dataset()

        df = self.clean_dataset(df)

        urls = df["url"].tolist()

        labels = df["label"].values

        print("Building Tokenizer...")

        X = self.tokenizer.fit_transform(urls)

        self.tokenizer.save()

        print("Tokenizer Built!")

        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            labels,
            test_size=0.20,
            random_state=RANDOM_STATE,
            stratify=labels
        )

        X_valid, X_test, y_valid, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=0.50,
            random_state=RANDOM_STATE,
            stratify=y_temp
        )

        print("\nDataset Summary")

        print("--------------------------")

        print("Train :", len(X_train))

        print("Validation :", len(X_valid))

        print("Test :", len(X_test))

        print("--------------------------")

        return (

            X_train,

            X_valid,

            X_test,

            y_train,

            y_valid,

            y_test,

            self.tokenizer.vocab_size

        )