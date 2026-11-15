#!/usr/bin/env python3
"""EP04 Wind Turbine: original kinetic engineering cinema with real Pexels footage.
A preview only. No upload or publication. Free Kokoro English narration.
"""
import json,math,os,pathlib,subprocess,urllib.request,urllib.error,shutil,random
import numpy as np
import soundfile as sf
import cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter

W,H,FPS=720,1280,15
DUR=14.45
SC=[
("THE INVISIBLE FUEL","Can invisible air really power a city?","At sunrise, a giant turbine turns in the wind. No fuel is burning in its tower. Yet its blades can turn moving air into electrical energy. The trick is hidden in the shape of the blades.","real0"),
("WHY DO THE BLADES TURN?","The surprising science inside a windmill.","A modern wind turbine is not just a fan running backward. Its three long blades are carefully shaped airfoils. As wind passes each blade, aerodynamic forces create torque, turning the entire rotor.","real1"),
("AN AIRFOIL IN THE WIND","Two surfaces. Different pressure.","Imagine slicing a blade and looking at its cross section. The air flows around the curved surface. Lift, along with drag, acts on the blade. The lift force supplies most of the useful rotation.","airfoil"),
("FROM LIFT TO ROTATION","Force becomes twisting motion.","Now look straight at the rotor. Each blade meets moving air while sweeping around the hub. Part of the aerodynamic force acts tangentially, creating torque. Three blades share this work as they spin.","rotor"),
("OPEN THE NACELLE","The machine room at the top.","Behind the rotor is the nacelle, the housing on top of the tower. Inside, a low speed shaft carries the turning force toward the electrical generator. Some machines use a gearbox; others connect directly.","nacelle"),
("THE GEARBOX SECRET","Slow input. Faster output.","In a geared design, large gears drive smaller gears, increasing rotational speed before the generator. Our drawing simplifies the real mechanism. Direct drive turbines skip this gearbox and use a generator designed for slower rotation.","gears"),
("MAGNETS CREATE CURRENT","Motion becomes electricity.","Inside a generator, magnetic fields move relative to coils of wire. That changing magnetic flux induces voltage. Modern wind turbines may use different generator designs, but this electromagnetic principle connects shaft rotation to electrical output.","generator"),
("THE POWER IS ALTERNATING","From spinning field to AC.","Watch the voltage rise, fall, and reverse as the magnetic field turns. Three phase systems carry several alternating waveforms. Power electronics help control the output so a variable speed turbine can deliver usable electricity.","waves"),
("KEEP FACING THE WIND","Yaw direction. Pitch the blades.","The nacelle can yaw to align with the wind direction. Each blade can also pitch, turning around its long axis. Pitch control manages aerodynamic loading and power, while sensors and computers keep the machine within operating limits.","pitch"),
("TWICE THE WIND SPEED?","Eight times the available power.","Moving air carries kinetic energy. For the same rotor area and air density, the power available in the wind rises with the cube of wind speed. Double the speed and the theoretical incoming power is eight times larger, before losses.","power"),
("KNOW WHEN TO STOP","Safety is part of the design.","A turbine cannot simply spin faster forever. At high winds, controls adjust blade pitch and may stop the machine to protect it. The exact speed thresholds depend on the turbine model and its operating conditions.","safety"),
("FROM WIND TO THE GRID","Five transformations in one machine.","Here is the complete chain: wind flows across an airfoil, lift turns the rotor, shafts transmit mechanical power, the generator produces electricity, and power electronics condition it for the grid. That is wind energy, engineered.","real2")
]
assert len(SC)==12
P=pathlib.Path
OUT=P(os.environ.get("EP_OUT","out_EP04"));OUT.mkdir(exist_ok=True,parents=True)
C={"bg":(7,17,32),"panel":(16,35,53),"dark":(10,23,42),"ink":(230,245,250),
   "mute":(151,179,195),"cyan":(68,218,232),"blue":(48,124,222),
   "gold":(255,192,91),"orange":(255,126,95),"wire":(57,91,116)}
