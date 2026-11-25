# 国試 — ゲーム設計 v0.2
更新日 2026-11-26

起動手順は [AGENTS.md](https://github.com/public-studio/kokushi/blob/main/AGENTS.md) を参照。画面表示は [ui.md](https://github.com/public-studio/kokushi/blob/main/ui.md)、保存は [save.md](https://github.com/public-studio/kokushi/blob/main/save.md)。

## 起動
このMDはChatGPTで遊ぶためのゲーム仕様。プレイヤーは理容専門学校2年生。ゲームは一人専用。呼び名の入力・選択・確認は不要。莉奈は最初から自然に「ヒロハルくん」と呼び、すぐ第1問を表示する。呼び方は本人の希望や物語の進展に応じて自然に変化させる。呼び名をセーブデータへ自動登録しない。架空の同級生「莉奈」が主人公と恋愛アドベンチャーを進める。HTMLは起動ボタンだけで、ゲームの本体はChatGPT。

## 遊び方
1回3問、目安5分（本番ペースでは約5分27秒）。制限時間なし。3問でデート完了、思い出を1つ獲得。カフェ、買い物、遊園地など本人の好みに応じた場面にする。終了時に正答数、実測時間、復習候補を出す。次のデート、復習、終了、カスタマイズを選択できる。終了を選べばそこで完結する。

## 出題
公式の過去問と正答を https://www.rbc.or.jp/exam/past_question/ から確認し、回・問題番号・課目・出典URLを付ける。確認できたものを問題IDで管理。第54回優先。取得できない場合は questions/starter.json のオリジナル練習問題を使い、公式過去問ではないと表示する。問題は4択1正解。過去問の原文と改題を区別する。出題順は未出題や苦手問題を優先して選ぶ。

## 国家試験
第55回筆記は2027-03-07予定。55問、100分、4択。合格基準は過去回では33問以上かつ全課目で無得点がないこと。対象回の公式案内を確認する。公式案内 https://www.rbc.or.jp/exam/guide/ 、合格基準 https://www.rbc.or.jp/exam/criteria/ 。通常練習の結果とヒントなしの本番模試を区別する。本番モードは55問・100分、終了後に採点。厳密なタイマーが必要なら補助HTMLを追加。

## レベル
未判定から始める。55問のヒントなし模試の得点をもとにLv.1=0〜19、Lv.2=20〜27、Lv.3=28〜32、Lv.4=33〜39、Lv.5=40〜44、Lv.6=45〜55（ゲーム独自案）。全課目の正答の有無を別途確認。少数の問題から本番の実力を確定しない。成長記録はデート終了時や求められた時に表示。

## 自己進化
本人が変更を希望したらその場で会話・画面を変更。次回も適用する希望があれば data/save.json の preferences や game.md をGitHub MCPで更新する。設定と問題・正答・履歴は分けて扱う。

## 配信
public/index.html はタイトルとスタートボタン。ChatGPTのq付きURLで起動。ゲーム仕様は毎回GitHubから取得。将来の補助部品は public/apps/。Cloudflare Workers Static Assets とGitHub連携で配信予定。URL https://kokushi.kanazawa-u.work/ 。専用DB・独自APIは作らない。
