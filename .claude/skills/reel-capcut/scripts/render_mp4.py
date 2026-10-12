# -*- coding: utf-8 -*-
"""plan.json から完成 mp4 を焼き出す（CapCut ドラフトと同じタイムライン）。

    python render_mp4.py plan.json 出力.mp4

make_draft.py の build_layout をそのまま使うので、CapCut ドラフトと mp4 は同じ割り付けになる。
テロップは フォント「企業」の TTF で焼き込み（白字・黒縁12px・強調行は黄）。
ナレーション＋効果音を混ぜて loudnorm(-16 LUFS)、頭0.5秒/尻0.7秒フェード。

落とし穴（reel-build の実績から）:
- フォントのパスに日本語が入ると ffmpeg が黙って標準ゴシックに落ちる → ASCII パスに corp.ttf をコピーして使う
- drawtext の日本語は textfile= で渡す（エスケープ地獄を避ける）
- subprocess は encoding="utf-8" 必須（cp932 で落ちる）
- 4K を複数同時デコードすると黙って尺欠けする → 1クリップずつ変換して concat、最後に出力尺を検証
"""
import os, re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_draft as md  # noqa: E402

US = md.US
PX_PER_SIZE = 100 / md.BASE_SIZE   # CapCut size 13 = 100px


def work_dir():
    """ASCII だけのパスの作業フォルダ（drawtext のフォント/テキストはここに置く）。"""
    for cand in [os.environ.get("TEMP", ""), r"C:\reel_tmp"]:
        if cand and cand.isascii():
            p = os.path.join(cand, "reel_render")
            os.makedirs(p, exist_ok=True)
            return p
    md.die("ASCII だけのパスの作業フォルダが作れません（C:\\reel_tmp を手で作ってください）")


def ff(args, what):
    r = md.run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-v", "error"] + args)
    if r.returncode != 0:
        md.die("%s に失敗しました:\n%s" % (what, r.stderr[-2000:]))


def probe_dur(path):
    r = md.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "csv=p=0", path])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def esc_path(p):
    # drawtext のオプション値として渡すパス。: と \ をエスケープ
    return p.replace("\\", "/").replace(":", r"\:")


def rgb(c):
    return "0x%02X%02X%02X" % tuple(int(round(v * 255)) for v in c)


