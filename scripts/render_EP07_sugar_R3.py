#!/usr/bin/env python3
"""EP07: reproducible documentary-first cargoship master.

Authentic Pexels film in nine nonrepeating chapters, and three distinct
original moving engineering cutaways. Stages a PRIVATE QA master only.
All scene sources must appear in EP07_Source_Acquisition_Report.json.
"""
import argparse
import hashlib
import json
import math
import os
import pathlib
import re
import subprocess
import sys

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 24
SCENE_FRAMES = 347
SCENE_SEC = SCENE_FRAMES / FPS
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_NORMAL = FONT_DIR + "/DejaVuSans.ttf"
FONT_BOLD = FONT_DIR + "/DejaVuSans-Bold.ttf"
BG = "#081a2b"
CYAN = "#51e0e5"
INK = "#eaf6f7"
GOLD = "#f7c36c"
MUTE = "#acc6d1"
DOC = pathlib.Path("episodes/EP07_TraditionalSugar_R3_Draft.json")


def run(cmd):
    print("RUN", " ".join(map(str, cmd[:7])), flush=True)
    subprocess.run(list(map(str, cmd)), check=True)


def probe(path):
    try:
        p = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_format", "-show_streams",
            "-of", "json", str(path)
        ])
        return json.loads(p)
    except FileNotFoundError:
        # The portable PyPI ffmpeg bundle does not ship a separate ffprobe.
        # Read the stream header using exactly the bundled ffmpeg binary instead.
        q=subprocess.run(["ffmpeg","-hide_banner","-i",str(path),
                          "-frames:v","1","-an","-f","null","-"],
                         capture_output=True,text=True,timeout=45)
        head=q.stderr
        d=re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)",head)
        v=re.search(r"Video:\s*([a-zA-Z0-9_]+)[^\n]*?(\d{3,5})x(\d{3,5})",head)
        a=re.search(r"Audio:\s*([a-zA-Z0-9_]+)",head)
        if q.returncode or not d or not v:
            raise RuntimeError("portable ffmpeg metadata verification failed: "+head[-600:])
        duration=int(d.group(1))*3600+int(d.group(2))*60+float(d.group(3))
        streams=[{"codec_type":"video","codec_name":v.group(1),
                  "width":int(v.group(2)),"height":int(v.group(3))}]
        if a:
            streams.append({"codec_type":"audio","codec_name":a.group(1)})
        return {"format":{"duration":str(duration)},"streams":streams}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            part = f.read(4 * 1024 * 1024)
            if not part:
                break
            h.update(part)
    return h.hexdigest()


def F(px, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_NORMAL, px)


FT = F(27, True)
FS = F(22)
FL = F(19)
FH = F(33, True)
FLL = F(17)


def text(d, x, y, value, font=FS, color=INK, anchor=None):
    d.text((int(x), int(y)), value, font=font, fill=color, anchor=anchor)


def circle(d, x, y, r, color, width=None):
    a = (int(x-r), int(y-r), int(x+r), int(y+r))
    if width is None:
        d.ellipse(a, fill=color)
    else:
        d.ellipse(a, outline=color, width=width)


def arrow(d, a, b, color=CYAN, width=7, head=17):
    ax, ay = a
    bx, by = b
    dx, dy = bx-ax, by-ay
    dist = max(1, math.hypot(dx, dy))
    ux, uy = dx/dist, dy/dist
    px, py = -uy, ux
    d.line((int(ax), int(ay), int(bx), int(by)), fill=color, width=width)
    d.polygon([
        (int(bx), int(by)),
        (int(bx-ux*head+px*head*.48), int(by-uy*head+py*head*.48)),
        (int(bx-ux*head-px*head*.48), int(by-uy*head-py*head*.48))
    ], fill=color)


def arrow_curve(d, pts, color=CYAN, width=7):
    d.line([(int(x),int(y)) for x,y in pts], fill=color, width=width, joint="curve")