FROOT="/usr/share/fonts/truetype/dejavu/"
def font(sz,bold=False):
 return ImageFont.truetype(FROOT+("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),sz)
F16=font(16);F18=font(18);F21=font(21);F24=font(24);F29=font(29);F32=font(32,True);F39=font(39,True);F45=font(45,True);F55=font(55,True)
def T(d,x,y,s,f=F24,fill=None,anchor=None,stroke=0):
 d.text((int(x),int(y)),s,font=f,fill=fill or C["ink"],anchor=anchor,stroke_width=stroke,stroke_fill=(0,6,18))
def shadow_panel(d,rect,r=22):
 x,y,a,b=rect
 d.rounded_rectangle((x+3,y+6,a+3,b+6),radius=r,fill=(4,11,23))
 d.rounded_rectangle(rect,radius=r,fill=C["panel"],outline=(48,85,109),width=2)
def poly(d,pts,fill,outline=None,width=1):
 d.polygon([(int(x),int(y)) for x,y in pts],fill=fill)
 if outline:d.line([(int(x),int(y)) for x,y in pts+[pts[0]]],fill=outline,width=width,joint="curve")
def arrow(d,a,b,color=None,w=6,head=15):
 col=color or C["cyan"]
 a=np.array(a);b=np.array(b);delta=b-a;norm=np.linalg.norm(delta)
 if norm<1:return
 v=delta/norm;side=np.array([-v[1],v[0]])
 d.line((tuple(a),tuple(b)),fill=col,width=w)
 p=b-v*head
 poly(d,[tuple(b),tuple(p+side*head*.43),tuple(p-side*head*.43)],col)
def ring(d,x,y,r,color,width=4,start=0,end=360):
 d.arc((x-r,y-r,x+r,y+r),start,end,fill=color,width=width)
def dot(d,x,y,r,fill):
 d.ellipse((x-r,y-r,x+r,y+r),fill=fill)
def grid(d,spacing=44):
 for x in range(0,W,spacing):d.line((x,0,x,H),fill=(14,32,51),width=1)
 for y in range(0,H,spacing):d.line((0,y,W,y),fill=(14,32,51),width=1)
def draw_base(idx,t,p,mode):
 im=Image.new("RGB",(W,H),C["bg"]);d=ImageDraw.Draw(im)
 grid(d,54)
 d.rectangle((0,0,W,11),fill=C["cyan"])
 T(d,36,28,"MOTION BLUEPRINT LAB",F21,C["cyan"])
 T(d,684,27,"EP04",F21,C["gold"],anchor="ra")
 d.line((37,69,683,69),fill=(48,85,110),width=2)
 ttl=SC[idx][0]
 T(d,37,94,ttl,F39,C["ink"])
 T(d,38,156,SC[idx][1],F21,C["mute"])
 if mode.startswith("real"):pass
 else:
  shadow_panel(d,(30,217,690,1025),23)
  d.rounded_rectangle((48,238,238,274),radius=9,fill=(28,78,95))
  T(d,62,244,"ENGINEERING VIEW",F18,C["cyan"])
 d.rectangle((0,1240,W,H),fill=(7,21,36))
 d.rectangle((27,1260,693,1267),fill=(36,71,92))
 d.rectangle((27,1260,27+666*(idx+p)/len(SC),1267),fill=C["cyan"])
 return im,d
def captions(d,idx,p):
 body=SC[idx][2]
 groups=[];words=body.split()
 while words:
  take=min(10,len(words));groups.append(" ".join(words[:take]));words=words[take:]
 n=min(len(groups)-1,int(p*len(groups)))
 s=groups[n]
 lines=[];line=""
 for word in s.split():
  if len(line)+1+len(word)>31:lines.append(line);line=word
  else:line=(line+" "+word).strip()
 if line:lines.append(line)
 d.rounded_rectangle((27,1052,693,1227),radius=21,fill=(8,39,58),outline=(27,102,128),width=2)
 T(d,48,1062,"NARRATION  /  "+str(idx+1).zfill(2),F18,C["cyan"])
 for j,ln in enumerate(lines[:3]):
  bb=d.textbbox((0,0),ln,font=F29);ww=bb[2]-bb[0]
  T(d,(W-ww)/2,1094+j*38,ln,F29,C["ink"])
def airfoil(d,t,p):
 cx,cy=356,604
 ang=-0.12
 pts=[]
 for i in range(81):
  x=i/80;yt=.12/0.2*(.2969*math.sqrt(max(.0001,x))-.1260*x-.3516*x*x+.2843*x*x*x-.1015*x*x*x*x)
  pts.append((x,yt))
 for i in range(80,-1,-1):
  x=i/80;yt=-.12/0.2*(.2969*math.sqrt(max(.0001,x))-.1260*x-.3516*x*x+.2843*x*x*x-.1015*x*x*x*x)
  pts.append((x,yt))
 shape=[]
 for x,y in pts:
  xx=(x-.5)*410;yy=-y*410
  shape.append((cx+xx*math.cos(ang)-yy*math.sin(ang),cy+xx*math.sin(ang)+yy*math.cos(ang)))
 for i in range(7):
  y=345+i*78
  st=[]
  for x in range(75,655,7):
   delta=math.exp(-((x-340)/145)**2)
   yy=y+(-55 if i<3 else 28)*delta*math.sin(math.pi*(x-75)/580)
   yy+=4*math.sin((x*.02+t*2+i)%6.283)
   st.append((x,yy))
  d.line(st,fill=C["cyan"] if i<4 else C["blue"],width=3)
  k=int((p*.9+i/9)*65)%len(st);arrow(d,st[max(0,k-3)],st[min(len(st)-1,k)],C["cyan"],3,9)
 poly(d,shape,(198,224,235),C["ink"],3)
 arrow(d,(510,565),(568,475),C["gold"],9,22)
 T(d,449,420,"LIFT",F29,C["gold"])
 arrow(d,(486,620),(594,647),C["orange"],6,16)
 T(d,525,667,"DRAG",F21,C["orange"])
 T(d,92,864,"SHAPED BLADE CROSS-SECTION",F24,C["ink"])
 T(d,92,908,"Illustrative airflow / forces",F21,C["mute"])
def rotor(d,t,p):
 cx,cy=354,600
 for r in [135,230,299]:
  ring(d,cx,cy,r,(32,68,94),3)
 for k in range(3):
  a=t*.47+k*2*math.pi/3
  v=np.array([math.sin(a),-math.cos(a)])
  q=np.array([-v[1],v[0]])
  pts=[]
  for rr,ww in [(38,28),(60,34),(210,17),(287,5)]:
   pt=np.array([cx,cy])+v*rr+q*ww
   pts.append(tuple(pt))
  for rr,ww in [(287,-5),(210,-15),(60,-24),(38,-22)]:
   pt=np.array([cx,cy])+v*rr+q*ww
   pts.append(tuple(pt))
  poly(d,pts,(179,225,235),C["cyan"],2)
  tip=np.array([cx,cy])+v*238
  tang=np.array([-v[1],v[0]])*75
  arrow(d,tuple(tip),tuple(tip+tang),C["gold"],7,16)
 dot(d,cx,cy,50,C["panel"]);dot(d,cx,cy,27,C["gold"])
 ring(d,cx,cy,318,C["gold"],7,190,355)
 T(d,75,930,"TANGENTIAL FORCE -> TORQUE",F21,C["gold"])
def nacelle(d,t,p):
 d.rectangle((336,705,375,1001),fill=(106,141,161))
 poly(d,[(346,935),(367,935),(405,1005),(311,1005)],(76,103,123))
 d.rounded_rectangle((184,398,633,694),radius=68,fill=(43,79,102),outline=(99,176,193),width=4)
 d.rounded_rectangle((196,419,614,671),radius=56,fill=(12,30,51),outline=(50,117,150),width=2)
 d.line((99,544,549,544),fill=C["gold"],width=13)
 for x,y,r in [(122,540,15),(344,541,26),(502,544,49)]:
  dot(d,x,y,r,C["gold"] if x!=502 else C["cyan"])
 for k in range(8):
  a=t*3+k*math.pi/4;rr=52
  d.line((502,544,502+rr*math.cos(a),544+rr*math.sin(a)),fill=C["cyan"],width=5)
 for k in range(3):
  a=t*.65+k*math.tau/3
  pts=[(121,537),(120+149*math.cos(a),537+149*math.sin(a)),(116+136*math.cos(a+.12),537+136*math.sin(a+.12))]
  poly(d,pts,(155,223,231),C["ink"],2)
 d.rectangle((287,486,396,604),fill=(45,62,85),outline=C["gold"],width=4)
 for x in range(299,394,21):d.line((x,486,x,601),fill=(198,151,79),width=3)
 d.line((510,598,510,697),fill=C["cyan"],width=6)
 for i,(x,label) in enumerate([(110,"ROTOR"),(300,"GEARBOX"),(484,"GENERATOR")]):
  T(d,x,783,label,F18,C["cyan"] if i!=1 else C["gold"])
  d.line((x+36,769,x+36,667),fill=(95,151,169),width=2)
 T(d,75,881,"CUTAWAY: NACELLE + TOWER",F24,C["ink"])
def gear(d,x,y,r,teeth,ang,col):
 pts=[]
 for k in range(teeth*4):
  a=ang+k*math.tau/(teeth*4)
  r2=r*(1.10 if k%4 in [1,2] else .94)
  pts.append((x+math.cos(a)*r2,y+math.sin(a)*r2))
 poly(d,pts,col,C["ink"],3);dot(d,x,y,r*.4,C["panel"]);dot(d,x,y,r*.17,C["gold"])
 for j in range(6):
  a=ang+j*math.tau/6
  d.line((x,y,x+math.cos(a)*r*.7,y+math.sin(a)*r*.7),fill=(9,48,69),width=9)
def gears(d,t,p):
 gear(d,268,588,188,20,t*.3,(67,160,203))
 gear(d,528,587,76,9,-t*.68,(242,172,78))
 arrow(d,(178,354),(267,400),C["cyan"],7)
 arrow(d,(536,383),(587,335),C["gold"],7)
 T(d,93,324,"SLOW INPUT",F24,C["cyan"])
 T(d,476,293,"FAST OUTPUT",F24,C["gold"])
 T(d,97,889,"SPEED INCREASES / TORQUE CHANGES",F21,C["ink"])
 T(d,97,927,"Illustrative pair of meshing gears",F21,C["mute"])
def generator(d,t,p):
 cx,cy=360,586
 for r in [250,207]:
  ring(d,cx,cy,r,C["wire"],8)
 for k in range(12):
  a=k*math.tau/12;xx=cx+236*math.cos(a);yy=cy+236*math.sin(a)
  ring(d,xx,yy,31,C["orange"],10,55,303)
  ring(d,xx,yy,19,C["gold"],5,55,303)
 a=t*1.8
 shape=[]
 for k in range(6):
  th=a+k*math.tau/6;rr=153 if k%2==0 else 125
  shape.append((cx+rr*math.cos(th),cy+rr*math.sin(th)))
 poly(d,shape,(91,134,171),C["ink"],4)
 poly(d,[(cx+142*math.cos(a+i*math.tau/24),cy+142*math.sin(a+i*math.tau/24)) for i in range(24)],(46,107,163))
 T(d,cx+100*math.cos(a)-25,cy+100*math.sin(a)-20,"N",F32,C["orange"])
 T(d,cx-100*math.cos(a)-25,cy-100*math.sin(a)-20,"S",F32,C["cyan"])
 dot(d,cx,cy,47,C["gold"])
 arrow(d,(510,855),(609,855),C["gold"],7)
 T(d,95,884,"CHANGING MAGNETIC FLUX",F24,C["ink"])
 T(d,95,920,"Induces voltage in wire coils",F21,C["mute"])
def waves(d,t,p):
 y0=650
 for y in range(380,900,85):d.line((92,y,630,y),fill=(41,72,98),width=1)
 for x in range(92,631,70):d.line((x,380,x,900),fill=(41,72,98),width=1)
 d.line((90,y0,636,y0),fill=C["ink"],width=2)
 palette=[C["cyan"],C["gold"],C["orange"]]
 for k in range(3):
  phase=k*math.tau/3
  pts=[(x,y0+125*math.sin((x-94)*math.pi/130-t*1.4+phase)) for x in range(92,635,4)]
  d.line(pts,fill=palette[k],width=5)
 T(d,100,344,"THREE-PHASE WAVEFORMS",F24,C["ink"])
 for k,c in enumerate(palette):
  dot(d,164+k*180,944,8,c);T(d,183+k*180,929,"ABC"[k],F24,c)
def pitch(d,t,p):
 d.rounded_rectangle((66,335,652,623),radius=18,fill=(12,38,59))
 cx,cy=360,486
 wind=t*.18
 for k in range(6):
  arrow(d,(89+(k%3)*72,375+(k//3)*143),(190+(k%3)*72,375+(k//3)*143),C["cyan"],4,11)
 ang=.5*math.sin(t*.23)
 d.ellipse((cx-93,cy-93,cx+93,cy+93),outline=C["wire"],width=5)
 d.line((cx,cy,cx+205*math.cos(ang),cy+205*math.sin(ang)),fill=C["gold"],width=18)
 dot(d,cx,cy,27,C["cyan"])
 T(d,108,342,"YAW  /  FACE THE WIND",F18,C["cyan"])
 d.rounded_rectangle((66,667,652,952),radius=18,fill=(12,38,59))
 pitchang=.36*math.sin(t*.7)
 pts=[]
 for x,y in [(-190,-21),(130,-46),(193,0),(130,46),(-190,21)]:
  pts.append((360+x*math.cos(pitchang)-y*math.sin(pitchang),809+x*math.sin(pitchang)+y*math.cos(pitchang)))
 poly(d,pts,(150,216,224),C["ink"],3)
 d.line((161,808,561,808),fill=C["gold"],width=4)
 T(d,107,678,"PITCH  /  ROTATE BLADE",F18,C["gold"])
def power(d,t,p):
 x0,y0=119,921
 d.line((x0,350,x0,y0,625,y0),fill=C["mute"],width=4)
 for i in range(0,11):
  x=x0+i*48.7;y=y0-480*(i/10)**3
  if i:
   xp=x0+(i-1)*48.7;yp=y0-480*((i-1)/10)**3
   d.line((xp,yp,x,y),fill=C["cyan"],width=6)
 for i,col in [(5,C["gold"]),(10,C["cyan"])]:
  x=x0+i*48.7;y=y0-480*(i/10)**3
  d.line((x,y,x,y0),fill=col,width=3);dot(d,x,y,12,col)
 T(d,160,353,"AVAILABLE WIND POWER",F24,C["ink"])
 T(d,169,873,"5 m/s",F21,C["gold"])
 T(d,483,870,"10 m/s",F21,C["cyan"])
 d.rounded_rectangle((337,335,596,409),radius=18,fill=(39,68,84))
 T(d,360,349,"8x  AVAILABLE",F29,C["gold"])
 T(d,105,954,"Same area / same density / before losses",F16,C["mute"])
def safety(d,t,p):
 x0=107
 for y,tag,col in [(390,"CUT-IN / START",C["cyan"]),(595,"RATED / CONTROL",C["gold"]),(803,"HIGH WIND / PROTECT",C["orange"])]:
  d.rounded_rectangle((85,y,635,y+133),radius=18,fill=(15,42,63),outline=(34,85,112),width=3)
  T(d,111,y+14,tag,F21,col)
  for j in range(3):
   a=t*(.2 if y==803 else .7)+j*math.tau/3
   x=448
   py=y+74
   d.line((x,py,x+42*math.cos(a),py+42*math.sin(a)),fill=col,width=6)
  dot(d,448,y+74,12,C["ink"])
  if y==803:
   d.line((515,y+72,582,y+72),fill=C["orange"],width=8)
   T(d,531,y+34,"STOP",F18,C["orange"])
 T(d,95,951,"Thresholds vary by turbine design",F18,C["mute"])
def cinematic(im,d,idx,t,p,frames):
 if frames is None:return
 cvim=frames.get(idx)
 if cvim is None:return
 frame_idx=min(len(cvim)-1,max(0,int(p*(len(cvim)-1))))
 shot=cvim[frame_idx]
 # actual film, full-bleed; subtitles and brand overlaid after
 rgb=cv2.cvtColor(shot,cv2.COLOR_BGR2RGB)
 im.paste(Image.fromarray(rgb),(0,0))
 d=ImageDraw.Draw(im)
 # top and bottom cinematic shaded scrims; leave genuine footage visible center
 for i in range(280):
  alpha=i/280
  y=i
  d.line((0,y,719,y),fill=(int(4+5*alpha),int(12+12*alpha),int(25+18*alpha)),width=1)
 for y in range(985,1280):
  d.line((0,y,719,y),fill=(7,20,33),width=1)
 d.rectangle((0,0,W,11),fill=C["cyan"])
 T(d,32,28,"MOTION BLUEPRINT LAB",F21,C["cyan"])
 T(d,682,28,"EP04",F21,C["gold"],anchor="ra")
 T(d,38,109,SC[idx][0],F39,C["ink"],stroke=1)
 T(d,40,167,SC[idx][1],F21,C["ink"],stroke=1)
 d.rounded_rectangle((33,898,288,941),radius=9,fill=(16,46,68))
 T(d,48,906,"REAL LICENSED FOOTAGE",F18,C["cyan"])
 d.rectangle((0,1240,W,H),fill=(7,21,36))
 d.rectangle((27,1260,693,1267),fill=(36,71,92))
 d.rectangle((27,1260,27+666*(idx+p)/len(SC),1267),fill=C["cyan"])
def draw(idx,t,frames):
 p=max(0,min(.999,t/DUR))
 mode=SC[idx][3]
 if mode.startswith("real"):
  im,d=draw_base(idx,t,p,mode)
  cinematic(im,d,idx,t,p,frames)
  d=ImageDraw.Draw(im)
 else:
  im,d=draw_base(idx,t,p,mode)
  {"airfoil":airfoil,"rotor":rotor,"nacelle":nacelle,"gears":gears,
   "generator":generator,"waves":waves,"pitch":pitch,"power":power,"safety":safety}[mode](d,t,p)
 captions(d,idx,p)
 return im
def test_url(url):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"video/mp4"})
  with urllib.request.urlopen(req,timeout=30) as resp:return resp
 except Exception:return None
def fetch_video(video_id,slug):
 dest=OUT/("EP04_REAL_"+slug+".mp4")
 candidates=[]
 for x,y in [(540,960),(960,540),(720,1280),(1280,720),(1080,1920),(1920,1080),(640,360),(360,640)]:
  kind="sd" if max(x,y)<=960 else "hd"
  for fps in [30,24,25,29,50,60]:
   candidates.append(f"https://videos.pexels.com/video-files/{video_id}/{video_id}-{kind}_{x}_{y}_{fps}fps.mp4")
 for u in candidates:
  r=test_url(u)
  if r is None:continue
  try:
   with r,open(dest,"wb") as o:shutil.copyfileobj(r,o)
   duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(dest)]))
   if dest.stat().st_size>200000 and duration>5:
    print("SOURCE FOOTAGE VERIFIED",slug,video_id,duration,dest.stat().st_size,flush=True);return dest,u
  except Exception as ex:print("download candidate failed",slug,str(ex)[:80],flush=True)
 raise RuntimeError("Real licensed source not obtainable; no synthetic fake substitution: "+slug)
