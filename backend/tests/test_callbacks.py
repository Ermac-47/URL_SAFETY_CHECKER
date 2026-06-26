from backend.models.training.callbacks import get_callbacks

callbacks = get_callbacks()

print()

print("Callbacks Loaded")

print()

for cb in callbacks:

    print(type(cb).__name__)