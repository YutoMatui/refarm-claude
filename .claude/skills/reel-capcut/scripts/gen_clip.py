# -*- coding: utf-8 -*-
"""撮っていない画（え）を、静止画から動画にして埋める。

素材が無いカットのための最後の手段。1本8秒で約180円かかるので、
実写が1本でもあるならそちらを使うこと。

    python gen_clip.py 見積                                  … 値段だけ出す（生成しない）
    python gen_clip.py 実行 out.mp4 元絵.png "動きの指示"      … 実際に作る
    python gen_clip.py 実行 out.mp4 元絵.png "動きの指示" 終わりの絵.png … 最初の絵から終わりの絵へ変化させる（first/last frame）
    python gen_clip.py 履歴                                  … だれがいくら使ったか

APIキーは環境変数 GEMINI_API_KEY から読む（スクリプトには書かない）。
使ったぶんは Drive の共有台帳に自動で記録される（cost.py）。
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost

ROOT = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "veo-3.1-fast-generate-preview"
LEDGER_MODEL = "veo-3.1-fast"
CLIP_SEC = 8

# 生成のクセ（実際に踏んだもの）。プロンプトの末尾に必ず足す
RULES = (" The camera is locked off: no orbit, no rotation. Nothing in the frame moves "
         "except what is described above. Any logo or text in the image must stay exactly "
         "as it is and must never change shape. This is real phone-camera footage, natural "
         "light. No cuts.")


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode("ascii")


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("APIエラー %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
        return None


def show_estimate():
    jpy, usd = cost.estimate(LEDGER_MODEL, CLIP_SEC)
    used, cap = cost.month_total(), cost.monthly_cap()
    print("生成動画 1本 = %d秒 = $%.2f（約%d円）" % (CLIP_SEC, usd, jpy))
    print("今月これまで: %d円 / 上限 %d円（あと %d円ぶん = 約%d本）"
          % (used, cap, max(0, cap - used), max(0, cap - used) // max(1, jpy)))
    print("※ 実写が1本でもあるなら、そちらを使ってください。生成は最後の手段です。")


def generate(out, still, prompt, last=None):
    key = cost.api_key()
    if not os.path.exists(still):
        print("エラー: 元にする画像がありません: " + still)
        sys.exit(1)

    ok, jpy, used, cap = cost.check_budget(LEDGER_MODEL, CLIP_SEC)
    if not ok:
        print("止めました。今月すでに %d円 使っていて、この1本(%d円)で上限 %d円 を超えます。"
              % (used, jpy, cap))
        print("  上限を上げるなら: python cost.py 上限 <金額>")
        sys.exit(1)
    print("これから %d円 使います（今月 %d円 → %d円 / 上限 %d円）"
          % (jpy, used, used + jpy, cap))

    mime = "image/png" if still.lower().endswith(".png") else "image/jpeg"
    op = post("%s/models/%s:predictLongRunning?key=%s" % (ROOT, MODEL, key),
              {"instances": [dict({"prompt": prompt + RULES,
                                   "image": {"bytesBase64Encoded": b64(still), "mimeType": mime}},
                                  **({"lastFrame": {"bytesBase64Encoded": b64(last),
                                                    "mimeType": "image/png" if last.lower().endswith(".png") else "image/jpeg"}} if last else {}))],
               "parameters": {"aspectRatio": "9:16", "resolution": "1080p"}})
    if not op or "name" not in op:
        print("生成を始められませんでした（課金なし）。")
        sys.exit(1)

    label = os.path.basename(out)
    print("生成中です（2〜4分かかります）...")
    for _ in range(80):
        time.sleep(15)
        try:
            with urllib.request.urlopen("%s/%s?key=%s" % (ROOT, op["name"], key),
                                        timeout=120) as r:
                st = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print("状態の確認に失敗しました: %s" % e.code)
            cost.record(LEDGER_MODEL, CLIP_SEC, label, ok=False)
            sys.exit(1)
        if not st.get("done"):
            continue
        if "error" in st:
            print("失敗しました: " + json.dumps(st["error"], ensure_ascii=False)[:200])
            # 失敗してもサーバー側では生成済み＝課金対象なので必ず記録する
            cost.record(LEDGER_MODEL, CLIP_SEC, label, ok=False)
            sys.exit(1)
        resp = st.get("response", {})
        vids = (resp.get("generateVideoResponse", {}).get("generatedSamples")
                or resp.get("generatedVideos") or resp.get("videos") or [])
        uri = (vids[0].get("video", {}).get("uri") or vids[0].get("uri")) if vids else None
        if not uri:
            print("動画のURLが入っていませんでした。")
            cost.record(LEDGER_MODEL, CLIP_SEC, label, ok=False)
            sys.exit(1)
        req = urllib.request.Request(uri + ("&" if "?" in uri else "?") + "key=" + key)
        with urllib.request.urlopen(req, timeout=900) as r, open(out, "wb") as f:
            # まるごとメモリに載せない（このPCは空きが少なくMemoryErrorになる）
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
        cost.record(LEDGER_MODEL, CLIP_SEC, label, ok=True)
        print("できました: %s（%d円・今月の合計 %d円）" % (out, jpy, cost.month_total()))
        return
    print("時間切れでした。")
    cost.record(LEDGER_MODEL, CLIP_SEC, label, ok=False)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    mode = sys.argv[1]
    if mode in ("履歴", "history"):
        cost.report()
    elif mode in ("見積", "estimate"):
        show_estimate()
    elif mode in ("実行", "run"):
        if len(sys.argv) < 5:
            print("使い方: python gen_clip.py 実行 out.mp4 元絵.png \"動きの指示\"")
            sys.exit(1)
        generate(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else None)
    else:
        print(__doc__)
        sys.exit(1)