def main(plan_path, out_path):
    plan = md.json.load(open(plan_path, encoding="utf-8"))
    plan["_plan_path"] = os.path.abspath(plan_path)
    md.set_style(plan.get("style", "pop")); md.set_font(plan.get("font"))
    if plan.get("color") in md.COLORS:
        md.STYLE["default_color"] = md.COLORS[plan["color"]]
    name = plan["name"]
    assets_dir = plan.get("assets_dir") or os.path.join(md.STABLE_ROOT, name)
    md.check_plan(plan)
    L = md.build_layout(plan, assets_dir)
    total = L["total"] / US

    W = work_dir()
    for f in os.listdir(W):
        try:
            os.remove(os.path.join(W, f))
        except OSError:
            pass

    ttf_src = md.font_ttf()
    if not ttf_src:
        md.die("フォント「企業」の実体（TTF）が見つかりません。_共通素材\\フォント\\メインテロップ.ttf を確認してください。")
    ttf = os.path.join(W, "corp.ttf")
    shutil.copy2(ttf_src, ttf)

    # 1) 映像を1クリップずつ切り出し（全て 1080x1920 / 30fps / 無音）
    print("映像を切り出します（%d カット）" % len(L["video"]))
    pieces = []
    for i, v in enumerate(L["video"]):
        src = os.path.join(assets_dir, v["file"])
        dst = os.path.join(W, "p%03d.mp4" % i)
        # 既定は画面いっぱい（cover）。収める指定（fit=contain）のときだけ黒帯で収める
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        fit = next((c.get("fit") for s in plan["segments"] for c in s["clips"] if c["file"] == v["file"]), None)
        if fit == "contain":
            vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
        vf += ",fps=30,setsar=1,format=yuv420p"
        ff(["-ss", "%.6f" % (v["src_off"] / US), "-t", "%.6f" % (v["dur"] / US), "-i", src,
            "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-x264-params", "threads=2:lookahead-threads=1:rc-lookahead=10", dst],
           "切り出し " + v["file"])
        got = probe_dur(dst)
        if abs(got - v["dur"] / US) > 0.08:
            md.die("%s の切り出し尺がずれました（期待 %.2f / 実際 %.2f）" % (v["file"], v["dur"] / US, got))
        pieces.append(dst)

    lst = os.path.join(W, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in pieces:
            f.write("file '%s'\n" % p.replace("\\", "/"))
    joined = os.path.join(W, "joined.mp4")
    tr = plan.get("transition")
    if tr and len(pieces) > 1:
        # カットの間をディゾルブでつなぐ（plan の "transition": {"type": "fade", "dur": 0.3}）。
        # 各カットの終わりを X 秒だけ止め絵で延ばしてから重ねるので、テロップの時刻（セグメントの開始）はずれない
        X = float(tr.get("dur", 0.3)); kind = tr.get("type", "fade")
        print("ディゾルブでつなぎます（%.2f秒・%s）" % (X, kind))
        durs = [v["dur"] / US for v in L["video"]]
        ins = []; fc = []
        for i, pc in enumerate(pieces):
            ins += ["-i", pc]
            fc.append("[%d:v]tpad=stop_mode=clone:stop_duration=%.3f[c%d]" % (i, X, i))
        prev = "[c0]"; off = 0.0
        # クリップごとの "xfade": 秒（0 なら切り替え）。L["video"] の並びは plan のセグメント順（音声なしセグメント＝1クリップ）
        per = [c.get("xfade") for seg in plan["segments"] for c in seg["clips"]]
        for i in range(1, len(pieces)):
            off += durs[i - 1]
            xi = X if (i >= len(per) or per[i] is None) else max(0.001, float(per[i]))
            outl = "[x%d]" % i if i < len(pieces) - 1 else "[v]"
            fc.append("%s[c%d]xfade=transition=%s:duration=%.3f:offset=%.3f%s" % (prev, i, kind, xi, off, outl))
            prev = outl
        fx = os.path.join(W, "filter_join.txt")
        with open(fx, "w", encoding="utf-8") as f:
            f.write(";\n".join(fc))
        ff(ins + ["-filter_complex_script", fx, "-map", "[v]", "-t", "%.3f" % total, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                  "-x264-params", "threads=2:lookahead-threads=1:rc-lookahead=10", "-pix_fmt", "yuv420p", joined], "結合（ディゾルブ）")
    else:
        ff(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined], "結合")

    # 2) テロップ焼き込みフィルタ（1行=1 drawtext）
    print("テロップを焼き込みます（%d 行）" % len(L["telop"]))
    chain = []
    for i, t in enumerate(L["telop"]):
        tf = os.path.join(W, "t%03d.txt" % i)
        with open(tf, "w", encoding="utf-8") as f:
            f.write(t["text"])
        fs = int(round(t["size"] * PX_PER_SIZE))
        s, e = t["start"] / US, (t["start"] + t["dur"]) / US
        chain.append(
            ("drawtext=textfile='%s':fontfile='%s':fontsize=%d:fontcolor=%s:"
             + ("borderw=12:bordercolor=black:" if md.STYLE.get("border", True) else "shadowx=0:shadowy=5:shadowcolor=black@0.75:")
             + "x=%d-tw/2:y=%d-th/2:enable='between(t,%.3f,%.3f)'")
            % (esc_path(tf), esc_path(ttf), fs, rgb(t["color"]), int(round(t.get("x", 540))), int(round(t["y"])), s, e))
    vchain = ",".join(chain) if chain else "null"
    if md.STYLE.get("border", True):   # pop だけ頭と尻をフェード。restaurant は暗転しない（2026-10-12 代表指示）
        vchain += ",fade=t=in:st=0:d=0.5,fade=t=out:st=%.3f:d=0.7" % max(0.0, total - 0.7)

    # 3) 音声: ナレーション＋効果音＋（OP/EDの素材音）
    inputs = ["-i", joined]
    amix = []
    idx = 1
    for a in L["audio"]:
        inputs += ["-i", os.path.join(assets_dir, a["file"])]
        amix.append("[%d:a]adelay=%d|%d,volume=1.0[a%d]" % (idx, a["start"] // 1000, a["start"] // 1000, idx))
        idx += 1
    for s in L["se"]:
        inputs += ["-i", os.path.join(assets_dir, s["file"])]
        amix.append("[%d:a]adelay=%d|%d,volume=%.2f[a%d]"
                    % (idx, s["start"] // 1000, s["start"] // 1000, s["volume"], idx))
        idx += 1
    for v in L["video"]:
        if v.get("keep_audio"):
            inputs += ["-i", os.path.join(assets_dir, v["file"])]
            amix.append("[%d:a]atrim=0:%.3f,adelay=%d|%d,volume=1.0[a%d]"
                        % (idx, v["dur"] / US, v["start"] // 1000, v["start"] // 1000, idx))
            idx += 1
    n = len(amix)
    # 音声は joined.mp4 を入力に含めないので、入力番号を 1 つ繰り下げる
    amix = [re.sub(r"^\[(\d+):a\]", lambda m: "[%d:a]" % (int(m.group(1)) - 1), x) for x in amix]
    script = ["[0:v]%s[v]" % vchain]
    if n:
        script += amix
        script.append("".join("[a%d]" % (i + 1) for i in range(n)) +
                      "amix=inputs=%d:normalize=0:dropout_transition=0,"
                      "loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,apad[a]"   # apad: 効果音だけのとき音声が短くなり映像が削れるのを防ぐ（-t total で切る）
                      % (n,))
    # 映像と音声は別々に書き出してから合わせる。
    # 1本の ffmpeg で [v] と [a] を同時に出すと、音声の入力が多い（10本以上）とき 5秒付近で止まることがある（2026-10-11 に実際に起きた）
    fv = os.path.join(W, "filter_video.txt")
    with open(fv, "w", encoding="utf-8") as f:
        f.write(script[0])
    print("書き出します（映像）")
    vtmp = os.path.join(W, "video_only.mp4")
    ff(["-i", joined, "-filter_complex_script", fv, "-map", "[v]", "-an", "-t", "%.3f" % total,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-x264-params", "threads=2:lookahead-threads=1:rc-lookahead=10", "-pix_fmt", "yuv420p", vtmp], "映像の書き出し")
    if n:
        fa = os.path.join(W, "filter_audio.txt")
        with open(fa, "w", encoding="utf-8") as f:
            f.write(";\n".join(script[1:]))
        print("書き出します（音声）")
        atmp = os.path.join(W, "audio_only.m4a")
        ff(inputs[2:] + ["-filter_complex_script", fa, "-map", "[a]", "-t", "%.3f" % total,
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", atmp], "音声の書き出し")
        ff(["-i", vtmp, "-i", atmp, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest",
            "-movflags", "+faststart", out_path], "合成")
    else:
        ff(["-i", vtmp, "-c", "copy", "-movflags", "+faststart", out_path], "合成")
    got = probe_dur(out_path)
    if abs(got - total) > 0.15:
        md.die("出力の尺がずれました（期待 %.2f / 実際 %.2f）。メモリ不足の可能性。もう一度実行してください。" % (total, got))
    print("")
    print("できました: %s（%.2f秒）" % (out_path, got))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        md.die("使い方: python render_mp4.py plan.json 出力.mp4")
    main(sys.argv[1], sys.argv[2])
