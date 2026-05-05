"""
enricher.py
-----------
base_chunks.json'daki her chunk için OpenAI API'ye istek göndererek
humor_analysis ve summary alanlarını doldurur.

Özellikler:
- Resume destekli: enriched_chunks.json varsa eksik chunk'ları bulur, sadece onları işler
- Her başarılı chunk'tan sonra dosyayı günceller (çökmede ilerleme kaybolmaz)
- Hata durumunda chunk atlanır, script devam eder

Kullanım:
    python src/data_prep/enricher.py
"""

import json
import time
from pathlib import Path
from openai import OpenAI


PROJECT_ROOT = Path(__file__).parent.parent.parent

OPENAI_API_KEY = "ssk-proj-FkyQ0EVKnTPsYNAhngm2N_W30uIz80lYkZ0f8L9v1p_dJzY3Lr1YxCygv9I5fTq5HszyMeGQkVT3BlbkFJAI7hZ-ZSs2iZHiSqg9u4wPAwGB4R30WkMaQJKGun4eYfpbN4kgDi1W92HEHHr-fb6vEDWCKlgA"  # buraya OpenAI API key gir
OPENAI_MODEL = "gpt-4o-mini"

RATE_LIMIT_SLEEP = 1.0  # saniye

SYSTEM_PROMPT = """\
Yahşi Batı (2010) filminden sahne analizleri üretiyorsun. \
Görevin: her sahne için belirtilen JSON alanlarını doldur. \
Gözlem ve tespit yaz. Öznel yorum veya değerlendirme katma.

Metin formatı:
- [köşeli parantez içi] sahne notu (görsel detay, kültürel bağlam, izleyicinin aldığı not)
- -XX- konuşmacı karakter kodu (hangi kodun kim olduğu sana ayrıca verilir)
- (bkz. yb_NNN) başka bir sahneye çapraz referans

Kullanılabilecek mizah teknikleri (sadece bu listeden seç, birden fazla olabilir):
irony, sarcasm, wordplay, exaggeration, anachronism, cultural_reference,
slapstick, absurd, anecdote, character_contrast, breaking_fourth_wall,
callback, misunderstanding, deadpan, timing\
"""

CHUNK_PROMPT_TEMPLATE = """\
Sahne: {chunk_id}
Mekan: {location}
Karakterler:
{characters}
{related_info}
--- Metin ---
{text}
--- Son ---

Yalnızca aşağıdaki JSON formatında yanıt ver, başka hiçbir şey yazma:

{{
  "techniques": ["teknik1", "teknik2"],
  "mechanism": "Mizahın nasıl işlediği — kısa, analitik, Türkçe.",
  "cultural_context": "Sahneyi anlamak için gereken kültürel veya tarihsel bağlam. Yoksa boş string.",
  "summary": "Sahnenin 1-2 cümlelik özeti, Türkçe."
}}\
"""


def call_openai(client: OpenAI, prompt: str) -> dict:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def build_prompt(chunk: dict) -> str:
    chars = chunk.get("characters", {})
    if isinstance(chars, dict) and chars:
        chars_str = "\n".join(f"  {code}: {name}" for code, name in chars.items())
    else:
        chars_str = "  —"

    loc = chunk.get("location", "") or "—"

    related = chunk.get("related_chunks", [])
    related_info = (
        f"Bağlantılı sahneler: {', '.join(related)}\n"
        if related else ""
    )

    return CHUNK_PROMPT_TEMPLATE.format(
        chunk_id=chunk["id"],
        location=loc,
        characters=chars_str,
        related_info=related_info,
        text=chunk.get("text", ""),
    )


def main():
    input_file = PROJECT_ROOT / "data" / "processing" / "base_chunks.json"
    output_file = PROJECT_ROOT / "data" / "processing" / "enriched_chunks.json"

    chunks: list[dict] = json.loads(input_file.read_text(encoding="utf-8"))

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

    client = OpenAI(api_key=OPENAI_API_KEY)
    errors = []

    for i, chunk in enumerate(pending, 1):
        cid = chunk["id"]
        print(f"  [{i}/{len(pending)}] {cid} ({chunk.get('location', '—')})...", end=" ", flush=True)

        try:
            prompt = build_prompt(chunk)
            result = call_openai(client, prompt)

            enriched = dict(chunk)
            enriched["humor_analysis"] = {
                "techniques": result.get("techniques", []),
                "mechanism": result.get("mechanism", ""),
                "cultural_context": result.get("cultural_context", ""),
            }
            enriched["summary"] = result.get("summary", "")

            result_map[cid] = enriched

            ordered = [result_map[c["id"]] for c in chunks if c["id"] in result_map]
            output_file.write_text(
                json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            techniques = enriched["humor_analysis"].get("techniques", [])
            print(f"OK — {techniques}")

        except Exception as e:
            print(f"HATA: {e}")
            errors.append(cid)

        if i < len(pending):
            time.sleep(RATE_LIMIT_SLEEP)

    total_done = len(result_map)
    print(f"\nTamamlandı: {total_done} / {len(chunks)} chunk zenginleştirildi.")
    if errors:
        print(f"Atlanan chunk'lar ({len(errors)}): {errors}")
    print(f"Kaydedildi: {output_file}")


if __name__ == "__main__":
    main()
