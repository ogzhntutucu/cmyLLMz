"""
quality_test.py
---------------
Cevap kalitesi ölçümü — LLM-as-a-Judge yöntemiyle.

RAG'lı sistem vs düz LLM cevaplarını bir hakem LLM (Gemini) ile puanlar.
Kriterler: doğruluk, detay, tutarlılık (1-5 arası)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_quality_comparison(questions: list[dict]) -> dict:
    """
    Her soru için RAG'lı ve RAG'sız cevapları karşılaştır.
    
    Returns:
        {
            "rag_scores": {"dogruluk": float, "detay": float, "tutarlilik": float},
            "no_rag_scores": {"dogruluk": float, "detay": float, "tutarlilik": float},
            "per_question": [...]
        }
    """
    # TODO: Implement
    pass


def main():
    print("⚠️  quality_test.py henüz implement edilmedi. Hafta 3'te doldurulacak.")


if __name__ == "__main__":
    main()
