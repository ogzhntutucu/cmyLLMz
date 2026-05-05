"""
retriever.py
------------
Kullanıcı sorusunu alır, ChromaDB'den ilgili chunk'ları getirir,
related_chunks ile bağlamı genişletir ve LLM için formatlar.

Akış:
1. Soruyu embed et
2. ChromaDB'den top-k chunk getir
3. Getirilen chunk'ların related_chunks alanını kontrol et
4. Henüz listede olmayan related chunk'ları ekle (maks toplam MAX_CHUNKS)
5. Chunk'ları LLM context'i için formatla
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

TOP_K = 5        # semantic search sonuç sayısı
MAX_CHUNKS = 8   # related_chunks dahil toplam üst sınır


def retrieve(query: str, top_k: int = TOP_K, where: dict | None = None) -> list[dict]:
    """
    Sorguya en benzer chunk'ları getir, related_chunks ile genişlet.

    Returns:
        Her chunk: id, text, summary, location, characters, techniques, related_chunks, score
    """
    from rag.embedder import embed_query
    from rag.vector_store import query_collection, get_by_ids

    query_vec = embed_query(query)
    results = query_collection(query_vec, n_results=top_k, where=where)

    chunks = _parse_results(results)

    # related_chunks expansion
    seen_ids = {c["id"] for c in chunks}
    extra_ids = []
    for c in chunks:
        for rid in c.get("related_chunks", []):
            if rid not in seen_ids and rid not in extra_ids:
                extra_ids.append(rid)
                if len(seen_ids) + len(extra_ids) >= MAX_CHUNKS:
                    break
        if len(seen_ids) + len(extra_ids) >= MAX_CHUNKS:
            break

    if extra_ids:
        extra_results = get_by_ids(extra_ids)
        extra_chunks = _parse_get_results(extra_results)
        chunks.extend(extra_chunks)

    return chunks


def _parse_results(results: dict) -> list[dict]:
    """query_collection çıktısını düz chunk listesine çevir."""
    chunks = []
    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]

    for cid, meta, doc, dist in zip(ids, metadatas, documents, distances):
        chunks.append(_build_chunk(cid, meta, doc, score=1 - dist))
    return chunks


def _parse_get_results(results: dict) -> list[dict]:
    """get_by_ids çıktısını düz chunk listesine çevir."""
    chunks = []
    for cid, meta, doc in zip(results["ids"], results["metadatas"], results["documents"]):
        chunks.append(_build_chunk(cid, meta, doc, score=None))
    return chunks


def _build_chunk(cid: str, meta: dict, doc: str, score) -> dict:
    return {
        "id": cid,
        "score": score,
        "start": meta.get("start", ""),
        "end": meta.get("end", ""),
        "location": meta.get("location", ""),
        "summary": meta.get("summary", ""),
        "mechanism": meta.get("mechanism", ""),
        "cultural_context": meta.get("cultural_context", ""),
        "techniques": json.loads(meta.get("techniques_json", "[]")),
        "characters": json.loads(meta.get("characters_json", "{}")),
        "related_chunks": json.loads(meta.get("related_chunks_json", "[]")),
        "text": doc,
    }


def build_context(chunks: list[dict]) -> str:
    """Chunk listesini LLM prompt'u için okunabilir metin bloğuna çevir."""
    parts = []
    for c in chunks:
        chars = ", ".join(f"{k}: {v}" for k, v in c["characters"].items()) or "—"
        score_str = f" (benzerlik: {c['score']:.2f})" if c["score"] is not None else " (ilişkili sahne)"
        block = (
            f"### {c['id']}{score_str}\n"
            f"Zaman: {c['start']} → {c['end']}\n"
            f"Mekan: {c['location'] or '—'}\n"
            f"Karakterler: {chars}\n"
            f"Özet: {c['summary']}\n"
            f"Mizah: {', '.join(c['techniques']) or '—'}\n"
        )
        if c["mechanism"]:
            block += f"Mekanizma: {c['mechanism']}\n"
        if c["cultural_context"]:
            block += f"Kültürel bağlam: {c['cultural_context']}\n"
        if c["related_chunks"]:
            block += f"İlişkili sahneler: {', '.join(c['related_chunks'])}\n"
        block += f"\nMetin:\n{c['text']}"
        parts.append(block)
    return "\n\n---\n\n".join(parts)


def ask(query: str, stream: bool = False, top_k: int = TOP_K):
    """
    Uçtan uca: soru → retrieval → LLM cevabı.

    Returns:
        stream=False: (cevap_str, chunks_list)
        stream=True:  (token_generator, chunks_list)
    """
    from llm.openai_client import chat
    from llm.prompt_templates import SYSTEM_PROMPT, format_user_prompt

    chunks = retrieve(query, top_k=top_k)
    context = build_context(chunks)
    user_prompt = format_user_prompt(context, query)
    response = chat(SYSTEM_PROMPT, user_prompt, stream=stream)
    return response, chunks
