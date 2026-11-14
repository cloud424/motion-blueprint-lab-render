#!/usr/bin/env python3
"""EP02 R2 candidate renderer: 9 different moving lock-mechanism scenes.
Private QA only. Reuses the licensed US Navy preview input and open-weight Kokoro.
Does not publish or grant copyright/visual QA approval.
"""
import json
import math
import pathlib
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw
import render_EP02_pilot as base

W, H = base.W, base.H
C = base.INK
CYAN = base.TEAL
BLUE = base.BLUE
LIGHT = (105,202,228)
DARK = (23,87,118)
SAND = (232,168,87)

def word(d, xy, s, font=None, color=None):
    d.text(xy, str(s), font=font or base.F24, fill=color or C)

def panel(d, y0=267, y1=954, fill=(248,253,253)):
    d.rounded_rectangle((40,y0,680,y1),radius=16,fill=fill,
                         outline=(118,197,210),width=4)

def arrow(d,x0,y0,x1,y1,color=BLUE,width=6):
    d.line((x0,y0,x1,y1),fill=color,width=width)
    angle=math.atan2(y1-y0,x1-x0)
    for delta in (-.46,.46):
        a=angle+delta
        d.line((x1,y1,x1-18*math.cos(a),y1-18*math.sin(a)),fill=color,width=width)

def label(d,s,sub=""):
    word(d,(64,282),s,base.F26,C)
    if sub: word(d,(64,322),sub,base.F18,(60,125,140))

def top_ship(d,x,y):
    d.polygon([(x,y-80),(x+49,y-32),(x+49,y+71),(x-49,y+71),(x-49,y-32)],
              fill=(21,83,115),outline=C)
    d.rectangle((x-29,y-32,x+29,y+29),fill=(248,249,244))
    for j in range(4):
        d.rectangle((x-34,y-19+j*20,x+34,y-9+j*20),
                    fill=[(238,160,94),(118,192,208),(238,209,111)][j%3])

