import pandas as pd
import numpy as np
import joblib


from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding,LSTM,Dense,Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


##-----LOAD DATA-----##
df = pd.read_csv(f'data\phishing_url_dataset_unique.csv')

df = df.dropna(subset = ["url", "label"])

urls = df["url"].astype(str).values
labels = df["label"].values

print(f"✅ Dataset loaded: {len(urls)} samples")

##------TOKENIZATION-----##

tokenizer = Tokenizer(char_level = True)
tokenizer.fit_on_texts(urls)

sequences = tokenizer.texts_to_sequences(urls)

MAX_LEN = 200

X = pad_sequences(sequences,maxlen = MAX_LEN)
y = np.array(labels)

##--------SPLIT-------##
X_train,X_test,y_train,y_test = train_test_split(
    X,y,test_size = 0.2,random_state=42
)

# ---------------- MODEL ----------------
model = Sequential([
    Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=64),
    LSTM(64, return_sequences=False),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

model.summary()

# ---------------- TRAIN ----------------
print("🚀 Training model...")
history = model.fit(
    X_train,
    y_train,
    epochs=8,              # ⬅️ increased
    batch_size=64,         # ⬅️ better
    validation_data=(X_test, y_test)
)
# ---------------- EVALUATION ----------------
preds = model.predict(X_test)
preds = (preds > 0.5).astype(int)

acc = accuracy_score(y_test, preds)

print(f"\n✅ Final Accuracy: {acc:.4f}")


# ---------------- SAVE ----------------
model.save("backend/models/dl_model.h5")
joblib.dump(tokenizer, "backend/models/tokenizer.pkl")

print("✅ Deep Learning model saved!")