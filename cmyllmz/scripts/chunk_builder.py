"""
chunk_builder.py
----------------
raw_subtitles.json'u okur, ardışık blokları sahne bazında birleştirir.

Birleştirme mantığı:
- İki ardışık bloğun zaman farkı > 3 saniye → yeni chunk
- Her chunk'ta text_tr ve text_en (varsa) alanları var
- Chunk ID formatı: yb_001, yb_002, ...
"""

import json
from pathlib import Path
from datetime import datetime


def time_to_seconds(t: str) -> float:
    """'01:23:45' → saniye (float)"""
    parts = t.split(':')
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2].replace(',', '.'))
    return h * 3600 + m * 60 + s


def build_chunks(blocks: list[dict], gap_threshold_sec: float = 3.0) -> list[dict]:
    """
    Ardışık blokları sahne bazında birleştir.
    gap_threshold_sec: saniyeden fazla boşluk varsa yeni chunk başlar.
    """
    if not blocks:
        return []
    
    chunks = []
    current_chunk_blocks = [blocks[0]]
    
    for i in range(1, len(blocks)):
        prev_end = time_to_seconds(blocks[i - 1]["end"])
        curr_start = time_to_seconds(blocks[i]["start"])
        gap = curr_start - prev_end
        
        if gap > gap_threshold_sec:
            # Yeni sahne başlıyor — mevcut chunk'ı kaydet
            chunks.append(current_chunk_blocks)
            current_chunk_blocks = [blocks[i]]
        else:
            # Aynı sahne devam ediyor
            current_chunk_blocks.append(blocks[i])
    
    # Son chunk'ı da kaydet
    chunks.append(current_chunk_blocks)
    
    # Her chunk grubunu birleştirerek JSON objesi yap
    result = []
    for idx, chunk_blocks in enumerate(chunks):
        chunk_id = f"yb_{idx + 1:03d}"
        
        # Türkçe metinleri birleştir
        tr_parts = [b["text_tr"] for b in chunk_blocks if b["text_tr"]]
        tr_text = " ".join(tr_parts).strip()
        
        # İngilizce metinleri birleştir (varsa)
        en_parts = [b["text_en"] for b in chunk_blocks if b.get("text_en")]
        en_text = " ".join(en_parts).strip() if en_parts else None
        
        # Çerçeve hikaye mi?
        is_frame = any(b["is_frame_story"] for b in chunk_blocks)
        
        # Zaman aralığı
        start = chunk_blocks[0]["start"]
        end = chunk_blocks[-1]["end"]
        
        # Blok id'leri (izlenebilirlik için)
        block_ids = [b["block_id"] for b in chunk_blocks]
        
        result.append({
            "id": chunk_id,
            "start": start,
            "end": end,
            "duration_sec": round(time_to_seconds(end) - time_to_seconds(start), 1),
            "block_count": len(chunk_blocks),
            "block_ids": block_ids,
            "text_tr": tr_text,
            "text_en": en_text,
            "is_frame_story": is_frame,
            # Zenginleştirme aşamasında doldurulacak alanlar
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
    
    # gap_threshold saniye sınırını isteğe göre değiştirebilirsin
    GAP_THRESHOLD = 3.0
    
    print(f"Okunuyor: {in_file}")
    blocks = json.loads(in_file.read_text(encoding='utf-8'))
    print(f"Toplam blok: {len(blocks)}")
    
    chunks = build_chunks(blocks, gap_threshold_sec=GAP_THRESHOLD)
    
    print(f"\n✅ Oluşturulan chunk sayısı: {len(chunks)}")
    
    # İstatistikler
    frame_chunks = sum(1 for c in chunks if c["is_frame_story"])
    multi_block = sum(1 for c in chunks if c["block_count"] > 1)
    with_en = sum(1 for c in chunks if c["text_en"])
    avg_blocks = sum(c["block_count"] for c in chunks) / len(chunks)
    
    print(f"   ├─ Çerçeve hikaye chunk: {frame_chunks}")
    print(f"   ├─ Birden fazla bloktan oluşan: {multi_block}")
    print(f"   ├─ İngilizce metni olan: {with_en}")
    print(f"   └─ Ortalama blok/chunk: {avg_blocks:.1f}")
    
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"\n💾 Kaydedildi: {out_file}")
    
    # İlk 3 chunk önizle
    print("\n--- İlk 3 chunk:")
    for c in chunks[:3]:
        print(f"  [{c['id']}] {c['start']} → {c['end']} ({c['block_count']} blok)")
        preview = c['text_tr'][:100] + "..." if len(c['text_tr']) > 100 else c['text_tr']
        print(f"  TR: {preview}")
        if c['text_en']:
            en_preview = c['text_en'][:80] + "..." if len(c['text_en']) > 80 else c['text_en']
            print(f"  EN: {en_preview}")
        print()
    
    # GAP deneyimi: farklı threshold'lar ne verir?
    print(f"\n📊 Farklı gap sınırları için chunk sayısı tahmini:")
    for t in [1.0, 2.0, 3.0, 5.0, 8.0]:
        c = build_chunks(blocks, gap_threshold_sec=t)
        print(f"  {t:.0f}s gap → {len(c)} chunk")


if __name__ == "__main__":
    main()
