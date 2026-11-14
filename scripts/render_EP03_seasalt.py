#!/usr/bin/env python3
"""EP03 Ancient salt production documentary with real licensed Pexels footage and moving engineering diagrams.
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
 ("COULD YOU MAKE SALT?","Imagine you traveled back one thousand years to a sunny coast. There is no factory, no supermarket, and no electricity. Could you make precious salt with seawater, sunlight, simple tools, and a little knowledge?","SALT FROM SEAWATER","real"),
 ("THE OCEAN HOLDS THE INGREDIENTS","Salt is already dissolved in seawater. On average, a liter contains around thirty five grams of dissolved salts. But a bowl of seawater is not a pile of clean salt. We must separate the water.","35 g OF DISSOLVED SALTS / L","real"),
 ("BUILD A SIMPLE SALTWORK","On a suitable shore, make shallow earth banked ponds. A channel and gate admit seawater when the tide permits. Close the gate to trap the water, and protect the ponds from flooding.","SEA > GATE > SHALLOW PAN","gate"),
 ("MOVE THROUGH A SERIES OF PANS","Why use many ponds? As brine moves from one pan to the next, evaporation makes it stronger. Older saltworks used staged basins. Each stage concentrates the brine or lets a different mineral settle.","POND ONE > TWO > THREE","pans"),
 ("LET THE SUN DO THE WORK","The sun gives energy to surface water, while wind removes the moist air above it. Water molecules escape as vapor. Dissolved salts remain. The pool becomes shallower, and the brine grows more concentrated.","SUN + WIND = EVAPORATION","evap"),
 ("WHAT DOES MORE SALTY MEAN?","Imagine the original salt spread through one full basin. Remove half the water, and the dissolved material now occupies far less space. The number of dissolved ions has not suddenly doubled: the concentration has.","LESS WATER, HIGHER SALINITY","salinity"),
 ("NOT EVERY MINERAL IS TABLE SALT","Seawater contains many dissolved minerals. As the brine strengthens, some calcium carbonate can separate first, followed by gypsum. The sodium chloride we want crystallizes at a later, higher concentration.","EARLY MINERALS SEPARATE FIRST","minerals"),
 ("WATCH A CRYSTAL TAKE SHAPE","When the brine reaches saturation, sodium and chloride ions begin joining a repeating arrangement. Tiny seeds of solid salt form. Additional ions attach to them. The familiar cubic crystal gradually grows.","Na+  +  Cl-  >  NaCl","lattice"),
 ("THE FINAL CRYSTALLIZER","In the last shallow crystallizer pond, water keeps evaporating, while the floor collects a white layer of solid salt. This takes days or weeks, not seconds. Later, the remaining brine can be removed.","SALT GROWS ON THE FLOOR","crystal"),
 ("RAKE THE WHITE HARVEST","Workers gather the deposited salt with rakes, then place it in piles for draining and drying. This modern footage shows the real physical harvesting action. Historical tools differed by location and period.","RAKE > COLLECT > DRY","harvest"),
 ("WHAT IF THE SUN IS NOT ENOUGH?","There is another old solution. Heat the brine in a vessel over a fire, making water boil away more quickly. But wood or other fuel costs time and resources. Solar salt needs sunshine, land, and patience.","BOILING NEEDS FUEL","boiling"),
 ("ANCIENT KNOWLEDGE, REAL PHYSICS","From ancient coastal villages to modern salt farms, the principles remain the same: move water, concentrate brine, grow crystals, and harvest them. Salt helped people preserve food and supported trade. That is engineering with almost nothing.","MOTION BLUEPRINT LAB / EP03","real")
]

def ff(cmd):
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode:raise RuntimeError("Command failed "+str(cmd[:4])+" "+p.stderr[-1600:])
 return p.stdout

def download_salt(dest, video_id):
 urls=[
  'https://videos.pexels.com/video-files/'+str(video_id)+'/'+str(video_id)+'-sd_960_540_24fps.mp4',
  'https://videos.pexels.com/video-files/'+str(video_id)+'/'+str(video_id)+'-hd_1920_1080_24fps.mp4'
 ]
 for u in urls:
  try:
   req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Accept':'video/mp4'})
   with urllib.request.urlopen(req,timeout=90) as stream,open(dest,'wb') as output:
    shutil.copyfileobj(stream,output)
   seconds=float(ff(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(dest)]).strip())
   if dest.stat().st_size>200000 and seconds>10:
    print('LICENSED PEXELS FILM OK',video_id,seconds,flush=True)
    return
  except Exception as exc:
   print('Video URL retry',str(exc)[:150],flush=True)
 raise RuntimeError('No authentic licensed film '+str(video_id))

def synthesize_voice(dest,work):
 from kokoro import KPipeline
 pipe=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M')
 chunks=[]; timing=[]; pos=0; sr=24000
 for idx,(title,body,caption,mode) in enumerate(SCENES):
  aud=[]
  for graphemes,phonemes,samples in pipe(body,voice='am_michael',speed=1.13):
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
 txt(d,(36,29),"EP03",F28,"white")
 txt(d,(134,31),"MOTION BLUEPRINT LAB",F26,INK)
 d.rectangle((0,H-69,W,H),fill=(228,247,249))
 txt(d,(23,H-51),"SEE HOW THE WORLD WORKS",F24,INK)
 d.rectangle((20,H-12,700,H-5),fill=(201,226,233))
 d.rectangle((20,H-12,20+680*progress,H-5),fill=TEAL)

def sun(d,x,y,t):
 d.ellipse((x-40,y-40,x+40,y+40),fill=(247,188,82),outline=(215,147,54),width=3)
 for k in range(10):
  a=k*math.pi/5+t*.15
  d.line((x+53*math.cos(a),y+53*math.sin(a),x+77*math.cos(a),y+77*math.sin(a)),fill=(229,181,91),width=4)

def grains(d,x,y,count,p=1):
 for k in range(int(count*p)):
  xx=x+(k*67)%420;yy=y+(k*37)%50
  d.rectangle((xx,yy,xx+8,yy+8),fill=(248,250,250),outline=(158,195,198),width=1)

def info(d,title,note):
 d.rounded_rectangle((66,965,654,1048),radius=12,fill=(226,248,249))
 txt(d,(81,974),title,F26,INK)
 txt(d,(81,1013),note,F18,(57,117,134))

def render_graph(im,d,scene_index,p,t,real):
 mode=SCENES[scene_index][3]
 if real:
  d.rounded_rectangle((34,709,685,1074),radius=19,fill="white",outline=(137,210,219),width=4)
  sun(d,526,793,t)
  d.polygon([(106,899),(313,861),(608,897),(608,959),(106,959)],fill=(111,199,218),outline=INK)
  grains(d,147,910,50,p)
  for k in range(8):
   xx=129+k*66;yy=840-int(52*((t*.09+k*.14)%1))
   d.ellipse((xx,yy,xx+8,yy+14),fill=(101,196,211))
  txt(d,(109,985),"REAL SALT PRODUCTION",F26,INK)
  return
 d.rounded_rectangle((35,248,685,1062),radius=19,fill="white",outline=(137,210,219),width=4)
 txt(d,(52,276),"ORIGINAL ENGINEERING ANIMATION",F18,TEAL)
 if mode=='gate':
  d.polygon([(91,354),(229,354),(229,914),(91,914)],fill=(102,200,228),outline=INK)
  txt(d,(119,414),"SEA",F34,"white")
  d.rectangle((233,626,371,672),fill=(196,213,217),outline=INK,width=4)
  d.rectangle((240,641,362,659),fill=(98,199,226))
  d.rectangle((378,443,622,897),fill=(237,247,249),outline=INK,width=5)
  d.rectangle((383,int(885-225*p),617,891),fill=(101,203,227))
  d.rectangle((367,616,379,690),fill=GOLD)
  for k in range(5):
   x=241+int((t*58+k*29)%129)
   arrow(d,(x,650),(min(x+31,360),650),TEAL,4)
  info(d,'BUILD A SLUICE','Fill shallow ponds with seawater')
 elif mode=='pans':
  shades=[(124,199,224),(152,219,224),(236,220,193),(240,206,172)]
  for i in range(4):
   x=84+(i%2)*294;y=361+(i//2)*251
   d.rounded_rectangle((x,y,x+263,y+211),radius=12,fill=shades[i],outline=INK,width=4)
   txt(d,(x+17,y+59),['RESERVOIR','EVAPORATOR','STRONG BRINE','CRYSTALLIZER'][i],F18,INK)
   if p*4>=i:d.rectangle((x+19,y+120,x+243,y+161),fill=(241,252,251))
  arrow(d,(353,473),(379,473),TEAL,5);arrow(d,(217,575),(217,609),TEAL,5);arrow(d,(353,730),(379,730),TEAL,5)
  info(d,'FOUR LINKED PANS','Move brine as evaporation advances')
 elif mode=='evap':
  sun(d,534,401,t)
  d.rounded_rectangle((93,610,627,882),radius=12,fill=(237,247,249),outline=INK,width=4)
  level=640+int(226*p)
  d.rectangle((100,level,620,876),fill=(99,193,223))
  grains(d,124,820,50,p)
  for k in range(28):
   xx=126+(k*73)%471;yy=582-int(164*((t*.08+k*.091)%1))
   d.ellipse((xx,yy,xx+7,yy+13),fill=(129,212,220))
  txt(d,(113,908),"H2O LEAVES AS VAPOR",F24,INK)
  info(d,'SUN AND WIND','Water escapes; ions remain')
 elif mode=='salinity':
  d.rounded_rectangle((93,371,303,886),radius=23,fill=(230,247,250),outline=INK,width=5)
  d.rectangle((101,415+int(459*p),295,877),fill=(101,197,225))
  for k in range(24):
   x=119+(k*39)%164;y=771+(k*17)%90
   d.ellipse((x,y,x+10,y+10),fill="white",outline=INK)
  d.rectangle((376,397,424,879),fill=(227,238,239))
  d.rectangle((376,879-int(475*p),424,879),fill=TEAL)
  txt(d,(446,426),"SALINITY",F26,INK)
  txt(d,(444,726),"~35 g/L",F26,INK)
  txt(d,(444,765),"SEAWATER",F18,TEAL)
  info(d,'MORE CONCENTRATED','Less water, same dissolved minerals')
 elif mode=='minerals':
  for i,(name,col) in enumerate([('CALCIUM CARBONATE',(185,218,207)),('GYPSUM',(237,217,177)),('SODIUM CHLORIDE',(113,204,229))]):
   y=367+i*197
   d.rounded_rectangle((75,y,644,y+175),radius=13,fill=(242,251,251),outline=(138,196,206),width=3)
   d.rectangle((92,y+39,230,y+143),fill=col,outline=INK,width=3)
   grains(d,95,y+72,12,min(1,max(0,p*3-i)))
   txt(d,(255,y+64),name,F22,INK)
   txt(d,(259,y+100),"STAGE "+str(i+1),F18,TEAL)
  info(d,'DIFFERENT MINERALS','Some solids separate before table salt')
 elif mode=='lattice':
  d.rounded_rectangle((86,356,636,864),radius=14,fill=(234,249,250),outline=(144,200,210),width=3)
  for i in range(7):
   for j in range(7):
    if p<.8*(i+j)/13:continue
    x=139+i*78;y=413+j*59
    d.ellipse((x-14,y-14,x+14,y+14),fill=GOLD if (i+j)%2==0 else AQUA,outline=INK,width=2)
  txt(d,(157,904),"Na+  +  Cl-   -->  NaCl",F28,INK)
  info(d,'SALT CRYSTALS','Sodium and chloride form cubic lattice')
 elif mode=='crystal':
  d.rounded_rectangle((87,370,634,900),radius=14,fill=(235,250,250),outline=INK,width=5)
  level=451+int(178*p)
  d.rectangle((93,level,629,895),fill=(98,198,227))
  for k in range(74):
   if p<.15+(k*7%17)*.03:continue
   x=110+(k*71)%508;h=12+int(p*(33+(k*17)%45))
   d.polygon([(x,887-h),(x+7,882-h),(x+13,887-h),(x+13,891),(x,891)],fill=(247,250,250),outline=(181,207,208))
  txt(d,(105,918),"NaCl BUILDS ON THE BOTTOM",F22,INK)
  info(d,'CRYSTALLIZER POND','White crystals grow over time')
 elif mode=='harvest':
  d.rectangle((95,672,631,765),fill=(234,244,241),outline=INK,width=3)
  x=171+277*p
  d.line((x,511,x+160,724),fill=(169,120,67),width=11)
  d.line((x+80,723,x+219,723),fill=(124,95,68),width=8)
  for k in range(10):
   xx=x+92+k*12
   d.line((xx,722,xx,756),fill=(124,95,68),width=3)
  grains(d,114,718,75,p)
  txt(d,(124,828),"HARVEST AND DRY SALT",F26,INK)
  info(d,'RAKE THE SALT','Collect the deposited white layer')
 elif mode=='boiling':
  d.rounded_rectangle((93,385,635,873),radius=15,fill=(252,247,239),outline=(218,171,115),width=4)
  d.polygon([(170,612),(532,612),(502,738),(203,738)],fill=(106,148,158),outline=INK)
  d.rectangle((201,613,503,645),fill=(102,200,226))
  for k in range(27):
   x=217+(k*43)%278;y=574-int(154*((t*.18+k*.08)%1))
   d.ellipse((x,y,x+9,y+16),fill=(160,200,203))
  for k in range(7):
   x=201+k*49
   d.polygon([(x,779),(x-17,832),(x+18,832)],fill=(236,127,55))
   d.polygon([(x,803),(x-7,828),(x+10,830)],fill=(251,207,91))
  txt(d,(140,900),"HEAT MAKES WATER EVAPORATE",F22,INK)
  info(d,'BOIL THE BRINE','Faster but requires scarce fuel')

def draw_frame(t,total,timing,footage_available):
 n=next((i for i,x in enumerate(timing) if t<x['end']),len(timing)-1)
 z=timing[n]
 p=E((t-z['start'])/max(.1,z['end']-z['start']))
 mode=z['mode'];real=mode=='real' and footage_available
 im=Image.new('RGB',(W,H),(250,253,254));d=ImageDraw.Draw(im)
 grid_base(d,t/total,n)
 d.rounded_rectangle((22,111,698,179),radius=11,fill=(232,248,250))
 txt(d,(34,123),str(n+1).zfill(2)+" / "+z['title'],F28,INK)
 if real:
  d.rounded_rectangle((28,210,692,648),radius=19,fill="white",outline=(130,202,216),width=4)
  d.rectangle((43,240,677,596),fill=(210,233,239))
  txt(d,(50,604),"REAL SALT MAKING  |  PEXELS LICENSE",F16,INK)
 render_graph(im,d,n,p,t,real)
 words=z['caption'].split();lines=[];line=""
 for word in words:
  if len(line+' '+word)>35 and line:lines.append(line);line=word
  else:line=(line+' '+word).strip()
 if line:lines.append(line)
 d.rounded_rectangle((40,1086,680,1179),radius=14,fill=(5,133,157))
 for j,ln in enumerate(lines[:2]):
  width=d.textlength(ln,font=F28)
  txt(d,((W-width)/2,1099+j*36),ln,F28,"white")
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
 a=parser.parse_args()
 out=pathlib.Path(a.outdir);out.mkdir(exist_ok=True,parents=True)
 voice=out/'EP03_EnglishVoice_Kokoro.wav'
 print('Creating free licensed English EP03 voice, not paid Grady',flush=True)
 timing,total=synthesize_voice(voice,out)
 if not 150<=total<=205:raise RuntimeError('Speech length outside expected 3min '+str(total))
 filmA=out/'EP03_PexelsWorkers.mp4';filmB=out/'EP03_PexelsCollect.mp4'
 download_salt(filmA,15574383);download_salt(filmB,15574396)
 total+=.2
 animation=out/'_EP03_original_diagrams.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','ultrafast','-crf','22','-pix_fmt','yuv420p',str(animation)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for i in range(int(total*FPS)):
   im,_=draw_frame(i/FPS,total,timing,True)
   p.stdin.write(im.tobytes())
   if i%(FPS*20)==0:print('Animation seconds',i/FPS,flush=True)
  p.stdin.close();err=p.stderr.read()
  if p.wait()!=0:raise RuntimeError(err.decode(errors='ignore')[-1700:])
 finally:
  if p.poll() is None:p.kill()
 score=out/'EP03_OriginalSoundtrack.wav';make_music(score,total)
 realA=[z for z in timing if z['mode']=='real' and z['index']!=9]
 realB=[z for z in timing if z['index']==9]
 condA='+'.join('between(t,{:.3f},{:.3f})'.format(z['start'],z['end']-.12) for z in realA)
 condB='+'.join('between(t,{:.3f},{:.3f})'.format(z['start'],z['end']-.12) for z in realB)
 graph=("[1:v]fps=24,scale=634:356,setsar=1,setpts=PTS-STARTPTS[a];"
        "[2:v]fps=24,scale=634:356,setsar=1,setpts=PTS-STARTPTS[b];"
        "[0:v]fps=24,format=yuv420p[base];"
        "[base][a]overlay=43:240:enable='"+condA+"':shortest=1[first];"
        "[first][b]overlay=43:240:enable='"+condB+"':shortest=1[video];"
        "[3:a]volume=1.0[voice];[4:a]volume=0.7[bg];"
        "[voice][bg]amix=inputs=2:duration=longest:normalize=0[audio]")
 final=out/'EP03_AncientSeaSalt_TimeTravelEngineering_3min_PREVIEW_720p.mp4'
 ff(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(animation),'-stream_loop','-1','-i',str(filmA),'-stream_loop','-1','-i',str(filmB),'-i',str(voice),'-i',str(score),'-filter_complex',graph,'-map','[video]','-map','[audio]','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','128k','-t',str(total),'-movflags','+faststart',str(final)])
 meta=json.loads(ff(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)]))
 vids=[z for z in meta['streams'] if z['codec_type']=='video'];aud=[z for z in meta['streams'] if z['codec_type']=='audio']
 assert len(vids)==1 and vids[0]['codec_name']=='h264' and vids[0]['width']==W and vids[0]['height']==H
 assert len(aud)==1 and aud[0]['codec_name']=='aac'
 assert 150<float(meta['format']['duration'])<205
 license_url='https://www.pexels.com/license/'
 sources=[
 'https://www.pexels.com/video/two-workers-harvesting-salt-by-the-sea-15574383/',
 'https://www.pexels.com/video/a-worker-shoveling-salt-into-a-wheelbarrow-15574396/',
 'https://www.noaa.gov/jetstream/ocean/sea-water',
 'https://historicengland.org.uk/images-books/publications/iha-preindustrial-salterns/heag225-pre-industrial-salterns/',
 'https://pubs.rsc.org/en/content/articlehtml/2017/ew/c6ew00268d']
 (out/'EP03_AncientSeaSalt_Credits.txt').write_text('EP03 HOW TO MAKE SALT WITHOUT FACTORIES\nReal modern salt harvesting footage: khanhhoangminh / Pexels (two original clips)\nEdited, resized and combined with original animated engineering explanations.\nPexels license: '+license_url+'\n'+'\n'.join(sources)+'\nOriginal English script, engineering diagrams and synthesised background music by Motion Blueprint Lab. Free Kokoro am_michael voice (NOT Grady). This is a private preview, not a published release.\n')
 report={'episode':'EP03','file':final.name,'duration':float(meta['format']['duration']),'size':final.stat().st_size,'voice':'Kokoro am_michael, not Grady','sources':sources,'chapters':timing,'publicationApproved':False}
 (out/'EP03_AncientSeaSalt_Report.json').write_text(json.dumps(report,indent=2))
 print('SUCCESS EP03',json.dumps({'duration':report['duration'],'bytes':report['size']}),flush=True)
if __name__=='__main__':
 main()
