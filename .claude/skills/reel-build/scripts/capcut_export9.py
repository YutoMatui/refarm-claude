# -*- coding: utf-8 -*-
"""試作編第1話 をCapCutドラフトとして書き出す（テロップ・効果音トラック付き）

- 映像/ナレーション: build_v2.py と同じタイムライン
- テロップ: 2行構成に対応するため「テロップ上」「テロップ下」の2テキストトラック
  （フォントはCapCut側でユーザーが1本目と同じものに一括変更する前提。位置・色・縁取りは設定済み）
- 効果音: 専用オーディオトラック
- CapCut国際版ネイティブ化（0111骨格グラフト）+ パス正規化込み
"""
import subprocess, json, os, shutil, sys, time

W = os.path.dirname(os.path.abspath(__file__))
os.chdir(W)

ASSETS = r"C:\Users\YutoM\Videos\リール素材\試作編第1話"
CAPCUT_DRAFTS = r"C:\Users\YutoM\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"
DRAFT_NAME = "試作編第1話"
US = 1_000_000

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

def dur(path):
    out = run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",path]).stdout
    return float(json.loads(out)["format"]["duration"])

os.makedirs(ASSETS, exist_ok=True)

SEGS = [
    ("オープニング.m4a", [("オープニング.mp4", 0, None)]),
    ("第3話での.m4a", [("投票お礼_結果前.png", 0, 10.85), ("トマト_リビール.png", 0, None)]),
    ("今日は.m4a", [("PXL_000649_2人エプロン厨房笑顔.mp4", 0.3, 2.6), ("PXL_003349_フライパンでトマト回す長尺.mp4", 6.0, None)]),
    ("もちろん.m4a", [("PXL_003107_鍋にトマト湯むき手元.mp4", 0.2, 2.5), ("PXL_003212_まな板で赤野菜刻む手元.mp4", 0.5, None)]),
    ("味付けは.m4a", [("PXL_012212_鍋_フタ越しの湯気.mp4", 0.6, 3.3), ("PXL_012344_こす_ザルで漉して注ぐ.mp4", 2.0, None)]),
    ("煮込んで.m4a", [("PXL_014600_トマト_ブレンダーで撹拌長尺.mp4", 0.3, 2.4),
                     ("IMG_3480_ミキサーで赤いスープ撹拌長尺.MOV", 3.0, 1.8),
                     ("IMG_3494_こす_ザルで漉してボウルへ.MOV", 1.5, 2.0),
                     ("IMG_3484_鍋にオレンジのスープ完成.MOV", 3.0, None)]),
    ("ん？.m4a", [("IMG_3468_試飲_カップで飲んで微妙な顔.MOV", 5.8, None)]),
    ("正直にいいます.m4a", [("PXL_014600_トマト_ブレンダーで撹拌長尺.mp4", 34.0, 3.1),
                           ("IMG_1787_室内前かがみ落ち込み後ろ姿.MOV", 0.5, 3.5),
                           ("IMG_2886_室内ジャケット正面語り長尺2.MOV", 5.0, None),
                           ("IMG_1523_段差前かがみ落ち込み.MOV", 0.0, 3.0)]),
    ("これどうやったら.m4a", [("IMG_1499_PC腕組み悩む.MOV", 0.8, 2.5),
                             ("IMG_6909_室内エプロン正面手前.MOV", 6.8, 3.22),
                             ("IMG_2881_室内ジャケット正面語り長尺.MOV", 13.7, 1.0)]),
    ("エンディング.m4a", [("IMG_2881_室内ジャケット正面語り長尺.MOV", 14.7, 2.9), ("エンディング.mp4", 0, None)]),
]

SE_LIB = r"C:\Users\YutoM\Videos\リール素材\SE_CapCutライブラリ"
SE_FILES = ["シャキーンとポーズを決めるイメージ.mp3","ピアノ、がーん、ショック、落ち込む.mp3","ドーン.mp3","シャキーン（ドキュイーン）.mp3","SE_ドラムロール.wav"]

