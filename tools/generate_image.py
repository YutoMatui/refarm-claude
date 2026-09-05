import json
import base64
import urllib.request
import urllib.error
import sys
import os

API_KEY = os.environ.get("GEMINI_API_KEY") or exit("環境変数 GEMINI_API_KEY を設定してください")
MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

INPUT_IMAGE = os.environ.get("INPUT_IMAGE")  # 元写真（編集モード）。未指定ならテキストのみ生成
OUT_DIR = os.environ.get("OUT_DIR", "flyers/img")

prompts = {
    "A_product_solo": (
        "Edit this photo of 'Vege-dashi-soup' (a clear Japanese vegetable dashi broth "
        "in a white paper cup, containing diced eggplant, carrot, daikon radish, and "
        "kaiware sprouts) into a clean, appetizing product photograph for catalog use. "
        "Replace the background with a bright clean off-white tabletop, softly blurred. "
        "Use soft natural window light from the side to enhance the transparency of the broth "
        "and the vivid colors of the vegetables. Shoot from a 30-degree overhead angle. "
        "Remove the gas burner and any clutter in the background. "
        "Clean up the white rim of the cup. Add gentle steam rising from the broth. "
        "KEEP the contents exactly as in the original: same vegetables, same broth color, "
        "same paper cup shape. No text, no logo, no watermark. "
        "Warm, natural, food-photography style. Square 1:1 aspect ratio."
    ),
    "B_ajihen_set": (
        "Edit this photo of 'Vege-dashi-soup' (white paper cup with clear vegetable dashi broth "
        "containing eggplant, carrot, daikon, kaiware sprouts) into a product photo featuring "
        "TWO cups side by side: the main vegetable soup cup on the left, and a small white mini cup "
        "(30-50ml size) filled to the brim with pure white soy milk on the right. "
        "The composition should immediately communicate 'a 2-cup flavor-change set'. "
        "Shot from a 30-degree overhead angle on a bright white or light beige tabletop, "
        "with soft natural lighting and gentle shadows. "
        "Warm color palette: red, orange, white tones dominant. "
        "Optionally add a small wooden spoon or dried flower softly in the background. "
        "KEEP the vegetable soup contents (eggplant, carrot, daikon, kaiware, clear broth) "
        "exactly as in the original photo. No text, no logo, no packaging labels. "
        "Natural product photography style, 4:5 portrait aspect ratio."
    ),
    "C_sizzle_closeup": (
        "Edit this photo of 'Vege-dashi-soup' into a magazine-style close-up food photograph "
        "with strong sizzle appeal. "
        "Angle: 45-degree side-overhead view, with the broth surface and vegetables "
        "pushed forward toward the viewer. "
        "Add soft, fluffy white steam rising from the broth. "
        "Lighting: slight backlight to emphasize the transparency of the broth and the steam. "
        "Background: dark wood tabletop with deep bokeh, focus on the vegetables. "
        "KEEP all contents exactly as in the original (eggplant, carrot, daikon, kaiware, clear broth). "
        "No text, no logo. "
        "Warm, atmospheric, premium food magazine aesthetic."
    ),
}

def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def generate(name, prompt, img_b64):
    print(f"\n--- Generating {name} ---")
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                *([{"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}] if img_b64 else []),
            ]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTPError {e.code}: {body[:500]}")
        return None

    saved = []
    for cand in result.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "inline_data" in part or "inlineData" in part:
                inline = part.get("inline_data") or part.get("inlineData")
                img_data = base64.b64decode(inline["data"])
                out_path = os.path.join(OUT_DIR, f"{name}.png")
                with open(out_path, "wb") as f:
                    f.write(img_data)
                saved.append(out_path)
                print(f"Saved: {out_path}")
            elif "text" in part:
                print(f"Text: {part['text'][:200]}")
    if not saved:
        print(f"No image returned for {name}. Raw: {json.dumps(result)[:500]}")
    return saved

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img_b64 = load_image_b64(INPUT_IMAGE) if INPUT_IMAGE else None
    print(f"Input image: {INPUT_IMAGE or '(none: text-only generation)'}")
    for name, prompt in prompts.items():
        generate(name, prompt, img_b64)

if __name__ == "__main__":
    main()
