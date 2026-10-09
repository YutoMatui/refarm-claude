---
name: creative-kv
description: りふぁーむの販促ビジュアル（SNS用4:5キービジュアル・A型看板A2・のぼり600×1800）をAIで作る標準手順。手本の広告＋実物の商品写真をGeminiに渡して「1枚の絵」として生成し、文字はコード（Python）で乗せる。商大祭2026の広告づくりで確立したやり方。
---

# creative-kv — 販促ビジュアルをAIで作る

**使う場面**：出店・イベント・新メニューの告知画像（インスタ4:5）、ブース前のA型看板（メニュー表の役割）、のぼり（遠くから呼ぶ役割）を作るとき。
**考え方（これを外すと失敗する）**
1. **手本の広告を2枚渡す**（構図・色・光を借りる）。文章だけで生成すると「AIの平均的な想像」になる
2. **商品は実物写真から素材化する**（グリーンバック #00FF00 で切り抜ける形に）。白背景は白い器・ホイップが抜けるのでNG
3. **1枚の絵として生成する**。器を別々に切り抜いてテーブルに置く合成は「置いただけ」に見える
4. **文字はコードで、明朝で、少なく**。見出し・日付・商品名＋価格・一言・ブランドの5つまで。縁取り・バッジ・札・QR・ふりがな・英字の飾りは使わない
5. **直すときは1つずつ**。元絵を渡し「変えないものを列挙し、変えるものを1つ」。自作の途中の絵を参考に入れて構図を変えようとすると引っ張られて効かない

## 手順（合計2〜3時間）
1. **伝えることを決める** → `templates/kv.example.json` をコピーして書き換える（headline / date / items / offer / sub / brand / by）
2. **手本を集める**：目指す広告2枚（例：スタバの季節キャンペーン）、商品の見た目の参考、実物の写真（スマホ・白いカップ・明るい窓際）
3. **商品素材**：`scripts/gen.py --aspect 1:1 --ref 実物.jpg --prompt "<reference/prompts.md の 3-1>" --out key_商品.png`
4. **本番の絵**：`scripts/gen.py --aspect 4:5 --ref 手本1.jpg --ref 手本2.jpg --ref key_商品1.png --ref key_商品2.png --prompt "<3-2>" --out base.png` を2〜3回。1枚選ぶ。葉などがイラスト風なら `<3-3>` で写真調に差し替え
5. **文字**：`python scripts/kv_text.py config.json base.png out.jpg`（1080×1350）
6. **看板**：写真系 `python scripts/a2_real.py config.json base.png print/A2_real`／手書き風 `scripts/gen.py --aspect 3:4 --prompt "<3-4 黒板>" --out chalk_bg.png` → `python scripts/a2_chalk.py config.json chalk_bg.png print/A2_chalk`
7. **のぼり**：まず `reference/nobori.md` を読み、**手本を2〜3枚もらってから型を決める**。**本命＝商品ヒーロー型** `scripts/nobori_viva.py config.json hero_green.png 出力名 01|02|03 [chalk_bg.png]`（ヒーローは「スプーンで持ち上げたスープ」などをグリーンバックで生成。ロゴは `scripts/brand.py` が描く）／文字主体＝`scripts/nobori_text.py config.json 出力名 [orange|cream]`／写真フルブリード＝`scripts/gen.py --aspect 9:16 --ref reference/examples/nobori_starbucks_strawberry_fullbleed.jpg --ref key_商品.png --prompt "<3-6>" --out nobori_base.png` → `scripts/nobori_full.py config.json nobori_base.png 出力名`。和風の縦書き明朝（`scripts/nobori.py`）は学祭・マルシェには合わないので使わない
8. 出来たものを見て、気になる点を**1つずつ**直す（文言は config を書き換えて再実行、絵は 3-3 の部分修正）

## 役割の違い
- **4:5の画像**：知らせるもの。価格はあってよいが小さく。QRは不要
- **A型看板（A2縦）**：ブース前のメニュー表。商品名と価格を5m先から読める大きさで。写真系と手書き風（黒板）の2型
- **のぼり**：遠くから呼ぶもの。縦書きの商品名2本＋ブランド。情報はそれ以上入れない。上と左のチチ（20〜30mm）に文字をかぶせない

## 環境
- Python 3 ＋ Pillow ＋ numpy（`pip install pillow numpy`）
- Gemini APIキー：環境変数 `GEMINI_API_KEY`（無ければ `vegedasheep_images/generate.py` から読む）
- フォント：Windows ＋ Office のHG明朝E・HG創英角ポップ体があると今回と同じ見た目。無い場合は游明朝・Noto Serif JP に自動で代替（`scripts/fonts.py`）
- 別のPCで使うには、このフォルダ（`.claude/skills/creative-kv/`）ごとリポジトリに入れて clone する。APIキーはコミットしない

## メンバーとの分担（これが前提）
メンバーはコードを書かない。**メンバー＝`templates/brief.md`（発注書）を埋めて、手本2〜3枚と実物写真を出す**。**ゆうと／まい＝Claude Code で `/creative-kv` を使って作る**。出来たものを見て直すのは、基準を知っている人（ゆうと）。別PCでの準備は `SETUP.md`。

## 手本を先にもらう（手戻りを減らす一番の方法）
AIが一から作って直すより、**「こういうのがいい」という実物を2〜3枚もらってから作る**方が早い。もらった手本は `reference/examples/` に入れて、ファイル名に「何の手本か」を書く（例：`nobori_taiyaki_textbased.jpg`）。今入っているもの：スタバ焼き芋の広告2枚（4:5の手本）、スタバのストロベリーバナー（写真フルブリードのぼり）、たい焼専門店ののぼり（文字主体）、りふぁーむのべじだしスープのぼり（水彩）、二葉屋の大学芋ソフト（商品の見た目）、商大祭の完成版。

## 参照
- `reference/nobori.md`：のぼりの目的・入れる情報・3つの型（文字主体／写真フルブリード／水彩）
- `reference/prompts.md`：プロンプトの型（コピペ用）
- `reference/lessons.md`：商大祭2026で試した v1〜v10 の学びと、レビューで出た判断基準
- 文字組のルール：見出し＝HG明朝E・クリーム・字間広め・柔らかい影／日付＝太めの白／商品名＝明朝E＋欧文セリフの数字／一言＝明朝B・ゴールド／ブランド＝Bookman 字間広め。上下にうっすら暗いグラデーションを敷いて読ませる
- 印刷：A2は塗り足し3mmで426×600mm（150dpi＝2516×3543）。のぼりは600×1800mm、100dpiで2362×7087。印刷会社の入稿規定を先に確認
