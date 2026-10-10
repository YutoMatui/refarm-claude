# 10月の新メニュー「極 焼きいもスープ」リール（様式 restaurant・約36秒）

2026-10-10 ゆうとの指摘（1回目：ダサい）を受けた2版目。文字は **Klee One**（手書き風・`fonts/KleeOne-SemiBold.ttf`・OFL）。背景は秋（もみじ）。

| 順 | 背景動画（文字なし） | 文字（plan.json） |
|---|---|---|
| 1 | 割った焼き芋に上から蜜が垂れる・もみじがゆらゆら（生成） | 10月の新メニュー／極 焼きいもスープ |
| 2 | 図解：カップの中へ線が伸びる（`bg_callout.py zukai.json`） | スープ＝さつまいも・かぼちゃ・たまねぎ（括り線でひとまとまり・クリーム）／枝豆・もち麦（別の線・金色）／大学芋・黒ごませんべい（上のトッピング）／スープの野菜は兵庫県産・さつまいもは ヘルシーファーム |
| 3 | カップに寄る | 極 焼きいもスープ／¥600 |
| 4 | 10月のカレンダー（カップなし・下の文字と離す） | 10月は 月・火・木／11:00 – 14:00／20日（火）はお休み・12日（祝）は営業します |
| 5 | 店の前・外観（`video/cal_reel/clips/03a・03b` を使い回す） | 場所・行き方 |
| 6 | ロゴ | 詳しくは公式LINEで／プロフィールのリンクから |

## 作る順（代表PC。生成はお金がかかるので、承認をもらってから）

```bash
cd video/imo_reel
S=../../.claude/skills/reel-capcut/scripts
REF=../../.claude/skills/creative-kv/reference/examples/kv_refarm_shodaisai_final.jpg

# A. 秋の背景（もみじ）… 試作 約6円 → 動かす 約180円
python $S/gen_image.py 試作 src/autumn_bg.png "Vertical 9:16 photographic background for a food advertisement. Warm golden-orange gradient from #D59040 at the top to #B86A1E at the bottom. Real photographed Japanese maple leaves (momiji) in red, orange and yellow only along the top edge, the bottom edge and the corners, some softly out of focus. The center 70 percent is completely empty and smooth for a product and text. Soft warm bokeh light. Photoreal, no illustration, no objects, no text." $REF
python $S/gen_clip.py 実行 src/autumn_bg.mp4 src/autumn_bg.png "The maple leaves at the edges sway gently in a light breeze, and one leaf slowly drifts down. The empty center and the gradient do not change."

# B. 最初のカット … 試作 約6円 → 動かす 約180円
python $S/gen_image.py 試作 src/01_imo_916.png "Vertical 9:16 autumn food advertisement photo in the style of the first reference. Warm golden-orange gradient background. A large split-open roasted Japanese sweet potato (yaki-imo) with glossy golden syrup pouring onto it from above, in the upper middle. In front of it, the white VEGEONE soup cup from the second reference exactly as it is (yellow potage, two candied sweet potato cubes and a black sesame cracker on top). Real photographed maple leaves near the edges. Do NOT include a separate bowl of candied sweet potatoes and do NOT include soft-serve ice cream. Keep the top 25 percent calm and empty for text. Photoreal, no illustration, no text except the logo on the cup." $REF src/cup_green.png
python $S/gen_clip.py 実行 clips/01_imo_raw.mp4 src/01_imo_916.png "Slow food-commercial motion. Thin glossy golden syrup keeps pouring from above onto the split roasted sweet potato and slowly drips down its flesh. Soft steam rises from the soup cup. The maple leaves sway gently in a light breeze and one leaf slowly drifts down. Everything else stays still."
python $S/prep_clip.py clips/01_imo_raw.mp4 clips/01_imo_drip.mp4 --t 6

# C. 残りの背景動画（無料）… src/autumn_bg.mp4 があれば自動で地に使う
python build_bg.py

# D. ドラフト
python $S/make_draft.py plan.json
```

- 無料でやるなら、A・B の画像と指示文を Dreamina か CapCut の AI動画生成（Seedance 2.0）に手で入れる
- 店では大学芋単品を売らないので、大学芋の器・ソフトクリームは画に入れない（B の指示に書いてある）
- 生成画像のもみじがイラストっぽくなったら使わない（NG：イラストの葉）。言葉を直して試作をもう1回
- 元画像（`src/cup_green.png`＝グリーンバックのカップ）と mp4・png はコミットしない
