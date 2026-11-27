#!/usr/bin/env python3
"""文化論及び理容技術理論の意味ベース知識分析を生成する。

問題本文・選択肢はローカルの collection.json の処理にだけ使い、分析JSONには
原文を保存しない。正答が取得できない問題は対象から除外し、coverage に残す。
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUBJECT = "文化論及び理容技術理論"
SUBJECT_SLUG = "culture-tech"
SOURCE_INDEXES = [
    "https://riyoushi.kakomonn.com/list",
    "https://www.rbc.or.jp/exam/past_question/",
]


# 選択肢そのものではなく、出題の意味領域を共通IDへ寄せるための語彙。
# 文言の完全一致を行わず、試験回をまたいだ論点の統合に使う。
KNOWLEDGE_DEFINITIONS: dict[str, tuple[str, str]] = {
    "history-fashion": ("服装・ファッション史", "明治以降の服装、ファッション文化、流行の時代区分を判定する知識"),
    "history-hairstyle": ("髪型の文化史", "明治以降の髪型・ヘアスタイルの流行時期や文化的背景を判定する知識"),
    "formal-wear": ("男性洋装礼装の区分", "モーニング、燕尾服、タキシード等の昼夜・正式略式の対応を判定する知識"),
    "head-landmarks": ("頭部・顔部の区分と名称", "頭部、顔部、頸部、手掌、眉部などの部位名称や基準線を識別する知識"),
    "nail-structure": ("爪の構造名称", "爪の各部位の名称と位置を識別する知識"),
    "blade-principles": ("理容刃物の切断原理と材料", "剪断・切断、刃の形状、鋼材、切削抵抗など刃物の原理を判定する知識"),
    "scissors": ("シザーズの形態と機能", "刃線、ひぞこ、鋏尖、鋏要、接点、裏面などシザーズの構造と働きを判定する知識"),
    "clipper": ("クリッパーの構造と機能", "上刃・下刃、歯、モーター式・マグネット式などクリッパーの構造と機能を判定する知識"),
    "comb": ("コームの形態と機能", "コーム各部の名称、歯の役割、カッティング時の機能を判定する知識"),
    "brush": ("ブラシの形態と用途", "セットに使うブラシの形態、名称、用途を識別する知識"),
    "work-posture": ("理容技術の姿勢", "技術者の位置、重心、手指、肘や肩の使い方など安全で効率的な作業姿勢を判定する知識"),
    "parting": ("分髪の基準と顔形への適用", "6:4、7:3、8:2等の分髪線の基準と顔形への適用を判定する知識"),
    "head-shape": ("頭の形とスタンダードヘアの補正", "平面・凸面・標準タイプ等の頭部形状に応じた高さ、分髪線、刈上げを判定する知識"),
    "standard-principles": ("スタンダードヘアの基本原則", "線とぼかし、毛髪の引出し、コームの運行、基礎刈など基本原則を判定する知識"),
    "standard-techniques": ("スタンダードヘアのカット技法", "押し刈、すくい刈、まわし刈、固定刈、指間刈等の用途・操作を判定する知識"),
    "design-cut": ("デザインヘアのカット技法", "ワンレングス、グラデーション、レイヤー、テーパー、ブラント等の技法と形状を判定する知識"),
    "hair-design": ("ヘアデザインの構成要素", "顔形、ヘアスタイルの構成要素、シルエットやデザインの関係を判定する知識"),
    "hair-setting": ("ヘアセッティングとアイロン操作", "ドライヤー・アイロンを用いたセットの種類、持ち方、操作方向を判定する知識"),
    "styling-products": ("整髪料の種類と作用", "整髪料の性質、固まり方、保持力、用途を判定する知識"),
    "winding": ("ワインディングのステムと角度", "ロング・ハーフ・ノンステム、ストランド角度、輪ゴム位置とボリュームの関係を判定する知識"),
    "permanent-wave": ("パーマネントウェーブの薬剤", "二浴式等のパーマ剤、中間酸リンス、薬剤の種類と作用を判定する知識"),
    "color-theory": ("色彩の三属性とマンセル表色系", "色相、明度、彩度、色相環、マンセル表色系など色彩の原理を判定する知識"),
    "hair-coloring": ("染毛・脱色の基本", "染毛剤、白髪染め、ブリーチ、脱染、施術前後の注意点を判定する知識"),
    "color-safety": ("染毛剤のパッチテスト", "酸化染毛剤等のパッチテストの目的、方法、判定時期、対象薬剤を判定する知識"),
    "razor-form": ("レザーの形態と持ち方", "レザー・替刃式レザーのホルダー、刃、プッシュハンド等の形態と持ち方を判定する知識"),
    "shaving-operation": ("シェービングの姿勢とレザー運行", "対皮角度、対皮圧力、斜行、運行方向、添え手、作業姿勢を判定する知識"),
    "shaving-lather": ("ラザーリング", "シェービング前のラザーリング剤の塗布、泡立ち、肌・毛への作用を判定する知識"),
    "women-shaving": ("レディースシェービング", "顔・襟足・うぶ毛など女性向けシェービングの部位別操作と注意点を判定する知識"),
    "facial-care": ("フェイシャルケアとスチームタオル", "スチーミング、てん包、スチームタオルの温度・覆い方などを判定する知識"),
    "shampoo": ("シャンプーイング", "シャンプー剤、洗浄、泡立ち、リンシング、スタンド・バック・リアの方法を判定する知識"),
    "massage": ("理容マッサージ", "ヘッドマッサージ、マニピュレーション、手技の順序と作用を判定する知識"),
    "hair-characteristics": ("毛髪・肌の性質", "毛髪の強度・水分・損傷、肌質など毛髪や皮膚の特徴を判定する知識"),
    "post-observation": ("事後観測", "技術後の状態を観測し、仕上がりや変化を確認するための知識"),
    "general-tools": ("理容用具の一般知識", "個別の器具分類に収まらない理容用具の名称・用途・取扱いを判定する知識"),
}


def source_key(exam: int, variant: str) -> str:
    return f"r{exam}-{variant}"


def question_scope(q: dict[str, Any]) -> bool:
    number = q.get("number")
    variant = q.get("variant")
    if not isinstance(number, int):
        return False
    if variant == "old":
        return 41 <= number <= 50
    return 41 <= number <= 55


def classify(stem: str, option: str) -> str:
    """問題の主題と選択肢から意味単位を推定する。

    画像選択肢や組合せ選択肢も、問題の主題に紐づく同一知識単位へ寄せる。
    """
    text = f"{stem} {option}"

    if "礼装" in text or any(word in text for word in ("モーニング", "燕尾服", "タキシード", "ホワイトタイ", "ブラックタイ", "ディレクターズスーツ")):
        return "formal-wear"
    if "服装" in text or "ファッション" in text:
        return "history-fashion"
    if any(word in text for word in ("大正", "明治", "昭和", "戦後", "戦前", "年代", "髪型", "ヘアスタイル", "流行", "チャン刈", "ビートルズ")):
        return "history-hairstyle"
    if "爪" in text:
        return "nail-structure"
    if "事後観測" in text:
        return "post-observation"
    if any(word in text for word in ("頭部の区分", "頭部と顔", "顔部", "頸部", "手掌", "眉毛", "イヤツーイヤ", "側面中心線", "側面正中線", "上段部", "中段部")):
        return "head-landmarks"
    if any(word in text for word in ("コバルト", "炭素鋼", "コンケーブ", "切削抵抗", "剪断", "切断", "刃の材料", "材料に関する")):
        return "blade-principles"
    if "シザーズ" in text or any(word in text for word in ("鋏身", "鋏体", "鋏尖", "鋏要", "ひぞこ", "刃線", "触点")):
        return "scissors"
    if "クリッパー" in text:
        return "clipper"
    if "コーム" in text or "櫛" in text:
        return "comb"
    if "ブラシ" in text:
        return "brush"
    if "レディースシェービング" in text:
        return "women-shaving"
    if "ラザーリング" in text:
        return "shaving-lather"
    if "替刃式レザー" in text or "替え刃式レザー" in text:
        return "razor-form" if any(word in text for word in ("形態", "持ち方", "ホルダー")) else "shaving-operation"
    if "レザー" in text and any(word in text for word in ("形態", "持ち方", "原理", "ホルダー", "プッシュハンド", "バックハンド")):
        return "razor-form"
    if "シェービング" in text or "レザーの運行" in text or "対皮" in text:
        return "shaving-operation"
    if "フェイシャル" in text or "スチームタオル" in text or "スチーミング" in text or "てん包" in text:
        return "facial-care"
    if "シャンプー" in text or "リンシング" in text:
        return "shampoo"
    if "マッサージ" in text:
        return "massage"
    if "肌の種類" in text or "毛髪" in text and any(word in text for word in ("水分", "弾力", "損傷", "強度")):
        return "hair-characteristics"
    if "パッチテスト" in text:
        return "color-safety"
    if any(word in text for word in ("染毛", "ヘアカラー", "白髪染め", "カラーリング", "ブリーチ", "脱色", "脱染")):
        return "hair-coloring"
    if any(word in text for word in ("マンセル", "色彩", "色相", "明度", "彩度", "色の三属性")):
        return "color-theory"
    if "ワインディング" in text or "ステム" in text or "ストランド" in text or "ピボットポイント" in text:
        return "winding"
    if "パーマネントウェーブ" in text or "パーマ剤" in text or "酸リンス" in text:
        return "permanent-wave"
    if "整髪料" in text:
        return "styling-products"
    if "アイロン" in text or "ヘアセッティング" in text or "ドライヤーセット" in text or "ヘアセット" in text:
        return "hair-setting"
    if "頭の形" in text or "平面タイプ" in text or "凸面タイプ" in text or "後頭部の形" in text:
        return "head-shape"
    if "分髪" in text:
        return "parting"
    if "デザインヘア" in text or "デザインカット" in text or any(word in text for word in ("ワンレングス", "グラデーションカット", "レイヤーカット", "テーパーカット", "ブラントカット", "スクエアカット")):
        return "design-cut"
    if "ヘアデザイン" in text or "顔とヘアスタイル" in text:
        return "hair-design"
    if "スタンダードヘア" in text or any(word in text for word in ("押し刈", "すくい刈", "まわし刈", "固定刈", "指間刈", "基礎刈", "直上線")):
        if any(word in text for word in ("押し刈", "すくい刈", "まわし刈", "固定刈", "指間刈", "技法")):
            return "standard-techniques"
        return "standard-principles"
    if "技術姿勢" in text or "作業姿勢" in text or "カッティングの姿勢" in text or "手指" in text:
        return "work-posture"
    if "理容用具" in text:
        return "general-tools"
    return "general-tools"


def load_collection(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo.resolve()
    collection_path = repo / "questions" / "past-exams" / "local" / "collection.json"
    output_path = repo / "questions" / "analysis" / "subjects" / "culture-tech.json"
    collection = load_collection(collection_path)
    questions = [q for q in collection.get("questions", []) if question_scope(q)]

    by_source: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    analyzed: list[dict[str, Any]] = []
    exclusions = Counter()
    all_source_keys = set()
    unanalysed_records: list[dict[str, Any]] = []

    for q in questions:
        exam = q.get("exam")
        variant = q.get("variant")
        if not isinstance(exam, int) or not isinstance(variant, str):
            exclusions["invalid_source_identity"] += 1
            continue
        exam_key = source_key(exam, variant)
        all_source_keys.add(exam_key)
        state = by_source.setdefault(
            exam_key,
            {
                "examKey": exam_key,
                "exam": exam,
                "variant": variant,
                "candidateRecordCount": 0,
                "structuredRecordCount": 0,
                "fourChoiceRecordCount": 0,
                "analyzedRecordCount": 0,
                "answerUnavailableRecordCount": 0,
                "pdfOnlyRecordCount": 0,
            },
        )
        state["candidateRecordCount"] += 1
        if not q.get("question"):
            state["pdfOnlyRecordCount"] += 1
            exclusions["pdf_only"] += 1
            unanalysed_records.append(
                {
                    "examKey": exam_key,
                    "examNumber": exam,
                    "questionNumber": q.get("number"),
                    "reason": "pdf-only",
                }
            )
            continue
        state["structuredRecordCount"] += 1
        choices = q.get("choices") or []
        if len(choices) != 4:
            exclusions["not_four_choices"] += 1
            unanalysed_records.append(
                {
                    "examKey": exam_key,
                    "examNumber": exam,
                    "questionNumber": q.get("number"),
                    "reason": "not-four-choices",
                }
            )
            continue
        state["fourChoiceRecordCount"] += 1
        correct = q.get("correct")
        if correct not in (1, 2, 3, 4):
            state["answerUnavailableRecordCount"] += 1
            exclusions["answer_unavailable"] += 1
            unanalysed_records.append(
                {
                    "examKey": exam_key,
                    "examNumber": exam,
                    "questionNumber": q.get("number"),
                    "reason": "answer-unavailable",
                }
            )
            continue
        state["analyzedRecordCount"] += 1
        analyzed.append(q)
        for choice_index, choice in enumerate(choices, start=1):
            key = classify(q.get("question", ""), choice or "")
            grouped[key].append(
                {
                    "examKey": exam_key,
                    "examNumber": exam,
                    "questionNumber": q.get("number"),
                    "choiceIndex": choice_index,
                    "polarity": "correct" if choice_index == correct else "incorrect",
                    "sourceUrl": q.get("sourceUrl") or q.get("officialSourceUrl"),
                    # 既存のランキング生成器との互換フィールド。
                    "exam": exam,
                    "variant": variant,
                    "number": q.get("number"),
                    "choice": choice_index,
                }
            )

    items = []
    for index, key in enumerate(sorted(grouped), start=1):
        refs = grouped[key]
        exam_count = len({ref["examKey"] for ref in refs})
        label, description = KNOWLEDGE_DEFINITIONS.get(key, KNOWLEDGE_DEFINITIONS["general-tools"])
        items.append(
            {
                "knowledgeId": f"{SUBJECT_SLUG}-k{index:03d}",
                "knowledgeLabel": label,
                "label": label,
                "description": description,
                "occurrenceCount": len(refs),
                "examCount": exam_count,
                "references": refs,
            }
        )

    source_order = sorted(
        by_source.values(),
        key=lambda item: (item["exam"], item["variant"]),
    )
    output = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "subjectSlug": SUBJECT_SLUG,
        "subject": SUBJECT,
        "questionNumberRange": {"newOrStandard": [41, 55], "old": [41, 50]},
        "method": {
            "unit": "問題文の文字列一致ではなく、正誤判定に必要な意味単位",
            "scope": "全試験回variantをスキャンし、文化・技術の問題番号範囲を対象化",
            "choiceCoverage": "正答が取得できた4択問題について、正答・誤答の全選択肢を1参照として分析",
            "integration": "同じ技術原理・器具機能・手順・文化知識に属する選択肢を共通knowledgeIdへ統合",
            "answerPolicy": "collection.jsonの取得済み正答候補のみ使用し、正答不明は推定しない",
            "textPolicy": "問題文・選択肢の原文はJSONへ保存しない",
        },
        "coverage": {
            "requestedExamRange": [24, 54],
            "scannedExamVariantCount": len(all_source_keys),
            "scannedExamVariants": [item["examKey"] for item in source_order],
            "candidateRecordCount": len(questions),
            "structuredRecordCount": sum(item["structuredRecordCount"] for item in source_order),
            "fourChoiceRecordCount": sum(item["fourChoiceRecordCount"] for item in source_order),
            "analyzedRecordCount": len(analyzed),
            "choiceReferenceCount": sum(len(refs) for refs in grouped.values()),
            "knowledgeItemCount": len(items),
            "excludedRecordCount": len(questions) - len(analyzed),
            "excludedByReason": dict(exclusions),
            "unanalysedRecords": sorted(
                unanalysed_records,
                key=lambda item: (item["examNumber"], item["examKey"], item["questionNumber"] or 0),
            ),
            "answerUnavailablePolicy": "正答候補がない構造化問題とPDF-only問題は、polarityを付けられないためknowledgeItemsから除外",
            "recordCountsByExamVariant": source_order,
            "sourceIndexes": SOURCE_INDEXES,
        },
        "knowledgeItems": items,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output_path),
                "candidateRecordCount": len(questions),
                "structuredRecordCount": len([q for q in questions if q.get("question")]),
                "analyzedRecordCount": len(analyzed),
                "choiceReferenceCount": sum(len(refs) for refs in grouped.values()),
                "knowledgeItemCount": len(items),
                "excludedByReason": dict(exclusions),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

