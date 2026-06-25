from backend.models.preprocessing.dataset import URLDataset

dataset = URLDataset()

(
    X_train,
    X_valid,
    X_test,
    y_train,
    y_valid,
    y_test,
    vocab_size
) = dataset.prepare()

print()

print("Train Shape :", X_train.shape)

print("Validation Shape :", X_valid.shape)

print("Test Shape :", X_test.shape)

print("Vocabulary :", vocab_size)