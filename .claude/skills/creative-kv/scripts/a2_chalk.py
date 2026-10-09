"""A2縦 黒板（手書き風）メニュー看板。
使い方: python a2_chalk.py config.json chalk_bg.png 出力名（拡張子なし）
chalk_bg は gen.py で「上と中央を空けた黒板」を生成したもの。価格は「300円」のように円表記にする（ポップ体に ¥ が無い）。"""
import sys, json
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from fonts import font
from common import fit, text_w

cfg = json.load(open(sys.argv[1], encoding="utf-8")); bgp = sys.argv[2]; outp = sys.argv[3]
DPI = 150; W = round(426 / 25.4 * DPI); H = round(600 / 25.4 * DPI); S = W / 1080
bg = fit(Image.open(bgp), W, H)
rng = np.random.default_rng(3)
noise = Image.fromarray((rng.random((H, W)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))

def chalk(txt, f, cx, y, color, sp=0, strength=0.55):
    """チョーク風：粒子でかすれさせ、うっすら光らせる"""
    layer = Image.new("L", (W, H), 0); d = ImageDraw.Draw(layer)
    x = cx - text_w(d, txt, f, sp) / 2
    for c in txt:
        d.text((x, y), c, font=f, fill=255); x += d.textlength(c, font=f) + sp
    a = np.array(layer).astype(np.float32) / 255 * (1 - strength + strength * np.array(noise).astype(np.float32) / 255)
    glow = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
    g = Image.new("RGBA", (W, H), color + (0,)); g.putalpha(glow.point(lambda v: int(v * 0.35))); bg.alpha_composite(g)
    col = Image.new("RGBA", (W, H), color + (0,)); col.putalpha(Image.fromarray((a * 255).astype(np.uint8))); bg.alpha_composite(col)

def yen_to_en(s):
    s = s.replace("¥", "").replace("￥", "")
    return s if "円" in s else s + "円"

WHITE = (240, 238, 228); YEL = (255, 225, 120); PINK = (255, 170, 150); ORG = (255, 190, 110)
cx = W / 2
chalk(cfg["headline"], font("pop", int(112 * S)), cx, int(200 * S), YEL, int(4 * S))
if cfg.get("date"):
    chalk(cfg["date"], font("kyokasho", int(48 * S)), cx, int(340 * S), WHITE, int(4 * S))
y = int(470 * S); d = ImageDraw.Draw(bg, "RGBA")
for k, it in enumerate(cfg["items"]):
    chalk(it["name"], font("pop", int(84 * S)), cx - int(170 * S), y, WHITE, int(4 * S))
    if it.get("price"):
        chalk(yen_to_en(it["price"]), font("pop", int(110 * S)), cx + int(300 * S), y - int(16 * S), YEL)
    if it.get("desc"):
        chalk(it["desc"], font("kyokasho", int(36 * S)), cx, y + int(108 * S), WHITE, int(3 * S), 0.5)
    if k < len(cfg["items"]) - 1:
        for x in range(int(220 * S), int(860 * S), int(28 * S)):
            d.line([(x, y + int(180 * S)), (x + int(14 * S), y + int(180 * S))], fill=WHITE + (170,), width=int(3 * S))
    y += int(220 * S)
if cfg.get("offer"):
    cyc = y + int(20 * S); r = int(95 * S)
    d.ellipse([cx - r * 1.6, cyc - r * 0.85, cx + r * 1.6, cyc + r * 0.85], outline=PINK + (220,), width=int(4 * S))
    chalk(yen_to_en(cfg["offer"]).replace("円引き円", "円引き"), font("pop", int(60 * S)), cx, cyc - int(36 * S), PINK, int(3 * S))
    y = cyc + int(110 * S)
if cfg.get("sub"):
    chalk(cfg["sub"], font("kyokasho", int(38 * S)), cx, y, ORG, int(4 * S)); y += int(65 * S)
chalk(cfg["brand"] + ("  by " + cfg["by"] if cfg.get("by") else ""), font("kyokasho", int(40 * S)), cx, y, WHITE, int(4 * S))
o = bg.convert("RGB")
o.save(outp + "_bleed.jpg", quality=94, dpi=(DPI, DPI)); o.save(outp + "_bleed.pdf", resolution=DPI)
o.resize((W // 3, H // 3), Image.LANCZOS).save(outp + "_preview.jpg", quality=90)
print("saved", outp)
