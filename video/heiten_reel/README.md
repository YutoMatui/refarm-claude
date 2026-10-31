# 11月閉店動画（2026-10-31）

様式③「お知らせ（速いカット）」の最初の実例。決まりは `.claude/skills/reel-capcut/reference/style_promo.md`。
台本＝Notion「11月閉店動画」、メンバー向けの説明＝その子ページ「まいへの説明資料：11月閉店動画の作り方」。

## 作り直し方

```bash
python ../../.claude/skills/reel-capcut/scripts/montage.py montage.json   # 背景動画（文字なし）を clips_v3/ に
python build_bg_v3.py 08                                                  # インスタの画面（08_insta.mp4）だけはこちら
python make_plan_v3.py                                                    # 文字を直したらここ → plan_v3.json
python ../../.claude/skills/reel-capcut/scripts/make_draft.py plan_v3.json      # CapCut の下書き「11月閉店動画_v3」
python ../../.claude/skills/reel-capcut/scripts/render_mp4.py plan_v3.json 11月閉店動画_仮v3.mp4   # 確認用
```

素材は Drive「50日企画素材」（`11月閉店動画_素材候補`・`道案内`・`間借り`・`食べログ`・`完成動画`）。
背景動画と確認用の mp4 は Drive「完成動画/11月閉店動画_背景動画v3（文字なし）」と「完成動画/11月閉店動画_仮v3.mp4」。
`src/insta_profile.jpg`（インスタの画面のスクショ）はリポジトリに入れていないので、使うときは Drive から置く。

## 直された経緯（第1版・第2版は不採用。スクリプトはリポジトリに入れていない）

- 第1版：「論外」。ガッツポーズで始まる、金・クリームの文字、閉店しますに席を案内する手、赤いカード、カレーの時の写真、遅い
- 第2版：「短すぎ」（0.45秒ずつ）。そのあと1秒に直して「いい感じ」。ただし暗い・画質が悪い（iPhone の HDR を変換していなかった）
- 第3版：HDR の色変換、閉店します＝お辞儀、オープン＝のぼり・2F看板・手を振る、やめたメンバーが写る写真を外す、「神戸市のマルシェやイベント」
