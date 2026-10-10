# 10月の営業日リール（店の告知動画の型）

- `build_cal.py`：1本目（静止画＋ズーム・文字焼き込み）。`REEL_STYLE=pop|restaurant`
- `build_bg.py`：**文字なしの背景動画**（カレンダーが1日ずつ出る7秒／金色の地にワードマーク4秒）→ `clips/`
- `plan_restaurant.json`：背景動画を並べて文字を書いた plan。`python ../../.claude/skills/reel-capcut/scripts/make_draft.py plan_restaurant.json` で CapCut ドラフト、`render_mp4.py` で確認用 mp4
- `clips/01_kv_syrup.mp4`・`04_kv_steam.mp4`：キービジュアル（`src/kv_916_crop.png`）を `gen_clip.py` で動かしたもの（Veo・各約180円）。`03a_person_wave.mp4`＝店の前で手を振る実写（IMG_2569）、`03b_gaikan.mp4`＝外観
- 元の写真（`kv.png` `gaikan.jpg` `key_soup.png` など）と出力 mp4 はコミットしない。完成品は Drive `50日企画素材/完成動画/`
