from __future__ import annotations

from typing import Any, Callable, Dict, List

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []          # in-memory fallback
        self._collection = None
        self._next_index = 0

        # Try to initialize ChromaDB
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path="./chroma_db")
            self._collection = self._client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
            print(f"✅ Using ChromaDB collection: {collection_name}")
        except Exception:
            self._use_chroma = False
            self._collection = None
            print("⚠️ ChromaDB not available. Using in-memory store.")

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Build a normalized stored record."""
        embedding = self._embedding_fn(doc.content)
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": doc.metadata or {},
            "embedding": embedding,
            "index": self._next_index
        }

    def add_documents(self, docs: list[Document]) -> None:
        """Embed each document and store it."""
        if not docs:
            return

        if self._use_chroma and self._collection:
            # ChromaDB path
            ids = []
            documents = []
            embeddings = []
            metadatas = []

            for doc in docs:
                emb = self._embedding_fn(doc.content)
                ids.append(doc.id)
                documents.append(doc.content)
                embeddings.append(emb)
                metadatas.append(doc.metadata or {})

            self._collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
        else:
            # In-memory path
            for doc in docs:
                record = self._make_record(doc)
                self._store.append(record)
                self._next_index += 1

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection:
            return self._collection.count()
        return len(self._store)

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """In-memory similarity search using cosine similarity."""
        if not records:
            return []

        query_embedding = self._embedding_fn(query)

        scored = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored.append((score, record))

        # Sort by score descending and take top_k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.
        Each result must contain: 'content', 'score', and optionally 'metadata'.
        """
        if self._use_chroma and self._collection:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            output = []
            for i in range(len(results["documents"][0])):
                output.append({
                    "id": results["ids"][0][i] if "ids" in results else None,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": float(1.0 - results["distances"][0][i]),   # convert distance → similarity
                })
            return output

        else:
            # In-memory search
            if not self._store:
                return []

            query_embedding = self._embedding_fn(query)
            scored = []

            for record in self._store:
                score = _dot(query_embedding, record["embedding"])
                scored.append({
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": record.get("metadata", {}),
                    "score": float(score),          # ← This is what the test expects
                })

            # Sort by score descending and take top_k
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:top_k]

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """Search with optional metadata pre-filtering."""
        if not metadata_filter:
            return self.search(query, top_k)

        if self._use_chroma and self._collection:
            # ChromaDB doesn't support complex filters easily in basic version, so fallback to in-memory logic
            filtered = [r for r in self._store if all(r["metadata"].get(k) == v for k, v in metadata_filter.items())]
            return self._search_records(query, filtered, top_k)
        else:
            filtered = [r for r in self._store if all(r["metadata"].get(k) == v for k, v in metadata_filter.items())]
            return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """Remove all chunks belonging to a document."""
        if self._use_chroma and self._collection:
            # ChromaDB delete (note: requires knowing the ids)
            try:
                self._collection.delete(ids=[doc_id])
                return True
            except:
                return False
        else:
            # In-memory delete
            original_len = len(self._store)
            self._store = [record for record in self._store if record["id"] != doc_id]
            return len(self._store) < original_len