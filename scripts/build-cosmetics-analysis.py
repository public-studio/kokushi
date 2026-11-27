#!/usr/bin/env python3
"""整髪（香粧品化学・旧理容の物理・化学）の意味ベース分析を生成する。"""

from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "questions" / "past-exams" / "local" / "collection.json"
OUTPUT = ROOT / "questions" / "analysis" / "subjects" / "cosmetics.json"
HTML_QUESTIONS = ROOT / "questions" / "past-exams" / "local" / "html" / "questions"

TARGET_SUBJECTS = {"香粧品化学", "（旧）理容の物理・化学"}


# 旧制度の問31〜40と新制度の問36〜40について、問題の意味から解決できる正答。
# collection.json の正答候補がある場合は、収集済み候補を優先し、差異はcoverageに記録する。
MANUAL_ANSWER_RANGES: dict[str, tuple[int, list[int]]] = {
    "27-standard": (31, [3, 2, 2, 3, 4, 1, 2, 4, 3, 1]),
    "28-standard": (31, [2, 1, 3, 4, 4, 1, 2, 1, 3, 3]),
    "29-standard": (31, [3, 4, 1, 1, 3, 3, 2, 3, 1, 4]),
    "30-standard": (31, [3, 4, 2, 1, 3, 1, 1, 1, 2, 2]),
    "31-standard": (31, [3, 2, 1, 2, 3, 1, 4, 4, 4, 2]),
    "32-standard": (31, [2, 2, 4, 3, 3, 4, 4, 1, 2, 1]),
    "33-standard": (31, [4, 2, 4, 2, 3, 1, 3, 2, 2, 4]),
    "34-standard": (31, [4, 2, 4, 3, 1, 1, 3, 4, 4, 2]),
    "35-standard": (31, [2, 1, 2, 4, 3, 3, 4, 1, 4, 4]),
    "36-standard": (31, [2, 3, 2, 4, 2, 4, 2, 1, 3, 2]),
    "37-standard": (31, [2, 3, 2, 4, 4, 3, 4, 2, 4, 4]),
    "38-standard": (31, [1, 1, 4, 3, 2, 4, 2, 3, 4, 1]),
    "39-standard": (31, [4, 3, 2, 4, 2, 3, 3, 1, 4, 1]),
    "40-standard": (31, [4, 3, 1, 4, 2, 3, 1, 3, 3, 2]),
    "41-old": (31, [3, 2, 3, 1, 3, 4, 2, 3, 3, 2]),
    "41-new": (36, [4, 2, 3, 3, 2]),
    "42-new": (36, [4, 1, 4, 3, 4]),
    "42-old": (36, [4, 1, 4, 3, 4]),
    "43-new": (36, [3, 2, 1, 4, 4]),
    "43-old": (36, [3, 2, 1, 4, 4]),
    "44-standard": (36, [1, 2, 2, 1, 3]),
    "45-standard": (36, [3, 4, 1, 2, 4]),
    "46-standard": (36, [4, 4, 3, 1, 2]),
    "47-standard": (36, [4, 4, 3, 1, 3]),
    "48-standard": (36, [2, 3, 3, 2, 4]),
    "49-standard": (36, [4, 3, 2, 1, 3]),
    "50-standard": (36, [2, 4, 3, 3, 1]),
    "51-standard": (36, [3, 1, 3, 2, 2]),
    "52-standard": (36, [1, 3, 4, 3, 4]),
    "53-standard": (36, [4, 2, 1, 2, 3]),
    "54-standard": (36, [4, 1, 2, 2, 4]),
}


