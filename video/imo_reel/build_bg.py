# -*- coding: utf-8 -*-
"""「10月の新メニュー 極 焼きいもスープ」リールの背景動画（文字なし）をそろえる。文字は CapCut で後入れ。

  python build_bg.py
    src/01_imo_916.png … 最初のカットの元絵（商大祭キービジュアルから大学芋・ソフトクリームを消し、カップを前に置く）
    src/leaf_*.png     … キービジュアルのもみじを切り抜いたもの
    src/autumn_bg.mp4  … 金色の地にもみじがゆらゆら揺れる秋の背景（2・3・5カットの地。無料）
    clips/02〜06       … 図解・寄り・カレンダー・ロゴ
  01 を動かすのだけ gen_clip.py（約180円・要承認）。05 店の前・外観は video/cal_reel/clips/03a・03b を使い回す

  元画像：src/kv_autumn.jpg（商大祭キービジュアル）・src/cup_green.png（グリーンバックのカップ）。どちらもコミットしない
"""
import math, os, subprocess, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.join(HERE, "..", "..", ".claude", "skills", "reel-capcut", "scripts")
sys.path.insert(0, SK)
import bg_common as B
from common import key_green

os.makedirs(os.path.join(HERE, "clips"), exist_ok=True)
P = lambda *a: os.path.join(HERE, *a)
os.environ.setdefault("REEL_FONT", "Yomogi-Regular.ttf")   # plan の "font" とそろえる
os.environ.setdefault("REEL_INK", "brown")                 # 地が明るいので、カレンダーの文字は焦げ茶・営業日の丸はテラコッタ
LEAF_BOX = {"red": (95, 30, 305, 245), "orange": (535, 20, 750, 228), "yellow": (92, 242, 218, 365)}   # キービジュアル上の位置


def cup_cut():
    cup = key_green(P("src", "cup_green.png"))
    # 緑がかった影と縁を落とす（影はこちらで描く）
    cup.putalpha(cup.getchannel("A").point(lambda v: 0 if v < 200 else int((v - 200) * 255 / 55))
                 .filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2)))
    return cup


def leaves():
    """キービジュアルのもみじを切り抜く。地はなめらかなので、葉を消した地（inpaint）との差で抜く"""
    kv = np.array(Image.open(P("src", "kv_autumn.jpg")).convert("RGB"))
    for name, (a, b, c, d) in LEAF_BOX.items():
        p = kv[b:d, a:c].copy(); sat = cv2.cvtColor(p, cv2.COLOR_RGB2HSV)[..., 1].astype(np.float32)
        edge = np.concatenate([sat[:3].ravel(), sat[-3:].ravel(), sat[:, :3].ravel(), sat[:, -3:].ravel()])
        rough = cv2.morphologyEx((sat > np.median(edge) + 45).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(rough)
        keep = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 300]).astype(np.uint8)
        bg = cv2.inpaint(p, cv2.dilate(keep, np.ones((15, 15), np.uint8)) * 255, 15, cv2.INPAINT_TELEA).astype(np.float32)
        dist = np.sqrt(((p.astype(np.float32) - bg) ** 2).sum(axis=2))
        al = np.clip((dist - 18) / 28, 0, 1) * (cv2.dilate(keep, np.ones((9, 9), np.uint8)) > 0)
        al = cv2.GaussianBlur(al.astype(np.float32), (3, 3), 0)
        Image.fromarray(np.dstack([p, (al * 255).astype(np.uint8)]), "RGBA").save(P("src", "leaf_%s.png" % name))
    print("できました: src/leaf_*.png")


