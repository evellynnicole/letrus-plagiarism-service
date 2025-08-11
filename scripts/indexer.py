from app.ai.semantic.indexer import Indexer
from app.config.config import Config


def main():
    """Orquestra a criação/validação das coleções e a indexação do corpus."""
    cfg = Config()
    idx = Indexer(cfg)

    print(
        f"""
        QDRANT_URL={cfg.qdrant_url}
        | HYBRID={cfg.qdrant_collection_hybrid}
        | DENSE={cfg.qdrant_collection_dense}
        """
    )

    d_dim = idx.dense_dim()
    idx.ensure_collection_hybrid(cfg.qdrant_collection_hybrid, d_dim)
    idx.ensure_collection_dense_only(cfg.qdrant_collection_dense, d_dim)

    rows = list(idx.iter_jsonl(cfg.data_path))
    if not rows:
        print(f"Nenhum dado encontrado em {cfg.data_path}")
        return

    base_docs = []
    for d in rows:
        _id = idx.stable_id(d)
        _hash = idx.content_sha1(d["text"])
        base_docs.append({"id": _id, "text": d["text"], "content_sha1": _hash})

    ids = [b["id"] for b in base_docs]

    existing_hash_h = idx.fetch_existing_hashes(cfg.qdrant_collection_hybrid, ids)
    to_upsert_h = [b for b in base_docs if existing_hash_h.get(str(b["id"])) != b["content_sha1"]]
    print(f"[hybrid] sem_mudanca={len(base_docs) - len(to_upsert_h)} upsert={len(to_upsert_h)}")
    if to_upsert_h:
        upsert_ids = [r["id"] for r in to_upsert_h]
        payloads = idx.build_payloads(to_upsert_h)
        documents_hybrid = idx.build_documents_hybrid(to_upsert_h)
        idx.upsert(
            cfg.qdrant_collection_hybrid,
            documents_hybrid,
            payloads,
            upsert_ids,
        )
    print(f"[hybrid] total={idx.count(cfg.qdrant_collection_hybrid)}")

    existing_hash_d = idx.fetch_existing_hashes(cfg.qdrant_collection_dense, ids)
    to_upsert_d = [b for b in base_docs if existing_hash_d.get(str(b["id"])) != b["content_sha1"]]
    print(f"[dense] sem_mudanca={len(base_docs) - len(to_upsert_d)} upsert={len(to_upsert_d)}")
    if to_upsert_d:
        upsert_ids = [r["id"] for r in to_upsert_d]
        payloads = idx.build_payloads(to_upsert_d)
        documents_dense = idx.build_documents_dense(to_upsert_d)
        idx.upsert(cfg.qdrant_collection_dense, documents_dense, payloads, upsert_ids)
    print(f"[dense] total={idx.count(cfg.qdrant_collection_dense)}")


if __name__ == "__main__":
    main()
