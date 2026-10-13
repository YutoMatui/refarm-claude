# -*- coding: utf-8 -*-
"""plan.json を CapCut ドラフトに変換する（汎用版）。

これまでは企画ごとに capcut_export9.py のようなスクリプトを複製して SEGS を書き換えていた。
このスクリプトは中身を plan.json に外出しして、コードを触らなくても新しい動画を作れるようにしたもの。

    python make_draft.py plan.json

同じ plan.json から mp4 を焼き出すのは render_mp4.py（タイムライン計算は build_layout を共用）。

plan.json の形（詳しくは SKILL.md）:
{
  "name": "試作編第2話",
  "assets_dir": "C:/Users/YutoM/Videos/リール素材/試作編第2話",   // 省略可
  "sources": ["G:/マイドライブ/50日企画素材/7 5 試作", ...],       // 素材を探すフォルダ
  "segments": [
    {"audio": "オープニング.m4a",
     "clips": [{"file": "オープニング.mp4", "offset": 0}],
     "telop": [{"at": 0.35, "lines": ["16日後に三宮に"], "y": 231}]}
  ],
  "se": [{"file": "ドーン.mp3", "seg": 7, "at": 3.1, "volume": 0.7}],
  "mute_clips": true,                      // 省略可。true なら音声なしセグメントの素材音も使わない（店の動画で現場音が汚いとき）
  "transition": {"type": "fade", "dur": 0.3}   // 省略可。render_mp4 のカット間ディゾルブ（CapCut ドラフトには付かないので CapCut で付ける）
}

telop カードの任意項目:
  "until": 終わり秒（省略=セグメント末尾）  "y": 中心px（既定1340）  "x": 横の中心px（既定540＝中央。図解のラベル用）  "size": CapCut上の文字サイズ（既定13）
  "vertical": true  縦書き（lines の1つ＝1列。右から左。CapCut では縦書きテキストになり、文字のまま直せる）
セグメントの "overlays": [{"file": "farmer_tile.png", "at": 0.3, "x": 832, "y": 818, "w": 356}]  … 画像を別トラックに重ねる（CapCut で動かせる）
  "color": "white"/"yellow"（カード全体）  "colors": ["white","yellow"]（行ごと。color より優先）
"""
import json
import os
import re
import shutil
import subprocess
import sys

