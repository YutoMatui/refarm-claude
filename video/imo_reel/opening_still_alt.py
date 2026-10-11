# -*- coding: utf-8 -*-
"""最初のカットの元絵（2026-10-11 第2案）：カップを小さく右へ寄せ、蜜の落ちる所（画面 x≈543, y≈800）をカップから離す。
カップをずらすと見えてしまう「大学芋の器を消した跡」は、右側の無地の地色で塗り直してからカップともみじを置く。
  python opening_still_alt.py  → src/01_imo_916_alt.png"""
import numpy as np, cv2, os
from PIL import Image, ImageDraw, ImageFilter
import build_bg as bb
P, B = bb.P, bb.B
Z, OY, CW, BY, CX = 1.45, 120, 680, 1692, 740
kv = np.array(Image.open(P("src", "kv_autumn.jpg")).convert("RGB"))
mask = np.zeros(kv.shape[:2], np.uint8)
for r in [(115, 690, 515, 1095), (200, 505, 395, 760), (430, 495, 845, 995)] + list(bb.LEAF_BOX.values()):
    cv2.rectangle(mask, r[:2], r[2:], 255, -1)
clean = cv2.inpaint(kv, mask, 25, cv2.INPAINT_TELEA)
W, H = B.W, B.H; kw, kh = int(896 * Z), int(1152 * Z)
a = np.array(Image.fromarray(clean).resize((kw, kh), Image.LANCZOS)).astype(np.float32)
ox, oy = (W - kw) // 2, int(OY)
topc = cv2.GaussianBlur(a[8:9], (0, 0), 60)[0][-ox:-ox + W]; botc = cv2.GaussianBlur(a[-2:-1], (0, 0), 60)[0][-ox:-ox + W]
can = np.array([topc * (1 - y / H) + botc * (y / H) for y in range(H)], np.float32)
y0, y1 = max(0, oy), min(H, oy + kh); can[y0:y1] = a[y0 - oy:y1 - oy, -ox:-ox + W]
blur = cv2.GaussianBlur(can, (0, 0), 25)
for yb in (oy, oy + kh):
    for dy in range(-50, 50):
        if 0 <= yb + dy < H:
            w = 1 - abs(dy) / 50; can[yb + dy] = can[yb + dy] * (1 - w) + blur[yb + dy] * w
# 消した跡（左下）を、同じ高さの右側の無地（x 1000〜1060）の色で塗り直す。境目は60pxでなじませる
X1, Y0f = 480, 980
ref = can[:, 1000:1060].mean(axis=1, keepdims=True)                    # (H,1,3)
fill = np.repeat(ref, X1, axis=1)
fill = cv2.GaussianBlur(fill, (0, 0), 3)
wx = np.clip((X1 - np.arange(X1)) / 60.0, 0, 1)[None, :, None]          # 右端でフェード
wy = np.clip((np.arange(H) - Y0f) / 60.0, 0, 1)[:, None, None]           # 上端でフェード
w = wx * wy
can[:, :X1] = can[:, :X1] * (1 - w) + fill * w
im = Image.fromarray(can.clip(0, 255).astype(np.uint8)).convert("RGBA")
cup = bb.cup_cut(); cup = cup.resize((CW, int(cup.height * CW / cup.width)), Image.LANCZOS)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse([CX - CW * 0.42, BY - 50, CX + CW * 0.46, BY + 30], fill=(80, 35, 5, 130))
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30))); im.alpha_composite(cup, (CX - CW // 2, BY - cup.height))
for n, wdt, x, y in [("red", 250, -10, 10), ("orange", 230, 850, 20), ("yellow", 120, 20, 520),
                     ("orange", 260, 150, 820), ("orange", 260, 30, 1250), ("red", 200, 120, 1500)]:   # (40,800) は消した跡のぼけを隠す
    lf = Image.open(P("src", "leaf_%s.png" % n)); lf = lf.resize((wdt, int(lf.height * wdt / lf.width)), Image.LANCZOS)
    im.alpha_composite(lf, (x, y))
im.convert("RGB").save(P("src", "01_imo_916_alt.png")); print("できました: src/01_imo_916_alt.png")
