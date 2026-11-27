#!/usr/bin/env python3
"""ローカル正本から、公開可能なメタデータJSON/Markdownを生成する。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def file_stem(exam: int, variant: str) -> str:
    return f"r{exam}" if variant == "standard" else f"r{exam}-{variant}"


def answer_status(question: dict) -> str:
    source = question.get("extraction", {}).get("answer")
    if source == "official-pdf-red-mark-candidate":
        return "official-pdf-candidate"
    if source == "kakomonn-commentary-candidate":
        return "kakomonn-html-candidate"
    return "unavailable"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()
    local_path = repo / "questions" / "past-exams" / "local" / "collection.json"
    data = json.loads(local_path.read_text(encoding="utf-8"))
    json_dir = repo / "questions" / "past-exams" / "json"
    md_dir = repo / "questions" / "past-exams" / "markdown"
    json_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)

    official = {(s["exam"], s["variant"]): s for s in data["officialSources"]}
    grouped: dict[tuple[int, str], list[dict]] = {}
    for question in data["questions"]:
        grouped.setdefault((question["exam"], question["variant"]), []).append(question)
    for key, questions in sorted(grouped.items()):
        exam, variant = key
        source = official[key]
        questions = sorted(questions, key=lambda item: item.get("number") or 999)
        public_questions = []
        for question in questions:
            public_questions.append({
                "id": question["id"],
                "number": question["number"],
                "subject": question.get("subject"),
                "correct": question.get("correct"),
                "answerStatus": answer_status(question),
                "textStatus": "available-locally" if question.get("question") else "official-pdf-image-only",
                "sourceUrl": question.get("sourceUrl"),
                "officialSourceUrl": question.get("officialSourceUrl") or source["url"],
            })
        payload = {
            "schemaVersion": 1,
            "publication": {
                "status": "metadata-only",
                "reason": "公式PDFと過去問サイトの問題本文・選択肢は、公開許諾を確認できるまでローカル管理する",
                "localCanonical": "questions/past-exams/local/collection.json",
            },
            "exam": {"number": exam, "variant": variant, "label": source["label"]},
            "sources": {"officialIndex": source["source_index"], "officialPdf": source["url"]},
            "questions": public_questions,
        }
        stem = file_stem(exam, variant)
        (json_dir / f"{stem}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lines = [
            f"# {source['label']}",
            "",
            "> 公開版は本文・選択肢を転載しないメタデータ版です。全文はローカル正本を参照してください。",
            "",
            f"- 公式PDF: {source['url']}",
            f"- 問題サイト一覧: {next((s['list_url'] for s in data['htmlSources'] if s['exam'] == exam and s['variant'] == variant), '掲載なし')}",
            f"- 問題数: {len(questions)}",
            "",
            "| 問題 | 科目 | 正答 | 正答情報 | 本文 | 出典 |",
            "|---:|---|---:|---|---|---|",
        ]
        for question in public_questions:
            source_link = question["sourceUrl"] or question["officialSourceUrl"]
            subject = question["subject"] or "未抽出"
            answer = str(question["correct"]) if question["correct"] is not None else "未取得"
            lines.append(f"| {question['number']} | {subject} | {answer} | {question['answerStatus']} | {question['textStatus']} | [{source_link}]({source_link}) |")
        (md_dir / f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"examFiles": len(grouped), "jsonDir": str(json_dir), "markdownDir": str(md_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

