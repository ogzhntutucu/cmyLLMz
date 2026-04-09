"""
embedder.py
-----------
SentenceTransformer ile chunk metinlerini embedding vektörlerine çevirir.

Model: paraphrase-multilingual-MiniLM-L12-v2
Çıktı boyutu: 384 boyutlu vektör
Türkçe dahil 50+ dil destekler.

Embedding için birleştirilecek metin:
{text}
Özet: {summary}
Mizah teknikleri: {humor_analysis.techniques}
Neden komik: {humor_analysis.why_funny}
Kültürel bağlam: {humor_analysis.cultural_context}
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384


def load_model():
    """SentenceTransformer modelini yükle."""
    # TODO: Implement
    # from sentence_transformers import SentenceTransformer
    # return SentenceTransformer(MODEL_NAME)
    pass


def build_embedding_text(chunk: dict) -> str:
    """
    Chunk'tan embedding için birleştirilmiş metin oluştur.
    
    text + summary + humor_analysis bilgileri birleştirilir.
    Bu, retrieval kalitesini artırır.
    """
    # TODO: Implement
    pass


def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    """Chunk listesini embedding vektörlerine çevir."""
    # TODO: Implement
    pass


def main():
    print("⚠️  embedder.py henüz implement edilmedi. Hafta 2'de doldurulacak.")


if __name__ == "__main__":
    main()