def mechanism(d,idx,u,t):
    panel(d)
    if idx==2:
        label(d,"TOP VIEW / ENTER THE LOCK","SHIP APPROACHES  -  GATES CLOSE  -  CHAMBER SEALED")
        d.rounded_rectangle((147,390,573,870),radius=9,fill=(142,215,231),outline=C,width=7)
        d.rectangle((152,407,568,848),fill=(118,201,225))
        x=360; y=390+270*base.E(u)
        top_ship(d,x,y)
        k=min(1,u*1.6)
        d.line((151,817,360-212*(1-k),817-52*k),fill=SAND,width=14)
        d.line((569,817,360+212*(1-k),817-52*k),fill=SAND,width=14)
        arrow(d,361,377,361,448,CYAN)
        word(d,(177,902),"CONTROLLED ENTRY / MOVING VESSEL",base.F18)
    elif idx==3:
        label(d,"V-SHAPED MITER GATES","CLOSE-UP: SWINGING STEEL LEAVES AND PRESSURE")
        d.rectangle((98,393,622,683),fill=(155,216,233),outline=C,width=6)
        word(d,(125,417),"UPSTREAM WATER",base.F18)
        k=base.E(u)
        left_end=(355-170*(1-k),560-145*k)
        right_end=(365+170*(1-k),560-145*k)
        d.line(((99,602),left_end),fill=SAND,width=23)
        d.line(((621,602),right_end),fill=SAND,width=23)
        for hx in (98,622):
            d.ellipse((hx-15,586,hx+15,616),fill=DARK)
        arrow(d,360,440,360,518,BLUE)
        d.rounded_rectangle((92,728,628,908),radius=12,fill=(231,246,248))
        d.rectangle((360,755,386,878),fill=SAND)
        for y in (780,821,862):
            arrow(d,162,y,333,y,BLUE,4)
        word(d,(420,791),"STEEL",base.F24)
        word(d,(420,827),"GATE",base.F24)
    elif idx==4:
        label(d,"SIDE CUTAWAY / CULVERT VALVES","WATER ENTERS FROM A HIGHER LEVEL")
        d.rectangle((94,389,255,732),fill=(224,239,241),outline=C,width=4)
        d.rectangle((99,458,251,727),fill=(104,198,224))
        d.rectangle((311,475,620,733),fill=(225,244,249),outline=C,width=5)
        d.rectangle((316,640-int(80*u),616,728),fill=(109,205,228))
        word(d,(113,416),"HIGH",base.F24)
        word(d,(443,426),"LOCK",base.F24)
        d.rectangle((177,753,567,815),fill=(188,216,223),outline=C,width=3)
        d.rectangle((181,773,561,797),fill=(113,203,232))
        for xx in (370,449,535):
            d.rectangle((xx-10,722,xx+10,792),fill=LIGHT)
            arrow(d,xx,767,xx,692,BLUE,4)
        for xx in (225,313,403):
            arrow(d,xx+int(35*(t%1)),784,xx+40+int(35*(t%1)),784,BLUE,4)
        word(d,(118,849),"HIDDEN PIPE NETWORK",base.F24)
        word(d,(118,886),"TRUNK CULVERT + FLOOR BRANCHES",base.F18)
    elif idx==5:
        label(d,"FLOOR PLAN / 100 OPENINGS","DISTRIBUTED INLET HOLES REDUCE TURBULENCE")
        d.rectangle((91,388,629,886),fill=(221,242,247),outline=C,width=5)
        active=int(u*100)
        for j in range(10):
            for k in range(10):
                x=123+k*53;y=425+j*45;num=j*10+k
                cc=CYAN if num<active else (175,209,218)
                rr=7+int(3*max(0,math.sin(t*4+j*.4)) if num<active else 0)
                d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=cc,outline=DARK)
        d.rounded_rectangle((208,891,530,931),radius=7,fill=(231,248,249))
        word(d,(227,897),f"{active:03d} / 100 PORTS ACTIVE",base.F18)
    elif idx==6:
        label(d,"WHY WATER FLOWS: GRAVITY","THE HYDROSTATIC HEAD CREATES PRESSURE")
        d.rectangle((107,413,302,785),outline=C,width=6,fill=(236,248,249))
        d.rectangle((414,413,607,785),outline=C,width=6,fill=(236,248,249))
        high=492;low=698-int(u*52)
        d.rectangle((112,high,297,779),fill=LIGHT)
        d.rectangle((419,low,602,779),fill=LIGHT)
        d.rectangle((223,778,503,811),fill=(95,194,220),outline=C,width=3)
        arrow(d,305,580,408,580,CYAN)
        word(d,(144,372),"UPSTREAM",base.F18)
        word(d,(447,372),"CHAMBER",base.F18)
        d.line((353,high,353,low),fill=SAND,width=4)
        arrow(d,359,high+14,359,low-12,SAND)
        word(d,(375,601),"h",base.F28,SAND)
        word(d,(132,848),"PRESSURE DIFFERENCE",base.F24)
        word(d,(144,886),"Delta P = density x gravity x height",base.F18)
    elif idx==7:
        label(d,"BUOYANCY / FORCES ON A SHIP","THE SHIP RISES WITH THE WATER SURFACE")
        water_y=741-int(170*base.E(u))
        d.rectangle((94,422,628,869),fill=(237,249,251),outline=C,width=5)
        d.rectangle((98,water_y,624,865),fill=LIGHT)
        base.ship(d,361,water_y,1.05)
        arrow(d,355,water_y+102,355,water_y-105,CYAN,8)
        arrow(d,470,water_y-135,470,water_y+36,SAND,8)
        word(d,(139,437),"UPWARD BUOYANCY",base.F18,CYAN)
        word(d,(448,463),"WEIGHT",base.F18,SAND)
        word(d,(103,909),"THE HULL DISPLACES WATER",base.F24)
    elif idx==8:
        label(d,"EQUALIZE FIRST. OPEN SECOND.","EQUAL WATER LEVELS REMOVE THE HEAD DIFFERENCE")
        d.rectangle((92,412,303,711),fill=(242,251,251),outline=C,width=5)
        d.rectangle((417,412,628,711),fill=(242,251,251),outline=C,width=5)
        yy=535+int((1-u)*80)
        d.rectangle((97,yy,298,706),fill=LIGHT)
        d.rectangle((422,535,623,706),fill=LIGHT)
        word(d,(137,380),"CHAMBER",base.F18)
        word(d,(463,380),"NEXT LEVEL",base.F18)
        word(d,(346,505),"=",base.F34,CYAN)
        k=base.E(max(0,(u-.38)/.62))
        d.rectangle((95,770,625,919),fill=(160,222,233),outline=C,width=4)
        d.line((103,883,355-190*k,806+66*k),fill=SAND,width=14)
        d.line((617,883,365+190*k,806+66*k),fill=SAND,width=14)
        word(d,(213,927),"ONLY OPEN WHEN LEVELS MATCH",base.F18)
    elif idx==9:
        label(d,"THREE STAGES / ONE CLIMB","THE ORIGINAL ATLANTIC-SIDE GATUN LOCKS")
        d.line((102,837,620,444),fill=(130,161,174),width=8)
        for i in range(3):
            xx=130+i*151; yy=796-i*113
            d.rectangle((xx,yy-12,xx+118,yy+60),fill=(124,208,228),outline=C,width=3)
            word(d,(xx+42,yy+21),str(i+1),base.F24,C)
        step=min(2,int(u*3))
        xx=181+step*151; yy=785-step*113
        top_ship(d,xx,yy-80)
        arrow(d,143,817,544,465,CYAN,6)
        word(d,(390,492),"GATUN LAKE",base.F18)
        word(d,(111,910),"ABOUT 26 METERS ABOVE SEA LEVEL",base.F18)
    elif idx==10:
        label(d,"THE REVERSE JOURNEY","ASCENT ADDS WATER / DESCENT DRAINS IT")
        for j,x0 in enumerate((86,397)):
            d.rectangle((x0,424,x0+230,837),fill=(236,249,249),outline=C,width=5)
            level=(698-150*u) if j==0 else (552+150*u)
            d.rectangle((x0+5,level,x0+225,831),fill=LIGHT)
            base.ship(d,x0+114,level,.65)
            if j==0:arrow(d,x0+192,744,x0+192,572,CYAN,7)
            else:arrow(d,x0+192,568,x0+192,735,SAND,7)
            word(d,(x0+48,871),"UPBOUND" if j==0 else "DOWNBOUND",base.F18)
        word(d,(113,919),"SAME CHAMBER  /  OPPOSITE FLOW",base.F18)

