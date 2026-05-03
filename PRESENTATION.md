# PDF-Constrained Conversational Agent
**STAIR Digital — Task 3 — Shivam Jaiswal**

A presentation outline. One slide per `##` heading; the bullets are speaker points.

---

## Slide 1 — Title

- **PDF-Constrained Conversational Agent**
- Task 3 · STAIR Digital · Semester 4, Term 2
- Shivam Jaiswal
- Live demo: `huggingface.co/spaces/shivam271206/PDF_Grounded_Chat`
- Code: `github.com/Shivam-Jaiswal-bot/PDF_Grounded_Chat`

---

## Slide 2 — The Problem

- Build a chatbot that answers questions about a PDF.
- **Three hard constraints:**
  1. Answer **only** from the PDF — no outside knowledge.
  2. **Refuse** out-of-scope questions explicitly.
  3. Every answer must cite the **page number** it came from.
- Bonus: handle questions in multiple languages.
- The hard part isn't generating answers — it's preventing the LLM from making things up.

---

## Slide 3 — Approach: RAG with Strict Grounding

- **Retrieval-Augmented Generation** — feed the LLM only relevant PDF chunks.
- Why not fine-tune? Slow, expensive, still hallucinates.
- Why not stuff the whole PDF in a prompt? Doesn't scale, dilutes attention, expensive per query.
- RAG gives us **traceable sources** (essential for citations) and **scope control** (essential for refusal).
- Trade-off: retrieval quality becomes the bottleneck, not the LLM.

---

## Slide 4 — Architecture

```
                ┌──────────────────────────┐
                │    Streamlit Frontend    │
                │  (upload + chat + UI)    │
                └────────────┬─────────────┘
                             │
                ┌────────────▼─────────────┐
                │      PDFChatAgent        │
                │  (orchestrator)          │
                └─┬──────────┬─────────┬───┘
                  │          │         │
       ┌──────────▼──┐  ┌────▼────┐  ┌─▼──────────┐
       │ PDFProcessor│  │  FAISS  │  │ LLM Client │
       │ (pypdf +    │  │ Vector  │  │ (Groq /    │
       │  chunker)   │  │ Store   │  │  OpenAI /  │
       └─────────────┘  └─────────┘  │  Gemini)   │
                                     └────────────┘
```

- 5 backend modules, ~80 lines each. One responsibility per file.
- Frontend talks to backend through a single class — `PDFChatAgent`.

---

## Slide 5 — Strict Grounding: Two Layers

**Layer 1 — Retrieval-side (cheap, runs first):**
- Embed the query, compute cosine similarity with all chunks.
- If **all** top-K scores fall below a 0.30 threshold → refuse immediately, **don't even call the LLM**.
- Saves API cost on obviously off-topic questions.

**Layer 2 — Prompt-side (catches subtler hallucinations):**
- System prompt says verbatim: *"Answer ONLY using the supplied context. If the answer is not in the context, reply with the refusal sentence verbatim."*
- Temperature 0.1 (deterministic, fact-leaning).
- Pattern-match the LLM output for refusal phrases — catches when the LLM tries to be helpful and bend the rules.

---

## Slide 6 — Citations

- Every chunk carries `{page: int, text: str}` metadata through the entire pipeline.
- The LLM is instructed to inline `(p. N)` markers in its answer.
- The UI surfaces an expandable **Sources** panel below every answer:
  - Page number
  - 200-character snippet from the chunk that was retrieved
  - Relevance score (cosine similarity, 0–1)
- Anyone can verify the answer by opening the PDF to that page.

---

## Slide 7 — Refusal Taxonomy

| Trigger | When | LLM call? |
|---|---|---|
| Low retrieval score | All top-K scores < 0.30 | No (saves cost) |
| LLM emits refusal | Output matches refusal patterns | Yes (already paid) |
| LLM error / quota | Exception during call | No (graceful degrade) |

- All three paths return the **same** refusal text and `refused: True`.
- Frontend renders any `refused=True` response as a yellow warning, no citations.
- Robust to: questions about the PDF's domain that aren't actually in it (e.g. wrong page), random topic shifts, prompt-injection attempts.

---

## Slide 8 — Multi-Language Support (Bonus)

- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` — trained on 50+ languages, embeds queries and chunks into the same space regardless of language.
- **Detection:** `langdetect` identifies the query language.
- **Generation:** LLM is instructed to respond in the **same language** as the query.
- A user can ask *"छुट्टियाँ कितनी हैं?"* about an English PDF and get an answer in Hindi citing the right page.
- Grounding holds across languages because retrieval happens in the shared embedding space.

---

## Slide 9 — Demo: Valid Queries (Sample PDF: Lumora Labs Handbook)

| # | Query | Expected Behavior |
|---|---|---|
| 1 | Where is Lumora Labs HQ and when was it founded? | Bengaluru, 2017 — *(p. 1)* |
| 2 | How many days of paid annual leave? | 24 days; 10 carry over — *(p. 2)* |
| 3 | Daily meal allowance for European travel? | $90/day — *(p. 2)* |
| 4 | How is Tier 1 customer data stored? | AES-256 encrypted at rest — *(p. 3)* |
| 5 | When are performance reviews held? | June and December cycles — *(p. 4)* |

→ Each answer comes back with the correct page citation and a Sources panel showing the matched chunk.

---

## Slide 10 — Demo: Invalid Queries

| # | Query | Expected Behavior |
|---|---|---|
| 1 | What is Apple's current stock price? | Refuse — outside scope |
| 2 | Write a Python Fibonacci function | Refuse — outside scope |
| 3 | Who won the 2024 FIFA World Cup? | Refuse — outside scope |

→ All three trigger the same refusal text. No citations. Yellow "Out of scope" banner in the UI.

The bot remains useful even when refusing — the refusal is informative, not just "I don't know."

---

## Slide 11 — Tech Stack & Deployment

- **Backend:** Python, `pypdf`, `sentence-transformers`, `faiss-cpu`, `langdetect`, `python-dotenv`
- **LLM:** Groq (Llama 3.3 70B) — sub-second responses, free tier; pluggable to OpenAI / Gemini via `LLM_PROVIDER` env var
- **Frontend:** Streamlit
- **Hosting:** Hugging Face Spaces (Docker)
- **Repo:** GitHub
- **Why Groq?** Inference speed matters for a chat UX; Llama 3.3 70B is competitive with GPT-4o on factual QA at a fraction of the latency.

---

## Slide 12 — Reflections / Closing

- **What was hard:** tuning the similarity threshold. Too low → hallucinations leak through; too high → valid questions get refused. Settled on 0.30 with multilingual embeddings.
- **What surprised me:** the LLM occasionally *tries* to be helpful and answer outside the context, even with a strict system prompt. The refusal-phrase detection layer is doing real work.
- **What I'd add next:**
  - OCR fallback for scanned PDFs (currently text-only).
  - Per-citation confidence so the UI can flag weak grounding.
  - Streaming responses for longer answers.
- **Thanks — questions?**

---

## Speaker tips

- Keep the demo to 90 seconds: 1 valid query that works beautifully, 1 invalid query that gets refused, 1 multilingual query.
- When asked "how do you prevent hallucinations?" — the answer is the **two-layer refusal**, not just "good prompting."
- When asked "what's the limitation?" — be honest: scanned PDFs won't work without OCR; very long single-paragraph chunks can dilute retrieval.
