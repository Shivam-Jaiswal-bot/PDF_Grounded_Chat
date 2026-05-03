from __future__ import annotations

import io
import re
from typing import Iterable, Union

from pypdf import PdfReader

from backend.config import CHUNK_OVERLAP, CHUNK_SIZE


def extract_pages(source: Union[str, bytes, io.BytesIO]) -> list[dict]:
    if isinstance(source, bytes):
        source = io.BytesIO(source)
    reader = PdfReader(source)
    pages: list[dict] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append({"page": i, "text": _normalize(text)})
    return pages


def _normalize(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_pages(
    pages: Iterable[dict],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    chunks: list[dict] = []
    for p in pages:
        text = p["text"]
        if not text:
            continue
        for piece in _sliding_window(text, chunk_size, overlap):
            piece = piece.strip()
            if piece:
                chunks.append({"page": p["page"], "text": piece})
    return chunks


def _sliding_window(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0:
        return [text]
    step = max(1, size - overlap)
    return [text[i : i + size] for i in range(0, len(text), step) if text[i : i + size]]
