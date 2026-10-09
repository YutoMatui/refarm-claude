"""VIVA Kitchen のタペストリー3型を手本にしたのぼり（600×1800）。
使い方: python nobori_viva.py config.json hero_green.png 出力名 [01|02|03] [chalk_bg.png]
  01 = 濃色地＋極太コンデンス英字＋赤リボン＋商品＋ロゴ
  02 = ティール地＋筆記体英字＋商品＋黄色の手書きシール＋白地にロゴ
  03 = 黒板＋チョーク英字＋白枠の日本語＋商品＋ロゴ
config の "viva": {"en1":"LET'S EAT","en2":"SOUP!","script":"Let's eat soup!","ribbon":"神戸野菜の 焼き芋スープ","sticker":"揚げたて 大学芋も","box1":"厳選 神戸野菜","box2":"焼き芋スープ"}"""
import sys, json, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from common import key_green, text_w, fit_font
from fonts import font
from brand import wordmark

F = os.environ.get("WINDIR", "C:/Windows") + "/Fonts/"
def ff(names, kind, s):
    for n in names:
        if os.path.exists(F + n):
            return ImageFont.truetype(F + n, s)
    return font(kind, s)
COND = lambda s: ff(["TCCEB.TTF", "impact.ttf", "ARIALNB.TTF"], "pop", s)      # Tw Cen MT Condensed Extra Bold
SCRIPT = lambda s: ff(["segoescb.ttf", "segoesc.ttf", "Gabriola.ttf"], "serif_en", s)
HAND = lambda s: ff(["segoeprb.ttf", "segoepr.ttf"], "kyokasho", s)
JPB = lambda s: ff(["HGRGE.TTC", "YuGothB.ttc", "meiryob.ttc"], "pop", s)      # HG創英角ゴシックUB
JPM = lambda s: ff(["YuGothB.ttc", "meiryob.ttc"], "kyokasho", s)

cfg = json.load(open(sys.argv[1], encoding="utf-8")); hero_p = sys.argv[2]; outp = sys.argv[3]
style = sys.argv[4] if len(sys.argv) > 4 else "01"; chalk_p = sys.argv[5] if len(sys.argv) > 5 else None
v = cfg.get("viva", {})
EN1 = v.get("en1", "LET'S EAT"); EN2 = v.get("en2", "SOUP!"); SCR = v.get("script", "Let's eat soup!")
RIBBON = v.get("ribbon", ""); STICKER = v.get("sticker", ""); BOX1 = v.get("box1", ""); BOX2 = v.get("box2", "")
BRAND_BY = cfg.get("by", "")
W, H = 1200, 3600
CREAM = (250, 246, 236, 255); WHITE = (255, 255, 255, 255); RED = (215, 53, 47, 255); INK = (20, 20, 20, 255)

def center(d, txt, f, y, fill, sp=0):
    x = W / 2 - text_w(d, txt, f, sp) / 2
    for c in txt:
        d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp

def place_hero(canvas, cut, width, cy_top, shadow=True):
    r = width / cut.size[0]; c = cut.resize((int(cut.size[0] * r), int(cut.size[1] * r)), Image.LANCZOS)
    x = int(W / 2 - c.size[0] / 2)
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a = c.split()[3].point(lambda p: int(p * 0.55))
        sh.paste((0, 0, 0, 255), (x + 10, cy_top + 28), a); canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)))
    canvas.alpha_composite(c, (x, cy_top)); return cy_top + c.size[1]

