#!/usr/bin/env python3
"""過去問ローカル正本の構造・件数・参照整合性を検証する。"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def expected_count(exam: int, variant: str) -> int:
    return 55 if exam >= 41 and variant != "old" else 50


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()
    path = repo / "questions" / "past-exams" / "local" / "collection.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []
    questions = data.get("questions", [])
    keys = {(source["exam"], source["variant"]): source for source in data.get("officialSources", [])}
    if len(keys) != len(data.get("officialSources", [])):
        errors.append("officialSources に重複キーがあります")
    if len({question.get("id") for question in questions}) != len(questions):
        errors.append("問題IDが重複しています")

    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for question in questions:
        key = (question.get("exam"), question.get("variant"))
        grouped[key].append(question)
        if key not in keys:
            errors.append(f"公式資料にない問題キー: {key}")
        number = question.get("number")
        expected = expected_count(*key) if None not in key else 0
        if not isinstance(number, int) or not 1 <= number <= expected:
            errors.append(f"問題番号が範囲外: {question.get('id')}")
        choices = question.get("choices") or []
        if choices and len(choices) != 4:
            errors.append(f"選択肢数が4でない: {question.get('id')}")
        correct = question.get("correct")
        if correct is not None and correct not in (1, 2, 3, 4):
            errors.append(f"正答が1〜4でない: {question.get('id')}")
        if question.get("question") and not question.get("sourceUrl"):
            errors.append(f"本文に出典URLがありません: {question.get('id')}")

    for key, source in keys.items():
        records = grouped.get(key, [])
        expected = expected_count(*key)
        numbers = sorted(question.get("number") for question in records)
        if len(records) != expected or numbers != list(range(1, expected + 1)):
            errors.append(f"{key} の問題数または番号が不一致: {len(records)}/{expected}")
        if not source.get("url", "").lower().endswith(".pdf"):
            warnings.append(f"公式PDF URLを確認してください: {key}")

    full_text = sum(bool(q.get("question") and len(q.get("choices") or []) == 4) for q in questions)
    answered = sum(q.get("correct") in (1, 2, 3, 4) for q in questions)
    official_answer = sum(q.get("extraction", {}).get("answer") == "official-pdf-red-mark-candidate" for q in questions)
    html_answer = sum(q.get("extraction", {}).get("answer") == "kakomonn-commentary-candidate" for q in questions)
    report = {
        "schemaVersion": 1,
        "valid": not errors,
        "counts": {
            "officialSources": len(keys),
            "expectedQuestions": sum(expected_count(*key) for key in keys),
            "questions": len(questions),
            "fullHtmlStructured": full_text,
            "answered": answered,
            "officialPdfAnswerCandidates": official_answer,
            "kakomonnAnswerCandidates": html_answer,
            "textUnavailable": len(questions) - full_text,
        },
        "errors": errors,
        "warnings": warnings,
        "byExam": {
            f"{exam}-{variant}": {
                "count": len(records),
                "fullHtmlStructured": sum(bool(q.get("question") and len(q.get("choices") or []) == 4) for q in records),
                "answered": sum(q.get("correct") in (1, 2, 3, 4) for q in records),
                "missingAnswer": sum(q.get("correct") not in (1, 2, 3, 4) for q in records),
            }
            for (exam, variant), records in sorted(grouped.items())
        },
    }
    output = repo / "questions" / "past-exams" / "local" / "validation.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

