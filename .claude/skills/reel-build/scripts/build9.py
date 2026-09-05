# -*- coding: utf-8 -*-
"""試作編第1話 v2（2026-08-05 ゆうと指摘を全面反映）

修正点:
- フォント: 日本語パスだとffmpegが読めず標準ゴシックに化けていた → ASCIIパス(corp.ttf)へコピーして使用
- OP: 1本目（５０日企画　１）と同じテロップ様式（上段y231/下段y1193/約105px・白字黒縁）
- 投票: 結果を先に見せない。お礼画面 → タメでドラムロール → トマト写真をバンッ（語り素材は使わない）
- 素材: 7/5試作の2フォルダをメインに。とうもろこしがトマトの語りに映らないよう全面差し替え
- こして: PXL_005221_ボウルにスープ漉す完成 を使用
- ネガティブ: 汎用素材の落ち込みカット（段差でうつむく）を使用
"""
import subprocess, json, os, time

W = os.path.dirname(os.path.abspath(__file__))
os.chdir(W)
FONT = os.path.abspath("corp.ttf").replace("\\", "/").replace(":", r"\:")
SE = r"C:\Users\YutoM\Videos\リール素材\SE_CapCutライブラリ"

def run(c): return subprocess.run(c, capture_output=True, text=True, encoding="utf-8", errors="replace")
def dur(p):
    return float(json.loads(run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",p]).stdout)["format"]["duration"])

DENOISE = "highpass=f=85,afftdn=nr=16:nf=-42,lowpass=f=14000"
X264 = ["-c:v","libx264","-preset","veryfast","-crf","18",
        "-x264-params","threads=2:lookahead-threads=1:rc-lookahead=10"]
VS = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p"
CLIP_VS = {
    # 手前の鍋にとうもろこしが写り込むため、完熟トマトだけが映るよう寄せる
    "PXL_003107_鍋にトマト湯むき手元.mp4":
        "scale=1728:3072,crop=1080:1920:324:0,fps=30,setsar=1,format=yuv420p",
}

SEGS = [
    ("オープニング.m4a", [("オープニング.mp4", 0, None)]),
    ("第3話での.m4a", [("投票お礼_結果前.png", 0, 10.85), ("トマト_リビール.png", 0, None)]),
    ("今日は.m4a", [("PXL_000649_2人エプロン厨房笑顔.mp4", 0.3, 2.6), ("PXL_003349_フライパンでトマト回す長尺.mp4", 6.0, None)]),
    ("もちろん.m4a", [("PXL_003107_鍋にトマト湯むき手元.mp4", 0.2, 2.5), ("PXL_003212_まな板で赤野菜刻む手元.mp4", 0.5, None)]),
    # 出汁：昆布かつおの琥珀色を漉す実カット（コーンは使わない）
    ("味付けは.m4a", [("PXL_012212_鍋_フタ越しの湯気.mp4", 0.6, 3.3), ("PXL_012344_こす_ザルで漉して注ぐ.mp4", 2.0, None)]),
    # 煮込んで＝鍋にローストしたトマト／ペーストにして・こして＝赤いスープをミキサーへ
    # 煮込む→ペースト→こす→完成品、と台詞どおりに進む（こす・完成品は8/9追加の新素材）
    ("煮込んで.m4a", [("PXL_014600_トマト_ブレンダーで撹拌長尺.mp4", 0.3, 2.4),
                     ("IMG_3480_ミキサーで赤いスープ撹拌長尺.MOV", 3.0, 1.8),
                     ("IMG_3494_こす_ザルで漉してボウルへ.MOV", 1.5, 2.0),
                     ("IMG_3484_鍋にオレンジのスープ完成.MOV", 3.0, None)]),
    # 一口飲んで表情が変わる新素材（カップなので他の器が写り込まない）
    ("ん？.m4a", [("IMG_3468_試飲_カップで飲んで微妙な顔.MOV", 5.8, None)]),
    # 音声の区切り実測: 正直に言います(〜3.1) / うまくできなかった(〜6.6) / 青臭さ・旨味(〜12.3) / 甘みは出せず(〜17.1)
    # 甘みは出せませんでした＝IMG_1523の冒頭3秒（最も落ち込んで見える）。手前の落胆はIMG_1522に振り分け
    ("正直にいいます.m4a", [("PXL_014600_トマト_ブレンダーで撹拌長尺.mp4", 34.0, 3.1),
                           ("IMG_1787_室内前かがみ落ち込み後ろ姿.MOV", 0.5, 3.5),
                           ("IMG_2886_室内ジャケット正面語り長尺2.MOV", 5.0, None),
                           ("IMG_1523_段差前かがみ落ち込み.MOV", 0.0, 3.0)]),
    # 「教えてください」は両手を差し出す→手を組むカット
    # 「ぜひ教えてください」(≈5.1s)に手を差し出す動作(素材8.0-8.9s)が重なるよう逆算
    ("これどうやったら.m4a", [("IMG_1499_PC腕組み悩む.MOV", 0.8, 2.5),
                             ("IMG_6909_室内エプロン正面手前.MOV", 6.8, 3.22),
                             ("IMG_2881_室内ジャケット正面語り長尺.MOV", 13.7, 1.0)]),
    # ガッツポーズ素材は1秒前（前セグメント末尾）から連続で入り、CTAの言葉に動作が重なる
    ("エンディング.m4a", [("IMG_2881_室内ジャケット正面語り長尺.MOV", 14.7, 2.9), ("エンディング.mp4", 0, None)]),
]

TRANS = {0:(None,"white"), 1:("white","white"), 2:("white","white"), 3:("white","white"),
         4:("white","white"), 5:("white","black"), 6:("black","black"), 7:("black","black"),
         8:("black","white"), 9:("white",None)}
HEAD_D, TAIL_D = 0.15, 0.10

def render_take(clip, off, take, pad, out):
    vs = CLIP_VS.get(clip, VS)
    want = take + pad
    if clip.lower().endswith(".png"):
        cmd = ["ffmpeg","-y","-loop","1","-t",f"{want:.3f}","-i",clip,"-vf",vs,"-an"] + X264 + [out]
    else:
        extra = f",tpad=stop_mode=clone:stop_duration={pad:.3f}" if pad > 0.01 else ""
        cmd = ["ffmpeg","-y","-threads","2","-ss",f"{off:.3f}","-t",f"{take:.3f}","-i",clip,
               "-vf",vs+extra,"-an"] + X264 + [out]
    for a in range(5):
        r = run(cmd)
        if r.returncode == 0 and abs(dur(out)-want) < 0.15: return
        print(f"  retry {out} ({a+1}) rc={r.returncode}"); time.sleep(10)
    print("FAIL", out, r.stderr[-500:]); raise SystemExit(1)

parts, seg_durs = [], []
for idx,(audio, clips) in enumerate(SEGS):
    adur = dur(audio); seg_durs.append(adur)
    fixed = sum(f for _,_,f in clips if f is not None)
    flexn = sum(1 for _,_,f in clips if f is None)
    flex = max(0.3,(adur-fixed)/flexn) if flexn else 0
    takes, rem = [], adur
    for clip, off, fx in clips:
        avail = 9999 if clip.lower().endswith(".png") else max(0.3, dur(clip)-off-0.05)
        take = min(fx if fx is not None else flex, avail)
        takes.append((clip,off,take)); rem -= take
    pad = max(0.0, rem)
    tfs=[]
    for i,(clip,off,take) in enumerate(takes):
        tf=f"b{idx}_{i}.mp4"; render_take(clip,off,take, pad if i==len(takes)-1 else 0.0, tf); tfs.append(tf)
    with open(f"L{idx}.txt","w",encoding="utf-8") as f:
        for p in tfs: f.write(f"file '{p}'\n")
    raw=f"R{idx}.mp4"
    r = run(["ffmpeg","-y","-f","concat","-safe","0","-i",f"L{idx}.txt","-i",audio,
             "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-t",f"{adur:.3f}",raw])
    if r.returncode != 0 or abs(dur(raw)-adur) > 0.2:
        print("FAIL",raw,r.stderr[-500:]); raise SystemExit(1)
    head,tail = TRANS[idx]; fades=[]
    if head: fades.append(f"fade=t=in:st=0:d={HEAD_D}:color={head}")
    if tail: fades.append(f"fade=t=out:st={adur-TAIL_D:.3f}:d={TAIL_D}:color={tail}")
    out=f"S{idx}.mp4"
    if fades:
        for a in range(4):
            r = run(["ffmpeg","-y","-i",raw,"-vf",",".join(fades)] + X264 + ["-c:a","copy",out])
            if r.returncode==0 and abs(dur(out)-adur)<0.2: break
            time.sleep(10)
        else: print("FAIL fade",out); raise SystemExit(1)
    else: os.replace(raw,out)
    print("ok",out,f"{dur(out):.2f}s / audio {adur:.2f}s"); parts.append(out)

with open("LA.txt","w",encoding="utf-8") as f:
    for p in parts: f.write(f"file '{p}'\n")
run(["ffmpeg","-y","-f","concat","-safe","0","-i","LA.txt","-c","copy","_j.mp4"])

# ── テロップ ──
Y="0xFFD633"; Wh="white"
# 通常テロップ（下1/3・fontsize100・行送り130）
TELOPS = {
    1: [(5.7, 7.2, [("投票ありがとうございます", Wh)]),
        (10.9, None, [("一番多かったのは", Wh), ("赤色のトマト", Y)])],
    2: [(0, 4.1, [("今日は完熟トマトで", Wh), ("看板になる一杯を", Wh)]),
        (4.1, None, [("作りにいきます", Y)])],
    3: [(0, 2.9, [("野菜は丸ごと使います", Wh)]),
        (2.9, None, [("捨てるところは", Wh), ("ありません", Y)])],
    4: [(0, 3.6, [("味つけはなんと", Wh), ("出汁だけです", Y)]),
        (3.6, None, [("だからこそ、ここは", Wh), ("絶対に手を抜けません", Wh)])],
    5: [(0, 6.2, [("煮込んで、ペーストにして", Wh), ("こして", Wh)]),
        (6.2, None, [("見た目は、いい感じでした", Wh), ("見た目は。", Y)])],
    6: [],
    7: [(0, 3.1, [("正直に言います", Wh)]),
        (3.1, 6.6, [("思ってたより", Wh), ("うまくできませんでした", Y)]),
        (6.6, 9.7, [("夏のトマト特有の", Wh), ("青臭さが残ってる", Y)]),
        (9.7, 12.3, [("出汁の旨味も", Wh), ("消えちゃってる", Wh)]),
        (12.3, None, [("ただ煮ただけじゃ", Wh), ("甘みは出せませんでした", Y)])],
    8: [(0, 3.9, [("これ、どうやったら", Wh), ("直せると思いますか", Wh)]),
        (3.9, None, [("料理に詳しい方", Wh), ("ぜひ教えてください", Wh)])],
    9: [(0, None, [("次は必ず、成功させます！", Wh)])],
}
FS, LH, CY = 100, 130, 1340
seg_starts = [sum(seg_durs[:i]) for i in range(len(seg_durs))]
draw, ti = [], 0
def dt(text, color, fs, ycenter, S, E):
    global ti
    fn=f"x{ti}.txt"; ti+=1
    open(fn,"w",encoding="utf-8").write(text)
    return (f"drawtext=textfile={fn}:fontfile='{FONT}':fontsize={fs}:fontcolor={color}:"
            f"borderw=12:bordercolor=black:shadowcolor=black@0.35:shadowx=0:shadowy=6:"
            f"x=(w-text_w)/2:y={ycenter-fs//2}:enable='between(t,{S:.3f},{E:.3f})'")

# OPは1本目と同じ様式（上段y231・下段y1193・fontsize105）
op_e = seg_durs[0]
draw.append(dt("16日後に三宮に", Wh, 105, 231, 0.35, op_e))
draw.append(dt("スープ屋を開く大学生", Wh, 105, 1193, 1.6, op_e))

for si, cards in TELOPS.items():
    for (s,e,lines) in cards:
        S = seg_starts[si]+s
        E = seg_starts[si]+(e if e is not None else seg_durs[si])
        y0 = CY-(len(lines)-1)*LH//2
        for li,(line,color) in enumerate(lines):
            draw.append(dt(line, color, FS, y0+li*LH, S, E))

D = dur("_j.mp4")
vf = ",".join(draw) + f",fade=t=in:st=0:d=0.4,fade=t=out:st={D-0.7:.3f}:d=0.7"

# ── SE ──
s = seg_starts
SES = [
    ("SE_ドラムロール.wav",                                s[1]+8.6, 0.5),
    (os.path.join(SE,"ピアノ、がーん、ショック、落ち込む.mp3"), s[6]+2.1, 0.55),
    (os.path.join(SE,"ドーン.mp3"),                         s[7]+3.1, 0.7),
    (os.path.join(SE,"シャキーンとポーズを決めるイメージ.mp3"), s[9],    0.55),
]
se_in, se_f, se_l = [], [], []
for i,(f,at,vol) in enumerate(SES):
    se_in += ["-i", f]; ms=int(at*1000)
    se_f.append(f"[{i+1}:a]volume={vol},adelay={ms}|{ms}[se{i}]"); se_l.append(f"[se{i}]")
af = (";".join(se_f) + ";[0:a]" + "".join(se_l) +
      f"amix=inputs={len(SES)+1}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,"
      f"afade=t=in:st=0:d=0.2,afade=t=out:st={D-0.7:.3f}:d=0.7[a]")

FINAL="試作編第1話_完成版.mp4"
for a in range(4):
    r = run(["ffmpeg","-y","-i","_j.mp4"]+se_in+["-filter_complex",af,"-map","0:v","-map","[a]","-vf",vf]+X264+
            ["-c:a","aac","-b:a","192k","-t",f"{D:.3f}",FINAL])
    if r.returncode==0 and abs(dur(FINAL)-D)<0.25: break
    print("retry master",a+1); time.sleep(12)
else:
    print("FAIL master", r.stderr[-800:]); raise SystemExit(1)
print("FINAL", f"{dur(FINAL):.2f}s", round(os.path.getsize(FINAL)/1e6,1),"MB")
