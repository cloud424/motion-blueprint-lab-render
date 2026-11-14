#!/usr/bin/env python3
"""EP02 Panama Canal 3-minute PREVIEW. Original vector engineering animations + licensed US Navy actual film.
No publication, no paid voice/video API. Kokoro-82M Apache-2.0 voice (not Grady).
"""
import argparse
import io
import json
import math
import os
import pathlib
import shutil
import subprocess
import sys
import time
import urllib.request

import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont

W,H,FPS=720,1280,12
INK=(19,55,78); BLUE=(36,137,205); TEAL=(7,163,180)
AQUA=(101,203,229); CREAM=(251,254,253); GOLD=(238,171,79)
FONTS='/usr/share/fonts/truetype/dejavu/'
F24=ImageFont.truetype(FONTS+'DejaVuSans.ttf',24)
F26=ImageFont.truetype(FONTS+'DejaVuSans.ttf',26)
F28=ImageFont.truetype(FONTS+'DejaVuSans-Bold.ttf',28)
F34=ImageFont.truetype(FONTS+'DejaVuSans-Bold.ttf',34)
F39=ImageFont.truetype(FONTS+'DejaVuSans-Bold.ttf',39)
F18=ImageFont.truetype(FONTS+'DejaVuSans.ttf',18)
F16=ImageFont.truetype(FONTS+'DejaVuSans.ttf',16)

SCENES=[
 ("THE IMPOSSIBLE CLIMB","How does a cargo ship climb a mountain? The Panama Canal raises enormous ships from sea level to Gatun Lake, about twenty six meters above the ocean. And the secret is water.","26 METERS / NO CRANE", "real"),
 ("A GIANT WATER ELEVATOR","Ships do not need to be lifted by a motorized platform. Instead, they float inside gigantic concrete chambers called locks. Each chamber has gates that control the flow of water.","A WATER ELEVATOR FOR SHIPS", "real"),
 ("THE LOWER CHAMBER","Picture a ship approaching a chamber at the lower water level. The first gates open, allowing it to enter. The water inside is already level with the channel outside, so entry is safe.","LOWER LEVEL / SHIP ENTERS", "cutaway"),
 ("SEAL THE GATES","Once the vessel is inside, the gates close behind it. These powerful paired steel doors form a water tight barrier. Their angled design helps withstand the pressure of the water.","STEEL MITER GATES CLOSE", "gate"),
 ("THE HIDDEN TUNNELS","Now comes the ingenious part. Water from a higher level is admitted through giant culverts in the walls of the original locks. Branching tunnels carry that water beneath the chamber floor.","WATER MOVES UNDER THE FLOOR", "culvert"),
 ("ONE HUNDRED OPENINGS","The original design uses one hundred openings in the floor of each chamber. Spreading the inflow across the floor reduces turbulence. Instead of a single violent jet, the chamber fills in a controlled way.","100 FLOOR OPENINGS", "culvert"),
 ("GRAVITY DOES THE WORK","Why does the water move? Because the supply level is higher than the water inside the lock. The difference in water level creates pressure. Open the valves, and gravity drives water into the chamber.","HIGHER LEVEL = MORE PRESSURE", "pressure"),
 ("THE SHIP FLOATS UP","As the water surface rises, the vessel rises with it. The hull displaces water, and buoyancy supports the ship. No giant crane pulls it upward. The changing water level does the lifting.","BUOYANCY RAISES THE SHIP", "rise"),
 ("EQUALIZE AND OPEN","The chamber keeps filling until its water reaches the next level. Then the inlet valves close. With the water levels equal, the next set of gates can safely swing open, letting the ship proceed.","EQUAL WATER LEVELS", "equal"),
 ("THREE STEPS TO THE LAKE","On the Atlantic side, the original Gatun locks raise a ship in three separate stages. Together, those stages bring the vessel up toward Gatun Lake. A vessel heading the other way descends through the same basic process.","THREE LOCKS / ONE BIG CLIMB", "profile"),
 ("THE REVERSE JOURNEY","For a descent, the system reverses. Water drains from the chamber toward a lower level. The ship gently sinks with the falling surface. These immense changes in elevation are achieved using carefully controlled water.","GOING DOWN: WATER DRAINS", "reverse"),
 ("ENGINEERING BY GRAVITY","The Panama Canal's original locks turn simple physical principles into a global transportation system. Gates, culverts, pressure, and buoyancy work together to move ships across the continent. That's engineering worth understanding.","ENGINEERING EXPLAINED", "real")
]

