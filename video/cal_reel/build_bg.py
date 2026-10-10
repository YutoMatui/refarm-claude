# -*- coding: utf-8 -*-
"""背景動画（文字なし）を作る。文字は CapCut で後入れする（2026-10-10 ゆうと指示）。
  python build_bg.py            → clips/02_calendar.mp4（カレンダーが1日ずつ出る・7秒）
                                   clips/05_end.mp4（金色の地にVEGEONEのワードマーク・4秒）
素材は既存のものだけ（key_soup.png のカップ、brand.py のワードマーク）。Pillowで1コマずつ描いて ffmpeg でつなぐ。
"""
import os, sys, subprocess, calendar, math, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "creative-kv", "scripts"))
from brand import wordmark
from common import key_green
W, H, FPS = 1080, 1920, 30
CREAM = (255, 247, 230, 255); GOLD = (255, 214, 140, 255); BROWN = (70, 28, 8, 255)
def TN(s):  # 数字（Bookman → Shippori）
    for p in ["C:/Windows/Fonts/BOOKOS.TTF", os.path.join(REPO, "fonts", "ShipporiMincho-Bold.ttf")]:
        if os.path.exists(p): return ImageFont.truetype(p, s)
def TJ(s):
    for p in [os.path.join(REPO, "fonts", "ShipporiMincho-Bold.ttf"), "C:/Windows/Fonts/HGRME.TTC"]:
        if os.path.exists(p): return ImageFont.truetype(p, s)
def ease_out(t): return 1 - (1 - t) ** 3
def ease_back(t): c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def gold_bg(phase=0.0):
    bg = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(bg)
    top, bot = (213, 144, 64), (184, 106, 30)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)) + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    cy = 1000 + int(60 * math.sin(phase)); gd.ellipse([-200, cy - 500, W + 200, cy + 500], fill=(243, 184, 96, 110))
    return Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(160)))
BG = gold_bg()

# ---------- カレンダー ----------
OPEN = [12, 13, 15, 19, 22, 26, 27, 29]; CLOSED_EXC = {20}
X0, Y0, CW, CH = 70, 560, 134, 150
CUP = key_green(os.path.join(HERE, "key_soup.png")); r = 320 / CUP.width
CUP = CUP.resize((int(CUP.width * r), int(CUP.height * r)), Image.LANCZOS)
def cal_frame(t):
    """t 秒時点のコマ。0〜0.6 グリッドがふわっと出る → 0.9秒から営業日が0.35秒おきに1つずつ → カップが右下から出る"""
    im = BG.copy(); d = ImageDraw.Draw(im, "RGBA")
    a = ease_out(min(1, t / 0.6))
    days = ["月", "火", "水", "木", "金", "土", "日"]
    f = TJ(40)
    for i, dn in enumerate(days):
        d.text((X0 + i * CW + CW / 2 - d.textlength(dn, font=f) / 2, Y0 - int(20 * (1 - a))), dn, font=f, fill=(255, 240, 220, int(230 * a)))
    f = TN(56); k = 0
    for wi, week in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(2026, 10)):
        for di, day in enumerate(week):
            if day == 0: continue
            cx = X0 + di * CW + CW / 2; cy = Y0 + 80 + wi * CH + CH / 2; txt = str(day)
            if day in OPEN:
                k += 1; t0 = 0.9 + (k - 1) * 0.35; p = (t - t0) / 0.4
                if p > 0:
                    s = ease_back(min(1, p)); rad = 56 * s
                    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=CREAM)
                    if p > 0.5:
                        d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=BROWN)
                    continue
            if day in CLOSED_EXC and t > 0.9 + len(OPEN) * 0.35:
                d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=(255, 240, 220, 120))
                d.line([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=(255, 240, 220, 150), width=4); continue
            d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=(255, 240, 220, int((110 if day < 10 else 190) * a)))
    # カップ
    tc = 0.9 + len(OPEN) * 0.35 + 0.2; p = max(0, min(1, (t - tc) / 0.7))
    if p > 0:
        e = ease_out(p); x = W - CUP.width - 40 + int(200 * (1 - e)); y = H - CUP.height - 60 + int(80 * (1 - e))
        c = CUP.copy(); c.putalpha(c.getchannel("A").point(lambda v: int(v * e)))
        im.alpha_composite(c, (x, y))
    return im

# ---------- エンド ----------
WM = wordmark(220, CREAM); WM = WM.resize((W - 160, int(WM.height * (W - 160) / WM.width)), Image.LANCZOS)
def end_frame(t):
    im = gold_bg(t * 0.8); p = ease_out(min(1, t / 1.0))
    wm = WM.copy(); wm.putalpha(wm.getchannel("A").point(lambda v: int(v * p)))
    im.alpha_composite(wm, (80, 760 + int(30 * (1 - p))))
    return im

def render(name, fn, dur, out):
    tmp = os.path.join(HERE, "_frames_" + name); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    n = int(dur * FPS)
    for i in range(n):
        fn(i / FPS).convert("RGB").save(os.path.join(tmp, "f%04d.png" % i))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
                    "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    shutil.rmtree(tmp, ignore_errors=True); print("done", out)

if __name__ == "__main__":
    os.makedirs("clips", exist_ok=True)
    render("cal", cal_frame, 7.0, "clips/02_calendar.mp4")
    render("end", end_frame, 4.0, "clips/05_end.mp4")
