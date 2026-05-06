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
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

_char_map_cache: dict | None = None


def _load_char_map() -> dict:
    """karakterler.txt'den KOD → İsim sözlüğü yükle (cache'li)."""
    global _char_map_cache
    if _char_map_cache is not None:
        return _char_map_cache
    char_file = PROJECT_ROOT / "notes" / "karakterler.txt"
    result = {}
    for line in char_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if " = " in line:
            code, name = line.split(" = ", 1)
            result[code.strip()] = name.strip()
    _char_map_cache = result
    return result


def replace_codes(text: str, char_map: dict | None = None) -> str:
    """LLM çıktısındaki karakter kodlarını gerçek isimlerle değiştir (post-process güvenlik ağı).
    Parantez içi açıklamayı atar, sadece isim kısmını kullanır.
    """
    if char_map is None:
        char_map = _load_char_map()
    for code, full_name in char_map.items():
        name = full_name.split("(")[0].strip()  # "Şerif Lloyd (açıklama)" → "Şerif Lloyd"
        text = re.sub(rf"-{re.escape(code)}-", name, text)
        text = re.sub(rf"\b{re.escape(code)}\b", name, text)
    return text

TOP_K = 5        # semantic search sonuç sayısı
MAX_CHUNKS = 8   # related_chunks dahil toplam üst sınır


def _parse_timestamp_query(query: str) -> int | None:
    """
    Sorguda dakika/saat referansı varsa saniyeye çevir, yoksa None döner.
    Örnekler: '90. dakikada', '1 saat 30 dk', '01:30:00'
    """
    # "1 saat", "1 saat 30 dakika" — önce kontrol et
    m = re.search(r"\b(\d+)\s*saat(?:\s*(\d+)\s*(?:dakika|dk))?", query, re.IGNORECASE)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2) or 0) * 60
    # "90. dakika", "90 dk", "90 dakikada", "90. dkda"
    m = re.search(r"\b(\d+)\s*\.?\s*(?:dakika|dk)", query, re.IGNORECASE)
    if m:
        return int(m.group(1)) * 60
    # "01:30:00" veya "01:30"
    m = re.search(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b", query)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3) or 0)
    return None


def retrieve(query: str, top_k: int = TOP_K, where: dict | None = None) -> list[dict]:
    """
    Sorguya en benzer chunk'ları getir, related_chunks ile genişlet.

    Timestamp sorgusu (ör. '90. dakika') tespit edilirse ilgili chunk metadata
    filtresiyle kesin olarak öne alınır; ardından semantik arama eklenir.

    Returns:
        Her chunk: id, text, summary, location, characters, techniques, related_chunks, score
    """
    from rag.embedder import embed_query
    from rag.vector_store import query_collection, get_by_ids

    query_vec = embed_query(query)

    # Timestamp tespiti — metadata ile kesin chunk bul
    pinned_chunks: list[dict] = []
    if where is None:
        target_sec = _parse_timestamp_query(query)
        if target_sec is not None:
            ts_where = {"$and": [
                {"start_sec": {"$lte": target_sec}},
                {"end_sec": {"$gte": target_sec}},
            ]}
            try:
                ts_results = query_collection(query_vec, n_results=1, where=ts_where)
                if ts_results["ids"][0]:
                    pinned_chunks = _parse_results(ts_results)
            except Exception:
                pass  # timestamp chunk bulunamazsa semantic'e düş

    # Semantik arama
    results = query_collection(query_vec, n_results=top_k, where=where)
    chunks = _parse_results(results)

    # Pinned chunk'ı başa al, tekrarı önle
    if pinned_chunks:
        pinned_ids = {c["id"] for c in pinned_chunks}
        chunks = [c for c in chunks if c["id"] not in pinned_ids]
        chunks = pinned_chunks + chunks

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
        "start_sec": meta.get("start_sec", 0),
        "end_sec": meta.get("end_sec", 0),
        "location": meta.get("location", ""),
        "summary": meta.get("summary", ""),
        "mechanism": meta.get("mechanism", ""),
        "cultural_context": meta.get("cultural_context", ""),
        "techniques": json.loads(meta.get("techniques_json", "[]")),
        "characters": json.loads(meta.get("characters_json", "{}")),
        "related_chunks": json.loads(meta.get("related_chunks_json", "[]")),
        "komik_count": meta.get("komik_count", 0),
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
        stream=True:  (token_generator, chunks_list) — post-processing app katmanında
    """
    from llm.openai_client import chat
    from llm.prompt_templates import SYSTEM_PROMPT, format_user_prompt

    char_map = _load_char_map()
    chunks = retrieve(query, top_k=top_k)
    context = build_context(chunks)
    user_prompt = format_user_prompt(context, query, char_map=char_map)
    response = chat(SYSTEM_PROMPT, user_prompt, stream=stream)
    if not stream:
        response = replace_codes(response, char_map)
    return response, chunks


def ask_with_history(
    query: str,
    history: list[dict],
    stream: bool = False,
    top_k: int = TOP_K,
):
    """
    Multi-turn: soru + önceki sohbet geçmişi → retrieval → LLM cevabı.

    Retrieval sadece mevcut query üzerinden yapılır.
    LLM tüm önceki Q&A geçmişini görür → follow-up sorularında bağlam kurar.

    history: [{"role": "user"|"assistant", "content": "..."}]
             Mevcut soru dahil edilmez, zaten user_prompt içinde.

    Returns:
        stream=False: (cevap_str, chunks_list)
        stream=True:  (token_generator, chunks_list)
    """
    from llm.openai_client import chat
    from llm.prompt_templates import SYSTEM_PROMPT, format_user_prompt

    char_map = _load_char_map()
    chunks = retrieve(query, top_k=top_k)
    context = build_context(chunks)
    user_prompt = format_user_prompt(context, query, char_map=char_map)
    response = chat(SYSTEM_PROMPT, user_prompt, stream=stream, history=history)
    if not stream:
        response = replace_codes(response, char_map)
    return response, chunks
