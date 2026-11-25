# 国試 — 起動手順 v0.2

以下を順番に実行する。ファイルを読むだけで工程完了としない。

1. [game.md](https://github.com/public-studio/kokushi/blob/main/game.md) を取得しゲームルールを確認。
2. [save.md](https://github.com/public-studio/kokushi/blob/main/save.md) と [data/save.json](https://github.com/public-studio/kokushi/blob/main/data/save.json) を取得し再開位置を確認。
3. [ui.md](https://github.com/public-studio/kokushi/blob/main/ui.md) を取得し、外部背景・キャラクター画像を実際に検索・参照する。取得不能なら画像なしと明示。SVGや生成画像で代替しない。
4. [questions/starter.json](https://github.com/public-studio/kokushi/blob/main/questions/starter.json) を取得し、game.md 指定の公式問題・正答を実際に照合する。未照合ならオリジナル練習問題を使う。
5. 上記工程の結果を確認してから最初のインタラクティブ画面を表示する。1問ずつ進める。
6. 回答後は採点・解説・ハート更新を行い、save.md に従い保存許可と実際の書き込み結果を確認する。

取得はGitHub MCPを優先し、不可なら上記公開URLを参照する。未接続は体験モード。取得・照合・保存の成功を推測で報告しない。本人専用のゲームとし、正答・履歴を演出で変更しない。
