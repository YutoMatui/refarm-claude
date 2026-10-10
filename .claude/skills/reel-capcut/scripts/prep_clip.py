# -*- coding: utf-8 -*-
"""実写や生成動画を、ドラフトに入れられる形（1080×1920・30fps・音声トラックあり）にそろえる。

  python prep_clip.py 入力.MOV 出力.mp4 [--ss 開始秒] [--t 長さ秒]
  python prep_clip.py --crop 元絵.png 出力.png      … 静止画を9:16に切る（画像→動画生成の元絵用。広げる生成はしない）

横長や回転情報つきのスマホ動画は自動で縦に直し、中央を切って画面いっぱいにする。
無音の動画には無音トラックを足す（CapCut と render_mp4 の両方で必要）。
"""
import argparse, subprocess
from PIL import Image


def has_audio(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type",
                          "-of", "csv=p=0", p], capture_output=True, text=True).stdout
    return "audio" in out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--ss", type=float, default=0); ap.add_argument("--t", type=float, default=0)
    ap.add_argument("--crop", action="store_true")
    a = ap.parse_args()
    if a.crop:
        im = Image.open(a.src).convert("RGB"); w, h = im.size
        if w / h > 9 / 16:
            cw = int(h * 9 / 16); box = ((w - cw) // 2, 0, (w - cw) // 2 + cw, h)
        else:
            ch = int(w * 16 / 9); box = (0, (h - ch) // 2, w, (h - ch) // 2 + ch)
        im.crop(box).resize((1080, 1920), Image.LANCZOS).save(a.dst)
        print("できました:", a.dst, "(1080x1920)")
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    if a.ss:
        cmd += ["-ss", str(a.ss)]
    if a.t:
        cmd += ["-t", str(a.t)]
    cmd += ["-i", a.src]
    if not has_audio(a.src):
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest"]
    cmd += ["-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "-r", "30",
            "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart", a.dst]
    subprocess.run(cmd, check=True)
    print("できました:", a.dst)


if __name__ == "__main__":
    main()
