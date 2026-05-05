"""
embedder.py
-----------
BAAI/bge-m3 modeliyle chunk metinlerini embedding vektörlerine çevirir.

Embedding için birleştirilen içerik: summary + text (concat)
- summary: retrieval kalitesini güçlendirir (semantik özet)
- text: detaylı diyalog ve sahne bilgisini sağlar

bge-m3: 8192 token, Türkçe dahil çok dilli, prefix gerekmez.

Model: BAAI/bge-m3
Çıktı boyutu: 1024
Max token: 8192
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"

_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_embedding_text(chunk: dict) -> str:
    """Embedding için summary + text + destekleyici metadata concat üret."""
    parts = []

    if summary := chunk.get("summary", "").strip():
        parts.append(summary)

    if text := chunk.get("text", "").strip():
        parts.append(text)

    if location := chunk.get("location", "").strip():
        parts.append(f"Mekan: {location}")

    chars = chunk.get("characters", {})
    if isinstance(chars, dict) and chars:
        names = ", ".join(chars.values())
        parts.append(f"Karakterler: {names}")

    ha = chunk.get("humor_analysis", {})
    if techniques := ha.get("techniques", []):
        parts.append(f"Mizah teknikleri: {', '.join(techniques)}")
    if ctx := ha.get("cultural_context", "").strip():
        parts.append(f"Kültürel bağlam: {ctx}")

    return " ".join(parts)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Metin listesini embedding vektörlerine çevir."""
    model = load_model()
    vectors = model.encode(
        texts,
        batch_size=8,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    return [v.tolist() for v in vectors]


def embed_query(query: str) -> list[float]:
    """Tek bir sorguyu embed et."""
    model = load_model()
    vec = model.encode(query, normalize_embeddings=True)
    return vec.tolist()
