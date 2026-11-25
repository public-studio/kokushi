# 国試 — 起動手順 v0.2

以下を順番に実行する。ファイルを読むだけで工程完了としない。

1. [game.md](https://github.com/public-studio/kokushi/blob/main/game.md) を取得しゲームルールを確認。
2. [save.md](https://github.com/public-studio/kokushi/blob/main/save.md) と [data/save.json](https://github.com/public-studio/kokushi/blob/main/data/save.json) を取得し再開位置を確認。
3. [ui.md](https://github.com/public-studio/kokushi/blob/main/ui.md) を取得し、相手の名前・性格・外見をAIが決め（再開時は既存の人物を維持）、外部背景・キャラクター画像を実際に検索・参照する。取得不能なら画像なしと明示。SVGや生成画像で代替しない。
4. [questions/starter.json](https://github.com/public-studio/kokushi/blob/main/questions/starter.json) を取得し、game.md 指定の公式問題・正答を実際に照合する。未照合ならオリジナル練習問題を使う。
5. 上記工程の結果を確認してから最初のインタラクティブ画面を表示する。呼び名やキャラクターの入力・選択・確認画面を挟まず、すぐ第1問を表示し、1問ずつ進める。
6. 回答後は採点・解説・ハート更新を行い、save.md に従い自動保存し、実際の書き込み結果を確認する。

取得はGitHub MCPを優先し、不可なら上記公開URLを参照する。未接続は体験モード。取得・照合・保存の成功を推測で報告しない。本人専用のゲームとし、正答・履歴を演出で変更しない。

## プレイヤー向け表示
起動時に設定・保存許可・取得結果の画面を挟まない。GitHub、MCP、JSON、SHA、API、ファイル名、技術的な処理結果は通常のゲーム画面に表示しない。すぐ会話と第1問を表示する。保存許可の質問は行わず、自動保存する。技術情報は求められた場合のみ説明する。

## 固定方針
本人専用ゲーム。公開GitHubを維持し、非公開化を再提案しない。保存許可の質問やセーブボタンは不要。毎回答後に自動保存し、次回は続きから自動再開する。詳細は save.md。
