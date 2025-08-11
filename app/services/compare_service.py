from typing import Any, Dict, List

from app.ai.lexical.tfidf import TextSimilarity
from app.ai.semantic.retriever import Retriever
from app.config.config import Config
from app.utils.json_utils import load_pt_corpus_from_jsonl


class CompareService:
    """Orquestra as buscas léxicas (TF-IDF) e semânticas"""

    def __init__(self, config: Config):
        self.config = config

        self._corpus_texts: List[str] = load_pt_corpus_from_jsonl(self.config.data_path)
        if not self._corpus_texts:
            raise RuntimeError(f"Nenhum texto encontrado em {self.config.data_path}")

        self._tfidf = TextSimilarity()
        self._tfidf.fit(self._corpus_texts)

        self._retriever = Retriever(self.config)

    def compare_lexical(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        ranked = self._tfidf.rank(text, top_k=top_k)
        return [
            {
                "index": idx,
                "similarity": similarity,
                "text": self._corpus_texts[idx]
            }
            for idx, similarity in ranked
        ]

    def compare_semantic(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        return self._retriever.search_dense_only(text, top_k=top_k)

    def compare_hybrid(self, text: str, top_k: int) -> List[Dict[str, Any]]:
        return self._retriever.search_hybrid(query=text, top_k=top_k)
