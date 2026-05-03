from __future__ import annotations

from typing import Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import EMBEDDING_MODEL


class VectorStore:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._index: Optional[faiss.Index] = None
        self._chunks: list[dict] = []
        self._dim: Optional[int] = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def _embed(self, texts: list[str]) -> np.ndarray:
        vecs = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vecs.astype("float32")

    def add(self, chunks: list[dict]) -> int:
        if not chunks:
            return 0
        vecs = self._embed([c["text"] for c in chunks])
        if self._index is None:
            self._dim = vecs.shape[1]
            # IndexFlatIP on L2-normalized vectors == cosine similarity
            self._index = faiss.IndexFlatIP(self._dim)
        self._index.add(vecs)
        self._chunks.extend(chunks)
        return len(chunks)

    def search(self, query: str, k: int) -> list[dict]:
        if self._index is None or not self._chunks:
            return []
        k = min(k, len(self._chunks))
        q = self._embed([query])
        scores, idxs = self._index.search(q, k)
        results: list[dict] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx < 0:
                continue
            ch = self._chunks[idx]
            # Clamp because tiny float drift can push cosine slightly above 1.0
            sim = max(0.0, min(1.0, float(score)))
            results.append({"page": ch["page"], "text": ch["text"], "score": sim})
        return results

    def reset(self) -> None:
        self._index = None
        self._chunks = []
        self._dim = None

    def __len__(self) -> int:
        return len(self._chunks)
