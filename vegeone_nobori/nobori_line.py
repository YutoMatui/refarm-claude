# -*- coding: utf-8 -*-
"""通年のぼり v6（2026-09-22）

ゆうと:「土付きなど野菜が汚い／文字のフォントがダサい／スープと文字の上の空間が違和感。
野菜はリアルな画像ではなく線画に（参考：VIVA Kitchen のパスタ03＝写真を切り抜き、まわりに材料の線画）」

構成:
  コーラル地／神戸の農家さんの／丸ごと 野菜スープ（書体を変更）／リボン：1杯で、1日の野菜の 約半分
  切り抜いたカップ写真（背景なし。湯気と影は半透明で残す）を中央に大きく
  まわりに白い線画の野菜（トマト・にんじん・玉ねぎ・なす）
  下の白いブロック：VEGEONE／テイクアウトOK
写真の背景がなくなったので、見出しとスープの間の「写真の空の部分」がなくなる。

素材:
  img_candidates/C1_cup_cut.png   … Gemini 3 Pro Image で白背景に撮った形で生成→切り抜き
  img_candidates/lineart_paths.json … 線画（Gemini 2.5 Flash Image）を4倍にしてSVGのパスに変換
書体（Google Fonts・OFL・無料）: ~/tools/fonts/
出力: nobori_line_{zen,dela}.pdf と preview、_cmp_line.png
"""
import os, sys, io, json, base64
from PIL import Image
import build_nobori as B
sys.path.insert(0, B.BRAND)
from build_print import logo_1line, Outliner
os.chdir(B.HERE)

W, H = B.W, B.H
CORAL, CORAL_D, INK, CREAM, WHITE = "#E86A6F", "#D2555B", "#4A423B", "#FCFAF6", "#FFFFFF"
FD = os.path.join(B.HERE, "..", "fonts")  # リポジトリ内の fonts/（無ければ ~/tools/fonts）
if not os.path.exists(os.path.join(FD, "ZenMaruGothic-Black.ttf")): FD = os.path.join(os.path.expanduser("~"), "tools", "fonts")
FONTS = {
    "zen": (Outliner(os.path.join(FD, "ZenMaruGothic-Black.ttf")), Outliner(os.path.join(FD, "ZenMaruGothic-Bold.ttf"))),
    "dela": (Outliner(os.path.join(FD, "DelaGothicOne-Regular.ttf")), Outliner(os.path.join(FD, "ZenMaruGothic-Bold.ttf"))),
}
IMG = os.path.join(B.HERE, "img_candidates")
LINES = json.load(open(os.path.join(IMG, "lineart_paths.json")))


def gw(f, t, z, tr=0.0):
    n = max(0, len([c for c in t if f.has(c)]) - 1)
    return f.adv(t) * z / f.upem + n * tr


def center(b, f, t, y, z, col, tr=0.0):
    w = gw(f, t, z, tr)
    if w > W - 40:
        print(f"  !! はみ出し {t} {w:.0f}")
    b.append(f.draw(t, W / 2, y, z, col, "middle", track=tr))


def runs(b, y, rs, tr):
    total = sum(gw(f, t, z, tr) for t, f, z, _ in rs)
    x = W / 2 - total / 2
    for t, f, z, col in rs:
        b.append(f.draw(t, x, y, z, col, "start", track=tr)); x += gw(f, t, z, tr)


def veg(name, x, y, w, rot=0, op=0.92):
    p = LINES[name]
    s = w / p["w"]
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({s:.4f})" opacity="{op}">'
            f'<path d="{p["d"]}" fill="{WHITE}" fill-rule="evenodd"/></g>')


