# 別のPCで creative-kv を動かす手順

## 必要なもの
1. **このリポジトリ**（`refarm-cc-company`）を clone する。スキル本体は `.claude/skills/creative-kv/`。
   のぼりのPDF出力は `vegeone_nobori/`（骨格）と `vegeone_brand/`（ロゴ描画 `build_print.py`）も使う。
2. **Claude Code**（Pro以上のアカウント）。リポジトリのフォルダで起動すると `/creative-kv` が使える。
3. **Python 3.11以上** と `pip install pillow numpy opencv-python`
4. **Gemini APIキー**：環境変数 `GEMINI_API_KEY` に設定（Windows: 設定→システム→環境変数）。キーはリポジトリに入れない。
5. **Google Chrome**（のぼり・看板のPDF出力に headless で使う。`vegeone_nobori/build_nobori.py` の `CHROME` のパスを合わせる）
6. **フォント**
   - Windows＋Office があれば HG明朝E／HG創英角ゴシックUB／HG創英角ポップ体 が入っている（無ければ游明朝などに自動で代替）
   - のぼりの骨格は Google Fonts の Zen Maru Gothic・Dela Gothic One を `~/tools/fonts/` に置く前提（無料・OFL）。無い場合は `vegeone_nobori/nobori_line.py` の `FD` を直す

## 動作確認（5分）
```bash
cd .claude/skills/creative-kv/scripts
python kv_text.py ../templates/kv.example.json ../reference/examples/kv_refarm_shodaisai_final.jpg test_kv.jpg
```
`test_kv.jpg` ができれば文字乗せは動いている。Gemini は
```bash
python gen.py --out test.png --aspect 1:1 --prompt "a red tomato on white background, photo"
```
で画像が返れば OK。

## 何がこのリポジトリに入っていて、何が入っていないか
- 入っている：手順（SKILL.md）、スクリプト、文言の設定例、手本画像、商品の切り抜き素材、ロゴの描画、既存ののぼりの骨格、学び（lessons.md）
- 入っていない：APIキー、Chrome、フォント本体、**判断する目**（どの案がよいか・ダサいか）。最後の判断はゆうとか、ゆうとが基準を伝えた人がする
