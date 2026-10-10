# -*- coding: utf-8 -*-
"""背景動画（文字なし）を Pillow で1コマずつ描くときの共通部品。様式②「飲食店」の色と地。"""
import os, sys, math, shutil, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "creative-kv", "scripts"))
CREAM = (255, 247, 230, 255); GOLD = (255, 214, 140, 255); BROWN = (70, 28, 8, 255)


def font_num(size):
    for p in ["C:/Windows/Fonts/BOOKOS.TTF", os.path.join(REPO, "fonts", "ShipporiMincho-Bold.ttf")]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)


def font_jp(size):
    for p in [os.path.join(REPO, "fonts", "ShipporiMincho-Bold.ttf"), "C:/Windows/Fonts/HGRME.TTC", "C:/Windows/Fonts/yumindb.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)


def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_back(t):
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def gold_bg(phase=0.0):
    """秋の金色グラデ（#D59040→#B86A1E）に、ゆっくり動く光だまり。通年ならコーラル等に差し替える。"""
    bg = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(bg)
    top, bot = (213, 144, 64), (184, 106, 30)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)) + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    cy = 1000 + int(60 * math.sin(phase))
    gd.ellipse([-200, cy - 500, W + 200, cy + 500], fill=(243, 184, 96, 110))
    return Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(160)))


def render(fn, dur, out, name="bg"):
    """fn(t秒)→RGBA画像 を dur 秒ぶん描いて mp4（無音トラック付き）にする。"""
    tmp = os.path.join(os.path.dirname(os.path.abspath(out)), "_frames_" + name)
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for i in range(int(dur * FPS)):
        fn(i / FPS).convert("RGB").save(os.path.join(tmp, "f%04d.png" % i))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("できました:", out)
