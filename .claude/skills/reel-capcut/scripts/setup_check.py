# -*- coding: utf-8 -*-
"""このPCで動画が作れる状態か、ひと目で分かるようにする。

    python setup_check.py

足りないものは日本語で「何を・どうすればいいか」を出す。
メンバーが最初に動かして、全部 ○ になってから台本の話に進む。
（2026-09-05: 共通素材が無いまま作って、効果音もOPも無い動画が返ってきたのを受けて追加）
"""
import importlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DRIVE = r"G:\マイドライブ\50日企画素材"
COMMON = os.path.join(DRIVE, "_共通素材")
CAPCUT_DRAFTS = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
LOCAL_ASSETS = os.path.expandvars(r"%USERPROFILE%\Videos\リール素材")

SE_FILES = ["ドーン.mp3", "どどん.mp3", "ピアノ、がーん、ショック、落ち込む.mp3",
            "シャキーンとポーズを決めるイメージ.mp3", "シャキーン（ドキュイーン）.mp3"]
OP_ED = ["オープニング.mp4", "エンディング.mp4"]

rows = []


def ok(what, detail=""):
    rows.append(("○", what, detail))


def ng(what, fix):
    rows.append(("×", what, fix))


def warn(what, fix):
    rows.append(("△", what, fix))


def exists_any(name, dirs):
    for d in dirs:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def main():
    # 1. 道具
    v = sys.version_info
    if v >= (3, 10):
        ok("Python %d.%d" % (v.major, v.minor))
    else:
        ng("Python が古い (%d.%d)" % (v.major, v.minor), "python.org から 3.11 以上を入れる（Add to PATH にチェック）")

    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        ok("ffmpeg / ffprobe")
    else:
        ng("ffmpeg が見つからない", "ffmpeg.org（gyan.dev版）を解凍して bin フォルダを PATH に追加")

    for mod, pipname in (("pyJianYingDraft", "pyJianYingDraft"), ("PIL", "pillow")):
        try:
            importlib.import_module(mod)
            ok("python: " + pipname)
        except Exception:
            ng("python: %s が無い" % pipname, "pip install " + pipname)

    # 2. CapCut
    if os.path.isdir(CAPCUT_DRAFTS):
        native = 0
        for n in os.listdir(CAPCUT_DRAFTS):
            p = os.path.join(CAPCUT_DRAFTS, n, "draft_content.json")
            if os.path.exists(p):
                try:
                    import json
                    j = json.load(open(p, encoding="utf-8"))
                    if (j.get("platform") or {}).get("app_source") == "cc":
                        native += 1
                except Exception:
                    pass
        if native:
            ok("CapCut（骨格にできるドラフト %d個）" % native)
        else:
            ng("CapCut にドラフトが1つも無い", "CapCut を開いて新規プロジェクトを1つ作る（中身は何でもいい）")
    else:
        ng("CapCut デスクトップ版が無い", "capcut.com から入れて一度起動する")

    # 3. Drive
    if os.path.isdir(DRIVE):
        ok("Google Drive（G:）")
        if os.path.isdir(os.path.join(DRIVE, "音声素材")):
            ok("音声素材フォルダ")
        else:
            warn("音声素材フォルダが見えない", "Drive の同期が終わるのを待つ。または refarmkobe のアカウントでサインインしているか確認")
    else:
        ng("Google Drive（G:）が見えない",
           "Googleドライブ（パソコン版）を起動。refarmkobe@gmail.com でサインインし、"
           "「50日企画素材」がストリーミングされているか確認")

    # 4. 共通素材（Drive優先、無ければ手元）
    se_dirs = [os.path.join(COMMON, "SE_CapCutライブラリ"), os.path.join(LOCAL_ASSETS, "SE_CapCutライブラリ")]
    miss = [f for f in SE_FILES if not exists_any(f, se_dirs)]
    if not miss:
        ok("効果音 5本")
    else:
        ng("効果音が足りない: " + "、".join(miss),
           "ゆうとに『_共通素材 を Drive に置いて』と頼む（%s）" % os.path.join(COMMON, "SE_CapCutライブラリ"))

    oped_dirs = [os.path.join(COMMON, "OP_ED"), os.path.join(DRIVE, "7 14 素材")]
    miss = [f for f in OP_ED if not exists_any(f, oped_dirs)]
    if not miss:
        ok("オープニング / エンディング")
    else:
        ng("OP/ED が見つからない: " + "、".join(miss),
           "Drive の「7 14 素材」か「_共通素材\\OP_ED」に オープニング.mp4 と エンディング.mp4 が要る")

    font_cache = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Cache\effect"),
                              "7532058832042790161")
    font_dirs = [os.path.join(COMMON, "フォント"), os.path.join(LOCAL_ASSETS, "フォント")]
    if os.path.isdir(font_cache):
        ok("テロップフォント「企業」（CapCutに入っている）")
    elif exists_any("メインテロップ.ttf", font_dirs):
        warn("テロップフォント「企業」がまだCapCutに無い",
             "初回だけ、CapCutでテキストのフォント一覧から「企業」を一度選ぶと落ちてくる。それまでは手元のTTFで代用")
    else:
        ng("テロップフォントが無い", "CapCutでフォント「企業」を一度使う。または _共通素材\\フォント\\メインテロップ.ttf を置く")

    # 5. 生成AI（使う人だけ）
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        ok("APIキー（生成AIを使える）")
    else:
        warn("APIキー未設定", "画像から動画を作る機能を使わないなら不要。使うなら setx GEMINI_API_KEY \"…\"")

    # 表示
    print("")
    print("=== 動画づくりの準備チェック ===")
    for mark, what, detail in rows:
        print(" %s %s" % (mark, what))
        if mark != "○" and detail:
            print("     → " + detail)
    n_ng = sum(1 for r in rows if r[0] == "×")
    n_wn = sum(1 for r in rows if r[0] == "△")
    print("")
    if n_ng == 0:
        print("準備OK。台本を渡してください。" + ("（△は使うときだけ）" if n_wn else ""))
    else:
        print("× が %d個 あります。上の → の通りに直してから、もう一度このチェックを動かしてください。" % n_ng)
        sys.exit(1)


if __name__ == "__main__":
    main()
