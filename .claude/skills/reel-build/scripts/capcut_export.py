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
    ("第3話での.m4a",   [("投票結果_赤11黄7緑3.png", 0, 6.4), ("IMG_2884_室内ジャケット正面真剣.MOV", 1.0, None)]),
    ("今日は.m4a",      [("PXL_002829_厨房_シンクで下準備長尺.mp4", 0.3, 2.8), ("PXL_003107_鍋にトマト湯むき手元.mp4", 0.2, None)]),
    ("もちろん.m4a",    [("PXL_002948_トマト枝豆ザル手元短尺.mp4", 0.1, 1.9), ("PXL_003212_まな板で赤野菜刻む手元.mp4", 0.5, None)]),
    ("味付けは.m4a",    [("PXL_012212_鍋_フタ越しの湯気.mp4", 0.5, 3.2), ("PXL_012344_こす_ザルで漉して注ぐ.mp4", 1.5, None)]),
    ("煮込んで.m4a",    [("PXL_014129_トマト_天板でロースト.mp4", 1.0, 2.8), ("PXL_014600_トマト_ブレンダーで撹拌長尺.mp4", 26.0, 3.0), ("PXL_012344_こす_ザルで漉して注ぐ.mp4", 7.0, None)]),
    ("ん？.m4a",        [("PXL_015207_試食_カップで試飲長尺.mp4", 8.2, None)]),
    ("正直にいいます.m4a", [("PXL_014600_トマト_ブレンダーで撹拌長尺.mp4", 34.0, 4.2), ("IMG_3478_ボウルでスープ混ぜる.MOV", 13.0, 4.0), ("IMG_2886_室内ジャケット正面語り長尺2.MOV", 5.0, None)]),
    ("これどうやったら.m4a", [("IMG_2882_室内ジャケット正面語り.MOV", 2.0, None)]),
    ("黄色を選んで.m4a",  [("IMG_2883_室内ジャケット手広げ説明.MOV", 0.5, None)]),
    ("エンディング.m4a",  [("エンディング.mp4", 0, None)]),
]

SE_LIB = r"C:\Users\YutoM\Videos\リール素材\SE_CapCutライブラリ"
SE_FILES = ["シャキーンとポーズを決めるイメージ.mp3","ピアノ、がーん、ショック、落ち込む.mp3","ドーン.mp3","シャキーン（ドキュイーン）.mp3"]

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
tx1 = script.append_track(d.TrackSpec(d.TrackType.text, "テロップ上"))
tx2 = script.append_track(d.TrackSpec(d.TrackType.text, "テロップ下"))

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
TELOPS = {
    0: [(0, None, [("あと16日", Yc)])],
    1: [(6.7, None, [("一番多かったのは", Wc), ("赤色のトマト", Yc)])],
    2: [(0, None, [("今日は完熟トマトで", Wc), ("看板になる一杯を", Wc)])],
    3: [(0, 2.9, [("野菜は丸ごと使います", Wc)]),
        (2.9, None, [("捨てるところは", Wc), ("ありません", Yc)])],
    4: [(0, 3.6, [("味つけはなんと", Wc), ("出汁だけです", Yc)]),
        (3.6, None, [("だからこそ、ここは", Wc), ("絶対に手を抜けません", Wc)])],
    5: [(0, 4.2, [("煮込んで、ペーストにして", Wc), ("こして", Wc)]),
        (4.2, None, [("見た目は、いい感じでした", Wc), ("見た目は。", Yc)])],
    6: [],
    7: [(0, 3.6, [("正直に言います", Wc)]),
        (3.6, 7.6, [("思ってたより", Wc), ("うまくできませんでした", Yc)]),
        (7.6, 12.4, [("夏のトマト特有の", Wc), ("青臭さが残ってる", Yc)]),
        (12.4, None, [("出汁の旨味も", Wc), ("消えちゃってる", Wc)])],
    8: [(0, 3.4, [("これ、どうやったら", Wc), ("直せると思いますか", Wc)]),
        (3.4, None, [("料理に詳しい方", Wc), ("ぜひ教えてください", Wc)])],
    9: [(0, 2.5, [("黄色を選んでくれた方は", Wc), ("次の動画でやります", Wc)]),
        (2.5, None, [("次は、黄色", Yc)])],
    10: [(0, None, [("次は必ず、成功させます！", Wc)])],
}
# 画面Y=1400中心（下1/3）。transform_yは正=上のため負値。
def ty(y_px):
    return (960 - y_px) / 960

for si, cards in TELOPS.items():
    for (s, e, lines) in cards:
        S = seg_starts_us[si] + round(s * US)
        E = seg_starts_us[si] + (round(e * US) if e is not None else seg_durs_us[si])
        n = len(lines)
        for li, (line, color) in enumerate(lines):
            y_px = 1340 + (li - (n - 1) / 2) * 130
            seg = d.TextSegment(
                line, Timerange(S, E - S),
                style=d.TextStyle(size=13.0, bold=True, color=color, align=1),
                border=d.TextBorder(color=(0.0, 0.0, 0.0)),
                clip_settings=d.ClipSettings(transform_y=ty(y_px)))
            script.add_segment(seg, tx1 if li == 0 else tx2)

# ── 効果音（CapCutライブラリの実音源） ──
def sec(x): return round(x * US)
s = seg_starts_us
SES = [
    ("シャキーンとポーズを決めるイメージ.mp3", s[1] + sec(7.2), 0.5),
    ("ピアノ、がーん、ショック、落ち込む.mp3", s[6] + sec(0.9), 0.55),
    ("ドーン.mp3", s[7] + sec(3.6), 0.7),
    ("シャキーン（ドキュイーン）.mp3", s[9] + sec(2.5), 0.5),
    ("シャキーンとポーズを決めるイメージ.mp3", s[10], 0.55),
]
for f, at, vol in SES:
    amat = d.AudioMaterial(os.path.join(ASSETS, f))
    script.add_segment(d.AudioSegment(amat, Timerange(at, amat.duration), volume=vol), tse)

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
