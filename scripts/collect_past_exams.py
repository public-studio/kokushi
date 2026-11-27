#!/usr/bin/env python3
"""理容師国家試験の公式一覧とHTML問題ページを収集する。

本文・選択肢は過去問サイトのHTMLから取得する。公式PDFは正答照合用に
ローカルへ保存し、公開成果物には含めない。サイトへ過度な負荷をかけない
ため、取得間隔を設け、既存のキャッシュを優先する。
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html as html_lib
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


OFFICIAL_INDEX = "https://www.rbc.or.jp/exam/past_question/"
KAKOMON_INDEX = "https://riyoushi.kakomonn.com/list"
USER_AGENT = "kokushi-research/1.0 (+https://github.com/public-studio/kokushi)"


@dataclass
class OfficialSource:
    exam: int
    variant: str
    label: str
    url: str
    filename: str
    source_index: str = OFFICIAL_INDEX
    pdf_downloaded: bool = False
    pdf_text_layer: bool | None = None
    answer_verification: str = "not-run"


@dataclass
class HtmlSource:
    exam: int
    variant: str
    label: str
    list_url: str
    question_count: int = 0
    status: str = "discovered"


def clean_text(value: str) -> str:
    value = re.sub(r"(?is)<script\b.*?</script\s*>", " ", value)
    value = re.sub(r"(?is)<style\b.*?</style\s*>", " ", value)
    value = re.sub(r"(?is)<br\s*/?>", "\n", value)
    value = re.sub(r"(?is)<img\b[^>]*alt=[\"']([^\"']*)[\"'][^>]*>", r"\1", value)
    value = re.sub(r"(?is)<img\b[^>]*>", "[画像]", value)
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = html_lib.unescape(value).replace("\u3000", " ")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in value.splitlines()]
    return re.sub(r"\s+", " ", " ".join(line for line in lines if line)).strip()


def fetch_text(url: str, cache_path: Path, delay: float, force: bool = False) -> str:
    if cache_path.exists() and not force:
        return cache_path.read_text(encoding="utf-8")
    if delay > 0:
        time.sleep(delay)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
    text = payload.decode(charset, errors="replace")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text


def fetch_bytes(url: str, cache_path: Path, delay: float, force: bool = False) -> bytes:
    if cache_path.exists() and not force:
        return cache_path.read_bytes()
    if delay > 0:
        time.sleep(delay)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(payload)
    return payload


def iter_links(source: str, pattern: str) -> Iterable[tuple[str, str]]:
    for match in re.finditer(
        r"(?is)<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a\s*>", source
    ):
        href = html_lib.unescape(match.group(1))
        label = clean_text(match.group(2))
        if re.search(pattern, href):
            yield href, label


def parse_official_sources(source: str) -> list[OfficialSource]:
    result: list[OfficialSource] = []
    seen: set[str] = set()
    for href, label in iter_links(source, r"\.pdf(?:[?#]|$)"):
        url = urljoin(OFFICIAL_INDEX, href)
        if url in seen or "理容師" not in label:
            continue
        match = re.search(r"第\s*(\d+)\s*回", label)
        if not match:
            match = re.search(r"(\d+)rhikki", url, flags=re.I)
        if not match:
            continue
        exam = int(match.group(1))
        if "再試験" in label or "saishi" in url.lower():
            variant = "retake"
        elif "旧試験" in label or re.search(r"rhikkio\b", url, flags=re.I):
            variant = "old"
        elif "新試験" in label or re.search(r"rhikkin\b", url, flags=re.I):
            variant = "new"
        else:
            variant = "standard"
        filename = Path(urlparse(url).path).name
        result.append(OfficialSource(exam, variant, label or f"第{exam}回", url, filename))
        seen.add(url)
    return sorted(result, key=lambda item: (item.exam, item.variant, item.url))


def parse_kakomonn_index(source: str) -> list[HtmlSource]:
    result: list[HtmlSource] = []
    seen: set[str] = set()
    for href, label in iter_links(source, r"/list1/\d+"):
        url = urljoin(KAKOMON_INDEX, href)
        base_url = re.sub(r"[?&]page=\d+", "", url)
        if base_url in seen:
            continue
        match = re.search(r"第\s*(\d+)\s*回", label)
        if not match:
            continue
        exam = int(match.group(1))
        # 41〜43回は公式資料が新・旧試験に分かれており、過去問サイトの
        # 42・43回の一覧ラベルには「新」が付かないため、新制度側へ寄せる。
        variant = "old" if "旧" in label else "new" if "新" in label or exam in {41, 42, 43} else "standard"
        result.append(HtmlSource(exam, variant, label or f"第{exam}回", base_url))
        seen.add(base_url)
    return sorted(result, key=lambda item: (item.exam, item.variant, item.list_url))


def list_page_urls(source: str, base_url: str) -> list[str]:
    urls = {re.sub(r"[?&]page=\d+", "", urljoin(base_url, href)) for href, _ in iter_links(source, r"/list1/\d+")}
    pages = {1}
    for href, _ in iter_links(source, r"/list1/\d+\?page=\d+"):
        match = re.search(r"[?&]page=(\d+)", href)
        if match:
            pages.add(int(match.group(1)))
    base = re.sub(r"[?&]page=\d+", "", base_url)
    return [f"{base}?page={page}" for page in sorted(pages)] if base in urls or not urls else [f"{base}?page={page}" for page in sorted(pages)]


def question_links(source: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for href, _ in iter_links(source, r"/questions/\d+"):
        url = urljoin(KAKOMON_INDEX, href)
        if url not in seen:
            found.append(url)
            seen.add(url)
    return found


def first_block(source: str, start_pattern: str, end_pattern: str) -> str:
    match = re.search(start_pattern + r"(.*?)" + end_pattern, source, flags=re.I | re.S)
    return match.group(1) if match else ""


def parse_html_answer(source: str) -> int | None:
    """HTMLページの解説に明示された正誤から正答候補を得る。

    解説は公式正答そのものではないため、候補として保存し、公式PDFの
    正答印または別の検証処理で上書き・照合する。
    """
    start = source.find('id="js-commentary-wrap"')
    end = source.find('class="bottom-report-link"', start)
    if start < 0:
        return None
    commentary = source[start:end if end > start else None]
    numeric_answer = re.search(r'class=["\'][^"\']*text-huge[^"\']*["\'][^>]*>\s*<strong>\s*([1-4])\s*</strong>', commentary, flags=re.I | re.S)
    if numeric_answer:
        return int(numeric_answer.group(1))
    votes: dict[int, list[bool]] = {}
    for match in re.finditer(r'<div\b[^>]*class=["\']expound-(\d+)["\'][^>]*>(.*?)(?=<div\b[^>]*class=["\']expound-\d+|</div>\s*<div\b[^>]*class=["\']expound-bottom)', commentary, flags=re.I | re.S):
        number = int(match.group(1))
        text_blocks = re.findall(r'<div\b[^>]*class=["\']expound-txt["\'][^>]*>(.*?)</div\s*>', match.group(2), flags=re.I | re.S)
        text = clean_text(text_blocks[0] if text_blocks else match.group(2))[:300]
        wrong = re.search(r"誤り|誤った|間違い|不適切", text)
        right = re.search(r"正しい", text)
        if wrong and (not right or wrong.start() <= right.start()):
            votes.setdefault(number, []).append(False)
        elif right:
            votes.setdefault(number, []).append(True)
    correct = [number for number, values in votes.items() if values and sum(values) * 2 > len(values)]
    return correct[0] if len(correct) == 1 else None


def parse_question_page(source: str, url: str, source_variant: str | None = None) -> dict:
    heading = clean_text(first_block(source, r"<h1\b[^>]*>", r"</h1>"))
    meta = clean_text(first_block(source, r"<p\b[^>]*class=[\"'][^\"']*when[^\"']*[\"'][^>]*>", r"</p>"))
    combined = f"{heading} {meta}"
    exam_match = re.search(r"第\s*(\d+)\s*回", combined)
    number_match = re.search(r"問\s*(\d+)", combined)
    subject_match = re.search(r"問\s*\d+\s*[（(]\s*(.+?)\s+問\s*\d+\s*[）)]", combined)
    exam = int(exam_match.group(1)) if exam_match else None
    number = int(number_match.group(1)) if number_match else None
    variant = source_variant or ("old" if "旧" in meta else "new" if "新" in meta else "standard")
    question_start = source.find('id="js-question-writing-scroll"')
    question_tail = source[question_start:] if question_start >= 0 else source
    question_block = first_block(question_tail, r'id=["\']js-question-writing-scroll["\'][^>]*>', r"</div>\s*<p\b[^>]*id=[\"']question-writing-hint")
    question_match = re.search(r'<div\b[^>]*class=["\']ttl["\'][^>]*>(.*?)</div>', question_block, flags=re.I | re.S)
    question = clean_text(question_match.group(1)) if question_match else ""
    options_block = first_block(question_tail, r'<ul\b[^>]*class=["\']list["\'][^>]*>', r'</ul>\s*<ul\b[^>]*class=["\']check["\']')
    options: list[str] = []
    for item in re.findall(r"<li\b[^>]*>(.*?)</li\s*>", options_block, flags=re.I | re.S):
        inner = re.search(r"<div\b[^>]*>(.*?)</div\s*>", item, flags=re.I | re.S)
        options.append(clean_text(inner.group(1) if inner else item))
    image_urls: list[str] = []
    for match in re.finditer(r"<img\b[^>]+(?:src|data-src)=[\"']([^\"']+)[\"']", question_block + options_block, flags=re.I):
        image_urls.append(urljoin(url, html_lib.unescape(match.group(1))))
    html_answer = parse_html_answer(source)
    id_prefix = f"r{exam}" if variant == "standard" else f"r{exam}-{variant}"
    return {
        "id": f"{id_prefix}-q{number:03d}" if exam and number else hashlib.sha1(url.encode()).hexdigest()[:16],
        "exam": exam,
        "variant": variant,
        "number": number,
        "subject": subject_match.group(1).strip() if subject_match else None,
        "question": question,
        "choices": options,
        "correct": html_answer,
        "sourceUrl": url,
        "officialSourceUrl": None,
        "imageUrls": image_urls,
        "extraction": {"text": "kakomonn-html", "answer": "kakomonn-commentary-candidate" if html_answer else "official-pdf-pending"},
    }


def source_key(exam: int | None, variant: str | None) -> tuple[int | None, str | None]:
    return exam, variant


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--delay", type=float, default=0.35)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--download-pdfs", action="store_true")
    parser.add_argument("--max-questions", type=int, default=0)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    repo = args.repo.resolve()
    local = repo / "questions" / "past-exams" / "local"
    raw_html = local / "html"
    pdf_dir = local / "official-pdf"
    raw_html.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    official_html = fetch_text(OFFICIAL_INDEX, raw_html / "official-index.html", args.delay, args.force)
    kakomonn_html = fetch_text(KAKOMON_INDEX, raw_html / "kakomonn-index.html", args.delay, args.force)
    official_sources = parse_official_sources(official_html)
    html_sources = parse_kakomonn_index(kakomonn_html)
    official_by_key = {(item.exam, item.variant): item for item in official_sources}

    for item in official_sources:
        target = pdf_dir / item.filename
        if args.download_pdfs:
            payload = fetch_bytes(item.url, target, args.delay, args.force)
            item.pdf_downloaded = bool(payload)

    questions: list[dict] = []
    for source in html_sources:
        first_url = f"{source.list_url}?page=1"
        list_cache = raw_html / f"list-{source.exam}-{source.variant}-1.html"
        first_page = fetch_text(first_url, list_cache, args.delay, args.force)
        page_numbers = {1}
        for href, _ in iter_links(first_page, r"/list1/\d+\?page=\d+"):
            match = re.search(r"[?&]page=(\d+)", href)
            if match:
                page_numbers.add(int(match.group(1)))
        links: list[str] = []
        for page in sorted(page_numbers):
            page_url = f"{source.list_url}?page={page}"
            page_cache = raw_html / f"list-{source.exam}-{source.variant}-{page}.html"
            page_html = first_page if page == 1 else fetch_text(page_url, page_cache, args.delay, args.force)
            links.extend(question_links(page_html))
        links = list(dict.fromkeys(links))
        source.question_count = len(links)
        source.status = "collected" if links else "empty"
        def collect_question(url: str) -> dict:
            question_id = re.search(r"/questions/(\d+)", url).group(1)
            cache_path = raw_html / "questions" / f"{question_id}.html"
            page_html = fetch_text(url, cache_path, args.delay, args.force)
            record = parse_question_page(page_html, url, source.variant)
            record["officialSourceUrl"] = official_by_key.get((record["exam"], record["variant"]), OfficialSource(0, "", "", "", "")).url or None
            return record

        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            records = list(executor.map(collect_question, links))
        questions.extend(records)
        if args.max_questions:
            questions = questions[: args.max_questions]
        if args.max_questions and len(questions) >= args.max_questions:
            break

    questions.sort(key=lambda item: (item["exam"] or 999, item["variant"], item["number"] or 999, item["sourceUrl"]))
    generated_at = datetime.now(timezone.utc).isoformat()
    output = {
        "schemaVersion": 1,
        "generatedAt": generated_at,
        "scope": "理容師筆記試験の公開過去問",
        "sources": {"officialIndex": OFFICIAL_INDEX, "kakomonnIndex": KAKOMON_INDEX},
        "collectionPolicy": {
            "htmlTextPriority": True,
            "officialPdfForAnswerVerification": True,
            "publicPublication": "metadata-only-until-rights-confirmed",
            "localCanonicalData": "questions/past-exams/local/collection.json",
        },
        "officialSources": [asdict(item) for item in official_sources],
        "htmlSources": [asdict(item) for item in html_sources],
        "questions": questions,
    }
    output_path = local / "collection.json"
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"officialSources": len(official_sources), "htmlSources": len(html_sources), "questions": len(questions), "output": str(output_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

