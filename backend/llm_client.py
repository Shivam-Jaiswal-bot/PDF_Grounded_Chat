from __future__ import annotations

from backend.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider = (provider or LLM_PROVIDER).lower()
        self._client = None
        self._init_provider()

    def _init_provider(self) -> None:
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
            from openai import OpenAI

            self._client = OpenAI(api_key=OPENAI_API_KEY)
            self._model = OPENAI_MODEL
        elif self.provider == "groq":
            if not GROQ_API_KEY:
                raise RuntimeError("GROQ_API_KEY is not set in the environment.")
            from openai import OpenAI

            self._client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
            self._model = GROQ_MODEL
        elif self.provider == "gemini":
            if not GEMINI_API_KEY:
                raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
            import google.generativeai as genai

            genai.configure(api_key=GEMINI_API_KEY)
            self._client = genai
            self._model = GEMINI_MODEL
        else:
            raise ValueError(
                f"Unknown LLM_PROVIDER '{self.provider}' (expected 'groq', 'openai', or 'gemini')."
            )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider in ("openai", "groq"):
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            return (resp.choices[0].message.content or "").strip()

        # Gemini has no native system role; prepend it as an instruction
        model = self._client.GenerativeModel(
            model_name=self._model, system_instruction=system_prompt
        )
        resp = model.generate_content(user_prompt)
        try:
            return (resp.text or "").strip()
        except Exception:
            return ""


def detect_language(text: str) -> str:
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        if not text or not text.strip():
            return "en"
        return detect(text)
    except Exception:
        return "en"
