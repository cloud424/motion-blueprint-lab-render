#!/usr/bin/env python3
"""EP02 Panama Canal R2 multiview original animations + licensed US Navy real film.
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

def layout_panel(d,title,subtitle=''):
 d.rounded_rectangle((38,297,682,1048),radius=18,fill=(253,254,255),outline=(120,205,217),width=4)
 txt(d,(57,314),title,F24,TEAL)
 if subtitle:txt(d,(58,352),subtitle,F16,INK)

def label_panel(d,y,title,subtitle):
 d.rounded_rectangle((64,y,660,y+75),radius=11,fill=(226,249,248))
 txt(d,(80,y+8),title,F24,INK)
 txt(d,(80,y+43),subtitle,F18,(57,113,134))

def render_graph(im,d,scene_index,p,t,real):
 mode=SCENES[scene_index][3]
 if real:
  d.rounded_rectangle((36,715,684,1085),radius=17,fill=(253,254,255),outline=(123,206,217),width=4)
  d.rectangle((108,780,615,976),fill=(232,242,245),outline=INK,width=4)
  lv=843+int(23*math.sin(t*.18))
  d.rectangle((114,lv,608,972),fill=(107,201,224))
  ship(d,366,lv,.64)
  d.rectangle((104,792,118,973),fill=GOLD)
  d.rectangle((607,792,620,973),fill=GOLD)
  txt(d,(75,1022),"REAL FILM + ORIGINAL ENGINEERING EXPLANATION",F16,INK)
  return
 if mode=='cutaway':
  layout_panel(d,'TOP VIEW / ENTERING THE LOCK','Ship advances into the chamber before gates seal')
  d.rounded_rectangle((174,413,550,890),radius=9,fill=(229,246,249),outline=INK,width=6)
  d.rectangle((180,418,544,884),fill=(107,206,230))
  for k in range(10):
   yy=440+k*44
   d.arc((211,yy,511,yy+19),0,180,fill=(214,248,250),width=2)
  yy=750-217*E(p)
  d.polygon([(360,yy-78),(299,yy-10),(299,yy+92),(421,yy+92),(421,yy-10)],fill=(31,80,117),outline=INK)
  for x in (330,365,393):
   d.rectangle((x,yy+8,x+23,yy+30),fill=GOLD,outline=INK,width=2)
  for x in (175,546):
   d.ellipse((x-8,411,x+8,427),fill=INK)
   d.ellipse((x-8,876,x+8,892),fill=INK)
  d.line((180,425,365,431),fill=GOLD,width=12)
  d.line((544,425,365,431),fill=GOLD,width=12)
  d.line((180,880,360,876),fill=GOLD,width=12)
  d.line((544,880,360,876),fill=GOLD,width=12)
  label_panel(d,947,'1 ENTER  /  2 CLOSE  /  3 FILL','An entire ship fits inside the water chamber')
 elif mode=='gate':
  layout_panel(d,'MITER GATES / MOVING STEEL LEAVES','Top view / two hinged gate leaves')
  d.rectangle((125,444,594,730),fill=(136,207,227),outline=INK,width=5)
  d.ellipse((139,466,160,487),fill=INK);d.ellipse((557,466,578,487),fill=INK)
  a=.18+1.23*E(p)
  left=(150+200*math.cos(a),477+180*math.sin(a))
  right=(568-200*math.cos(a),477+180*math.sin(a))
  d.line((150,477,left[0],left[1]),fill=GOLD,width=13)
  d.line((568,477,right[0],right[1]),fill=GOLD,width=13)
  d.arc((131,456,343,672),10,88,fill=INK,width=3)
  d.arc((378,456,589,672),92,169,fill=INK,width=3)
  txt(d,(133,778),"HINGES ROTATE TO CLOSE THE SEAL",F18,INK)
  d.rounded_rectangle((95,821,622,928),radius=12,fill=(228,247,248),outline=(109,188,200),width=2)
  arrow(d,(140,877),(296,877),BLUE,5)
  d.rectangle((311,846,333,910),fill=GOLD)
  txt(d,(352,853),"HIGH WATER PRESSURE",F18,INK)
  txt(d,(353,885),"ACTS ON THE CLOSED GATES",F16,INK)
  label_panel(d,951,'TWO MOVING LEAVES','Geometry lets the closed gates resist pressure')
 elif mode=='culvert' and scene_index==4:
  layout_panel(d,'HIDDEN CULVERT NETWORK','Side cutaway / water enters beneath the lock')
  d.rectangle((76,444,246,854),fill=(113,210,230),outline=INK,width=4)
  d.rectangle((247,443,626,856),fill=(242,250,252),outline=INK,width=5)
  d.rectangle((254,710,619,846),fill=(106,207,228))
  d.rectangle((100,868,609,915),fill=(185,220,228),outline=INK,width=3)
  d.rectangle((101,883,610,903),fill=(105,203,231))
  ship(d,446,710,.65)
  arrow(d,(158,893),(386,893),TEAL,8)
  for i in range(4):
   x=289+91*i
   d.rectangle((x-10,829,x+11,888),fill=(105,206,232))
   wave=(t*.42+i*.15)%1
   arrow(d,(x,865-int(wave*19)),(x,825-int(wave*10)),BLUE,5)
  txt(d,(104,945),"FLOW UNDER THE FLOOR",F24,INK)
  label_panel(d,973,'GRAVITY FED','Higher reservoir feeds branched floor openings')
 elif mode=='culvert':
  layout_panel(d,'100 FLOOR OPENINGS / UNIFORM FILL','Plan view / a distributed inlet grid')
  d.rounded_rectangle((103,418,618,896),radius=15,fill=(217,244,248),outline=INK,width=5)
  active=int(100*E(p))
  for n in range(100):
   x=128+(n%10)*50
   y=446+(n//10)*42
   d.ellipse((x-8,y-8,x+8,y+8),fill=TEAL if n<active else (178,217,224),outline=(122,177,188),width=1)
  txt(d,(149,925),str(active).zfill(3)+" / 100 OPENINGS ACTIVE",F26,TEAL)
  label_panel(d,970,'SPREAD THE INFLOW','Distributed water enters with less turbulence')
 elif mode=='pressure':
  layout_panel(d,'WHY WATER MOVES / GRAVITY','Difference in water level generates pressure')
  for x,label,top in [(90,'UPSTREAM',465),(409,'CHAMBER',671)]:
   d.rectangle((x,434,x+218,864),fill=(246,250,251),outline=INK,width=4)
   d.rectangle((x+5,top,x+212,857),fill=(108,205,230))
   d.arc((x+11,top+9,x+207,top+26),0,180,fill=(211,249,251),width=3)
   txt(d,(x+28,399),label,F18,INK)
  d.line((314,477,403,477),fill=GOLD,width=4)
  d.line((357,477,357,671),fill=GOLD,width=3)
  arrow(d,(355,499),(355,646),GOLD,5)
  txt(d,(317,699),"DELTA h",F18,INK)
  d.rounded_rectangle((266,851,464,914),radius=12,fill=TEAL)
  for k in range(3):
   off=(t*37+k*53)%160
   arrow(d,(292+off,882),(318+off,882),'white',4)
  label_panel(d,960,'PRESSURE DIFFERENCE','Head difference drives flow through culverts')
 elif mode=='rise':
  layout_panel(d,'BUOYANCY / FORCES ON THE HULL','Ship rises because it floats on the surface')
  d.rectangle((97,492,617,873),fill=(244,251,252),outline=INK,width=4)
  level=704-int(129*E(p))
  d.rectangle((102,level,612,869),fill=(99,201,229))
  ship(d,353,level,.95)
  arrow(d,(358,level+147),(358,level-79),TEAL,8)
  arrow(d,(440,level-100),(440,level+79),GOLD,8)
  txt(d,(145,444),"BUOYANCY",F24,TEAL)
  txt(d,(451,445),"WEIGHT",F24,INK)
  txt(d,(138,902),"SHIP RISES WITH THE WATER SURFACE",F18,INK)
  label_panel(d,964,'HULL DISPLACES WATER','No crane is lifting the ship')
 elif mode=='equal':
  layout_panel(d,'EQUALIZE WATER LEVELS FIRST','Open the next gates only after levels match')
  left=557+int((1-E(p))*101)
  for x,label,top in [(84,'LOCK',left),(417,'NEXT LEVEL',558)]:
   d.rounded_rectangle((x,456,x+230,732),radius=8,fill=(239,250,252),outline=INK,width=4)
   d.rectangle((x+6,top,x+224,727),fill=(110,209,233))
   txt(d,(x+28,412),label,F18,INK)
  txt(d,(343,569),"=",F34,TEAL)
  d.rectangle((115,782,600,891),fill=(201,238,246))
  d.ellipse((141,792,158,809),fill=INK);d.ellipse((563,792,580,809),fill=INK)
  opening=1.0*E(p)
  d.line((149,801,358-opening*100,871-opening*61),fill=GOLD,width=11)
  d.line((572,801,365+opening*100,871-opening*61),fill=GOLD,width=11)
  label_panel(d,944,'VALVES CLOSE; GATES OPEN','Water level equality makes passage safe')
 elif mode=='profile':
  layout_panel(d,'THREE STEPS TO GATUN LAKE','Original Atlantic locks / simplified elevation')
  for k in range(4):
   x=83+132*k
   top=855-105*k
   d.rounded_rectangle((x,top,x+113,921-105*k),radius=6,fill=(119,207,227),outline=INK,width=3)
   if k<3:
    d.line((x+100,top,x+123,top-93),fill=GOLD,width=4)
  for k in range(3):
   x=136+k*132;y=820-105*k
   txt(d,(x,y),str(k+1),F24,INK)
   if p*3>k:
    arrow(d,(x+15,y-40),(x+87,y-93),TEAL,5)
  ship(d,124+400*E(p),850-317*E(p),.66)
  txt(d,(437,472),"LAKE",F26,INK)
  label_panel(d,954,'ABOUT 26 METERS TOTAL','The elevation change spans multiple lockages')
 elif mode=='reverse':
  layout_panel(d,'THE REVERSE JOURNEY / DESCENT','Same mechanism, water drains to a lower level')
  for i,(lab,col) in enumerate([('UPBOUND',TEAL),('DOWNBOUND',GOLD)]):
   x=84+i*295
   d.rounded_rectangle((x,447,x+250,887),radius=9,fill=(241,251,252),outline=INK,width=4)
   h=676-175*E(p) if i==0 else 500+175*E(p)
   d.rectangle((x+7,int(h),x+243,879),fill=(106,201,231))
   ship(d,x+125,int(h),.6)
   txt(d,(x+40,407),lab,F18,col)
   arrow(d,(x+120,795),(x+120,718),col,5) if i==0 else arrow(d,(x+120,719),(x+120,795),col,5)
  label_panel(d,963,'ADD WATER / DRAIN WATER','One chamber, opposite flow directions')
 else:
  layout_panel(d,'ENGINEERING EXPLAINED','Gates, water pressure and buoyancy work together')
  d.rectangle((112,479,613,915),fill=(238,250,252),outline=INK,width=4)
  d.rectangle((118,708,606,908),fill=(109,210,235))
  ship(d,360,711,.92)
  label_panel(d,962,'THREE PRINCIPLES','Hydraulics + pressure + ship buoyancy')

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
 final=out/'EP02_PanamaCanal_GravityLocks_R2_CloudRender_720p.mp4'
 ff(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(frames),'-stream_loop','-1','-i',str(real),'-i',str(voice),'-i',str(music),'-filter_complex',filtergraph,'-map','[video]','-map','[audio]','-c:v','libx264','-preset','veryfast','-crf','24','-r','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t',str(total),'-movflags','+faststart',str(final)])
 # verify real file content with ffprobe and decode
 data=json.loads(ff(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)]))
 vids=[s for s in data['streams'] if s['codec_type']=='video'];auds=[s for s in data['streams'] if s['codec_type']=='audio']
 assert len(vids)==1 and vids[0]['codec_name']=='h264' and vids[0]['width']==W and vids[0]['height']==H
 assert len(auds)==1 and auds[0]['codec_name']=='aac'
 assert 155<float(data['format']['duration'])<191
 finalmeta={'editorial_version':'R2_multiview_cloud', 'file':final.name,'duration':float(data['format']['duration']),'size':final.stat().st_size,'fps':vids[0]['r_frame_rate'],'narrator':'Kokoro am_michael, Apache 2.0 - NOT Grady','footage':'US Navy public domain, Wikimedia Commons','licensed':True,'publication_approved':False,'chapters':timing}
 (out/'EP02_PanamaCanal_GravityLocks_Preview_Report.json').write_text(json.dumps(finalmeta,indent=2))
 print('SUCCESS',json.dumps({k:finalmeta[k] for k in ['file','duration','size','fps','publication_approved']}),flush=True)

if __name__=='__main__':main()
