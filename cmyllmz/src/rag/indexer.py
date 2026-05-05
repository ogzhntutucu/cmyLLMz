"""
indexer.py
----------
enriched_chunks.json'daki 62 chunk'ı embed edip ChromaDB'ye yükler.

Akış:
1. enriched_chunks.json oku
2. Her chunk için "passage: {summary} {text}" embed metni oluştur
3. multilingual-e5-large ile batch embed et
4. ChromaDB yb_chunks collection'ına yükle

Kullanım:
    python src/rag/indexer.py
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rag.embedder import build_embedding_text, embed_texts
from rag.vector_store import load_chunks, collection_count


def main():
    input_file = PROJECT_ROOT / "data" / "processing" / "enriched_chunks.json"

    if not input_file.exists():
        print(f"HATA: {input_file} bulunamadı.")
        sys.exit(1)

    chunks: list[dict] = json.loads(input_file.read_text(encoding="utf-8"))
    print(f"Yüklenen chunk: {len(chunks)}")

    print("Embedding metinleri hazırlanıyor...")
    documents = [build_embedding_text(c) for c in chunks]

    # Token uzunluğu kontrolü (bilgi amaçlı)
    avg_len = sum(len(d.split()) for d in documents) / len(documents)
    max_len = max(len(d.split()) for d in documents)
    print(f"Ortalama kelime uzunluğu: {avg_len:.0f}, maksimum: {max_len}")

    print(f"\nEmbedding başlıyor ({len(documents)} chunk)...")
    embeddings = embed_texts(documents)
    print(f"Embedding tamamlandı. Boyut: {len(embeddings[0])}")

    print("\nChromaDB'ye yükleniyor...")
    load_chunks(chunks, embeddings, documents)

    count = collection_count()
    print(f"\nToplam indexlenen chunk: {count}")

    if count != len(chunks):
        print(f"UYARI: Beklenen {len(chunks)}, indexlenen {count} — uyuşmazlık var!")
        sys.exit(1)

    print("Faz 10 tamamlandı.")


if __name__ == "__main__":
    main()
