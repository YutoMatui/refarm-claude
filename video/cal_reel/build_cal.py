# 10月の営業日リール（1080x1920・約19秒）。素材＝既存の写真とKVだけ。Pillowで静止フレーム→ffmpegで動きとつなぎ。
import os, subprocess, sys, calendar
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
sys.path.insert(0, r"C:\Users\YutoM\refarm-cc-company\.claude\skills\creative-kv\scripts")
from brand import wordmark
H_, W_ = 1920, 1080
S = os.path.dirname(os.path.abspath(__file__)); os.chdir(S)
import os as _o
STYLE = _o.environ.get("REEL_STYLE", "pop")   # pop=コーポレートロゴ丸ゴ（従来） / restaurant=明朝・字間・縁なし
def T(s):
    if STYLE == "restaurant":
        return ImageFont.truetype("C:/Windows/Fonts/HGRME.TTC", s)
    return ImageFont.truetype("telop.ttf", s)
def TN(s):  # 数字・英字
    if STYLE == "restaurant":
        return ImageFont.truetype("C:/Windows/Fonts/BOOKOS.TTF", s)
    return ImageFont.truetype("telop.ttf", s)
CREAM = (255, 247, 230, 255); GOLD = (255, 214, 140, 255); BROWN = (70, 28, 8, 255); CORAL = (232, 106, 111, 255); WHITE = (255, 255, 255, 255)

def cover(im, w=W_, h=H_, focus=0.5):
    im = ImageOps.exif_transpose(im).convert("RGB"); r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * focus); return im.crop((x, y, x + w, y + h)).convert("RGBA")

def gold_bg():
    bg = Image.new("RGBA", (W_, H_)); d = ImageDraw.Draw(bg)
    top, bot = (213, 144, 64), (184, 106, 30)
    for y in range(H_):
        t = y / H_; d.line([(0, y), (W_, y)], fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)) + (255,))
    glow = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([-200, 500, W_ + 200, 1500], fill=(243, 184, 96, 110)); glow = glow.filter(ImageFilter.GaussianBlur(160))
    return Image.alpha_composite(bg, glow)

def dark(im, top=0.0, bot=0.0, a_top=0, a_bot=0):
    ov = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    th = int(H_ * top); bh = int(H_ * bot)
    for i in range(th): od.line([(0, i), (W_, i)], fill=(40, 15, 0, int(a_top * (1 - i / th) ** 1.5)))
    for i in range(bh): od.line([(0, H_ - bh + i), (W_, H_ - bh + i)], fill=(40, 15, 0, int(a_bot * (i / bh) ** 1.3)))
    return Image.alpha_composite(im, ov)

def tw(d, t, f, sp=0): return sum(d.textlength(c, font=f) for c in t) + sp * (len(t) - 1)
def ctext(im, t, f, y, fill, sp=0, shadow=True, x=None):
    d = ImageDraw.Draw(im, "RGBA"); w = tw(d, t, f, sp); x0 = (W_ - w) / 2 if x is None else x
    if shadow:
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer); xx = x0
        for c in t: ld.text((xx, y + 6), c, font=f, fill=(30, 10, 0, 170)); xx += ld.textlength(c, font=f) + sp
        im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(8))); d = ImageDraw.Draw(im, "RGBA")
    xx = x0
    for c in t: d.text((xx, y), c, font=f, fill=fill); xx += d.textlength(c, font=f) + sp

# ---------- S1: KV + タイトル
s1 = cover(Image.open("kv.png"), focus=0.45); s1 = dark(s1, 0.3, 0.25, 150, 140)
ctext(s1, "10月の営業日", T(132 if STYLE=="pop" else 120), 150, CREAM, 4 if STYLE=="pop" else 10)
ctext(s1, "VEGEONE ｜ 三宮・加納町の野菜スープ", T(42), 320, GOLD, 2)
ctext(s1, "保存しておくと便利です", T(44), 1700, CREAM, 2)
s1.convert("RGB").save("s1.png")

# ---------- S2: カレンダー（営業日が1つずつ出る）
OPEN = {12, 13, 15, 19, 22, 26, 27, 29}; CLOSED_EXC = {20}; PAST = set(range(1, 10)) | {5, 6, 8}
def cal_frame(n_show):
    im = gold_bg(); d = ImageDraw.Draw(im, "RGBA")
    ctext(im, "10月は 月・火・木", T(96), 120, CREAM, 3)
    ctext(im, "11:00 – 14:00", TN(72), 250, GOLD, 4)
    # grid
    x0, y0, cw, ch = 70, 430, 134, 150
    days = ["月", "火", "水", "木", "金", "土", "日"]
    for i, dn in enumerate(days):
        col = CORAL if dn in ("土",) else (CREAM if dn not in ("日",) else CORAL)
        f = T(40); d.text((x0 + i * cw + cw / 2 - d.textlength(dn, font=f) / 2, y0), dn, font=f, fill=(255, 240, 220, 230))
    shown = 0
    for week_i, week in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(2026, 10)):
        for di, day in enumerate(week):
            if day == 0: continue
            cx = x0 + di * cw + cw / 2; cy = y0 + 80 + week_i * ch + ch / 2
            f = TN(56); txt = str(day)
            if day in OPEN:
                shown += 1
                if shown <= n_show:
                    d.ellipse([cx - 56, cy - 56, cx + 56, cy + 56], fill=CREAM)
                    d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=BROWN)
                    continue
            if day in CLOSED_EXC:
                d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=(255, 240, 220, 120))
                d.line([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=(255, 240, 220, 150), width=4)
                continue
            d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=(255, 240, 220, 110 if day < 10 else 190))
    ctext(im, "●＝営業日　20日（火）はお休み", T(40), 1430, CREAM, 2)
    ctext(im, "月曜12日（祝）も営業します", T(40), 1495, GOLD, 2)
    # 商品ちら見せ
    cup = Image.open("key_soup.png").convert("RGBA")
    from common import key_green
    cup = key_green("key_soup.png"); r = 300 / cup.width; cup = cup.resize((int(cup.width * r), int(cup.height * r)), Image.LANCZOS)
    im.alpha_composite(cup, (W_ - cup.width - 40, H_ - cup.height - 40))
    return im
