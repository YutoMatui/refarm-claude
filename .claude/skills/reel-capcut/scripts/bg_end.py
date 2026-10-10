# -*- coding: utf-8 -*-
"""最後の1枚の背景動画（4秒）：金色の地に VEGEONE のワードマークがふわっと出る。
文字（団体名・営業時間・@）は CapCut で後入れ。ワードマークは creative-kv/scripts/brand.py が描く（AIに描かせない）。

  python bg_end.py --out clips/05_end.mp4
"""
import argparse
from PIL import Image
import bg_common as B
from brand import wordmark


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--dur", type=float, default=4.0)
    a = ap.parse_args()
    WM = wordmark(220, B.CREAM)
    WM = WM.resize((B.W - 160, int(WM.height * (B.W - 160) / WM.width)), Image.LANCZOS)

    def frame(t):
        im = B.gold_bg(t * 0.8); p = B.ease_out(min(1, t / 1.0))
        wm = WM.copy(); wm.putalpha(wm.getchannel("A").point(lambda v: int(v * p)))
        im.alpha_composite(wm, (80, 760 + int(30 * (1 - p))))
        return im
    B.render(frame, a.dur, a.out, "end")


if __name__ == "__main__":
    main()