def draw_frame(scene, t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 58):
        d.line((x,0,x,H), fill="#102a3b", width=1)
    for y in range(0,H,58):
        d.line((0,y,W,y), fill="#102a3b", width=1)
    d.rectangle((0, 0, W, 12), fill=CYAN)
    text(d, 35, 33, "MOTION BLUEPRINT LAB", FL, CYAN)
    text(d, 681, 34, "EP07", FL, GOLD, anchor="ra")
    text(d, 38, 104, scene["title"], FH)
    text(d, 39, 160, scene["subtitle"], FL, MUTE)
    d.rounded_rectangle((27,225,693,1032),radius=28,fill="#112b40",outline="#41687b",width=3)
    d.rounded_rectangle((53,247,303,285),radius=12,fill="#1e6076")
    text(d, 70, 253, "ORIGINAL CUTAWAY", FL, "#defafd")
    kind = scene["mechanism"]
    if kind == "manual_cane_press_force":
        d.rounded_rectangle((74,330,643,947),radius=22,fill="#102d43",outline=CYAN,width=3)
        text(d,103,354,"PRESSURE EXTRACTS JUICE",F(24,True))
        for n in range(2):
            cy=520+n*178
            cx=356
            d.ellipse((cx-108,cy-108,cx+108,cy+108),fill="#547a89",outline="#dbfaff",width=7)
            a=t*(2.8 if n==0 else -2.8)
            for k in range(8):
                ang=a+k*math.pi/4
                d.line((cx+39*math.cos(ang),cy+39*math.sin(ang),
                        cx+98*math.cos(ang),cy+98*math.sin(ang)),fill="#b4dce5",width=6)
        travel=18*math.sin(t*.6)
        d.rectangle((83,592+travel,650,637+travel),fill="#86b957")
        for k in range(10):
            xx=93+k*55
            d.line((xx,599+travel,xx+17,628+travel),fill="#cae69b",width=4)
        for k in range(6):
            y=765+(t*25+k*33)%95
            d.ellipse((263+k*30,y,272+k*30,y+17),fill=CYAN)
        arrow(d,(119,462),(210,462),GOLD,7,16)
        arrow(d,(540,792),(540,900),CYAN,7,19)
        text(d,110,902,"JUICE LEAVES THE FIBERS",F(20,True),CYAN)
        text(d,89,969,"Conceptual press, not a 1792 reconstruction",FLL,MUTE)
    elif kind == "open_pan_evaporation":
        d.rounded_rectangle((74,329,645,938),radius=20,fill="#173748",outline="#55979d",width=3)
        text(d,105,350,"HEAT REMOVES WATER",F(27,True))
        d.rectangle((120,690,604,806),fill="#79543b",outline=GOLD,width=8)
        d.rectangle((132,690,590,732),fill="#dea34f")
        for k in range(14):
            xx=146+(k*39+int(t*38))%431
            yy=716-((k+int(t*2))%3)*8
            rad=4+(k%3)*3
            d.ellipse((xx-rad,yy-rad,xx+rad,yy+rad),outline="#fff1af",width=4)
        for k in range(6):
            xx=160+k*76
            yy=622-(int(t*27+k*45)%213)
            d.arc((xx-20,yy-15,xx+22,yy+22),10,165,fill="#bce8f1",width=5)
        for k in range(5):
            cx=147+k*98
            amp=39+13*math.sin(t*4+k)
            d.polygon(((cx,827),(cx+16,827-amp),(cx+32,827)),fill=GOLD)
        arrow(d,(550,487),(550,414),CYAN,8,19)
        text(d,97,847,"FIRE AND EVAPORATION",F(22,True),GOLD)
        text(d,90,961,"Thicker syrup as water leaves the pan",FLL,MUTE)
    elif kind == "jaggery_cooling_and_setting":
        d.rounded_rectangle((76,333,642,935),radius=20,fill="#113748",outline=CYAN,width=3)
        text(d,101,354,"SYRUP COOLS AND SETS",F(24,True))
        d.polygon(((208,477),(509,477),(474,563),(244,563)),fill="#b97b3e",outline=GOLD)
        d.polygon(((244,563),(474,563),(463,666),(251,666)),fill="#9c5b35")
        d.rectangle((139,731,579,855),fill="#3f6470",outline="#d4e9ed",width=6)
        fullness=min(1,t/SCENE_SEC)
        for k in range(4):
            px=153+k*104
            top=843-24-55*fullness
            d.rounded_rectangle((px,top,px+91,848),radius=7,fill="#bb7e3f",outline=GOLD,width=3)
            for j in range(12):
                cx=px+7+(j*27)%77;cy=top+7+(j*13)%max(16,int(65*fullness+20))
                d.ellipse((cx,cy,cx+3,cy+3),fill="#f6ce8a")
        if t<SCENE_SEC*.83:
            d.polygon(((343,642),(369,642),(374,745),(341,745)),fill="#dda75b")
        arrow(d,(574,506),(574,596),GOLD,8,18)
        text(d,96,888,"SEMI-CRYSTALLINE CANE SWEETENER",F(18,True),CYAN)
        text(d,94,961,"Jaggery is not refined white sugar",FLL,MUTE)
    else:
        raise ValueError("Unknown mechanism: "+str(kind))
    d.rectangle((0,1239,W,H),fill="#081c2c")
    d.rectangle((31,1259,689,1267),fill="#23475e")
    d.rectangle((31,1259,31+int(658*t/SCENE_SEC),1267),fill=CYAN)
    return img


