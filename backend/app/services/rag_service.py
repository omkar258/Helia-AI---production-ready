"""
RAG Service – FAISS vector store with all-MiniLM-L6-v2 embeddings.
Indexes mental health knowledge base and retrieves relevant context for AI responses.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval-Augmented Generation service using FAISS + sentence-transformers."""

    def __init__(self):
        self.model = None
        self.index = None
        self.documents: List[str] = []
        self.metadata: List[dict] = []
        self._initialized = False

    async def initialize(self):
        """Load the embedding model and build/load the FAISS index."""
        if self._initialized:
            return

        try:
            from sentence_transformers import SentenceTransformer
            import faiss

            logger.info("Loading embedding model: all-MiniLM-L6-v2...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")

            # Load knowledge base
            kb_dir = Path(__file__).parent.parent.parent / "knowledge_base"
            self._load_knowledge_base(kb_dir)

            if self.documents:
                # Check if we have a saved index
                index_path = kb_dir / "faiss_index.bin"
                docs_path = kb_dir / "indexed_docs.json"

                if index_path.exists() and docs_path.exists():
                    logger.info("Loading existing FAISS index...")
                    self.index = faiss.read_index(str(index_path))
                    with open(docs_path, "r") as f:
                        saved = json.load(f)
                        self.documents = saved["documents"]
                        self.metadata = saved["metadata"]
                else:
                    logger.info(f"Building FAISS index from {len(self.documents)} chunks...")
                    self._build_index()
                    # Save for future loads
                    self._save_index(index_path, docs_path)

            self._initialized = True
            logger.info(f"RAG service initialized with {len(self.documents)} document chunks.")

        except ImportError as e:
            logger.warning(f"RAG dependencies not available: {e}. RAG features disabled.")
            self._initialized = True  # Mark as initialized to avoid repeated attempts
        except Exception as e:
            logger.error(f"RAG initialization error: {e}")
            self._initialized = True

    def _load_knowledge_base(self, kb_dir: Path):
        """Load and chunk all knowledge base files."""
        if not kb_dir.exists():
            logger.warning(f"Knowledge base directory not found: {kb_dir}")
            return

        for file_path in kb_dir.glob("*.json"):
            if file_path.name.startswith("faiss_") or file_path.name == "indexed_docs.json":
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    for item in data:
                        self._process_kb_item(item, file_path.stem)
                elif isinstance(data, dict):
                    for key, items in data.items():
                        if isinstance(items, list):
                            for item in items:
                                self._process_kb_item(item, f"{file_path.stem}/{key}")

            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    def _process_kb_item(self, item: dict, source: str):
        """Process a single knowledge base item into chunks."""
        if isinstance(item, str):
            self.documents.append(item)
            self.metadata.append({"source": source})
            return

        if isinstance(item, dict):
            # Combine title + content for embedding
            parts = []
            if "title" in item:
                parts.append(item["title"])
            if "content" in item:
                parts.append(item["content"])
            if "description" in item:
                parts.append(item["description"])
            if "text" in item:
                parts.append(item["text"])
            if "steps" in item and isinstance(item["steps"], list):
                parts.append(" ".join(item["steps"]))

            if parts:
                text = " — ".join(parts)
                # Chunk long texts (500 chars with 100 char overlap)
                if len(text) > 600:
                    chunks = self._chunk_text(text, chunk_size=500, overlap=100)
                    for chunk in chunks:
                        self.documents.append(chunk)
                        self.metadata.append({"source": source, "title": item.get("title", "")})
                else:
                    self.documents.append(text)
                    self.metadata.append({"source": source, "title": item.get("title", "")})

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks

    def _build_index(self):
        """Build FAISS index from documents."""
        import faiss

        embeddings = self.model.encode(self.documents, normalize_embeddings=True, show_progress_bar=True)
        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product ≈ cosine similarity (with normalized vectors)
        self.index.add(embeddings)

    def _save_index(self, index_path: Path, docs_path: Path):
        """Persist FAISS index and document mapping to disk."""
        import faiss

        try:
            faiss.write_index(self.index, str(index_path))
            with open(docs_path, "w", encoding="utf-8") as f:
                json.dump({"documents": self.documents, "metadata": self.metadata}, f)
            logger.info("FAISS index saved to disk.")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")

    async def retrieve(self, query: str, top_k: int = 3) -> Optional[str]:
        """Retrieve relevant context for a query."""
        if not self.index or not self.model or not self.documents:
            return None

        try:
            query_embedding = self.model.encode([query], normalize_embeddings=True)
            query_embedding = np.array(query_embedding).astype("float32")

            distances, indices = self.index.search(query_embedding, top_k)

            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents) and distances[0][i] > 0.3:  # Relevance threshold
                    results.append(self.documents[idx])

            if results:
                return "\n\n".join(results)
            return None

        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return None


# Singleton instance
rag_service = RAGService()