def source_frames(path,seconds=DUR):
 tmp=OUT/("_transcoded_"+path.stem+".mp4")
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-stream_loop","-1","-i",str(path),
  "-vf",f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1",
  "-t",str(seconds+.15),"-an","-c:v","libx264","-preset","ultrafast","-crf","23",str(tmp)],check=True)
 cap=cv2.VideoCapture(str(tmp));frames=[]
 while len(frames)<int(DUR*FPS)+2:
  ok,fr=cap.read()
  if not ok:break
  frames.append(fr)
 cap.release()
 if len(frames)<DUR*FPS-5:raise RuntimeError("Insufficient real frames: "+str(path))
 print("B ROLL FRAMES",path,len(frames),flush=True)
 return frames
def voice():
 from kokoro import KPipeline
 pipe=KPipeline(lang_code="a",repo_id="hexgrad/Kokoro-82M")
 sr=24000;parts=[];times=[]
 for i,(title,hook,body,mode) in enumerate(SC):
  chunks=[]
  for gr,ph,a in pipe(body,voice="am_michael",speed=1.18):
   chunks.append(np.array(a,dtype=np.float32))
  if not chunks:raise RuntimeError("No narration "+str(i))
  speech=np.concatenate(chunks)
  avail=int(12.85*sr)
  if len(speech)>avail:
   ratio=len(speech)/avail
   if ratio>1.23:raise RuntimeError(f"EP04 speech overrun chapter {i}: {ratio}")
   speech=np.interp(np.linspace(0,len(speech)-1,avail),np.arange(len(speech)),speech).astype(np.float32)
  audio=np.concatenate([np.zeros(int(.35*sr),dtype=np.float32),speech,
                        np.zeros(max(0,int(DUR*sr)-int(.35*sr)-len(speech)),dtype=np.float32)])
  audio=audio[:int(DUR*sr)]
  parts.append(audio);times.append({"chapter":i+1,"title":title,"duration":len(audio)/sr,"words":len(body.split()),"speech_len":len(speech)/sr})
  print("VOICE",i,title,round(len(speech)/sr,2),flush=True)
 raw=np.concatenate(parts);n=int(DUR*len(SC)*sr)
 if len(raw)<n:raw=np.pad(raw,(0,n-len(raw)))
 sf.write(OUT/"EP04_Narration_Kokoro.wav",raw,sr)
 return raw,times,sr