KNOWLEDGE_DEFS = {
    "cosmetics-k001": ("理美容器具の力学", "てこ・くさび・せん断・応力など、器具が毛髪や物体を切断・変形させるときの力学的関係。"),
    "cosmetics-k002": ("熱・温度・物質の状態変化", "比熱、温度、沸騰・融解・凝縮・昇華、対流など、熱と物質の状態変化の関係。"),
    "cosmetics-k003": ("電気・電流・電気器具", "電流・電圧・抵抗・電力・電力量、交流、漏電や電気器具の作用に関する知識。"),
    "cosmetics-k004": ("光・紫外線・赤外線", "電磁波の波長・作用、紫外線と赤外線の生体作用、殺菌・美容・サンケアへの利用。"),
    "cosmetics-k005": ("物質の構成", "原子・元素・単体・化合物・混合物の区別と、原子核・電子などの構造。"),
    "cosmetics-k006": ("溶液・溶媒・溶質・水和", "溶液を構成する溶媒・溶質、水和、極性など、物質が溶ける仕組み。"),
    "cosmetics-k007": ("酸・塩基・pH・指示薬", "酸性・塩基性の強弱、pH、リトマス紙・フェノールフタレイン、有機酸・無機酸の区別。"),
    "cosmetics-k008": ("有機化合物・アルコール", "炭化水素、アルコール、有機酸、油脂などの分類と、エタノール等の香粧品用途。"),
    "cosmetics-k009": ("硬水・軟水", "カルシウム・マグネシウム、硬度、一時硬水・永久硬水、石けんの泡立ちとの関係。"),
    "cosmetics-k010": ("化学結合", "共有結合・イオン結合・水素結合などの性質と、毛髪・香粧品中での結合の意味。"),
    "cosmetics-k011": ("高分子・タンパク質", "天然・半合成・合成高分子、タンパク質の分類、構成単位、ケラチン等の性質。"),
    "cosmetics-k012": ("金属・合金・さび", "金属の熱・電気的性質、合金、刃物材料、酸化によるさびと防錆。"),
    "cosmetics-k013": ("単位・物理量・計算", "長さ・力・熱量・電圧などの単位と、電力・電力量・温度の基本計算。"),
    "cosmetics-k014": ("油脂・ロウ・炭化水素・シリコーン", "油脂・高級アルコール・高級脂肪酸・ロウ・炭化水素・シリコーン油の分類と用途。"),
    "cosmetics-k015": ("色材・顔料・色素", "無機顔料・天然色素・タール色素・光輝性顔料の分類、性質、規制、香粧品用途。"),
    "cosmetics-k016": ("界面活性剤の種類と性質", "陰イオン・陽イオン・両性・非イオン界面活性剤の電荷、代表成分、用途、刺激性。"),
    "cosmetics-k017": ("界面活性剤の作用", "臨界ミセル濃度、ミセル、洗浄・乳化・可溶化・分散、O/W・W/O型の意味。"),
    "cosmetics-k018": ("石けん・洗浄剤", "油脂のけん化、石けんの製法・性質、シャンプー等の洗浄剤との関係。"),
    "cosmetics-k019": ("香粧品成分の配合目的", "防腐・酸化防止・金属イオン封鎖・紫外線吸収・収れん・保湿などの成分機能。"),
    "cosmetics-k020": ("香粧品の機能性原料", "保湿・エモリエント・美白・収れん・清涼など、代表的な機能性原料と効果。"),
    "cosmetics-k021": ("頭皮・毛髪用製品", "シャンプー、リンス、スタイリング剤、エアゾール、育毛剤などの成分と製品機能。"),
    "cosmetics-k022": ("芳香製品・香料", "香水・オーデコロン等の香料濃度と、香りの発散・持続に関する知識。"),
    "cosmetics-k023": ("パーマ剤の還元・酸化機序", "第1剤の還元剤・アルカリ剤、第2剤の酸化剤、シスチン結合の切断・再結合。"),
    "cosmetics-k024": ("染毛・脱色の分類と機序", "一時・半永久・永久染毛、酸性染毛料、酸化染毛剤、脱色剤の染着・脱色機序。"),
    "cosmetics-k025": ("染毛剤の成分と役割", "染料中間体、カップラー、過酸化水素、アンモニア、レゾルシン等の役割。"),
    "cosmetics-k026": ("染毛時の安全・法規", "酸化染毛剤の医薬部外品区分、パッチテスト、使用上の安全管理。"),
}


