"""
chunk_merger.py
---------------
notes/block_referans.md dosyasındaki === sınırlarını okur,
ham_chunks.json ile birleştirerek base_chunks.json oluşturur.

Beklenen block_referans.md formatı:
    0001 [00:00:14] [rakı masasında oturuyorlar] -AL- Şimdi kadın...
    0002 [00:00:20] -RA- Ustaya bak! [herkes gülüyor]
    --- [3s boşluk] ---        ← bunlara dokunma
    0003 [00:00:25] -AZ- Calm down, calm down.
    ===                        ← chunk sınırı (senin eklediğin)
    0004 [00:00:30] -ZE- Zekicim, istersen şey yapalım.
    ...

Satır içi notlar [...] köşeli parantezle doğrudan block satırına yazılır.
Karakter kodları notes/karakterler.txt'ten yüklenir.
characters alanı -XX- etiketlerinden otomatik doldurulur.

Kullanım:
    python src/data_prep/chunk_merger.py
"""

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent

# -XX- etiket kalıbı: tire, 1-3 büyük harf veya rakam, tire
CHAR_CODE_RE = re.compile(r'-([A-Z][A-Z0-9]{0,2})-')

# Blok satırı: NNNN [HH:MM:SS] metin
BLOCK_LINE_RE = re.compile(r'^(\d{4})\s+\[\d{2}:\d{2}:\d{2}\]\s*(.*)')


def time_to_seconds(t: str) -> float:
    parts = t.split(':')
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2].replace(',', '.'))
    return h * 3600 + m * 60 + s


def load_char_map(filepath: Path) -> dict[str, str]:
    """karakterler.txt'yi oku → {KOD: "Tam İsim"} sözlüğü döndür."""
    char_map = {}
    if not filepath.exists():
        return char_map
    for line in filepath.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            kod, isim = line.split('=', 1)
            char_map[kod.strip()] = isim.strip()
    return char_map


def extract_characters(text: str, char_map: dict[str, str]) -> list[str]:
    """Metindeki -XX- etiketlerini bul, tam isimlere çevir, sırala."""
    codes = CHAR_CODE_RE.findall(text)
    seen = []
    for code in codes:
        name = char_map.get(code, code)  # map'te yoksa kodu olduğu gibi kullan
        if name not in seen:
            seen.append(name)
    return seen


def parse_ref_file(filepath: Path) -> list[list[tuple[int, str]]]:
    """
    block_referans.txt'yi oku.
    Çıktı: chunk listesi. Her chunk, (seq_num, text) çiftlerinin listesi.
    Chunk'lar === satırlarıyla ayrılır.
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
            continue

        m = BLOCK_LINE_RE.match(line)
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
    char_map: dict[str, str],
) -> list[dict]:
    chunks = []

    for chunk_num, block_entries in enumerate(ref_chunks, start=1):
        if not block_entries:
            continue

        seq_nums = [s for s, _ in block_entries]

        first_block = blocks[seq_nums[0] - 1]
        last_block = blocks[seq_nums[-1] - 1]

        start_time = first_block['start']
        end_time = last_block['end']
        duration = round(time_to_seconds(end_time) - time_to_seconds(start_time), 1)

        text = ' '.join(t for _, t in block_entries if t).strip()
        characters = extract_characters(text, char_map)

        chunks.append({
            "id": f"yb_{chunk_num:03d}",
            "start": start_time,
            "end": end_time,
            "duration_sec": duration,
            "block_range": f"{seq_nums[0]:04d}-{seq_nums[-1]:04d}",
            "text": text,
            "characters": characters,
            "location": "",
            "scene_description": "",
            "humor_note": "",
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
    ref_file = PROJECT_ROOT / "notes" / "block_referans.md"
    blocks_file = PROJECT_ROOT / "data" / "processing" / "ham_chunks.json"
    char_file = PROJECT_ROOT / "notes" / "karakterler.txt"
    out_file = PROJECT_ROOT / "data" / "processing" / "base_chunks.json"

    blocks = json.loads(blocks_file.read_text(encoding='utf-8'))
    print(f"Ham block sayısı   : {len(blocks)}")

    char_map = load_char_map(char_file)
    print(f"Yüklenen karakter  : {len(char_map)}")

    ref_chunks = parse_ref_file(ref_file)
    print(f"Tespit edilen chunk: {len(ref_chunks)}")

    if not ref_chunks:
        print("❌ block_referans.txt'de henüz === ile ayrılmış chunk bulunamadı.")
        return

    covered = sum(len(c) for c in ref_chunks)
    uncovered = len(blocks) - covered
    print(f"Kapsanan block     : {covered} / {len(blocks)}")
    if uncovered > 0:
        print(f"⚠️  {uncovered} block hiçbir chunk'a dahil edilmemiş.")

    chunks = build_chunks(ref_chunks, blocks, char_map)
    print(f"\n✅ Oluşturulan chunk: {len(chunks)}")

    durations = [c['duration_sec'] for c in chunks]
    print(f"   Ortalama süre   : {sum(durations) / len(durations):.0f}s")
    print(f"   En kısa / uzun  : {min(durations):.0f}s  /  {max(durations):.0f}s")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 Kaydedildi: {out_file}")

    print("\n--- İlk 3 chunk:")
    for c in chunks[:3]:
        preview = c['text'][:100] + '...' if len(c['text']) > 100 else c['text']
        print(f"  [{c['id']}] {c['start']} → {c['end']} ({c['duration_sec']:.0f}s)")
        print(f"  Karakterler: {c['characters']}")
        print(f"  {preview}")
        print()


if __name__ == "__main__":
    main()
