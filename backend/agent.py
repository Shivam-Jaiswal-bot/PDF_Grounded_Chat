from __future__ import annotations

import io
from typing import Optional, Union

from backend.config import REFUSAL_MESSAGE, SIMILARITY_THRESHOLD, TOP_K
from backend.llm_client import LLMClient, detect_language
from backend.pdf_processor import chunk_pages, extract_pages
from backend.vector_store import VectorStore

_LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "it": "Italian",
    "ru": "Russian",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "ur": "Urdu",
}


class PDFChatAgent:
    def __init__(self) -> None:
        self.store = VectorStore()
        self.llm = LLMClient()
        self.history: list[dict] = []
        self.filename: Optional[str] = None
        self.pages_count: int = 0

    def ingest_pdf(
        self, path_or_bytes: Union[str, bytes, io.BytesIO], filename: str
    ) -> dict:
        self.store.reset()
        pages = extract_pages(path_or_bytes)
        chunks = chunk_pages(pages)
        self.store.add(chunks)
        self.filename = filename
        self.pages_count = len(pages)
        return {"pages": len(pages), "chunks": len(chunks), "filename": filename}

    def chat(self, query: str, history: Optional[list[dict]] = None) -> dict:
        lang = detect_language(query)
        lang_name = _LANG_NAMES.get(lang.lower(), lang)

        hits = self.store.search(query, k=TOP_K)

        if not hits or all(h["score"] < SIMILARITY_THRESHOLD for h in hits):
            return {
                "answer": REFUSAL_MESSAGE,
                "citations": [],
                "refused": True,
                "language": lang,
            }

        used = [h for h in hits if h["score"] >= SIMILARITY_THRESHOLD] or hits[:1]

        context_block = "\n\n".join(
            f"[Page {h['page']}] {h['text']}" for h in used
        )

        system_prompt = (
            "You are a strict document-grounded assistant. "
            "Answer ONLY using the supplied context. "
            "If the answer is not in the context, reply with this refusal sentence verbatim and nothing else: "
            f"\"{REFUSAL_MESSAGE}\" "
            "Always cite page numbers inline like (p. N) for any fact you state. "
            f"Respond in the same language as the user's question ({lang_name})."
        )

        history_block = ""
        hist = history if history is not None else self.history
        if hist:
            recent = hist[-6:]
            lines = []
            for m in recent:
                role = m.get("role", "user")
                content = m.get("content", "")
                lines.append(f"{role.upper()}: {content}")
            history_block = "Conversation so far:\n" + "\n".join(lines) + "\n\n"

        user_prompt = (
            f"{history_block}"
            f"Context from the PDF:\n{context_block}\n\n"
            f"Question: {query}\n\n"
            "Answer using only the context above and cite pages like (p. N)."
        )

        try:
            answer = self.llm.generate(system_prompt, user_prompt)
        except Exception as e:
            return {
                "answer": f"LLM error: {e}",
                "citations": [],
                "refused": True,
                "language": lang,
            }

        refused = self._looks_like_refusal(answer)

        if refused:
            self.history.append({"role": "user", "content": query})
            self.history.append({"role": "assistant", "content": REFUSAL_MESSAGE})
            return {
                "answer": REFUSAL_MESSAGE,
                "citations": [],
                "refused": True,
                "language": lang,
            }

        citations = [
            {
                "page": h["page"],
                "snippet": (h["text"][:200]).strip(),
                "score": round(h["score"], 4),
            }
            for h in used
        ]

        self.history.append({"role": "user", "content": query})
        self.history.append({"role": "assistant", "content": answer})

        return {
            "answer": answer,
            "citations": citations,
            "refused": False,
            "language": lang,
        }

    def reset(self) -> None:
        self.store.reset()
        self.history = []
        self.filename = None
        self.pages_count = 0

    @staticmethod
    def _looks_like_refusal(text: str) -> bool:
        if not text:
            return True
        normalized = text.strip().lower()
        # Catch the verbatim refusal plus minor LLM paraphrases
        markers = [
            "i can only answer questions grounded in the provided pdf",
            "outside its scope",
            "outside the scope of the provided pdf",
            "not in the context",
            "not contained in the context",
            "the context does not",
            "context does not contain",
        ]
        return any(m in normalized for m in markers)