# ── 素材コピー ──
names = set(SE_FILES)
for audio, clips in SEGS:
    if audio is not None:
        names.add(audio)
    for c, _, _f in clips:
        names.add(c)
for n in sorted(names):
    dst = os.path.join(ASSETS, n)
    if os.path.exists(dst):
        continue
    if n.lower().endswith(".m4a"):
        # 高域ヒスの除去（S/N +16dB・音声帯域は無傷。実測で確認済み）
        r = run(["ffmpeg","-y","-v","error","-i",n,"-af",
                 "highpass=f=85,afftdn=nr=16:nf=-42,lowpass=f=14000",
                 "-c:a","aac","-b:a","192k","-ar","48000",dst])
        if r.returncode != 0:
            shutil.copy2(n, dst)
            print("denoise失敗のため原音をコピー:", n)
        else:
            print("denoised", n)
        continue
    srcp = os.path.join(SE_LIB, n) if n.lower().endswith(".mp3") else n
    shutil.copy2(srcp, dst)
    print("copied", n)

# ── ドラフト生成 ──
import pyJianYingDraft as d
from pyJianYingDraft import Timerange

folder = d.DraftFolder(CAPCUT_DRAFTS)
script = folder.create_draft(DRAFT_NAME, 1080, 1920, fps=30, allow_replace=True)
tv = script.append_track(d.TrackSpec(d.TrackType.video, "映像"))
ta = script.append_track(d.TrackSpec(d.TrackType.audio, "ナレーション"))
tse = script.append_track(d.TrackSpec(d.TrackType.audio, "効果音"))
tse2 = script.append_track(d.TrackSpec(d.TrackType.audio, "効果音2"))
tx1 = script.append_track(d.TrackSpec(d.TrackType.text, "テロップ上"))
tx2 = script.append_track(d.TrackSpec(d.TrackType.text, "テロップ下"))
tx3 = script.append_track(d.TrackSpec(d.TrackType.text, "テロップ予備1"))
tx4 = script.append_track(d.TrackSpec(d.TrackType.text, "テロップ予備2"))
TEXT_TRACKS = [tx1, tx2, tx3, tx4]
track_end = [0, 0, 0, 0]   # 各テキストトラックの最終終了時刻(µs)

