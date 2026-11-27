#!/usr/bin/env python3
"""科目別知識分析JSONを共通公開仕様へ機械的に正規化する。"""

from __future__ import annotations

import argparse
import json
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    subject_dir = args.repo.resolve() / "questions" / "analysis" / "subjects"
    changed = []
    for path in sorted(subject_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        slug = data.get("subjectSlug") or data.get("slug") or path.stem
        raw_subject = data.get("subject")
        if isinstance(raw_subject, dict):
            data["subject"] = raw_subject.get("name") or SUBJECT_NAMES.get(slug, slug)
        elif not isinstance(raw_subject, str) or not raw_subject.strip():
            data["subject"] = SUBJECT_NAMES.get(slug, slug)
        data["subjectSlug"] = slug
        for item in data.get("knowledgeItems") or []:
            if "knowledgeId" not in item and item.get("id"):
                item["knowledgeId"] = item.pop("id")
            if "description" not in item and item.get("meaning"):
                item["description"] = item.pop("meaning")
            refs = item.get("references") or []
            item["occurrenceCount"] = len(refs)
            item["examCount"] = len({(ref.get("exam"), ref.get("variant")) for ref in refs})
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed.append(path.name)
    print(json.dumps({"normalized": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

