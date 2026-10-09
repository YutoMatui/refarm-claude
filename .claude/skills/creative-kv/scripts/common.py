from PIL import Image, ImageDraw, ImageFilter
import numpy as np

CREAM = (255, 247, 230, 255)
GOLD = (255, 214, 140, 255)
BROWN = (70, 28, 8, 255)

def shift_up(im, px):
    """絵を上に px ずらし、空いた下は最下段の色で埋める"""
    if px <= 0:
        return im.convert("RGBA")
    w, h = im.size
    a = np.array(im.convert("RGB")).astype(np.float32)
    out = np.zeros_like(a); out[:h - px] = a[px:]
    base = np.median(a[h - 60:h], axis=0)
    for i in range(px):
        out[h - px + i] = base * (1 - 0.04 * (i / max(px, 1)))
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA").filter(ImageFilter.GaussianBlur(0.4))

def fit(im, W, H, shift=0):
    """引き伸ばさず、切り抜いて W:H に合わせる"""
    im = shift_up(im, shift); w, h = im.size
    if w / h > W / H:
        tw = int(h * W / H); im = im.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
    else:
        th = int(w * H / W); off = max(0, (h - th) // 2); im = im.crop((0, off, w, off + th))
    return im.resize((W, H), Image.LANCZOS)

def darken_bands(im, top_frac=0.22, bot_frac=0.19, top_a=90, bot_a=150, color=(80, 30, 0)):
    """上下をうっすら暗くして文字を読ませる"""
    W, H = im.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    th = int(H * top_frac); bh = int(H * bot_frac)
    for i in range(th):
        od.line([(0, i), (W, i)], fill=color + (int(top_a * (1 - i / th) ** 1.6),))
    for i in range(bh):
        od.line([(0, H - bh + i), (W, H - bh + i)], fill=color + (int(bot_a * (i / bh) ** 1.3),))
    return Image.alpha_composite(im, ov)

def text_w(d, txt, f, sp=0):
    return sum(d.textlength(c, font=f) for c in txt) + sp * (len(txt) - 1)

def spaced(d, txt, f, cx, y, fill, sp=0):
    """字間つきで中央揃え"""
    x = cx - text_w(d, txt, f, sp) / 2
    for c in txt:
        d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp

def shadow_text(im, txt, f, cx, y, fill, sp=0, blur=10, alpha=150, off=(0, 6)):
    """縁取りの代わりに、柔らかい影を落として読ませる"""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    spaced(ld, txt, f, cx + off[0], y + off[1], (40, 15, 0, alpha), sp)
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    spaced(ImageDraw.Draw(im, "RGBA"), txt, f, cx, y, fill, sp)

def key_green(path, soft=60):
    """グリーンバックで生成した商品画像を切り抜いて RGBA で返す。
    背景色は縁のピクセルの中央値から推定し、その色との距離でαを決める（緑が暗くてもムラがあっても抜ける）"""
    im = Image.open(path).convert("RGB")
    mw, mh = int(im.size[0] * 0.03), int(im.size[1] * 0.03); im = im.crop((mw, mh, im.size[0] - mw, im.size[1] - mh))  # 縁のゴミを落とす
    a = np.array(im).astype(np.float32); h, w = a.shape[:2]
    border = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
    greenish = (a[..., 1] - np.maximum(a[..., 0], a[..., 2])) > 25     # 緑っぽい画素だけを抜く候補にする
    alpha = np.clip((dist - 35) / soft, 0, 1); alpha = np.where(greenish, alpha, np.maximum(alpha, 0.0))
    alpha = np.where(~greenish & (dist > 35), 1.0, alpha)
    # 緑かぶりを抑える
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    spill = np.clip(g - np.maximum(r, b), 0, None); g2 = g - spill * 0.85
    out = np.stack([r, g2, b, alpha * 255], axis=-1).clip(0, 255).astype(np.uint8)
    im2 = Image.fromarray(out, "RGBA")
    bbox = Image.fromarray((alpha * 255).astype(np.uint8)).point(lambda v: 255 if v > 40 else 0).getbbox()
    return im2.crop(bbox)

def fit_font(d, txt, make_font, max_w, start, min_size=40, sp=0):
    """幅 max_w に収まる最大サイズのフォントを返す"""
    size = start
    while size > min_size and text_w(d, txt, make_font(size), sp) > max_w:
        size -= 6
    return make_font(size)
