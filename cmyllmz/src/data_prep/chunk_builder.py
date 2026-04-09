"""
chunk_builder.py
----------------
ham_chunks.json'u (raw_subtitles) okur, ardışık blokları sahne bazında birleştirir.

Birleştirme mantığı:
- İki ardışık bloğun zaman farkı > 3 saniye → yeni chunk
- Chunk ID formatı: yb_001, yb_002, ...
- Çıktı şeması proje planındaki JSON şemasıyla uyumlu
"""

import json
from pathlib import Path


# Proje kök dizini (src/data_prep/ → iki seviye yukarı)
PROJECT_ROOT = Path(__file__).parent.parent.parent


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
        
        # Tek text alanı
        text_parts = [b["text"] for b in chunk_blocks if b["text"]]
        text = " ".join(text_parts).strip()
        
        is_frame = any(b["is_frame_story"] for b in chunk_blocks)
        start = chunk_blocks[0]["start"]
        end = chunk_blocks[-1]["end"]
        
        # Yeni proje planı şemasına uygun çıktı
        result.append({
            "id": chunk_id,
            "start": start,
            "end": end,
            "duration_sec": round(time_to_seconds(end) - time_to_seconds(start), 1),
            "text": text,
            "characters": [],
            "scene_type": "frame_story" if is_frame else "",
            "location": "",
            "note": "",
            "related_chunks": [],
            "humor_analysis": {
                "techniques": [],
                "why_funny": "",
                "cultural_context": "",
                "comedic_timing": ""
            },
            "entities": {
                "persons": [],
                "locations": [],
                "orgs": [],
                "misc": []
            },
            "summary": ""
        })
    
    return result


def main():
    in_file = PROJECT_ROOT / "data" / "processing" / "ham_chunks.json"
    out_file = PROJECT_ROOT / "data" / "processing" / "chunks.json"
    
    GAP_THRESHOLD = 3.0
    
    print(f"Okunuyor: {in_file}")
    blocks = json.loads(in_file.read_text(encoding='utf-8'))
    print(f"Toplam blok: {len(blocks)}")
    
    chunks = build_chunks(blocks, gap_threshold_sec=GAP_THRESHOLD)
    
    print(f"\n✅ Oluşturulan chunk sayısı: {len(chunks)}")
    
    frame_chunks = sum(1 for c in chunks if c["scene_type"] == "frame_story")
    avg_len = sum(len(c["text"]) for c in chunks) / len(chunks)
    
    print(f"   ├─ Çerçeve hikaye chunk: {frame_chunks}")
    print(f"   └─ Ortalama chunk uzunluğu: {avg_len:.0f} karakter")
    
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"\n💾 Kaydedildi: {out_file}")
    
    print("\n--- İlk 3 chunk:")
    for c in chunks[:3]:
        print(f"  [{c['id']}] {c['start']} → {c['end']}")
        preview = c['text'][:120] + "..." if len(c['text']) > 120 else c['text']
        print(f"  {preview}")
        print()


if __name__ == "__main__":
    main()
