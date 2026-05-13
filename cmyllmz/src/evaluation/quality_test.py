"""
quality_test.py
---------------
RAG'lı sistem vs RAG'sız LLM cevaplarını Gemini ile karşılaştırır.
LLM-as-a-Judge: doğruluk, detay, tutarlılık (1-5 arası).

Çalıştırma:
    cd cmyllmz && python3 src/evaluation/quality_test.py

Not: GEMINI_API_KEY ortam değişkeni gerekli.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

QUESTIONS_PATH = Path(__file__).parent.parent.parent / "data" / "eval" / "questions.json"


def get_rag_answer(question: str) -> tuple[str, list[dict]]:
    """RAG pipeline'dan cevap al."""
    from rag.retriever import ask
    answer, chunks = ask(question, stream=False)
    return answer, chunks


def get_no_rag_answer(question: str) -> str:
    """Direkt LLM'e sor, chunk vermeden."""
    from llm.openai_client import chat
    from llm.prompt_templates import NO_RAG_SYSTEM_PROMPT
    return chat(NO_RAG_SYSTEM_PROMPT, question, stream=False)


JUDGE_MODEL = "gpt-5.4"


def judge_with_openai(question: str, ground_truth: str, answer_a: str, answer_b: str) -> dict:
    """OpenAI gpt-5.4 ile iki cevabı puanla."""
    from llm.openai_client import get_client
    from llm.prompt_templates import format_judge_prompt

    client = get_client()
    prompt = format_judge_prompt(question, ground_truth, answer_a, answer_b)

    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content.strip()

    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def run_quality_comparison(questions: list[dict], delay: float = 1.5) -> dict:
    """Her soru için RAG ve no-RAG cevaplarını karşılaştır."""
    per_question = []
    n = len(questions)

    for i, q in enumerate(questions, 1):
        print(f"  [{i}/{n}] {q['id']} — {q['question'][:50]}...")

        rag_answer, chunks = get_rag_answer(q["question"])
        no_rag_answer = get_no_rag_answer(q["question"])

        try:
            scores = judge_with_openai(
                q["question"], q["ground_truth"], rag_answer, no_rag_answer
            )
        except Exception as e:
            print(f"    ! Hakem hatası: {e}")
            scores = {
                "cevap_a": {"dogruluk": None, "detay": None, "tutarlilik": None},
                "cevap_b": {"dogruluk": None, "detay": None, "tutarlilik": None},
            }

        per_question.append({
            "id": q["id"],
            "type": q["type"],
            "question": q["question"],
            "ground_truth": q["ground_truth"],
            "rag_answer": rag_answer,
            "no_rag_answer": no_rag_answer,
            "retrieved_chunk_ids": [c["id"] for c in chunks],
            "scores": scores,
        })

        time.sleep(delay)

    return _summarize(per_question)


def _avg(values: list) -> float | None:
    clean = [v for v in values if v is not None]
    return round(sum(clean) / len(clean), 2) if clean else None


def _summarize(per_question: list[dict]) -> dict:
    rag_d = [r["scores"]["cevap_a"]["dogruluk"] for r in per_question]
    rag_de = [r["scores"]["cevap_a"]["detay"] for r in per_question]
    rag_t = [r["scores"]["cevap_a"]["tutarlilik"] for r in per_question]

    nr_d = [r["scores"]["cevap_b"]["dogruluk"] for r in per_question]
    nr_de = [r["scores"]["cevap_b"]["detay"] for r in per_question]
    nr_t = [r["scores"]["cevap_b"]["tutarlilik"] for r in per_question]

    return {
        "rag_scores": {
            "dogruluk": _avg(rag_d),
            "detay": _avg(rag_de),
            "tutarlilik": _avg(rag_t),
        },
        "no_rag_scores": {
            "dogruluk": _avg(nr_d),
            "detay": _avg(nr_de),
            "tutarlilik": _avg(nr_t),
        },
        "n_questions": len(per_question),
        "per_question": per_question,
    }


def print_report(results: dict) -> None:
    print("\n" + "=" * 60)
    print(f"  QUALITY TEST SONUÇLARI  (LLM-as-a-Judge / {JUDGE_MODEL})")
    print("=" * 60)
    print(f"  Soru sayısı: {results['n_questions']}")
    print()
    print(f"  {'Kriter':15s}  {'RAG':>6}  {'No-RAG':>8}  {'Fark':>6}")
    print(f"  {'-'*15}  {'-'*6}  {'-'*8}  {'-'*6}")
    for k in ["dogruluk", "detay", "tutarlilik"]:
        r = results["rag_scores"][k]
        n = results["no_rag_scores"][k]
        diff = round(r - n, 2) if (r and n) else None
        diff_str = f"+{diff}" if diff and diff > 0 else str(diff)
        print(f"  {k:15s}  {r or '-':>6}  {n or '-':>8}  {diff_str or '-':>6}")
    print("=" * 60 + "\n")


def main():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    print(f"{len(questions)} soru yüklendi. Quality testi başlıyor...")
    print("(Her soru: RAG cevabı + No-RAG cevabı + Gemini hakemi)\n")

    results = run_quality_comparison(questions)

    out_path = QUESTIONS_PATH.parent / "results_quality.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nSonuçlar kaydedildi → {out_path}")

    print_report(results)


if __name__ == "__main__":
    main()
