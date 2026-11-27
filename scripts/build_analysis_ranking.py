#!/usr/bin/env python3
"""科目別知識分析JSONを検証し、全科目ランキングを生成する。"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


SUBJECT_NAMES = {
    "anatomy": "人体の構造及び機能",
    "public-health": "公衆衛生・環境衛生",
    "infection": "感染症",
    "sanitation": "衛生管理",
    "dermatology": "皮膚科学",
    "law": "関係法規・制度",
    "cosmetics": "整髪技術",
    "culture-tech": "文化論及び理容技術理論",
}


def normalise_subject(data: dict, path: Path) -> tuple[str, str]:
    raw = data.get("subject")
    if isinstance(raw, dict):
        subject = raw.get("name") or raw.get("slug") or path.stem
    elif isinstance(raw, str) and raw.strip():
        subject = raw
    else:
        subject = SUBJECT_NAMES.get(path.stem, data.get("slug") or path.stem)
    return data.get("subjectSlug") or data.get("slug") or path.stem, subject


def normalise_item(item: dict) -> dict:
    item = dict(item)
    if "knowledgeId" not in item and item.get("id"):
        item["knowledgeId"] = item["id"]
    if "description" not in item and item.get("meaning"):
        item["description"] = item["meaning"]
    return item


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()
    subject_dir = repo / "questions" / "analysis" / "subjects"
    files = sorted(subject_dir.glob("*.json"))
    all_items: list[dict] = []
    errors: list[str] = []
    subjects: list[dict] = []
    seen_ids: set[str] = set()
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        subject_slug, subject = normalise_subject(data, path)
        items = data.get("knowledgeItems") or []
        subjects.append({"slug": subject_slug, "subject": subject, "knowledgeItems": len(items), "coverage": data.get("coverage", {})})
        for item in items:
            item = normalise_item(item)
            knowledge_id = item.get("knowledgeId")
            refs = item.get("references") or []
            if not knowledge_id:
                errors.append(f"{path.name}: knowledgeId missing")
                continue
            for required in ("label", "description", "occurrenceCount", "examCount", "references"):
                if required not in item:
                    errors.append(f"{knowledge_id}: {required} missing")
            if knowledge_id in seen_ids:
                errors.append(f"duplicate knowledgeId: {knowledge_id}")
            seen_ids.add(knowledge_id)
            if item.get("occurrenceCount") != len(refs):
                errors.append(f"{knowledge_id}: occurrenceCount != references length")
            exams = {(ref.get("exam"), ref.get("variant")) for ref in refs}
            if item.get("examCount") != len(exams):
                errors.append(f"{knowledge_id}: examCount != unique exam references")
            for ref in refs:
                for required in ("exam", "variant", "number", "choice", "polarity", "sourceUrl"):
                    if required not in ref:
                        errors.append(f"{knowledge_id}: reference {required} missing")
                if ref.get("choice") not in (1, 2, 3, 4):
                    errors.append(f"{knowledge_id}: invalid choice")
                if ref.get("polarity") not in ("correct", "incorrect"):
                    errors.append(f"{knowledge_id}: invalid polarity")
                if not isinstance(ref.get("sourceUrl"), str) or not ref.get("sourceUrl", "").startswith(("http://", "https://")):
                    errors.append(f"{knowledge_id}: invalid sourceUrl")
                if "question" in ref or "choiceText" in ref or "choices" in ref:
                    errors.append(f"{knowledge_id}: source text must not be copied into public analysis")
            all_items.append({"subject": subject, **item})
    all_items.sort(key=lambda item: (-item.get("occurrenceCount", 0), -item.get("examCount", 0), item["subject"], item["knowledgeId"]))
    ranking = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": {
            "unit": "意味統合した知識命題",
            "occurrenceCount": "知識命題に紐づく選択肢の延べ出現数。正答・誤答を別の出典として数える",
            "examCount": "知識命題が出現した異なる試験回（variantを含む）の数",
            "ranking": "全知識項目をoccurrenceCount降順、examCount降順で並べる。科目別配分補正なし",
        },
        "coverage": {"subjectFiles": len(files), "knowledgeItems": len(all_items)},
        "subjects": subjects,
        "validation": {"valid": not errors, "errors": errors},
        "knowledgeItems": all_items,
    }
    output = repo / "questions" / "analysis" / "ranking.json"
    output.write_text(json.dumps(ranking, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"subjectFiles": len(files), "knowledgeItems": len(all_items), "errors": len(errors), "output": str(output)}, ensure_ascii=False))
    return 0 if files and not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

