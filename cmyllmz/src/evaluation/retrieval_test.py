"""
retrieval_test.py
-----------------
Retrieval precision ölçümü.

RAG sisteminin doğru chunk'ları getirip getirmediğini ölçer.
Metrik: ilgili_chunk_sayısı / toplam_getirilen_chunk_sayısı
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def evaluate_retrieval(questions: list[dict], top_k: int = 3) -> dict:
    """
    Her soru için getirilen chunk'ların ilgililiğini değerlendir.
    
    Returns:
        {"average_precision": float, "per_question": [...]}
    """
    # TODO: Implement
    pass


def main():
    print("⚠️  retrieval_test.py henüz implement edilmedi. Hafta 3'te doldurulacak.")


if __name__ == "__main__":
    main()
