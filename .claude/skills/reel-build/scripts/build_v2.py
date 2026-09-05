# -*- coding: utf-8 -*-
"""間借り編2 v2「全部、断られました」完成版（テロップ・効果音入り）

v1からの変更（2026-07-31 ゆうと指示）:
- 素材差し替え: PC操作=IMG_1500 / 断られました=IMG_1526 / でもダメでした=IMG_1523 /
  足で回る=三宮歩き / 12軒ゼロ=IMG_6814+6821 / 諦めません=IMG_6815(前を指さして歩く)
- シェアレストラン画面は全面モザイク（シェアレストラン_モザイク.mp4）
- テロップ焼き込み: HG創英角ポップ体・白字黒縁・中央・下1/3（1本目の様式）
- 効果音: don/whoosh/pop/kiran/sad を要所に配置
"""
import subprocess, json, os

W = os.path.dirname(os.path.abspath(__file__))
os.chdir(W)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

def dur(path):
    out = run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",path]).stdout
    return float(json.loads(out)["format"]["duration"])

X264 = ["-c:v","libx264","-preset","veryfast","-crf","18",
        "-x264-params","threads=2:lookahead-threads=1:rc-lookahead=10"]

SEGS = [
    ("オープニング.m4a", [("オープニング.mp4", 0)]),
    ("お店12件.m4a", [("IMG_2884_室内ジャケット正面真剣.MOV", 1.0), ("IMG_1526_芝生しゃがみ観察.MOV", 0.1)]),
    ("ネットで探せば.m4a", [("IMG_1500_PCうつむき没頭.MOV", 0.5), ("シェアレストラン_モザイク.mp4", 0.3)]),
    ("だから足で回る.m4a", [("IMG_6813_横断歩道振り返り.MOV", 1.0), ("IMG_6816_2人指さし商店街.MOV", 0.2)]),
    ("でもダメでした.m4a", [("IMG_1523_段差前かがみ落ち込み.MOV", 0.2), ("IMG_2886_室内ジャケット正面語り長尺2.MOV", 5.0)]),
    ("心折れてる.m4a", [("IMG_6814_2人歩く後ろ姿長尺.MOV", 3.0), ("IMG_6821_2人街角立ち止まり.MOV", 1.0)]),
    ("エンディング.m4a", [("IMG_6815_2人歩き手を広げる.MOV", 0.5), ("エンディング.mp4", 0)]),
]

VS = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p"

# ── 1) セグメント組み立て（省メモリ: 1クリップずつ変換→concat。4K HEVC同時デコードはOOMで黙って尺欠けする） ──
import time

def render_take(clip, off, take, pad, out):
    """1クリップを縦1080x1920に変換（尺検証+リトライ付き）"""
    extra = f",tpad=stop_mode=clone:stop_duration={pad:.3f}" if pad > 0.01 else ""
    want = take + pad
    cmd = ["ffmpeg","-y","-threads","2","-ss",f"{off:.3f}","-t",f"{take:.3f}","-i",clip,
           "-vf",VS+extra,"-an"] + X264 + [out]
    for attempt in range(5):
        r = run(cmd)
        if r.returncode == 0 and abs(dur(out) - want) < 0.12:
            return
        print(f"  retry {out} (attempt {attempt+1}): rc={r.returncode}")
        time.sleep(12)
    print("FAIL", out, r.stderr[-500:]); raise SystemExit(1)

parts, seg_durs = [], []
for idx, (audio, clips) in enumerate(SEGS):
    adur = dur(audio)
    seg_durs.append(adur)
    takes, remaining = [], adur
    for i, (clip, off) in enumerate(clips):
        avail = max(0.3, dur(clip) - off - 0.05)
        want = remaining / (len(clips) - i)
        take = min(want, avail)
        takes.append((clip, off, take))
        remaining -= take
    pad = max(0.0, remaining)

    take_files = []
    for i, (clip, off, take) in enumerate(takes):
        tf = f"v2_s{idx}_c{i}.mp4"
        render_take(clip, off, take, pad if i == len(takes)-1 else 0.0, tf)
        take_files.append(tf)
    with open(f"v2_list{idx}.txt","w",encoding="utf-8") as f:
        for p in take_files: f.write(f"file '{p}'\n")
    out = f"v2_seg{idx}.mp4"
    r = run(["ffmpeg","-y","-f","concat","-safe","0","-i",f"v2_list{idx}.txt","-i",audio,
             "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-t",f"{adur:.3f}",out])
    if r.returncode != 0 or abs(dur(out) - adur) > 0.15:
        print("FAIL", out, r.stderr[-500:]); raise SystemExit(1)
    print("ok", out, f"{dur(out):.2f}s / audio {adur:.2f}s")
    parts.append(out)

with open("list_v2.txt","w",encoding="utf-8") as f:
    for p in parts: f.write(f"file '{p}'\n")
run(["ffmpeg","-y","-f","concat","-safe","0","-i","list_v2.txt","-c","copy","_joined_v2.mp4"])