def render_animation(scene, dest):
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo",
         "-pixel_format","rgb24","-video_size",f"{W}x{H}",
         "-framerate",str(FPS),"-i","-","-an",
         "-c:v","libx264","-preset","ultrafast","-crf","22",
         "-pix_fmt","yuv420p","-r",str(FPS),str(dest)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for f in range(SCENE_FRAMES):
            process.stdin.write(draw_frame(scene,f/FPS).tobytes())
        process.stdin.close()
        err=process.stderr.read()
        if process.wait()!=0:
            raise RuntimeError("draw ffmpeg failed "+err.decode(errors="replace")[-1000:])
    finally:
        if process.poll() is None:process.kill()


def render_real(scene, input_path, dest, outdir):
    i=scene["n"]
    # Draw all captions as an original alpha PNG; portable FFmpeg does not have
    # drawtext and must NOT depend on Apt packages during unattended runs.
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    d.rectangle((0,0,W,225),fill=(7,27,43,206))
    d.rectangle((0,1129,W,H),fill=(7,27,43,177))
    title_font=F(35 if len(scene["title"])<25 else 29,True)
    d.text((35,106),scene["title"],font=title_font,fill=(255,255,255,255))
    d.text((38,165),scene["subtitle"],font=F(20),fill=(205,229,236,255))
    d.text((37,37),"MOTION BLUEPRINT LAB  EP07",font=F(17,True),fill=(113,228,229,255))
    d.text((35,1154),"MODERN REAL DEMONSTRATION",font=F(15),fill=(184,237,242,255))
    overlay_path=outdir/f"EP07_film_overlay_{i:02d}.png"
    overlay.save(overlay_path)
    info=probe(input_path)
    dur=float(info["format"]["duration"])
    if dur < SCENE_SEC * .83:
        raise RuntimeError(f"Real clip too short to retime without obvious unnatural motion: {input_path}")
    # An authentic 12.3s harvest shot may be played at 0.85x (not repeated
    # or converted into still frames), so it can fill a unique 14.46s scene.
    slow = max(1.0,SCENE_SEC/dur)
    ss=0 if slow>1 else min(max(.0,(dur-SCENE_SEC)/3),9)
    vf=(f"setpts={slow:.8f}*(PTS-STARTPTS),"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"setsar=1,fps={FPS}")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-ss",f"{ss:.2f}","-i",input_path,
         "-loop","1","-i",overlay_path,
         "-t",str(SCENE_SEC),
         "-filter_complex",f"[0:v]{vf}[base];[base][1:v]overlay=0:0:shortest=1[v]",
         "-map","[v]","-an","-c:v","libx264","-crf","21","-preset","veryfast",
         "-pix_fmt","yuv420p","-r",str(FPS),str(dest)])
    dat=probe(dest)
    duration=float(dat["format"]["duration"])
    if abs(duration-SCENE_SEC)>.08:
        raise RuntimeError(f"Unexpected film scene duration {i}: {duration}")

