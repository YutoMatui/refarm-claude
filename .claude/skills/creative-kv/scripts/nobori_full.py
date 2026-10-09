"""写真フルブリード型のぼり（スタバのストロベリーバナーの構造）。 python nobori_full.py base_9x16.png 出力名"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
"""使い方: python nobori_full.py config.json base_9x16.png 出力名  （config の nobori_full: {script, main, sub, price_line}）"""
import numpy as np, sys, json, os
from common import text_w
from fonts import font
F=os.environ.get("WINDIR","C:/Windows")+"/Fonts/"
def _f(names,kind,s):
    for n in names:
        if os.path.exists(F+n): return ImageFont.truetype(F+n,s)
    return font(kind,s)
gab=lambda s: _f(["Gabriola.ttf","FRSCRIPT.TTF","BRUSHSCI.TTF"],"serif_en",s); gUB=lambda s: _f(["HGRGE.TTC","YuGothB.ttc"],"pop",s)
book=lambda s: font("serif_en",s); kyo=lambda s: font("kyokasho",s)
W,H=1200,3600
cfg=json.load(open(sys.argv[1],encoding="utf-8")); src=Image.open(sys.argv[2]).convert("RGB"); outp=sys.argv[3]
nf=cfg.get("nobori_full",{})
SCRIPT=nf.get("script","Daigaku-imo"); MAIN=nf.get("main",cfg["items"][0]["name"]); SUB=nf.get("sub",""); PRICE=nf.get("price_line","")
base=src.resize((W,int(src.size[1]*W/src.size[0])),Image.LANCZOS); bh=base.size[1]
pad=(H-bh)//2
top=ImageOps.flip(base.crop((0,0,W,pad))).filter(ImageFilter.GaussianBlur(26))
bot=ImageOps.flip(base.crop((0,bh-(H-bh-pad),W,bh))).filter(ImageFilter.GaussianBlur(26))
canvas=Image.new("RGB",(W,H)); canvas.paste(top,(0,0)); canvas.paste(base,(0,pad)); canvas.paste(bot,(0,pad+bh))
canvas=canvas.convert("RGBA")
# 上下を少し暗くして文字を読ませる
ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
for i in range(520): od.line([(0,i),(W,i)],fill=(70,25,0,int(150*(1-i/520)**1.4)))
for i in range(760): od.line([(0,H-760+i),(W,H-760+i)],fill=(70,25,0,int(190*(i/760)**1.3)))
canvas=Image.alpha_composite(canvas,ov); d=ImageDraw.Draw(canvas,"RGBA")
CREAM=(255,247,230,255)
def shadow(txt,f,cx,y,fill,sp=0,blur=14,alpha=170):
    layer=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(layer); x=cx-text_w(ld,txt,f,sp)/2
    for c in txt: ld.text((x,y+8),c,font=f,fill=(50,15,0,alpha)); x+=ld.textlength(c,font=f)+sp
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    dd=ImageDraw.Draw(canvas,"RGBA"); x=cx-text_w(dd,txt,f,sp)/2
    for c in txt: dd.text((x,y),c,font=f,fill=fill); x+=dd.textlength(c,font=f)+sp
shadow(cfg["brand"],book(96),W/2,110,CREAM,18)
shadow(cfg.get("by",""),kyo(40),W/2,235,CREAM,6,blur=8)
_sz=330
while _sz>120 and text_w(ImageDraw.Draw(canvas),SCRIPT,gab(_sz))>W-120: _sz-=10
shadow(SCRIPT,gab(_sz),W/2,H-930+(330-_sz)//2,CREAM,0,blur=18)
shadow(MAIN,gUB(118),W/2,H-520,CREAM,6)
if SUB: shadow(SUB,gUB(60),W/2,H-350,CREAM,4,blur=10)
if PRICE: shadow(PRICE,gUB(70),W/2,H-230,CREAM,4,blur=10)
out=canvas.convert("RGB"); out.resize((2362,7087),Image.LANCZOS).save(f"{outp}_100dpi.jpg",quality=92,dpi=(100,100))
out.resize((600,1800),Image.LANCZOS).save(f"{outp}_preview.jpg",quality=90); print("ok")
