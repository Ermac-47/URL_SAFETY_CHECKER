import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

model = load_model("backend/models/dl_model.h5")
tokenizer = joblib.load("backend/models/tokenizer.pkl")

MAX_LEN = 200

def predict_url(url):
    seq = tokenizer.texts_to_sequences([url])
    padded = pad_sequences(seq, maxlen=MAX_LEN)

    prob = model.predict(padded, verbose=0)[0][0]
    return float(prob)