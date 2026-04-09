"""
preprocessor.py
---------------
NLP ön işleme adımları. Rapor için uygulanır, embedding'e doğrudan verilmez.

Adımlar:
1. Metin temizleme (HTML tagları, fazla boşluklar)
2. Tokenizasyon (NLTK veya spaCy)
3. Stop-word çıkarımı (Türkçe stop-word listesi)
4. Normalizasyon (küçük harf, Zeyrek ile lemmatizasyon)

NOT: Embedding modeli (SentenceTransformer) kendi tokenizer'ını kullanır.
Bu ön işleme adımları SADECE raporlama ve NLP süreçlerini göstermek için uygulanır.
Embedding ve retrieval için orijinal temiz metin kullanılır.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def clean_text(text: str) -> str:
    """HTML taglarını ve artefaktları temizle."""
    # TODO: Implement
    pass


def tokenize(text: str) -> list[str]:
    """Metni kelime bazında token'lara ayır."""
    # TODO: Implement
    pass


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Türkçe stop-word'leri çıkar."""
    # TODO: Implement
    pass


def normalize(tokens: list[str]) -> list[str]:
    """Küçük harf + Zeyrek ile lemmatizasyon."""
    # TODO: Implement
    pass


def preprocess_pipeline(text: str) -> dict:
    """
    Tam ön işleme pipeline'ı. Rapor için her adımın çıktısını döndürür.
    
    Returns:
        {
            "original": str,
            "cleaned": str,
            "tokens": list[str],
            "token_count": int,
            "without_stopwords": list[str],
            "stopword_removed_count": int,
            "normalized": list[str],
        }
    """
    # TODO: Implement
    pass


def main():
    """Tüm chunk'lar üzerinde ön işleme çalıştır ve sonuçları kaydet."""
    input_file = PROJECT_ROOT / "data" / "processing" / "annotated_chunks.json"
    output_file = PROJECT_ROOT / "data" / "processing" / "preprocessing_report.json"

    # TODO: Implement
    print("⚠️  preprocessor.py henüz implement edilmedi. Hafta 2'de doldurulacak.")


if __name__ == "__main__":
    main()
