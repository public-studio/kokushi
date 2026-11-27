# 理容師国家試験 過去問データ

## 公開範囲

公式PDFと過去問サイトの問題本文・選択肢は、公開許諾を確認できるまでリポジトリへ転載しない。公開ディレクトリには、試験回、問題番号、科目、正答候補の状態、出典URL、本文の取得状態だけを保存する。問題本文・選択肢を含む正本は、`.gitignore` 対象の `questions/past-exams/local/collection.json` で管理する。

公式ページは第29回以降の問題と正答を公表すると説明しているが、個別の再利用ライセンスは確認できない。過去問.comの利用規約も、利用により知的財産権を取得しないこと、著作権者の許可または法律上認められる場合を除きコンテンツを利用できないことを定めている。そのため、公開版は保守的にメタデータのみとした。

## ディレクトリと正本

- `json/`: 試験回別の公開メタデータJSON。`r41-new.json`、`r41-old.json`、`r31-retake.json` のように制度区分を分ける。
- `markdown/`: 試験回別の公開メタデータMarkdown。確認用の索引であり、問題本文の転載版ではない。
- `local/collection.json`: 本文・4選択肢を含むローカル正本。公式PDFにしかない回や、未取得・未検証状態も同じスキーマで保持する。
- `local/html/`: 取得したHTMLキャッシュ。
- `local/official-pdf/`: 取得した公式PDF。GitHubへpushしない。

## スキーマ

ローカルの問題レコードは次の主要項目を持つ。

```json
{
  "id": "r54-q001",
  "exam": 54,
  "variant": "standard",
  "number": 1,
  "subject": "関係法規・制度及び運営管理",
  "question": "問題文（ローカルのみ）",
  "choices": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
  "correct": 3,
  "sourceUrl": "https://riyoushi.kakomonn.com/questions/96750",
  "officialSourceUrl": "https://www.rbc.or.jp/wp-content/uploads/2026/09/54rhikki.pdf",
  "extraction": {"text": "kakomonn-html", "answer": "official-pdf-red-mark-candidate"}
}
```

`correct` は1〜4、未取得は `null`。`answer` は `official-pdf-red-mark-candidate`、`kakomonn-commentary-candidate`、`not-run` のいずれかで、検証状態を隠さない。

## 取得・変換・検証

```powershell
python scripts/collect_past_exams.py --download-pdfs --delay 0.25 --workers 3
python scripts/derive_official_answers.py
python scripts/validate_past_exams.py
python scripts/build_past_exam_artifacts.py
```

本文は過去問サイトのHTMLを優先し、公式PDFは出典と正答印の照合に使う。公式PDFが画像のみの場合、画像認識で確実に対応できない正答は推測で埋めず `null` とする。図・画像を含む問題は `imageUrls` と抽出状態を残し、文字列だけで完全再現しない。

## 対象範囲

公式一覧で確認できた第24回〜第54回を対象とし、第41〜43回は新試験・旧試験を分け、第31回再試験も含める。過去問サイトのHTMLがあるのは第27回〜第54回の29試験回で、第49回は一覧上で問33が欠落している。取得状況は `local/validation.json` と公開Markdownの索引で確認する。

## 出典

- 公式一覧: https://www.rbc.or.jp/exam/past_question/
- HTML問題一覧: https://riyoushi.kakomonn.com/list
- 過去問.com利用規約: https://kakomonn.com/policies/user_terms

