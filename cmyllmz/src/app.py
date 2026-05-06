"""
app.py
------
cmyLLMz — Yahşi Batı Mizah Analiz Sistemi
Streamlit ana uygulaması.

Çalıştırma: streamlit run src/app.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
CONV_DIR = PROJECT_ROOT / "data" / "conversations"
CONV_DIR.mkdir(parents=True, exist_ok=True)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="cmyLLMz — Yahşi Batı",
    page_icon="🤠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
# Material Icons: sidebar toggle ikonunu düzeltir
# CSS değişkenleri: Streamlit'in açık/koyu temasıyla uyumlu çalışır
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Rye&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Sharp');

/* Açık mod değişkenleri (config.toml'daki light theme ile eş) */
:root {
    --yb-accent: #a06828;
    --yb-gold: #7a4515;
    --yb-card-bg: rgba(236, 226, 208, 0.7);
    --yb-card-border: #c8a878;
    --yb-muted: #6a4828;
    --yb-divider: rgba(160, 104, 40, 0.35);
    --yb-title-shadow: rgba(138, 85, 32, 0.18);
    --yb-conv-active: rgba(160, 104, 40, 0.14);
}

/* Koyu mod değişkenleri (OS/tarayıcı koyu mod tercihine göre) */
@media (prefers-color-scheme: dark) {
    :root {
        --yb-accent: #c9953a;
        --yb-gold: #d4a843;
        --yb-card-bg: rgba(20, 15, 8, 0.9);
        --yb-card-border: #3a2810;
        --yb-muted: #7a5c38;
        --yb-divider: rgba(201, 149, 58, 0.22);
        --yb-title-shadow: rgba(201, 149, 58, 0.22);
        --yb-conv-active: rgba(201, 149, 58, 0.11);
    }
}

/* ── Global ── */
.stApp {
    font-family: 'Lora', Georgia, serif;
}

.main .block-container {
    max-width: 780px;
    padding-top: 0.5rem;
    padding-bottom: 5rem;
}

/* ── Header ── */
.yb-header {
    text-align: center;
    padding: 1.75rem 0 1.25rem;
    border-bottom: 1px solid var(--yb-divider);
    margin-bottom: 1.5rem;
}

.yb-title {
    font-family: 'Rye', serif;
    font-size: 2.8rem;
    color: var(--yb-accent);
    letter-spacing: 0.06em;
    margin: 0;
    line-height: 1.1;
    text-shadow: 0 2px 40px var(--yb-title-shadow);
}

.yb-subtitle {
    font-size: 0.9rem;
    color: var(--yb-muted);
    font-style: italic;
    margin-top: 0.4rem;
    letter-spacing: 0.04em;
}

.yb-divider {
    width: 60px;
    height: 1px;
    background: linear-gradient(to right, transparent, var(--yb-accent), transparent);
    margin: 0.6rem auto 0;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border: 1px solid var(--yb-divider) !important;
    border-radius: 3px !important;
    padding: 0.9rem 1.1rem !important;
    margin-bottom: 0.6rem !important;
}

[data-testid="stChatMessage"] p {
    font-family: 'Lora', Georgia, serif !important;
    line-height: 1.7 !important;
}

/* ── Chunk kartları ── */
.chunk-card {
    background: var(--yb-card-bg);
    border: 1px solid var(--yb-card-border);
    border-left: 3px solid var(--yb-accent);
    padding: 0.6rem 0.9rem;
    margin: 0.4rem 0;
    border-radius: 2px;
}

.chunk-id {
    font-family: 'Rye', serif;
    color: var(--yb-accent);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    display: inline-block;
}

.chunk-score {
    color: var(--yb-muted);
    font-size: 0.72rem;
    margin-left: 0.6rem;
    font-style: italic;
}

.chunk-meta-row {
    color: var(--yb-muted);
    font-size: 0.78rem;
    margin-top: 0.2rem;
    font-style: italic;
}

.chunk-summary {
    font-size: 0.82rem;
    color: var(--yb-muted);
    margin-top: 0.35rem;
    line-height: 1.5;
    border-top: 1px solid var(--yb-divider);
    padding-top: 0.3rem;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border-color: var(--yb-card-border) !important;
    border-radius: 2px !important;
    margin-top: 0.4rem !important;
}

/* ── Butonlar ── */
.stButton button {
    font-family: 'Lora', Georgia, serif !important;
    font-size: 0.82rem !important;
    border-radius: 2px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { border-radius: 2px; }
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# ── Sohbet yönetimi ───────────────────────────────────────────────────────────

def new_conv_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_conv(conv_id: str, messages: list[dict]) -> None:
    if not messages:
        return
    title = next(
        (m["content"][:50] for m in messages if m["role"] == "user"),
        "Yeni Sohbet",
    )
    data = {
        "id": conv_id,
        "title": title,
        "messages": [
            {"role": m["role"], "content": m["content"], "chunks": m.get("chunks")}
            for m in messages
        ],
    }
    (CONV_DIR / f"{conv_id}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2)
    )


def list_convs() -> list[dict]:
    convs = []
    for f in sorted(CONV_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            convs.append({"id": data["id"], "title": data["title"]})
        except Exception:
            pass
    return convs


def load_conv(conv_id: str) -> list[dict]:
    path = CONV_DIR / f"{conv_id}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text()).get("messages", [])


# ── Session state ─────────────────────────────────────────────────────────────
if "conv_id" not in st.session_state:
    st.session_state.conv_id = new_conv_id()
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Kaynak sahneler ───────────────────────────────────────────────────────────

def render_sources(chunks: list[dict]) -> None:
    if not chunks:
        return
    with st.expander(f"📜  {len(chunks)} kaynak sahne", expanded=False):
        for c in chunks:
            score_str = f"{c['score']:.2f}" if c.get("score") is not None else "ilişkili"
            chars = ", ".join(c["characters"].values()) if c.get("characters") else "—"
            techniques = ", ".join(c["techniques"]) if c.get("techniques") else "—"
            st.markdown(
                f"""<div class="chunk-card">
  <span class="chunk-id">{c['id']}</span>
  <span class="chunk-score">eşleşme: {score_str}</span>
  <div class="chunk-meta-row">🕐 {c.get('start', '—')} → {c.get('end', '—')} &nbsp;·&nbsp; 📍 {c.get('location') or '—'}</div>
  <div class="chunk-meta-row">👥 {chars}</div>
  <div class="chunk-meta-row">🎭 {techniques}</div>
  {f'<div class="chunk-summary">{c["summary"]}</div>' if c.get("summary") else ""}
