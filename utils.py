import json
import pickle

DATA_PATH = "data/output.json"
INDEX_PATH = "data/index.pkl"
STOPWORDS_PATH = "data/stopwords.txt"


def save_json(path: str, data: dict, **kwargs):
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, **kwargs)


def load_json(path: str):
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)
    return data


def save_pkl(path, obj):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_pkl(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data