# ── 2) テロップ定義（セグメント内オフセット秒, 行リスト, 行ごとの色） ──
Y = "yellow"; Wh = "white"
TELOPS = {  # seg_idx: [(start, end, [(line, color), ...]), ...]
    1: [(0, 3.0, [("お店12軒に", Wh), ("連絡しました", Wh)]),
        (3.0, 5.0, [("結果から言います", Wh)]),
        (5.0, None, [("全部、断られました", Y)])],
    2: [(0, 3.4, [("間借りのマッチング", Wh), ("サイトも見たんです", Wh)]),
        (3.4, 5.9, [("ネットで探せば", Wh), ("早いと思って", Wh)]),
        (5.9, None, [("条件が合うところが", Wh), ("一件もなかった", Y)])],
    3: [(0, 3.4, [("だから、", Wh), ("足で回るしかなかった", Wh)]),
        (3.4, None, [("リストを持って", Wh), ("一軒ずつ飛び込みました", Wh)])],
    4: [(0, 2.3, [("でもダメでした", Wh)]),
        (2.3, 5.2, [("断られる理由は", Wh), ("だいたい同じでした", Wh)]),
        (5.2, 7.9, [("①そもそも", Wh), ("募集していない", Wh)]),
        (7.9, 10.6, [("②実は昼も", Wh), ("仕込みで使ってる", Wh)]),
        (10.6, None, [("現実は、", Wh), ("甘くなかったです", Wh)])],
    5: [(0, 2.0, [("12軒回って", Wh)]),
        (2.0, 4.9, [("話を聞いてくれた", Wh), ("お店は、ゼロ", Y)]),
        (4.9, None, [("正直、けっこう", Wh), ("心が折れてます", Wh)])],
    6: [(0, 3.6, [("それでも、", Wh), ("あきらめません", Y)])],
}

FONT = "C\\:/Windows/Fonts/HGRPP1.TTC"   # HG創英角ポップ体（1本目のポップ様式に最も近い手持ちフォント）
FS = 80      # フォントサイズ
LH = 102     # 行送り
CY = 1400    # テロップブロックの中心Y（1本目と同じ下1/3）

seg_starts = [sum(seg_durs[:i]) for i in range(len(seg_durs))]
draw, ti = [], 0
for si, cards in TELOPS.items():
    for (s, e, lines) in cards:
        S = seg_starts[si] + s
        E = seg_starts[si] + (e if e is not None else seg_durs[si])
        y0 = CY - len(lines) * LH // 2
        for li, (line, color) in enumerate(lines):
            fn = f"tel_{ti}.txt"; ti += 1
            open(fn, "w", encoding="utf-8").write(line)
            draw.append(
                f"drawtext=textfile={fn}:fontfile='{FONT}':fontsize={FS}:fontcolor={color}:"
                f"borderw=10:bordercolor=black:shadowcolor=black@0.4:shadowx=0:shadowy=5:"
                f"x=(w-text_w)/2:y={y0 + li*LH}:enable='between(t,{S:.3f},{E:.3f})'")

D = dur("_joined_v2.mp4")
vf = ",".join(draw) + f",fade=t=in:st=0:d=0.5,fade=t=out:st={D-0.7:.3f}:d=0.7"

# ── 3) 効果音（絶対時刻に配置） ──
SES = [
    ("SE_whoosh.wav", seg_starts[1], 0.5), ("SE_whoosh.wav", seg_starts[2], 0.5),
    ("SE_whoosh.wav", seg_starts[3], 0.5), ("SE_whoosh.wav", seg_starts[5], 0.45),
    ("SE_don.wav", seg_starts[1] + 5.0, 0.8), ("SE_don.wav", seg_starts[4], 0.8),
    ("SE_don.wav", seg_starts[5] + 2.0, 0.7),
    ("SE_pop.wav", seg_starts[2] + 4.7, 0.5),
    ("SE_sad.wav", seg_starts[4] + 10.6, 0.5),
    ("SE_kiran.wav", seg_starts[6], 0.6),
]
se_inputs, se_filters, se_labels = [], [], []
for i, (f, at, vol) in enumerate(SES):
    se_inputs += ["-i", f]
    ms = int(at * 1000)
    se_filters.append(f"[{i+1}:a]volume={vol},adelay={ms}|{ms}[se{i}]")
    se_labels.append(f"[se{i}]")
af = (";".join(se_filters) + ";[0:a]" + "".join(se_labels) +
      f"amix=inputs={len(SES)+1}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,"
      f"afade=t=in:st=0:d=0.3,afade=t=out:st={D-0.7:.3f}:d=0.7[a]")

FINAL = "間借り編2_v2_完成版.mp4"
r = run(["ffmpeg","-y","-i","_joined_v2.mp4"] + se_inputs +
        ["-filter_complex", af, "-map","0:v","-map","[a]", "-vf", vf] + X264 +
        ["-c:a","aac","-b:a","192k","-t",f"{D:.3f}",FINAL])
if r.returncode != 0:
    print("FAIL master", r.stderr[-800:]); raise SystemExit(1)
print("FINAL", f"{dur(FINAL):.2f}s", round(os.path.getsize(FINAL)/1e6,1), "MB")
