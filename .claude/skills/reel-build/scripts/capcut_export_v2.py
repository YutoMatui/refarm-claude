# -*- coding: utf-8 -*-
"""間借り編2 v2 をCapCutドラフトとして書き出す（テロップ・効果音トラック付き）

- 映像/ナレーション: build_v2.py と同じタイムライン
- テロップ: 2行構成に対応するため「テロップ上」「テロップ下」の2テキストトラック
  （フォントはCapCut側でユーザーが1本目と同じものに一括変更する前提。位置・色・縁取りは設定済み）
- 効果音: 専用オーディオトラック
- CapCut国際版ネイティブ化（0111骨格グラフト）+ パス正規化込み
"""
import subprocess, json, os, shutil, sys, time

W = os.path.dirname(os.path.abspath(__file__))
os.chdir(W)

ASSETS = r"C:\Users\YutoM\Videos\リール素材\間借り編2"
CAPCUT_DRAFTS = r"C:\Users\YutoM\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"
DRAFT_NAME = "間借り編2_v2"
US = 1_000_000

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

def dur(path):
    out = run(["ffprobe","-v","error","-show_entries","format=duration","-of","json",path]).stdout
    return float(json.loads(out)["format"]["duration"])

os.makedirs(ASSETS, exist_ok=True)

SEGS = [
    ("オープニング.m4a", [("オープニング.mp4", 0)]),
    ("お店12件.m4a", [("IMG_2884_室内ジャケット正面真剣.MOV", 1.0), ("IMG_1526_芝生しゃがみ観察.MOV", 0.1)]),
    ("ネットで探せば.m4a", [("IMG_1500_PCうつむき没頭.MOV", 0.5), ("シェアレストラン_モザイク.mp4", 0.3)]),
    ("だから足で回る.m4a", [("IMG_6813_横断歩道振り返り.MOV", 1.0), ("IMG_6816_2人指さし商店街.MOV", 0.2)]),
    ("でもダメでした.m4a", [("IMG_1523_段差前かがみ落ち込み.MOV", 0.2), ("IMG_2886_室内ジャケット正面語り長尺2.MOV", 5.0)]),
    ("心折れてる.m4a", [("IMG_6814_2人歩く後ろ姿長尺.MOV", 3.0), ("IMG_6821_2人街角立ち止まり.MOV", 1.0)]),
    ("エンディング.m4a", [("IMG_6815_2人歩き手を広げる.MOV", 0.5), ("エンディング.mp4", 0)]),
]

SE_FILES = ["SE_don.wav","SE_whoosh.wav","SE_pop.wav","SE_kiran.wav","SE_sad.wav"]

# ── 素材コピー ──
names = set(SE_FILES)
for audio, clips in SEGS:
    names.add(audio)
    for c, _ in clips:
        names.add(c)
for n in sorted(names):
    dst = os.path.join(ASSETS, n)
    if not os.path.exists(dst):
        shutil.copy2(n, dst)
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
    apath = os.path.join(ASSETS, audio)
    amat = d.AudioMaterial(apath)
    adur_us = amat.duration
    script.add_segment(d.AudioSegment(amat, Timerange(cursor, adur_us)), ta)

    mats = []
    for clip, off in clips:
        vmat = d.VideoMaterial(os.path.join(ASSETS, clip))
        off_us = round(off * US)
        avail = max(300_000, vmat.duration - off_us - 50_000)
        mats.append((vmat, off_us, avail))
    takes, remaining = [], adur_us
    for i, (vmat, off_us, avail) in enumerate(mats):
        want = remaining // (len(mats) - i)
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
    1: [(0, 3.0, [("お店12軒に", Wc), ("連絡しました", Wc)]),
        (3.0, 5.0, [("結果から言います", Wc)]),
        (5.0, None, [("全部、断られました", Yc)])],
    2: [(0, 3.4, [("間借りのマッチング", Wc), ("サイトも見たんです", Wc)]),
        (3.4, 5.9, [("ネットで探せば", Wc), ("早いと思って", Wc)]),
        (5.9, None, [("条件が合うところが", Wc), ("一件もなかった", Yc)])],
    3: [(0, 3.4, [("だから、", Wc), ("足で回るしかなかった", Wc)]),
        (3.4, None, [("リストを持って", Wc), ("一軒ずつ飛び込みました", Wc)])],
    4: [(0, 2.3, [("でもダメでした", Wc)]),
        (2.3, 5.2, [("断られる理由は", Wc), ("だいたい同じでした", Wc)]),
        (5.2, 7.9, [("①そもそも", Wc), ("募集していない", Wc)]),
        (7.9, 10.6, [("②実は昼も", Wc), ("仕込みで使ってる", Wc)]),
        (10.6, None, [("現実は、", Wc), ("甘くなかったです", Wc)])],
    5: [(0, 2.0, [("12軒回って", Wc)]),
        (2.0, 4.9, [("話を聞いてくれた", Wc), ("お店は、ゼロ", Yc)]),
        (4.9, None, [("正直、けっこう", Wc), ("心が折れてます", Wc)])],
    6: [(0, 3.6, [("それでも、", Wc), ("あきらめません", Yc)])],
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
            y_px = 1400 + (li - (n - 1) / 2) * 102
            seg = d.TextSegment(
                line, Timerange(S, E - S),
                style=d.TextStyle(size=11.0, bold=True, color=color, align=1),
                border=d.TextBorder(color=(0.0, 0.0, 0.0)),
                clip_settings=d.ClipSettings(transform_y=ty(y_px)))
            script.add_segment(seg, tx1 if li == 0 else tx2)

# ── 効果音 ──
def sec(x): return round(x * US)
SES = [
    ("SE_whoosh.wav", seg_starts_us[1], 0.5), ("SE_whoosh.wav", seg_starts_us[2], 0.5),
    ("SE_whoosh.wav", seg_starts_us[3], 0.5), ("SE_whoosh.wav", seg_starts_us[5], 0.45),
    ("SE_don.wav", seg_starts_us[1] + sec(5.0), 0.8), ("SE_don.wav", seg_starts_us[4], 0.8),
    ("SE_don.wav", seg_starts_us[5] + sec(2.0), 0.7),
    ("SE_pop.wav", seg_starts_us[2] + sec(4.7), 0.5),
    ("SE_sad.wav", seg_starts_us[4] + sec(10.6), 0.5),
    ("SE_kiran.wav", seg_starts_us[6], 0.6),
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
