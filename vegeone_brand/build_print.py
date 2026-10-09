# -*- coding: utf-8 -*-
"""VEGEONE カップシール — 印刷用PDF出力

やっていること:
  1. 文字をすべて fontTools でアウトライン化（パス化）する
     → PDFにフォントを1つも積まない。書体を持たない印刷所・コンビニ印刷でも
       同じ形で出るし、書体の埋め込み可否も問われない
  2. 仕上がり径を引数で変えられるようにする（カップが未確定のため）
  3. A4のテスト印刷用シートを出す（実寸確認 → カップに当てて径を決める）

出力:
  VEGEONE_sticker_D65 / D55 / D50 / D45 .pdf/.svg   入稿用（塗り足し3mm込み）
  VEGEONE_A4_testprint.pdf                          A4テスト印刷用（4サイズ・実寸）
"""
import os, math, subprocess
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

os.chdir(os.path.dirname(os.path.abspath(__file__)))
HERE = os.getcwd()
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

BLACK, WHITE, GRAY = "#000000", "#FFFFFF", "#666666"
BLEED = 3.0                                       # 塗り足し（mm）


class Outliner:
    """フォントの字形をSVGパスに変換する。PDFに書体を積まないための道具"""

    def __init__(self, path, index=0):
        self.f = TTFont(path, fontNumber=index)
        self.upem = self.f["head"].unitsPerEm
        self.cmap = self.f.getBestCmap()
        self.hmtx = self.f["hmtx"]
        self.gs = self.f.getGlyphSet()

    def has(self, ch):
        return ord(ch) in self.cmap

    def gname(self, ch):
        return self.cmap[ord(ch)]

    def adv(self, text):
        """字送り幅（フォント単位）"""
        return sum(self.hmtx[self.gname(c)][0] for c in text if self.has(c))

    def bbox(self, ch):
        g = self.f["glyf"][self.gname(ch)]
        return g.xMin, g.yMin, g.xMax, g.yMax

    def draw(self, text, x, baseline, size_mm, color, anchor="start", track=0.0):
        """size_mm は em の高さ（＝CSSのfont-sizeと同じ意味）／track は字間(mm)"""
        s = size_mm / self.upem
        n = max(0, len([c for c in text if self.has(c)]) - 1)
        if anchor == "middle":
            x -= (self.adv(text) * s + n * track) / 2
        elif anchor == "end":                      # 右揃え（メニュー表の価格で使う）
            x -= self.adv(text) * s + n * track
        out = []
        for ch in text:
            if not self.has(ch):
                continue
            g = self.gname(ch)
            pen = SVGPathPen(self.gs)
            self.gs[g].draw(pen)
            d = pen.getCommands()
            if d:                                  # 空白文字はパスを持たない
                out.append(f'<path fill="{color}" d="{d}" '
                           f'transform="translate({x:.4f},{baseline:.4f}) '
                           f'scale({s:.6f},{-s:.6f})"/>')   # SVGはY下向きなので反転
            x += self.hmtx[g][0] * s + track
        return "".join(out)


GILL = Outliner("C:/Windows/Fonts/GILSANUB.TTF")            # Gill Sans Ultra Bold
LABEL = Outliner("C:/Windows/Fonts/BIZ-UDGothicB.ttc", 1)   # BIZ UDPGothic Bold

# ロゴの比率（仕上がり径 D = 1.0 としたときの値）。確定版 D=65 / VEGE幅=49 から
R_W1 = 49.0 / 65.0
R_GAP = 0.50                                      # 行間 ÷ 大文字高さ
CAP_U = GILL.bbox("H")[3]                         # 大文字高さ（フォント単位）
LEAF_ANGLES = (150, 191, 349, 30)                 # y下向き・0=右
LEAF_LEN, LEAF_WID, CALYX_Y = 0.55, 0.155, 0.58


