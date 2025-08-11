class Config:
    def __init__(self):
        self.qdrant_url = "http://qdrant=:6333"
        self.model_dense_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model_sparse_name = "Qdrant/bm25"
        self.dense_name = "dense"
        self.sparse_name = "sparse"
        self.qdrant_collection_hybrid = "docs_hybrid"
        self.qdrant_collection_dense = "docs_dense"
        self.data_path = "data/raw/wikipedia-PT-300.jsonl"
