---
title: PDF Grounded Chat
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8501
pinned: false
---

# PDF-Constrained Conversational Agent

A small Retrieval-Augmented Generation (RAG) chatbot that answers **only** from a user-provided PDF. Out-of-scope questions are refused. Built as a Streamlit UI on top of a thin Python backend (FAISS + sentence-transformers + OpenAI/Gemini).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # then fill in your API key
```

Edit `.env` and set either `OPENAI_API_KEY` (default) or switch `LLM_PROVIDER=gemini` and set `GEMINI_API_KEY`.

### Generate the sample PDF (first run only)

```bash
python samples/generate_sample.py
```

This produces `samples/sample.pdf`, a fictional 4-page Lumora Labs employee handbook used for the evaluation queries below.

## Run

From the project root:

```bash
streamlit run frontend/app.py
```

Upload a PDF in the sidebar, then ask questions in the chat panel. Click "Reset" to load a new PDF.

## Architecture

```
+----------------+        +-----------------------------+
|  Streamlit UI  | -----> |        PDFChatAgent         |
|  frontend/     |        |        backend/agent.py     |
+----------------+        +--------------+--------------+
                                         |
              +--------------+-----------+-----------+--------------+
              |              |                       |              |
              v              v                       v              v
     pdf_processor.py   vector_store.py         llm_client.py    config.py
       pypdf extract     FAISS + multilingual    OpenAI / Gemini  .env vars
       chunk + pages     MiniLM embeddings       langdetect
```

Flow: `ingest_pdf` -> per-page extract -> ~500-char chunks (50 overlap) -> embed with `paraphrase-multilingual-MiniLM-L12-v2` -> FAISS `IndexFlatIP` (cosine via L2-normalized vectors). `chat` -> embed query -> top-K retrieval -> if all scores below `SIMILARITY_THRESHOLD` refuse; otherwise build a strict-grounding prompt and call the LLM. The LLM's own refusal phrasing is also detected as a refusal.

## Evaluation

Sample PDF: `samples/sample.pdf` (Lumora Labs Employee Handbook, 4 pages, fictional).

### Valid queries (must answer with citations)

| # | Query | Expected answer | Page |
|---|-------|-----------------|------|
| 1 | Where is Lumora Labs headquartered, and when was it founded? | Bengaluru, India; founded 2017 by Anika Rao and Marcus Belo. | 1 |
| 2 | How many days of paid annual leave, and how many can carry over? | 24 days/year; up to 10 carry over. | 2 |
| 3 | What is the daily meal allowance for business travel within Europe? | 90 USD per day. | 2 |
| 4 | How is Tier 1 customer data required to be stored? | Encrypted at rest using AES-256, company-managed devices only. | 3 |
| 5 | When are formal performance review cycles held, and when are promotions evaluated? | June and December; promotions only in December. | 4 |

### Invalid / out-of-scope queries (must refuse)

| # | Query | Expected |
|---|-------|----------|
| 1 | What is the current stock price of Apple Inc.? | Refusal, no citations. |
| 2 | Write me a Python function for the Fibonacci sequence. | Refusal, no citations. |
| 3 | Who won the 2024 FIFA World Cup? | Refusal, no citations. |

Refusal message (verbatim): *"I can only answer questions grounded in the provided PDF. This question appears to be outside its scope."*

The full evaluation set is also in `samples/test_queries.md`.

## Multi-language bonus

The embedding model `paraphrase-multilingual-MiniLM-L12-v2` supports 50+ languages, so retrieval works across languages. The agent detects the query language with `langdetect` and instructs the LLM to respond in the same language. Example: ask the same questions above in Hindi, Spanish, or French and the answer is returned in that language with the same English-PDF citations.

## Configuration

Set in `.env`:

| Variable | Default | Notes |
|----------|---------|-------|
| `LLM_PROVIDER` | `openai` | `openai` or `gemini` |
| `OPENAI_API_KEY` | — | required if `LLM_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-4o-mini` | any chat-completions model |
| `GEMINI_API_KEY` | — | required if `LLM_PROVIDER=gemini` |
| `GEMINI_MODEL` | `gemini-1.5-flash` | |
| `TOP_K` | `4` | retrieved chunks per query |
| `SIMILARITY_THRESHOLD` | `0.30` | cosine similarity, below = refuse |

## Project layout

```
backend/
  __init__.py        # exposes PDFChatAgent
  agent.py           # PDFChatAgent (the contract surface)
  pdf_processor.py   # pypdf extraction + chunking
  vector_store.py    # FAISS + multilingual embeddings
  llm_client.py      # OpenAI / Gemini wrapper + langdetect
  config.py          # .env-backed constants
frontend/            # Streamlit UI (separate agent owns this)
samples/
  generate_sample.py # one-shot script to build sample.pdf
  sample.pdf         # produced by the script
  test_queries.md    # evaluation queries
CONTRACT.md          # frozen interface between FE and BE
.env.example
requirements.txt
```

## Notes

- First chat call downloads the sentence-transformers model (~120 MB) into the HuggingFace cache; subsequent calls are fast.
- FAISS index is in-memory only — `agent.reset()` (or uploading a new PDF) clears it.
- Refusal is enforced two ways: low retrieval score *and* detection of the LLM's own refusal phrasing.
