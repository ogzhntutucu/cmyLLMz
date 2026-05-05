"""
enricher.py
-----------
base_chunks.json'daki her chunk için Gemini API'ye istek göndererek
humor_analysis ve summary alanlarını doldurur.

Özellikler:
- Resume destekli: enriched_chunks.json varsa eksik chunk'ları bulur, sadece onları işler
- Her başarılı chunk'tan sonra dosyayı günceller (çökmede ilerleme kaybolmaz)
- Rate limiting: Gemini free tier için 4s bekleme (15 req/min altında kalır)
- Hata durumunda chunk atlanır, script devam eder

Kullanım:
    python src/data_prep/enricher.py
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent

GEMINI_API_KEY = "AIzaSyBjSi707S1KrxafoVAHnYUj4VV3H3lPPzk"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

RATE_LIMIT_SLEEP = 4.5  # saniye — free tier 15 req/min için güvenli marj

SYSTEM_PROMPT = """\
Sen Türk mizahı ve sinema konusunda uzman bir analistsin. \
Sana Cem Yılmaz'ın "Yahşi Batı" (2010) filminden bir sahne verilecek. \
Sahneyi mizah açısından analiz edip Türkçe yanıt vereceksin.

Verinin formatı hakkında bilgi:
- Köşeli parantez [içindekiler] izleyicinin aldığı sahne notlarıdır: görsel detaylar, \
kültürel bağlam, mizah mekanizması açıklamaları.
- -XX- etiketleri konuşmacı karakter kodlarıdır (-AZ- Aziz Vefa, -LE- Lemi Galip vb.).
- (bkz. yb_NNN) başka bir sahnede geçen ilgili bir olaya cross-reference'tır.
- Diyalog metni ve sahne notları iç içe geçmiş biçimdedir.

Kullanabileceğin mizah teknikleri (sadece bu listeden seç, birden fazla olabilir):
irony, sarcasm, wordplay, exaggeration, anachronism, cultural_reference,
slapstick, absurd, anecdote, character_contrast, breaking_fourth_wall,
callback, misunderstanding, deadpan, timing\
"""

CHUNK_PROMPT_TEMPLATE = """\
Sahne ID: {chunk_id}
Mekan: {location}
Karakterler: {characters}
{related_info}
--- Sahne metni (diyalog + sahne notları) ---
{text}
--- Sahne metni sonu ---

Yalnızca aşağıdaki JSON formatında yanıt ver, başka hiçbir şey yazma:

{{
  "humor_analysis": {{
    "techniques": ["liste", "şeklinde", "teknikler"],
    "why_funny": "Bu sahne neden komik? 2-3 cümle, Türkçe.",
    "cultural_context": "Bu sahneyi anlamak için gereken kültürel/tarihsel bağlam. Yoksa boş string.",
    "comedic_timing": "Zamanlama veya beklenmedik tepkilerin rolü. Yoksa boş string."
  }},
  "summary": "Sahnenin 1-2 cümlelik özeti, Türkçe."
}}\
"""


def call_gemini(prompt: str) -> dict:
    """Gemini API'ye istek at, parsed JSON döndür."""
    body = json.dumps({
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL, data=body,
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=60)
    data = json.loads(resp.read())
    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(raw_text)


def build_prompt(chunk: dict) -> str:
    chars = ", ".join(chunk.get("characters", [])) or "—"
    loc = chunk.get("location", "") or "—"

    related = chunk.get("related_chunks", [])
    related_info = (
        f"Bağlantılı sahneler: {', '.join(related)}\n"
        if related else ""
    )

    return CHUNK_PROMPT_TEMPLATE.format(
        chunk_id=chunk["id"],
        location=loc,
        characters=chars,
        related_info=related_info,
        text=chunk.get("text", ""),
    )


def main():
    input_file = PROJECT_ROOT / "data" / "processing" / "base_chunks.json"
    output_file = PROJECT_ROOT / "data" / "processing" / "enriched_chunks.json"

    chunks: list[dict] = json.loads(input_file.read_text(encoding="utf-8"))

    # Resume: çıktı dosyası varsa işlenmiş ID'leri bul
    if output_file.exists():
        done_chunks: list[dict] = json.loads(output_file.read_text(encoding="utf-8"))
        done_ids = {c["id"] for c in done_chunks}
        result_map = {c["id"]: c for c in done_chunks}
        print(f"Resume: {len(done_ids)} chunk zaten işlenmiş, devam ediliyor.")
    else:
        done_ids = set()
        result_map = {}

    pending = [c for c in chunks if c["id"] not in done_ids]
    print(f"İşlenecek chunk: {len(pending)} / {len(chunks)}")

    errors = []

    for i, chunk in enumerate(pending, 1):
        cid = chunk["id"]
        print(f"  [{i}/{len(pending)}] {cid} ({chunk.get('location', '—')})...", end=" ", flush=True)

        try:
            prompt = build_prompt(chunk)
            result = call_gemini(prompt)

            enriched = dict(chunk)
            enriched["humor_analysis"] = result.get("humor_analysis", chunk["humor_analysis"])
            enriched["summary"] = result.get("summary", "")

            result_map[cid] = enriched

            # Her chunk'tan sonra dosyayı güncelle
            ordered = [result_map[c["id"]] for c in chunks if c["id"] in result_map]
            output_file.write_text(
                json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            techniques = enriched["humor_analysis"].get("techniques", [])
            print(f"OK — {techniques}")

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"HATA (HTTP {e.code}): {body[:120]}")
            errors.append(cid)
        except Exception as e:
            print(f"HATA: {e}")
            errors.append(cid)

        if i < len(pending):
            time.sleep(RATE_LIMIT_SLEEP)

    total_done = len(result_map)
    print(f"\n✅ Tamamlandı: {total_done} / {len(chunks)} chunk zenginleştirildi.")
    if errors:
        print(f"⚠️  Atlanan chunk'lar ({len(errors)}): {errors}")
    print(f"💾 Kaydedildi: {output_file}")


if __name__ == "__main__":
    main()
