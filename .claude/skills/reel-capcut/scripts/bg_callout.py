# -*- coding: utf-8 -*-
"""商品の図解の背景動画（文字なし）。カップが出てきて、中の材料へ線が1本ずつ伸びる。
線の先の文字（「さつまいも」など）は入れない。CapCut で後入れする（plan の telop に x・y を書く）。

  python bg_callout.py spec.json clips/02_zukai.mp4     （背景は REEL_BG があればそれ。無ければ金色）

spec.json の例（video/imo_reel/zukai.json）:
  {"cup": "グリーンバックの商品.png", "cup_w": 600, "cup_cx": 540, "cup_cy": 1150, "dur": 8.0,
   "callouts": [{"anchor": [80, 290], "end": [300, 1120], "side": "left", "at": 1.0,
                 "bracket": [1010, 1230], "color": "cream"}, ...]}
  anchor  = 元の商品画像（切り抜き後）の上の点 px。end = 画面上の線の終わり px（文字はこの外側に置く）
  side    = 文字を置く側（left / right）。終わりからさらに横へ短く線を引く（tail px）。at = 線が伸び始める秒
  bracket = [上y, 下y] を書くと、線の終わりに縦の括り線を引く（いくつかの名前を1つのまとまりとして示す）
  color   = cream（既定）・gold・brown・terra。まとまりごとに色を変えて区別する（明るい地なら brown／terra）
  photo   = 実物の写真（任意）。photo_at=[x,y]（中心px）・photo_r=半径px で、線の先に丸く置く。文字はその横に
  photos  = 複数のときは [{"file":..,"at":[x,y],"r":..}, ...]
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
import bg_common as B

COL = {"cream": (255, 247, 230, 235), "gold": (255, 214, 140, 240), "brown": (90, 46, 14, 235), "terra": (140, 52, 15, 240)}


def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(spec_path))
    from common import key_green
    src = key_green(os.path.join(base, spec["cup"]))
    # 元絵に付いている緑がかった影は捨てる（半透明の画素を落とす）。影はこちらで描く
    src.putalpha(src.getchannel("A").point(lambda v: 0 if v < 200 else int((v - 200) * 255 / 55)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2)))
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
        e = tuple(c["end"]); sgn = -1 if c.get("side", "left") == "left" else 1
        phs = []
        for pc in ([{"file": c["photo"], "at": c["photo_at"], "r": c.get("photo_r", 80)}] if c.get("photo") else []) + c.get("photos", []):
            # 実物の写真を丸く切って、線の先に置く（at＝中心px・r＝半径px）。線と同じ色の細い輪をつける
            pr = int(pc.get("r", 80)); src_p = Image.open(os.path.join(base, pc["file"])).convert("RGB")
            side = min(src_p.size); src_p = src_p.crop(((src_p.width - side) // 2, (src_p.height - side) // 2,
                                                       (src_p.width - side) // 2 + side, (src_p.height - side) // 2 + side)).resize((pr * 2, pr * 2), Image.LANCZOS)
            mask = Image.new("L", (pr * 2, pr * 2), 0); ImageDraw.Draw(mask).ellipse([0, 0, pr * 2 - 1, pr * 2 - 1], fill=255)
            tile = Image.new("RGBA", (pr * 2 + 12, pr * 2 + 12), (0, 0, 0, 0))
            ImageDraw.Draw(tile).ellipse([0, 0, pr * 2 + 11, pr * 2 + 11], fill=COL.get(c.get("color", "cream"), COL["cream"]))
            tile.paste(src_p, (6, 6), mask); phs.append((tile, tuple(pc["at"])))
        callouts.append({"a": a, "e": e, "tl": (e[0] + c.get("tail", 50) * sgn, e[1]), "at": c["at"], "sgn": sgn,
                         "br": c.get("bracket"), "col": COL.get(c.get("color", "cream"), COL["cream"]), "phs": phs})

    def frame(t):
        im = B.bg_at(t)
        p = B.ease_out(min(1, t / 0.8))
        if p > 0:
            sh = shadow.copy(); sh.putalpha(sh.getchannel("A").point(lambda v: int(v * p))); im.alpha_composite(sh)
            c = cup.copy(); c.putalpha(c.getchannel("A").point(lambda v: int(v * p)))
            im.alpha_composite(c, (x0, y0 + int(60 * (1 - p))))
        d = ImageDraw.Draw(im, "RGBA")
        for k in callouts:
            a, e, tl, col = k["a"], k["e"], k["tl"], k["col"]
            q = (t - k["at"]) / 0.6
            if q <= 0:
                continue
            q1, q2 = B.ease_out(min(1, q / 0.7)), B.ease_out(max(0, min(1, (q - 0.7) / 0.3)))
            rad = 9 * B.ease_back(min(1, q / 0.4))
            d.ellipse([a[0] - rad - 5, a[1] - rad - 5, a[0] + rad + 5, a[1] + rad + 5], outline=col, width=3)
            d.ellipse([a[0] - rad * 0.55, a[1] - rad * 0.55, a[0] + rad * 0.55, a[1] + rad * 0.55], fill=col)
            m = (a[0] + (e[0] - a[0]) * q1, a[1] + (e[1] - a[1]) * q1)
            d.line([a, m], fill=col, width=4)
            if q2 > 0:
                for tile, (px, py) in k["phs"]:
                    tc = tile.copy(); tc.putalpha(tc.getchannel("A").point(lambda v: int(v * q2)))
                    im.alpha_composite(tc, (int(px - tile.width / 2), int(py - tile.height / 2)))
                d = ImageDraw.Draw(im, "RGBA")
            if q2 > 0:
                if k["br"]:
                    # 縦の括り線：終わりの点から上下へ伸び、両端に文字側へ短い返し
                    bx = tl[0]; top, bot = k["br"]
                    d.line([e, (e[0] + (bx - e[0]) * q2, e[1])], fill=col, width=4)
                    d.line([(bx, e[1] + (top - e[1]) * q2), (bx, e[1] + (bot - e[1]) * q2)], fill=col, width=4)
                    if q2 >= 1:
                        for yy in (top, bot):
                            d.line([(bx, yy), (bx + 18 * k["sgn"], yy)], fill=col, width=4)
                else:
                    d.line([e, (e[0] + (tl[0] - e[0]) * q2, e[1])], fill=col, width=4)
        return im
    B.render(frame, spec.get("dur", 8.0), out, "callout")


if __name__ == "__main__":
    main()