def logo(cx, cy, D, fg=WHITE, bg=BLACK, tomato=None, leaf=None):
    """仕上がり径 D の完成ロゴ（地の円は含まない）

    tomato / leaf を指定すると、トマトの実とヘタだけ別色にできる
    （フルカラーで刷る場合に使う。省略時は fg / bg と同色＝黒1色）
    """
    tomato = tomato or fg
    leaf = leaf or bg
    w1 = R_W1 * D
    s = w1 / GILL.adv("VEGE")                     # フォント単位 → mm
    em = self_em = GILL.upem * s                  # em の実寸
    cap = CAP_U * s
    gap = cap * R_GAP
    base1 = cy - (2 * cap + gap) / 2 + cap
    base2 = base1 + cap + gap
    w2 = GILL.adv("ONE") * s

    body = (GILL.draw("VEGE", cx, base1, em, fg, "middle")
            + GILL.draw("ONE", cx, base2, em, fg, "middle"))

    # 「O」のインク外接矩形（字形から直接取る。目分量だとヘタがズレる）
    xmin, ymin, xmax, ymax = GILL.bbox("O")
    ox = cx - w2 / 2 + (xmin + xmax) / 2 * s
    oy = base2 - (ymin + ymax) / 2 * s
    orad = min(xmax - xmin, ymax - ymin) * s / 2

    # トマトの実（Oの穴を埋める）
    body += f'<circle cx="{ox:.4f}" cy="{oy:.4f}" r="{orad*0.99:.4f}" fill="{tomato}"/>'
    # ヘタ：葉4枚を実の肩に寝かせる。上に伸びる茎は付けない
    ly = oy - orad * CALYX_Y
    body += f'<circle cx="{ox:.4f}" cy="{ly:.4f}" r="{orad*0.10:.4f}" fill="{leaf}"/>'
    for ang in LEAF_ANGLES:
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        ln, wd = orad * LEAF_LEN, orad * LEAF_WID
        P = lambda u, v: f"{ox+u*ca-v*sa:.4f},{ly+u*sa+v*ca:.4f}"
        body += (f'<path fill="{leaf}" d="M{P(0,0)} Q{P(ln*0.55,-wd)} {P(ln,0)} '
                 f'Q{P(ln*0.55,wd)} {P(0,0)} Z"/>')
    return body


def disc(cx, cy, D):
    return f'<circle cx="{cx}" cy="{cy}" r="{D/2:.4f}" fill="{BLACK}"/>'


CSS = ("*{margin:0;padding:0;}html,body{-webkit-print-color-adjust:exact;"
       "print-color-adjust:exact;}svg{display:block;}")


def _write(stem, w, h, inner, title):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" '
           f'viewBox="0 0 {w} {h}">{inner}</svg>')
    open(f"{stem}.svg", "w", encoding="utf-8").write(svg)
    open(f"{stem}.html", "w", encoding="utf-8").write(
        f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>'
        f'<style>{CSS}@page{{size:{w}mm {h}mm;margin:0;}}'
        f'body{{width:{w}mm;height:{h}mm;}}</style></head><body>{svg}</body></html>')
    return f"{stem}.html", f"{stem}.pdf"


def sticker(D, stem):
    """入稿用：仕上がり径D＋塗り足し3mm。角まで黒く塗って塗り足しにする"""
    P = D + BLEED * 2
    c = P / 2
    inner = (f'<rect width="{P}" height="{P}" fill="{BLACK}"/>'
             f'{disc(c, c, D)}{logo(c, c, D)}')
    return _write(stem, P, P, inner, f"VEGEONE シール Ø{D:.0f}mm")


# ---- A4テスト印刷シート -------------------------------------
ROWS = [(65.0, [68, 142], 44.5), (55.0, [48, 105, 162], 116.5),
        (50.0, [50, 105, 160], 181.0), (45.0, [52, 105, 158], 240.5)]


