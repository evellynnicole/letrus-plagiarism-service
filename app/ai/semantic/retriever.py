# app/ai/semantic/retriever.py
from typing import Any, Dict, List

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from app.config.config import Config


class Retriever:
    """Executa buscas dense-only e híbridas (dense + sparse) no Qdrant."""

    def __init__(self, config: Config):
        """Inicializa o retriever."""
        self.config = config
        self.client = QdrantClient(url=self.config.qdrant_url)
        self.dense_name = self.config.dense_name
        self.sparse_name = self.config.sparse_name
        self.dense_model_name = self.config.model_dense_name
        self.sparse_model_name = self.config.model_sparse_name

        self.enc = TextEmbedding(self.dense_model_name)

    def encode_query(self, query: str) -> List[float]:
        """Gera o embedding denso para a consulta."""
        return list(self.enc.embed([query]))[0].tolist()

    def search_dense_only(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Busca apenas no índice denso. Retorna score = cosine (da própria coleção)."""
        q_vec = self.encode_query(query)
        res = self.client.query_points(
            collection_name=self.config.qdrant_collection_dense,
            query=q_vec,
            using=self.dense_name,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        return [
            {
                "id": p.id,
                "similarity": p.score,
                "text": (p.payload or {}).get("text"),
            }
            for p in res.points
        ]

    def search_hybrid(
        self,
        query: str,
        top_k: int = 3,
        candidates_dense: int = 10,
        candidates_sparse: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Híbrido: combina dense+sparse via RRF para ORDENAR.
        Depois, roda uma segunda consulta rápida filtrando pelos IDs retornados
        para obter o cosine oficial do Qdrant. O campo `score` abaixo é SEMPRE
        a similaridade de cosseno.
        """
        q_vec = self.encode_query(query)

        dense_prefetch = models.Prefetch(
            query=q_vec,
            using=self.dense_name,
            limit=candidates_dense,
        )
        sparse_prefetch = models.Prefetch(
            query=models.Document(text=query, model=self.sparse_model_name),
            using=self.sparse_name,
            limit=candidates_sparse,
        )

        fusion = models.FusionQuery(fusion=models.Fusion.RRF)
        fused = self.client.query_points(
            collection_name=self.config.qdrant_collection_hybrid,
            prefetch=[dense_prefetch, sparse_prefetch],
            query=fusion,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        if not fused.points:
            return []

        ids = [p.id for p in fused.points]

        dense_filtered = self.client.query_points(
            collection_name=self.config.qdrant_collection_dense,
            query=q_vec,
            using=self.dense_name,
            limit=len(ids),
            with_payload=False,
            with_vectors=False,
            query_filter=models.Filter(must=[models.HasIdCondition(has_id=ids)]),
        )

        cos_by_id: Dict[Any, float] = {p.id: p.score for p in dense_filtered.points}

        results: List[Dict[str, Any]] = []
        for p in fused.points:
            results.append(
                {
                    "id": p.id,
                    "similarity": cos_by_id.get(p.id),
                    "text": (p.payload or {}).get("text"),
                }
            )
        return results
