---
description: りふぁーむ（スープ・おかえり農園・団体紹介）のスライドをRREP風デザインで作成する。温かい紙×明朝見出し×緑アクセント
allowed-tools: Bash, Write, Edit, Read, Glob
---

# りふぁーむ スライド作成スキル（/refarm-slide）

りふぁーむのスライド資料を、代表が気に入っている**RREP「農園 in the park」のデザイン**（温かい紙・明朝の大見出し・緑アクセント・差し色の暖赤）で作成し、HTML/PDF/PPTXに変換する。
代表が別用途で使う赤基調テンプレート（`/slide`）とは別物。**りふぁーむの資料は必ずこちらを使う**。

## 引数

$ARGUMENTS

引数＝スライドのお題（例:「スープ事業のビジコン発表」「おかえり農園の行政説明」「新入生向け団体紹介」）。
空の場合は「どんなスライドを作りますか？（用途・聞き手・伝えたい結論）」と確認する。

## テーマ・出力先

- テーマCSS: `slides/themes/refarm.css`（このデザインの本体。RREPを汎用化したもの）
- Mermaid設定: `slides/themes/mermaid-config.json`
- 出力先: `slides/` ディレクトリ
- 参照デザインの実物: `rrep-slides/rrep.md`（クラスの使い方の生きた見本。迷ったらここを見る）

## デザインの世界観（外さない軸）

- **背景は紙（オフホワイト `#FBFAF6`）**。黒背景・緑ベタ背景はNG（濃色スライドは深緑インク `#1E2A22` か写真オーバーレイのみ）
- **見出しは明朝**（Yu Mincho系）、**本文・UIはゴシック**（Yu Gothic系）の二層使い
- **緑 `#2F6B45` はアクセント**（キッカー・強調・数字・マーカー）。**暖赤 `#C0533F` は差し色**（Before・注意）。多用しない
- 1スライド1メッセージ。余白をたっぷり取り、明朝コピーで「想い」を語るスライドを要所に置く（りふぁーむは想い重視）
- 写真を大きく使う。図表は横長で大きく

## フロントマター（必須）

```yaml
---
marp: true
theme: refarm
paginate: true
size: 16:9
---
```

## スライドクラス一覧（`<!-- _class: xxx -->` で指定）

| クラス | 用途 |
|--------|------|
| `cover` | 表紙。`.eyebrow`／`.ctitle`（明朝特大）／`.sub`／`.who`。深緑 or 写真背景 |
| `divider` | セクション区切り。`.dnum`（01）／`h2`／`.sub` |
| `statement` | 主張スライド。`.eyebrow`＋`.big`（大きな明朝コピー）＋`.after`。想いを語る場面に |
| `message` | 写真×白文字の中央メッセージ |
| `closing` | 締め。`.thx`＋`.foot` |
| （なし） | 通常コンテンツ（紙背景）。`.kicker`／`h2`／`.points` 等 |

濃色スライド（cover/divider/statement/message/closing）は `<!-- _paginate: false -->` を併用してページ番号を隠す。

## コンテンツ部品（本文スライドで使う）

- `.kicker` … 見出し上の緑ラベル（例: AGENDA）
- `.points` > `li` … 緑丸ビュレットの箇条書き（素の `-` リストも自動で同トーン）
- `.mk` … 緑マーカー蛍光、`.em`/`**強調**` … 緑太字
- `.srow`（`.sn`/`.sfull` or `.sk`+`.sd`）… 番号つき行（アジェンダ・サマリー）
- `.row`＋`.figure`／`.big-photo` … 文章＋写真の横並び・大判写真
- `.ba`（`.b`→`.arw`→`.a`）… Before→After
- `.tl`＋`.tlitem` … 3枚並べの写真タイムライン
- `.result`（`.num`+`.lbl`）… 大きな数字で結果を見せる
- `.chip`／`.tag`／`.tagred` … チップ・ラベル
- 標準Markdownテーブルは自動でカード風（緑ヘッダー）になる

背景写真を使う濃色スライドは、そのスライドに `<!-- _backgroundImage: url("img/xxx.png") -->` を書くか、`section` に inline style で `background` を上書きする。画像は `slides/img/` 等に置く。

## 図表（Mermaid）

Marpはmermaidを直接描けないため、`.mmd`→SVG変換して画像埋め込みする（`/slide` と同じ手順）:
```bash
npx @mermaid-js/mermaid-cli -i slides/diagrams/{名前}.mmd -o slides/diagrams/{名前}.svg -c slides/themes/mermaid-config.json -b transparent
```
Mermaidノードの配色はりふぁーむ配色に合わせる（メイン=`#2F6B45`／注意=`#C0533F`／補助=薄緑 `#CDE7B4`・文字色は視認性優先）。

## 出力手順

```bash
# HTML
npx @marp-team/marp-cli slides/{ファイル名}.md --theme slides/themes/refarm.css --html --output slides/{ファイル名}.html
# PDF
npx @marp-team/marp-cli slides/{ファイル名}.md --theme slides/themes/refarm.css --html --pdf --allow-local-files --output slides/{ファイル名}.pdf
# PPTX（編集可能にするなら --pptx-editable を追加）
npx @marp-team/marp-cli slides/{ファイル名}.md --theme slides/themes/refarm.css --html --pptx --allow-local-files --output slides/{ファイル名}.pptx
```
確認: `start slides/{ファイル名}.html`

## 進め方のベストプラクティス

1. まず構成（表紙→アジェンダ→本論→想いのstatement→まとめ→closing）を決める
2. `rrep-slides/rrep.md` のクラスの使い方を参照しながら組む
3. 1スライド1メッセージ。テキストを詰め込みすぎない
4. 想いを語るstatement/messageスライドを必ず1〜2枚入れる（りふぁーむの資料の肝）
5. スープの対外資料でトーンを白×コーラル寄りにしたい場合のみ、`--primary` 相当を暖赤側に寄せてもよいが、基本はこの緑アクセントで統一する