def ribbon(canvas, txt, y, fill=RED, fg=WHITE, f=None, pad=40, angle=0):
    f = f or JPB(78); d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(text_w(d, txt, f, 4) + pad * 2); h = int(f.size * 1.55)
    band = Image.new("RGBA", (w + 60, h), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    bd.polygon([(30, 0), (w + 30, 0), (w + 60, h / 2), (w + 30, h), (30, h), (0, h / 2)], fill=fill)
    x = 30 + pad
    for c in txt:
        bd.text((x, int(f.size * 0.18)), c, font=f, fill=fg); x += bd.textlength(c, font=f) + 4
    if angle: band = band.rotate(angle, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(band, (int(W / 2 - band.size[0] / 2), int(y)))
    return y + band.size[1]

hero = key_green(hero_p)

if style == "01":
    canvas = Image.new("RGBA", (W, H), (14, 59, 46, 255)); d = ImageDraw.Draw(canvas)
    f1 = fit_font(d, EN1, COND, W - 80, 330, sp=6); center(d, EN1, f1, 120, CREAM, 6)
    y = ribbon(canvas, RIBBON, 470, f=JPB(74)); d = ImageDraw.Draw(canvas)
    f2 = fit_font(d, EN2, COND, W - 80, 430, sp=8); center(d, EN2, f2, y + 10, CREAM, 8)
    bottom = place_hero(canvas, hero, 1040, 1010)
    wm = wordmark(230, CREAM); wm = wm.resize((W - 110, int(wm.size[1] * (W - 110) / wm.size[0])), Image.LANCZOS) if wm.size[0] > W - 110 else wm; canvas.alpha_composite(wm, (int(W / 2 - wm.size[0] / 2), 2880))
    d = ImageDraw.Draw(canvas); f3 = JPM(52); tw_ = text_w(d, BRAND_BY, f3, 6)
    d.line([(W / 2 - tw_ / 2 - 120, 3240), (W / 2 - tw_ / 2 - 40, 3240)], fill=CREAM, width=4)
    d.line([(W / 2 + tw_ / 2 + 40, 3240), (W / 2 + tw_ / 2 + 120, 3240)], fill=CREAM, width=4)
    center(d, BRAND_BY, f3, 3208, CREAM, 6)

elif style == "02":
    canvas = Image.new("RGBA", (W, H), (29, 125, 118, 255)); d = ImageDraw.Draw(canvas)
    # 筆記体（少し傾ける）
    fs = fit_font(d, SCR, SCRIPT, W - 120, 190); tmp = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
    center(td, SCR, fs, 60, WHITE); tmp = tmp.rotate(6, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(tmp, (int(W / 2 - tmp.size[0] / 2), 90))
    bottom = place_hero(canvas, hero, 1080, 620)
    # 黄色の手書きシール
    if STICKER:
        st = Image.new("RGBA", (560, 560), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.ellipse([20, 60, 540, 500], outline=(243, 216, 74, 255), width=10)
        lines = STICKER.split(" "); fh = JPB(84); yy = 280 - len(lines) * 55
        for ln in lines:
            sd.text((280 - sd.textlength(ln, font=fh) / 2, yy), ln, font=fh, fill=(243, 216, 74, 255)); yy += 110
        st = st.rotate(-10, resample=Image.BICUBIC, expand=True)
        canvas.alpha_composite(st, (40, 1900))
    # 白地のロゴブロック
    d = ImageDraw.Draw(canvas); d.rectangle([0, 2760, W, H], fill=WHITE)
    wm = wordmark(230, INK); wm = wm.resize((W - 110, int(wm.size[1] * (W - 110) / wm.size[0])), Image.LANCZOS) if wm.size[0] > W - 110 else wm; canvas.alpha_composite(wm, (int(W / 2 - wm.size[0] / 2), 2960))
    d = ImageDraw.Draw(canvas); f3 = JPM(52); tw_ = text_w(d, BRAND_BY, f3, 6)
    d.line([(W / 2 - tw_ / 2 - 120, 3320), (W / 2 - tw_ / 2 - 40, 3320)], fill=INK, width=4)
    d.line([(W / 2 + tw_ / 2 + 40, 3320), (W / 2 + tw_ / 2 + 120, 3320)], fill=INK, width=4)
    center(d, BRAND_BY, f3, 3288, INK, 6)

else:  # 03 黒板
    bg = Image.open(chalk_p).convert("RGBA") if chalk_p else Image.new("RGBA", (W, H), (38, 42, 40, 255))
    bw, bh = bg.size; r = max(W / bw, H / bh); bg = bg.resize((int(bw * r), int(bh * r)), Image.LANCZOS)
    canvas = bg.crop(((bg.size[0] - W) // 2, (bg.size[1] - H) // 2, (bg.size[0] - W) // 2 + W, (bg.size[1] - H) // 2 + H))
    rng = np.random.default_rng(5); noise = Image.fromarray((rng.random((H, W)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    def chalk(txt, f, y, sp=0, strength=0.45):
        layer = Image.new("L", (W, H), 0); ld = ImageDraw.Draw(layer); center(ld, txt, f, y, 255, sp)
        a = np.array(layer).astype(np.float32) / 255 * (1 - strength + strength * np.array(noise).astype(np.float32) / 255)
        col = Image.new("RGBA", (W, H), (245, 243, 236, 0)); col.putalpha(Image.fromarray((a * 255).astype(np.uint8))); canvas.alpha_composite(col)
    chalk(EN1 + " " + EN2, fit_font(ImageDraw.Draw(canvas), EN1 + " " + EN2, COND, W - 80, 190, sp=4), 140, 4)
    d = ImageDraw.Draw(canvas)
    if BOX1:
        f = JPB(80); w = text_w(d, BOX1, f, 6) + 90; x0 = W / 2 - w / 2
        d.rounded_rectangle([x0, 400, x0 + w, 400 + f.size * 1.5], radius=14, fill=WHITE); center(d, BOX1, f, 400 + f.size * 0.2, INK, 6)
    if BOX2:
        f = JPB(96); w = text_w(d, BOX2, f, 6) + 100; x0 = W / 2 - w / 2; y0 = 580
        d.rounded_rectangle([x0, y0, x0 + w, y0 + f.size * 1.5], radius=14, outline=WHITE, width=8); center(d, BOX2, f, y0 + f.size * 0.2, WHITE, 6)
    bottom = place_hero(canvas, hero, 1000, 860)
    wm = wordmark(230, WHITE); wm = wm.resize((W - 110, int(wm.size[1] * (W - 110) / wm.size[0])), Image.LANCZOS) if wm.size[0] > W - 110 else wm; canvas.alpha_composite(wm, (int(W / 2 - wm.size[0] / 2), 2900))
    d = ImageDraw.Draw(canvas); f3 = JPM(52); tw_ = text_w(d, BRAND_BY, f3, 6)
    d.line([(W / 2 - tw_ / 2 - 120, 3260), (W / 2 - tw_ / 2 - 40, 3260)], fill=WHITE, width=4)
    d.line([(W / 2 + tw_ / 2 + 40, 3260), (W / 2 + tw_ / 2 + 120, 3260)], fill=WHITE, width=4)
    center(d, BRAND_BY, f3, 3228, WHITE, 6)

out = canvas.convert("RGB")
out.resize((2362, 7087), Image.LANCZOS).save(f"{outp}_{style}_100dpi.jpg", quality=92, dpi=(100, 100))
out.resize((600, 1800), Image.LANCZOS).save(f"{outp}_{style}_preview.jpg", quality=90); print("saved", outp, style)
