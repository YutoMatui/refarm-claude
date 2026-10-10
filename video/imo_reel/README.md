# 10月の新メニュー「極 焼きいもスープ」リール（様式 restaurant・約35秒）

| 順 | 背景動画（文字なし） | 作り方 |
|---|---|---|
| 1 | スプーンからスープが垂れる | `build_bg.py` が元絵 `src/01_spoon_916.png` を作る → `gen_clip.py 実行 clips/01_spoon_drip.mp4 src/01_spoon_916.png "…"`（約180円・要承認）→ `prep_clip.py --t 5.5` で短く |
| 2 | 図解：中の材料へ線が伸びる 8秒 | `bg_callout.py zukai.json`（線の位置は zukai.json。文字は plan の telop に `x`・`y`） |
| 3 | カップに寄る 3.5秒 | `build_bg.py` |
| 4 | 10月のカレンダー 7秒 | `bg_calendar.py`（営業日は 10月の営業日リールと同じ） |
| 5 | 店の前・外観 | `video/cal_reel/clips/03a・03b` を使い回す |
| 6 | 金色の地にロゴ 4秒 | `bg_end.py` |

- `python build_bg.py` で 2・3・4・6 と 1 の元絵がそろう（Windows で実行。ロゴのフォントは Windows 同梱）
- 元画像（`src/cup_green.png`・`src/kv_spoon_green.png`＝グリーンバックの生成画像）と mp4 はコミットしない
- 店では大学芋単品を売らないので、大学芋単品が写った商大祭のキービジュアルは使わない