def exam_key(q: dict) -> str:
    return f"{q['exam']}-{q['variant']}"


def manual_answer(key: str, number: int) -> int | None:
    start, values = MANUAL_ANSWER_RANGES.get(key, (0, []))
    offset = number - start
    if 0 <= offset < len(values):
        return values[offset]
    return None


def html_answer(q: dict) -> int | None:
    """キャッシュ済みHTMLの解説中の正答を読む（原文はJSONへ出力しない）。"""
    source_url = q.get("sourceUrl") or ""
    match = re.search(r"/questions/(\d+)", source_url)
    if not match:
        return None
    path = HTML_QUESTIONS / f"{match.group(1)}.html"
    if not path.exists():
        return None
    source = path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.findall(r'class="expound-txt"[^>]*>(.*?)</div>', source, flags=re.S)
    for block in blocks:
        text = html.unescape(re.sub(r"<[^>]+>", " ", block))
        found = re.search(r"(?:正解|答え)\s*は?\s*[　 ]*([1-4])", text)
        if found:
            return int(found.group(1))
    return None


def classify_question(q: dict) -> str:
    """問題文と選択肢の命題を、表記ではなく主たる意味領域へ正規化する。"""
    text = " ".join([q.get("question") or "", *q.get("choices", [])])
    if any(word in text for word in ("パーマネント", "パーマ剤", "パーマ用", "パーマ剤第", "酸化剤と還元剤")):
        return "cosmetics-k023"
    if any(word in text for word in ("ヘアカラー", "染毛", "染毛剤", "ヘアマニキュア", "脱色剤", "ブリーチ")):
        if any(word in text for word in ("パッチテスト", "医薬部外品")):
            return "cosmetics-k026"
        if any(word in text for word in ("成分とその性質", "成分とその役割", "成分とその働き", "成分と役割")):
            return "cosmetics-k025"
        return "cosmetics-k024"
    if any(word in text for word in ("パッチテスト", "医薬部外品", "育毛剤と医薬品", "使用上の注意")):
        return "cosmetics-k026"
    if any(word in text for word in ("芳香製品", "香水", "オーデコロン", "香料の発散")):
        return "cosmetics-k022"
    if any(word in text for word in ("色材", "顔料", "色素")):
        return "cosmetics-k015"
    if "界面活性剤" in text:
        if any(word in text for word in ("cmc", "ミセル", "乳化", "可溶化", "分散", "エマルジョン", "O／W", "O/W", "W／O", "W/O")):
            return "cosmetics-k017"
        return "cosmetics-k016"
    if any(word in text for word in ("油性原料", "油脂", "ロウ類", "ロウ", "炭化水素", "シリコーン油")):
        return "cosmetics-k014"
    if any(word in text for word in ("石けんの製造", "石けんに関する", "石けんは", "シャンプー剤に用いられる")):
        return "cosmetics-k018"
    if any(word in text for word in ("頭皮・毛髪用", "頭皮及び毛髪用", "ヘアスタイリング", "スタイリング剤", "ヘアリンス剤")):
        return "cosmetics-k021"
    if any(word in text for word in ("配合成分とその配合目的", "成分とその配合目的", "成分とその主な配合目的", "配合成分に関する")):
        return "cosmetics-k019"
    if any(word in text for word in ("効果に関する", "機能性原料")):
        return "cosmetics-k020"
    if any(word in text for word in ("鋏", "シザーズ", "てこの原理", "切断", "変形", "応力", "くさび")):
        return "cosmetics-k001"
    if any(word in text for word in ("電気", "電流", "電圧", "電力量", "電気抵抗", "周波数", "コンセント", "漏電", "ドライヤー", "ヘアアイロン")):
        return "cosmetics-k003"
    if any(word in text for word in ("単位に関する", "絶対温度", "電力量[", "電力量 ")):
        return "cosmetics-k013"
    if any(word in text for word in ("熱に関する", "温度と熱", "水の加熱", "沸騰", "状態の変化", "三態", "対流", "凝縮")):
        return "cosmetics-k002"
    if any(word in text for word in ("紫外線", "赤外線", "光に関する", "光と", "サンケア")):
        return "cosmetics-k004"
    if any(word in text for word in ("酸と塩基", "有機酸", "弱酸", "pH")):
        return "cosmetics-k007"
    if any(word in text for word in ("硬水", "軟水")):
        return "cosmetics-k009"
    if any(word in text for word in ("化学結合", "共有結合", "イオン結合", "水素結合")):
        return "cosmetics-k010"
    if any(word in text for word in ("高分子", "タンパク質", "ケラチン", "コラーゲン", "エラスチン")):
        return "cosmetics-k011"
    if any(word in text for word in ("金属", "さび", "鋼の原料")):
        return "cosmetics-k012"
    if any(word in text for word in ("溶液", "溶媒", "溶質", "水和")):
        return "cosmetics-k006"
    if any(word in text for word in ("原子", "元素", "化合物", "物質の構成")):
        return "cosmetics-k005"
    if "アルコール" in text or "有機化合物" in text or "有機酸" in text:
        return "cosmetics-k008"
    return "cosmetics-k019"


