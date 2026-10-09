"""4:5（1080×1350）のキービジュアルに文字を乗せる。
使い方: python kv_text.py config.json base.png out.jpg
config は templates/kv.example.json を参照。"""
import sys, json
from PIL import Image, ImageDraw
from fonts import font
from common import CREAM, GOLD, fit, darken_bands, spaced, shadow_text

cfg = json.load(open(sys.argv[1], encoding="utf-8")); base = sys.argv[2]; out = sys.argv[3]
W, H = 1080, 1350
im = fit(Image.open(base), W, H, cfg.get("shift_up", 60))
im = darken_bands(im)
cx = W / 2
shadow_text(im, cfg["headline"], font("mincho_heavy", 116), cx, 58, CREAM, sp=6)
if cfg.get("date"):
    shadow_text(im, cfg["date"], font("mincho_heavy", 50), cx, 214, CREAM, sp=4, blur=8, alpha=170)
d = ImageDraw.Draw(im, "RGBA")
items = " ／ ".join((it["name"] + " " + it["price"]) if it.get("price") else it["name"] for it in cfg["items"])
spaced(d, items, font("mincho_heavy", 42), cx, H - 212, CREAM, 2)
if cfg.get("sub"):
    spaced(d, cfg["sub"], font("mincho_bold", 28), cx, H - 146, GOLD, 4)
d.line([(cx - 140, H - 104), (cx + 140, H - 104)], fill=GOLD, width=1)
spaced(d, cfg["brand"], font("serif_en", 40), cx, H - 94, CREAM, 10)
if cfg.get("by"):
    spaced(d, "by " + cfg["by"], font("mincho_bold", 24), cx, H - 46, CREAM, 2)
im.convert("RGB").save(out, quality=93)
print("saved", out)
