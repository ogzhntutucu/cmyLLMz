"""
chunk_builder.py
----------------
raw_subtitles.json'u okur, ardışık blokları sahne bazında birleştirir.

Birleştirme mantığı:
- İki ardışık bloğun zaman farkı > 3 saniye → yeni chunk
- Her chunk'ta tek `text` alanı var (TR + EN birleşik)
- Chunk ID formatı: yb_001, yb_002, ...
"""

import json
from pathlib import Path


def time_to_seconds(t: str) -> float:
    """'01:23:45' → saniye (float)"""
    parts = t.split(':')
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2].replace(',', '.'))
    return h * 3600 + m * 60 + s


def build_chunks(blocks: list[dict], gap_threshold_sec: float = 3.0) -> list[dict]:
    if not blocks:
        return []
    
    chunks = []
    current_chunk_blocks = [blocks[0]]
    
    for i in range(1, len(blocks)):
        prev_end = time_to_seconds(blocks[i - 1]["end"])
        curr_start = time_to_seconds(blocks[i]["start"])
        gap = curr_start - prev_end
        
        if gap > gap_threshold_sec:
            chunks.append(current_chunk_blocks)
            current_chunk_blocks = [blocks[i]]
        else:
            current_chunk_blocks.append(blocks[i])
    
    chunks.append(current_chunk_blocks)
    
    result = []
    for idx, chunk_blocks in enumerate(chunks):
        chunk_id = f"yb_{idx + 1:03d}"
        
        # Tek text alanı (EN + TR birleşik)
        text_parts = [b["text"] for b in chunk_blocks if b["text"]]
        text = " ".join(text_parts).strip()
        
        is_frame = any(b["is_frame_story"] for b in chunk_blocks)
        start = chunk_blocks[0]["start"]
        end = chunk_blocks[-1]["end"]
        block_ids = [b["block_id"] for b in chunk_blocks]
        
        result.append({
            "id": chunk_id,
            "start": start,
            "end": end,
            "duration_sec": round(time_to_seconds(end) - time_to_seconds(start), 1),
            "block_count": len(chunk_blocks),
            "block_ids": block_ids,
            "text": text,
            "is_frame_story": is_frame,
            "characters": [],
            "scene": "",
            "context": "",
            "tags": []
        })
    
    return result


def main():
    base = Path(__file__).parent.parent
    in_file = base / "data" / "filmler" / "yahsi_bati" / "processed" / "raw_subtitles.json"
    out_file = base / "data" / "filmler" / "yahsi_bati" / "processed" / "chunks.json"
    
    GAP_THRESHOLD = 3.0
    
    print(f"Okunuyor: {in_file}")
    blocks = json.loads(in_file.read_text(encoding='utf-8'))
    print(f"Toplam blok: {len(blocks)}")
    
    chunks = build_chunks(blocks, gap_threshold_sec=GAP_THRESHOLD)
    
    print(f"\n✅ Oluşturulan chunk sayısı: {len(chunks)}")
    
    frame_chunks = sum(1 for c in chunks if c["is_frame_story"])
    multi_block = sum(1 for c in chunks if c["block_count"] > 1)
    avg_blocks = sum(c["block_count"] for c in chunks) / len(chunks)
    avg_len = sum(len(c["text"]) for c in chunks) / len(chunks)
    
    print(f"   ├─ Çerçeve hikaye chunk: {frame_chunks}")
    print(f"   ├─ Birden fazla bloktan oluşan: {multi_block}")
    print(f"   ├─ Ortalama blok/chunk: {avg_blocks:.1f}")
    print(f"   └─ Ortalama chunk uzunluğu: {avg_len:.0f} karakter")
    
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"\n💾 Kaydedildi: {out_file}")
    
    print("\n--- İlk 3 chunk:")
    for c in chunks[:3]:
        print(f"  [{c['id']}] {c['start']} → {c['end']} ({c['block_count']} blok)")
        preview = c['text'][:120] + "..." if len(c['text']) > 120 else c['text']
        print(f"  {preview}")
        print()


if __name__ == "__main__":
    main()
