"""
ner_extractor.py
----------------
Chunk'lardan Named Entity Recognition (NER) ile varlık çıkarma.

İki katmanlı sistem:
1. spaCy çok dilli modeli (xx_ent_wiki_sm) — genel PER, ORG, LOC, MISC
2. Türkçe regex pattern'leri — Osmanlıca/film-spesifik varlıklar

Çıktı: Her chunk'ın 'entities' alanını doldurur.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Türkçe/Osmanlıca'ya özel regex pattern'ler
TURKISH_PATTERNS = {
    "titles": [
        "Paşa", "Efendi", "Sultan", "Bey", "Abi", "Reis",
        "Şerif", "Peder", "Gardiyan",
    ],
    "orgs": [
        "Teşkilât-ı Mahsusa", "Hazine", "Konfederasyon",
    ],
    "historical_figures": [
        "Garfield",  # ABD Başkanı
        "Wellington",  # Çizme/Duke
    ],
}


def extract_entities_spacy(text: str) -> dict:
    """spaCy ile NER çalıştır."""
    # TODO: Implement
    # 1. spaCy modelini yükle (xx_ent_wiki_sm)
    # 2. text üzerinde NER çalıştır
    # 3. Bulunan entity'leri kategorize et (persons, locations, orgs, misc)
    pass


def extract_entities_regex(text: str) -> dict:
    """Türkçe regex pattern'leri ile ek varlık çıkarma."""
    # TODO: Implement
    # TURKISH_PATTERNS'deki kalıpları text'te ara
    pass


def extract_entities(text: str) -> dict:
    """İki katmanlı NER: spaCy + regex sonuçlarını birleştir."""
    # TODO: Implement
    # 1. spaCy sonuçlarını al
    # 2. Regex sonuçlarını al
    # 3. Birleştir ve deduplicate et
    # 4. {"persons": [...], "locations": [...], "orgs": [...], "misc": [...]} döndür
    pass


def main():
    """Tüm chunk'lar üzerinde NER çalıştır."""
    input_file = PROJECT_ROOT / "data" / "processing" / "annotated_chunks.json"
    output_file = PROJECT_ROOT / "data" / "processing" / "annotated_chunks_with_ner.json"

    # TODO: Implement
    print("⚠️  ner_extractor.py henüz implement edilmedi. Hafta 2'de doldurulacak.")


if __name__ == "__main__":
    main()
