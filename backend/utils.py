import json
import pickle
import re
from collections import Counter
from string import punctuation, whitespace

import spacy  # python -m spacy download en_core_web_sm

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


def load_stopwords(path: str):
    with open(path, "r", encoding="utf8") as f:
        words = f.read().splitlines()
    words += list(punctuation + whitespace)
    return set(words)


STOPWORDS = load_stopwords(STOPWORDS_PATH)
NLP = spacy.load("en_core_web_sm")
PUNC_ESCAPER = re.compile(r"[{}]+".format(punctuation))


def escape(s: str):
    return s in STOPWORDS or s.isspace() or s.isnumeric()


def get_tokens(text: str, pharse: bool = True) -> list[str]:
    text = PUNC_ESCAPER.sub(" ", text)
    doc = NLP(text)
    stems = [token.lemma_.lower() for token in doc]
    tokens = [token for token in stems if not escape(token)]
    if pharse:
        tokens.extend(
            chunk.text
            for chunk in doc.noun_chunks
            if chunk.text.count(" ") > 0 and not escape(chunk.text)
        )
    return tokens


# define a function to extract keywords
def extract_keywords(title, article, n=5):
    tokens = get_tokens(article, False) + get_tokens(title, False)
    # calculate word frequencies
    freq_dist = Counter(tokens)

    # get the top n keywords
    top_n = freq_dist.most_common(n)

    return [(word, freq) for word, freq in top_n]