US = 1_000_000
CAPCUT_DRAFTS = os.path.expandvars(
    r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
SE_LIB = os.path.expandvars(r"%USERPROFILE%\Videos\リール素材\SE_CapCutライブラリ")
STABLE_ROOT = os.path.expandvars(r"%USERPROFILE%\Videos\リール素材")

# 全員で共有する素材（Drive）。効果音・OP/ED・フォント。
# ここに無いと、メンバーのPCでは効果音やOPが見つからず「別の質感の動画」になる（2026-09-05に実際に起きた）。
COMMON = r"G:\マイドライブ\50日企画素材\_共通素材"
COMMON_DIRS = [
    os.path.join(COMMON, "SE_CapCutライブラリ"),
    os.path.join(COMMON, "OP_ED"),
    os.path.join(COMMON, "フォント"),
    SE_LIB,
    os.path.join(STABLE_ROOT, "フォント"),
    os.path.join(STABLE_ROOT, "試作編第1話"),          # ゆうとPCでの OP/ED の実体
    r"G:\マイドライブ\50日企画素材\7 14 素材",     # OP/EDの元の置き場
]

# テロップのフォント = コーポレート・ロゴ（ラウンド）ver3 Bold。CapCut内の名前は「企業」
FONT_ID = "7532058832042790161"
FONT_CACHE = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Cache\effect"), FONT_ID)
CANVAS_W, CANVAS_H = 1080, 1920
BASE_SIZE = 13.0          # CapCut の文字サイズ 13 = 焼き込み 100px 相当
LINE_STEP = 130           # size 13 のときの行送り px

# 録音のヒスノイズ除去（S/N +16dB・音声帯域は無傷。実測で確認済み）
DENOISE = "highpass=f=85,afftdn=nr=16:nf=-42,lowpass=f=14000"

WHITE = (1.0, 1.0, 1.0)
YELLOW = (1.0, 0.84, 0.2)
CREAM = (1.0, 0.97, 0.90)
GOLD = (1.0, 0.84, 0.55)
BROWN = (0.35, 0.18, 0.055)   # 明るい地（ベージュ）用の文字
TERRA = (0.55, 0.20, 0.06)    # 明るい地での強調（焦げ茶の中の差し色）
COLORS = {"white": WHITE, "yellow": YELLOW, "黄": YELLOW, "白": WHITE, "cream": CREAM, "gold": GOLD, "brown": BROWN, "terra": TERRA}

# 様式：plan.json の "style" で切り替える
#   "pop"（既定）      = reference/style.md         50日企画の連載（企業フォント・白字黒縁・OP/ED・SE）
#   "restaurant"       = reference/style_restaurant.md 店のメニュー・営業日・行き方（Shippori Mincho・クリーム・縁なし・OP/EDなし）
_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
STYLES = {
    "pop": {"ttf": None, "font_id": FONT_ID, "font_title": "企業", "default_color": WHITE,
            "border": True, "need_op_ed": True, "size": BASE_SIZE},
    "restaurant": {"ttf": os.path.join(_REPO, "fonts", "ShipporiMincho-Bold.ttf"), "font_id": "",
                   "font_title": "Shippori Mincho", "default_color": CREAM,
                   "border": False, "need_op_ed": False, "size": 11.0},
}
STYLE = {}
def set_style(name):
    STYLE.clear(); STYLE.update(STYLES.get(name or "pop", STYLES["pop"])); STYLE["name"] = name if name in STYLES else "pop"


def set_font(font):
    """plan の "font": {"file": "KleeOne-SemiBold.ttf", "title": "Klee One"} で様式のフォントだけ差し替える（file はリポジトリの fonts/ に置く）"""
    if font:
        STYLE.update({"ttf": os.path.join(_REPO, "fonts", font["file"]), "font_id": "", "font_title": font.get("title", font["file"])})
set_style("pop")


def run(cmd):
    # Windows の cp932 で ffmpeg の stderr が UnicodeDecodeError になるため必ず utf-8 指定
    # stdin を閉じて渡す。開いたままだと、背景で動かしたときに ffmpeg がキー入力待ちで止まることがある（2026-10-11 に実際に起きた）
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)


def die(msg):
    print("エラー: " + msg)
    sys.exit(1)


# ── 素材を探す ──────────────────────────────────────────────
def find_source(name, sources):
    """素材名からフルパスを引く。sources の順に探し、見つからなければ再帰で探す。"""
    if os.path.isabs(name) and os.path.exists(name):
        return name
    for d in sources:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    for d in sources:
        for root, _dirs, files in os.walk(d):
            if name in files:
                return os.path.join(root, name)
    for d in COMMON_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def cover_scale(vmat, fit):
    """横長素材を縦画面いっぱいに拡大する倍率。

    CapCut は素材を画面に「収める」(contain) のが既定なので、横長の素材を置くと上下に黒帯が出る。
    黒帯のままだと素人っぽく見える。1080x1920 を覆う (cover) 倍率を計算して ClipSettings に渡す。
    画面録画など切れてはいけない素材だけ plan で "fit": "contain" を指定する。
    """
    if fit == "contain":
        return None
    w, h = getattr(vmat, "width", 0), getattr(vmat, "height", 0)
    if not w or not h:
        return None
    contain = min(CANVAS_W / w, CANVAS_H / h)
    cover = max(CANVAS_W / w, CANVAS_H / h)
    s = cover / contain
    return None if abs(s - 1.0) < 0.01 else s


def stage(name, sources, assets_dir):
    """素材を安定パスへコピーする。

    CapCut はドラフトを開くたびに元ファイルを読みにいくので、Drive（G:）や
    scratchpad を参照させてはいけない（アンマウント・セッション終了で消える）。
    """
    dst = os.path.join(assets_dir, name)
    if os.path.exists(dst):
        return dst
    src = find_source(name, sources)
    if src is None:
        die("素材が見つかりません: %s\n  探した場所: %s" % (name, "  ".join(sources)))
    if name.lower().endswith(".m4a"):
        r = run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", DENOISE,
                 "-c:a", "aac", "-b:a", "192k", "-ar", "48000", dst])
        if r.returncode != 0:
            shutil.copy2(src, dst)
            print("  ノイズ除去に失敗したので原音をコピー: " + name)
        else:
            print("  ノイズ除去してコピー: " + name)
        return dst
    shutil.copy2(src, dst)
    print("  コピー: " + name)
    return dst


