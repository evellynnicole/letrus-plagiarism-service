# app/ai/semantic/indexer.py
import hashlib
import os
import uuid
from typing import Any, Dict, Iterable, List

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config.config import Config
from app.utils.json_utils import iter_jsonl


class Indexer:
    def __init__(self, config: Config):
        """Inicializa o indexador com as configurações e o cliente Qdrant."""
        self.config = config
        self.client = QdrantClient(url=self.config.qdrant_url)
        self.DENSE_NAME = self.config.dense_name
        self.SPARSE_NAME = self.config.sparse_name
        self.UUID_NS = uuid.UUID("11111111-2222-3333-4444-555555555555")
        self.DENSE_MODEL = self.config.model_dense_name
        self.SPARSE_MODEL = self.config.model_sparse_name

    @staticmethod
    def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
        """Lê um arquivo JSONL e gera dicionários com id e texto."""
        for o in iter_jsonl(path):
            text = (o.get("text") or "").strip()
            if text:
                yield {"id": o.get("id"), "text": text}

    def stable_id(self, d: Dict[str, Any]) -> str:
        """Gera um ID determinístico baseado no texto."""
        basis = d.get("text") or ""
        return str(uuid.uuid5(self.UUID_NS, basis))

    @staticmethod
    def content_sha1(text: str) -> str:
        """Calcula o hash SHA1 de um texto."""
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    @staticmethod
    def dense_dim() -> int:
        """Retorna a dimensão do embedding do modelo denso."""
        return 384

    def collection_exists(self, name: str) -> bool:
        """Verifica se uma coleção existe no Qdrant."""
        try:
            return self.client.collection_exists(name)
        except Exception:
            return False

    def ensure_collection_hybrid(self, name: str, dense_size: int) -> None:
        """Garante a existência de uma coleção híbrida, criando-a se necessário."""
        if self.collection_exists(name):
            print(f"Coleção híbrida já existe: {name}", flush=True)
            return
        try:
            self.client.create_collection(
                collection_name=name,
                vectors_config={
                    self.DENSE_NAME: models.VectorParams(
                        size=dense_size, distance=models.Distance.COSINE
                    )
                },
                sparse_vectors_config={self.SPARSE_NAME: models.SparseVectorParams()},
            )
            print(f"Coleção híbrida criada: {name}", flush=True)
        except UnexpectedResponse as e:
            msg = str(e).lower()
            if "already exists" in msg or "409" in msg:
                print(
                    f"Coleção híbrida já existia (conflito): {name}",
                    flush=True,
                )
            else:
                raise

    def ensure_collection_dense_only(self, name: str, dense_size: int) -> None:
        """Garante a existência de uma coleção densa, criando-a se necessário."""
        if self.collection_exists(name):
            print(f"Coleção densa já existe: {name}", flush=True)
            return
        try:
            self.client.create_collection(
                collection_name=name,
                vectors_config={
                    self.DENSE_NAME: models.VectorParams(
                        size=dense_size, distance=models.Distance.COSINE
                    )
                },
            )
            print(f"Coleção densa criada: {name}", flush=True)
        except UnexpectedResponse as e:
            msg = str(e).lower()
            if "already exists" in msg or "409" in msg:
                print(f"Coleção densa já existia (conflito): {name}", flush=True)
            else:
                raise

    def fetch_existing_hashes(
        self, collection: str, ids: List[str], step: int = 1024
    ) -> Dict[str, str]:
        """Retorna os hashes SHA1 já armazenados para os IDs informados."""
        out: Dict[str, str] = {}
        for i in range(0, len(ids), step):
            pts = self.client.retrieve(
                collection_name=collection,
                ids=ids[i : i + step],
                with_payload=True,
                with_vectors=False,
            )
            for p in pts:
                payload = p.payload or {}
                out[str(p.id)] = payload.get("content_sha1")
        return out

    @staticmethod
    def build_payloads(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cria payloads com texto e hash para upload."""
        return [{"text": r["text"], "content_sha1": r["content_sha1"]} for r in rows]

    def build_documents_hybrid(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cria documentos para indexação híbrida (denso + esparso)."""
        return [
            {
                self.DENSE_NAME: models.Document(text=r["text"], model=self.DENSE_MODEL),
                self.SPARSE_NAME: models.Document(text=r["text"], model=self.SPARSE_MODEL),
            }
            for r in rows
        ]

    def build_documents_dense(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cria documentos para indexação apenas densa."""
        return [
            {self.DENSE_NAME: models.Document(text=r["text"], model=self.DENSE_MODEL)} for r in rows
        ]

    def upsert(
        self,
        collection: str,
        vectors: List[Dict[str, Any]],
        payloads: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        """Insere ou atualiza documentos na coleção."""
        self.client.upload_collection(
            collection_name=collection,
            vectors=vectors,
            payload=payloads,
            ids=ids,
            parallel=os.cpu_count() or 2,
        )

    def count(self, collection: str) -> int:
        """Retorna a contagem exata de documentos na coleção."""
        return self.client.count(collection, exact=True).count
