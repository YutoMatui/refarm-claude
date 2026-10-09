# -*- coding: utf-8 -*-
"""VEGEONE のぼり組版 — 600x1800mm

構成:
  地   : 4色ストライプ（ベクター。sage/olive/mustard/coral ＝看板と同じ）
  絵   : art_1.png から白線画だけを抽出して敷く（地の色はベクターに置き換わる）
  文字 : すべて fontTools でアウトライン化（フォント非依存）
         VEGEONE は確定ロゴ（Gill Sans Ultra Bold・Oがトマト）を流用

レイアウト2案:
  A … VEGE/ONE 2行ロゴ大 ＋「神戸野菜の / まるごとスープ」横書き ＋ 絵
  B … 縦書き「神戸野菜のスープ」主役 ＋ VEGEONE 1行 ＋ 絵（のぼりの定石）

出力: nobori_A / nobori_B の .pdf（入稿・原寸600x1800）/ .png（プレビュー）
"""
import os, sys, math, base64, subprocess
from PIL import Image, ImageChops, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(HERE, "..", "vegeone_brand")
sys.path.insert(0, BRAND)
import build_print as bp          # os.chdir(vegeone_brand) が走るので戻す
from build_print import GILL, CAP_U, Outliner, logo, logo_1line
os.chdir(HERE)

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

W, H = 600, 1800                                   # 仕上がり(mm)
# 2026-08-15 ゆうと「背景が暗い」→ チョーク調から明るめに引き上げたパレット
SAGE, OLIVE, MUSTARD, CORAL = "#9BCBAF", "#A2C05B", "#F0C245", "#EE9AA2"
BANDS = [(SAGE, 148), (OLIVE, 142), (MUSTARD, 158), (CORAL, 152)]
WHITE = "#FFFFFF"
TOMATO = "#D9503F"
HETA = "#5F7040"                                   # トマトのヘタ（深緑）

# 和文書体: HG丸ゴシックは「ダサい」指摘で廃止（2026-08-15）。
# Noto Sans JP 可変フォントから wght=900 (Black) を切り出して使う（_font_compare.py が生成）
MARU = Outliner(os.path.join(HERE, "noto_black.ttf")) if os.path.exists(os.path.join(HERE, "noto_black.ttf")) else None


def _instance_vf(src, dst, wght):
    if not os.path.exists(dst):
        from fontTools import ttLib
        from fontTools.varLib import instancer
        vf = ttLib.TTFont(src)
        instancer.instantiateVariableFont(vf, {"wght": wght}).save(dst)
        print(f"  instanced {os.path.basename(dst)} (wght={wght})")
    return dst


# E案（ペルソナD向け・大人トーン）の見出し明朝
SERIF = Outliner(_instance_vf("C:/Windows/Fonts/NotoSerifJP-VF.ttf", os.path.join(HERE, "noto_serif_black.ttf"), 900)) if os.path.exists("C:/Windows/Fonts/NotoSerifJP-VF.ttf") else None

# E案の配色（SST的：生成り×コーラル×墨）
# 深緑は「ダサい」指摘（2026-08-15）でコーラルに置換
CREAM, CORAL_D, SUMI = "#F6F1E4", "#DA6F66", "#3A352C"

# E案のパレット（warm=コーラル基調 / cool=冷製の涼色基調・2026-08-17ゆうと案）
PALETTES = {
    "warm": {"base": CREAM, "accent": CORAL_D, "ink": SUMI},
    "cool": {"base": "#EDF5F6", "accent": "#5FA8BC", "ink": "#2F3B40"},
}


# ---------- 絵（白線画の抽出） ----------------------------------

