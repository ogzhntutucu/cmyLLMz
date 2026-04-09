"""
srt_parser.py
-------------
Yahşi Batı .srt dosyasını parse eder ve ham JSON'a çevirir.

Birleştirme stratejisi:
- Aynı zaman damgasında hem {\\a6} (İngilizce orijinal) hem Türkçe çeviri 
  bulunuyorsa: İngilizce orijinali kullan, Türkçe çeviriyi AT.
  Çünkü İngilizce orijinal sahnede gerçekten söylenen, Türkçe sadece altyazı çevirisi.
- Sadece Türkçe → doğrudan kullan (sahne zaten Türkçe).
- [EFEKT] notları → atla
- <i>...</i> tagları → sil, metni koru, is_frame_story: true
- Reklam satırları → atla
"""

import re
import json
from pathlib import Path
from collections import defaultdict


# Proje kök dizini (src/data_prep/ → iki seviye yukarı)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Atlanacak reklam/teknik satırlar
SKIP_PATTERNS = [
    re.compile(r'www\.\S+', re.IGNORECASE),
    re.compile(r'^eme[gğ]i\s+ge[cç]enler', re.IGNORECASE),
    re.compile(r'divxplanet', re.IGNORECASE),
]

# Efekt notları: [MÜZİK], [SİLAH SESİ] vs.
EFFECT_PATTERN = re.compile(r'^\s*\[.+\]\s*$')


def is_skip_line(text: str) -> bool:
    for p in SKIP_PATTERNS:
        if p.search(text):
            return True
    return False


def is_effect_only(text: str) -> bool:
    cleaned = re.sub(r'<[^>]+>', '', text).strip()
    return bool(EFFECT_PATTERN.match(cleaned))


def clean_html_tags(text: str) -> tuple[str, bool]:
    is_frame = '<i>' in text or '</i>' in text
    cleaned = re.sub(r'<[^>]+>', '', text).strip()
    return cleaned, is_frame


def parse_time(time_str: str) -> str:
    return time_str.split(',')[0].strip()


def parse_srt(filepath: Path) -> list[dict]:
    content = filepath.read_text(encoding='utf-8')
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    raw_blocks = re.split(r'\n\s*\n', content.strip())
    
    # 1. Adım: Tüm blokları parse et
    all_blocks = []
    for raw in raw_blocks:
        lines = [l.strip() for l in raw.strip().split('\n') if l.strip()]
        if len(lines) < 3:
            continue
        try:
            block_id = int(lines[0])
        except ValueError:
            continue
        
        time_line = lines[1]
        if '-->' not in time_line:
            continue
        
        start_raw, end_raw = time_line.split('-->')
        start = parse_time(start_raw.strip())
        end = parse_time(end_raw.strip())
        start_full = start_raw.strip()  # timestamp eşleştirme için
        
        text_lines = lines[2:]
        
        # {\a6} kontrolü
        is_en = any(l.startswith(r'{\a6}') for l in text_lines)
        
        # Metin satırlarını temizle
        cleaned_lines = []
        for line in text_lines:
            # {\a6} tag'ını sök
            if line.startswith(r'{\a6}'):
                line = line[5:]
            
            if is_skip_line(line):
                continue
            if is_effect_only(line):
                continue
            cleaned_lines.append(line)
        
        if not cleaned_lines:
            continue
        
        raw_text = ' '.join(cleaned_lines).strip()
        text, is_frame = clean_html_tags(raw_text)
        text = text.strip()
        
        # > - işaretleri
        text = re.sub(r'^[>]+\s*', '', text)
        text = re.sub(r'^<-\s*', '', text)
        
        if not text:
            continue
        
        all_blocks.append({
            "block_id": block_id,
            "start": start,
            "end": end,
            "start_full": start_full,
            "text": text,
            "is_en": is_en,
            "is_frame_story": is_frame,
            "raw_lines": lines[2:]
        })
    
    # 2. Adım: Aynı timestamp'teki EN+TR çiftlerini bul, TR çevirisini at
    by_timestamp = defaultdict(list)
    for b in all_blocks:
        by_timestamp[b["start_full"]].append(b)
    
    # TR çevirisi olup atılacak blok ID'lerini topla
    skip_ids = set()
    for ts, group in by_timestamp.items():
        if len(group) >= 2:
            en_blocks = [b for b in group if b["is_en"]]
            tr_blocks = [b for b in group if not b["is_en"]]
            if en_blocks and tr_blocks:
                # Aynı zamanda EN ve TR var → TR çevirisini at
                for tr in tr_blocks:
                    skip_ids.add(tr["block_id"])
    
    # 3. Adım: Sonuç listesini oluştur
    result = []
    for b in all_blocks:
        if b["block_id"] in skip_ids:
            continue
        result.append({
            "block_id": b["block_id"],
            "start": b["start"],
            "end": b["end"],
            "text": b["text"],
            "is_frame_story": b["is_frame_story"],
            "raw_lines": b["raw_lines"]
        })
    
    return result, len(skip_ids)


def main():
    srt_file = PROJECT_ROOT / "data" / "raw" / "yahsi_bati.srt"
    out_file = PROJECT_ROOT / "data" / "processing" / "ham_chunks.json"
    
    print(f"Okunuyor: {srt_file}")
    blocks, skipped = parse_srt(srt_file)
    
    print(f"✅ Parse edildi: {len(blocks)} blok")
    print(f"   ├─ Çeviri olarak atlanan TR blok: {skipped}")
    
    frame_story = sum(1 for b in blocks if b["is_frame_story"])
    print(f"   └─ Çerçeve hikaye (italik): {frame_story}")
    
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(blocks, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"💾 Kaydedildi: {out_file}")
    
    # Önizle
    print("\n--- İlk 5 blok:")
    for b in blocks[:5]:
        print(f"  [{b['start']} → {b['end']}]")
        print(f"  {b['text'][:100]}")
        print()
    
    # İngilizce içeren blok örnekleri
    en_examples = [b for b in blocks if any(c.isascii() and c.isalpha() for c in b['text']) 
                   and 'ottoman' in b['text'].lower() or 'village' in b['text'].lower() 
                   or 'garfield' in b['text'].lower()]
    if en_examples:
        print("--- İngilizce içeren blok örnekleri:")
        for b in en_examples[:3]:
            print(f"  [{b['start']}] {b['text'][:120]}")
            print()


if __name__ == "__main__":
    main()
