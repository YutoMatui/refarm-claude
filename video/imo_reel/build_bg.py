# -*- coding: utf-8 -*-
"""「10月の新メニュー 極 焼きいもスープ」リールの背景動画（文字なし）をそろえる。文字は CapCut で後入れ。

  python build_bg.py        … clips/ に 01 の元絵・02 図解・03 寄り・04 カレンダー・06 ロゴ を作る
  01 は元絵（src/01_spoon_916.png）まで。動かすのは gen_clip.py（約180円・要承認）か Dreamina／CapCut の無料生成
  05 店の前・外観は 10月の営業日リール（video/cal_reel/clips/03a・03b）を使い回す
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SK = os.path.join(HERE, "..", "..", ".claude", "skills", "reel-capcut", "scripts")
sys.path.insert(0, SK)
import bg_common as B
from common import key_green
from PIL import Image

os.makedirs(os.path.join(HERE, "clips"), exist_ok=True)
P = lambda *a: os.path.join(HERE, *a)


def spoon_still():
    """スプーンの絵（グリーンバック）を金色の地に載せて 9:16 の元絵にする（広げる生成はしない）"""
    im = key_green(P("src", "kv_spoon_green.png")); r = 860 / im.width
    im = im.resize((860, int(im.height * r)), Image.LANCZOS)
    # 元絵の湯気・影は緑みが残って合成に見えるので捨てる（湯気は動画生成で足す）
    import numpy as np
    a = np.array(im).astype(np.float32); a[..., 3] = np.where(a[..., 3] < 150, 0, (a[..., 3] - 150) * 255 / 105)
    im = Image.fromarray(a.clip(0, 255).astype("uint8"), "RGBA")
    bg = B.gold_bg(); bg.alpha_composite(im, (110, B.H - im.height - 170))  # 上の見出しの場所を空ける
    bg.convert("RGB").save(P("src", "01_spoon_916.png")); print("できました: src/01_spoon_916.png")


def cup_closeup():
    """カップにゆっくり寄る 3.5秒（大学芋と黒ごませんべいを見せる）"""
    cup = key_green(P("src", "cup_green.png"))
    cup.putalpha(cup.getchannel("A").point(lambda v: 0 if v < 200 else int((v - 200) * 255 / 55)))
    BG = B.gold_bg()

    def frame(t):
        k = 760 + 140 * B.ease_out(min(1, t / 3.5)); c = cup.resize((int(k), int(cup.height * k / cup.width)), Image.LANCZOS)
        im = BG.copy(); im.alpha_composite(c, ((B.W - c.width) // 2, 880 - int(c.height * 0.5))); return im  # 下の文字の場所を空ける
    B.render(frame, 3.5, P("clips", "03_cup_close.mp4"), "close")


if __name__ == "__main__":
    spoon_still()
    subprocess.run([sys.executable, os.path.join(SK, "bg_callout.py"), P("zukai.json"), P("clips", "02_zukai.mp4")], check=True)
    cup_closeup()
    subprocess.run([sys.executable, os.path.join(SK, "bg_calendar.py"), "--year", "2026", "--month", "10",
                    "--open", "12,13,15,19,22,26,27,29", "--closed", "20", "--cup", P("src", "cup_green.png"),
                    "--out", P("clips", "04_calendar.mp4")], check=True)
    subprocess.run([sys.executable, os.path.join(SK, "bg_end.py"), "--out", P("clips", "06_end.mp4")], check=True)