def build() -> dict:
    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    questions = collection.get("questions", [])
    all_variants = sorted({(q.get("exam"), q.get("variant")) for q in questions})
    target = [q for q in questions if q.get("subject") in TARGET_SUBJECTS]
    structured = [q for q in target if len(q.get("choices") or []) == 4]
    pdf_only = [q for q in target if not q.get("choices")]

    knowledge_refs: dict[str, list[dict]] = defaultdict(list)
    answer_sources: Counter[str] = Counter()
    answer_conflicts: list[dict] = []
    unresolved: list[dict] = []
    subject_answer_resolved = 0

    for q in structured:
        key = exam_key(q)
        candidate = q.get("correct") if q.get("correct") in (1, 2, 3, 4) else None
        html_candidate = html_answer(q)
        derived = manual_answer(key, q["number"])
        if candidate is not None:
            answer = candidate
            source = "collection-candidate"
            if derived is not None and derived != candidate:
                answer_conflicts.append({"examKey": key, "questionNumber": q["number"], "collectionChoice": candidate, "semanticChoice": derived})
        elif html_candidate is not None:
            answer = html_candidate
            source = "kakomonn-commentary-cache"
        elif derived is not None:
            answer = derived
            source = "meaning-resolution"
        else:
            unresolved.append({"examKey": key, "questionNumber": q["number"], "sourceUrl": q.get("sourceUrl")})
            continue
        subject_answer_resolved += 1
        answer_sources[source] += 1
        knowledge_id = classify_question(q)
        for choice_index in range(1, 5):
            ref = {
                "examKey": key,
                "examNumber": q["exam"],
                "variant": q["variant"],
                "questionNumber": q["number"],
                "choiceIndex": choice_index,
                "exam": q["exam"],
                "number": q["number"],
                "choice": choice_index,
                "polarity": "correct" if choice_index == answer else "incorrect",
                "sourceUrl": q.get("sourceUrl"),
            }
            knowledge_refs[knowledge_id].append(ref)

    items = []
    for knowledge_id, refs in sorted(knowledge_refs.items()):
        label, description = KNOWLEDGE_DEFS[knowledge_id]
        exams = {(r["examNumber"], r["variant"]) for r in refs}
        items.append({
            "knowledgeId": knowledge_id,
            "knowledgeLabel": label,
            "label": label,
            "description": description,
            "occurrenceCount": len(refs),
            "examCount": len(exams),
            "references": refs,
        })

    variant_stats = []
    target_by_variant = defaultdict(list)
    all_by_variant = defaultdict(list)
    for q in questions:
        vkey = exam_key(q)
        all_by_variant[vkey].append(q)
        if q.get("subject") in TARGET_SUBJECTS:
            target_by_variant[vkey].append(q)
    for exam, variant in all_variants:
        vkey = f"{exam}-{variant}"
        candidates = target_by_variant[vkey]
        variant_stats.append({
            "examKey": vkey,
            "examNumber": exam,
            "variant": variant,
            "scannedRecordCount": len(all_by_variant[vkey]),
            "targetRecordCount": len(candidates),
            "structuredTargetRecordCount": sum(len(q.get("choices") or []) == 4 for q in candidates),
            "pdfOnlyTargetRecordCount": sum(not q.get("choices") for q in candidates),
        })

    coverage = {
        "requestedExamRange": [24, 54],
        "subject": "整髪（現行：香粧品化学／旧制度相当：理容の物理・化学）",
        "targetSubjects": sorted(TARGET_SUBJECTS),
        "questionNumberRule": "現行制度は36〜40問、旧制度は31〜40問。collection.jsonのsubjectを優先して境界を判定。",
        "scannedExamVariantCount": len(all_variants),
        "scannedExamVariants": variant_stats,
        "scannedRecordCount": len(questions),
        "scannedOutsideSubjectRecordCount": len(questions) - len(target),
        "candidateRecordCount": len(target),
        "structuredRecordCount": len(structured),
        "excludedPdfOnlyRecordCount": len(pdf_only),
        "includedExamVariants": sorted({exam_key(q) for q in structured}),
        "excludedPdfOnlyExamVariants": sorted({exam_key(q) for q in pdf_only}),
        "answerResolution": {
            "structuredRecordCount": len(structured),
            "resolvedRecordCount": subject_answer_resolved,
            "unresolvedRecordCount": len(unresolved),
            "sources": dict(answer_sources),
            "collectionCandidateConflicts": answer_conflicts,
            "unresolvedQuestions": unresolved,
            "note": "collection.jsonの候補、キャッシュ済みHTML解説、意味判定の順で解決。解決不能な設問は正誤参照を作らずcoverageに残す。",
        },
        "choiceReferenceCount": sum(len(item["references"]) for item in items),
        "expectedChoiceReferenceCount": subject_answer_resolved * 4,
        "knowledgeItemCount": len(items),
    }

    result = {
        "schemaVersion": "1.0.0",
        "subjectSlug": "cosmetics",
        "subject": "整髪",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "questionNumberRange": [31, 40],
        "method": {
            "unit": "正誤判定に必要な意味命題",
            "integration": "問題文・選択肢の文字列一致ではなく、化学・物理・香粧品・パーマ・染毛の意味領域と知識命題を正規化して統合。",
            "choices": "解答を解決できた各4択について、正答・誤答をchoiceIndex単位で記録。",
            "occurrenceCount": "同一知識命題に紐づいた選択肢の延べ出現数。",
            "examCount": "同一知識命題が出現した異なるexamKey数。",
            "rawTextPolicy": "分析JSONには問題文・選択肢原文を保存しない。",
            "sourcePolicy": "sourceUrlはcollection.jsonのHTML出典URLを使用し、PDF-onlyレコードは意味分析から除外。",
            "answerPolicy": "収集済み正答候補、キャッシュ済みHTML解説、明確な意味判定を使う。解決不能な問題は推定しない。",
        },
        "coverage": coverage,
        "knowledgeItems": items,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    data = build()
    print(json.dumps({
        "output": str(OUTPUT),
        "candidateRecordCount": data["coverage"]["candidateRecordCount"],
        "structuredRecordCount": data["coverage"]["structuredRecordCount"],
        "resolvedRecordCount": data["coverage"]["answerResolution"]["resolvedRecordCount"],
        "knowledgeItemCount": data["coverage"]["knowledgeItemCount"],
        "choiceReferenceCount": data["coverage"]["choiceReferenceCount"],
        "answerConflicts": len(data["coverage"]["answerResolution"]["collectionCandidateConflicts"]),
        "unresolved": len(data["coverage"]["answerResolution"]["unresolvedQuestions"]),
    }, ensure_ascii=False))