def build(fkey, cup_uri):
    HEAD, SUB = FONTS[fkey]
    b = [f'<rect width="{W}" height="{H}" fill="{CORAL}"/>']

    # ---- 見出し ----
    center(b, SUB, "神戸の農家さんの", 100, 40, CREAM, 3)
    if fkey == "dela":
        center(b, HEAD, "丸ごと", 262, 150, WHITE, 6)
        center(b, HEAD, "野菜スープ", 390, 104, WHITE, 2)
    else:
        center(b, HEAD, "丸ごと", 266, 162, WHITE, 6)
        center(b, HEAD, "野菜スープ", 396, 108, WHITE, 2)

    # ---- リボン ----
    # 2026-09-22 ゆうと「約半分のところは二行に」→ 1杯で、1日の野菜の／約 半分
    # 2026-09-22 ゆうと「枠ごと少し下に。見出しとの間と写真との間を同じくらいに」→ 見出し下端406・写真上端718の間の中央に
    y0, h = 474, 176
    x0, x1, n = 18, W - 18, 22
    ym = y0 + h / 2
    pts = [(x0, y0), (x1, y0), (x1 - n, ym), (x1, y0 + h), (x0, y0 + h), (x0 + n, ym)]
    b.append(f'<g filter="url(#sh2)"><polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{CREAM}"/></g>')
    runs(b, y0 + 58, [("1杯で、1日の野菜の", SUB, 40, INK)], 1.5)
    runs(b, y0 + 152, [("約", SUB, 44, CORAL_D), ("半分", HEAD, 96, CORAL_D)], 4)

    # ---- 線画の野菜（カップの後ろ・まわり）----
    # 2026-09-22 ゆうと「カップをもう少し中央に。イラストにかぶってもいい」→ カップを上げて大きく、線画はその後ろに
    b.append(veg("tomato", 26, 686, 200, -8))
    b.append(veg("carrot", 430, 668, 150, 24))
    b.append(veg("onion", 4, 1230, 176, 4))
    b.append(veg("eggplant", 432, 1236, 150, -14))

    # ---- 切り抜いたカップ（湯気・写真の影は消し、影は地の色に合わせて描く）----
    iw, ih = 2830, 3066                      # C1_cup_cut.png の大きさ
    cw = 740.0
    BOT = 1450                               # カップの底
    ch = cw * ih / iw
    ix = W / 2 - 0.372 * cw                  # カップの中心（切り抜き画像の幅の37%）を紙面の中央に
    iy = BOT - ch
    b.append(f'<defs><filter id="blur" x="-50%" y="-50%" width="200%" height="200%">'
             f'<feGaussianBlur stdDeviation="9"/></filter></defs>')
    b.append(f'<ellipse cx="{W/2:.1f}" cy="{BOT - 6}" rx="205" ry="22" fill="#6B2A2A" opacity="0.28" filter="url(#blur)"/>')
    b.append(f'<image href="{cup_uri}" x="{ix:.1f}" y="{iy:.1f}" width="{cw}" height="{ch:.1f}"/>')

    # ---- 下のブロック ----
    y0 = 1540
    b.append(f'<rect x="0" y="{y0}" width="{W}" height="{H - y0}" fill="{WHITE}"/>')
    b.append(logo_1line(W / 2, y0 + 100, 420, INK, WHITE, CORAL, INK))
    t = "テイクアウトOK"
    pw_ = gw(SUB, t, 28, 1.5) + 50
    py = y0 + 170
    b.append(f'<rect x="{W/2 - pw_/2:.1f}" y="{py}" width="{pw_:.1f}" height="46" rx="23" fill="{CORAL}"/>')
    b.append(SUB.draw(t, W / 2, py + 33, 28, WHITE, "middle", track=1.5))
    return "".join(b)


if __name__ == "__main__":
    # 2026-09-22 カップの影を明るく（brighten_cup.py）。
    # data URI（約10MB）だと空きメモリの少ないときに Chrome が止まったので、ファイルを直接読ませる
    uri = "img_candidates/C1_cup_cut_bright.png"
    KEYS = sys.argv[1:] or ["zen", "dela"]
    for k in KEYS:
        B.write_page(f"nobori_line_{k}", build(k, uri), f"VEGEONE のぼり v6 {k}")
    if len(KEYS) < 2: sys.exit()
    ims = [Image.open(f"nobori_line_{k}_preview.png").convert("RGB") for k in ("zen", "dela")]
    gap = 40
    c = Image.new("RGB", (sum(i.width for i in ims) + gap * 3, ims[0].height + gap * 2), "#cfcbc4")
    x = gap
    for i in ims:
        c.paste(i, (x, gap)); x += i.width + gap
    c.save("_cmp_line.png"); print("done")