def ff(cmd):
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode:raise RuntimeError("Command failed "+str(cmd[:4])+" "+p.stderr[-1600:])
 return p.stdout

def download_navy(dest):
 urls=[
 'https://upload.wikimedia.org/wikipedia/commons/a/a2/Continuing_Promise_transits_the_Panama_Canal-ZLIWzvfdisQ-248%2B251.webm',
 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Continuing_Promise_transits_the_Panama_Canal-ZLIWzvfdisQ-248%2B251.webm'
 ]
 for url in urls:
  for attempt in range(3):
   try:
    req=urllib.request.Request(url,headers={'User-Agent':'MotionBlueprintLab/1.0 (scientific video educational production; https://github.com/cloud424/motion-blueprint-lab-render)','Accept':'video/webm,video/*;q=0.9,*/*;q=0.8'})
    with urllib.request.urlopen(req,timeout=70) as src,open(dest,'wb') as out:
     shutil.copyfileobj(src,out)
    if dest.stat().st_size>1000000:
     p=ff(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(dest)])
     if float(p.strip())>20:return True
   except Exception as e:
    print('Navy download attempt failed',type(e).__name__,str(e)[:130],flush=True)
   time.sleep(3*(attempt+1))
 return False

def synthesize_voice(dest,work):
 from kokoro import KPipeline
 pipe=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M')
 chunks=[]; timing=[]; pos=0; sr=24000
 for idx,(title,body,caption,mode) in enumerate(SCENES):
  aud=[]
  for graphemes,phonemes,samples in pipe(body,voice='am_michael',speed=0.96):
   aud.append(np.asarray(samples,dtype=np.float32))
  if not aud:raise RuntimeError('TTS returned empty chapter '+str(idx))
  block=np.concatenate(aud)
  # A short break gives room for moving diagrams to explain the previous step.
  head=np.zeros(int(sr*.5),dtype=np.float32)
  tail=np.zeros(int(sr*1.0),dtype=np.float32)
  whole=np.concatenate([head,block,tail])
  start=pos/sr;pos+=len(whole)
  chunks.append(whole)
  timing.append(dict(index=idx,title=title,start=start,end=pos/sr,caption=caption,mode=mode,words=len(body.split())))
  print('VOICE',idx,title,'seconds',round(len(whole)/sr,1),flush=True)
 voice=np.concatenate(chunks)
 # Avoid an unnaturally long 3+ minute render if TTS speaks much slower than expected.
 sf.write(str(dest),voice,sr)
 (work/'timings.json').write_text(json.dumps(timing,indent=2))
 return timing,len(voice)/sr

def E(x):x=max(0,min(1,x));return x*x*(3-2*x)

def arrow(d,a,b,fill=BLUE,width=6):
 d.line((a,b),fill=fill,width=width)
 ang=math.atan2(b[1]-a[1],b[0]-a[0])
 for delta in [-.45,.45]:
  aa=ang+delta
  d.line((b,(b[0]-17*math.cos(aa),b[1]-17*math.sin(aa))),fill=fill,width=width)

def txt(d,pos,text,font,color=INK):
 d.text(pos,text,font=font,fill=color)