def choose_clips(scenes, footage_dir, records):
    byslug={r["slug"]:r for r in records}
    usedids=set()
    usedfiles=set()
    selected={}
    for scene in scenes:
        if scene["type"]!="real":
            continue
        match=None
        for slug in scene["clip_candidates"]:
            r=byslug.get(slug)
            f=footage_dir/(slug+(".webm" if r and r.get("source_type")=="wikimedia_commons" else ".mp4"))
            if (r and f.is_file() and f.stat().st_size>100000
               and str(r["pexels_id"]) not in usedids
               and slug not in usedfiles
               and float(r["duration"])>=SCENE_SEC*.83):
                match=r;break
        if not match:
            raise RuntimeError("Cannot fill original real scene "+str(scene["n"])+
                               " from available validated sources. BLOCK, no duplicate.")
        selected[scene["n"]]=match
        usedids.add(str(match["pexels_id"]))
        usedfiles.add(match["slug"])
    assert len(selected)==9 and len(usedids)==9
    return selected


def voice_scenes(scenes,outdir):
    from kokoro import KPipeline
    pipe=KPipeline(lang_code="a",repo_id="hexgrad/Kokoro-82M")
    sr=24000
    words=[]
    audio_segments=[]
    voice_seconds=[]
    for i,s in enumerate(scenes):
        packets=[]
        for _gr,_ph,wav in pipe(s["narration"],voice="am_michael",speed=1.24):
            packets.append(np.asarray(wav,dtype=np.float32))
        if not packets:
            raise RuntimeError("No audio for "+str(s["n"]))
        speech=np.concatenate(packets)
        lim=int((SCENE_SEC-.8)*sr)
        if len(speech)>lim:
            factor=len(speech)/lim
            if factor>1.36:
                raise RuntimeError(f"Narration scene {s['n']} too long to sound natural: {factor:.3f}")
            path=outdir/f"EP07_voice_orig_{i:02d}.wav"
            target=outdir/f"EP07_voice_atempo_{i:02d}.wav"
            sf.write(path,speech,sr)
            run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",path,
                 "-af",f"atempo={factor:.6f}","-ar",str(sr),target])
            speech,sr2=sf.read(target,dtype="float32")
            if sr2!=sr:raise RuntimeError("Voice resample mismatch")
        speech=np.asarray(speech,dtype=np.float32)
        prefix=np.zeros(int(.45*sr),dtype=np.float32)
        padded=np.concatenate((prefix,speech))
        if len(padded)>SCENE_FRAMES/FPS*sr:
            raise RuntimeError("Voice chapter too long after speed correction")
        padded=np.pad(padded,(0,int(SCENE_SEC*sr)-len(padded)))
        audio_segments.append(padded)
        voice_seconds.append(len(speech)/sr)
        words.append(len(s["narration"].split()))
        print("VOICE",s["n"],"words",words[-1],"secs",round(voice_seconds[-1],2),flush=True)
    full=np.concatenate(audio_segments)
    path=outdir/"EP07_Narration_English_Kokoro.wav"
    sf.write(path,full,sr)
    return path, voice_seconds, sr, full


def SRT_TIME(t):
    msec=round(1000*t)
    hour,ms=divmod(msec,3600000)
    minute,ms=divmod(ms,60000)
    sec,ms=divmod(ms,1000)
    return f"{hour:02}:{minute:02}:{sec:02},{ms:03}"


def subtitles(scenes, speech_times, outdir):
    cues=[]
    for j,sc in enumerate(scenes):
        content=re.split(r"(?<=[.!?])\s+",sc["narration"])
        parts=[]
        for sentence in content:
            sentence=sentence.strip()
            words=sentence.split()
            while words:
                k=min(9,len(words))
                parts.append(" ".join(words[:k]))
                words=words[k:]
        total=sum(len(x.split()) for x in parts)
        start=j*SCENE_SEC+.42
        stop=start+speech_times[j]
        now=start
        for k,p in enumerate(parts):
            dt=(stop-start)*len(p.split())/total
            nxt=stop if k==len(parts)-1 else now+dt
            if nxt-now>=.48:cues.append((now,nxt,p))
            now=nxt
    text_data="\n\n".join(f"{i}\n{SRT_TIME(start)} --> {SRT_TIME(end)}\n{line}"
                           for i,(start,end,line) in enumerate(cues,1))
    path=outdir/"EP07_English_Subtitles.srt"
    path.write_text(text_data+"\n",encoding="utf-8")
    return path,len(cues)