def autocrop_white_border(im, tol=26, frac=0.80):
    px = im.convert("RGB")
    w, h = px.size

    def near_white(xy):
        r, g, b = px.getpixel(xy)
        return r > 255 - tol and g > 255 - tol and b > 255 - tol

    def row_white(y):
        s = [near_white((x, y)) for x in range(0, w, max(1, w // 60))]
        return sum(s) / len(s) >= frac

    def col_white(x):
        s = [near_white((x, y)) for y in range(0, h, max(1, h // 60))]
        return sum(s) / len(s) >= frac

    top = 0
    while top < h // 8 and row_white(top):
        top += 1
    bot = h - 1
    while bot > h - h // 8 and row_white(bot):
        bot -= 1
    left = 0
    while left < w // 8 and col_white(left):
        left += 1
    right = w - 1
    while right > w - w // 8 and col_white(right):
        right -= 1
    return im.crop((left, top, right + 1, bot + 1))


def extract_white_art(src, thresh=185, ramp=55, side_trim=0.05):
    """色帯の上の白線画 → 白+アルファのRGBA。min(R,G,B)が高い画素ほど白い

    side_trim: 生成画像の左右に残る「破れ紙風の白フチ」はautocropで取り切れない
    （波打っていて列の白率が閾値未満のため）ので、左右を固定率で追加トリムする"""
    im = autocrop_white_border(Image.open(src).convert("RGB"))
    tw = int(im.width * side_trim)
    im = im.crop((tw, 0, im.width - tw, im.height))
    r, g, b = im.split()
    lo = ImageChops.darker(ImageChops.darker(r, g), b)
    alpha = lo.point(lambda p: 0 if p < thresh
                     else min(255, (p - thresh) * 255 // ramp))
    alpha = alpha.filter(ImageFilter.MaxFilter(3))     # 白線を少し太らせる（遠距離対策）
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out


def crop_subject_square(im, sat_thresh=40, pad_top=0.12, pad_side=0.08, pad_bottom=0.06):
    """写真から被写体まわりをタイトに切り、背景色パディングで正方形にする。

    背景がクリーム/薄グレーで明度閾値では切れないので、
    彩度（max-min）で被写体（色のあるカップ）を検出する。
    透明カップの縁やスプーンは彩度に乗らないため、上方向は多めに残す。"""
    rgb = im.convert("RGB")
    r, g, b = rgb.split()
    hi = ImageChops.lighter(ImageChops.lighter(r, g), b)
    lo = ImageChops.darker(ImageChops.darker(r, g), b)
    sat = ImageChops.subtract(hi, lo)
    bbox = sat.point(lambda p: 255 if p > sat_thresh else 0).getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        bw, bh = x1 - x0, y1 - y0
        x0 = max(0, int(x0 - bw * pad_side))
        x1 = min(rgb.width, int(x1 + bw * pad_side))
        y0 = max(0, int(y0 - bh * pad_top))
        y1 = min(rgb.height, int(y1 + bh * pad_bottom))
        rgb = rgb.crop((x0, y0, x1, y1))
    side = max(rgb.width, rgb.height)
    sq = Image.new("RGB", (side, side), rgb.getpixel((3, 3)))   # 背景色で埋める
    sq.paste(rgb, ((side - rgb.width) // 2, (side - rgb.height) // 2))
    return sq


def data_uri(im):
    from io import BytesIO
    buf = BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ---------- 部品 ------------------------------------------------

def stripes():
    body, x = [], 0.0
    for color, w in BANDS:
        body.append(f'<rect x="{x:.2f}" y="0" width="{w + 0.5:.2f}" height="{H}" fill="{color}"/>')
        x += w
    return "".join(body)


def bunting(y_rope=14.0, flag_w=44.0, flag_h=36.0, stroke=2.2):
    """上端のガーランド。白フチ三角を等間隔に（塗り/白抜き/ハッチの繰り返し）"""
    n = 11
    step = W / n
    body = [f'<path d="M0,{y_rope} Q{W/2},{y_rope + 10} {W},{y_rope}" '
            f'fill="none" stroke="{WHITE}" stroke-width="{stroke}"/>']
    for i in range(n):
        cx = step * (i + 0.5)
        sag = 10 * math.sin(math.pi * (cx / W))
        y0 = y_rope + sag
        x0, x1 = cx - flag_w / 2, cx + flag_w / 2
        tri = f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y0:.1f} L{cx:.1f},{y0 + flag_h:.1f} Z"
        kind = i % 3
        if kind == 0:                                  # 白ベタ
            body.append(f'<path d="{tri}" fill="{WHITE}"/>')
        else:                                          # 白フチ
            body.append(f'<path d="{tri}" fill="none" stroke="{WHITE}" '
                        f'stroke-width="{stroke}" stroke-linejoin="round"/>')
            if kind == 2:                              # ハッチ
                for t in (0.30, 0.55):
                    yy = y0 + flag_h * t
                    xx = flag_w / 2 * (1 - t)
                    body.append(f'<line x1="{cx - xx:.1f}" y1="{yy:.1f}" '
                                f'x2="{cx + xx:.1f}" y2="{yy:.1f}" '
                                f'stroke="{WHITE}" stroke-width="{stroke * 0.8}"/>')
    return "".join(body)


def fatten(inner, size, color=WHITE):
    """画線をわずかに太らせる（遠距離での文字の沈み対策。Black体なので控えめ）"""
    return (f'<g stroke="{color}" stroke-width="{size * 0.015:.2f}" '
            f'stroke-linejoin="round">{inner}</g>')


def jp_line(text, cx, baseline, size, color=WHITE, track_r=0.06):
    return fatten(MARU.draw(text, cx, baseline, size, color, "middle",
                            size * track_r), size)


def jp_vertical(text, cx, y_top, size, color=WHITE, step_r=1.06, font=None):
    """縦書き。長音「ー」はまっすぐな縦棒として描く
    （字形を90度回転させると明朝の波打つストロークになり違和感が出る。
    2026-08-17 ゆうと指摘で置き換え）"""
    f = font or MARU
    body = []
    y = y_top
    for ch in text:
        base = y + size * 0.82
        if ch in "ーｰ―−":
            bw, bh = size * 0.095, size * 0.72
            body.append(f'<rect x="{cx - bw / 2:.1f}" y="{y + size * 0.13:.1f}" '
                        f'width="{bw:.1f}" height="{bh:.1f}" rx="{bw / 2:.1f}" '
                        f'fill="{color}"/>')
        else:
            body.append(f.draw(ch, cx, base, size, color, "middle"))
        y += size * step_r
    return fatten("".join(body), size, color), y - size * (step_r - 1)   # 実際の下端


def art_image(uri, y0, y1, align="xMidYMid"):
    return (f'<image href="{uri}" x="0" y="{y0:.1f}" width="{W}" '
            f'height="{y1 - y0:.1f}" preserveAspectRatio="{align} slice"/>')


SHADOW = ('<filter id="sh" x="-20%" y="-20%" width="140%" height="140%">'
          '<feDropShadow dx="1.6" dy="2.2" stdDeviation="3.4" '
          'flood-color="#3C2D1E" flood-opacity="0.38"/></filter>'
          '<filter id="sh2" x="-20%" y="-20%" width="140%" height="140%">'
          '<feDropShadow dx="1.2" dy="1.8" stdDeviation="3.0" '
          'flood-color="#3C2D1E" flood-opacity="0.16"/></filter>')


# ---------- 書き出し --------------------------------------------

CSS = ("*{margin:0;padding:0;}html,body{-webkit-print-color-adjust:exact;"
       "print-color-adjust:exact;}svg{display:block;}")


def write_page(stem, inner, title):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
           f'viewBox="0 0 {W} {H}"><defs>{SHADOW}</defs>{inner}</svg>')
    open(f"{stem}.html", "w", encoding="utf-8").write(
        f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>'
        f'<style>{CSS}@page{{size:{W}mm {H}mm;margin:0;}}'
        f'body{{width:{W}mm;height:{H}mm;}}</style></head><body>{svg}</body></html>')

    url = "file:///" + os.path.join(HERE, f"{stem}.html").replace("\\", "/")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files",
                    f"--print-to-pdf={os.path.join(HERE, stem)}.pdf", url],
                   check=True, capture_output=True)
    # プレビューPNG（96dpi相当で撮って縮小保存）
    pw, ph = round(W * 96 / 25.4), round(H * 96 / 25.4)
    subprocess.run([CHROME, "--headless", "--disable-gpu",
                    "--allow-file-access-from-files", "--hide-scrollbars",
                    f"--screenshot={os.path.join(HERE, stem)}_full.png",
                    f"--window-size={pw},{ph}", url],
                   check=True, capture_output=True)
    im = Image.open(f"{stem}_full.png")
    im.resize((im.width // 3, im.height // 3), Image.LANCZOS).save(f"{stem}_preview.png")
    print(f"  {stem}.pdf  {os.path.getsize(stem + '.pdf') / 1024 / 1024:.2f} MB / "
          f"preview {im.width // 3}x{im.height // 3}")


def variant_A(uri):
    """VEGE/ONE 2行ロゴ主役"""
    body = [stripes(),
            f'<image href="{uri}" x="0" y="700" width="{W}" height="1086" '
            f'preserveAspectRatio="xMidYMid meet"/>',
            bunting()]
    txt = ['<g filter="url(#sh)">']
    # VEGE/ONE 確定ロゴ（VEGE幅470mm）
    D = 470 / (49.0 / 65.0)
    txt.append(logo(W / 2, 300, D, fg=WHITE, bg=OLIVE, tomato=TOMATO, leaf=HETA))
    # 和文コピー
    s1 = 545 / (MARU.adv("神戸野菜の") / MARU.upem + 4 * 0.06)
    txt.append(jp_line("神戸野菜の", W / 2, 560, s1))
    s2 = 560 / (MARU.adv("まるごとスープ") / MARU.upem + 6 * 0.06)
    txt.append(jp_line("まるごとスープ", W / 2, 668, s2))
    txt.append("</g>")
    return "".join(body) + "".join(txt)


def star(cx, cy, s):
    """4つ角のキラキラ星"""
    return (f'<path fill="{WHITE}" d="M{cx},{cy - s} Q{cx + s*0.18},{cy - s*0.18} {cx + s},{cy} '
            f'Q{cx + s*0.18},{cy + s*0.18} {cx},{cy + s} '
            f'Q{cx - s*0.18},{cy + s*0.18} {cx - s},{cy} '
            f'Q{cx - s*0.18},{cy - s*0.18} {cx},{cy - s} Z"/>')


def variant_D(photo_uri):
    """写真入り決定稿（2026-08-15 ゆうと指定）
    縦二行コピー＋「テイクアウトOK」帯＋冷製トマトスープの円形写真。VEGEONEロゴなし
    ※ ガーランド（三角旗）は 2026-08-15 のゆうと指示で廃止。空いた分コピーを上に詰めた"""
    body = [stripes()]

    txt = ['<g filter="url(#sh)">']
    # 列間は約0.5字（行間空きすぎ指摘 2026-08-15 で 159mm→55mm に詰めた）
    v1, _ = jp_vertical("神戸野菜の", 380, 55, 112)       # 右の行（先に読む）
    v2, _ = jp_vertical("まるごとスープ", 222, 165, 94)   # 左の行（字下げ）
    txt.append(v1)
    txt.append(v2)
    txt.append("</g>")

    # テイクアウトOK 帯（白地×トマト赤。のぼりの実用情報）
    band_y, band_h = 930, 108
    txt.append(f'<g filter="url(#sh)"><rect x="45" y="{band_y}" width="510" '
               f'height="{band_h}" rx="{band_h / 2}" fill="{WHITE}"/></g>')
    t = "テイクアウトOK"
    adv = MARU.adv(t) / MARU.upem
    size = 440 / adv
    txt.append(MARU.draw(t, W / 2, band_y + band_h / 2 + size * 0.36,
                         size, TOMATO, "middle"))

    # 冷製トマトスープの円形写真（白フチ）
    pcx, pcy, pr, ring = 300, 1425, 262, 13
    txt.append(f'<defs><clipPath id="pc"><circle cx="{pcx}" cy="{pcy}" r="{pr}"/></clipPath></defs>')
    txt.append(f'<g filter="url(#sh)"><circle cx="{pcx}" cy="{pcy}" r="{pr + ring}" '
               f'fill="{WHITE}"/></g>')
    txt.append(f'<image href="{photo_uri}" x="{pcx - pr}" y="{pcy - pr}" '
               f'width="{pr * 2}" height="{pr * 2}" '
               f'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>')

    # 写真まわりのキラキラ
    for sx, sy, ss in ((88, 1136, 26), (520, 1180, 20), (60, 1560, 18),
                       (548, 1520, 26), (500, 1090, 13)):
        txt.append(star(sx, sy, ss))

    return "".join(body) + "".join(txt)


def wa_mark_uri(fill=(246, 241, 228)):
    """gen_wa の椀＋湯気マーク（黒/白PNG）を指定色＋アルファに変換して返す"""
    src = os.path.join(BRAND, "gen_wa", "wa_wan_yuge.png")
    im = autocrop_white_border(Image.open(src).convert("RGB"))
    r, g, b = im.split()
    lo = ImageChops.darker(ImageChops.darker(r, g), b)
    alpha = lo.point(lambda p: max(0, 255 - p))          # 黒いほど不透明
    out = Image.new("RGBA", im.size, fill + (0,))
    out.putalpha(alpha)
    return data_uri(out), im.width / im.height


def photo_card(uri, x, y, size, angle, clip_id, frame=10):
    """白フチ角丸の写真カード（少し傾けてポラロイド/誌面風に）"""
    cx, cy = x + size / 2, y + size / 2
    inner = size - frame * 2
    return (f'<g transform="rotate({angle} {cx:.1f} {cy:.1f})">'
            f'<defs><clipPath id="{clip_id}"><rect x="{x + frame}" y="{y + frame}" '
            f'width="{inner}" height="{inner}" rx="14"/></clipPath></defs>'
            f'<g filter="url(#sh2)"><rect x="{x}" y="{y}" width="{size}" '
            f'height="{size}" rx="20" fill="{WHITE}"/></g>'
            f'<image href="{uri}" x="{x + frame}" y="{y + frame}" '
            f'width="{inner}" height="{inner}" '
            f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{clip_id})"/></g>')


def variant_E(photos, palette="warm", bleed=0):
    """ペルソナD（35〜50・上質志向の大人の女性）向けの大人トーン版。
    SST的世界観＝明朝見出し・余白。palette="warm"（生成り×コーラル）／
    "cool"（氷青×浅葱＝冷製の涼しさ。2026-08-17ゆうと案）

    写真は単品ヒーローをやめ、冷製3種（黄・赤・緑）のカードをジグザグに散らす
    （2026-08-15 ゆうと「メニューが変わったら使えない」「映えそうな店に見せたい」
    → 1品の広告ではなく "カラフルなカップスープが並ぶ店" の見せ方に変更。
    メニュー入替時は写真1枚差し替えで済む）。
    ※ E案には元からガーランドなし"""
    P = PALETTES[palette]
    BASE, AC, INK = P["base"], P["accent"], P["ink"]
    B = bleed
    body = [f'<rect x="{-B}" y="{-B}" width="{W + 2 * B}" height="{H + 2 * B}" fill="{BASE}"/>']

    # 上下のアクセント帯（のれんの空気）。上帯＝のぼりで一番遠くまで見える特等席。
    # タグライン案は「いらない」（2026-08-15 ゆうと）→ 期間限定の告知に変更。
    # 季節が変わったら文言と写真・朱印をセットで差し替える
    # 椀マークは「いらない」（2026-08-15 ゆうと）→ 文言だけを帯の中央に
    body.append(f'<rect x="{-B}" y="{-B}" width="{W + 2 * B}" height="{132 + B}" fill="{AC}"/>')
    body.append(f'<rect x="{-B}" y="{H - 40}" width="{W + 2 * B}" height="{40 + B}" fill="{AC}"/>')
    tag = "8・9月限定メニュー"
    ts = min(52, 490 / (SERIF.adv(tag) / SERIF.upem))
    tv = SERIF.draw(tag, W / 2, 66 + ts * 0.36, ts, BASE, "middle", 2.0)
    body.append(fatten(tv, ts, BASE))

    # 縦二行（明朝・墨色）。帯直下が窮屈との指摘（2026-08-17）で
    # 見出しの上に余白を取り、以下すべてを組み直した
    v1, _ = jp_vertical("神戸野菜の", 380, 190, 112, INK, font=SERIF)
    v2, _ = jp_vertical("まるごとスープ", 222, 270, 94, INK, font=SERIF)
    body.append(v1)
    body.append(v2)

    # 落款風の朱印（右の行の下に署名のように）
    # 「神戸」は見出しと情報がかぶる指摘（2026-08-15）→「冷製」に変更。
    # 写真と連動する情報なので、冬は写真と一緒に「温製」へ差し替える
    sx, sy, sw, sh_ = 380, 808, 88, 150
    body.append(f'<rect x="{sx - sw / 2}" y="{sy}" width="{sw}" height="{sh_}" '
                f'rx="10" fill="{AC}"/>')
    sv, _ = jp_vertical("冷製", sx, sy + 14, 56, BASE, font=SERIF)
    body.append(sv)

    # テイクアウトOK 帯（墨地×地色文字。機能情報はゴシックで締める）
    band_y, band_h = 985, 100
    body.append(f'<g filter="url(#sh2)"><rect x="55" y="{band_y}" width="490" '
                f'height="{band_h}" rx="{band_h / 2}" fill="{INK}"/></g>')
    t = "テイクアウトOK"
    size = 420 / (MARU.adv(t) / MARU.upem)
    body.append(MARU.draw(t, W / 2, band_y + band_h / 2 + size * 0.36,
                          size, BASE, "middle"))

    # 冷製3種の写真カードをジグザグに（黄→赤→緑。トマトを主役に少し大きく）
    cards = [
        ("corn",    photos["corn"],    60, 1120, 235, -4, "とうもろこし"),
        ("tomato",  photos["tomato"], 300, 1268, 260,  3, "トマト"),
        ("edamame", photos["edamame"], 70, 1450, 240, -3, "えだまめ"),
    ]
    for key, uri, x, y, s, ang, label in cards:
        body.append(photo_card(uri, x, y, s, ang, f"pc_{key}_{palette}"))
        lv = SERIF.draw(label, x + s / 2, y + s + 36, 26, INK, "middle", 1.5)
        body.append(fatten(lv, 26, INK))

    return "".join(body)


def variant_C(uri):
    """縦二行「神戸野菜の / まるごとスープ」主役（右→左に読む・字下げあり）"""
    body = [stripes(),
            f'<image href="{uri}" x="0" y="1000" width="{W}" height="786" '
            f'preserveAspectRatio="xMidYMid meet"/>',
            bunting()]
    txt = ['<g filter="url(#sh)">']
    v1, _ = jp_vertical("神戸野菜の", 430, 80, 112)       # 右の行（先に読む）
    v2, y2 = jp_vertical("まるごとスープ", 168, 190, 94)  # 左の行（字下げ）
    txt.append(v1)
    txt.append(v2)
    txt.append(logo_1line(W / 2, 950, 560, ink=WHITE, bg=OLIVE,
                          tomato=TOMATO, leaf=HETA, track=0.0, rules=0.0))
    txt.append("</g>")
    return "".join(body) + "".join(txt)


def write_template_page(stem, inner, title, bleed=20):
    """発注先テンプレ（レギュラーのぼり・チチ左・PPT）準拠の入稿PDF。

    テンプレ実測（template_slide.png のガイド解析・実寸換算）:
      スライド 300×550mm ＝ 実寸 1200×2200 の 1/4（印刷所で400%拡大）
      仕上がり600×1800 はスライド中央（実寸 x300-900 / y200-2000）
      塗り足しガイド（緑）＝左右+20mm。上下も同量まで絵を伸ばしておく
    viewBox を実寸 1200×2200 にしてページを 300×550mm にすれば 1/4 縮小は自動"""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="300mm" height="550mm" '
           f'viewBox="0 0 1200 2200"><defs>{SHADOW}</defs>'
           f'<rect width="1200" height="2200" fill="#FFFFFF"/>'
           f'<g transform="translate(300,200)">{inner}</g></svg>')
    open(f"{stem}.html", "w", encoding="utf-8").write(
        f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>'
        f'<style>{CSS}@page{{size:300mm 550mm;margin:0;}}'
        f'body{{width:300mm;height:550mm;}}</style></head><body>{svg}</body></html>')
    url = "file:///" + os.path.join(HERE, f"{stem}.html").replace("\\", "/")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files",
                    f"--print-to-pdf={os.path.join(HERE, stem)}.pdf", url],
                   check=True, capture_output=True)
    pw, ph = round(300 * 96 / 25.4), round(550 * 96 / 25.4)
    subprocess.run([CHROME, "--headless", "--disable-gpu",
                    "--allow-file-access-from-files", "--hide-scrollbars",
                    f"--screenshot={os.path.join(HERE, stem)}_full.png",
                    f"--window-size={pw},{ph}", url],
                   check=True, capture_output=True)
    im = Image.open(f"{stem}_full.png")
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(f"{stem}_preview.png")
    print(f"  {stem}.pdf  {os.path.getsize(stem + '.pdf') / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    # 公式のシール入り写真（vegeone_brand/soup_photos/ 2026-08-17）。
    # クリアシール仕様（地を刷らない・文字#1c1916・トマト#e0675c）で貼り位置も実測済み。
    # こちらが正。当セッションの自作合成（photos_vegeone/）は旧・予備
    PHOTO_DIR = os.path.join(BRAND, "soup_photos")

    def load(name, **kw):
        return data_uri(crop_subject_square(
            Image.open(os.path.join(PHOTO_DIR, name)), **kw))

    uri = load("冷製_トマト_ロゴ入り.png")
    # カード用は寄りで（カードが小さいぶん、カップを大きく写す）
    tight = dict(pad_top=0.10, pad_side=0.06, pad_bottom=0.04)
    # とうもろこしは light 版（コーン粒＋枝豆トッピング。2026-08-17 ゆうと指定）
    photos = {"tomato": load("冷製_トマト_ロゴ入り.png", **tight),
              "corn": load("冷製_とうもろこし_ロゴ入り_light.png", **tight),
              "edamame": load("冷製_枝豆_ロゴ入り.png", **tight)}

    write_page("nobori_D", variant_D(uri), "VEGEONE のぼり D（写真入り）")
    write_page("nobori_E", variant_E(photos, "warm"), "VEGEONE のぼり E（コーラル）")
    write_page("nobori_E_cool", variant_E(photos, "cool"), "VEGEONE のぼり E（涼色）")

    # 発注テンプレ準拠（塗り足し20mm込み・300×550mm＝1/4スケール入稿）
    write_template_page("nobori_E_nyuko",
                        variant_E(photos, "warm", bleed=20),
                        "VEGEONE のぼり 入稿用（塗り足し込み）")

    # ロゴなし版（シール除去だけしたクリーン写真を使う）
    CLEAN_DIR = os.path.join(HERE, "photos_clean")

    def load_clean(name):
        return data_uri(crop_subject_square(
            Image.open(os.path.join(CLEAN_DIR, name)), **tight))

    photos_nologo = {"tomato": load_clean("冷製_トマト.png"),
                     "corn": load_clean("冷製_とうもろこし.png"),
                     "edamame": load_clean("冷製_枝豆.png")}
    write_page("nobori_E_cool_nologo", variant_E(photos_nologo, "cool"),
               "VEGEONE のぼり E（涼色・ロゴなし写真）")

    # warm/cool 比較
    d = Image.open("nobori_E_preview.png")
    e = Image.open("nobori_E_cool_preview.png")
    hh = min(d.height, e.height)
    d = d.resize((d.width * hh // d.height, hh), Image.LANCZOS)
    e = e.resize((e.width * hh // e.height, hh), Image.LANCZOS)
    cmp = Image.new("RGB", (d.width + e.width + 40, hh), (245, 243, 238))
    cmp.paste(d, (0, 0)); cmp.paste(e, (d.width + 40, 0))
    cmp.save("_cmp_E_warm_cool.png")
    print("done")
