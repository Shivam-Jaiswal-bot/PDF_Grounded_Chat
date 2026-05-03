import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from backend.agent import PDFChatAgent

st.set_page_config(page_title="PDF Chat", page_icon=":books:", layout="wide")

if "agent" not in st.session_state:
    st.session_state.agent = PDFChatAgent()
if "history" not in st.session_state:
    st.session_state.history = []
if "filename" not in st.session_state:
    st.session_state.filename = None
if "ingest_info" not in st.session_state:
    st.session_state.ingest_info = None

agent = st.session_state.agent

LANG_HINTS = {
    "Auto-detect": None,
    "English": "[Respond in English]",
    "Hindi": "[Respond in Hindi]",
    "Spanish": "[Respond in Spanish]",
}

with st.sidebar:
    st.header("PDF Chat")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded is not None and uploaded.name != st.session_state.filename:
        with st.spinner(f"Ingesting {uploaded.name}..."):
            try:
                info = agent.ingest_pdf(uploaded.read(), uploaded.name)
                st.session_state.filename = uploaded.name
                st.session_state.ingest_info = info
                st.session_state.history = []
            except Exception as e:
                st.error(f"Failed to ingest PDF: {e}")

    if st.session_state.filename:
        st.success(f"Loaded: **{st.session_state.filename}**")
        if st.session_state.ingest_info:
            info = st.session_state.ingest_info
            st.info(f"Pages: {info.get('pages', '?')} • Chunks: {info.get('chunks', '?')}")

    language = st.selectbox(
        "Response language",
        list(LANG_HINTS.keys()),
        index=0,
        help="Auto-detects from your query by default.",
    )

    if st.button("Reset conversation", use_container_width=True):
        agent.reset()
        st.session_state.history = []
        st.session_state.filename = None
        st.session_state.ingest_info = None
        st.rerun()

    st.markdown("---")
    st.markdown(
        "**About**\n\n"
        "This assistant answers strictly from the uploaded PDF. "
        "Out-of-scope questions are refused rather than guessed."
    )

st.title("Chat with your PDF")

if not st.session_state.filename:
    st.info("Upload a PDF in the sidebar to start chatting.")

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("refused"):
            st.warning(f"**Out of scope** — {msg['content']}")
        else:
            st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("citations"):
            with st.expander("Sources"):
                for c in msg["citations"]:
                    snippet = (c.get("snippet") or "").strip().replace("\n", " ")
                    st.markdown(
                        f"**Page {c.get('page', '?')}** — _\"{snippet}...\"_  "
                        f"(relevance: {c.get('score', 0.0):.2f})"
                    )

prompt = st.chat_input(
    "Ask about the PDF...",
    disabled=st.session_state.filename is None,
)

if prompt:
    hint = LANG_HINTS.get(language)
    sent_query = f"{hint} {prompt}" if hint else prompt

    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                prior = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.history[:-1]
                ]
                response = agent.chat(sent_query, prior)

            answer = response.get("answer", "")
            refused = bool(response.get("refused"))
            citations = response.get("citations", []) or []

            if refused:
                st.warning(f"**Out of scope** — {answer}")
            else:
                st.markdown(answer)

            if citations:
                with st.expander("Sources"):
                    for c in citations:
                        snippet = (c.get("snippet") or "").strip().replace("\n", " ")
                        st.markdown(
                            f"**Page {c.get('page', '?')}** — _\"{snippet}...\"_  "
                            f"(relevance: {c.get('score', 0.0):.2f})"
                        )

            st.session_state.history.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "refused": refused,
                    "citations": citations,
                }
            )
        except Exception as e:
            st.error(f"Error: {e}")
            if st.session_state.history and st.session_state.history[-1]["role"] == "user":
                st.session_state.history.pop()
