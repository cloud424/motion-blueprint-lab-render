#!/usr/bin/env python3
"""Motion Blueprint Lab original EP02 safe engineering-animation preview.
This renderer NEVER publishes a video or approves a source license.
"""
import argparse
import json
import math
import pathlib
import subprocess
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=720,1280,24
BG=(247,253,254); INK=(22,67,88); WATER=(82,189,218); LIGHT=(218,243,248)

def font(size,bold=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf"
    return ImageFont.truetype(p,size)

def clamp(x):
    return max(0.0,min(1.0,x))

def ease(x):
    x=clamp(x)
    return x*x*(3-2*x)

def draw(t,duration,ep):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    for x in range(0,W,36):d.line((x,0,x,H),fill=(229,245,248))
    for y in range(0,H,36):d.line((0,y,W,y),fill=(229,245,248))
    d.rounded_rectangle((18,18,118,72),radius=12,fill=(0,165,177))
    d.text((37,29),ep,font=font(23,True),fill="white")
    d.text((136,35),"MOTION BLUEPRINT LAB",font=font(21,True),fill=INK)
    d.text((35,120),"THE PANAMA CANAL",font=font(34,True),fill=INK)
    d.text((35,171),"THE GRAVITY-POWERED LOCK",font=font(22,True),fill=(27,117,148))
    d.rounded_rectangle((25,245,695,1010),radius=22,fill="white",outline=(137,210,220),width=4)
    phase=t/duration
    if phase<.18:label="1  SHIP ENTERS THE LOCK"
    elif phase<.34:label="2  GATES CLOSE"
    elif phase<.76:label="3  GRAVITY FILLS THE CHAMBER"
    else:label="4  WATER LEVELS MATCH"
    d.text((49,277),label,font=font(20,True),fill=INK)
    left,right=149,568
    floor=839
    level=718-171*ease((phase-.32)/.45)
    d.rectangle((left,339,right,floor),fill=(241,251,253),outline=INK,width=6)
    d.rectangle((left+4,round(level),right-4,floor-4),fill=WATER)
    for k in range(7):
        y=round(level+18+k*33)
        if y<floor-4:
            wav=math.sin(t*3+k)*6
            d.arc((left+13,y+wav,right-13,y+wav+19),0,180,fill=(181,244,254),width=3)
    d.rectangle((left-32,336,left-2,855),fill=(165,200,210),outline=INK,width=3)
    d.rectangle((right+2,336,right+32,855),fill=(165,200,210),outline=INK,width=3)
    for xx in (left+6,right-9):
        if .18<=phase<.86:
            d.rectangle((xx-7,430,xx+8,845),fill=(255,159,79))
        else:
            d.rectangle((xx-26,430,xx-10,845),fill=(255,159,79))
    deck=round(level)-85
    d.polygon([(213,deck+58),(516,deck+58),(490,deck+100),(236,deck+100)],fill=(24,104,137),outline=INK)
    d.rectangle((255,deck+15,447,deck+56),fill=(245,252,255),outline=INK,width=3)
    d.rectangle((454,deck+25,479,deck+55),fill=(248,193,89),outline=INK,width=2)
    d.line((313,deck+8,313,deck-28),fill=INK,width=4)
    d.text((270,deck+66),"CONTAINER SHIP",font=font(14,True),fill="white")
    d.rectangle((79,862,650,909),fill=LIGHT,outline=INK,width=3)
    d.rectangle((80,876,648,895),fill=WATER)
    for xx in (281,421):
        d.rectangle((xx,819,xx+29,894),fill=WATER)
        if .33<phase<.76:
            d.line((xx+15,866,xx+15,826),fill=(5,113,190),width=7)
            d.polygon([(xx+5,839),(xx+15,825),(xx+25,839)],fill=(5,113,190))
    d.text((207,923),"UNDERGROUND WATER TUNNELS",font=font(17,True),fill=INK)
    d.text((38,1041),"NO PUMPS NEEDED",font=font(27,True),fill=(0,148,167))
    d.text((38,1090),"WATER MOVES BY GRAVITY",font=font(21),fill=INK)
    d.rounded_rectangle((28,1181,692,1252),radius=12,fill=(239,247,247))
    d.text((42,1200),"TECHNICAL TEST • NOT FOR PUBLICATION",font=font(19,True),fill=(172,58,47))
    return im

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",required=True)
    p.add_argument("--outdir",default="out")
    p.add_argument("--duration",type=float,default=2.0)
    p.add_argument("--test-only",action="store_true")
    a=p.parse_args()
    obj=json.loads(pathlib.Path(a.episode).read_text(encoding="utf-8"))
    ep=obj["episode"]
    if not ep.startswith("EP") or not ep[2:].isdigit() or not pathlib.Path(a.episode).name.startswith(ep+"_"):
        raise ValueError("Invalid EP manifest")
    if not a.test_only:raise RuntimeError("Only safe previews are enabled. Full rendering and publishing are not integrated.")
    out=pathlib.Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    dest=out/(ep+"_"+obj["slug"]+"_TechnicalTest.mp4")
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-crf","24","-movflags","+faststart",str(dest)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(max(1,int(a.duration*FPS))):
            proc.stdin.write(draw(n/FPS,a.duration,ep).tobytes())
        proc.stdin.close()
        err=proc.stderr.read()
        if proc.wait()!=0:raise RuntimeError(err.decode(errors="replace")[-1500:])
    finally:
        if proc.poll() is None:proc.kill()
    print(json.dumps({"episode":ep,"preview":str(dest),"frames":int(a.duration*FPS),"approved":False}))

if __name__=="__main__":main()
