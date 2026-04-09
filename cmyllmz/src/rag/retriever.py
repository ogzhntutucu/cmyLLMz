"""
retriever.py
------------
Kullanıcı sorusunu alır, embedding'e çevirir, ChromaDB'den ilgili chunk'ları getirir
ve LLM'e gönderilecek prompt'u oluşturur.

Akış:
1. Soruyu embedding'e çevir
2. ChromaDB'den top-k chunk getir
3. Getirilen chunk'ların related_chunks alanını kontrol et
4. İlişkili chunk'ları da getir (maks toplam 5 chunk)
5. Tüm chunk'ları prompt template'ine yerleştir
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def retrieve(query: str, top_k: int = 3, filters: dict = None) -> list[dict]:
    """
    Sorguya en benzer chunk'ları getir.
    
    Args:
        query: Kullanıcının sorusu
        top_k: Kaç chunk getirileceği
        filters: Metadata filtreleri (karakter, sahne türü vs.)
    
    Returns:
        İlgili chunk'ların listesi (related_chunks dahil)
    """
    # TODO: Implement
    # 1. query'yi embed et
    # 2. ChromaDB'den top-k getir
    # 3. related_chunks kontrolü
    # 4. Toplam maks 5 chunk ile sınırla
    pass


def build_context(chunks: list[dict]) -> str:
    """Getirilen chunk'ları LLM prompt'u için formatla."""
    # TODO: Implement
    pass


def main():
    print("⚠️  retriever.py henüz implement edilmedi. Hafta 2'de doldurulacak.")


if __name__ == "__main__":
    main()
