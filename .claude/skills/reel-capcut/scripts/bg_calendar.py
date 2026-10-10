# -*- coding: utf-8 -*-
"""営業日カレンダーの背景動画（文字なし・7秒）。営業日が1つずつ出て、最後に商品が右下から滑り込む。
見出し（「10月は 月・火・木」「11:00–14:00」など）は入れない。文字は CapCut で後入れする。

  python bg_calendar.py --year 2026 --month 11 --open 5,6,12,13 --closed 10 --out clips/02_calendar.mp4 [--cup key_soup.png]

--cup はグリーンバック（#00FF00）の商品画像。省略すると商品なし。
"""
import argparse, calendar
from PIL import Image, ImageDraw
import bg_common as B


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True); ap.add_argument("--month", type=int, required=True)
    ap.add_argument("--open", required=True, help="営業日をカンマ区切り")
    ap.add_argument("--closed", default="", help="特記の休業日（×印）")
    ap.add_argument("--cup", default=""); ap.add_argument("--out", required=True); ap.add_argument("--dur", type=float, default=7.0)
    a = ap.parse_args()
    OPEN = [int(x) for x in a.open.split(",") if x.strip()]
    CLOSED = {int(x) for x in a.closed.split(",") if x.strip()}
    cup = None
    if a.cup:
        from common import key_green
        cup = key_green(a.cup); r = 320 / cup.width
        cup = cup.resize((int(cup.width * r), int(cup.height * r)), Image.LANCZOS)
    BG = B.gold_bg(); X0, Y0, CW, CH = 70, 560, 134, 150
    t_last = 0.9 + len(OPEN) * 0.35

    def frame(t):
        im = B.bg_at(t); d = ImageDraw.Draw(im, "RGBA"); al = B.ease_out(min(1, t / 0.6))
        f = B.font_jp(40)
        for i, dn in enumerate(["月", "火", "水", "木", "金", "土", "日"]):
            d.text((X0 + i * CW + CW / 2 - d.textlength(dn, font=f) / 2, Y0 - int(20 * (1 - al))), dn, font=f, fill=(255, 240, 220, int(230 * al)))
        f = B.font_num(56); k = 0
        for wi, week in enumerate(calendar.Calendar(firstweekday=0).monthdayscalendar(a.year, a.month)):
            for di, day in enumerate(week):
                if day == 0:
                    continue
                cx = X0 + di * CW + CW / 2; cy = Y0 + 80 + wi * CH + CH / 2; txt = str(day)
                if day in OPEN:
                    k += 1; p = (t - (0.9 + (k - 1) * 0.35)) / 0.4
                    if p > 0:
                        rad = 56 * B.ease_back(min(1, p))
                        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=B.CREAM)
                        if p > 0.5:
                            d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=B.BROWN)
                        continue
                if day in CLOSED and t > t_last:
                    d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=(255, 240, 220, 120))
                    d.line([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=(255, 240, 220, 150), width=4)
                    continue
                d.text((cx - d.textlength(txt, font=f) / 2, cy - 36), txt, font=f, fill=(255, 240, 220, int(190 * al)))
        if cup is not None:
            p = max(0, min(1, (t - (t_last + 0.2)) / 0.7))
            if p > 0:
                e = B.ease_out(p); c = cup.copy(); c.putalpha(c.getchannel("A").point(lambda v: int(v * e)))
                im.alpha_composite(c, (B.W - cup.width - 40 + int(200 * (1 - e)), B.H - cup.height - 60 + int(80 * (1 - e))))
        return im
    B.render(frame, a.dur, a.out, "cal")


if __name__ == "__main__":
    main()