def music(sr,n):
 t=np.arange(n,dtype=np.float32)/sr
 score=np.zeros(n,dtype=np.float32)
 # Original atmospheric synth; no copyrighted notes or commercial song.
 for hz,amp in [(73.42,.005),(110,.006),(146.83,.004),(220,.002)]:
  score+=amp*np.sin(2*np.pi*hz*t+0.6*np.sin(2*np.pi*.025*t))
 beat=np.zeros(n,dtype=np.float32)
 for start in range(0,int(n/sr),3):
  idx=start*sr
  lng=min(sr//3,n-idx)
  if lng>0:
   q=np.arange(lng,dtype=np.float32)/sr
   beat[idx:idx+lng]+=.009*np.sin(2*np.pi*110*q)*np.exp(-12*q)
 score+=beat
 score*=np.minimum(1,t/3)*np.minimum(1,(n/sr-t)/4)
 sf.write(OUT/"EP04_Original_Ambience.wav",score,sr)
def main():
 srcs=[
  (34078191,"AerialGreenFieldVertical","https://www.pexels.com/video/aerial-view-of-wind-turbines-in-open-field-34078191/","Matthias Groeneveld"),
  (4230063,"CloseUpRotatingBlades","https://www.pexels.com/video/wind-turbine-rotating-4230063/","Pexels contributor, credited in page"),
  (7047314,"AerialWindFarm","https://www.pexels.com/video/done-footage-of-wind-turbines-7047314/","ROMAN ODINTSOV")]
 src_manifest=[]
 frames={}
 for i,(vid,slug,page,credit) in enumerate(srcs):
  filepath,u=fetch_video(vid,slug)
  frames[{0:0,1:1,2:11}[i]]=source_frames(filepath)
  src_manifest.append(dict(id=vid,slug=slug,page_url=page,direct_asset_url=u,author=credit,license="Pexels License, free commercial derivative use",license_url="https://www.pexels.com/license/",used_at_chapter=[1,2,12][i],embedded_audio="removed; original narration and music only"))
 raw,times,sr=voice();music(sr,len(raw))
 render=OUT/"_EP04_Original_MotionSilent.mp4"
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p",str(render)]
 process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 count=int(DUR*FPS)
 try:
  for i in range(len(SC)):
   for j in range(count):
    im=draw(i,j/FPS,frames)
    process.stdin.write(im.tobytes())
   print("RENDER CHAPTER",i+1,flush=True)
  process.stdin.close()
  err=process.stderr.read()
  if process.wait()!=0:raise RuntimeError("ffmpeg render: "+err.decode(errors="ignore")[-2000:])
 finally:
  if process.poll() is None:process.kill()
 final=OUT/"EP04_WindTurbine_InsideTheMachine_173s_PRIVATE_PREVIEW_720p.mp4"
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(render),
  "-i",str(OUT/"EP04_Narration_Kokoro.wav"),"-i",str(OUT/"EP04_Original_Ambience.wav"),
  "-filter_complex","[1:a]volume=1.4[v];[2:a]volume=.55[b];[v][b]amix=inputs=2:duration=first:normalize=0[a]",
  "-map","0:v","-map","[a]","-r","24","-c:v","libx264","-preset","veryfast","-crf","21",
  "-c:a","aac","-b:a","160k","-pix_fmt","yuv420p","-movflags","+faststart",str(final)],check=True)
 probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(final)]))
 duration=float(probe["format"]["duration"])
 assert 167<=duration<=177,duration
 assert any(x.get("codec_name")=="h264" and x.get("width")==720 and x.get("height")==1280 for x in probe["streams"])
 assert any(x.get("codec_name")=="aac" for x in probe["streams"])
 subprocess.run(["ffmpeg","-v","error","-i",str(final),"-f","null","-"],check=True)
 sheet=Image.new("RGB",(720,960),(4,15,28))
 for i in range(12):
  path=OUT/f"_EP04_check_{i:02}.jpg"
  subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",str((i+.45)*DUR),"-i",str(final),"-frames:v","1",str(path)],check=True)
  shot=Image.open(path).convert("RGB").resize((180,320))
  sheet.paste(shot,((i%4)*180,(i//4)*320))
 sheet.save(OUT/"EP04_12Shot_ActualVideo_ContactSheet.jpg",quality=91)
 manifest=dict(episode="EP04",topic="How Wind Turbines Turn Air Into Electricity",status="review_only_not_published",
    duration_sec=duration,dimensions=[720,1280],video_codec="H264",audio_codec="AAC",narration="Kokoro am_michael open-weight, not paid Grady",
    budget_paid_credits=0,source_footage=src_manifest,storyboard=times,original_elements="12 distinct motion chapters including 9 mechanism views, original soundtrack and English on-screen captions",
    scientific_facts=["https://www.energy.gov/cmei/systems/how-do-wind-turbines-work",
      "https://www.energy.gov/cmei/systems/explore-wind-turbine-text-version"],
    release_approval="PENDING — preview only")
 (OUT/"EP04_Source_License_QA.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
 (OUT/"EP04_Script_English.txt").write_text("\n\n".join(f"CHAPTER {i+1} | {s[0]}\n{s[2]}" for i,s in enumerate(SC)),encoding="utf-8")
 print("SUCCESS EP04 PREVIEW",final,"seconds",duration,"bytes",final.stat().st_size,flush=True)
if __name__=="__main__":main()
