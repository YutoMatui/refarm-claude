# -*- coding: utf-8 -*-
"""商品の図解の背景動画（文字なし）。カップが出てきて、中の材料へ線が1本ずつ伸びる。
線の先の文字（「さつまいも」など）は入れない。CapCut で後入れする（plan の telop に x・y を書く）。

  python bg_callout.py spec.json clips/02_zukai.mp4

spec.json の例（templates/callout.example.json）:
  {"cup": "グリーンバックの商品.png", "cup_w": 520, "cup_cx": 540, "cup_cy": 1130, "dur": 8.0,
   "callouts": [{"anchor": [75, 275], "end": [330, 640], "side": "left", "at": 1.0}, ...]}
  anchor = 元の商品画像（切り抜き後）の上の点 px。end = 画面上の線の終わり px（文字はこの外側に置く）
  side   = 文字を置く側。終わりからさらに横へ短く線を引く。at = 線が伸び始める秒
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
import bg_common as B

LINE = (255, 247, 230, 235)


def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(spec_path))
    from common import key_green
    src = key_green(os.path.join(base, spec["cup"]))
    # 元絵に付いている緑がかった影は捨てる（半透明の画素を落とす）。影はこちらで描く
    src.putalpha(src.getchannel("A").point(lambda v: 0 if v < 200 else int((v - 200) * 255 / 55)))
    r = spec.get("cup_w", 520) / src.width
    cup = src.resize((int(src.width * r), int(src.height * r)), Image.LANCZOS)
    cx, cy = spec.get("cup_cx", 540), spec.get("cup_cy", 1130)
    x0, y0 = cx - cup.width // 2, cy - cup.height // 2
    # 床に落ちる柔らかい影
    shadow = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([cx - cup.width * 0.42, y0 + cup.height - 40, cx + cup.width * 0.46, y0 + cup.height + 30],
                                   fill=(90, 40, 5, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    callouts = []
    for c in spec["callouts"]:
        a = (x0 + c["anchor"][0] * r, y0 + c["anchor"][1] * r)
        e = tuple(c["end"]); tail = c.get("tail", 70) * (-1 if c.get("side", "left") == "left" else 1)
        callouts.append((a, e, (e[0] + tail, e[1]), c["at"]))
    BG = B.gold_bg()

    def frame(t):
        im = BG.copy()
        p = B.ease_out(min(1, t / 0.8))
        if p > 0:
            sh = shadow.copy(); sh.putalpha(sh.getchannel("A").point(lambda v: int(v * p))); im.alpha_composite(sh)
            c = cup.copy(); c.putalpha(c.getchannel("A").point(lambda v: int(v * p)))
            im.alpha_composite(c, (x0, y0 + int(60 * (1 - p))))
        d = ImageDraw.Draw(im, "RGBA")
        for a, e, tl, at in callouts:
            q = (t - at) / 0.6
            if q <= 0:
                continue
            q1, q2 = B.ease_out(min(1, q / 0.7)), B.ease_out(max(0, min(1, (q - 0.7) / 0.3)))
            rad = 9 * B.ease_back(min(1, q / 0.4))
            d.ellipse([a[0] - rad - 5, a[1] - rad - 5, a[0] + rad + 5, a[1] + rad + 5], outline=LINE, width=3)
            d.ellipse([a[0] - rad * 0.55, a[1] - rad * 0.55, a[0] + rad * 0.55, a[1] + rad * 0.55], fill=LINE)
            m = (a[0] + (e[0] - a[0]) * q1, a[1] + (e[1] - a[1]) * q1)
            d.line([a, m], fill=LINE, width=4)
            if q2 > 0:
                d.line([e, (e[0] + (tl[0] - e[0]) * q2, e[1])], fill=LINE, width=4)
        return im
    B.render(frame, spec.get("dur", 8.0), out, "callout")


if __name__ == "__main__":
    main()
