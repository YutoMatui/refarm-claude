# -*- coding: utf-8 -*-
"""最後の1枚の背景動画（4秒）：金色の地に VEGEONE のワードマークがふわっと出る。
文字（団体名・営業時間・@）は CapCut で後入れ。ワードマークは creative-kv/scripts/brand.py が描く（AIに描かせない）。

  python bg_end.py --out clips/05_end.mp4
  python bg_end.py --out clips/05_end_qr.mp4 --qr src/line_qr.png     … 公式LINEのQRを下に置く（ワードマークは上へ）
"""
import argparse
from PIL import Image
import bg_common as B
from brand import wordmark


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--dur", type=float, default=4.0)
    ap.add_argument("--qr", default="", help="QR画像。指定するとワードマークを上（y=560）に、QRを中央（y=1150・380px）に置く")
    a = ap.parse_args()
    qr = None
    if a.qr:
        from PIL import ImageDraw
        q = Image.open(a.qr).convert("RGB"); side = min(q.size)
        q = q.crop(((q.width - side) // 2, (q.height - side) // 2, (q.width - side) // 2 + side, (q.height - side) // 2 + side)).resize((330, 330), Image.LANCZOS)
        qr = Image.new("RGBA", (380, 380), (0, 0, 0, 0)); ImageDraw.Draw(qr).rounded_rectangle([0, 0, 379, 379], radius=28, fill=(255, 255, 255, 255))
        qr.paste(q, (25, 25))
    WM = wordmark(220, B.CREAM)
    WM = WM.resize((B.W - 160, int(WM.height * (B.W - 160) / WM.width)), Image.LANCZOS)

    def frame(t):
        im = B.bg_at(t); p = B.ease_out(min(1, t / 1.0))
        wm = WM.copy(); wm.putalpha(wm.getchannel("A").point(lambda v: int(v * p)))
        wy = 560 if qr is not None else 760
        im.alpha_composite(wm, (80, wy + int(30 * (1 - p))))
        if qr is not None:
            p2 = B.ease_out(max(0, min(1, (t - 0.5) / 0.8)))
            if p2 > 0:
                qq = qr.copy(); qq.putalpha(qq.getchannel("A").point(lambda v: int(v * p2)))
                im.alpha_composite(qq, (540 - 190, 1150 - 190 + int(30 * (1 - p2))))
        return im
    B.render(frame, a.dur, a.out, "end")


if __name__ == "__main__":
    main()
