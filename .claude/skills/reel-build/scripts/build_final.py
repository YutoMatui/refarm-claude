# -*- coding: utf-8 -*-
"""間借り編2「全部、断られました」完成版（テロップなし）

粗つなぎからの品質引き上げ:
- seg2(ネットで探せば)にシェアレストラン画面録画を採用。590x1280の縦画面は
  中央cropだと内容が切れるため「背景ぼかし+前景等倍」方式。URLバー(サービス名)はぼかしで伏せる。
- 全体マスタリング: loudnorm(-16LUFS)で音量統一、冒頭0.5sフェードイン、末尾0.7sフェードアウト。
- 画質: crf18 / preset slow。
"""
import subprocess, json, os

W = os.path.dirname(os.path.abspath(__file__))
os.chdir(W)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

def dur(path):
    out = run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",path]).stdout
    return float(json.loads(out)["format"]["duration"])

SCREEN = "シェアレストラン_画面録画.mp4"

# セグメント定義: (音声, [(クリップ, 開始オフセット秒), ...])
SEGS = [
    ("オープニング.m4a", [("オープニング.mp4", 0)]),
    ("お店12件.m4a", [("IMG_2884_室内ジャケット正面真剣.MOV", 1.0), ("IMG_1786_室内頭抱え悩む.MOV", 0.5)]),
    # 「ネットで探せば」: PCの前で考える→実際のマッチングサイト画面録画
    # 画面録画は4.4秒以降を使う（それ以前はサイトのロゴ大写しがぼかし圏外に映るため）
    ("ネットで探せば.m4a", [("IMG_1497_PC頬杖考える.MOV", 0.5), (SCREEN, 4.4)]),
    ("だから足で回る.m4a", [("書きながら悩んでる.MOV", 0.5), ("IMG_1789_室内電話ふう後ろ姿.MOV", 1.0), ("IMG_6812_商店街歩く後ろ姿.MOV", 2.0)]),
    ("でもダメでした.m4a", [("紙投げる.MOV", 0), ("紙投げる2.MOV", 0), ("書きながら悩んでる.MOV", 10.0)]),
    ("心折れてる.m4a", [("IMG_6813_横断歩道振り返り.MOV", 1.0), ("IMG_1787_室内前かがみ落ち込み後ろ姿.MOV", 0.5)]),
    ("エンディング.m4a", [("あきらめたくない　１.MOV", 0), ("エンディング.mp4", 0)]),
]

# 通常素材: 拡大→中央crop（実写はcropで切れても問題ない）
VS = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p"

def screen_filter(idx, extra):
    """画面録画用: 背景=拡大ぼかし、前景=切らずに等倍フィット、URLバー(上部約290px)をぼかして伏せる"""
    return (
        f"[{idx}:v]fps=30,setsar=1,split=2[s{idx}a][s{idx}b];"
        f"[s{idx}a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.08[bg{idx}];"
        f"[s{idx}b]scale=-2:1920[fgraw{idx}];"
        f"[fgraw{idx}]split=2[fg{idx}a][fg{idx}b];"
        f"[fg{idx}b]crop=iw:450:0:0,gblur=sigma=28[bar{idx}];"
        f"[fg{idx}a][bar{idx}]overlay=0:0[fg{idx}];"
        f"[bg{idx}][fg{idx}]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p{extra}[v{idx}]"
    )

parts = []
for idx, (audio, clips) in enumerate(SEGS):
    adur = dur(audio)
    takes = []
    remaining = adur
    for i, (clip, off) in enumerate(clips):
        avail = max(0.3, dur(clip) - off - 0.05)
        want = remaining / (len(clips) - i)
        take = min(want, avail)
        takes.append((clip, off, take))
        remaining -= take
    pad = max(0.0, remaining)

    inputs, fparts = [], []
    for i, (clip, off, take) in enumerate(takes):
        inputs += ["-ss", f"{off:.3f}", "-t", f"{take:.3f}", "-i", clip]
        extra = f",tpad=stop_mode=clone:stop_duration={pad:.3f}" if (i == len(takes)-1 and pad > 0.01) else ""
        if clip == SCREEN:
            fparts.append(screen_filter(i, extra))
        else:
            fparts.append(f"[{i}:v]{VS}{extra}[v{i}]")
    n = len(takes)
    fc = ";".join(fparts) + ";" + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    out = f"f_seg{idx}.mp4"
    cmd = ["ffmpeg","-y"] + inputs + ["-i", audio,
           "-filter_complex", fc, "-map", "[v]", "-map", f"{n}:a",
           "-c:v","libx264","-preset","slow","-crf","18","-c:a","aac","-b:a","192k",
           "-t", f"{adur:.3f}", "-shortest", out]
    r = run(cmd)
    if r.returncode != 0:
        print("FAIL", out, r.stderr[-800:]); raise SystemExit(1)
    print("ok", out, f"{dur(out):.2f}s / audio {adur:.2f}s")
    parts.append(out)

with open("list_final.txt","w",encoding="utf-8") as f:
    for p in parts: f.write(f"file '{p}'\n")
run(["ffmpeg","-y","-f","concat","-safe","0","-i","list_final.txt","-c","copy","_joined.mp4"])

# マスタリング: 音量統一 + フェードイン/アウト
D = dur("_joined.mp4")
FINAL = "間借り編2_完成版.mp4"
r = run(["ffmpeg","-y","-i","_joined.mp4",
    "-vf", f"fade=t=in:st=0:d=0.5,fade=t=out:st={D-0.7:.3f}:d=0.7",
    "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st={D-0.7:.3f}:d=0.7",
    "-c:v","libx264","-preset","slow","-crf","18","-c:a","aac","-b:a","192k",
    FINAL])
if r.returncode != 0:
    print("FAIL master", r.stderr[-800:]); raise SystemExit(1)
print("FINAL", f"{dur(FINAL):.2f}s", round(os.path.getsize(FINAL)/1e6,1), "MB")
