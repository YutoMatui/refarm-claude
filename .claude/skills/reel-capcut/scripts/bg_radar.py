# -*- coding: utf-8 -*-
"""栄養レーダーチャートの背景動画（6秒）。soup-app の「1杯の栄養バランス」と同じ6軸で、0 から値が伸びていく。
軸の名前と％は図の一部として描く（CapCut で後入れするのは見出しだけ）。

  python bg_radar.py --values "たんぱく質=19,食物繊維=102,鉄=77,ビタミンA=58,ビタミンC=116,葉酸=97" --out clips/radar.mp4

値は soup-app（api/app/seed.py の nutrition.ratios。1食の目安＝栄養素等表示基準値の1/3 に対する％）から写す。
アプリと同じく 100% を超える分はチャートの上限で描き、数字はそのまま出す。30% の点線も同じ。効能表現は書かない。
背景は REEL_BG があればそれ、無ければ金色。文字色は REEL_INK=brown なら焦げ茶、既定はクリーム。
"""
import argparse, math
from PIL import Image, ImageDraw, ImageFilter
import bg_common as B


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--values", required=True, help="名前=％ をカンマ区切り（6つ）")
    ap.add_argument("--out", required=True); ap.add_argument("--dur", type=float, default=6.0)
    ap.add_argument("--cy", type=int, default=1000, help="チャート中心の y（px）")
    ap.add_argument("--radius", type=int, default=300)
    a = ap.parse_args()
    items = []
    for kv in a.values.split(","):
        k, v = kv.split("="); items.append((k.strip(), float(v)))
    n = len(items); cx, cy, R = 540, a.cy, a.radius
    ink = B.INK + (255,)
    fill_col = (176, 82, 30, 150) if B.DARK_INK else (255, 214, 140, 130)
    line_col = (140, 52, 15, 255) if B.DARK_INK else (255, 247, 230, 255)
    f_lab, f_num, f_small = B.font_jp(42), B.font_num(46), B.font_jp(28)

    def pt(i, frac):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        return (cx + R * frac * math.cos(ang), cy + R * frac * math.sin(ang))

    def frame(t):
        im = B.bg_at(t)
        # うっすら暗い円盤で地と分ける
        disk = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0))
        ImageDraw.Draw(disk).ellipse([cx - R - 90, cy - R - 90, cx + R + 90, cy + R + 90], fill=(60, 25, 5, 70 if not B.DARK_INK else 0))
        im.alpha_composite(disk.filter(ImageFilter.GaussianBlur(40)))
        d = ImageDraw.Draw(im, "RGBA")
        g = B.ease_out(min(1, t / 0.6))
        # 目盛りの網（0.5・1.0）と 30% の点線
        for frac in (0.5, 1.0):
            poly = [pt(i, frac * g) for i in range(n)]
            d.polygon(poly, outline=B.INK + (int(120 * g),), width=2)
        for i in range(n):
            d.line([(cx, cy), pt(i, g)], fill=B.INK + (int(90 * g),), width=2)
        if g >= 1:
            steps = 72
            for s in range(0, steps, 2):
                p1 = pt(s / steps * n, 0.3); p2 = pt((s + 1) / steps * n, 0.3)
                d.line([p1, p2], fill=B.INK + (170,), width=3)
        # 値：0.8 秒から 1.8 秒かけて伸びる
        q = B.ease_out(max(0, min(1, (t - 0.8) / 1.8)))
        if q > 0:
            poly = [pt(i, min(1.0, v / 100) * q) for i, (_, v) in enumerate(items)]
            lay = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.polygon(poly, fill=fill_col, outline=line_col, width=5)
            im.alpha_composite(lay); d = ImageDraw.Draw(im, "RGBA")
            for p in poly:
                d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=line_col)
        # 軸の名前（外側）と％（値が伸び切ったら）
        for i, (k, v) in enumerate(items):
            lx, ly = pt(i, 1.0 + 0.30)
            w = d.textlength(k, font=f_lab)
            d.text((lx - w / 2, ly - 52), k, font=f_lab, fill=B.INK + (int(255 * g),))
            if q >= 1:
                s = "%d%%" % round(v); w2 = d.textlength(s, font=f_num)
                col = (176, 82, 30, 255) if B.DARK_INK else (255, 214, 140, 255)
                d.text((lx - w2 / 2, ly + 4), s, font=f_num, fill=col)
        if q >= 1:
            s = "1食の目安（栄養素等表示基準値の1/3）に対する割合・八訂の推定値。点線は30%"
            w = d.textlength(s, font=f_small)
            d.text((cx - w / 2, cy + R + 150), s, font=f_small, fill=B.INK + (200,))
        return im
    B.render(frame, a.dur, a.out, "radar")


if __name__ == "__main__":
    main()
