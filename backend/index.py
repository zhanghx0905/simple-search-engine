import os
from dataclasses import asdict

import numpy as np
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import SparseMatrixSimilarity

from spider import Page, run_spider
from utils import INDEX_PATH, get_tokens, load_pkl, save_pkl


class Index:
    def __init__(self, pages: list[Page]) -> None:
        self.pages = pages
        bodies = [get_tokens(page.body) for page in pages]
        titles = [get_tokens(page.title) for page in pages]

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

    def search(self, query: str, topk: int = 50):  # -> list[Page]:
        tokens = get_tokens(query)
        query_bow = self.dictionary.doc2bow(tokens)
        query_tfidf = self.tfidf[query_bow]
        bsim = self.bindex[query_tfidf]
        tsim = self.tindex[query_tfidf]
        sim: np.ndarray = cal_scores(tsim, bsim)
        indices = reversed(np.argsort(sim)[-topk:])
        return [
            {"score": sim[id], **asdict(self.pages[id])}
            for id in indices
            if sim[id] > 0
        ]

def cal_scores(title, body):
    # Only float64 is Json serializable
    return np.float64(5 * title + body)


def load_index():
    pages, updated = run_spider()
    if updated or not os.path.isfile(INDEX_PATH):
        print("building index")
        index = Index(pages)
        save_pkl(INDEX_PATH, index)
        print(f"index saved at {INDEX_PATH}")
    else:
        index: Index = load_pkl(INDEX_PATH)
        print(f"index loaded from {INDEX_PATH}")
    return index


if __name__ == "__main__":
    index = load_index()
    from pprint import pprint

    ret = index.search("HKUST")
    for r in ret:
        print(r["score"], r["url"], r["title"])
    # pprint(index.similar_pages(316))  # PG page
