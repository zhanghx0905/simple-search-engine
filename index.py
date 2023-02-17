import os

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
        bodies_bow = [self.dictionary.doc2bow(body) for body in bodies]
        titles_bow = [self.dictionary.doc2bow(title) for title in titles]
        corpus = bodies_bow + titles_bow
        self.tfidf = TfidfModel(corpus, self.dictionary)
        self.bindex = SparseMatrixSimilarity(
            self.tfidf[bodies_bow], len(self.dictionary)
        )
        self.tindex = SparseMatrixSimilarity(
            self.tfidf[titles_bow], len(self.dictionary)
        )

    def search(self, query: str, topk: int = 10) -> list[Page]:
        tokens = get_tokens(query)
        query_bow = self.dictionary.doc2bow(tokens)
        query_tfidf = self.tfidf[query_bow]
        bsim = self.bindex[query_tfidf]
        tsim = self.tindex[query_tfidf]
        sim = tsim * 10 + bsim
        indices = np.argpartition(sim, -topk)[-topk:]
        # TODO return page object
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
