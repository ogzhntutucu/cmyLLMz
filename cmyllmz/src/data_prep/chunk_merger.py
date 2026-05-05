"""
chunk_merger.py
---------------
notes/block_referans.md dosyasını okur:
  - ===NNN=== sınırlarından chunk'ları ayırır
  - @lokasyon X directive'lerini chunk'ın location field'ına yazar
  - (bkz. yb_NNN) referanslarını related_chunks field'ına extract eder
  - -XX- karakter kodlarını characters field'ına çevirir
  - ham_chunks.json'dan timestamp bilgisini alır
Çıktılar:
  - data/processing/base_chunks.json
  - notes/chunk_index.md (kullanıcı referans tablosu)

Beklenen block_referans.md formatı:
    ===001===
    @lokasyon beykoz meyhanesi
    0001 [00:00:14] [rakı masasında oturuyorlar] -AL- Şimdi kadın...
    0002 [00:00:20] -RA- Ustaya bak! [bkz. yb_005]
    ===002===
    @lokasyon Dolmabahçe Sarayı
    0003 [00:00:25] -AZ- Selam.
    ...

Kullanım:
    python src/data_prep/chunk_merger.py
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent

CHAR_CODE_RE = re.compile(r'-([A-Z][A-Z0-9]{0,2})-')
BLOCK_LINE_RE = re.compile(r'^(\d{4})\s+\[\d{2}:\d{2}:\d{2}\]\s*(.*)')
LOKASYON_RE = re.compile(r'^@lokasyon\s+(.+)$', re.IGNORECASE)
BKZ_RE = re.compile(r'bkz\.\s*(yb_\d{3})', re.IGNORECASE)
CHUNK_HEADER_RE = re.compile(r'^===\d+===$')


@dataclass
class RefChunk:
    blocks: list[tuple[int, str]] = field(default_factory=list)
    location: str = ""


def time_to_seconds(t: str) -> float:
    parts = t.split(':')
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2].replace(',', '.'))
    return h * 3600 + m * 60 + s


def load_char_map(filepath: Path) -> dict[str, str]:
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


def extract_characters(text: str, char_map: dict[str, str]) -> dict[str, str]:
    codes = CHAR_CODE_RE.findall(text)
    seen: dict[str, str] = {}
    for code in codes:
        if code not in seen:
            seen[code] = char_map.get(code, code)
    return seen


def extract_related_chunks(text: str, self_id: str) -> list[str]:
    """Metindeki (bkz. yb_NNN) referanslarını çıkar, dedupe et, sırala."""
    refs = BKZ_RE.findall(text)
    unique = sorted(set(r.lower() for r in refs))
    return [r for r in unique if r != self_id]


def parse_ref_file(filepath: Path) -> list[RefChunk]:
    """
    block_referans.md'yi oku.
    ===NNN=== ile chunk açılır.
    @lokasyon X bir sonraki satırlarda gelirse chunk.location'a yazılır.
    NNNN [HH:MM:SS] satırları block olarak eklenir.
    """
    chunks: list[RefChunk] = []
    current: RefChunk | None = None

    for line in filepath.read_text(encoding='utf-8').splitlines():
        line = line.rstrip()

        if CHUNK_HEADER_RE.match(line):
            if current is not None:
                chunks.append(current)
            current = RefChunk()
            continue

        if current is None:
            continue

        loc_match = LOKASYON_RE.match(line.strip())
        if loc_match:
            current.location = loc_match.group(1).strip()
            continue

        if line.startswith('---') or not line.strip():
            continue

        m = BLOCK_LINE_RE.match(line)
        if m:
            seq_num = int(m.group(1))
            text = m.group(2).strip()
            current.blocks.append((seq_num, text))

    if current is not None:
        chunks.append(current)

    return chunks


def build_chunks(
    ref_chunks: list[RefChunk],
    blocks: list[dict],
    char_map: dict[str, str],
) -> list[dict]:
    chunks = []

    for chunk_num, ref in enumerate(ref_chunks, start=1):
        if not ref.blocks:
            continue

        seq_nums = [s for s, _ in ref.blocks]
        first_block = blocks[seq_nums[0] - 1]
        last_block = blocks[seq_nums[-1] - 1]

        start_time = first_block['start']
        end_time = last_block['end']
        duration = round(time_to_seconds(end_time) - time_to_seconds(start_time), 1)

        text = ' '.join(t for _, t in ref.blocks if t).strip()
        characters = extract_characters(text, char_map)
        chunk_id = f"yb_{chunk_num:03d}"
        related = extract_related_chunks(text, chunk_id)

        chunks.append({
            "id": chunk_id,
            "start": start_time,
            "end": end_time,
            "duration_sec": duration,
            "block_range": f"{seq_nums[0]:04d}-{seq_nums[-1]:04d}",
            "text": text,
            "characters": characters,
            "location": ref.location,
            "related_chunks": related,
            "humor_analysis": {
                "techniques": [],
                "mechanism": "",
                "cultural_context": ""
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


def write_chunk_index(chunks: list[dict], out_file: Path) -> None:
    """notes/chunk_index.md üret: kullanıcı/RAG için referans tablosu."""
    lines = [
        '# Chunk Index\n',
        f'Toplam: {len(chunks)} chunk\n\n',
        '| ID | Süre | s | Lokasyon | İlk 100 karakter |\n',
        '|---|---|---|---|---|\n',
    ]
    for c in chunks:
        preview = c['text'][:100].replace('\n', ' ').replace('|', '/')
        loc = c.get('location', '') or '—'
        lines.append(
            f"| {c['id']} | {c['start']}→{c['end']} | {int(c['duration_sec'])}s "
            f"| {loc} | {preview} |\n"
        )
    out_file.write_text(''.join(lines), encoding='utf-8')


def main():
    ref_file = PROJECT_ROOT / "notes" / "block_referans.md"
    blocks_file = PROJECT_ROOT / "data" / "processing" / "ham_chunks.json"
    char_file = PROJECT_ROOT / "notes" / "karakterler.txt"
    out_file = PROJECT_ROOT / "data" / "processing" / "base_chunks.json"
    index_file = PROJECT_ROOT / "notes" / "chunk_index.md"

    blocks = json.loads(blocks_file.read_text(encoding='utf-8'))
    print(f"Ham block sayısı   : {len(blocks)}")

    char_map = load_char_map(char_file)
    print(f"Yüklenen karakter  : {len(char_map)}")

    ref_chunks = parse_ref_file(ref_file)
    print(f"Tespit edilen chunk: {len(ref_chunks)}")

    if not ref_chunks:
        print("❌ block_referans.md'de === ile ayrılmış chunk bulunamadı.")
        return

    covered = sum(len(c.blocks) for c in ref_chunks)
    uncovered = len(blocks) - covered
    print(f"Kapsanan block     : {covered} / {len(blocks)}")
    if uncovered > 0:
        print(f"⚠️  {uncovered} block hiçbir chunk'a dahil edilmemiş.")

    chunks = build_chunks(ref_chunks, blocks, char_map)
    print(f"\n✅ Oluşturulan chunk: {len(chunks)}")

    durations = [c['duration_sec'] for c in chunks]
    print(f"   Ortalama süre   : {sum(durations) / len(durations):.0f}s")
    print(f"   En kısa / uzun  : {min(durations):.0f}s  /  {max(durations):.0f}s")

    with_loc = sum(1 for c in chunks if c['location'])
    with_refs = sum(1 for c in chunks if c['related_chunks'])
    total_refs = sum(len(c['related_chunks']) for c in chunks)
    print(f"   Lokasyonlu      : {with_loc} / {len(chunks)}")
    print(f"   Cross-ref olan  : {with_refs} chunk, toplam {total_refs} referans")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 base_chunks.json: {out_file}")

    write_chunk_index(chunks, index_file)
    print(f"💾 chunk_index.md  : {index_file}")

    print("\n--- İlk 3 chunk:")
    for c in chunks[:3]:
        preview = c['text'][:100] + '...' if len(c['text']) > 100 else c['text']
        print(f"  [{c['id']}] {c['start']} → {c['end']} ({c['duration_sec']:.0f}s) "
              f"@{c['location']}")
        print(f"  Karakterler: {c['characters']}")
        if c['related_chunks']:
            print(f"  → bağlı: {c['related_chunks']}")
        print(f"  {preview}")
        print()


if __name__ == "__main__":
    main()