for k, n in enumerate([0, 2, 4, 6, 8]): cal_frame(n).convert("RGB").save(f"s2_{k}.png")

# ---------- S3: 場所
s3 = cover(Image.open("gaikan.jpg"), focus=0.4); s3 = dark(s3, 0.35, 0.4, 170, 200)
ctext(s3, "場所は", T(60), 150, GOLD, 2)
ctext(s3, "加納町3-11-8 の 2階", T(84), 240, CREAM, 2)
ctext(s3, "1階はECGの看板。黒い階段を上がってください", T(40), 1540, CREAM, 1)
ctext(s3, "JR三ノ宮駅から徒歩10分", T(44), 1620, GOLD, 2)
ctext(s3, "Googleマップで「VEGEONE」", T(44), 1700, CREAM, 2)
s3.convert("RGB").save("s3.png")

# ---------- S4: 商大祭
s4 = cover(Image.open("kv.png"), focus=0.5); s4 = dark(s4, 0.42, 0.42, 190, 210)
ctext(s4, "10.30 金 ・ 11.1 日", T(76), 130, CREAM, 3 if STYLE=="pop" else 8)
ctext(s4, "商大祭にも出店します", T(80), 240, GOLD, 2)
ctext(s4, "揚げたて大学芋 300円", T(56), 1480, CREAM, 2)
ctext(s4, "極 焼き芋スープ 500円", T(56), 1560, CREAM, 2)
ctext(s4, "2点で100円引き", T(48), 1650, GOLD, 2)
s4.convert("RGB").save("s4.png")

# ---------- S5: エンド
s5 = gold_bg(); wm = wordmark(220, CREAM); wm = wm.resize((W_ - 160, int(wm.height * (W_ - 160) / wm.width)), Image.LANCZOS)
s5.alpha_composite(wm, (80, 760)); ctext(s5, "学生団体りふぁーむ", T(48), 1010, CREAM, 4)
ctext(s5, "月・火・木 11:00–14:00", T(60), 1200, CREAM, 2)
ctext(s5, "Googleマップで VEGEONE", T(52), 1300, GOLD, 2)
ctext(s5, "@refarm_soup", T(44), 1420, CREAM, 2)
s5.convert("RGB").save("s5.png")

# ---------- ffmpeg：各シーンに動き → 1本に
FPS = 30
def zoom(src, out, dur, zin=True):
    frames = int(dur * FPS); z = f"zoom+0.0006" if zin else f"1.06-0.0006*on"
    expr = f"zoompan=z='min({z},1.08)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W_}x{H_}:fps={FPS}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", src, "-vf", expr, "-t", str(dur), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", out], check=True)
zoom("s1.png", "c1.mp4", 2.8, True)
# カレンダー：静止フレームを順に（1つずつ出る）
with open("cal.txt", "w", encoding="utf-8") as f:
    for k, dur in zip(range(5), [0.6, 0.45, 0.45, 0.45, 3.0]):
        f.write(f"file 's2_{k}.png'\nduration {dur}\n")
    f.write("file 's2_4.png'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "cal.txt", "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-crf", "18", "c2.mp4"], check=True)
zoom("s3.png", "c3.mp4", 3.6, False)
zoom("s4.png", "c4.mp4", 3.6, True)
zoom("s5.png", "c5.mp4", 3.2, False)
# xfade でつなぐ
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode().strip())
clips = ["c1.mp4", "c2.mp4", "c3.mp4", "c4.mp4", "c5.mp4"]; X = 0.4
inputs = sum([["-i", c] for c in clips], []); fc = []; off = 0; prev = "[0:v]"
for i in range(1, len(clips)):
    off += dur(clips[i - 1]) - X; out = f"[v{i}]" if i < len(clips) - 1 else "[v]"
    fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}{out}"); prev = out
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18", "-movflags", "+faststart", ("10月の営業日_リール.mp4" if STYLE=="pop" else "10月の営業日_リール_restaurant.mp4")], check=True)
print("done", STYLE)
