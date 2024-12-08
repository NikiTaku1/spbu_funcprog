import json

def load_books(filepath="data/books.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)