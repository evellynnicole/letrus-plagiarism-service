# app/ai/lexical/tfidf.py
from typing import List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TextSimilarity:
    """
    TF‑IDF + cosseno para ranquear quais docs do corpus são mais similares com uma query.
    Uso:
        ts = TextSimilarity()
        ts.fit(corpus)
        ts.rank("meu trecho", top_k=5)
        ts.top1("meu trecho")  # só o mais parecido
    """

    def __init__(
        self,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 2,
        max_df: float = 0.9,
        max_features: Optional[int] = 100_000,
    ):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            max_features=max_features,
        )
        self._tfidf_matrix = None
        self.docs: List[str] = []

    def fit(self, texts: List[str]) -> None:
        """Treina o vetorizar no corpus e guarda a matriz TF-IDF."""
        self.docs = texts
        self._tfidf_matrix = self.vectorizer.fit_transform(texts)

    def rank(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Retorna os índices dos documentos mais parecidos com a `query` e seus scores.
        Saída: lista de (indice_no_corpus, score) em ordem decrescente.
        """
        if self._tfidf_matrix is None:
            raise RuntimeError("Chame fit(corpus) antes de rank().")

        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self._tfidf_matrix)[0]

        top_k = max(1, min(top_k, len(self.docs)))
        idx = np.argsort(-scores)[:top_k]
        return [(int(i), float(scores[i])) for i in idx]

    def top1(self, query: str) -> Tuple[int, float]:
        """Retorna (indice, score) do **documento mais parecido** com a query."""
        idx_score = self.rank(query, top_k=1)[0]
        return idx_score
