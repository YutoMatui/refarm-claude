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
import os
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
    r = md.run(["ffmpeg", "-hide_banner", "-y", "-v", "error"] + args)
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
    md.set_style(plan.get("style", "pop"))
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
             + ("borderw=12:bordercolor=black:" if md.STYLE.get("border", True) else "shadowx=0:shadowy=4:shadowcolor=black@0.45:")
             + "x=(w-tw)/2:y=%d-th/2:enable='between(t,%.3f,%.3f)'")
            % (esc_path(tf), esc_path(ttf), fs, rgb(t["color"]), int(round(t["y"])), s, e))
    vchain = ",".join(chain) if chain else "null"
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
    script = ["[0:v]%s[v]" % vchain]
    if n:
        script += amix
        script.append("".join("[a%d]" % (i + 1) for i in range(n)) +
                      "amix=inputs=%d:normalize=0:dropout_transition=0,"
                      "loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=%.3f:d=0.7[a]"
                      % (n, max(0.0, total - 0.7)))
    fscript = os.path.join(W, "filter.txt")
    with open(fscript, "w", encoding="utf-8") as f:
        f.write(";\n".join(script))

    print("書き出します")
    args = inputs + ["-filter_complex_script", fscript, "-map", "[v]"]
    if n:
        args += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    args += ["-t", "%.3f" % total, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-x264-params", "threads=2:lookahead-threads=1:rc-lookahead=10",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    ff(args, "書き出し")
    got = probe_dur(out_path)
    if abs(got - total) > 0.15:
        md.die("出力の尺がずれました（期待 %.2f / 実際 %.2f）。メモリ不足の可能性。もう一度実行してください。" % (total, got))
    print("")
    print("できました: %s（%.2f秒）" % (out_path, got))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        md.die("使い方: python render_mp4.py plan.json 出力.mp4")
    main(sys.argv[1], sys.argv[2])
