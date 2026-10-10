# 10月の新メニュー「極 焼きいもスープ」リール（様式 restaurant・約36秒）

2026-10-10 ゆうとの指摘を受けた3版目。文字は **Yomogi**（ゆるい手書き・`fonts/Yomogi-Regular.ttf`・OFL）。
背景は商大祭キービジュアルの秋（もみじ）。**お金がかかるのは最初のカットを動かす 約180円 だけ**。

| 順 | 背景動画（文字なし） | 文字（plan.json） |
|---|---|---|
| 1 | 割った焼き芋に上から蜜が垂れ、もみじがゆらゆら（元絵＝`build_bg.py`、動かす＝生成 約180円）。もみじは見出しにかからない隅に置き直している | 10月の新メニュー／極 焼きいもスープ |
| 2 | 図解：カップの中へ線が伸びる（`bg_callout.py zukai.json`） | こだわりの野菜／さつまいも・かぼちゃ・たまねぎ（括り線でひとまとまり）／枝豆・もち麦（別の線）／大学芋・黒ごませんべい（上のトッピング）／さつまいもは ヘルシーファーム（差し色）／スープの野菜は すべて兵庫県産 |
| 3 | カップに寄る | 極 焼きいもスープ／¥600 |
| 4 | 店の前・外観（`video/cal_reel/clips/03a・03b` を使い回す。文字はクリーム） | 場所・行き方 |
| 5 | 10月のカレンダー（カップなし・下の文字と離す） | 10月は 月・火・木／11:00 – 14:00／20日（火）はお休み・12日（祝）は営業します |
| 6 | ロゴ（10月の営業日リールの `video/cal_reel/clips/05_end.mp4`・金色の地。文字はクリーム） | 詳しくは公式LINEで／プロフィールのリンクから |

地が明るい（ベージュ）カットの文字は焦げ茶（plan の `"color": "brown"`）、差し色は `terra`。実写とロゴのカットだけクリーム。

2・3・5 の地は `src/autumn_bg.mp4`（キービジュアルのもみじを切り抜いて四隅で揺らし、コードで作るので無料）。

## 作る順（代表PC）

```bash
cd video/imo_reel
S=../../.claude/skills/reel-capcut/scripts
# 0. src/ に kv_autumn.jpg（商大祭キービジュアル）と cup_green.png（グリーンバックのカップ）を置く
python build_bg.py                         # 1 の元絵・もみじ・秋の背景・2・3・5 の背景動画（無料）
# 1. 最初のカットを動かす（約180円・承認をもらってから）
python $S/gen_clip.py 実行 clips/01_imo_raw.mp4 src/01_imo_916.png "Slow food-commercial motion. Thin glossy golden syrup keeps pouring from the top of the frame onto the split roasted sweet potato and slowly drips down its flesh. The maple leaves sway gently back and forth as if in a light breeze. Soft steam rises from the soup cup. The soup cup, its toppings and the logo stay completely still."
python $S/prep_clip.py clips/01_imo_raw.mp4 clips/01_imo_drip.mp4 --t 6
python $S/make_draft.py plan.json          # CapCut を再起動して開く
```

- 無料でやるなら、`src/01_imo_916.png` と上の指示文を Dreamina か CapCut の AI動画生成に手で入れる
- 店では大学芋単品を売らないので、元絵では大学芋の器とソフトクリームを消してカップの後ろに隠している
- 元画像・mp4・png はコミットしない
