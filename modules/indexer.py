import hashlib
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

class VectorIndex:
    def __init__(self, cache_dir: str = ".rag_cache"):
        self.client = chromadb.PersistentClient(path=cache_dir)
        self.collection = self.client.get_or_create_collection(name="full_file_index")
        # Fast CPU model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def _hash_content(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def index_files(self, file_paths: list[Path]):
        """Index full files incrementally based on MD5 file hash."""
        for file_path in file_paths:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if not content.strip():
                continue

            file_id = str(file_path.resolve())
            content_hash = self._hash_content(content)

            # Incremental check: Skip file if hash hasn't changed
            existing = self.collection.get(ids=[file_id])
            if existing and existing.get("metadatas") and len(existing["metadatas"]) > 0:
                if existing["metadatas"][0].get("hash") == content_hash:
                    continue

            # Embed first 2,000 characters for high-level semantic search
            embedding = self.embedder.encode(content[:2000]).tolist()

            self.collection.upsert(
                ids=[file_id],
                embeddings=[embedding],
                documents=[content],  # Store FULL file content
                metadatas=[{
                    "file_path": str(file_path),
                    "hash": content_hash
                }]
            )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Returns top_k full files matching the user query."""
        query_embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        output_files = []
        if results and results["documents"] and results["documents"][0]:
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                output_files.append({
                    "file_path": meta["file_path"],
                    "content": doc
                })
        return output_files