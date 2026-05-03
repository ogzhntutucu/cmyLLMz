"""
block_referans.md'deki [inline not] içlerindeki ASCII Türkçeye diakritik ekler.
Diyalog metni, timestamp'ler ve yapısal elementler (===, -XX-) dokunulmaz.
"""

import re
import json
import time
from openai import OpenAI

API_KEY = "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"
FILEPATH = "/home/thwisse/myDesktopL/computerScience/Programming/NLP/cmyllmz/notes/block_referans.md"
BATCH_SIZE = 20

BRACKET_RE = re.compile(r'\[([^\[\]]+)\]')
TIMESTAMP_RE = re.compile(r'^\d{2}:\d{2}:\d{2}$')

client = OpenAI(api_key=API_KEY)


def add_diacritics_batch(texts: list[str]) -> list[str]:
    prompt = (
        "Aşağıdaki JSON array'deki her Türkçe metne yalnızca eksik diakritik işaretleri ekle "
        "(ö, ü, ç, ş, ğ, ı). ÖNEMLI: array'deki eleman sayısı değişmemeli, sıra korunmalı. "
        "Başka hiçbir şeyi değiştirme. "
        f'Tam olarak {len(texts)} elemanlı {{"results": [...]}} döndür.\n\n'
        + json.dumps(texts, ensure_ascii=False)
    )
    for attempt in range(3):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        data = json.loads(response.choices[0].message.content)
        results = data.get("results") or list(data.values())[0]
        if len(results) == len(texts):
            return results
        print(f"    uyarı: {len(texts)} gönderildi, {len(results)} döndü — retry {attempt+1}/3")
        time.sleep(1)
    # fallback: birer birer gönder
    print("    fallback: tek tek işleniyor...")
    return [add_diacritics_batch([t])[0] for t in texts]


def main():
    with open(FILEPATH, encoding="utf-8") as f:
        content = f.read()

    all_matches = list(BRACKET_RE.finditer(content))
    note_matches = [(i, m) for i, m in enumerate(all_matches)
                    if not TIMESTAMP_RE.match(m.group(1).strip())]

    print(f"Toplam bracket: {len(all_matches)}, işlenecek: {len(note_matches)}")

    indices = [i for i, _ in note_matches]
    matches = [m for _, m in note_matches]
    texts = [m.group(1) for m in matches]

    corrected: list[str] = []
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
    for b in range(total_batches):
        batch = texts[b * BATCH_SIZE:(b + 1) * BATCH_SIZE]
        print(f"  Batch {b+1}/{total_batches} ({len(batch)} segment)...")
        corrected.extend(add_diacritics_batch(batch))
        if b < total_batches - 1:
            time.sleep(0.3)

    # Sondan başa doğru yerleştir (offset kayması olmasın)
    for match, fixed in zip(reversed(matches), reversed(corrected)):
        start, end = match.start(1), match.end(1)
        content = content[:start] + fixed + content[end:]

    with open(FILEPATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nTamamlandı. {len(corrected)} bracket güncellendi.")
    print("Şimdi VS Code'da 'git diff notes/block_referans.md' ile kontrol edin.")


if __name__ == "__main__":
    main()
