"""
Global configuration for the Deep Learning URL Detector
"""

# ======================================================
# DATASET
# ======================================================

DATASET_PATH = "data/phishing_url_dataset_unique.csv"

# ======================================================
# TOKENIZER
# ======================================================

CHAR_LEVEL = True

MAX_URL_LENGTH = 200

# ======================================================
# MODEL
# ======================================================

EMBEDDING_DIM = 64

CNN_FILTERS = 128

CNN_KERNEL_SIZES = [3, 5, 7]

LSTM_UNITS = 128

DENSE_1 = 128

DENSE_2 = 64

DROPOUT_RATE = 0.40

# ======================================================
# TRAINING
# ======================================================

BATCH_SIZE = 128

EPOCHS = 20

VALIDATION_SPLIT = 0.20

LEARNING_RATE = 0.001

RANDOM_STATE = 42

# ======================================================
# SAVE PATHS
# ======================================================

MODEL_PATH = "backend/models/trained_models/url_detector.keras"

TOKENIZER_PATH = "backend/models/trained_models/tokenizer.pkl"

HISTORY_PATH = "backend/models/trained_models/history.pkl"

MODEL_INFO_PATH = "backend/models/trained_models/model_info.json"