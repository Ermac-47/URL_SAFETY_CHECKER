from backend.models.architecture.model import build_model

VOCAB = 90

model = build_model(VOCAB)

model.summary()