def ship(d,x,y,s=1):
 # y is surface level; hull dips in the water and rides on it.
 x=int(x);y=int(y)
 d.polygon([(x-119*s,y-16*s),(x+116*s,y-16*s),(x+98*s,y+35*s),(x-91*s,y+35*s)],fill=(24,75,105),outline=(15,52,72))
 for k in range(5):
  xx=x-70*s+k*30*s
  d.rounded_rectangle((xx,y-55*s,xx+28*s,y-18*s),radius=2,fill=[(237,143,81),(117,194,218),(227,180,93)][k%3],outline=INK,width=1)
 d.rectangle((x-41*s,y-82*s,x+37*s,y-57*s),fill=(241,248,247),outline=INK,width=2)
 d.line((x+5*s,y-83*s,x+5*s,y-112*s),fill=INK,width=3)

def grid_base(d,progress,scene):
 d.rectangle((0,0,W,H),fill=(248,252,253))
 for x in range(0,W,38):d.line((x,82,x,H),fill=(231,242,245),width=1)
 for y in range(82,H,38):d.line((0,y,W,y),fill=(231,242,245),width=1)
 d.rectangle((0,0,W,94),fill=(229,248,249))
 d.rounded_rectangle((24,20,113,71),radius=12,fill=TEAL)
 txt(d,(36,29),"EP02",F28,"white")
 txt(d,(134,31),"MOTION BLUEPRINT LAB",F26,INK)
 d.rectangle((0,H-69,W,H),fill=(228,247,249))
 txt(d,(23,H-51),"SEE HOW THE WORLD WORKS",F24,INK)
 d.rectangle((20,H-12,700,H-5),fill=(201,226,233))
 d.rectangle((20,H-12,20+680*progress,H-5),fill=TEAL)

