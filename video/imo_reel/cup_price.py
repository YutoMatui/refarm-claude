# -*- coding: utf-8 -*-
"""値段のカット（3.5秒）：図解・レーダーと同じ暗い写真の地（REEL_BG）に、カップだけを置いてゆっくり寄る。もみじは使わない。
文字（商品名・価格）は上に CapCut で入れるので、カップは y=600 より下に置く。
  REEL_BG=src/zukai_bg.mp4 python cup_price.py"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", ".claude", "skills", "reel-capcut", "scripts"))
import bg_common as B, build_bg as bb
cup = bb.cup_cut()
glow = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([140, 700, 940, 1500], fill=(255, 200, 120, 90)); glow = glow.filter(ImageFilter.GaussianBlur(140))
def frame(t):
    k = 720 + 90 * B.ease_out(min(1, t / 3.5)); c = cup.resize((int(k), int(cup.height * k / cup.width)), Image.LANCZOS)
    im = B.bg_at(t); im.alpha_composite(glow)
    x = (B.W - c.width) // 2; y = 1130 - c.height // 2
    sh = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([x + 40, y + c.height - 60, x + c.width - 40, y + c.height + 30], fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30))); im.alpha_composite(c, (x, y))
    return im
B.render(frame, 3.5, os.path.join(HERE, "clips_raw", "03_cup_close.mp4"), "price")