# ── CapCut 国際版ネイティブ化 ───────────────────────────────
def pick_template(explicit):
    """骨格に使う既存ドラフトを選ぶ。

    pyJianYingDraft は剪映（中国版）形式で書くため、CapCut国際版がそのままでは
    「異常なパス」と言って開かない。CapCut 自身が作ったドラフトの外枠に
    tracks/materials だけ差し込むと開けるようになる。
    """
    if explicit:
        p = os.path.join(CAPCUT_DRAFTS, explicit, "draft_content.json")
        if os.path.exists(p):
            return p
        die("指定された骨格ドラフトがありません: " + explicit)
    best = None
    for name in os.listdir(CAPCUT_DRAFTS):
        p = os.path.join(CAPCUT_DRAFTS, name, "draft_content.json")
        if not os.path.exists(p):
            continue
        try:
            j = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if (j.get("platform") or {}).get("app_source") != "cc":
            continue
        m = os.path.getmtime(p)
        if best is None or m > best[0]:
            best = (m, p)
    if best is None:
        die("CapCutが作ったドラフトが1つも見つかりません。\n"
            "  CapCutを開いて、何でもいいので新しいプロジェクトを1つ作ってから、もう一度実行してください。")
    return best[1]


def normalize_paths(obj):
    """パスを C:/... のスラッシュ区切りに直す。バックスラッシュだとCapCutが開けない。"""
    if isinstance(obj, dict):
        return {k: normalize_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_paths(v) for v in obj]
    if isinstance(obj, str) and re.match(r"^[A-Za-z]:\\", obj):
        return obj.replace("\\", "/")
    return obj


