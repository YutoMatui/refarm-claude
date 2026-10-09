"""のぼり 600×1800mm（1:3）。縦書き2本＋下にブランド。
使い方: python nobori.py config.json base_9x16.png 出力名（拡張子なし）
base は gen.py で 9:16・商品を下45%に寄せて生成したもの。上は背景色で延長する。
出力: 出力名_100dpi.jpg（2362×7087）／ 出力名_preview.jpg
config の "nobori": {"line1":"揚げたて大学芋","line2":"極 焼き芋スープ"} を使う（無ければ items の名前）。"""
import sys, json
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from fonts import font
from common import CREAM, spaced

cfg = json.load(open(sys.argv[1], encoding="utf-8")); basep = sys.argv[2]; outp = sys.argv[3]
W, H = 1200, 3600
src = Image.open(basep).convert("RGBA"); sw, sh = src.size
base = src.resize((W, int(sh * W / sw)), Image.LANCZOS); bh = base.size[1]
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
# 上を背景色で延長（最上段の中央値→大きくぼかす）
a = np.array(base.convert("RGB")).astype(np.float32); top = np.median(a[:12], axis=0)
ext = np.zeros((H - bh, W, 3), np.float32)
for i in range(H - bh):
    ext[i] = top * (0.92 + 0.08 * (i / (H - bh)))
ext = Image.fromarray(ext.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)).convert("RGBA")
canvas.paste(ext, (0, 0)); canvas.alpha_composite(base, (0, H - bh))
# 継ぎ目を600pxでなじませる
seam = 600
top_band = base.crop((0, 0, W, seam)).convert("RGB"); ext_band = ext.crop((0, ext.size[1] - seam, W, ext.size[1])).convert("RGB")
mask = Image.linear_gradient("L").resize((W, seam))
canvas.paste(Image.composite(top_band, ext_band, mask), (0, H - bh))
d = ImageDraw.Draw(canvas, "RGBA")
# 蜜の線が上から来ている絵なら、上端まで伸ばす
row = np.array(base.convert("RGB")).astype(int)[5]; dark = np.where((row[:, 0] - row[:, 2]) > 120)[0]
if len(dark):
    sx = int(dark.mean())
    for dx, al in ((-6, 90), (-3, 170), (0, 230), (3, 170), (6, 90)):
        d.line([(sx + dx, 0), (sx + dx, H - bh + 40)], fill=(200, 110, 20, al), width=3)

def vtext(txt, f, x_center, y, fill, gap=0):
    """縦書き（長音は回転）。チチ（上・左60px）を避けて置く"""
    y0 = y
    for c in txt:
        if c in "ー－":
            tmp = Image.new("RGBA", (f.size * 2, f.size * 2), (0, 0, 0, 0))
            ImageDraw.Draw(tmp).text((f.size // 2, f.size // 4), c, font=f, fill=fill)
            tmp = tmp.rotate(-90, resample=Image.BICUBIC); tmp = tmp.crop(tmp.getbbox())
            canvas.alpha_composite(tmp, (int(x_center - tmp.size[0] / 2), int(y0 + (f.size - tmp.size[1]) / 2)))
            y0 += f.size + gap; continue
        w = d.textlength(c, font=f)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((x_center - w / 2, y0 + 6), c, font=f, fill=(40, 15, 0, 160))
        canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(canvas, "RGBA").text((x_center - w / 2, y0), c, font=f, fill=fill)
        y0 += f.size + gap

nb = cfg.get("nobori", {})
line1 = nb.get("line1", cfg["items"][0]["name"]); line2 = nb.get("line2", cfg["items"][1]["name"] if len(cfg["items"]) > 1 else "")
vtext(line1, font("mincho_heavy", 165), W * 0.62, 150, CREAM, gap=14)
if line2:
    vtext(line2, font("mincho_heavy", 130), W * 0.30, 170, CREAM, gap=10)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for i in range(260):
    od.line([(0, H - 260 + i), (W, H - 260 + i)], fill=(60, 22, 0, int(200 * (i / 260) ** 1.2)))
canvas = Image.alpha_composite(canvas, ov); d = ImageDraw.Draw(canvas, "RGBA")
spaced(d, cfg["brand"], font("serif_en", 84), W / 2, H - 200, CREAM, 16)
if cfg.get("by"):
    spaced(d, cfg["by"], font("mincho_heavy", 44), W / 2, H - 100, CREAM, 6)
out = canvas.convert("RGB")
out.resize((2362, 7087), Image.LANCZOS).save(outp + "_100dpi.jpg", quality=92, dpi=(100, 100))
out.resize((600, 1800), Image.LANCZOS).save(outp + "_preview.jpg", quality=90)
print("saved", outp)
