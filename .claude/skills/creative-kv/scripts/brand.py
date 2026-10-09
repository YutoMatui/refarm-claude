"""VEGEONE のワードマーク（Gill Sans Ultra Bold、O がトマト）を Pillow で描く。
wordmark(height_px, color, tomato=(red, calyx)) -> RGBA image"""
from PIL import Image, ImageDraw, ImageFont
import os
F = os.environ.get("WINDIR", "C:/Windows") + "/Fonts/"

def _gill(size):
    for n in ("GILSANUB.TTF", "GIL_____.TTF", "ARLRDBD.TTF", "arialbd.ttf"):
        if os.path.exists(F + n):
            return ImageFont.truetype(F + n, size)
    return ImageFont.load_default()

def _quad(p0, p1, p2, n=10):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]) for t in [i / n for i in range(n + 1)]]

def tomato(d, cx, cy, r, red=(217, 52, 43, 255), calyx=(40, 60, 35, 255)):
    """ロゴSVGのトマト（円＋4枚のへた）を半径 r で描く。SVGでは円r=5.916・へたは中心(22.979,40.763)基準"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=red)
    s = r / 5.916; ox, oy = cx - 22.979 * s, cy - 44.229 * s
    def P(x, y): return (ox + x * s, oy + y * s)
    c = (22.979, 40.763)
    petals = [((21.877, 42.469), (20.133, 42.406), (20.951, 40.865)),
              ((21.028, 41.327), (19.753, 40.136), (21.382, 39.509)),
              ((24.577, 39.509), (26.205, 40.136), (24.930, 41.327)),
              ((25.008, 40.865), (25.826, 42.406), (24.082, 42.469))]
    for a, b, cc in petals:
        pts = _quad(P(*c), P(*a), P(*b)) + _quad(P(*b), P(*cc), P(*c))
        d.polygon(pts, fill=calyx)
    d.ellipse([cx - 0.598 * s, oy + (40.763 - 0.598) * s, cx + 0.598 * s, oy + (40.763 + 0.598) * s], fill=calyx)

def wordmark(height, color=(255, 255, 255, 255), red=(217, 52, 43, 255), calyx=(40, 60, 35, 255), spacing=0.0):
    f = _gill(height)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    parts = ["VEGE", "O", "NE"]
    widths = [tmp.textlength(p, font=f) for p in parts]
    gap = height * spacing
    W = int(sum(widths) + gap * 6) + 10; H = int(height * 1.3)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = 5; base_y = int(height * 0.08)
    for i, p in enumerate(parts):
        if p == "O":
            bb = d.textbbox((x, base_y), "O", font=f)
            cx = (bb[0] + bb[2]) / 2; cy = (bb[1] + bb[3]) / 2; r = (bb[3] - bb[1]) / 2 * 0.98
            tomato(d, cx, cy, r, red, calyx)
        else:
            for ch in p:
                d.text((x, base_y), ch, font=f, fill=color); x += d.textlength(ch, font=f) + gap
            continue
        x += widths[i] + gap
    return im.crop(im.getbbox())

if __name__ == "__main__":
    wordmark(200).save("wordmark_test.png"); print("ok")
