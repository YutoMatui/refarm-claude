# -*- coding: utf-8 -*-
"""Drive の撮影素材とナレーション音声をひとつの索引にまとめる。

Drive を毎回歩くと遅い（G:はネットワーク越し）ので、一度だけ歩いて JSON に落とす。
台本の「画・素材」欄のことばで検索して、使えそうなクリップを引くために使う。

    python scan_assets.py                    … 索引を作り直す
    python scan_assets.py 落ち込み 語り        … 索引からことばで探す
"""
import json
import os
import subprocess
import sys

ROOTS = [
    r"G:\マイドライブ\50日企画素材",
    r"G:\マイドライブ\スープ素材",
]
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_asset_index.json")

VIDEO = (".mp4", ".mov", ".m4v", ".avi")
AUDIO = (".m4a", ".mp3", ".wav")
IMAGE = (".png", ".jpg", ".jpeg", ".webp")
SKIP_DIR = {"完成動画", ".tmp.drivedownload"}


def dur(path):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "json", path],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        return round(float(json.loads(r.stdout)["format"]["duration"]), 2)
    except Exception:
        return None


def build():
    roots = [r for r in ROOTS if os.path.isdir(r)]
    if not roots:
        print("エラー: Google Drive が見つかりません。")
        print("  Googleドライブ（パソコン版）を起動して、G:ドライブが開けるか確認してください。")
        sys.exit(1)

    items = []
    for root in roots:
        for dirpath, dirnames, files in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
            for f in files:
                low = f.lower()
                if low.startswith(("desktop.ini", "~$", ".")):
                    continue
                kind = ("video" if low.endswith(VIDEO) else
                        "audio" if low.endswith(AUDIO) else
                        "image" if low.endswith(IMAGE) else None)
                if kind is None:
                    continue
                p = os.path.join(dirpath, f)
                items.append({"name": f, "kind": kind, "dir": dirpath,
                              "folder": os.path.basename(dirpath),
                              "rel": os.path.relpath(p, root)})
    # 尺は動画と音声だけ、しかも時間がかかるので後から必要なぶんだけ入れる
    json.dump({"roots": roots, "items": items},
              open(INDEX, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = {}
    for i in items:
        n[i["kind"]] = n.get(i["kind"], 0) + 1
    print("索引を作りました: %s" % INDEX)
    print("  動画 %d / 音声 %d / 画像 %d" % (n.get("video", 0), n.get("audio", 0), n.get("image", 0)))


def search(words):
    if not os.path.exists(INDEX):
        build()
    data = json.load(open(INDEX, encoding="utf-8"))
    hits = []
    for i in data["items"]:
        hay = i["rel"]
        score = sum(1 for w in words if w in hay)
        if score:
            hits.append((score, i))
    hits.sort(key=lambda x: (-x[0], x[1]["rel"]))
    if not hits:
        print("見つかりませんでした: %s" % " ".join(words))
        print("ヒント: 素材のファイル名が IMG_1234.MOV のままだと中身で探せません。")
        print("        中身を見て IMG_1234_内容.MOV にリネームしてから索引を作り直してください。")
        return
    for score, i in hits[:40]:
        d = dur(os.path.join(i["dir"], i["name"])) if i["kind"] != "image" else None
        print("%-6s %-7s %s" % (i["kind"], ("%.1fs" % d) if d else "-", i["rel"]))
    if len(hits) > 40:
        print("... ほか %d件" % (len(hits) - 40))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        search(sys.argv[1:])
    else:
        build()
