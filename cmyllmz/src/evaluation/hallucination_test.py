"""
hallucination_test.py
---------------------
Hallucination oranı ölçümü.

RAG'lı vs RAG'sız LLM cevaplarını karşılaştırarak
LLM'in ne kadar uydurma bilgi ürettiğini ölçer.

Metrik: uydurma_cevap_sayısı / toplam_soru_sayısı
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_test_questions() -> list[dict]:
    """Test sorularını yükle."""
    # TODO: Implement
    pass


def run_rag_test(questions: list[dict]) -> list[dict]:
    """Her soruyu RAG pipeline'ı üzerinden sor."""
    # TODO: Implement
    pass


def run_no_rag_test(questions: list[dict]) -> list[dict]:
    """Her soruyu doğrudan LLM'e sor (chunk vermeden)."""
    # TODO: Implement
    pass


def evaluate_responses(responses: list[dict]) -> dict:
    """
    Cevapları doğru/yanlış/uydurma olarak değerlendir.
    
    Returns:
        {"total": int, "correct": int, "wrong": int, "hallucinated": int, 
         "hallucination_rate": float}
    """
    # TODO: Implement
    pass


def main():
    print("⚠️  hallucination_test.py henüz implement edilmedi. Hafta 3'te doldurulacak.")


if __name__ == "__main__":
    main()
