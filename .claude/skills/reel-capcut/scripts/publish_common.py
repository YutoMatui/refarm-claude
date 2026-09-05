# -*- coding: utf-8 -*-
"""共通素材（効果音・OP/ED・フォント）を Drive の _共通素材 に置く。ゆうとのPCで1回だけ動かす。

メンバーのPCには効果音もOPも無いので、Driveに置かないと「別の質感の動画」になる。
このスクリプトは、このPCにある実体を Drive にコピーするだけ。すでにあるものは触らない。

    python publish_common.py
"""
import os
import shutil
import sys

DRIVE = r"G:\マイドライブ\50日企画素材"
COMMON = os.path.join(DRIVE, "_共通素材")
LOCAL = os.path.expandvars(r"%USERPROFILE%\Videos\リール素材")

PLAN = [
    # (Drive側フォルダ, 探すファイル名, このPCで探す場所の候補)
    ("SE_CapCutライブラリ", ["ドーン.mp3", "どどん.mp3", "ピアノ、がーん、ショック、落ち込む.mp3",
                           "シャキーンとポーズを決めるイメージ.mp3", "シャキーン（ドキュイーン）.mp3"],
     [os.path.join(LOCAL, "SE_CapCutライブラリ")]),
    ("OP_ED", ["オープニング.mp4", "エンディング.mp4"],
     [os.path.join(DRIVE, "7 14 素材"), os.path.join(LOCAL, "試作編第1話"), os.path.join(LOCAL, "間借り編2")]),
    ("フォント", ["メインテロップ.ttf", "紫アクセント.otf"],
     [os.path.join(LOCAL, "フォント")]),
]


def main():
    if not os.path.isdir(DRIVE):
        print("Google Drive（G:）が見えません。Googleドライブを起動してから、もう一度。")
        sys.exit(1)
    copied, skipped, missing = 0, 0, []
    for sub, names, cands in PLAN:
        dst_dir = os.path.join(COMMON, sub)
        os.makedirs(dst_dir, exist_ok=True)
        for n in names:
            dst = os.path.join(dst_dir, n)
            if os.path.exists(dst):
                skipped += 1
                continue
            src = next((os.path.join(c, n) for c in cands if os.path.exists(os.path.join(c, n))), None)
            if src is None:
                missing.append("%s\\%s" % (sub, n))
                continue
            shutil.copy2(src, dst)
            copied += 1
            print("  置いた: %s\\%s" % (sub, n))
    print("")
    print("コピー %d / すでにあった %d" % (copied, skipped))
    if missing:
        print("見つからなかった:")
        for m in missing:
            print("  " + m)
        sys.exit(1)
    print("完了: " + COMMON)


if __name__ == "__main__":
    main()
