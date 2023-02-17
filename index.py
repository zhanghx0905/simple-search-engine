import os
from string import punctuation

import numpy as np
import spacy  # python -m spacy download en_core_web_sm
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import SparseMatrixSimilarity

from spider import Page, run_spider
from utils import INDEX_PATH, STOPWORDS_PATH, load_pkl, save_pkl


def load_stopwords(path: str):
    with open(path, "r", encoding="utf8") as f:
        words = f.read().splitlines()
    words += list(punctuation)
    return set(words)


STOPWORDS = load_stopwords(STOPWORDS_PATH)
NLP = spacy.load("en_core_web_sm")


class Index:
    def __init__(self, pages: list[Page]) -> None:
        self.pages = pages
        bodies = [self.get_tokens(page.body) for page in pages]
        titles = [self.get_tokens(page.title) for page in pages]

        self.dictionary = Dictionary(bodies + titles)
        self.bodies_bow = [self.dictionary.doc2bow(body) for body in bodies]
        self.titles_bow = [self.dictionary.doc2bow(title) for title in titles]
        corpus = self.bodies_bow + self.titles_bow
        self.tfidf = TfidfModel(corpus, self.dictionary)
        self.bindex = SparseMatrixSimilarity(
            self.tfidf[self.bodies_bow], len(self.dictionary)
        )
        self.tindex = SparseMatrixSimilarity(
            self.tfidf[self.titles_bow], len(self.dictionary)
        )

    def get_tokens(self, text: str) -> list[str]:
        doc = NLP(text.lower())
        tokens = [token.lemma_ for token in doc if token not in STOPWORDS]
        tokens.extend(
            chunk.text for chunk in doc.noun_chunks if chunk.text.count(" ") > 0
        )
        return tokens

    def search(self, query: str, topk: int = 10) -> list[Page]:
        tokens = self.get_tokens(query)
        query_bow = self.dictionary.doc2bow(tokens)
        query_tfidf = self.tfidf[query_bow]
        bsim = self.bindex[query_tfidf]
        tsim = self.tindex[query_tfidf]
        sim = tsim * 10 + bsim
        indices = np.argpartition(sim, -topk)[-topk:]
        return {sim[id]: self.pages[id].url for id in indices}


def load_index():
    pages, updated = run_spider()
    if updated or not os.path.isfile(INDEX_PATH):
        index = Index(pages)
        save_pkl(INDEX_PATH, index)
    else:
        index: Index = load_pkl(INDEX_PATH)
    return index


if __name__ == "__main__":
    index = load_index()
    import pprint
    pprint.pprint(index.search("hong kong"))
