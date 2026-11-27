# 科目別知識分析

## 目的

過去問の問題文の文字列一致ではなく、正誤判定に必要な意味上の知識命題を統合する。正答選択肢と誤答選択肢を両方の出典として扱い、同じ知識の反復を測る。

## JSON仕様

科目別ファイルは `questions/analysis/subjects/*.json` に置く。

- `knowledgeId`: 科目内で安定したID。科目slugを接頭辞にする。
- `label`: 公開可能な短い知識名。
- `description`: 問題文を転載しない意味記述。
- `occurrenceCount`: その知識に紐づく選択肢の延べ出現数。
- `examCount`: 出現した異なる試験回数。新旧試験区分・再試験はvariantで区別する。
- `references`: `exam`、`variant`、`number`、`choice`、`polarity`、`sourceUrl`。原文は入れない。

全科目の統合ランキングは `ranking.json`。科目別の問題数による補正はまだ行わず、全知識項目を同じ基準で並べる。

## 再集計

```powershell
python scripts/normalize_analysis_schema.py
python scripts/validate_analysis.py
python scripts/build_analysis_ranking.py
```

過去問追加時は、まずローカル正本を更新し、科目別JSONを再生成してから上記コマンドで重複ID・参照数・試験回数を検証する。80問の選定やゲーム本体の変更はこの分析工程に含めない。

`validate_analysis.py` は8科目の必須キー、knowledge IDの重複、正答・誤答の選択肢参照、出典URL、本文・選択肢原文の混入を検査する。`normalize_analysis_schema.py` はサブエージェント間の別名キーを共通キーへそろえ、`occurrenceCount` と `examCount` を参照から再計算する。

