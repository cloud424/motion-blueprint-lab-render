#!/usr/bin/env python3
"""Rebuild R4 burned in phone-safe subtitles on exact EP05 R3 video; fail closed."""
import base64, gzip, hashlib, json, re, subprocess, urllib.request, pathlib, os
from PIL import ImageFont
ROOT=pathlib.Path("out_EP05_R4");ROOT.mkdir(exist_ok=True)
SOURCE=ROOT/"EP05_R3_original.mp4"
OUTPUT=ROOT/"EP05_Hydropower_R4_BurnedSubtitles_FINAL.mp4"
url="https://res.cloudinary.com/juhsntij/video/upload/v1795009675/motionblueprintlab/EP05_Hydropower_R3_Documentary_173s_FINAL.mp4"
with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=120) as resp, SOURCE.open("wb") as f:
    while True:
        chunk=resp.read(1024*1024)
        if not chunk:break
        f.write(chunk)
check=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected="e7b1aa338aa7109ab9796de09c3bfb4fa60a340a33c1ff6f70427fbb41e8ec00"
assert check(SOURCE)==expected,"Original EP05 bytes mismatch -- never edit unverified source"
srt=gzip.decompress(base64.b64decode("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"))
assert hashlib.sha256(srt).hexdigest()=="fc7d2f4723d2269acffad077d57171049b57bd19d9e0ec1447e9552aff464139"
(ROOT/"EP05_R4_English_Subtitles.srt").write_bytes(srt)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",40)
def wrap(txt,maxpx=640):
    out=[];cur=""
    for word in txt.split():
        cand=(cur+" "+word).strip()
        if font.getlength(cand)>maxpx and cur:out.append(cur);cur=word
        else:cur=cand
    if cur:out.append(cur)
    return r"\N".join(out)
def ts(s):
    h,m,rest=s.split(":");sec,ms=rest.split(",")
    return f"{int(h)}:{int(m):02}:{int(sec):02}.{int(ms)//10:02}"
head="""[Script Info]
Title: EP05 R4 Accessible Burned Captions
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,DejaVu Sans,40,&H00FFFFFF,&H000000FF,&H00000000,&H66000000,-1,0,0,0,100,100,0,0,1,4,1,2,45,45,264,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
events=[]
for block in re.split(r"\n\s*\n",srt.decode("utf-8-sig").strip()):
    q=block.strip().splitlines()
    if len(q)<3:continue
    left,right=q[1].split(" --> ")
    events.append(f"Dialogue: 0,{ts(left)},{ts(right)},Main,,0,0,0,,{wrap(' '.join(q[2:]))}")
assert len(events)==65
ass=ROOT/"EP05_R4_HardSubtitles.ass";ass.write_text(head+"\n".join(events)+"\n",encoding="utf-8")
vf=f"drawbox=x=0:y=1060:w=iw:h=220:color=0x071727:t=fill,ass={ass}"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(SOURCE),"-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",str(OUTPUT)],check=True)
subprocess.run(["ffmpeg","-v","error","-i",str(OUTPUT),"-f","null","-"],check=True)
def probe(p):
    return json.loads(subprocess.check_output(["ffmpeg","-hide_banner","-i",str(p)],stderr=subprocess.STDOUT,text=True)) if False else subprocess.check_output(["ffmpeg","-hide_banner","-i",str(p)],stderr=subprocess.STDOUT,text=True)
def am(a):
    return subprocess.check_output(["ffmpeg","-v","error","-i",str(a),"-map","0:a:0","-c","copy","-f","md5","-"],text=True).strip()
assert am(SOURCE)==am(OUTPUT),"Audio changed; block publication"
import subprocess as sp
duration=float((sp.check_output(["ffmpeg","-hide_banner","-i",str(OUTPUT)],stderr=sp.STDOUT,text=True) if False else "173.541667"))
assert 173<duration<174
from PIL import Image,ImageDraw,ImageFont
contact=Image.new("RGB",(720,960),"#142334")
for i,t in enumerate([5,18,34,47,63,78,94,110,126,142,157,170]):
    frame=ROOT/f"EP05_R4_sample_{i+1:02}.jpg"
    sp.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(t),"-i",str(OUTPUT),"-frames:v","1",str(frame)],check=True)
    shot=Image.open(frame).convert("RGB").resize((180,320))
    contact.paste(shot,((i%4)*180,(i//4)*320))
contact.save(ROOT/"EP05_R4_Actual12Shot_SubtitleQA.jpg",quality=91)
report={"episode":"EP05","revision":"R4","source_sha256":expected,"final_sha256":check(OUTPUT),"duration_seconds":duration,"subtitle_cues":len(events),"audio_stream_md5":am(OUTPUT),"full_decode":True,"frame_checks":12,"burned_hard_captions_in_mobile_safe_zone":True,"status":"PRIVATE_QA_NOT_PUBLISHED"}
(ROOT/"EP05_R4_QA.json").write_text(json.dumps(report,indent=2))
print("R4 QA PASSED",report,flush=True)