def opening_still(Z=1.45, OY=120, CW=880, BY=1692, CX=640):
    """最初のカットの元絵。キービジュアルを拡大して上に置き、大学芋の器・ソフトクリーム・元のカップを消して、
    前にカップを置く（消した跡はカップの後ろに隠れる位置にしてある）。
    蜜の筋が焼き芋の実に落ちる所（画面 x≈543, y≈800）が見えるよう、カップは右に寄せる。
    真上にトッピングがあると、動画生成で蜜が大学芋にかかってしまう（2026-10-11 代表の指摘：ヘルシーさから離れる）"""
    kv = np.array(Image.open(P("src", "kv_autumn.jpg")).convert("RGB"))
    mask = np.zeros(kv.shape[:2], np.uint8)
    # 器・ソフトクリーム・元のカップ／上のもみじ3枚（見出しにかからない隅へ置き直す）。蜜の筋は残す
    for r in [(115, 690, 515, 1095), (200, 505, 395, 760), (430, 495, 845, 995)] + list(LEAF_BOX.values()):
        cv2.rectangle(mask, r[:2], r[2:], 255, -1)
    clean = cv2.inpaint(kv, mask, 25, cv2.INPAINT_TELEA)
    W, H = B.W, B.H; kw, kh = int(896 * Z), int(1152 * Z)
    a = np.array(Image.fromarray(clean).resize((kw, kh), Image.LANCZOS)).astype(np.float32)
    ox, oy = (W - kw) // 2, int(OY)
    # 上下の足りない所は、キービジュアルの上端・下端の色を横にぼかしてのばす
    topc = cv2.GaussianBlur(a[8:9], (0, 0), 60)[0][-ox:-ox + W]; botc = cv2.GaussianBlur(a[-2:-1], (0, 0), 60)[0][-ox:-ox + W]
    can = np.array([topc * (1 - y / H) + botc * (y / H) for y in range(H)], np.float32)
    y0, y1 = max(0, oy), min(H, oy + kh); can[y0:y1] = a[y0 - oy:y1 - oy, -ox:-ox + W]
    blur = cv2.GaussianBlur(can, (0, 0), 25)
    for yb in (oy, oy + kh):
        for dy in range(-50, 50):
            if 0 <= yb + dy < H:
                w = 1 - abs(dy) / 50; can[yb + dy] = can[yb + dy] * (1 - w) + blur[yb + dy] * w
    im = Image.fromarray(can.clip(0, 255).astype(np.uint8)).convert("RGBA")
    cup = cup_cut(); cup = cup.resize((CW, int(cup.height * CW / cup.width)), Image.LANCZOS)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([CX - CW * 0.42, BY - 50, CX + CW * 0.46, BY + 30], fill=(80, 35, 5, 130))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30))); im.alpha_composite(cup, (CX - CW // 2, BY - cup.height))
    # もみじは見出し（y 230〜470）にかからない隅へ置き直す
    # 左下の2枚は、カップを右に寄せて見えた「大学芋を消した跡」を隠す役も兼ねる
    for n, w, x, y in [("red", 250, -10, 10), ("orange", 230, 850, 20), ("yellow", 120, 20, 520),
                       ("orange", 300, 20, 880), ("red", 230, -30, 1110)]:
        lf = Image.open(P("src", "leaf_%s.png" % n)); lf = lf.resize((w, int(lf.height * w / lf.width)), Image.LANCZOS)
        im.alpha_composite(lf, (x, y))
    im.convert("RGB").save(P("src", "01_imo_916.png")); print("できました: src/01_imo_916.png")


def autumn_bg(dur=10.0):
    """金色の地に、キービジュアルのもみじが四隅でゆらゆら揺れる（落ちる葉はカレンダーの数字に重なるので入れない）（2・3・5カットの地）"""
    L = {n: Image.open(P("src", "leaf_%s.png" % n)) for n in LEAF_BOX}

    def sized(n, w, flip=False):
        im = L[n].resize((w, int(L[n].height * w / L[n].width)), Image.LANCZOS)
        return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
    # (葉, 幅, 中心x, 中心y, 揺れ幅°, 周期秒, 位相, 左右反転)
    # 上の葉は y 200 より上に収める（見出しと重ねない）
    spec = [("red", 250, 105, 95, 6, 3.4, 0.0, False), ("orange", 230, 985, 95, 5, 3.0, 1.3, False),
            ("yellow", 110, 55, 330, 8, 2.6, 2.1, False), ("orange", 240, 985, 1800, 5, 3.6, 0.7, True),
            ("yellow", 160, 90, 1830, 7, 2.9, 2.6, True)]
    items = [(sized(n, w, f), cx, cy, amp, per, ph) for n, w, cx, cy, amp, per, ph, f in spec]
    # 地はキービジュアルと同じ色（上が明るいベージュ→下が濃い金色）。最初のカットとつながるように
    kv = np.array(Image.open(P("src", "kv_autumn.jpg")).convert("RGB")).astype(np.float32)
    top, mid, bot = kv[10:30, 380:520].mean(axis=(0, 1)), kv[230:260, 380:520].mean(axis=(0, 1)), kv[1110:1140, 380:520].mean(axis=(0, 1))
    g = np.array([(top * (1 - y / 600) + mid * (y / 600)) if y < 600 else (mid * (1 - (y - 600) / 1320) + bot * ((y - 600) / 1320))
                  for y in range(B.H)], np.float32)
    BG = Image.fromarray(np.repeat(g[:, None, :], B.W, axis=1).clip(0, 255).astype(np.uint8)).convert("RGBA")

    def frame(t):
        im = BG.copy()
        for leaf, cx, cy, amp, per, ph in items:
            ang = amp * math.sin(2 * math.pi * t / per + ph)
            r = leaf.rotate(ang, resample=Image.BICUBIC, expand=True)
            im.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2 + 6 * math.sin(2 * math.pi * t / per + ph + 1))))
        return im
    B.render(frame, dur, P("src", "autumn_bg.mp4"), "autumn")