def nativize(draft_dir, draft_name, template_path):
    content_p = os.path.join(draft_dir, "draft_content.json")
    meta_p = os.path.join(draft_dir, "draft_meta_info.json")
    content = normalize_paths(json.load(open(content_p, encoding="utf-8")))
    meta = normalize_paths(json.load(open(meta_p, encoding="utf-8")))

    tpl = json.load(open(template_path, encoding="utf-8"))
    native = dict(tpl)
    native["id"] = content["id"]
    native["duration"] = content["duration"]
    native["fps"] = content["fps"]
    native["canvas_config"] = {"ratio": "original", "width": 1080, "height": 1920,
                               "background": None}
    native["tracks"] = content["tracks"]
    mats = dict(tpl["materials"])
    for k in mats:
        mats[k] = content["materials"].get(k, [])
    # 骨格側に無い素材キー（texts等）も持ち込む
    for k, v in content["materials"].items():
        if k not in mats and v:
            mats[k] = v
    native["materials"] = mats
    for k in ["cover", "static_cover_image_path", "retouch_cover", "path", "name",
              "create_time", "update_time"]:
        if k in content:
            native[k] = content[k]

    # allow_replace での再生成時に空で書かれることがあるので明示的に入れ直す
    meta["tm_duration"] = native.get("duration", 0)
    meta["draft_name"] = draft_name
    meta["draft_root_path"] = CAPCUT_DRAFTS.replace("\\", "/")
    meta["draft_fold_path"] = meta["draft_root_path"] + "/" + draft_name
    json.dump(native, open(content_p, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    json.dump(meta, open(meta_p, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))


def font_ttf():
    if STYLE.get("ttf"):
        return STYLE["ttf"].replace("\\", "/") if os.path.exists(STYLE["ttf"]) else ""
    """フォント「企業」の実体（TTF）のパス。CapCutのキャッシュ → 手持ちの メインテロップ.ttf の順。"""
    if os.path.isdir(FONT_CACHE):
        for root, _dirs, files in os.walk(FONT_CACHE):
            for f in files:
                if f.lower().endswith((".ttf", ".otf")):
                    return os.path.join(root, f).replace("\\", "/")
    local = find_source("メインテロップ.ttf", [])
    return local.replace("\\", "/") if local else ""


def inject_font(content_p):
    """テロップのフォントを「企業」（コーポレート・ロゴ ラウンド ver3 Bold）にする。

    pyJianYingDraft はフォント情報を一切書かないので、生成直後のドラフトは CapCut 既定のゴシック
    （CapCut上の表示は「システム」）になる。これまではゆうとが毎回 CapCut 上で全選択→一括変更していた。
    その手作業を無くすため、ゆうと編集版（間借り編2_v5）のテキスト素材と同じ形をここで書き足す。
    """
    import uuid
    c = json.load(open(content_p, encoding="utf-8"))
    texts = c.get("materials", {}).get("texts", [])
    if not texts:
        return False
    ttf = font_ttf()
    for t in texts:
        t.update({"font_path": ttf, "font_resource_id": STYLE["font_id"], "font_id": "",
                  "font_title": "none", "font_name": "", "font_source_platform": 1,
                  "font_category_id": "", "font_category_name": "", "font_url": "",
                  "font_third_resource_id": "", "font_team_id": ""})
        t["fonts"] = [{"id": str(uuid.uuid4()).upper(), "resource_id": STYLE["font_id"],
                       "third_resource_id": "", "category_id": "preset",
                       "category_name": "プリセット", "source_platform": 1, "path": ttf,
                       "effect_id": STYLE["font_id"], "title": STYLE["font_title"], "team_id": "", "file_uri": "",
                       "request_id": ""}]
        try:
            cj = json.loads(t.get("content", "{}"))
            for st in cj.get("styles", []):
                st["font"] = {"path": ttf, "id": STYLE["font_id"]}
            t["content"] = json.dumps(cj, ensure_ascii=False)
        except Exception:
            pass
    json.dump(c, open(content_p, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    return bool(ttf)


# ── タイムライン計算（CapCut と mp4 焼き出しで共用）────────────
def check_plan(plan):
    segments = plan.get("segments") or []
    if not segments:
        die("segments が空です。")
    # 骨格の検査。OPとEDが無い動画は「りふぁーむの動画」に見えない（reference/style.md 1.）
    if not plan.get("no_op_ed") and STYLE.get("need_op_ed", True):
        first = (segments[0].get("clips") or [{}])[0].get("file", "")
        last = (segments[-1].get("clips") or [{}])[-1].get("file", "")
        if "オープニング" not in first:
            die("最初のセグメントが オープニング.mp4 で始まっていません（今: %s）。\n"
                "  全本共通で OP を付けます。意図して外す場合だけ plan に \"no_op_ed\": true を書いてください。"
                % (first or "なし"))
        if "エンディング" not in last:
            die("最後のセグメントが エンディング.mp4 で終わっていません（今: %s）。\n"
                "  全本共通で ED を付けます。意図して外す場合だけ plan に \"no_op_ed\": true を書いてください。"
                % (last or "なし"))


def build_layout(plan, assets_dir):
    """plan から絶対時間のタイムラインを組む。全て µs 整数。

    返り値:
      {"total": µs,
       "video": [{"file", "start", "dur", "src_off", "scale", "vmat"}],
       "audio": [{"file", "start", "dur", "amat"}],
       "telop": [{"text", "start", "dur", "y", "size", "color"}],   # 1行=1要素
       "se":    [{"file", "start", "dur", "volume", "amat"}]}
    """
    import pyJianYingDraft as d
    segments = plan["segments"]
    # sources は plan.json のある場所からの相対パスでもよい（別のPCでも同じ plan が使えるように）
    base = os.path.dirname(os.path.abspath(plan.get("_plan_path", "")))  if plan.get("_plan_path") else os.getcwd()
    sources = [d if os.path.isabs(d) else os.path.normpath(os.path.join(base, d)) for d in (plan.get("sources") or [])]
    os.makedirs(assets_dir, exist_ok=True)

    print("素材をそろえます")
    for seg in segments:
        if seg.get("audio"):
            stage(seg["audio"], sources, assets_dir)
        for c in seg["clips"]:
            stage(c["file"], sources, assets_dir)
    for s in plan.get("se", []):
        stage(s["file"], sources, assets_dir)

    L = {"video": [], "audio": [], "telop": [], "se": []}
    cursor = 0
    starts, durs = [], []
    for seg in segments:
        starts.append(cursor)
        clips = seg["clips"]

        # 音声なしのセグメントは、1本目のクリップの尺をそのまま使う（OP/EDの単体置き）
        if not seg.get("audio"):
            vmat = d.VideoMaterial(os.path.join(assets_dir, clips[0]["file"]))
            # "dur": 秒 を書くと、その長さで切る（テンポを上げるとき。素材より長くはできない）
            voff = round(float(clips[0].get("offset", 0)) * US)   # "offset": 秒 で頭を切る
            avail = max(100_000, vmat.duration - voff)
            vdur = avail if clips[0].get("dur") is None else min(avail, round(float(clips[0]["dur"]) * US))
            L["video"].append({"file": clips[0]["file"], "start": cursor, "dur": vdur,
                               "src_off": voff, "scale": cover_scale(vmat, clips[0].get("fit")),
                               "vmat": vmat, "keep_audio": not plan.get("mute_clips", False)})   # "mute_clips": true で素材の音を使わない
            durs.append(vdur)
            cursor += vdur
            continue

        amat = d.AudioMaterial(os.path.join(assets_dir, seg["audio"]))
        # 尺は ffprobe でなく AudioMaterial.duration を正とする（ms差で素材時長超過になる）
        adur = amat.duration
        L["audio"].append({"file": seg["audio"], "start": cursor, "dur": adur, "amat": amat})

        mats = []
        for c in clips:
            vmat = d.VideoMaterial(os.path.join(assets_dir, c["file"]))
            off = round(c.get("offset", 0) * US)
            avail = max(300_000, vmat.duration - off - 50_000)
            mats.append((vmat, off, avail, c.get("dur"), c.get("fit"), c["file"]))

        fixed_total = sum(round(f * US) for _, _, _, f, _fit, _n in mats if f is not None)
        flex_n = sum(1 for m in mats if m[3] is None)
        flex_each = max(300_000, (adur - fixed_total) // flex_n) if flex_n else 0

        takes, remaining = [], adur
        for vmat, off, avail, fixed, fit, fname in mats:
            want = round(fixed * US) if fixed is not None else flex_each
            take = min(want, avail)
            takes.append([vmat, off, take, avail, fit, fname])
            remaining -= take
        if remaining > 0:
            # 足りない分は最後のクリップを伸ばす。それでも足りなければ警告する
            vmat, off, take, avail, _fit, _n = takes[-1]
            add = min(remaining, avail - take)
            takes[-1][2] = take + add
            if remaining - add > 50_000:
                print("  警告: %s は映像が %.2f秒 足りません（CapCut上で静止延長するか素材を足してください）"
                      % (seg["audio"], (remaining - add) / US))
        elif remaining < 0:
            # 固定尺の合計が音声尺を超えると次のセグメントと重なるので末尾を刈る
            takes[-1][2] = max(100_000, takes[-1][2] + remaining)

        t = cursor
        for vmat, off, take, _avail, fit, fname in takes:
            if take <= 0:
                continue
            L["video"].append({"file": fname, "start": t, "dur": take, "src_off": off,
                               "scale": cover_scale(vmat, fit), "vmat": vmat, "keep_audio": False})
            t += take
        durs.append(adur)
        cursor += adur
    L["total"] = cursor

    for si, seg in enumerate(segments):
        for card in seg.get("telop", []):
            lines = card["lines"]
            size = float(card.get("size", STYLE.get("size", BASE_SIZE)))
            step = LINE_STEP * size / BASE_SIZE
            yc = card.get("y", 1340)
            per_line = card.get("colors")
            S = starts[si] + round(card.get("at", 0) * US)
            E = (starts[si] + round(card["until"] * US)) if card.get("until") is not None \
                else starts[si] + durs[si]
            E = min(E, starts[si] + durs[si])
            n = len(lines)
            vertical = bool(card.get("vertical"))   # 縦書き：lines の1つが1列。右から左へ並べる（CapCut の縦書きテキスト）
            colstep = (100 / BASE_SIZE) * size * 1.9   # 列の間隔 px（文字の大きさ×1.9）
            for li, line in enumerate(lines):
                cname = (per_line[li] if per_line and li < len(per_line) else card.get("color", ""))
                if vertical:
                    x = card.get("x", 540) + ((n - 1) / 2 - li) * colstep; y = yc
                else:
                    x = card.get("x", 540); y = yc + (li - (n - 1) / 2) * step
                L["telop"].append({"text": line, "start": S, "dur": E - S,
                                   "y": y, "x": x, "size": size, "vertical": vertical,
                                   "color": COLORS.get(cname, STYLE["default_color"]), "line": li})

    # 画像の重ね（農家さんの顔・QRなど）。plan のセグメントに "overlays": [{"file","at","until","x","y","w"}]
    # 別トラックに置くので、CapCut 上で位置や大きさを動かせる
    L["overlay"] = []
    for si, seg in enumerate(segments):
        for ov in seg.get("overlays", []):
            path = stage(ov["file"], sources, assets_dir)
            S = starts[si] + round(ov.get("at", 0) * US)
            E = (starts[si] + round(ov["until"] * US)) if ov.get("until") is not None else starts[si] + durs[si]
            E = min(E, starts[si] + durs[si])
            L["overlay"].append({"file": ov["file"], "path": path, "start": S, "dur": E - S,
                                 "x": ov.get("x", 540), "y": ov.get("y", 960), "w": ov.get("w", 300)})

    for s in plan.get("se", []):
        at = starts[s["seg"]] + round(s.get("at", 0) * US)
        amat = d.AudioMaterial(os.path.join(assets_dir, s["file"]))
        L["se"].append({"file": s["file"], "start": at, "dur": amat.duration,
                        "volume": s.get("volume", 0.6), "amat": amat})
    return L


# ── 本体 ────────────────────────────────────────────────────
def main(plan_path):
    plan = json.load(open(plan_path, encoding="utf-8"))
    plan["_plan_path"] = os.path.abspath(plan_path)
    set_style(plan.get("style", "pop")); set_font(plan.get("font"))
    if plan.get("color") in COLORS:   # 地が明るいときは "color": "brown" で文字の既定色を変える
        STYLE["default_color"] = COLORS[plan["color"]]
    print("様式: %s（reference/%s）" % (STYLE["name"], "style_restaurant.md" if STYLE["name"] == "restaurant" else "style.md"))
    name = plan["name"]
    assets_dir = plan.get("assets_dir") or os.path.join(STABLE_ROOT, name)
    if not os.path.isdir(CAPCUT_DRAFTS):
        die("CapCutのドラフト置き場が見つかりません: " + CAPCUT_DRAFTS +
            "\n  CapCutをインストールして一度起動してください。")
    check_plan(plan)
    L = build_layout(plan, assets_dir)

    import pyJianYingDraft as d
    from pyJianYingDraft import Timerange

    folder = d.DraftFolder(CAPCUT_DRAFTS)
    script = folder.create_draft(name, 1080, 1920, fps=30, allow_replace=True)
    tv = script.append_track(d.TrackSpec(d.TrackType.video, "映像"))
    ta = script.append_track(d.TrackSpec(d.TrackType.audio, "ナレーション"))
    se_tracks = [script.append_track(d.TrackSpec(d.TrackType.audio, "効果音%d" % (i + 1)))
                 for i in range(2)]
    tx_tracks = [script.append_track(d.TrackSpec(d.TrackType.text, t))
                 for t in ["テロップ上", "テロップ下"] + ["テロップ予備%d" % i for i in range(1, 15)]]  # 図解のように同時に多くの文字が出るカットがあるので16本

    print("タイムラインを組みます")
    for v in L["video"]:
        s = v["scale"]
        cs = d.ClipSettings(scale_x=s, scale_y=s) if s else None
        # 現場音はミュート（ナレーションと混ざる）。OP/ED単体は素材の音をそのまま
        script.add_segment(d.VideoSegment(v["vmat"], Timerange(v["start"], v["dur"]),
                                          source_timerange=Timerange(v["src_off"], v["dur"]),
                                          volume=1.0 if v["keep_audio"] else 0.0,
                                          clip_settings=cs), tv)
    for a in L["audio"]:
        script.add_segment(d.AudioSegment(a["amat"], Timerange(a["start"], a["dur"])), ta)

    if L.get("overlay"):
        print("画像を重ねます（%d 枚）" % len(L["overlay"]))
        tov = script.append_track(d.TrackSpec(d.TrackType.video, "画像"))
        from PIL import Image as _Img
        for o in L["overlay"]:
            mat = d.VideoMaterial(o["path"])
            iw, ih = _Img.open(o["path"]).size
            fitted_w = iw * min(CANVAS_W / iw, CANVAS_H / ih)   # CapCut は画像を画面に収めて置くので、その幅を基準に倍率を出す
            sc = o["w"] / fitted_w
            script.add_segment(d.VideoSegment(mat, Timerange(o["start"], o["dur"]),
                                              clip_settings=d.ClipSettings(scale_x=sc, scale_y=sc,
                                                                           transform_x=(o["x"] - 540) / 540,
                                                                           transform_y=(960 - o["y"]) / 960)), tov)
    print("テロップを入れます")
    tx_end = [0] * len(tx_tracks)
    for t in L["telop"]:
        S, E = t["start"], t["start"] + t["dur"]
        seg_t = d.TextSegment(
            t["text"], Timerange(S, E - S),
            style=d.TextStyle(size=t["size"], bold=STYLE["border"], color=t["color"], align=1, vertical=bool(t.get("vertical"))),
            border=(d.TextBorder(color=(0.0, 0.0, 0.0)) if STYLE["border"] else None),
            # 縁取りなしの様式（restaurant）は、代わりに柔らかい影で読ませる
            shadow=(None if STYLE["border"] else d.TextShadow(alpha=0.8, color=(0.0, 0.0, 0.0), diffuse=22.0, distance=6.0, angle=-90.0)),
            # 画面中心が960px。transform_y は正が上なのでこの向きになる
            clip_settings=d.ClipSettings(transform_x=(t["x"] - 540) / 540, transform_y=(960 - t["y"]) / 960))
        # 同じトラック内で時間が重なると落ちるので、空いているトラックへ逃がす
        pref = t["line"] if t["line"] < 2 else 0
        order = [pref] + [x for x in range(len(tx_tracks)) if x != pref]
        k = next((x for x in order if tx_end[x] <= S), None)
        if k is None:
            die("テキストトラックが足りません（%.1f秒付近）" % (S / US))
        script.add_segment(seg_t, tx_tracks[k])
        tx_end[k] = E

    if L["se"]:
        print("効果音を入れます")
    se_end = [0] * len(se_tracks)
    for s in L["se"]:
        at = s["start"]
        k = next((i for i in range(len(se_tracks)) if se_end[i] <= at), None)
        if k is None:
            die("効果音トラックが足りません: %s" % s["file"])
        script.add_segment(d.AudioSegment(s["amat"], Timerange(at, s["dur"]),
                                          volume=s["volume"]), se_tracks[k])
        se_end[k] = at + s["dur"]

    script.save()
    draft_dir = os.path.join(CAPCUT_DRAFTS, name)
    nativize(draft_dir, name, pick_template(plan.get("template_draft")))
    font_ok = inject_font(os.path.join(draft_dir, "draft_content.json"))

    print("")
    print("できました: %s" % draft_dir)
    print("長さ: %.2f秒" % (L["total"] / US))
    print("CapCutを再起動すると一覧に出ます。")
    if not font_ok:
        print("※ フォント「%s」の実体がこのPCに見つかりませんでした。" % STYLE["font_title"])
        print("  CapCutで開いて既定のゴシックになっていたら、テロップを全選択→フォント「%s」に一括変更してください。" % STYLE["font_title"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        die("使い方: python make_draft.py plan.json")
    main(sys.argv[1])
