#!/usr/bin/env python3
"""公式PDFの正答印を画像から抽出し、ローカル収集JSONへ反映する。

公式PDFは画像PDFのため、本文抽出には使わず、赤い正答丸印の位置だけを
検出する。検出結果は必ず検証スクリプトで問題数・選択肢数と突き合わせる。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

from PIL import Image
import numpy as np
import pypdfium2 as pdfium


def red_mask_groups(image: Image.Image) -> list[tuple[int, int, int, int, float]]:
    array = np.asarray(image.convert("RGB"))
    red = array[:, : min(array.shape[1], 360), :]
    mask = (red[:, :, 0] >= 105) & (red[:, :, 0] - red[:, :, 1] >= 24) & (red[:, :, 0] - red[:, :, 2] >= 24) & (red[:, :, 0] >= red[:, :, 1] * 1.08)
    row_counts = mask.sum(axis=1)
    rows = {y: np.flatnonzero(mask[y]).tolist() for y in np.flatnonzero(row_counts >= 2)}
    groups: list[list[int]] = []
    for y in sorted(rows):
        if not groups or y - groups[-1][-1] > 5:
            groups.append([y])
        else:
            groups[-1].append(y)
    result: list[tuple[int, int, int, int, float]] = []
    for group in groups:
        points = [(x, y) for y in group for x in rows[y]]
        if not points:
            continue
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        area = len(points)
        if 8 <= xmax - xmin <= 110 and 8 <= ymax - ymin <= 110:
            result.append((xmin, xmax, ymin, ymax, float(area)))
    return result


def dark_row_groups(image: Image.Image, xmin: int = 220, xmax: int = 430) -> list[tuple[int, int]]:
    gray = np.asarray(image.convert("L"))
    width = gray.shape[1]
    left, right = min(width, xmin), min(width, xmax)
    row_counts = (gray[:, left:right] < 150).sum(axis=1)
    rows = np.flatnonzero(row_counts >= 2).tolist()
    groups: list[list[int]] = []
    for y in rows:
        if not groups or y - groups[-1][-1] > 4:
            groups.append([y])
        else:
            groups[-1].append(y)
    return [(group[0], group[-1]) for group in groups if group[-1] - group[0] >= 2]


def option_row_groups(image: Image.Image, anchor_x: int | None = None) -> list[tuple[int, int]]:
    """選択肢番号の行だけを拾う。

    問題文の折返し行は左側が連続した黒画素になりやすい一方、
    「(数字)」は左右に分かれた黒画素群になる。この差を利用する。
    """
    gray = np.asarray(image.convert("L"))
    anchor = 260 if anchor_x is None else anchor_x
    label_start = max(0, anchor + 3)
    label_end = label_start + 20
    candidates = dark_row_groups(image, xmin=max(0, anchor - 20), xmax=anchor + 180)
    result: list[tuple[int, int]] = []
    for start, end in candidates:
        occupied = []
        for x in range(label_start, label_end):
            occupied.append(bool((gray[start:end + 1, x] < 170).any()))
        runs = 0
        in_run = False
        for is_dark in occupied:
            if is_dark and not in_run:
                runs += 1
                in_run = True
            elif not is_dark:
                in_run = False
        if runs >= 2:
            result.append((start, end))
    return result


def nearest_line_index(mark_y: float, line_groups: list[tuple[int, int]]) -> int | None:
    candidates = []
    for index, (start, end) in enumerate(line_groups):
        center = (start + end) / 2
        distance = abs(center - mark_y)
        if distance <= max(14, (end - start) * 1.5):
            candidates.append((distance, index))
    return min(candidates)[1] if candidates else None


def estimate_answer_indices(image: Image.Image, marks: list[tuple[int, int, int, int, float]]) -> list[int | None]:
    """赤丸のY座標と本文左側の行群を照合する。

    PDFの選択肢番号は左側に縦に並ぶため、各赤丸を同じ行の候補へ割り当て、
    問題ごとに連続する4行（画像問題は可変行）として相対位置を求める。
    """
    line_groups = option_row_groups(image, min((mark[0] for mark in marks), default=260))
    centers = [(ymin + ymax) / 2 for _, _, ymin, ymax, _ in marks]
    answers: list[int | None] = []
    for center in centers:
        line_index = nearest_line_index(center, line_groups)
        if line_index is None:
            answers.append(None)
            continue
        # ページ内で選択肢番号は4行単位で繰り返される。
        answers.append((line_index % 4) + 1)
    return answers


def render_page(document: pdfium.PdfDocument, page_number: int, scale: float) -> Image.Image:
    page = document[page_number]
    bitmap = page.render(scale=scale, rotation=0, rev_byteorder=True)
    return bitmap.to_pil()


def derive_pdf(path: Path, expected_questions: int, debug: bool = False) -> tuple[list[int | None], dict]:
    document = pdfium.PdfDocument(str(path))
    marks: list[tuple[int, int, int, int, float, int]] = []
    for page_number in range(len(document)):
        image = render_page(document, page_number, 2.0)
        page_marks = red_mask_groups(image)
        answers = estimate_answer_indices(image, page_marks)
        if debug:
            lines = option_row_groups(image, min((mark[0] for mark in page_marks), default=260))
            mark_centers = [round((mark[2] + mark[3]) / 2, 1) for mark in page_marks]
            print(f"{path.name}: page={page_number + 1} marks={len(page_marks)} centers={mark_centers} answers={answers}")
            if page_marks:
                print(f"  dark-lines={lines}")
        for mark, answer in zip(page_marks, answers):
            marks.append((*mark, page_number + 1, answer if answer is not None else -1))
    values = [answer if answer > 0 else None for *_, answer in marks]
    info = {
        "pages": len(document),
        "redMarks": len(marks),
        "expectedQuestions": expected_questions,
        "answerCount": sum(value is not None for value in values),
        "status": "candidate" if len(marks) == expected_questions and all(values) else "needs-review",
    }
    return values, info


def expected_count(exam: int, variant: str) -> int:
    return 55 if exam >= 41 and variant != "old" else 50


def subject_for_number(exam: int, variant: str, number: int) -> str | None:
    if exam >= 41 and variant != "old":
        ranges = [
            (1, 10, "関係法規・制度及び運営管理"),
            (11, 15, "公衆衛生・環境衛生"), (16, 20, "感染症"),
            (21, 25, "衛生管理技術"), (26, 30, "人体の構造及び機能"),
            (31, 35, "皮膚科学"), (36, 40, "香粧品化学"),
            (41, 55, "文化論及び理容技術理論"),
        ]
    else:
        ranges = [
            (1, 10, "関係法規・制度"), (11, 15, "公衆衛生・環境衛生"),
            (16, 20, "感染症"), (21, 25, "衛生管理技術"),
            (26, 30, "人体の構造及び機能"), (31, 35, "皮膚科学"),
            (36, 40, "香粧品化学"), (41, 50, "文化論及び理容技術理論"),
        ]
    for start, end, subject in ranges:
        if start <= number <= end:
            return subject
    return None


def add_missing_question_records(data: dict) -> None:
    """公式資料に存在するがHTML一覧にない問題を空欄レコードで補う。"""
    by_key: dict[tuple[int, str], dict[int, dict]] = {}
    for question in data["questions"]:
        by_key.setdefault((question["exam"], question["variant"]), {})[question.get("number")] = question
    for source in data["officialSources"]:
        key = (source["exam"], source["variant"])
        records = by_key.setdefault(key, {})
        for number in range(1, expected_count(*key) + 1):
            if number in records:
                continue
            records[number] = {
                "id": f"r{source['exam']}-{source['variant']}-q{number:03d}",
                "exam": source["exam"], "variant": source["variant"], "number": number,
                "subject": subject_for_number(source["exam"], source["variant"], number),
                "question": None, "choices": [], "correct": None,
                "sourceUrl": None, "officialSourceUrl": source["url"], "imageUrls": [],
                "extraction": {"text": "official-pdf-image-only", "answer": "not-run"},
            }
    data["questions"] = [record for records in by_key.values() for record in records.values()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    local = repo / "questions" / "past-exams" / "local"
    collection_path = local / "collection.json"
    data = json.loads(collection_path.read_text(encoding="utf-8"))
    add_missing_question_records(data)
    by_key = {}
    for question in data["questions"]:
        by_key.setdefault((question["exam"], question["variant"]), []).append(question)

    report = {"schemaVersion": 1, "sources": {}, "errors": []}
    for source in data["officialSources"]:
        key = (source["exam"], source["variant"])
        questions = sorted(by_key.get(key, []), key=lambda item: item.get("number") or 999)
        pdf_path = local / "official-pdf" / source["filename"]
        if not pdf_path.exists():
            report["errors"].append({"key": key, "error": "pdf-not-found"})
            continue
        values, info = derive_pdf(pdf_path, expected_count(*key), args.debug)
        report["sources"][f"{source['exam']}-{source['variant']}"] = {"url": source["url"], **info}
        source["pdf_text_layer"] = False
        source["answer_verification"] = info["status"]
        if len(values) != len(questions):
            continue
        for question, answer in zip(questions, values):
            if answer is not None:
                question["correct"] = answer
                question["extraction"]["answer"] = "official-pdf-red-mark-candidate"

    data["questions"].sort(key=lambda item: (item["exam"], item["variant"], item.get("number") or 999))
    data["answerDerivation"] = report
    collection_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources": len(report["sources"]), "errors": report["errors"], "output": str(collection_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