def cup_closeup():
    """カップにゆっくり寄る 3.5秒。秋らしく：カップの後ろに夕日のような光、まわりにもみじ（後ろ・足もと）がゆらゆら"""
    cup = cup_cut()
    glow = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([90, 330, 990, 1230], fill=(255, 196, 110, 150))
    glow = glow.filter(ImageFilter.GaussianBlur(120))

    def leaf(n, w, flip=False):
        im = Image.open(P("src", "leaf_%s.png" % n)); im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
        return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
    # (葉, 幅, 中心x, 中心y, 揺れ°, 周期, 位相, 反転)  back＝カップの後ろ、front＝足もと（値段の文字 y1500〜 にはかけない）
    back = [(leaf("red", 210), 150, 640, 7, 3.2, 0.3), (leaf("orange", 200, True), 935, 560, 6, 2.8, 1.7),
            (leaf("yellow", 130), 300, 330, 9, 2.5, 0.9), (leaf("orange", 160), 120, 1060, 6, 3.0, 2.4),
            (leaf("red", 150, True), 975, 1010, 7, 3.4, 1.1)]
    front = [(leaf("yellow", 140, True), 250, 1380, 5, 2.9, 0.5), (leaf("red", 130), 840, 1400, 5, 3.1, 2.0)]

    def put(im, items, t):
        for lf, cx, cy, amp, per, ph in items:
            r = lf.rotate(amp * math.sin(2 * math.pi * t / per + ph), resample=Image.BICUBIC, expand=True)
            im.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2)))

    def frame(t):
        k = 760 + 140 * B.ease_out(min(1, t / 3.5)); c = cup.resize((int(k), int(cup.height * k / cup.width)), Image.LANCZOS)
        im = B.bg_at(t); im.alpha_composite(glow); put(im, back, t)
        im.alpha_composite(c, ((B.W - c.width) // 2, 880 - int(c.height * 0.5)))  # 下の文字の場所を空ける
        put(im, front, t)
        return im
    B.render(frame, 3.5, P("clips", "03_cup_close.mp4"), "close")


if __name__ == "__main__":
    leaves(); opening_still(); autumn_bg()
    os.environ["REEL_BG"] = P("src", "autumn_bg.mp4")
    run = lambda *a: subprocess.run([sys.executable, os.path.join(SK, a[0])] + list(a[1:]), check=True)
    run("bg_callout.py", P("zukai.json"), P("clips", "02_zukai.mp4"))
    cup_closeup()
    run("bg_calendar.py", "--year", "2026", "--month", "10", "--open", "12,13,15,19,22,26,27,29", "--closed", "20",
        "--out", P("clips", "04_calendar.mp4"))   # 下の文字と離すためカップは出さない
    # 最後のロゴは 10月の営業日リールのもの（video/cal_reel/clips/05_end.mp4・金色の地）をそのまま使う