def build_mobile_safe_ass(subtitle_srt,outdir):
    """Burn actual English captions in video pixels above the Shorts/Reels UI overlay."""
    from PIL import ImageFont
    font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",40)
    def wrap(txt):
        lines=[];cur=""
        for word in txt.split():
            proposed=(cur+" "+word).strip()
            if font.getlength(proposed)>640 and cur:
                lines.append(cur);cur=word
            else:cur=proposed
        if cur:lines.append(cur)
        return r"\N".join(lines)
    def conv(ts):
        h,m,x=ts.split(":");sec,ms=x.split(",")
        return f"{int(h)}:{int(m):02}:{int(sec):02}.{int(ms)//10:02}"
    header="""[Script Info]
Title: EP07 Mobile-Safe Hard Captions
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
    for block in re.split(r"\n\s*\n",subtitle_srt.read_text(encoding="utf-8-sig").strip()):
        q=block.splitlines()
        if len(q)<3:continue
        begin,end=q[1].split(" --> ")
        events.append(f"Dialogue: 0,{conv(begin)},{conv(end)},Main,,0,0,0,,{wrap(' '.join(q[2:]))}")
    if len(events)<30:raise RuntimeError("Too few caption events: block publication")
    dst=outdir/"EP07_R3_MobileSafe_English_Captions.ass"
    dst.write_text(header+"\n".join(events)+"\n",encoding="utf-8")
    return dst,len(events)

def ambience(sr,n,outdir):
    t=np.arange(n,dtype=np.float32)/sr
    a=np.zeros(n,dtype=np.float32)
    for freq,amp in [(73.42,.005),(110,.005),(146.83,.004),(220,.002)]:
        a+=amp*np.sin(2*np.pi*freq*t+.5*np.sin(2*np.pi*.027*t))
    for beat in range(0,int(n/sr),4):
        z=beat*sr
        m=min(sr//2,n-z)
        if m>0:
            tau=np.arange(m,dtype=np.float32)/sr
            a[z:z+m]+=.008*np.exp(-15*tau)*np.sin(2*np.pi*98*tau)
    a*=np.minimum(1,t/2.5)*np.minimum(1,(n/sr-t)/3)
    path=outdir/"EP07_Original_Ambience.wav"
    sf.write(path,a,sr)
    return path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",default="out_EP07_sources")
    ap.add_argument("--out-dir",default="out_EP07_R3")
    args=ap.parse_args()
    raw=json.loads(DOC.read_text(encoding="utf-8"))
    scenes=raw["scenes"]
    assert raw["episode"]=="EP07" and raw["revision"]=="R3" and len(scenes)==12
    assert [x["n"] for x in scenes]==list(range(1,13))
    assert sum(x["type"]=="real" for x in scenes)==9
    assert {x["mechanism"] for x in scenes if x["type"]=="animation"}=={
        "manual_cane_press_force","open_pan_evaporation","jaggery_cooling_and_setting"}
    footage_dir=pathlib.Path(args.source_dir)
    acq=json.loads((footage_dir/"EP07_Source_Acquisition_Report.json").read_text(encoding="utf-8"))
    sources=[z["meta"] for z in acq["outputs"] if z.get("result")=="downloaded_valid_media_not_release_approved"]
    selected=choose_clips(scenes,footage_dir,sources)
    out=pathlib.Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    segments=[]
    for s in scenes:
        dest=out/f"EP07_chapter_{s['n']:02d}.mp4"
        if s["type"]=="real":
            src=footage_dir/(selected[s["n"]]["slug"]+(".webm" if selected[s["n"]].get("source_type")=="wikimedia_commons" else ".mp4"))
            render_real(s,src,dest,out)
        else:
            render_animation(s,dest)
        segments.append(dest)
        print("SCENE",s["n"],"OK",dest.stat().st_size,flush=True)
    listfile=out/"EP07_concat.txt"
    listfile.write_text("\n".join("file '"+x.name+"'" for x in segments)+"\n")
    merged=out/"EP07_Merged_Silent.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-f","concat","-safe","0","-i",listfile,
         "-c","copy",merged])
    vox,speachtimes,sr,data=voice_scenes(scenes,out)
    mus=ambience(sr,len(data),out)
    sub,ncues=subtitles(scenes,speachtimes,out)
    ass,hardcues=build_mobile_safe_ass(sub,out)
    assert hardcues==ncues
    final=out/"EP07_TraditionalSugar_R3_Documentary_173s_PRIVATE_QA.mp4"
    filt=f"subtitles='{ass}'"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-i",merged,"-i",vox,"-i",mus,
         "-filter_complex",f"[0:v]{filt}[v];[1:a]volume=1.35[s];[2:a]volume=0.65[m];[s][m]amix=inputs=2:duration=first:normalize=0[a]",
         "-map","[v]","-map","[a]","-r",str(FPS),
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","160k","-movflags","+faststart",final])
    inf=probe(final)
    duration=float(inf["format"]["duration"])
    v=[s for s in inf["streams"] if s["codec_type"]=="video"]
    a=[s for s in inf["streams"] if s["codec_type"]=="audio"]
    assert 172<duration<175,(duration,inf)
    assert len(v)==1 and v[0]["width"]==720 and v[0]["height"]==1280 and v[0]["codec_name"]=="h264"
    assert len(a)==1 and a[0]["codec_name"]=="aac"
    run(["ffmpeg","-v","error","-i",final,"-f","null","-"])
    contact=Image.new("RGB",(720,960),"#142334")
    for k in range(12):
        thumb=out/f"EP07_shot_{k+1:02d}.jpg"
        run(["ffmpeg","-v","error","-y","-ss",f"{(k+.45)*SCENE_SEC:.3f}",
             "-i",final,"-frames:v","1",thumb])
        frame=Image.open(thumb).convert("RGB").resize((180,320))
        contact.paste(frame,((k%4)*180,(k//4)*320))
    contact.save(out/"EP07_R3_Actual12Shot_Storyboard.jpg",quality=94)
    credits=[dict(chapter=n,slug=r["slug"],pexels_id=r["pexels_id"],creator=r["contributor"],
                  source_url=r["page"],asset_url=r["asset_url"],
                  source_sha256=sha256(footage_dir/(r["slug"]+(".webm" if r.get("source_type")=="wikimedia_commons" else ".mp4"))),
                  source_duration=r["duration"],licence_url=r["license"],
                  modification="Reframed, color adjusted, trimmed to unique 14.45s scene, source sound discarded")
             for n,r in sorted(selected.items())]
    report={
        "episode":"EP07","revision":"R3","status":"TECHNICAL_QA_PASSED_VISUAL_RIGHTS_REVIEW_PENDING",
        "published":False,"qa_approval":"pending",
        "media":final.name,"sha256":sha256(final),"duration":duration,"width":720,"height":1280,"fps":24,
        "real_seconds":9*SCENE_SEC,"real_ratio":.75,"unique_source_ids":len({r["pexels_id"] for r in selected.values()}),
        "distinct_original_mechanisms":3,"on_screen_caption_events":ncues,"burned_caption_profile":{"font_px":40,"black_outline_px":4,"ass_margin_bottom_px":264,"play_res":[720,1280],"pixel_overlay_required":True},
        "scientific_sources":list(raw["sources"].values()),"credits":credits,
        "notes":["Every source used only once; all real footage is modern and illustrative",
                 "Do not claim modern film is historic archival footage",
                 "Automatic codec/audio/no-repeat test passed; full human-level visual/rights review still required",
                 "Never publish until authorized by separate review and official links verified"]
    }
    (out/"EP07_R3_Technical_Source_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("EP07_PRIVATE_REVIEW_SUCCESS",final,duration,final.stat().st_size,sha256(final),flush=True)


if __name__=="__main__":
    main()
