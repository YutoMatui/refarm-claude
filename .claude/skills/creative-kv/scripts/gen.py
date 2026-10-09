"""Gemini画像生成（参考画像を複数渡せる）。

使い方:
  python gen.py --out base.png --aspect 4:5 --prompt "..." --ref 手本1.jpg --ref 手本2.jpg --ref 商品1.png
  python gen.py --out base.png --aspect 4:5 --prompt-file prompt.txt --ref ...

APIキー: 環境変数 GEMINI_API_KEY を使う。無ければ vegedasheep_images/generate.py の API_KEY を探す。
aspect に使えるもの: 1:1 3:4 4:3 9:16 16:9 2:3 3:2 4:5 5:4 21:9（4:5 は実際には約0.78で返るので後で切って合わせる）
"""
import json, base64, urllib.request, urllib.error, re, sys, os, time, argparse, mimetypes

def api_key():
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k
    here = os.path.dirname(os.path.abspath(__file__))
    for up in range(6):
        cand = os.path.join(here, *([".."] * up), "vegedasheep_images", "generate.py")
        if os.path.exists(cand):
            m = re.search(r'API_KEY\s*=\s*"([^"]+)"', open(cand, encoding="utf-8").read())
            if m:
                return m.group(1)
    sys.exit("GEMINI_API_KEY が見つかりません。環境変数に設定してください。")

def generate(prompt, refs, aspect, out, model="gemini-2.5-flash-image", tries=3):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key()}"
    parts = [{"text": prompt}]
    for p in refs:
        mt = mimetypes.guess_type(p)[0] or "image/png"
        parts.append({"inline_data": {"mime_type": mt, "data": base64.b64encode(open(p, "rb").read()).decode()}})
    payload = {"contents": [{"parts": parts}],
               "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    res = None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                res = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, e.read()[:300]); time.sleep(8)
        except Exception as e:
            print("ERR", e); time.sleep(8)
    if res is None:
        sys.exit("生成に失敗しました")
    for part in res.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            open(out, "wb").write(base64.b64decode(part["inlineData"]["data"]))
            print("saved", out)
            return out
    sys.exit("画像が返りませんでした: " + json.dumps(res)[:300])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt"); ap.add_argument("--prompt-file")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--aspect", default="4:5"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    prompt = a.prompt or open(a.prompt_file, encoding="utf-8").read()
    generate(prompt, a.ref, a.aspect, a.out)
