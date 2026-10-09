# -*- coding: utf-8 -*-
"""さつまいも版のぼり・金色（2026-10-09 ゆうと「さつまいもなんだから黄色っぽく。スープ画像はA型看板と同じ。リボンは真ん中の文言。A型看板の色合いと揃える」）
骨格は nobori_line.py（zen）。地色＝キービジュアル（sb_A_real2）の金色グラデ、文字＝クリーム、下のブロック＝焦げ茶にクリームのロゴ。
写真＝A2看板と同じカップ（key_soup の切り抜き IMO_cup_cut.png）。
使い方: python nobori_imo_gold.py → nobori_imo_gold.pdf / _preview.png"""
import os, sys
from PIL import Image
import build_nobori as B
sys.path.insert(0, B.BRAND)
from build_print import logo_1line
import nobori_line as L
os.chdir(B.HERE)
W, H = B.W, B.H
GOLD_TOP, GOLD_MID, GOLD_BOT = "#D59040", "#C5761F", "#B86A1E"   # sb_A_real2 の地色から
CREAM, WHITE = "#FFF7E6", "#FFFFFF"
BROWN = "#3C1A08"          # 下のブロック
ACCENT = "#B5561B"         # リボンの文字（焦げたオレンジ）
HEAD, SUB = L.FONTS["zen"]

IMGS={"cup":("IMO_cup_cut.png",595,707,470.0,0.494),"spoon":("IMO_cup_spoon_cut.png",None,None,560.0,None)}
def build(variant="cup"):
    b = [f'<defs><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{GOLD_TOP}"/><stop offset="0.55" stop-color="{GOLD_MID}"/><stop offset="1" stop-color="{GOLD_BOT}"/></linearGradient>'
         f'<radialGradient id="glow" cx="0.5" cy="0.62" r="0.55"><stop offset="0" stop-color="#F3B860" stop-opacity="0.75"/><stop offset="1" stop-color="#F3B860" stop-opacity="0"/></radialGradient>'
         f'<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#gold)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>']
    # 見出し
    L.center(b, SUB, "神戸の農家さんの", 100, 40, CREAM, 3)
    L.center(b, HEAD, "丸ごと", 266, 162, CREAM, 6)
    L.center(b, HEAD, "焼き芋スープ", 396, 86, CREAM, 1)
    # 線画（白・少し薄く）
    b.append(L.veg("sweetpotato", 14, 690, 215, -6, 0.8))
    b.append(L.veg("pumpkin", 420, 676, 165, 10, 0.8))
    b.append(L.veg("onion2", 10, 1236, 160, 4, 0.8))
    b.append(L.veg("mapleleaf", 428, 1250, 158, -12, 0.8))
    # 写真：A2看板と同じカップ（大学芋・黒ごま煎餅のせ）
    fn, iw, ih, cw, cf = IMGS[variant]
    if iw is None:
        import numpy as np
        _im = Image.open(os.path.join("img_candidates", fn)); iw, ih = _im.size
        _a = np.array(_im.split()[3]); _c = np.where(_a[int(ih * 0.85)] > 128)[0]; cf = (_c.min() + _c.max()) / 2 / iw
    BOT = 1472; ch = cw * ih / iw; ix = W / 2 - cf * cw; iy = BOT - ch
    b.append(f'<ellipse cx="{W/2:.1f}" cy="{BOT - 6}" rx="200" ry="24" fill="#5A2A08" opacity="0.35" filter="url(#blur)"/>')
    b.append(f'<image href="img_candidates/{fn}" x="{ix:.1f}" y="{iy:.1f}" width="{cw}" height="{ch:.1f}"/>')
    # リボン（真ん中の文言）
    y0, h = 474, 176; x0, x1, n = 18, W - 18, 22; ym = y0 + h / 2
    pts = [(x0, y0), (x1, y0), (x1 - n, ym), (x1, y0 + h), (x0, y0 + h), (x0 + n, ym)]
    b.append(f'<g filter="url(#sh2)"><polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{CREAM}"/></g>')
    L.runs(b, y0 + 58, [("揚げたて大学芋をのせた", SUB, 40, "#4A2A12")], 1.5)
    L.runs(b, y0 + 150, [("極", HEAD, 88, ACCENT), ("焼き芋スープ", HEAD, 64, ACCENT)], 4)
    # 下のブロック（焦げ茶にクリームのロゴ）
    y0 = 1540
    b.append(f'<rect x="0" y="{y0}" width="{W}" height="{H - y0}" fill="{BROWN}"/>')
    b.append(logo_1line(W / 2, y0 + 100, 420, CREAM, BROWN, "#E24B3C", BROWN))
    t = "テイクアウトOK"; pw_ = L.gw(SUB, t, 28, 1.5) + 50; py = y0 + 170
    b.append(f'<rect x="{W/2 - pw_/2:.1f}" y="{py}" width="{pw_:.1f}" height="46" rx="23" fill="{CREAM}"/>')
    b.append(SUB.draw(t, W / 2, py + 33, 28, BROWN, "middle", track=1.5))
    return "".join(b)

if __name__ == "__main__":
    B.write_page("nobori_imo_gold", build("cup"), "VEGEONE のぼり さつまいも版 金")
    B.write_page("nobori_imo_gold_spoon", build("spoon"), "VEGEONE のぼり さつまいも版 金（スプーン）")
    ims = [Image.open(f).convert("RGB") for f in ("nobori_imo_gold_preview.png", "nobori_imo_gold_spoon_preview.png")]
    gap = 40; c = Image.new("RGB", (sum(i.width for i in ims) + gap * 3, ims[0].height + gap * 2), "#cfcbc4")
    x = gap
    for i in ims: c.paste(i, (x, gap)); x += i.width + gap
    c.save("_cmp_imo_gold_spoon.png")
    # A2看板と並べた比較
    a2p = os.path.join(B.HERE, "..", "shodaisai_images", "print", "A2_real_preview.jpg")
    if not os.path.exists(a2p): a2p = os.path.join(B.HERE, "..", ".claude", "skills", "creative-kv", "reference", "examples", "kv_refarm_shodaisai_final.jpg")
    a2 = Image.open(a2p).convert("RGB")
    nb = Image.open("nobori_imo_gold_preview.png").convert("RGB")
    a2 = a2.resize((int(a2.width * nb.height / a2.height), nb.height), Image.LANCZOS)
    gap = 40; c = Image.new("RGB", (a2.width + nb.width + gap * 3, nb.height + gap * 2), "#cfcbc4")
    c.paste(a2, (gap, gap)); c.paste(nb, (a2.width + gap * 2, gap)); c.save("_cmp_imo_gold.png"); print("done")
