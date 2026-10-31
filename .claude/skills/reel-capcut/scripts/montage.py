# -*- coding: utf-8 -*-
"""速いカットの背景動画（文字なし・1080×1920・30fps）を、1つの文ごとに1本ずつ作る。

    python montage.py montage.json            … 全部作る
    python montage.py montage.json 02 07      … 番号（ファイル名の先頭2文字）を指定して作り直す

1つの文（＝plan.json の1セグメント）の間に、約1秒のカットを数本つないで1本の mp4 にする。
できた mp4 を plan.json の clips に1本ずつ並べ、文字は make_draft.py で CapCut の文字として入れる。
11月閉店動画（2026-10-31、video/heiten_reel/）で決めたやり方。決まりは reference/style_promo.md。

montage.json の形:
{
  "root": "G:/マイドライブ/50日企画素材",     // 素材の場所（各パスはここからの相対でも絶対でもよい）
  "out_dir": "clips",                          // montage.json からの相対
  "groups": {
    "01_bow.mp4":  [{"video": "道案内/IMG_2957.MOV", "ss": 1.0, "t": 3.3}],
    "02_open.mp4": [{"photo": "完成動画/VEGEONE_外観_のぼりあり.jpg", "t": 1.2, "cy": 0.6},
                    {"video": "間借り/xxx.mp4", "ss": 0, "t": 1.5}],
    "03_soups.mp4": [{"photo": "…/4種とパン.jpg", "t": 1.4, "move": "pan"}]
  }
}
  video … ss＝始める秒、t＝長さ。iPhone の HDR は hdr.py が自動で色を直す（直さないと灰色っぽく暗く沈む）
  photo … t＝長さ。move＝"push"（既定。ゆっくり6%寄る）／"pan"（横長の写真を左から右へ流す）
          cx, cy＝切り取る中心（0〜1。既定0.5）。看板や器が端で切れるときに動かす

画質の決まり：縮小は lanczos、圧縮は crf 12・preset slow、BT.709 の色タグを付ける。
カットをつなぐときは再圧縮しない（-c copy）。写真の動きは1コマずつ小数点の位置で描く（zoompan のガタつきを出さない）。
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hdr  # noqa: E402

W, H, FPS = 1080, 1920, 30
ENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p"] + hdr.BT709_TAGS
TMP = os.path.join(tempfile.gettempdir(), "reel_montage")


def cut_video(src, ss, t, dst):
    r = hdr.run(lambda pre, vf, tags: ["ffmpeg", "-y", "-loglevel", "error", *pre, "-ss", str(ss), "-t", str(t),
                                       "-i", src, "-vf", vf, "-an", *ENC, dst], src)
    if r.returncode:
        raise SystemExit("動画の切り出しに失敗: %s\n%s" % (src, r.stderr[-1500:]))


def cut_photo(path, t, move, cx, cy, dst):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    n = max(2, round(t * FPS))
    iw, ih = im.size
    # 9:16 の窓（元画像の画素のまま切る。先に縮めない）
    if iw / ih > W / H:
        wh, ww = ih, ih * W / H
    else:
        ww, wh = iw, iw * H / W
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
                             "-vf", "scale=out_range=tv:out_color_matrix=bt709:flags=lanczos,format=yuv420p",
                             *ENC, dst], stdin=subprocess.PIPE)
    for k in range(n):
        a = k / (n - 1)
        if move == "pan":
            a = a * a * (3 - 2 * a)                       # 始めと終わりをなめらかに
            x0 = (iw - ww) * (0.08 + 0.84 * a); y0 = (ih - wh) * cy; w_, h_ = ww, wh
        else:
            z = 1 + 0.06 * a
            w_, h_ = ww / z, wh / z
            x0 = (iw - w_) * cx; y0 = (ih - h_) * cy
        proc.stdin.write(im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w_, y0 + h_)).tobytes())
    proc.stdin.close(); proc.wait()
    if proc.returncode:
        raise SystemExit("写真の書き出しに失敗: %s" % path)


def build(name, parts, root, out_dir):
    os.makedirs(TMP, exist_ok=True)
    pieces, total = [], 0.0
    for i, p in enumerate(parts):
        dst = os.path.join(TMP, "%s_%02d.mp4" % (name[:2], i))
        if "video" in p:
            src = p["video"] if os.path.isabs(p["video"]) else os.path.join(root, p["video"])
            cut_video(src, p.get("ss", 0), p["t"], dst)
        else:
            src = p["photo"] if os.path.isabs(p["photo"]) else os.path.join(root, p["photo"])
            cut_photo(src, p["t"], p.get("move", "push"), p.get("cx", 0.5), p.get("cy", 0.5), dst)
        pieces.append(dst); total += p["t"]
    lst = os.path.join(TMP, "%s_list.txt" % name[:2])
    with open(lst, "w", encoding="utf-8") as f:
        f.writelines("file '%s'\n" % x.replace("\\", "/") for x in pieces)
    # つなぐときは再圧縮しない。CapCut 用に無音の音声トラックだけ付ける
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart",
                        os.path.join(out_dir, name)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit("つなぐのに失敗: %s\n%s" % (name, r.stderr[-1500:]))
    return total


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = os.path.abspath(sys.argv[1])
    cfg = json.load(open(path, encoding="utf-8"))
    root = cfg.get("root", "")
    out_dir = os.path.join(os.path.dirname(path), cfg.get("out_dir", "clips"))
    os.makedirs(out_dir, exist_ok=True)
    want = sys.argv[2:]
    for name, parts in cfg["groups"].items():
        if want and name[:2] not in want:
            continue
        print("できました: %s（%.2f秒）" % (name, build(name, parts, root, out_dir)), flush=True)


if __name__ == "__main__":
    main()
