# 国試 (kokushi)

理容師国家試験に向けた、一人専用の自己進化型AI学習ゲーム。

ゲームタイトル案：**君と、合格する春。 / LOVE & LICENSE**

## 目的

- 理容専門学校2年生のプレイヤーが、恋愛アドベンチャーを楽しみながら国家試験の筆記を学ぶ。
- ChatGPTの会話とインタラクティブな画面をゲーム本体にする。
- プレイヤー自身がChatGPTに改善を頼み、自分専用のゲームを育てられるようにする。
- 汎用化や一般利用者向けのサービス化は目的にしない。

## 構成

| 要素 | 方針 |
|---|---|
| GitHub | public-studio/kokushi、main。ゲーム仕様・問題・設定・セーブを管理 |
| ChatGPT | ゲームエンジン、画面、出題、採点、会話、改善 |
| GitHub MCP | 読み込み、セーブ、ロード、仕様変更 |
| HTML | 起動ボタン中心のランチャー。必要な補助部品は後から |
| Cloudflare | HTML配信、GitHub連携による自動デプロイ |
| 予定URL | https://kokushi.kanazawa-u.work/ |
| DB・独自API | 初期段階では導入しない |

## ドキュメント

- [AGENTS.md](AGENTS.md)：AIの共通運用ルール
- [game.md](game.md)：ゲーム仕様・画面・保存・実装方針

## 現在の状態（2026-11-26）

- [ゲーム起動用HTML](public/index.html) と Cloudflare Workers Static Assets 用の設定を作成済み。
- [練習用3問](questions/starter.json) と [初期セーブ](data/save.json) を作成済み。練習用問題はオリジナルであり、公式過去問ではない。
- ChatGPTのゲーム進行・保存・再開・未接続モードのルールを実装仕様として記録済み。別アカウントでのセーブ・再開の実動作は未検証。
- 公式過去問は [公式サイト](https://www.rbc.or.jp/exam/past_question/) を参照。第54回の参考問題一覧 https://www.kakomon-ai.jp/riyoshi/2026-second 。公式PDFの直接取得ができなかったため、正答照合済みの全問データは未収録。
- CloudflareのGitHubリポジトリ接続は未完了。Git連携の再認可が必要。予定URLはまだ稼働未確認。
- プレイヤーの実データは未登録。

まずChatGPTに「public-studio/kokushi の AGENTS.md と game.md を読み、国試ゲームを開始して」と依頼する。MCP未接続でも体験モードで遊べるようにする。
