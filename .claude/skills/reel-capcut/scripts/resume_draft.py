# -*- coding: utf-8 -*-
"""別のPCで、同じ plan.json から CapCut ドラフトを作り直す（＝編集を再開する）。

  python resume_draft.py video/imo_reel/plan.json

やること：
  1. plan の "drive_clips"（Drive のフォルダ）から、足りない背景動画を plan と同じ場所の clips/ にコピーする
  2. make_draft.py を実行して、このPCの CapCut にドラフトを作る
CapCut の共有スペースが使えないときの代わり。背景動画はリポジトリに入れない（大きい）ので Drive 経由。
前提：CapCut をインストールして一度起動しておく（新規プロジェクトを1つ作っておくと確実）／ffmpeg／pip install pyJianYingDraft pillow numpy
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(plan_path):
    plan_path = os.path.abspath(plan_path)
    plan = json.load(open(plan_path, encoding="utf-8"))
    base = os.path.dirname(plan_path)
    clips = os.path.join(base, "clips"); os.makedirs(clips, exist_ok=True)
    drive = plan.get("drive_clips", "")
    need = []
    for seg in plan.get("segments", []):
        for c in seg.get("clips", []):
            need.append(c["file"])
    for s in plan.get("se", []):
        pass  # 効果音は Drive の _共通素材 から make_draft が探す
    missing = [f for f in need if not os.path.exists(os.path.join(clips, f))]
    if missing:
        if not drive or not os.path.isdir(drive):
            print("背景動画が %d 本足りません: %s" % (len(missing), ", ".join(missing)))
            print("Drive のフォルダが見つかりません: %s" % (drive or "（plan に drive_clips がありません）"))
            print("  Google ドライブ（G:）が起動しているか確認してください。")
            sys.exit(1)
        for f in missing:
            src = os.path.join(drive, f)
            if not os.path.exists(src):
                print("Drive にもありません: %s" % src); sys.exit(1)
            shutil.copy2(src, os.path.join(clips, f)); print("コピー: %s" % f)
    else:
        print("背景動画はそろっています（%d 本）" % len(need))
    r = subprocess.run([sys.executable, os.path.join(HERE, "make_draft.py"), plan_path])
    sys.exit(r.returncode)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python resume_draft.py plan.json"); sys.exit(1)
    main(sys.argv[1])
