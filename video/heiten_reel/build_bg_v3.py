# -*- coding: utf-8 -*-
"""11月閉店動画 第3版の背景動画（文字なし・1080×1920・30fps）をそろえる。

  python build_bg_v3.py          … clips_v3/ に全部作る
  python build_bg_v3.py 02 07    … 番号を指定して作り直す

第2版からの変更（2026-10-31 ゆうとの指摘「暗い・画質が悪い」）：
- iPhone の映像は HDR（HLG・BT.2020・10bit）。これをそのまま普通の動画にすると灰色っぽく暗く沈む。
  libplacebo で色を変換し直して（トーンマッピング bt.2390）、見た目どおりの明るさ・色に戻す
- 縮小は lanczos、圧縮は crf 12・preset slow（何度も圧縮し直さない。つなぐときは再圧縮しない）
- 写真の寄り・横流しは Python で1コマずつ小数点の位置で描く（ffmpeg の zoompan のガタつきを出さない）
- 閉店します＝お辞儀／オープン＝のぼりを立てた外観・2Fの看板・店内で手を振る
- やめたメンバーが写っているマルシェの写真は使わない
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "G:/マイドライブ/50日企画素材"
CAND = ROOT + "/11月閉店動画_素材候補"
STORE = ROOT + "/道案内"
OUT = os.path.join(HERE, "clips_v3")
TMP = os.path.join(tempfile.gettempdir(), "heiten_v3"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = 1080, 1920, 30
ENC = ["-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]

PLATE = STORE + "/IMG_2963.MOV"        # 店で焼き芋スープを盛り付ける（61秒）
TRAY = STORE + "/IMG_2965.MOV"         # 席にスープが届く
BOW = STORE + "/IMG_2957.MOV"          # お辞儀
STAND = STORE + "/IMG_2960.MOV"        # カウンターの奥で立って笑顔
SMILE = STORE + "/IMG_2962.MOV"        # テーブルの奥で笑顔
HEART = STORE + "/IMG_2956.MOV"        # 手でハート
WELCOME = ROOT + "/間借り/eQCFGr_zLXiut8ffwJsjXIVGaBa7aVmG78eqfwxa2Tc.mp4"   # エプロンで両手を振る（店内）
WAVE = CAND + "/4_エンディング_店の前で手を振る_実写3秒.mp4"


def run(cmd, **kw):
    subprocess.run(cmd, check=True, encoding="utf-8", errors="replace", **kw)


def v(src, ss, t):
    return ("v", src, ss, t)


def p(img, t, move="push", cx=0.5, cy=0.5):
    """写真を t 秒の動画にする。push＝ゆっくり寄る／pan＝横長の写真を左から右へ流す。cx,cy＝切り取る中心（0〜1）"""
    return ("p", img, t, move, cx, cy)


def is_hdr(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "default=nw=1:nk=1", src], capture_output=True, text=True)
    return r.stdout.strip() in ("arib-std-b67", "smpte2084")


def cut_video(src, ss, t, dst):
    if is_hdr(src):
        # iPhone の HDR → 普通の動画（BT.709）。GPU（Vulkan）で色を変換して 1080×1920 に縮める
        vf = ("libplacebo=w=1080:h=1920:crop_w=iw:crop_h=iw*16/9:colorspace=bt709:color_primaries=bt709:"
              "color_trc=bt709:range=tv:tonemapping=bt.2390:upscaler=ewa_lanczos:downscaler=ewa_lanczos:"
              f"format=yuv420p,fps={FPS}")
        pre = ["-init_hw_device", "vulkan"]
    else:
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos:out_range=tv:out_color_matrix=bt709,"
              f"crop={W}:{H},fps={FPS},format=yuv420p")
        pre = []
    run(["ffmpeg", "-y", "-loglevel", "error", *pre, "-ss", str(ss), "-t", str(t), "-i", src,
         "-vf", vf, "-an", *ENC, dst])


def cut_photo(img, t, move, cx, cy, dst):
    im = img if isinstance(img, Image.Image) else ImageOps.exif_transpose(Image.open(img)).convert("RGB")
    n = max(2, round(t * FPS))
    iw, ih = im.size
    # 9:16 の窓（元画像の画素のまま。縮めない）
    if iw / ih > W / H:
        wh, ww = ih, ih * W / H
    else:
        ww, wh = iw, iw * H / W
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-vf", "scale=out_range=tv:out_color_matrix=bt709:flags=lanczos,format=yuv420p",
                             *ENC, dst], stdin=subprocess.PIPE)
    for k in range(n):
        a = k / (n - 1)
        a = a * a * (3 - 2 * a) if move == "pan" else a      # 横流しは始めと終わりをなめらかに
        if move == "pan":
            span = iw - ww
            x0 = span * (0.08 + 0.84 * a); y0 = (ih - wh) * cy; w_, h_ = ww, wh
        else:
            z = 1 + 0.06 * a                                  # 1秒で6%寄る（ゆっくり）
            w_, h_ = ww / z, wh / z
            x0 = (iw - w_) * cx; y0 = (ih - h_) * cy
        fr = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w_, y0 + h_))
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    if proc.returncode:
        raise SystemExit("写真の書き出しに失敗: %s" % dst)


def insta_card():
    """インスタのプロフィール画面（時計・電池の帯と閲覧数を外して上下につなぐ）"""
    im = Image.open(os.path.join(HERE, "src", "insta_profile.jpg")).convert("RGB")
    w, h = im.size; s = w / 923
    top = im.crop((0, int(150 * s), w, int(890 * s)))
    grid = im.crop((0, int(1255 * s), w, int(1800 * s)))
    card = Image.new("RGB", (w, top.height + grid.height), "white")
    card.paste(top, (0, 0)); card.paste(grid, (0, top.height))
    bg = Image.new("RGB", (W * 2, H * 2), (251, 250, 246))   # 寄る動きでぼけないよう2倍で作る
    card = card.resize(((W - 80) * 2, round(card.height * (W - 80) * 2 / card.width)), Image.LANCZOS)
    bg.paste(card, ((W * 2 - card.width) // 2, 600 * 2))
    return bg


def build(name, parts):
    pieces = []
    for i, part in enumerate(parts):
        dst = os.path.join(TMP, f"{name[:2]}_{i:02d}.mp4")
        if part[0] == "v":
            cut_video(part[1], part[2], part[3], dst)
        else:
            cut_photo(part[1], *part[2:], dst)
        pieces.append(dst)
    lst = os.path.join(TMP, f"{name[:2]}_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        f.writelines(f"file '{x}'\n" for x in pieces)
    # つなぐときは再圧縮しない（画質を落とさない）。CapCut 用に無音の音声だけ付ける
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", os.path.join(OUT, name)])
    return sum(x[3] if x[0] == "v" else x[2] for x in parts)


GROUPS = {
    # 三宮のスープ屋さん VEGEONE は 11月26日で閉店します（お辞儀）
    "01_bow.mp4": [v(BOW, 1.0, 3.3)],
    # 8月20日にオープンして（のぼりを立てた外観 → 2Fの看板の入口 → 店内で両手を振る）
    "02_open.mp4": [p(ROOT + "/完成動画/VEGEONE_外観_のぼりあり.jpg", 1.2, cy=0.6),
                    p(ROOT + "/食べログ/02_外観_1階入口（2Fの看板）.jpg", 1.0, cx=0.12, cy=0.7),
                    v(WELCOME, 0.0, 1.5)],
    # あっという間の3か月（これまでのスープ）
    "03_soups.mp4": [p(CAND + "/1_OP_スープ写真_トマト冷製_実物.jpg", 1.0),
                     p(CAND + "/1_OP_スープ写真_枝豆冷製_実物.jpg", 1.0),
                     p(CAND + "/1_OP_スープ写真_とうもろこし_実物.jpg", 1.0),
                     p(CAND + "/1_OP_スープ写真_4種とパン_実物.jpg", 1.4, move="pan")],
    # たくさんのご来店 ありがとうございました（盛り付けて席に届ける）
    "04_thanks.mp4": [v(PLATE, 0.4, 1.0), v(PLATE, 12.6, 1.0), v(TRAY, 5.0, 1.6)],
    # みなさんのおかげで 毎日たのしく営業できました（店で盛り付けている手元＋笑顔）
    "05_work.mp4": [v(PLATE, 30.2, 1.0), v(PLATE, 46.0, 1.0), v(PLATE, 57.3, 1.0),
                    v(SMILE, 2.0, 1.0), v(HEART, 1.3, 1.2)],
    # でも これで終わりではありません（カウンターの奥で立って笑顔）
    "06_but.mp4": [v(STAND, 0.8, 2.2)],
    # これからは神戸市の マルシェやイベントで スープを届けます（商大祭のテント）
    "07_next.mp4": [p(CAND + "/3_次へ_商大祭テントのメンバー集合_実物.jpg", 4.0, move="pan")],
    # 出店の情報はインスタで
    "08_insta.mp4": [p("INSTA", 1.8)],
    # お店で食べられるのは あと4日だけ → 11月の木曜 5・12・19・26日 11:00〜14:00
    "09_days.mp4": [p(CAND + "/4_エンディング_今の焼き芋スープ_実物.jpg", 1.9), v(PLATE, 52.0, 2.4)],
    # 最後に食べにきてください！（店の前で手を振る）
    "10_end.mp4": [v(WAVE, 0, 3.4)],
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    want = sys.argv[1:]
    for name, parts in GROUPS.items():
        if want and name[:2] not in want:
            continue
        parts = [(x[0], insta_card(), *x[2:]) if x[1] == "INSTA" else x for x in parts]
        print("できました: %s（%.2f秒）" % (name, build(name, parts)), flush=True)
