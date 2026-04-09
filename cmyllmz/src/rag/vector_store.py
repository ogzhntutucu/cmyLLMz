"""
vector_store.py
---------------
ChromaDB ile vektör veritabanı işlemleri.

Koleksiyon: "yahsi_bati"
Distance metric: cosine similarity
Persistent storage: chroma_db/ dizini
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

COLLECTION_NAME = "yahsi_bati"
CHROMA_DB_PATH = str(PROJECT_ROOT / "chroma_db")


def get_client():
    """Persistent ChromaDB client döndür."""
    # TODO: Implement
    # import chromadb
    # return chromadb.PersistentClient(path=CHROMA_DB_PATH)
    pass


def get_or_create_collection(client=None):
    """Koleksiyonu getir veya oluştur."""
    # TODO: Implement
    pass


def load_chunks_to_db(chunks: list[dict], embeddings: list[list[float]]):
    """
    Chunk'ları ve embedding'lerini ChromaDB'ye yükle.
    
    Her chunk için:
    - id: chunk ID'si (yb_001, yb_002...)
    - documents: birleştirilmiş metin (text + summary + humor_analysis)
    - embeddings: vektör
    - metadatas: tüm chunk alanları (filtreleme için)
    """
    # TODO: Implement
    pass


def query(query_embedding: list[float], n_results: int = 3, where: dict = None):
    """
    ChromaDB'den en benzer chunk'ları getir.
    
    Args:
        query_embedding: Sorgu vektörü
        n_results: Kaç sonuç getirileceği
        where: Metadata filtresi (opsiyonel)
    """
    # TODO: Implement
    pass


def delete_collection():
    """Koleksiyonu sil (yeniden yükleme için)."""
    # TODO: Implement
    pass


def main():
    print("⚠️  vector_store.py henüz implement edilmedi. Hafta 2'de doldurulacak.")


if __name__ == "__main__":
    main()