cursor = 0
seg_starts_us = []
for audio, clips in SEGS:
    seg_starts_us.append(cursor)
    if audio is None:
        vmat = d.VideoMaterial(os.path.join(ASSETS, clips[0][0]))
        script.add_segment(d.VideoSegment(vmat, Timerange(cursor, vmat.duration),
                           source_timerange=Timerange(0, vmat.duration), volume=1.0), tv)
        cursor += vmat.duration
        continue
    apath = os.path.join(ASSETS, audio)
    amat = d.AudioMaterial(apath)
    adur_us = amat.duration
    script.add_segment(d.AudioSegment(amat, Timerange(cursor, adur_us)), ta)

    mats = []
    for clip, off, fixed in clips:
        vmat = d.VideoMaterial(os.path.join(ASSETS, clip))
        off_us = round(off * US)
        avail = max(300_000, vmat.duration - off_us - 50_000)
        mats.append((vmat, off_us, avail, fixed))
    fixed_total = sum(round(f * US) for _, _, _, f in mats if f is not None)
    flex_n = sum(1 for m in mats if m[3] is None)
    flex_each = max(300_000, (adur_us - fixed_total) // flex_n) if flex_n else 0
    takes, remaining = [], adur_us
    for vmat, off_us, avail, fixed in mats:
        want = round(fixed * US) if fixed is not None else flex_each
        take = min(want, avail)
        takes.append([vmat, off_us, take, avail])
        remaining -= take
    if remaining > 0:
        vmat, off_us, take, avail = takes[-1]
        add = min(remaining, avail - take)
        takes[-1][2] = take + add
        if remaining - add > 50_000:
            print(f"  警告: {audio} 映像 {(remaining-add)/US:.2f}s 不足")
    elif remaining < 0:
        # 固定尺の合計が音声尺をわずかに超えると次セグメントと重なるため、末尾を刈る
        takes[-1][2] = max(100_000, takes[-1][2] + remaining)
    t = cursor
    for vmat, off_us, take, _ in takes:
        if take <= 0:
            continue
        script.add_segment(d.VideoSegment(vmat, Timerange(t, take),
                           source_timerange=Timerange(off_us, take), volume=0.0), tv)
        t += take
    cursor += adur_us
total_us = cursor
seg_durs_us = [seg_starts_us[i+1]-seg_starts_us[i] for i in range(len(seg_starts_us)-1)] + [total_us-seg_starts_us[-1]]

# ── テロップ（build_v2.pyと同一の割付） ──
Yc = (1.0, 0.84, 0.2); Wc = (1.0, 1.0, 1.0)
# (開始, 終了, [(行, 色)], y中心) ※y中心を省くと既定の1340
# (開始, 終了, [(行, 色)], y中心) ※y中心を省くと既定の1340
TELOPS = {
    0: [(0.35, None, [("16日後に三宮に", Wc)], 231),
        (1.6, None, [("スープ屋を開く大学生", Wc)], 1193)],
    1: [(5.7, 7.2, [("投票ありがとうございます", Wc)]),
        (10.9, None, [("一番多かったのは", Wc), ("赤色のトマト", Yc)])],
    2: [(0, 4.1, [("今日は完熟トマトで", Wc), ("看板になる一杯を", Wc)]),
        (4.1, None, [("作りにいきます", Yc)])],
    3: [(0, 2.9, [("野菜は丸ごと使います", Wc)]),
        (2.9, None, [("捨てるところは", Wc), ("ありません", Yc)])],
    4: [(0, 3.6, [("味つけはなんと", Wc), ("出汁だけです", Yc)]),
        (3.6, None, [("だからこそ、ここは", Wc), ("絶対に手を抜けません", Wc)])],
    5: [(0, 6.2, [("煮込んで、ペーストにして", Wc), ("こして", Wc)]),
        (6.2, None, [("見た目は、いい感じでした", Wc), ("見た目は。", Yc)])],
    6: [],
    7: [(0, 3.1, [("正直に言います", Wc)]),
        (3.1, 6.6, [("思ってたより", Wc), ("うまくできませんでした", Yc)]),
        (6.6, 9.7, [("夏のトマト特有の", Wc), ("青臭さが残ってる", Yc)]),
        (9.7, 12.3, [("出汁の旨味も", Wc), ("消えちゃってる", Wc)]),
        (12.3, None, [("ただ煮ただけじゃ", Wc), ("甘みは出せませんでした", Yc)])],
    8: [(0, 3.9, [("これ、どうやったら", Wc), ("直せると思いますか", Wc)]),
        (3.9, None, [("料理に詳しい方", Wc), ("ぜひ教えてください", Wc)])],
    9: [(0, None, [("次は必ず、成功させます！", Wc)])],
}
# 画面Y=1400中心（下1/3）。transform_yは正=上のため負値。
def ty(y_px):
    return (960 - y_px) / 960

for si, cards in TELOPS.items():
    for card in cards:
        s_, e_, lines = card[0], card[1], card[2]
        yc = card[3] if len(card) > 3 else 1340
        S = seg_starts_us[si] + round(s_ * US)
        E = seg_starts_us[si] + (round(e_ * US) if e_ is not None else seg_durs_us[si])
        n = len(lines)
        for li, (line, color) in enumerate(lines):
            y_px = yc + (li - (n - 1) / 2) * 130
            seg = d.TextSegment(
                line, Timerange(S, E - S),
                style=d.TextStyle(size=13.0, bold=True, color=color, align=1),
                border=d.TextBorder(color=(0.0, 0.0, 0.0)),
                clip_settings=d.ClipSettings(transform_y=ty(y_px)))
            # 上下の行はまず1本目/2本目に置き、埋まっていれば空いているトラックへ逃がす
            pref = li if li < 2 else 0
            ti_ = next((k for k in [pref] + [x for x in range(len(TEXT_TRACKS)) if x != pref]
                        if track_end[k] <= S), None)
            if ti_ is None:
                raise SystemExit(f"テキストトラックが不足: si={si} S={S}")
            script.add_segment(seg, TEXT_TRACKS[ti_])
            track_end[ti_] = E

# ── 効果音（CapCutライブラリの実音源） ──
def sec(x): return round(x * US)
s = seg_starts_us
SES = [
    ("SE_ドラムロール.wav", s[1] + sec(8.6), 0.5),
    ("ピアノ、がーん、ショック、落ち込む.mp3", s[6] + sec(2.1), 0.55),
    ("ドーン.mp3", s[7] + sec(3.1), 0.7),
    ("シャキーンとポーズを決めるイメージ.mp3", s[9], 0.55),
]
SE_TRACKS = [tse, tse2]
se_end = [0, 0]
for f, at, vol in SES:
    amat = d.AudioMaterial(os.path.join(ASSETS, f))
    k = next((i for i in range(len(SE_TRACKS)) if se_end[i] <= at), None)
    if k is None:
        raise SystemExit(f"効果音トラックが不足: {f} @{at}")
    script.add_segment(d.AudioSegment(amat, Timerange(at, amat.duration), volume=vol), SE_TRACKS[k])
    se_end[k] = at + amat.duration

script.save()

# ── パス正規化 + CapCutネイティブ化（骨格=0111） ──
import re
DRAFT_DIR = os.path.join(CAPCUT_DRAFTS, DRAFT_NAME)

def normalize_paths(obj):
    if isinstance(obj, dict):
        return {k: normalize_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_paths(v) for v in obj]
    if isinstance(obj, str) and re.match(r"^[A-Za-z]:\\", obj):
        return obj.replace("\\", "/")
    return obj

content_p = os.path.join(DRAFT_DIR, "draft_content.json")
meta_p = os.path.join(DRAFT_DIR, "draft_meta_info.json")
content = normalize_paths(json.load(open(content_p, encoding="utf-8")))
meta = normalize_paths(json.load(open(meta_p, encoding="utf-8")))

TEMPLATE_P = os.path.join(CAPCUT_DRAFTS, "0111", "draft_content.json")
tpl = json.load(open(TEMPLATE_P, encoding="utf-8"))
native = dict(tpl)
native["id"] = content["id"]
native["duration"] = content["duration"]
native["fps"] = content["fps"]
native["canvas_config"] = {"ratio": "original", "width": 1080, "height": 1920, "background": None}
native["tracks"] = content["tracks"]
native_materials = dict(tpl["materials"])
for k in native_materials:
    native_materials[k] = content["materials"].get(k, [])
# 0111に無い素材キー（texts等）も持ち込む必要がある
for k, v in content["materials"].items():
    if k not in native_materials and v:
        native_materials[k] = v
native["materials"] = native_materials
for k in ["cover", "static_cover_image_path", "retouch_cover", "path", "name", "create_time", "update_time"]:
    if k in content:
        native[k] = content[k]
content = native

meta["tm_duration"] = content.get("duration", 0)
meta["draft_name"] = DRAFT_NAME
meta["draft_root_path"] = CAPCUT_DRAFTS.replace("\\", "/")
meta["draft_fold_path"] = meta["draft_root_path"] + "/" + DRAFT_NAME
json.dump(content, open(content_p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump(meta, open(meta_p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("DRAFT SAVED:", DRAFT_DIR)
print("total", f"{total_us/US:.2f}s")
