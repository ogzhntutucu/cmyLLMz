"""
app.py
------
cmyLLMz — Yahşi Batı Mizah Analiz Sistemi
Streamlit ana uygulaması.

Çalıştırma: streamlit run src/app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

st.set_page_config(
    page_title="cmyLLMz — Yahşi Batı",
    page_icon="🤠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ─────────────────────────────────────────────────────────────────────

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Rye&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

/* Base */
.stApp {
    background-color: #0f0c07;
    font-family: 'Lora', Georgia, serif;
}

.main .block-container {
    max-width: 780px;
    padding-top: 0.5rem;
    padding-bottom: 5rem;
}

/* Header */
.yb-header {
    text-align: center;
    padding: 1.75rem 0 1.25rem;
    border-bottom: 1px solid #3a2810;
    margin-bottom: 1.5rem;
}

.yb-title {
    font-family: 'Rye', serif;
    font-size: 2.8rem;
    color: #c9953a;
    letter-spacing: 0.06em;
    margin: 0;
    line-height: 1.1;
    text-shadow: 0 0 60px rgba(201, 149, 58, 0.25);
}

.yb-subtitle {
    font-size: 0.9rem;
    color: #7a5c38;
    font-style: italic;
    margin-top: 0.4rem;
    letter-spacing: 0.04em;
}

.yb-divider {
    width: 60px;
    height: 1px;
    background: linear-gradient(to right, transparent, #c9953a, transparent);
    margin: 0.6rem auto 0;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(20, 15, 8, 0.9) !important;
    border: 1px solid #2e2010 !important;
    border-radius: 3px !important;
    padding: 0.9rem 1.1rem !important;
    margin-bottom: 0.6rem !important;
}

[data-testid="stChatMessage"] p {
    color: #e8dcc0 !important;
    font-family: 'Lora', Georgia, serif !important;
    line-height: 1.7 !important;
}

/* Chunk cards */
.chunk-card {
    background: #100d07;
    border: 1px solid #2e2010;
    border-left: 3px solid #a06828;
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0;
    border-radius: 2px;
}

.chunk-id {
    font-family: 'Rye', serif;
    color: #c9953a;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    display: inline-block;
}

.chunk-score {
    color: #5a4028;
    font-size: 0.72rem;
    margin-left: 0.6rem;
    font-style: italic;
}

.chunk-meta-row {
    color: #7a5c38;
    font-size: 0.78rem;
    margin-top: 0.2rem;
    font-style: italic;
}

.chunk-summary {
    color: #a89070;
    font-size: 0.82rem;
    margin-top: 0.35rem;
    line-height: 1.5;
    border-top: 1px solid #2a1e0d;
    padding-top: 0.3rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0a0805 !important;
    border-right: 1px solid #2a1e0d !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #9a7850 !important;
    font-family: 'Lora', Georgia, serif !important;
    font-size: 0.85rem !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #0d0a06 !important;
    border: 1px solid #2a1e0d !important;
    border-radius: 2px !important;
    margin-top: 0.4rem !important;
}

[data-testid="stExpander"] summary {
    color: #7a5c38 !important;
    font-size: 0.82rem !important;
    font-style: italic !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    border-color: #3a2810 !important;
    background: #130f08 !important;
}

[data-testid="stChatInput"] textarea {
    color: #e8dcc0 !important;
    font-family: 'Lora', Georgia, serif !important;
    background: #130f08 !important;
}

/* Buttons */
.stButton button {
    background: #1c1409 !important;
    border: 1px solid #3a2810 !important;
    color: #9a7850 !important;
    font-family: 'Lora', Georgia, serif !important;
    font-size: 0.82rem !important;
    border-radius: 2px !important;
    transition: border-color 0.2s, color 0.2s !important;
}

.stButton button:hover {
    border-color: #a06828 !important;
    color: #c9953a !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0f0c07; }
::-webkit-scrollbar-thumb { background: #3a2810; border-radius: 2px; }
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def render_sources(chunks: list[dict]) -> None:
    if not chunks:
        return
    with st.expander(f"📜  {len(chunks)} kaynak sahne", expanded=False):
        for c in chunks:
            score_str = f"{c['score']:.2f}" if c["score"] is not None else "ilişkili"
            chars = ", ".join(c["characters"].values()) if c["characters"] else "—"
            techniques = ", ".join(c["techniques"]) if c["techniques"] else "—"
            st.markdown(
                f"""<div class="chunk-card">
  <span class="chunk-id">{c['id']}</span>
  <span class="chunk-score">eşleşme: {score_str}</span>
  <div class="chunk-meta-row">🕐 {c['start']} → {c['end']} &nbsp;·&nbsp; 📍 {c['location'] or '—'}</div>
  <div class="chunk-meta-row">👥 {chars}</div>
  <div class="chunk-meta-row">🎭 {techniques}</div>
  {f'<div class="chunk-summary">{c["summary"]}</div>' if c.get("summary") else ""}
</div>""",
                unsafe_allow_html=True,
            )


# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<div style='font-family:Rye,serif;color:#c9953a;font-size:1.1rem;"
        "letter-spacing:0.06em;margin-bottom:0.5rem;'>cmyLLMz</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color:#5a4028;font-size:0.78rem;font-style:italic;"
        "margin-bottom:1rem;'>Yahşi Batı · Mizah Analiz Asistanı</div>",
        unsafe_allow_html=True,
    )

    if st.button("↺  Yeni Sohbet", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "<div style='border-top:1px solid #2a1e0d;margin:0.8rem 0;'></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color:#5a4028;font-size:0.78rem;margin-bottom:0.5rem;'>Örnek sorular:</div>",
        unsafe_allow_html=True,
    )
    examples = [
        "47. dakikada ne oluyor?",
        "Hangi dakikada kola yapıyorlar?",
        "Betty nasıl bir karakter?",
        "Şerif Lloyd nasıl biri?",
        "Filmde ne tür mizah teknikleri kullanılmış?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex__{ex}"):
            st.session_state.pending_question = ex
            st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """<div class="yb-header">
  <div class="yb-title">cmyLLMz</div>
  <div class="yb-subtitle">Yahşi Batı · Mizah Analiz Asistanı</div>
  <div class="yb-divider"></div>
</div>""",
    unsafe_allow_html=True,
)


# ── Chat history render ───────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("chunks"):
            render_sources(msg["chunks"])


# ── Question handler ──────────────────────────────────────────────────────────

def handle_question(query: str) -> None:
    from rag.retriever import ask_with_history

    # Kullanıcı mesajını göster ve kaydet
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Geçmiş: mevcut soru hariç önceki tüm turlar
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    # Cevap üret (streaming)
    with st.chat_message("assistant"):
        response_gen, chunks = ask_with_history(query, history, stream=True)
        response_text = st.write_stream(response_gen)
        render_sources(chunks)

    # Kaydet
    st.session_state.messages.append(
        {"role": "assistant", "content": response_text, "chunks": chunks}
    )


# Sidebar'dan gelen örnek soru
if "pending_question" in st.session_state:
    pending = st.session_state.pop("pending_question")
    handle_question(pending)

# Manuel girdi
if prompt := st.chat_input("Yahşi Batı hakkında bir soru sor…"):
    handle_question(prompt)
