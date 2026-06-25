from backend.models.preprocessing.tokenizer import URLTokenizer

urls = [
    "https://google.com",
    "https://go0gle.com",
    "https://amazon.com/login"
]

tok = URLTokenizer()

X = tok.fit_transform(urls)

print(X.shape)

print(tok.vocab_size)

tok.save()