# -*- coding: utf-8 -*-
"""動画のもとになる静止画を作る（gen_clip.py に渡す「元絵」用）。

    python gen_image.py 見積
    python gen_image.py 試作 out.png "英語のプロンプト" [参考画像.png ...]   … 約6円/枚
    python gen_image.py 本番 out.png "英語のプロンプト" [参考画像.png ...]   … 約20円/枚

試作＝gemini-2.5-flash-image、本番＝gemini-3-pro-image。
構図やレイアウトを探す段階は必ず「試作」で回すこと。値段が3.4倍ちがう。
"""
import base64
import io
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost

ROOT = "https://generativelanguage.googleapis.com/v1beta"
MODES = {
    "試作": ("gemini-2.5-flash-image", "gemini-2.5-flash-image"),
    "本番": ("gemini-3-pro-image", "gemini-3-pro-image"),
}


def small_b64(path, max_side=1024):
    """参考画像は送る前に縮める。

    元のまま何枚も積むと、JSONを組む時点で MemoryError になる（このPCは空きが少ない）。
    手本として渡すだけなので1024pxあれば足りる。
    """
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if max(im.size) > max_side:
        r = max_side / max(im.size)
        im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def generate(mode, out, prompt, refs):
    key = cost.api_key()
    model, ledger = MODES[mode]

    ok, jpy, used, cap = cost.check_budget(ledger, 1)
    if not ok:
        print("止めました。今月すでに %d円 使っていて、上限 %d円 を超えます。" % (used, cap))
        print("  上限を上げるなら: python cost.py 上限 <金額>")
        sys.exit(1)

    parts = [{"text": prompt}]
    for r in refs:
        if not os.path.exists(r):
            print("参考画像がありません: " + r)
            sys.exit(1)
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": small_b64(r)}})

    payload = {"contents": [{"parts": parts}],
               "generationConfig": {"responseModalities": ["TEXT", "IMAGE"],
                                    "imageConfig": {"aspectRatio": "9:16"}}}
    req = urllib.request.Request(
        "%s/models/%s:generateContent?key=%s" % (ROOT, model, key),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            res = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("APIエラー %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
        sys.exit(1)

    label = os.path.basename(out)
    for c in res.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            inl = p.get("inline_data") or p.get("inlineData")
            if inl:
                open(out, "wb").write(base64.b64decode(inl["data"]))
                cost.record(ledger, 1, label, ok=True)
                print("できました: %s（%d円・今月の合計 %d円）" % (out, jpy, cost.month_total()))
                return
            if p.get("text"):
                print("返事:", p["text"][:150])
    print("画像が返ってきませんでした。")
    # 返ってこなくてもサーバー側では生成済み＝課金対象
    cost.record(ledger, 1, label, ok=False)
    sys.exit(1)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("見積", "estimate"):
        used, cap = cost.month_total(), cost.monthly_cap()
        for m, (model, ledger) in MODES.items():
            jpy, usd = cost.estimate(ledger, 1)
            print("%-4s %-24s $%.3f（約%d円）/枚" % (m, model, usd, jpy))
        print("今月これまで: %d円 / 上限 %d円" % (used, cap))
        print("※ 構図さがしは必ず「試作」で。「本番」は最後の1枚だけ。")
    elif a[0] in MODES:
        if len(a) < 3:
            print("使い方: python gen_image.py %s out.png \"プロンプト\" [参考画像...]" % a[0])
            sys.exit(1)
        generate(a[0], a[1], a[2], a[3:])
    else:
        print(__doc__)
        sys.exit(1)
