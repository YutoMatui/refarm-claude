# -*- coding: utf-8 -*-
"""さつまいも版のぼり（2026-10-09）＝ nobori_line.py（zen）の骨格そのまま。
変更点: 見出し「丸ごと 焼き芋スープ」／リボンの文言（約半分→別フレーズ）／線画をさつまいも・かぼちゃ・玉ねぎ・もみじに／
        写真をクリエイティブと同じ「スプーンで持ち上げた焼き芋スープ（大学芋のせ）」に（img_candidates/IMO_spoon_cut.png）
使い方: python nobori_imo.py [A|B|C]  → nobori_imo_{A,B,C}.pdf / _preview.png / _cmp_imo.png"""
import os, sys
from PIL import Image
import build_nobori as B
sys.path.insert(0, B.BRAND)
from build_print import logo_1line
import nobori_line as L
os.chdir(B.HERE)
W, H = B.W, B.H
CORAL, CORAL_D, INK, CREAM, WHITE = L.CORAL, L.CORAL_D, L.INK, L.CREAM, L.WHITE
HEAD, SUB = L.FONTS["zen"]
RIBBONS = {
    "A": [("100%神戸産さつまいも", SUB, 40, INK)], 
    "B": [("揚げたて大学芋をのせた", SUB, 40, INK)],
    "C": [("とろ〜り、ほくほく。", SUB, 40, INK)],
}
RIBBON2 = {
    "A": [("大学芋", HEAD, 88, CORAL_D), ("のせ", SUB, 52, CORAL_D)],
    "B": [("極", HEAD, 88, CORAL_D), ("焼き芋スープ", HEAD, 64, CORAL_D)],
    "C": [("神戸の", SUB, 52, CORAL_D), ("秋の味", HEAD, 88, CORAL_D)],
}
TITLE2 = {"A": "焼き芋スープ", "B": "焼き芋スープ", "C": "焼き芋スープ"}

def build(key):
    b = [f'<rect width="{W}" height="{H}" fill="{CORAL}"/>']
    L.center(b, SUB, "神戸の農家さんの", 100, 40, CREAM, 3)
    L.center(b, HEAD, "丸ごと", 266, 162, WHITE, 6)
    L.center(b, HEAD, TITLE2[key], 396, 86, WHITE, 1)
    # 線画（さつまいも・かぼちゃ・玉ねぎ・もみじ）
    b.append(L.veg("sweetpotato", 14, 690, 215, -6))
    b.append(L.veg("pumpkin", 420, 676, 165, 10))
    b.append(L.veg("onion2", 10, 1236, 160, 4))
    b.append(L.veg("mapleleaf", 428, 1250, 158, -12))
    # 写真：スプーンで持ち上げた焼き芋スープ（クリエイティブと同じ）
    iw, ih = 672, 1029; cw = 600.0; BOT = 1472
    ch = cw * ih / iw; ix = W / 2 - 0.4055 * cw; iy = BOT - ch
    b.append('<defs><filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter></defs>')
    b.append(f'<ellipse cx="{W/2:.1f}" cy="{BOT - 6}" rx="190" ry="22" fill="#6B2A2A" opacity="0.28" filter="url(#blur)"/>')
    b.append(f'<image href="img_candidates/IMO_spoon_cut.png" x="{ix:.1f}" y="{iy:.1f}" width="{cw}" height="{ch:.1f}"/>')
    # リボン（位置は元のまま）
    y0, h = 474, 176; x0, x1, n = 18, W - 18, 22; ym = y0 + h / 2
    pts = [(x0, y0), (x1, y0), (x1 - n, ym), (x1, y0 + h), (x0, y0 + h), (x0 + n, ym)]
    b.append(f'<g filter="url(#sh2)"><polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{CREAM}"/></g>')
    L.runs(b, y0 + 58, RIBBONS[key], 1.5)
    L.runs(b, y0 + 150, RIBBON2[key], 4)
    # 下のブロック
    y0 = 1540
    b.append(f'<rect x="0" y="{y0}" width="{W}" height="{H - y0}" fill="{WHITE}"/>')
    b.append(logo_1line(W / 2, y0 + 100, 420, INK, WHITE, CORAL, INK))
    t = "テイクアウトOK"; pw_ = L.gw(SUB, t, 28, 1.5) + 50; py = y0 + 170
    b.append(f'<rect x="{W/2 - pw_/2:.1f}" y="{py}" width="{pw_:.1f}" height="46" rx="23" fill="{CORAL}"/>')
    b.append(SUB.draw(t, W / 2, py + 33, 28, WHITE, "middle", track=1.5))
    return "".join(b)

if __name__ == "__main__":
    KEYS = sys.argv[1:] or ["A", "B", "C"]
    for k in KEYS:
        B.write_page(f"nobori_imo_{k}", build(k), f"VEGEONE のぼり さつまいも版 {k}")
    ims = [Image.open(f"nobori_imo_{k}_preview.png").convert("RGB") for k in KEYS]
    gap = 40; c = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) + 1), ims[0].height + gap * 2), "#cfcbc4")
    x = gap
    for i in ims: c.paste(i, (x, gap)); x += i.width + gap
    c.save("_cmp_imo.png"); print("done")
