#!/usr/bin/env python3
"""EP06: reproducible documentary-first cargoship master.

Authentic Pexels film in nine nonrepeating chapters, and three distinct
original moving engineering cutaways. Stages a PRIVATE QA master only.
All scene sources must appear in EP06_R3_New_Footage_Manifest.json.
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
DOC = pathlib.Path("episodes/EP06_CargoShip_R3.json")


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
    text(d, 681, 34, "EP06", FL, GOLD, anchor="ra")
    text(d, 38, 104, scene["title"], FH)
    text(d, 39, 160, scene["subtitle"], FL, MUTE)
    d.rounded_rectangle((27,225,693,1032),radius=28,fill="#112b40",outline="#41687b",width=3)
    d.rounded_rectangle((53,247,303,285),radius=12,fill="#1e6076")
    text(d, 70, 253, "ORIGINAL CUTAWAY", FL, "#defafd")
    kind = scene["mechanism"]
    if kind == "hull_pressure":
        # Qualitative ship hull force distribution, pressure increases with depth.
        sea=635+3*math.sin(t*.7)
        d.rectangle((65,int(sea),655,983),fill="#155e8d")
        for k in range(7):
            y=sea+25+k*44
            d.arc((73,y-12,645,y+12),0,180,fill="#39a8c7",width=3)
        hull=[(145,500),(577,500),(541,782),(216,782)]
        d.polygon(hull,fill="#accbd5",outline="#e5fbff")
        d.polygon([(154,516),(567,516),(548,690),(209,690)],fill="#173a50")
        for k in range(5):
            xx=180+k*72
            d.rectangle((xx,453,xx+62,496),fill=GOLD if k%2 else "#5ba8c7",outline="#e1f6fa",width=2)
        for k in range(5):
            x=246+k*62
            y=735+16*(k%2)
            arrow(d,(x,y+75),(x,y),CYAN,5,14)
        arrow(d,(369,356),(369,492),GOLD,9,20)
        arrow(d,(369,899),(369,778),CYAN,9,20)
        text(d,97,327,"HYDROSTATIC PRESSURE",FT)
        text(d,388,390,"WEIGHT",FL,GOLD)
        text(d,406,873,"LIFT",FL,CYAN)
        text(d,93,959,"Simplified section; forces not to scale",FLL,MUTE)
    elif kind == "displaced_volume":
        # Heavier loading increases draft, thus increases displaced water.
        phase=.5-.5*math.cos(t*.36)
        sea=645
        sinking=20+70*phase
        top=498+sinking
        d.rectangle((68,sea,660,985),fill="#196b93")
        d.line((68,sea,660,sea),fill="#d4ffff",width=5)
        hull=[(150,top),(570,top),(544,top+200),(214,top+200)]
        d.polygon(hull,fill="#a3bfcc",outline="#ecfbff")
        d.polygon([(160,top+10),(560,top+10),(550,top+102),(210,top+102)],fill="#224355")
        visible=3+int(4*phase)
        for k in range(visible):
            x=176+(k%4)*94
            y=top-42-(k//4)*43
            d.rectangle((x,y,x+74,y+35),fill=GOLD if k%2 else "#7bc0d8",outline="#f3ffff",width=2)
        for k in range(7):
            y=sea+23+k*42
            d.arc((76,y-14,652,y+14),0,180,fill="#3bb0d4",width=2)
        d.rectangle((219,sea,543,min(int(top+199),985)),outline=CYAN,width=4)
        arrow(d,(601,420),(601,609+65*phase),GOLD,8,19)
        arrow(d,(100,917),(100,774),CYAN,8,19)
        text(d,95,332,"MORE CARGO  →  MORE DRAFT",FT)
        text(d,96,820,"WATER",FLL,CYAN)
        text(d,96,846,"DISPLACED",FLL,CYAN)
        text(d,446,374,"ADDED",FLL,GOLD)
        text(d,446,402,"WEIGHT",FLL,GOLD)
        text(d,92,961,"Floating weight = displaced-water weight",FLL,MUTE)
    elif kind == "ship_stability":
        # A conceptual righting moment, not a numeric stability prediction.
        a=.15*math.sin(t*.54)
        cx,cy=359,612
        def turn(x,y):
            x0=x-cx;y0=y-cy
            return (cx+x0*math.cos(a)-y0*math.sin(a),
                    cy+x0*math.sin(a)+y0*math.cos(a))
        sea=683
        d.rectangle((60,sea,662,1000),fill="#116c91")
        for k in range(8):
            y=sea+13+k*35
            d.arc((68,y-10,655,y+10),0,180,fill="#31a4c8",width=3)
        hull=[(136,531),(581,531),(536,750),(211,750)]
        rotated=[turn(x,y) for x,y in hull]
        d.polygon(rotated,fill="#adc8d2",outline="#f2faff")
        interior=[turn(x,y) for x,y in [(149,542),(567,542),(527,642),(222,642)]]
        d.polygon(interior,fill="#22435a")
        for k in range(4):
            pos=turn(187+k*88,493)
            d.rectangle((pos[0]-28,pos[1]-22,pos[0]+29,pos[1]+20),fill=GOLD if k%2 else "#65aac7")
        G=turn(357,620)
        B=(357+110*math.sin(a*3),721-9*math.cos(a))
        circle(d,*G,16,GOLD)
        circle(d,*B,16,CYAN)
        arrow(d,(G[0],G[1]-135),G,GOLD,8,20)
        arrow(d,(B[0],B[1]+136),B,CYAN,8,20)
        text(d,G[0]-8,G[1]-47,"G",FLL,GOLD)
        text(d,B[0]+20,B[1]+8,"B",FLL,CYAN)
        d.line((78,sea,638,sea),fill="#defaff",width=4)
        text(d,94,332,"HEEL CHANGES BUOYANCY LOCATION",F(24,True))
        text(d,88,919,"G: center of gravity    B: center of buoyancy",FLL)
        text(d,88,957,"Conceptual restoring moment, not to scale",FLL,MUTE)
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
    d.text((37,37),"MOTION BLUEPRINT LAB  EP06",font=F(17,True),fill=(113,228,229,255))
    d.text((35,1154),"AUTHENTIC FOOTAGE",font=F(15),fill=(184,237,242,255))
    overlay_path=outdir/f"EP06_film_overlay_{i:02d}.png"
    overlay.save(overlay_path)
    info=probe(input_path)
    dur=float(info["format"]["duration"])
    if dur<SCENE_SEC:
        raise RuntimeError(f"Real clip too short: {input_path}")
    ss=min(max(.0,(dur-SCENE_SEC)/3),9)
    vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"
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
            f=footage_dir/(slug+".mp4")
            if (r and f.is_file() and f.stat().st_size>100000
               and str(r["pexels_id"]) not in usedids
               and slug not in usedfiles
               and float(r["duration"])>=SCENE_SEC):
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
            path=outdir/f"EP06_voice_orig_{i:02d}.wav"
            target=outdir/f"EP06_voice_atempo_{i:02d}.wav"
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
    path=outdir/"EP06_Narration_English_Kokoro.wav"
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
    path=outdir/"EP06_English_Subtitles.srt"
    path.write_text(text_data+"\n",encoding="utf-8")
    return path,len(cues)


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
    path=outdir/"EP06_Original_Ambience.wav"
    sf.write(path,a,sr)
    return path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",default="out_EP06_R3_NEW_CLIPS")
    ap.add_argument("--out-dir",default="out_EP06_R3")
    args=ap.parse_args()
    raw=json.loads(DOC.read_text(encoding="utf-8"))
    scenes=raw["scenes"]
    assert raw["episode"]=="EP06" and raw["revision"]=="R3" and len(scenes)==12
    assert [x["n"] for x in scenes]==list(range(1,13))
    assert sum(x["type"]=="real" for x in scenes)==9
    assert {x["mechanism"] for x in scenes if x["type"]=="animation"}=={
        "hull_pressure","displaced_volume","ship_stability"}
    footage_dir=pathlib.Path(args.source_dir)
    sources=json.loads((footage_dir/"EP06_R3_New_Footage_Manifest.json").read_text(encoding="utf-8"))
    selected=choose_clips(scenes,footage_dir,sources)
    out=pathlib.Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    segments=[]
    for s in scenes:
        dest=out/f"EP06_chapter_{s['n']:02d}.mp4"
        if s["type"]=="real":
            src=footage_dir/(selected[s["n"]]["slug"]+".mp4")
            render_real(s,src,dest,out)
        else:
            render_animation(s,dest)
        segments.append(dest)
        print("SCENE",s["n"],"OK",dest.stat().st_size,flush=True)
    listfile=out/"EP06_concat.txt"
    listfile.write_text("\n".join("file '"+x.name+"'" for x in segments)+"\n")
    merged=out/"EP06_Merged_Silent.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-f","concat","-safe","0","-i",listfile,
         "-c","copy",merged])
    vox,speachtimes,sr,data=voice_scenes(scenes,out)
    mus=ambience(sr,len(data),out)
    sub,ncues=subtitles(scenes,speachtimes,out)
    final=out/"EP06_CargoShip_R3_Documentary_173s_PRIVATE_QA.mp4"
    filt=f"subtitles='{sub}':force_style='FontName=DejaVu Sans,FontSize=7,PrimaryColour=&H00FFFFFF,OutlineColour=&H00151515,Outline=1,Shadow=0,Alignment=2,MarginV=27'"
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
        thumb=out/f"EP06_shot_{k+1:02d}.jpg"
        run(["ffmpeg","-v","error","-y","-ss",f"{(k+.45)*SCENE_SEC:.3f}",
             "-i",final,"-frames:v","1",thumb])
        frame=Image.open(thumb).convert("RGB").resize((180,320))
        contact.paste(frame,((k%4)*180,(k//4)*320))
    contact.save(out/"EP06_R3_Actual12Shot_Storyboard.jpg",quality=94)
    credits=[dict(chapter=n,slug=r["slug"],pexels_id=r["pexels_id"],creator=r["contributor"],
                  source_url=r["page"],asset_url=r["url"],
                  source_sha256=sha256(footage_dir/(r["slug"]+".mp4")),
                  source_duration=r["duration"],licence_url=r["license"],
                  modification="Reframed, color adjusted, trimmed to unique 14.45s scene, source sound discarded")
             for n,r in sorted(selected.items())]
    report={
        "episode":"EP06","revision":"R3","status":"TECHNICAL_QA_PASSED_VISUAL_RIGHTS_REVIEW_PENDING",
        "published":False,"qa_approval":"pending",
        "media":final.name,"sha256":sha256(final),"duration":duration,"width":720,"height":1280,"fps":24,
        "real_seconds":9*SCENE_SEC,"real_ratio":.75,"unique_source_ids":len({r["pexels_id"] for r in selected.values()}),
        "distinct_original_mechanisms":3,"on_screen_caption_events":ncues,
        "scientific_sources":raw["scientific_sources"],"credits":credits,
        "notes":["Every source used only once; all real footage is modern and illustrative",
                 "Flood spillways bypass generating turbines: text explicitly distinguishes these paths",
                 "Automatic codec/audio/no-repeat test passed; full human-level visual/rights review still required",
                 "Never publish until authorized by separate review and official links verified"]
    }
    (out/"EP06_R3_Technical_Source_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("EP06_PRIVATE_REVIEW_SUCCESS",final,duration,final.stat().st_size,sha256(final),flush=True)


if __name__=="__main__":
    main()
