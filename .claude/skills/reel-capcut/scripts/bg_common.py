# -*- coding: utf-8 -*-
"""背景動画（文字なし）を Pillow で1コマずつ描くときの共通部品。様式②「飲食店」の色と地。"""
import os, sys, math, shutil, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "creative-kv", "scripts"))
CREAM = (255, 247, 230, 255); GOLD = (255, 214, 140, 255); BROWN = (70, 28, 8, 255)
# 地が明るい（ベージュ）ときは REEL_INK=brown。カレンダーの曜日・数字を焦げ茶に、営業日の丸をテラコッタにする
DARK_INK = os.environ.get("REEL_INK", "") == "brown"
INK = (90, 46, 14) if DARK_INK else (255, 240, 220)
DOT, DOT_TXT = ((176, 82, 30, 255), CREAM) if DARK_INK else (CREAM, BROWN)


def font_num(size):
    for p in ["C:/Windows/Fonts/BOOKOS.TTF", os.path.join(REPO, "fonts", "ShipporiMincho-Bold.ttf")]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)


def font_jp(size):
    """環境変数 REEL_FONT（fonts/ のファイル名）があれば、それを優先（plan の "font" とそろえる）"""
    for p in [os.path.join(REPO, "fonts", os.environ.get("REEL_FONT", "-")),os.path.join(REPO, "fonts", "ShipporiMincho-Bold.ttf"), "C:/Windows/Fonts/HGRME.TTC", "C:/Windows/Fonts/yumindb.ttf"]:
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


_BG = {}


def bg_at(t):
    """t 秒の背景。環境変数 REEL_BG に画像か動画（秋の背景など）があればそれ、無ければ金色グラデ。
    画像はゆっくり寄る（動きを出す）。動画は 1080×1920 に切ってループ。"""
    src = os.environ.get("REEL_BG", "")
    if not src or not os.path.exists(src):
        if "gold" not in _BG:
            _BG["gold"] = gold_bg()
        return _BG["gold"].copy()
    if src.lower().endswith((".mp4", ".mov")):
        if "frames" not in _BG:
            tmp = os.path.join(os.path.dirname(os.path.abspath(src)), "_frames_bgsrc")
            shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf",
                            "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=%d" % (W, H, W, H, FPS),
                            os.path.join(tmp, "f%04d.png")], check=True)
            _BG["frames"] = [os.path.join(tmp, f) for f in sorted(os.listdir(tmp))]
        fr = _BG["frames"]
        return Image.open(fr[int(t * FPS) % len(fr)]).convert("RGBA")
    if "img" not in _BG:
        from common import fit
        _BG["img"] = fit(Image.open(src).convert("RGB"), W, H)
    z = 1 + 0.03 * min(1, t / 8)
    im = _BG["img"]; w, h = int(W * z), int(H * z)
    return im.resize((w, h), Image.LANCZOS).crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H)).convert("RGBA")


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
