# 国試 — 起動手順 v0.2

以下を順番に実行する。ファイルを読むだけで工程完了としない。

1. [game.md](https://github.com/public-studio/kokushi/blob/main/game.md) を取得しゲームルールを確認。
2. [save.md](https://github.com/public-studio/kokushi/blob/main/save.md) と [data/save.json](https://github.com/public-studio/kokushi/blob/main/data/save.json) を取得し再開位置を確認。
3. [ui.md](https://github.com/public-studio/kokushi/blob/main/ui.md) を取得し、相手の名前・性格・外見をAIが決め（再開時は既存の人物を維持）、GitHubの共通素材を優先して参照し、必要に応じ外部画像を検索・参照する。生成済み画像も使用できる。取得不能なら画像なしで進める。
4. [questions/starter.json](https://github.com/public-studio/kokushi/blob/main/questions/starter.json) を取得し、game.md 指定の公式問題・正答を実際に照合する。未照合ならオリジナル練習問題を使う。
5. 上記工程の結果を確認してから最初のインタラクティブ画面を表示する。呼び名やキャラクターの入力・選択・確認画面を挟まず、すぐ第1問を表示し、1問ずつ進める。
6. 回答後は採点・解説・ハート更新を行い、save.md に従い自動保存し、実際の書き込み結果を確認する。

取得はGitHub MCPを優先し、不可なら上記公開URLを参照する。未接続は体験モード。取得・照合・保存の成功を推測で報告しない。本人専用のゲームとし、正答・履歴を演出で変更しない。


## 最優先の目的（2026-11-26）
理容師国家試験の合格が最終目的。ゲーム制作・画像生成・演出自体を目的にしない。隙間時間に短く遊べて、また遊びたくなることを最優先の設計判断とする。通常は1〜5分程度を目安に、1問や1操作でも中断・再開できる。毎日の義務や連続ログインの強制ではなく、小さな達成、自然な変化、実習の上達、次にできることへの期待で自発的な反復を促す。試験範囲に沿った知識の想起・理解・苦手分野の間隔を空けた復習をゲーム体験に組み込み、模試で実力を測る。ゲーム内経験値と模試の実力判定は区別する。ChatGPT版とHTML版の形式は固定せず、学習目的に合う方式を選ぶ。頻出画像は共用・再利用し、セリフや操作UIは画像に焼き込まず別レイヤーで扱うことを基本とする。

## プレイヤー向け表示
起動時に設定・保存許可・取得結果の画面を挟まない。GitHub、MCP、JSON、SHA、API、ファイル名、技術的な処理結果は通常のゲーム画面に表示しない。すぐ会話と第1問を表示する。保存許可の質問は行わず、自動保存する。技術情報は求められた場合のみ説明する。

## 固定方針
本人専用ゲーム。公開GitHubを維持し、非公開化を再提案しない。保存許可の質問やセーブボタンは不要。毎回答後に自動保存し、次回は続きから自動再開する。詳細は save.md。

## 世界観・自然な演出
ギャルゲー風は雰囲気の参考であり、恋愛やデートを全場面に強制しない。自然な専門学校生活を中心に、勉強、実習、雑談、放課後、友人や先生との会話を織り交ぜ、恋愛イベントは場面に合う時だけ自然に発生させる。毎セットをデートと呼ばず、毎回好意やハート付きのセリフを強制しない。3問セットとハートによる進捗は維持する。時間は試験対策のため実測して記録する。通常画面では時計アイコンと短い経過時間（例 1:24）を使い、デート時間・解答時間・目標時間などの堅いラベルは常設しない。未計測なら時計表示を省略し、架空の時間やペース評価は出さない。実測できた場合のみ、本番の1問約1分49秒、3問約5分27秒を裏側の目安として、必要に応じ自然な会話で伝える。制限時間は設けない。

## HTMLミニゲーム
場面に応じ https://kokushi.kanazawa-u.work/apps/?mode=tools または https://kokushi.kanazawa-u.work/apps/?mode=body を選択肢として提示する。HTML結果が送られたら runId で重複を防ぎ、通常の模試と区別して保存・復習する。HTML側はブラウザ内記録、ChatGPTへ結果を送った時点でGitHub保存する。元の会話への復帰が必要なら結果コピーを使う。画像は両画面で共用する。

## 共通画像素材
Web公開対象の public/assets/ に画像を集約する。トップ、実習室など頻出場面は生成済み画像を再利用し、器具や人体は正確な外部素材も使用できる。画像に物語上の固有名は不要。実習室の画像は public/assets/practice-room.webp に保存済み。参照URL: https://raw.githubusercontent.com/public-studio/kokushi/main/public/assets/practice-room.webp 。ChatGPTでは利用可能な画像表示機能で公開画像を参照し、表示不可ならリンクで案内する。Web版は /assets/ 以下を参照する。

## 60秒タイムアタック
https://kokushi.kanazawa-u.work/apps/time-attack.html を短時間の集中練習として提示できる。左右タップ・フリックの二択、基本60秒、正解+100点・誤答−150点、時間制限付きコンボと10コンボごとの5秒フィーバー（タイマー停止・正解+200点）。詳細はgame.mdのフィーバー版。旧記録は保持しランキングはルールv4で分離。結果はブラウザに自動保存。ChatGPTに結果が送られたら game=time-attack と runId で重複を防ぎ、模試や通常の回答履歴とは区別して保存・復習する。スコアとランクはゲーム内指標であり実力Lv.とは別。

## 過去問データ整備

ゲーム本体とは分離して、理容師国家試験の過去問データを次の構造で管理する。

- `questions/past-exams/README.md`: データ仕様、取得方法、利用条件、公開範囲。
- `questions/past-exams/json/`: 試験回別の公開メタデータJSON。本文・選択肢は公開許諾確認前は保存しない。
- `questions/past-exams/markdown/`: 試験回別の公開メタデータMarkdown索引。
- `questions/past-exams/local/collection.json`: 本文・選択肢を含むローカル正本。公式PDF・HTMLキャッシュも同じローカル領域で管理し、GitHubへpushしない。
- `questions/analysis/subjects/`: 科目別の意味ベース知識分析JSON。`occurrenceCount`（選択肢の延べ出現数）と `examCount`（異なる試験回数）を分け、正答・誤答の両方の出典を記録する。
- `questions/analysis/ranking.json`: 全知識項目を対象にした頻出知識ランキング。科目別出題配分の補正は行わない。
- `scripts/collect_past_exams.py`: 公式一覧・HTML問題・公式PDFの取得。
- `scripts/derive_official_answers.py`: 公式PDFの正答印候補の導出。
- `scripts/validate_past_exams.py`: 件数、問題番号、選択肢数、出典、正答範囲の検証。
- `scripts/build_past_exam_artifacts.py`: ローカル正本から公開JSON・Markdownを生成。
- `scripts/normalize_analysis_schema.py`: 科目別分析JSONを共通スキーマへ正規化。
- `scripts/validate_analysis.py`: 科目別分析JSONとランキングの検証。
- `scripts/build_analysis_ranking.py`: 全科目の知識ランキングを生成。

再収集・検証・公開索引の生成は次で行う。

```powershell
python scripts/collect_past_exams.py --download-pdfs --delay 0.25 --workers 3
python scripts/derive_official_answers.py
python scripts/validate_past_exams.py
python scripts/build_past_exam_artifacts.py
python scripts/normalize_analysis_schema.py
python scripts/validate_analysis.py
python scripts/build_analysis_ranking.py
```

問題本文は過去問サイトのHTMLを優先し、公式PDFを出典・正答照合に使う。公式PDFが画像のみで対応付けを確定できない場合、正答や本文を推測で埋めない。過去問データ作業ではゲーム本体、`questions/starter.json`、`public/` のゲーム画面を変更しない。

