"""
enricher.py
-----------
chunks.json'deki her chunk'ı OpenAI API'ye gönderir ve:
- characters: Chunk'taki konuşmacıları tahmin eder
- scene: Sahnenin kısa açıklaması
- context: Bağlam bilgisi
- tags: Etiketler (komedi, aksiyon vs.)

Kullanım:
  1. OPENAI_API_KEY ortam değişkenini ayarla:
     export OPENAI_API_KEY='sk-...'

  2. Çalıştır:
     source venv/bin/activate
     python scripts/enricher.py

Not: Hata durumunda kaldığı yerden devam eder (progress tracking).
     ~177 chunk × GPT-4o-mini ≈ $0.03 toplam maliyet.
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ openai kütüphanesi yüklü değil.")
    print("   Yüklemek için: pip install openai")
    sys.exit(1)


# ========== DOSYA YOLLARI ==========

BASE = Path(__file__).parent.parent
CHUNKS_FILE    = BASE / "data" / "filmler" / "yahsi_bati" / "processed" / "chunks.json"
OUTPUT_FILE    = BASE / "data" / "filmler" / "yahsi_bati" / "processed" / "enriched_chunks.json"
PROGRESS_FILE  = BASE / "data" / "filmler" / "yahsi_bati" / "processed" / ".enricher_progress.json"

# Kullanılacak model — hem ucuz hem yeterince zeki
MODEL = "gpt-4o-mini"
DELAY_BETWEEN_REQUESTS = 0.5  # saniye (rate limit için)


# ========== FİLM BİLGİSİ ==========

SYSTEM_PROMPT = """Sen "Yahşi Batı" (2010) filmini çok iyi bilen bir asistansın.
Verilen altyazı chunk'larını analiz edip JSON formatında yapılandırılmış bilgi üretirsin.

Film hakkında:
- Aziz Vefa: Teşkilât-ı Mahsusa ajanı. Ciddi, görev odaklı. (Cem Yılmaz)
- Lemi Galip: Hazine memuru. Korkak, komik, sakar. (Cem Yılmaz - çift rol)
- Suzan Van Dyke: Amerikalı kadın. (Demet Evgar)
- Johnny Lesh: Kötü adam, silahşor.
- Şerif Lloyd: Kasaba şerifi.
- Zeki Abi: Çerçeve hikayede hikayeyi anlatan kişi. (is_frame_story=true sahneler)
- Vedat Abi / Alpay Abi: Çerçeve hikayede dinleyenler.
- Sultan: Osmanlı Sultanı, filmin başında görevi veren.

Film yapısı: Çerçeve hikaye (günümüz, Zeki Abi anlatıyor) + Ana hikaye (1881 Vahşi Batı)."""

USER_PROMPT_TEMPLATE = """Aşağıdaki altyazı chunk'ını analiz et:

Chunk ID: {chunk_id}
Zaman: {start} → {end}
Çerçeve hikaye: {is_frame}
Türkçe metin: {text_tr}{en_part}

SADECE geçerli bir JSON döndür, başka hiçbir şey yazma:
{{
  "characters": ["konuşan karakter adları listesi"],
  "scene": "tek cümle sahne açıklaması",
  "context": "bu sahne hikayede ne ifade ediyor (1-2 cümle)",
  "tags": ["etiketler: komedi, aksiyon, romantik, çerçeve-hikaye, vs."]
}}

- characters: Sadece emin olduklarını yaz. Bilinmiyorsa boş liste.
- Çerçeve hikaye ise tags'e mutlaka "çerçeve-hikaye" ekle.
- scene kısa ve öz olsun: "Lemi posta arabasında özür diliyor" gibi."""


def setup_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY ortam değişkeni bulunamadı!")
        print('   Terminalde şunu çalıştır: export OPENAI_API_KEY="sk-..."')
        sys.exit(1)
    return OpenAI(api_key=api_key)


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text("utf-8"))
    return {}


def save_progress(progress: dict):
    PROGRESS_FILE.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def enrich_chunk(client: OpenAI, chunk: dict) -> dict:
    en_part = ""
    if chunk.get("text_en"):
        en_part = f"\nİngilizce metin: {chunk['text_en']}"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        chunk_id=chunk["id"],
        start=chunk["start"],
        end=chunk["end"],
        is_frame=chunk["is_frame_story"],
        text_tr=chunk["text_tr"],
        en_part=en_part,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,   # Düşük yaratıcılık → tutarlı çıktı
        max_tokens=300,
        response_format={"type": "json_object"},  # JSON garantisi
    )

    text = response.choices[0].message.content.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"  ⚠️ JSON parse hatası: {text[:200]}")
        return {"characters": [], "scene": "PARSE_HATASI", "context": text[:200], "tags": []}


def main():
    print("=" * 60)
    print("  Yahşi Batı — Chunk Enricher  |  model: " + MODEL)
    print("=" * 60)

    client = setup_client()

    chunks = json.loads(CHUNKS_FILE.read_text("utf-8"))
    print(f"Toplam chunk: {len(chunks)}")

    progress = load_progress()
    if progress:
        print(f"✅ Devam ediliyor — daha önce işlenen: {len(progress)} chunk")

    errors = 0
    for i, chunk in enumerate(chunks):
        chunk_id = chunk["id"]

        if chunk_id in progress:
            continue

        label = f"[{i+1}/{len(chunks)}] {chunk_id}  {chunk['start']}→{chunk['end']}"
        print(f"{label}...", end=" ", flush=True)

        try:
            result = enrich_chunk(client, chunk)
            progress[chunk_id] = result
            save_progress(progress)

            chars = ", ".join(result.get("characters", [])) or "—"
            scene = result.get("scene", "")[:50]
            print(f"✅  [{chars}]  {scene}")

        except Exception as e:
            errors += 1
            print(f"❌  {e}")
            if errors >= 5:
                print("\n⚠️  5 ardışık hata! Durdu. Tekrar çalıştırırsan kaldığı yerden devam eder.")
                break

        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Sonuçları chunk'larla birleştir
    enriched = []
    for chunk in chunks:
        c = dict(chunk)
        if chunk["id"] in progress:
            d = progress[chunk["id"]]
            c["characters"] = d.get("characters", [])
            c["scene"]      = d.get("scene", "")
            c["context"]    = d.get("context", "")
            c["tags"]       = d.get("tags", [])
        enriched.append(c)

    OUTPUT_FILE.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    done = sum(1 for c in enriched if c.get("scene"))
    print(f"\n{'='*60}")
    print(f"İşlenen: {done}/{len(chunks)}")
    print(f"Hata:    {errors}")
    print(f"💾 Kaydedildi: {OUTPUT_FILE}")
    if done == len(chunks):
        print("✅ Tüm chunk'lar zenginleştirildi! Film izleme rehberine geç.")


if __name__ == "__main__":
    main()
