#!/usr/bin/env python3
"""科目別知識分析JSONと統合ランキングを検証する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()
    subject_dir = repo / "questions" / "analysis" / "subjects"
    errors: list[str] = []
    seen_ids: set[str] = set()
    reference_count = 0
    item_count = 0
    for path in sorted(subject_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("schemaVersion", "subjectSlug", "subject", "method", "coverage", "knowledgeItems"):
            if key not in data:
                errors.append(f"{path.name}: top-level {key} missing")
        if not isinstance(data.get("subject"), str):
            errors.append(f"{path.name}: subject must be a string")
        for item in data.get("knowledgeItems") or []:
            item_count += 1
            knowledge_id = item.get("knowledgeId")
            if not knowledge_id:
                errors.append(f"{path.name}: knowledgeId missing")
                continue
            if knowledge_id in seen_ids:
                errors.append(f"duplicate knowledgeId: {knowledge_id}")
            seen_ids.add(knowledge_id)
            forbidden = {"question", "choices", "choiceText"}.intersection(item)
            if forbidden:
                errors.append(f"{knowledge_id}: raw item keys present: {sorted(forbidden)}")
            for key in ("label", "description", "occurrenceCount", "examCount", "references"):
                if key not in item:
                    errors.append(f"{knowledge_id}: {key} missing")
            refs = item.get("references") or []
            reference_count += len(refs)
            if item.get("occurrenceCount") != len(refs):
                errors.append(f"{knowledge_id}: occurrenceCount mismatch")
            variants = {(ref.get("exam"), ref.get("variant")) for ref in refs}
            if item.get("examCount") != len(variants):
                errors.append(f"{knowledge_id}: examCount mismatch")
            for ref in refs:
                forbidden = {"question", "choices", "choiceText"}.intersection(ref)
                if forbidden:
                    errors.append(f"{knowledge_id}: raw reference keys present: {sorted(forbidden)}")
                for key in ("exam", "variant", "number", "choice", "polarity", "sourceUrl"):
                    if key not in ref:
                        errors.append(f"{knowledge_id}: reference {key} missing")
                if ref.get("choice") not in (1, 2, 3, 4):
                    errors.append(f"{knowledge_id}: invalid choice")
                if ref.get("polarity") not in ("correct", "incorrect"):
                    errors.append(f"{knowledge_id}: invalid polarity")
                if not str(ref.get("sourceUrl", "")).startswith(("http://", "https://")):
                    errors.append(f"{knowledge_id}: invalid sourceUrl")
    ranking_path = repo / "questions" / "analysis" / "ranking.json"
    ranking = json.loads(ranking_path.read_text(encoding="utf-8")) if ranking_path.exists() else {}
    if ranking.get("validation", {}).get("valid") is not True:
        errors.append("ranking.json validation.valid is not true")
    result = {
        "valid": not errors,
        "subjectFiles": len(list(subject_dir.glob("*.json"))),
        "knowledgeItems": item_count,
        "references": reference_count,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

