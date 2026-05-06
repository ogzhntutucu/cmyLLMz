"""
retrieval_test.py
-----------------
Her soru için sistemin getirdiği chunk'ları ground truth ile karşılaştırır.

Metrik: Precision@k
    ilgili_ve_getirilen / toplam_getirilen

Çalıştırma:
    cd cmyllmz && python3 src/evaluation/retrieval_test.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

QUESTIONS_PATH = Path(__file__).parent.parent.parent / "data" / "eval" / "questions.json"
TOP_K = 5


def precision_at_k(retrieved: list[str], relevant: list[str]) -> float:
    if not retrieved:
        return 0.0
    hits = sum(1 for cid in retrieved if cid in relevant)
    return hits / len(retrieved)


def recall_at_k(retrieved: list[str], relevant: list[str]) -> float:
    if not relevant:
        return 1.0
    hits = sum(1 for cid in retrieved if cid in relevant)
    return hits / len(relevant)


def evaluate_retrieval(questions: list[dict], top_k: int = TOP_K) -> dict:
    from rag.retriever import retrieve

    per_question = []
    for q in questions:
        chunks = retrieve(q["question"], top_k=top_k)
        retrieved_ids = [c["id"] for c in chunks]
        relevant_ids = q["relevant_chunk_ids"]

        p = precision_at_k(retrieved_ids, relevant_ids)
        r = recall_at_k(retrieved_ids, relevant_ids)
        hit = any(cid in relevant_ids for cid in retrieved_ids)

        per_question.append({
            "id": q["id"],
            "type": q["type"],
            "question": q["question"],
            "relevant": relevant_ids,
            "retrieved": retrieved_ids,
            "precision": round(p, 3),
            "recall": round(r, 3),
            "hit": hit,
        })

    avg_precision = sum(x["precision"] for x in per_question) / len(per_question)
    avg_recall = sum(x["recall"] for x in per_question) / len(per_question)
    hit_rate = sum(x["hit"] for x in per_question) / len(per_question)

    # Tipe göre grupla
    by_type: dict[str, list] = {}
    for row in per_question:
        by_type.setdefault(row["type"], []).append(row)

    type_summary = {
        t: {
            "count": len(rows),
            "avg_precision": round(sum(r["precision"] for r in rows) / len(rows), 3),
            "hit_rate": round(sum(r["hit"] for r in rows) / len(rows), 3),
        }
        for t, rows in by_type.items()
    }

    return {
        "avg_precision": round(avg_precision, 3),
        "avg_recall": round(avg_recall, 3),
        "hit_rate": round(hit_rate, 3),
        "n_questions": len(per_question),
        "top_k": top_k,
        "by_type": type_summary,
        "per_question": per_question,
    }


def print_report(results: dict) -> None:
    print("\n" + "=" * 60)
    print("  RETRIEVAL TEST SONUÇLARI")
    print("=" * 60)
    print(f"  Soru sayısı : {results['n_questions']}")
    print(f"  Top-k       : {results['top_k']}")
    print(f"  Precision@k : {results['avg_precision']:.1%}")
    print(f"  Recall@k    : {results['avg_recall']:.1%}")
    print(f"  Hit rate    : {results['hit_rate']:.1%}  (en az 1 doğru chunk geldi mi?)")

    print("\n  Tipe göre:")
    for t, s in results["by_type"].items():
        print(f"    {t:12s}  precision={s['avg_precision']:.1%}  hit={s['hit_rate']:.1%}  (n={s['count']})")

    print("\n  Başarısız sorular (hit=False):")
    failures = [r for r in results["per_question"] if not r["hit"]]
    if not failures:
        print("    Yok — tüm sorularda en az 1 ilgili chunk bulundu.")
    else:
        for f in failures:
            print(f"    [{f['id']}] {f['question'][:60]}")
            print(f"          beklenen={f['relevant']}  gelen={f['retrieved'][:3]}")

    print("=" * 60 + "\n")


def main():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    print(f"{len(questions)} soru yüklendi. Retrieval başlıyor...")
    results = evaluate_retrieval(questions, top_k=TOP_K)

    out_path = QUESTIONS_PATH.parent / "results_retrieval.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"Sonuçlar kaydedildi → {out_path}")

    print_report(results)


if __name__ == "__main__":
    main()