def a4(stem):
    parts = [f'<rect width="210" height="297" fill="{WHITE}"/>']
    for D, xs, cy in ROWS:
        for x in xs:
            parts.append(disc(x, cy, D) + logo(x, cy, D))
        cap = f"Ø{D:.0f}mm" if LABEL.has("Ø") else f"{D:.0f}mm"
        parts.append(LABEL.draw(cap, 105, cy + D / 2 + 5.6, 3.8, GRAY, "middle"))

    # 実寸で刷れているかの確認用スケール（100mm）
    parts.append(f'<line x1="55" y1="277" x2="155" y2="277" stroke="{GRAY}" stroke-width="0.3"/>')
    for i in range(11):
        parts.append(f'<line x1="{55+i*10}" y1="277" x2="{55+i*10}" '
                     f'y2="{283 if i % 5 == 0 else 281}" stroke="{GRAY}" stroke-width="0.3"/>')
    parts.append(LABEL.draw("この目盛りが100mmなら実寸で印刷できています（等倍・原寸で印刷）",
                            105, 290, 3.4, GRAY, "middle"))
    return _write(stem, 210, 297, "".join(parts), "VEGEONE シール A4テスト印刷")


def to_pdf(h, p):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files",
                    f"--print-to-pdf={os.path.join(HERE, p)}",
                    "file:///" + os.path.join(HERE, h).replace("\\", "/")],
                   check=True, capture_output=True)
    print(f"  {p:<34}{os.path.getsize(p)/1024:7.1f} KB")


if __name__ == "__main__":
    for D in (65, 55, 50, 45):
        to_pdf(*sticker(float(D), f"VEGEONE_sticker_D{D}"))
    to_pdf(*a4("VEGEONE_A4_testprint"))


def logo_1line(cx, cy, w_mm, ink=WHITE, bg=BLACK, tomato=None, leaf=None,
               track=0.0, leaf_wid=None, rules=0.0):
    """VEGEONE を1行で組んだロゴ。横長のシールに使う。
    w_mm  … 文字列の幅（トラッキング込み）
    track … 字間(mm)。入れると1文字ぶん小さくなるが、小サイズでは読みやすくなる
    rules … 0より大きいと、上下に細い罫（この太さmm）を引く
    「O」はトマトになる（5文字目）"""
    tomato = tomato or ink
    leaf = leaf or bg
    n = 6                                                # VEGEONE の字間の数
    s = (w_mm - n * track) / GILL.adv("VEGEONE")
    em = GILL.upem * s
    cap = CAP_U * s
    base = cy + cap / 2
    body = GILL.draw("VEGEONE", cx, base, em, ink, "middle", track)

    xmin, ymin, xmax, ymax = GILL.bbox("O")
    # 「O」の字送り開始位置（前に4文字ぶんの字間が入る）
    left = cx - w_mm / 2 + GILL.adv("VEGE") * s + 4 * track
    ox = left + (xmin + xmax) / 2 * s
    oy = base - (ymin + ymax) / 2 * s
    orad = min(xmax - xmin, ymax - ymin) * s / 2

    body += f'<circle cx="{ox:.4f}" cy="{oy:.4f}" r="{orad*0.99:.4f}" fill="{tomato}"/>'
    ly = oy - orad * CALYX_Y
    body += f'<circle cx="{ox:.4f}" cy="{ly:.4f}" r="{orad*0.10:.4f}" fill="{leaf}"/>'
    for ang in LEAF_ANGLES:
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        ln, wd = orad * LEAF_LEN, orad * (leaf_wid or LEAF_WID)
        P = lambda u, v: f"{ox+u*ca-v*sa:.4f},{ly+u*sa+v*ca:.4f}"
        body += (f'<path fill="{leaf}" d="M{P(0,0)} Q{P(ln*0.55,-wd)} {P(ln,0)} '
                 f'Q{P(ln*0.55,wd)} {P(0,0)} Z"/>')
    if rules > 0:                                        # 上下に細い罫を引く
        x0 = cx - w_mm / 2
        for yy in (base - cap - cap * 0.55, base + cap * 0.55):
            body += (f'<rect x="{x0:.3f}" y="{yy - rules/2:.3f}" width="{w_mm:.3f}" '
                     f'height="{rules:.3f}" fill="{ink}"/>')
    return body
