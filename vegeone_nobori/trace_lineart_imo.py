"""白線画（黒地）PNG → 4分割 → 各パーツを SVG パス(evenodd)に。lineart_paths.json に追記"""
import cv2, json, numpy as np
from PIL import Image
src=r"..\shodaisai_images\lineart_imo.png"
im=np.array(Image.open(src).convert("L")); h,w=im.shape
cells={"sweetpotato":(0,0),"pumpkin":(1,0),"onion2":(0,1),"mapleleaf":(1,1)}
d=json.load(open("img_candidates/lineart_paths.json"))
for name,(cx,cy) in cells.items():
    tile=im[cy*h//2:(cy+1)*h//2, cx*w//2:(cx+1)*w//2]
    big=cv2.resize(tile,None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC)
    _,bw=cv2.threshold(big,128,255,cv2.THRESH_BINARY)
    ys,xs=np.where(bw>0); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    bw=bw[y0:y1+1,x0:x1+1]
    cs,_=cv2.findContours(bw,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_TC89_KCOS)
    parts=[]
    for c in cs:
        if cv2.contourArea(c)<60: continue
        c=cv2.approxPolyDP(c,1.2,True).reshape(-1,2)
        parts.append("M"+" L".join(f"{x},{y}" for x,y in c)+"Z")
    d[name]={"w":int(bw.shape[1]),"h":int(bw.shape[0]),"d":" ".join(parts)}
    print(name,bw.shape,len(parts))
json.dump(d,open("img_candidates/lineart_paths.json","w"))
