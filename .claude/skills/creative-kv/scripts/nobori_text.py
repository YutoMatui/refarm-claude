"""文字主体ののぼり（たい焼きのぼりの構造を、学祭向けの明るい配色で）"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, sys, json
from common import text_w, key_green
from fonts import font
"""使い方: python nobori_text.py config.json 出力名 [orange|cream]  （config の nobori_text: {main, badge, sub, price_line, product_images:[...]}）"""
import os
F=os.environ.get("WINDIR","C:/Windows")+"/Fonts/"
def gUB(s):
    for n in ("HGRGE.TTC","YuGothB.ttc","meiryob.ttc"):
        if os.path.exists(F+n): return ImageFont.truetype(F+n,s)
    return font("pop",s)
book=lambda s: font("serif_en",s); kyo=lambda s: font("kyokasho",s)
W,H=1200,3600
cfg=json.load(open(sys.argv[1],encoding="utf-8")); outp=sys.argv[2]; variant=sys.argv[3] if len(sys.argv)>3 else "orange"
nt=cfg.get("nobori_text",{})
MAIN=nt.get("main",cfg["items"][0]["name"]); BADGE=nt.get("badge",cfg["items"][0].get("desc","")); SUB=nt.get("sub",cfg["items"][1]["name"] if len(cfg["items"])>1 else "")
PRICE=nt.get("price_line"," ／ ".join(i["price"].replace("¥","")+"円" for i in cfg["items"] if i.get("price")))
IMGS=nt.get("product_images",[])
if variant=="orange":
    top,bot=(214,92,20),(240,140,40); ink=(255,250,240,255); accent=(255,236,160,255); badge_bg=(255,250,240,255); badge_fg=(190,50,30,255)
else:  # cream
    top,bot=(252,244,228),(246,222,180); ink=(150,52,18,255); accent=(200,90,30,255); badge_bg=(200,60,35,255); badge_fg=(255,250,240,255)
a=np.zeros((H,W,3),np.float32)
for y in range(H):
    t=y/H; a[y]=np.array(top)*(1-t)+np.array(bot)*t
im=Image.fromarray(a.astype(np.uint8)).convert("RGBA"); d=ImageDraw.Draw(im,"RGBA")
def vtext(txt,f,cx,y,fill,gap=0,shadow=True):
    for c in txt:
        if c in "ー－":
            tmp=Image.new("RGBA",(f.size*2,f.size*2),(0,0,0,0)); ImageDraw.Draw(tmp).text((f.size//2,f.size//4),c,font=f,fill=fill)
            tmp=tmp.rotate(-90,resample=Image.BICUBIC); tmp=tmp.crop(tmp.getbbox()); im.alpha_composite(tmp,(int(cx-tmp.size[0]/2),int(y+(f.size-tmp.size[1])/2))); y+=f.size+gap; continue
        w=d.textlength(c,font=f)
        if shadow:
            layer=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(layer).text((cx-w/2+4,y+8),c,font=f,fill=(60,20,0,110)); im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(8)))
        ImageDraw.Draw(im,"RGBA").text((cx-w/2,y),c,font=f,fill=fill); y+=f.size+gap
    return y
# 主文：揚げたて大学芋（極太ゴシック・白）
f_main=gUB(230)
vtext(MAIN,f_main,W*0.60,210,ink,gap=-6)
# 帯バッジ：ホイップかけ放題（縦）
bx,by,bw,bh=int(W*0.19),200,150,900
d.rounded_rectangle([bx,by,bx+bw,by+bh],radius=20,fill=badge_bg)
vtext(BADGE,gUB(86),bx+bw/2,by+40,badge_fg,gap=6,shadow=False)
# 副文：極 焼き芋スープ（縦・中サイズ）
vtext(SUB,gUB(120),W*0.19,1230,ink,gap=4)
# 下：商品写真（切り抜き）＋ ブランド
cuts=[key_green(p) for p in IMGS]
def place(cut,wd,cx,bottom):
    r=wd/cut.size[0]; c=cut.resize((int(cut.size[0]*r),int(cut.size[1]*r)),Image.LANCZOS)
    sh=Image.new("RGBA",(c.size[0]+160,200),(0,0,0,0)); ImageDraw.Draw(sh).ellipse([80,40,c.size[0]+80,160],fill=(60,20,0,120)); sh=sh.filter(ImageFilter.GaussianBlur(22))
    im.alpha_composite(sh,(int(cx-sh.size[0]/2),int(bottom-110))); im.alpha_composite(c,(int(cx-c.size[0]/2),int(bottom-c.size[1])))
if len(cuts)>=2: place(cuts[1],520,W*0.68,3080); place(cuts[0],620,W*0.36,3130)
elif cuts: place(cuts[0],700,W*0.5,3120)
d=ImageDraw.Draw(im,"RGBA")
def hcenter(txt,f,y,fill,sp=0):
    x=W/2-text_w(d,txt,f,sp)/2
    for c in txt: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
hcenter(PRICE,gUB(80),3180,ink,4)
hcenter(cfg["brand"],book(84),3330,ink,16); hcenter(cfg.get("by",""),kyo(44),3440,ink,6)
out=im.convert("RGB"); out.resize((2362,7087),Image.LANCZOS).save(f"{outp}_{variant}_100dpi.jpg",quality=92,dpi=(100,100))
out.resize((600,1800),Image.LANCZOS).save(f"{outp}_{variant}_preview.jpg",quality=90); print("ok",variant)
