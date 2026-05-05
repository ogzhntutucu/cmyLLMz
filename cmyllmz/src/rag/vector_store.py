"""
vector_store.py
---------------
ChromaDB ile vektör veritabanı işlemleri.

Koleksiyon: yb_chunks
Distance metric: cosine similarity
Persistent storage: data/chroma/ dizini
"""

import json
from pathlib import Path

import chromadb

PROJECT_ROOT = Path(__file__).parent.parent.parent

COLLECTION_NAME = "yb_chunks"
CHROMA_DB_PATH = str(PROJECT_ROOT / "data" / "chroma")


def get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_or_create_collection(client: chromadb.PersistentClient) -> chromadb.Collection:
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _build_metadata(chunk: dict) -> dict:
    """ChromaDB metadata'sı — sadece scalar değerler (str, int, float, bool)."""
    ha = chunk.get("humor_analysis", {})
    return {
        "location": chunk.get("location", "") or "",
        "start": chunk.get("start", ""),
        "end": chunk.get("end", ""),
        "duration_sec": chunk.get("duration_sec", 0.0),
        "block_range": chunk.get("block_range", ""),
        "characters_json": json.dumps(chunk.get("characters", {}), ensure_ascii=False),
        "related_chunks_json": json.dumps(chunk.get("related_chunks", []), ensure_ascii=False),
        "techniques_json": json.dumps(ha.get("techniques", []), ensure_ascii=False),
        "mechanism": ha.get("mechanism", "") or "",
        "cultural_context": ha.get("cultural_context", "") or "",
        "summary": chunk.get("summary", "") or "",
    }


def load_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
    documents: list[str],
) -> None:
    """Chunk'ları ChromaDB'ye yükle. Koleksiyon varsa önce siler."""
    client = get_client()

    # Varsa temizle — tam yeniden yükleme
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)

    col = get_or_create_collection(client)

    ids = [c["id"] for c in chunks]
    metadatas = [_build_metadata(c) for c in chunks]

    col.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    print(f"ChromaDB'ye {len(ids)} chunk yüklendi → {CHROMA_DB_PATH}")


def query_collection(
    query_embedding: list[float],
    n_results: int = 5,
    where: dict | None = None,
) -> dict:
    """En benzer n_results chunk'ı getir."""
    client = get_client()
    col = get_or_create_collection(client)
    kwargs = {"query_embeddings": [query_embedding], "n_results": n_results}
    if where:
        kwargs["where"] = where
    return col.query(**kwargs)


def get_by_ids(ids: list[str]) -> dict:
    """ID listesiyle direkt chunk getir (related_chunks için)."""
    client = get_client()
    col = get_or_create_collection(client)
    return col.get(ids=ids, include=["documents", "metadatas", "embeddings"])


def collection_count() -> int:
    client = get_client()
    col = get_or_create_collection(client)
    return col.count()