def faster_voice(dest,work):
    from kokoro import KPipeline
    pipe=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M')
    sr=24000; blocks=[]; timing=[]; cursor=0
    for i,(title,body,caption,mode) in enumerate(base.SCENES):
        pieces=[]
        for gr,ph,samples in pipe(body,voice='am_michael',speed=1.09):
            pieces.append(np.asarray(samples,dtype=np.float32))
        if not pieces: raise RuntimeError("empty voice section "+str(i))
        seg=np.concatenate([np.zeros(int(sr*.5),dtype=np.float32),
                            np.concatenate(pieces),np.zeros(sr,dtype=np.float32)])
        start=cursor/sr;cursor+=len(seg)
        blocks.append(seg)
        timing.append(dict(index=i,title=title,start=start,end=cursor/sr,
                           caption=caption,mode=mode,words=len(body.split())))
        print("R2 VOICE",i,round(len(seg)/sr,2),flush=True)
    sf.write(str(dest),np.concatenate(blocks),sr)
    (work/'timings.json').write_text(json.dumps(timing,indent=2))
    return timing,cursor/sr

def draw_frame(t,total,timing,footage_available):
    idx=next((i for i,x in enumerate(timing) if t<x['end']),len(timing)-1)
    chapter=timing[idx]
    u=base.E((t-chapter['start'])/max(.1,chapter['end']-chapter['start']))
    isreal=base.SCENES[idx][3]=='real' and footage_available
    im=Image.new('RGB',(W,H),(250,252,254));d=ImageDraw.Draw(im)
    base.grid_base(d,t/total,idx)
    d.rounded_rectangle((22,110,698,176),radius=10,fill=(228,247,249))
    word(d,(36,127),f"{idx+1:02d} / {chapter['title']}",base.F28,C)
    if isreal:
        d.rounded_rectangle((28,209,692,649),radius=19,fill='white',outline=(130,202,216),width=4)
        d.rectangle((43,240,677,596),fill=(214,232,239))
        word(d,(52,607),"AUTHENTIC CANAL FOOTAGE  |  U.S. NAVY",base.F16,C)
        base.render_graph(im,d,idx,u,t,True)
    else:
        mechanism(d,idx,u,t)
    body=base.SCENES[idx][1].split()
    chunks=[' '.join(body[j:j+8]) for j in range(0,len(body),8)]
    ci=min(len(chunks)-1,int(u*len(chunks)))
    sub=chunks[ci]
    d.rounded_rectangle((39,980,681,1064),radius=12,fill=(227,247,249),outline=(127,196,207),width=2)
    if len(sub)>43:
        pivot=sub.rfind(' ',0,43)
        first,second=sub[:pivot],sub[pivot+1:]
    else:first,second=sub,""
    word(d,(60,992),first,base.F24,C)
    if second:word(d,(60,1025),second,base.F24,C)
    d.rounded_rectangle((40,1086,680,1176),radius=13,fill=(3,126,155))
    cap=chapter['caption'];maxlen=35;lines=[];s=""
    for wordpart in cap.split():
        if len(s+' '+wordpart)>maxlen and s:lines.append(s);s=wordpart
        else:s=(s+' '+wordpart).strip()
    if s:lines.append(s)
    for j,ln in enumerate(lines[:2]):
        width=d.textlength(ln,font=base.F28)
        word(d,((W-width)/2,1098+35*j),ln,base.F28,'white')
    return im,isreal

base.synthesize_voice=faster_voice
base.draw_frame=draw_frame

if __name__ == '__main__':
    base.main()
