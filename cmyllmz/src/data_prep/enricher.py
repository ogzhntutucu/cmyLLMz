"""
enricher.py
-----------
annotated_chunks.json dosyasını okur, her chunk için Gemini API'ye istek göndererek
humor_analysis ve summary alanlarını doldurur.

Çıktı: enriched_chunks.json

Özellikler:
- İlerleme takibi (.enricher_progress.json) ile yarıda kalan işleme devam edebilir
- Rate limiting (Gemini API kotasına uyum)
- Hata durumunda chunk atlanır, log tutulur
"""

import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Gemini'ye gönderilecek prompt şablonu
ENRICHMENT_PROMPT = """
Sen bir mizah analisti ve film eleştirmenisin. Sana Cem Yılmaz'ın "Yahşi Batı" filminden
bir sahne vereceğim. Bu sahneyi mizah açısından analiz etmeni istiyorum.

Sahne bilgileri:
- Karakterler: {characters}
- Mekan: {location}
- Sahne türü: {scene_type}
- İzleyici notu: {note}

Diyaloglar:
{text}

Lütfen aşağıdaki JSON formatında cevap ver (sadece JSON, başka bir şey yazma):

{{
  "humor_analysis": {{
    "techniques": ["kullanılan mizah teknikleri listesi"],
    "why_funny": "Bu sahne neden komik? 2-3 cümle ile açıkla.",
    "cultural_context": "Bu espriyi anlamak için hangi kültürel bilgiye ihtiyaç var?",
    "comedic_timing": "Zamanlamanın veya beklenmedik tepkilerin komikliğe etkisini açıkla."
  }},
  "summary": "Sahnenin 1-2 cümlelik kısa özeti."
}}
"""


def load_chunks(filepath: Path) -> list[dict]:
    """Chunk dosyasını yükle."""
    # TODO: Implement
    pass


def load_progress(progress_file: Path) -> set:
    """Daha önce işlenmiş chunk ID'lerini yükle."""
    # TODO: Implement
    pass


def save_progress(progress_file: Path, processed_ids: set):
    """İlerlemeyi kaydet."""
    # TODO: Implement
    pass


def enrich_chunk(chunk: dict) -> dict:
    """Tek bir chunk'ı Gemini API ile zenginleştir."""
    # TODO: Implement
    # 1. ENRICHMENT_PROMPT'u chunk verileriyle doldur
    # 2. Gemini API'ye gönder
    # 3. JSON cevabı parse et
    # 4. chunk'ın humor_analysis ve summary alanlarını güncelle
    # 5. Güncellenmiş chunk'ı döndür
    pass


def main():
    """Ana enrichment pipeline'ı."""
    input_file = PROJECT_ROOT / "data" / "processing" / "annotated_chunks.json"
    output_file = PROJECT_ROOT / "data" / "processing" / "enriched_chunks.json"
    progress_file = PROJECT_ROOT / "data" / "processing" / ".enricher_progress.json"

    # TODO: Implement
    # 1. annotated_chunks.json'u yükle
    # 2. İlerlemeyi kontrol et (daha önce işlenen chunk'ları atla)
    # 3. Her chunk için enrich_chunk() çağır
    # 4. Rate limiting uygula (Gemini API kotası)
    # 5. Her başarılı işlemden sonra ilerlemeyi kaydet
    # 6. enriched_chunks.json olarak kaydet
    print("⚠️  enricher.py henüz implement edilmedi. Hafta 2'de doldurulacak.")


if __name__ == "__main__":
    main()