def render_graph(im,d,scene_index,localp,t,real):
 # same lock/cross-section across related chapters, with continuously moving mechanisms
 mode=SCENES[scene_index][3]
 x0=102 if not real else 132
 x1=616 if not real else 586
 sy=396 if not real else 776
 floor=924 if not real else 1075
 chamberHigh=sy+103
 chamberLow=floor-180
 barY=sy-32
 if real:
  d.rounded_rectangle((37,720,682,1118),radius=17,fill=(252,254,255),outline=(124,205,220),width=4)
 else:
  d.rounded_rectangle((37,296,682,1048),radius=20,fill=(252,254,255),outline=(124,205,220),width=4)
 level=chamberLow
 if mode in ['rise','culvert','pressure','equal']:level=chamberLow-(chamberLow-chamberHigh)*E(localp)
 if mode=='reverse':level=chamberHigh+(chamberLow-chamberHigh)*E(localp)
 if mode=='profile':level=chamberHigh
 if mode=='gate':level=chamberLow
 d.rectangle((x0,sy,x1,floor),fill=(241,249,252),outline=INK,width=6)
 d.rectangle((x0+5,int(level),x1-5,floor-4),fill=(114,212,233))
 for k in range(5):
  yy=int(level+13+k*32)
  if yy<floor-12:
   off=math.sin(t*2.3+k*2)*4
   d.arc((x0+10,yy+off,x1-10,yy+16+off),0,180,fill=(206,245,253),width=2)
 gateClose=E(localp*2) if mode=='gate' else (1-E((localp-.67)*4) if mode=='equal' else 1)
 for xx in (x0+7,x1-7):
  gw=14
  xx2=xx+(35 if xx==x0+7 else -35)*(1-gateClose)
  d.rectangle((xx2-gw,sy+74,xx2+gw,floor),fill=(230,156,83),outline=(121,93,62),width=2)
 ship(d,(x0+x1)//2,level,0.98 if not real else .72)
 # supply reservoir and culverts in a clearly exposed schematic
 d.rectangle((51,sy+75,x0-12,floor),fill=(214,226,229),outline=(149,178,190),width=2)
 d.rectangle((x1+12,sy+75,669,floor),fill=(214,226,229),outline=(149,178,190),width=2)
 # upper side head line and reference level
 if not real:
  d.line((50,chamberHigh,96,chamberHigh),fill=(13,157,181),width=5)
  d.line((x1+8,chamberLow,666,chamberLow),fill=BLUE,width=5)
  txt(d,(42,chamberHigh-39),"HIGH",F16,TEAL)
  txt(d,(626,chamberLow+8),"LOW",F16,BLUE)
 # hollow underground culvert
 cy=floor+12
 d.rectangle((x0,cy,x1,cy+50),fill=(190,215,222),outline=INK,width=3)
 d.rectangle((x0+2,cy+13,x1-2,cy+32),fill=(102,200,233))
 for xx in (x0+140,x0+290,x0+420):
  if xx>x1-15:continue
  d.rectangle((xx-12,floor-22,xx+13,cy+32),fill=(102,200,233))
  if mode in ('culvert','pressure','rise'):
   wave=(t*95+xx)%98
   arrow(d,(int(x0+20+wave*(x1-x0-80)/98),cy+23),(int(x0+53+wave*(x1-x0-80)/98),cy+23),BLUE,4)
   arrow(d,(xx,cy+12),(xx,floor-23),BLUE,4)
 if mode in ('rise','reverse'):
  arrow(d,(x1+52,level+45),(x1+52,level-42),TEAL if mode=='rise' else GOLD,6)
 if mode=='pressure':
  d.rounded_rectangle((x0+14,sy+12,x1-14,sy+50),radius=6,fill=(228,247,247))
  txt(d,(x0+37,sy+21),"DELTA P = rho g Delta h",F18,INK)
 if mode=='profile':
  for i in range(3):
   by=floor-10-i*74
   d.line((x0+20+i*120,by,x0+145+i*120,by),fill=TEAL,width=12)
   txt(d,(x0+50+i*120,by-29),str(i+1),F18,INK)
 d.rectangle((85,1124,635,1144),fill=(233,246,249))
 txt(d,(85,1156),"ORIGINAL LOCKS • SIMPLIFIED CUTAWAY",F18,(64,112,135))

def draw_frame(t, total,timing,footage_available):
 n=next((i for i,s in enumerate(timing) if t<s['end']),len(timing)-1)
 s=timing[n]
 localp=E((t-s['start'])/max(0.1,s['end']-s['start']))
 mode=s['mode'];real=mode=='real' and footage_available
 im=Image.new('RGB',(W,H),(250,252,254));d=ImageDraw.Draw(im)
 grid_base(d,t/total,n)
 d.rounded_rectangle((22,111,698,173),radius=10,fill=(239,248,250))
 txt(d,(37,118),str(n+1).zfill(2)+" / "+s['title'],F28,INK)
 if real:
  d.rounded_rectangle((28,210,692,648),radius=19,fill='white',outline=(130,202,216),width=4)
  d.rectangle((43,240,677,596),fill=(216,236,242))
  txt(d,(54,604),"ACTUAL PANAMA CANAL FOOTAGE  |  U.S. NAVY",F16,INK)
 else:
  txt(d,(42,202),"ANIMATED ENGINEERING CUTAWAY",F18,(78,143,158))
 render_graph(im,d,n,localp,t,real)
 if not real and mode=='profile':
  txt(d,(108,1035),"26 m IN TOTAL — NOT IN ONE CHAMBER",F18,INK)
 # editorial caption box distinct from narrator lines: clear technical punchline
 d.rounded_rectangle((40,1086 if real else 1076,680,1176),radius=14,fill=(3,126,155))
 cap=s['caption']
 maxlen=35
 words=cap.split();lines=[];line=""
 for word in words:
  if len(line+" "+word)>maxlen and line:lines.append(line);line=word
  else:line=(line+" "+word).strip()
 if line:lines.append(line)
 for i,ln in enumerate(lines[:2]):
  tw=d.textlength(ln,font=F28)
  txt(d,((W-tw)/2,1094+34*i),ln,F28,'white')
 return im,real

def make_music(path,duration):
 sr=24000; N=int(duration*sr)
 t=np.arange(N,dtype=np.float32)/sr
 # Original slowly evolving ambient tones, quiet enough for spoken narrative.
 a=np.zeros(N,dtype=np.float32)
 for i,(hz,amp) in enumerate([(110,0.007),(164.81,0.004),(220,0.003),(329.63,.002)]):
  a+=amp*np.sin(2*np.pi*hz*t+0.35*np.sin(2*np.pi*(.03+i*.008)*t))
 a*=np.minimum(1,t/3)*np.minimum(1,(duration-t)/4)
 sf.write(str(path),a,sr)

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--outdir',default='out')
 args=parser.parse_args()
 out=pathlib.Path(args.outdir)
 out.mkdir(exist_ok=True,parents=True)
 voice=out/'voice_kokoro_preview.wav'
 print('Generating rights-cleared open-weight TTS (NOT Grady), no paid credits',flush=True)
 timing,total=synthesize_voice(voice,out)
 if total<110 or total>190:
  raise ValueError('TTS runtime outside plausible range '+str(total))
 real=out/'usnavy_panama.webm'
 has_real=download_navy(real)
 if not has_real:raise RuntimeError('Real U.S. Navy Panama Canal footage could not be downloaded; refusing a slideshow-like substitute')
 print('REAL FOOTAGE READY',real.stat().st_size,flush=True)
 total=max(total,163)
 print('RENDER START frames',int(total*FPS),'seconds',round(total,2),flush=True)
 frames=out/'_engineering_animation.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','ultrafast','-crf','22','-pix_fmt','yuv420p',str(frames)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i in range(int(total*FPS)):
   im,isreal=draw_frame(i/FPS,total,timing,has_real)
   p.stdin.write(im.tobytes())
   if i%(FPS*30)==0:print('animation sec',i/FPS,flush=True)
  p.stdin.close()
  er=p.stderr.read()
  if p.wait()!=0:raise RuntimeError('ffmpeg raw encode error '+er.decode(errors='ignore')[-1600:])
 finally:
  if p.poll() is None:p.kill()
 music=out/'music_original.wav';make_music(music,total)
 # Overlay authentic, muted US Navy film only during selected real scenes.
 # Preserve 16:9 video within the portrait science layout, not a misleading crop.
 intervals=[s for s in timing if s['mode']=='real']
 condition='+'.join("between(t,{:.2f},{:.2f})".format(s['start'],s['end']-.12) for s in intervals)
 filtergraph=f"[1:v]fps=24,scale=634:356,setsar=1,setpts=PTS-STARTPTS[news];[0:v]fps=24,format=yuv420p[base];[base][news]overlay=43:240:enable='{condition}':shortest=1[video];[2:a]volume=1.0[voice];[3:a]volume=0.8[bg];[voice][bg]amix=inputs=2:duration=longest:normalize=0[audio]"
 final=out/'EP02_PanamaCanal_GravityLocks_3min_Preview_720p.mp4'
 ff(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(frames),'-stream_loop','-1','-i',str(real),'-i',str(voice),'-i',str(music),'-filter_complex',filtergraph,'-map','[video]','-map','[audio]','-c:v','libx264','-preset','veryfast','-crf','24','-r','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t',str(total),'-movflags','+faststart',str(final)])
 # verify real file content with ffprobe and decode
 data=json.loads(ff(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)]))
 vids=[s for s in data['streams'] if s['codec_type']=='video'];auds=[s for s in data['streams'] if s['codec_type']=='audio']
 assert len(vids)==1 and vids[0]['codec_name']=='h264' and vids[0]['width']==W and vids[0]['height']==H
 assert len(auds)==1 and auds[0]['codec_name']=='aac'
 assert 155<float(data['format']['duration'])<191
 finalmeta={'file':final.name,'duration':float(data['format']['duration']),'size':final.stat().st_size,'fps':vids[0]['r_frame_rate'],'narrator':'Kokoro am_michael, Apache 2.0 - NOT Grady','footage':'US Navy public domain, Wikimedia Commons','licensed':True,'publication_approved':False,'chapters':timing}
 (out/'EP02_PanamaCanal_GravityLocks_Preview_Report.json').write_text(json.dumps(finalmeta,indent=2))
 print('SUCCESS',json.dumps({k:finalmeta[k] for k in ['file','duration','size','fps','publication_approved']}),flush=True)

if __name__=='__main__':main()
