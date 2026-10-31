# -*- coding: utf-8 -*-
"""実写の動画を 1080×1920 にそろえるときの色の扱い（prep_clip.py と render_mp4.py で共通）。

iPhone の動画は HDR（HLG・BT.2020・10bit）で撮られていることが多い。これを普通の scale/crop だけで
縮めると、色の変換をしないまま「普通の動画」として扱われ、灰色っぽく暗く沈む（2026-10-31 ゆうとの指摘
「謎のエフェクト・暗い・画質が悪い」）。HDR かどうかを ffprobe で見て、HDR なら色を変換し直す。

- HDR かつ このPCで Vulkan＋libplacebo が動く → libplacebo（GPU）でトーンマッピング（bt.2390）＋縮小（ewa_lanczos）
- HDR だが Vulkan が使えない（GPU ドライバが古いPCなど）→ zscale＋tonemap=hable（CPU。少し遅い・色は少し地味）
- SDR（普通の動画・生成動画）→ これまでどおり scale（lanczos）＋crop

環境変数 REEL_HDR=fallback で、Vulkan が使えても CPU の方式を使う（確かめる用）。
"""
import os
import subprocess

W, H = 1080, 1920
HDR_TRC = ("arib-std-b67", "smpte2084")   # HLG と PQ
BT709_TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]

_placebo_ok = None


def color_transfer(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "default=nw=1:nk=1", src], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()


def is_hdr(src):
    return color_transfer(src) in HDR_TRC


def has_placebo():
    """このPCで Vulkan＋libplacebo が動くか（1回だけ小さく試して覚えておく）。"""
    global _placebo_ok
    if _placebo_ok is None:
        if os.environ.get("REEL_HDR") == "fallback":
            _placebo_ok = False
        else:
            try:
                r = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-init_hw_device", "vulkan",
                                    "-f", "lavfi", "-i", "color=c=gray:s=64x64:d=0.1",
                                    "-vf", "libplacebo=w=32:h=32:format=yuv420p", "-frames:v", "1", "-f", "null", "-"],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
                _placebo_ok = r.returncode == 0
            except (OSError, subprocess.TimeoutExpired):
                _placebo_ok = False
    return _placebo_ok


def video_args(src, fit="cover", fps=30, cpu=False):
    """(入力の前に置く引数, -vf の中身, 出力に付ける色タグ) を返す。

    fit="cover"   … 画面いっぱい（はみ出たぶんを中央で切る。横長でも縦長でも）
    fit="contain" … 全体を収めて黒帯
    cpu=True      … HDR でも GPU を使わない（GPU 方式で失敗したときのやり直し用）
    回転情報（縦撮り）は ffmpeg が先に縦へ直すので、ここでは向きを気にしなくてよい。
    """
    tail = ",fps=%d,setsar=1,format=yuv420p" % fps
    trc = color_transfer(src)
    if trc not in HDR_TRC:
        if fit == "contain":
            vf = "scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,pad=%d:%d:(ow-iw)/2:(oh-ih)/2" % (W, H, W, H)
        else:
            vf = "scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d" % (W, H, W, H)
        return [], vf + tail, []
    if not cpu and has_placebo():
        # 縦長でも横長でも切り出す窓は min(…) で 9:16 にする（cover）。contain は全体を縮めて黒で埋める
        if fit == "contain":
            geo = "w=%d:h=%d:pos_w='min(ow,oh*iw/ih)':pos_h='min(oh,ow*ih/iw)':fillcolor=black" % (W, H)
        else:
            geo = "w=%d:h=%d:crop_w='min(iw,ih*%d/%d)':crop_h='min(ih,iw*%d/%d)'" % (W, H, W, H, H, W)
        vf = ("libplacebo=%s:colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv:"
              "tonemapping=bt.2390:upscaler=ewa_lanczos:downscaler=ewa_lanczos:format=yuv420p" % geo)
        return ["-init_hw_device", "vulkan"], vf + tail, BT709_TAGS
    # 予備（CPU）：先に 10bit のまま縮めてから、線形光にして hable で丸め、BT.709 に戻す
    if fit == "contain":
        geo = "scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,pad=%d:%d:(ow-iw)/2:(oh-ih)/2" % (W, H, W, H)
    else:
        geo = "scale=%d:%d:force_original_aspect_ratio=increase:flags=lanczos,crop=%d:%d" % (W, H, W, H)
    # npl：HLG は 75 で GPU 方式とほぼ同じ明るさになる（IMG_2957 で比べた。100 だと一段暗い）
    npl = 75 if trc == "arib-std-b67" else 100
    vf = (geo + ",zscale=tin=%s:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=%d,format=gbrpf32le,"
          "zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv" % (trc, npl))
    return [], vf + tail, BT709_TAGS


def run(build, src, fit="cover"):
    """build(pre, vf, tags) が返す ffmpeg コマンドを実行する。
    GPU 方式で失敗したら（メモリ不足・ドライバ。4K を縮めるとき 1 回起きた）CPU 方式で 1 回だけやり直す。"""
    def go(args):
        return subprocess.run(build(*args), capture_output=True, text=True, encoding="utf-8", errors="replace")
    args = video_args(src, fit)
    r = go(args)
    if r.returncode and args[0]:
        last = (r.stderr.strip().splitlines() or [""])[-1]
        print("  GPU の方式で失敗したので、CPU の方式でやり直します（%s）" % last[-120:])
        r = go(video_args(src, fit, cpu=True))
    return r


def method(src):
    """表示用：どの方式で変換するか。"""
    if not is_hdr(src):
        return "SDR"
    return "HDR→SDR（GPU・libplacebo）" if has_placebo() else "HDR→SDR（CPU・zscale+hable）"