</div>""",
                unsafe_allow_html=True,
            )


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        "<div style='font-family:Rye,serif;color:var(--yb-accent);"
        "font-size:1.05rem;letter-spacing:0.06em;margin-bottom:0.5rem;'>cmyLLMz</div>",
        unsafe_allow_html=True,
    )

    if st.button("↺  Yeni Sohbet", use_container_width=True):
        if st.session_state.messages:
            save_conv(st.session_state.conv_id, st.session_state.messages)
        st.session_state.conv_id = new_conv_id()
        st.session_state.messages = []
        st.rerun()

    # Geçmiş sohbetler
    convs = list_convs()
    active_id = st.session_state.conv_id

    if convs:
        st.markdown(
            "<div style='font-size:0.7rem;color:var(--yb-muted);margin:0.9rem 0 0.3rem;"
            "letter-spacing:0.06em;text-transform:uppercase;'>Geçmiş Sohbetler</div>",
            unsafe_allow_html=True,
        )
        for conv in convs:
            is_active = conv["id"] == active_id
            label = ("▸ " if is_active else "") + conv["title"]
            if st.button(label, key=f"conv__{conv['id']}", use_container_width=True):
                if not is_active:
                    if st.session_state.messages:
                        save_conv(st.session_state.conv_id, st.session_state.messages)
                    st.session_state.conv_id = conv["id"]
                    st.session_state.messages = load_conv(conv["id"])
                    st.rerun()

    # Örnek sorular
    st.markdown(
        "<div style='border-top:1px solid var(--yb-divider);margin:0.9rem 0 0.3rem;'></div>"
        "<div style='font-size:0.7rem;color:var(--yb-muted);margin-bottom:0.3rem;"
        "letter-spacing:0.06em;text-transform:uppercase;'>Örnek Sorular</div>",
        unsafe_allow_html=True,
    )
    for ex in [
        "47. dakikada ne oluyor?",
        "Hangi dakikada kola yapıyorlar?",
        "Betty nasıl bir karakter?",
        "Şerif Lloyd nasıl biri?",
        "Filmde ne tür mizah teknikleri kullanılmış?",
    ]:
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


# ── Sohbet geçmişi göster ─────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("chunks"):
            render_sources(msg["chunks"])


# ── Soru işleyici ─────────────────────────────────────────────────────────────

def handle_question(query: str) -> None:
    from rag.retriever import ask_with_history

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    with st.chat_message("assistant"):
        response_gen, chunks = ask_with_history(query, history, stream=True)
        response_text = st.write_stream(response_gen)
        render_sources(chunks)

    st.session_state.messages.append(
        {"role": "assistant", "content": response_text, "chunks": chunks}
    )
    save_conv(st.session_state.conv_id, st.session_state.messages)


if "pending_question" in st.session_state:
    pending = st.session_state.pop("pending_question")
    handle_question(pending)

if prompt := st.chat_input("Yahşi Batı hakkında bir soru sor…"):
    handle_question(prompt)
