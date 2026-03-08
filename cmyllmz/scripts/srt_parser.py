"""
srt_parser.py
-------------
Yahşi Batı .srt dosyasını parse eder ve ham JSON'a çevirir.

Temizleme kuralları:
- {\a6} ile başlayan satırlar → İngilizce orijinal (text_en)
- Aynı zaman damgasındaki Türkçe satır → text_tr
- [EFEKT] notları (köşeli parantez) → tamamen atla
- <i>...</i> tagları → tag'ı sil, metni koru (is_frame_story: True)
- www.divxplanet.com, "Emeği geçenler:" gibi reklam satırları → atla
- \r\n → \n
- Çok kısa / anlamsız tek kelime blokları tutulur (repliklerin parçası olabilir)
"""

import re
import json
from pathlib import Path


# Atlanacak reklam/teknik satırlar için paternler
SKIP_PATTERNS = [
    re.compile(r'www\.\S+', re.IGNORECASE),
    re.compile(r'^eme[gğ]i\s+ge[cç]enler', re.IGNORECASE),
    re.compile(r'divxplanet', re.IGNORECASE),
]

# Efekt notları: [MÜZİK], [SİLAH SESİ] vs.
EFFECT_PATTERN = re.compile(r'^\s*\[.+\]\s*$')


def is_skip_line(text: str) -> bool:
    """Reklam/teknik satır mı?"""
    for pattern in SKIP_PATTERNS:
        if pattern.search(text):
            return True
    return False


def is_effect_only(text: str) -> bool:
    """Sadece [EFEKT] içeren satır mı?"""
    cleaned = re.sub(r'<[^>]+>', '', text).strip()
    return bool(EFFECT_PATTERN.match(cleaned))


def clean_html_tags(text: str) -> tuple[str, bool]:
    """
    <i> taglarını temizler. is_frame_story True ise çerçeve hikaye.
    Döndürür: (temiz metin, is_frame_story)
    """
    is_frame = '<i>' in text or '</i>' in text
    cleaned = re.sub(r'<[^>]+>', '', text).strip()
    return cleaned, is_frame


def parse_time(time_str: str) -> str:
    """'00:05:16,000' → '00:05:16'"""
    return time_str.split(',')[0].strip()


def parse_srt(filepath: Path) -> list[dict]:
    """
    .srt dosyasını parse eder. Döndürür:
    [
      {
        "block_id": int,
        "start": "00:05:16",
        "end": "00:05:23",
        "text_tr": "Türkçe metin",
        "text_en": "English text or null",
        "is_frame_story": bool,
        "raw_lines": [...]
      },
      ...
    ]
    """
    content = filepath.read_text(encoding='utf-8')
    
    # Windows satır sonlarını temizle
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Blokları boş satırla ayır
    raw_blocks = re.split(r'\n\s*\n', content.strip())
    
    parsed = []
    
    for raw in raw_blocks:
        lines = [l.strip() for l in raw.strip().split('\n') if l.strip()]
        if len(lines) < 3:
            continue
        
        # Satır 1: blok numarası
        try:
            block_id = int(lines[0])
        except ValueError:
            continue
        
        # Satır 2: zaman damgası
        time_line = lines[1]
        if '-->' not in time_line:
            continue
        
        start_raw, end_raw = time_line.split('-->')
        start = parse_time(start_raw.strip())
        end = parse_time(end_raw.strip())
        
        # Geri kalan satırlar: metin
        text_lines = lines[2:]
        
        # İngilizce ({\a6}) ve Türkçe satırları ayır
        en_lines = []
        tr_lines = []
        
        for line in text_lines:
            # {\a6} ile başlayan: İngilizce orijinal
            if line.startswith(r'{\a6}'):
                en_line = line[5:].strip()  # '{\a6}' = 5 karakter
                if not is_skip_line(en_line) and not is_effect_only(en_line):
                    en_lines.append(en_line)
            else:
                # Türkçe satır
                if is_skip_line(line):
                    continue
                if is_effect_only(line):
                    continue
                tr_lines.append(line)
        
        # Türkçe metin birleştir ve temizle
        tr_raw = ' '.join(tr_lines).strip()
        tr_text = ""
        is_frame = False
        
        if tr_raw:
            tr_text, is_frame = clean_html_tags(tr_raw)
            tr_text = tr_text.strip()
            # > - işaretleri (diyalog devamı işaretçileri)
            tr_text = re.sub(r'^[>]+\s*', '', tr_text)
            tr_text = re.sub(r'^<-\s*', '', tr_text)
        
        # İngilizce metin
        en_text = None
        if en_lines:
            en_joined = ' '.join(en_lines)
            en_cleaned, _ = clean_html_tags(en_joined)
            en_text = en_cleaned.strip() or None
        
        # Ne Türkçe ne İngilizce metin yoksa atla
        if not tr_text and not en_text:
            continue
        
        parsed.append({
            "block_id": block_id,
            "start": start,
            "end": end,
            "text_tr": tr_text,
            "text_en": en_text,
            "is_frame_story": is_frame,
            "raw_lines": text_lines
        })
    
    return parsed


def main():
    base = Path(__file__).parent.parent
    srt_file = base / "data" / "filmler" / "yahsi_bati" / "raw" / "yahsi_bati.srt"
    out_file = base / "data" / "filmler" / "yahsi_bati" / "processed" / "raw_subtitles.json"
    
    print(f"Okunuyor: {srt_file}")
    blocks = parse_srt(srt_file)
    
    print(f"✅ Parse edildi: {len(blocks)} blok")
    
    # İstatistikler
    with_en = sum(1 for b in blocks if b["text_en"])
    frame_story = sum(1 for b in blocks if b["is_frame_story"])
    print(f"   ├─ İngilizce çifti olan: {with_en}")
    print(f"   └─ Çerçeve hikaye (italik): {frame_story}")
    
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        json.dumps(blocks, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"💾 Kaydedildi: {out_file}")
    
    # İlk 3 bloğu önizle
    print("\n--- İlk 3 blok:")
    for b in blocks[:3]:
        print(f"  [{b['start']} → {b['end']}]")
        print(f"  TR: {b['text_tr']}")
        if b['text_en']:
            print(f"  EN: {b['text_en']}")
        print()


if __name__ == "__main__":
    main()
