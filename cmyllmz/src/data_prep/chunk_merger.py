"""
chunk_merger.py
---------------
notes/block_referans.txt dosyasını okur, === ile ayrılmış chunk gruplarını
ham_chunks.json ile birleştirerek base_chunks.json oluşturur.

Dosya formatı (block_referans.txt):
    0001 [00:00:14] - Şimdi kadın, ince uzun da olur...
    0002 [00:00:18] ...şöyle de olur, böyle de olur deyince...
    --- [3s boşluk] ---        ← bunlara dokunma
    0006 [00:00:30] - Tabii canım, eskiden ona zıbık derler.
    ===                        ← chunk sınırı (senin eklediğin)
    0015 [00:01:09] - Zekicim, istersen şey yapalım.
    ...

Kullanım:
    python src/data_prep/chunk_merger.py
"""

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent

BLOCK_LINE = re.compile(r'^(\d{4})\s+\[\d{2}:\d{2}:\d{2}\]\s*(.*)')


def time_to_seconds(t: str) -> float:
    parts = t.split(':')
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2].replace(',', '.'))
    return h * 3600 + m * 60 + s


def parse_ref_file(filepath: Path) -> list[list[tuple[int, str]]]:
    """
    block_referans.txt'yi oku.
    Çıktı: chunk listesi. Her chunk, (seq_num, text) çiftlerinin listesi.
    """
    chunks = []
    current: list[tuple[int, str]] = []

    for line in filepath.read_text(encoding='utf-8').splitlines():
        line = line.rstrip()

        if line.startswith('==='):
            if current:
                chunks.append(current)
                current = []
            continue

        if line.startswith('---') or not line:
            continue  # boşluk göstergesi veya boş satır

        m = BLOCK_LINE.match(line)
        if m:
            seq_num = int(m.group(1))
            text = m.group(2).strip()
            current.append((seq_num, text))

    if current:
        chunks.append(current)

    return chunks


def build_chunks(
    ref_chunks: list[list[tuple[int, str]]],
    blocks: list[dict],
) -> list[dict]:
    """
    ref_chunks: parse_ref_file çıktısı
    blocks: ham_chunks.json içeriği (start/end zamanları için)
    """
    chunks = []

    for chunk_num, block_entries in enumerate(ref_chunks, start=1):
        if not block_entries:
            continue

        seq_nums = [s for s, _ in block_entries]
        texts = [t for _, t in block_entries]

        # Seq num → ham block (start/end için)
        first_block = blocks[seq_nums[0] - 1]
        last_block = blocks[seq_nums[-1] - 1]

        start_time = first_block['start']
        end_time = last_block['end']
        duration = round(time_to_seconds(end_time) - time_to_seconds(start_time), 1)

        text = ' '.join(t for t in texts if t).strip()

        chunks.append({
            "id": f"yb_{chunk_num:03d}",
            "start": start_time,
            "end": end_time,
            "duration_sec": duration,
            "block_range": f"{seq_nums[0]:04d}-{seq_nums[-1]:04d}",
            "text": text,
            "characters": [],
            "scene_type": "",
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

    return chunks


def main():
    ref_file = PROJECT_ROOT / "notes" / "block_referans.txt"
    blocks_file = PROJECT_ROOT / "data" / "processing" / "ham_chunks.json"
    out_file = PROJECT_ROOT / "data" / "processing" / "base_chunks.json"

    blocks = json.loads(blocks_file.read_text(encoding='utf-8'))
    print(f"Ham block sayısı: {len(blocks)}")

    ref_chunks = parse_ref_file(ref_file)
    print(f"Tespit edilen chunk sayısı: {len(ref_chunks)}")

    if not ref_chunks:
        print("❌ block_referans.txt'de henüz === ile ayrılmış chunk bulunamadı.")
        return

    # Kaç block kapsandı?
    covered = sum(len(c) for c in ref_chunks)
    print(f"Kapsanan block: {covered} / {len(blocks)}")
    if covered < len(blocks):
        print(f"⚠️  {len(blocks) - covered} block hiçbir chunk'a dahil edilmemiş.")

    chunks = build_chunks(ref_chunks, blocks)
    print(f"\n✅ Oluşturulan chunk sayısı: {len(chunks)}")

    durations = [c['duration_sec'] for c in chunks]
    print(f"   Ortalama süre : {sum(durations) / len(durations):.0f}s")
    print(f"   En kısa / uzun: {min(durations):.0f}s  /  {max(durations):.0f}s")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 Kaydedildi: {out_file}")

    print("\n--- İlk 3 chunk:")
    for c in chunks[:3]:
        preview = c['text'][:100] + '...' if len(c['text']) > 100 else c['text']
        print(f"  [{c['id']}] {c['start']} → {c['end']} ({c['duration_sec']:.0f}s) | blocks {c['block_range']}")
        print(f"  {preview}")
        print()


if __name__ == "__main__":
    main()
