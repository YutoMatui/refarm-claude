"""A2縦（420×594mm・塗り足し3mm・150dpi）の写真系メニュー看板。
使い方: python a2_real.py config.json base.png 出力名（拡張子なし）
出力: 出力名_bleed.jpg / 出力名_bleed.pdf / 出力名_preview.jpg"""
import sys, json
from PIL import Image, ImageDraw
from fonts import font
from common import CREAM, GOLD, fit, darken_bands, spaced, shadow_text, text_w

cfg = json.load(open(sys.argv[1], encoding="utf-8")); base = sys.argv[2]; outp = sys.argv[3]
DPI = 150; W = round(426 / 25.4 * DPI); H = round(600 / 25.4 * DPI); S = W / 1080
im = fit(Image.open(base), W, H, cfg.get("shift_up_a2", 175))
im = darken_bands(im, 0.26, 0.36, 110, 215)
cx = W / 2
shadow_text(im, cfg["headline"], font("mincho_heavy", int(118 * S)), cx, int(70 * S), CREAM, sp=int(6 * S), blur=int(10 * S))
if cfg.get("date"):
    shadow_text(im, cfg["date"], font("mincho_heavy", int(50 * S)), cx, int(225 * S), CREAM, sp=int(4 * S), blur=int(8 * S))
d = ImageDraw.Draw(im, "RGBA")
y = int(H * 0.708)
for it in cfg["items"]:
    fn = font("mincho_heavy", int(60 * S)); fp = font("serif_en_bold", int(78 * S))
    nw = text_w(d, it["name"], fn, int(3 * S)); pw = text_w(d, it.get("price", ""), fp)
    left = cx - (nw + pw + int(40 * S)) / 2
    spaced(d, it["name"], fn, left + nw / 2, y, CREAM, int(3 * S))
    d.text((left + nw + int(40 * S), y - int(14 * S)), it.get("price", ""), font=fp, fill=CREAM)
    if it.get("desc"):
        spaced(d, it["desc"], font("mincho_bold", int(26 * S)), cx, y + int(78 * S), GOLD, int(3 * S))
    y += int(125 * S)
if cfg.get("offer"):
    spaced(d, cfg["offer"], font("mincho_heavy", int(40 * S)), cx, y + int(20 * S), CREAM, int(3 * S)); y += int(50 * S)
if cfg.get("sub"):
    spaced(d, cfg["sub"], font("mincho_bold", int(26 * S)), cx, y + int(60 * S), GOLD, int(4 * S))
d.line([(cx - int(140 * S), H - int(118 * S)), (cx + int(140 * S), H - int(118 * S))], fill=GOLD, width=max(2, int(1.5 * S)))
spaced(d, cfg["brand"], font("serif_en", int(40 * S)), cx, H - int(110 * S), CREAM, int(10 * S))
if cfg.get("by"):
    spaced(d, "by " + cfg["by"], font("mincho_bold", int(24 * S)), cx, H - int(60 * S), CREAM, int(2 * S))
o = im.convert("RGB")
o.save(outp + "_bleed.jpg", quality=94, dpi=(DPI, DPI)); o.save(outp + "_bleed.pdf", resolution=DPI)
o.resize((W // 3, H // 3), Image.LANCZOS).save(outp + "_preview.jpg", quality=90)
print("saved", outp)
