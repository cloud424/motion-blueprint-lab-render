#!/usr/bin/env python3
"""EP05: reproducible documentary-first hydropower master.

Authentic Pexels film in nine nonrepeating chapters, and three distinct
original moving engineering cutaways. Stages a PRIVATE QA master only.
All scene sources must appear in EP05_R3_New_Footage_Manifest.json.
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
DOC = pathlib.Path("episodes/EP05_Hydropower_R3.json")


def run(cmd):
    print("RUN", " ".join(map(str, cmd[:7])), flush=True)
    subprocess.run(list(map(str, cmd)), check=True)


def probe(path):
    p = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path)
    ])
    return json.loads(p)


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
    text(d, 681, 34, "EP05", FL, GOLD, anchor="ra")
    text(d, 38, 104, scene["title"], FH)
    text(d, 39, 160, scene["subtitle"], FL, MUTE)
    d.rounded_rectangle((27,225,693,1032),radius=28,fill="#112b40",outline="#41687b",width=3)
    d.rounded_rectangle((53,247,303,285),radius=12,fill="#1e6076")
    text(d, 70, 253, "ORIGINAL CUTAWAY", FL, "#defafd")
    kind = scene["mechanism"]
    if kind == "penstock_head":
        # Simplified vertical section through a generic dam and generating plant.
        d.rectangle((78,386,330,590), fill="#1d7797")
        for i in range(13):
            yy = 388 + i * 12
            d.line((80,yy,327,yy),fill="#2e90b0",width=1)
        d.polygon([(330,321),(399,321),(399,873),(330,873)],fill="#8a9eab")
        d.polygon([(399,873),(532,873),(532,943),(399,943)],fill="#526e80")
        text(d,97,338,"UPPER RESERVOIR",FL)
        text(d,407,896,"POWERHOUSE",FL)
        d.rectangle((307,522,365,562),fill="#f2c16b")
        # Water pressure pipe, concept only. Do not claim flood spillway drives turbine.
        path=[(298,543),(383,543),(443,578),(485,656),(516,779)]
        d.line(path, fill="#153547",width=63,joint="curve")
        d.line(path, fill="#3ed4ed",width=41,joint="curve")
        for k in range(9):
            q=(k/9+t*.15)%1
            idx=q*(len(path)-1)
            i=min(int(idx),len(path)-2);p=idx-i
            x=path[i][0]*(1-p)+path[i+1][0]*p
            y=path[i][1]*(1-p)+path[i+1][1]*p
            circle(d,x,y,7,"#c9faff")
        circle(d,520,813,61,GOLD,width=6)
        for k in range(6):
            a=t*2+k*math.tau/6
            d.line((520,813,520+50*math.cos(a),813+50*math.sin(a)),fill=GOLD,width=9)
        arrow(d,(585,806),(650,806),CYAN,6,15)
        d.line((94,394,94,806),fill=GOLD,width=4)
        arrow(d,(94,409),(94,770),GOLD,5,14)
        text(d,108,663,"HEAD",FT,GOLD)
        text(d,176,490,"INTAKE",FL)
        text(d,399,616,"PENSTOCK",FLL)
        text(d,544,847,"TURBINE",FLL)
        text(d,90,961,"ILLUSTRATIVE SECTION • NOT TO SCALE",FLL,MUTE)
    elif kind == "runner_vanes":
        cx,cy=360,618
        circle(d,cx,cy,289,"#36657b",7)
        for k in range(12):
            a=k*math.tau/12
            x,y=cx+247*math.cos(a),cy+247*math.sin(a)
            da=.22*math.sin(t*.6+k*.16)
            d.line((x-30*math.cos(a+da),y-30*math.sin(a+da),
                    x+30*math.cos(a+da),y+30*math.sin(a+da)),fill=GOLD,width=14)
        circle(d,cx,cy,184,CYAN,4)
        for j in range(4):
            rad=220-j*30
            d.arc((cx-rad,cy-rad,cx+rad,cy+rad),
                  (t*57+j*82)%360,(t*57+j*82+68)%360,fill=CYAN,width=8)
        for j in range(6):
            a=t*1.4+j*math.tau/6
            p=[(cx+28*math.cos(a-.5),cy+28*math.sin(a-.5)),
               (cx+160*math.cos(a-.15),cy+160*math.sin(a-.15)),
               (cx+160*math.cos(a+.17),cy+160*math.sin(a+.17)),
               (cx+29*math.cos(a+.5),cy+29*math.sin(a+.5))]
            d.polygon(p,fill="#73bbd0",outline="#ecfdff")
        circle(d,cx,cy,34,GOLD)
        arrow(d,(110,786),(201,786),CYAN,8)
        text(d,104,823,"WATER IN",FS,CYAN)
        arrow(d,(521,786),(615,786),GOLD,8)
        text(d,517,823,"SHAFT",FS,GOLD)
        text(d,89,940,"GUIDE VANES  →  ROTATING RUNNER",FL)
        text(d,89,978,"Simplified reaction turbine mechanism",FLL,MUTE)
    elif kind == "magnetic_induction":
        cx,cy=359,601
        circle(d,cx,cy,261,"#45637e",9)
        for k in range(12):
            a=k*math.tau/12
            x,y=cx+222*math.cos(a),cy+222*math.sin(a)
            d.arc((x-24,y-25,x+24,y+25),45,309,fill="#ffbc73",width=8)
        a=t*1.6
        d.ellipse((cx-157,cy-157,cx+157,cy+157),fill="#244664",outline="#74d5f7",width=6)
        x,y=math.cos(a),math.sin(a)
        d.polygon([(cx-140*y,cy+140*x),(cx+140*y,cy-140*x),
                   (cx-90*y+98*x,cy+90*x+98*y),
                   (cx+90*y+98*x,cy-90*x+98*y)],fill="#53aad2")
        circle(d,cx,cy,32,GOLD)
        text(d,cx+112*x-10,cy+112*y-19,"N",FT,"#ffb17f")
        text(d,cx-112*x-10,cy-112*y-19,"S",FT,CYAN)
        d.line((103,919,617,919),fill="#52708b",width=2)
        wave=[(x,918+45*math.sin(x*.035-t*2.8)) for x in range(103,618,5)]
        d.line(wave,fill=GOLD,width=4)
        text(d,107,974,"CHANGING FIELD  →  AC VOLTAGE",FLL)
        text(d,95,320,"GENERATOR CONCEPT: ROTATING FIELD",FLL,CYAN)
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
    title_file=outdir/f"EP05_title_{i:02d}.txt"
    subtitle_file=outdir/f"EP05_subtitle_{i:02d}.txt"
    title_file.write_text(scene["title"],encoding="utf-8")
    subtitle_file.write_text(scene["subtitle"],encoding="utf-8")
    info=probe(input_path)
    dur=float(info["format"]["duration"])
    if dur<SCENE_SEC:
        raise RuntimeError(f"Real clip too short: {input_path}")
    ss=min(max(.0,(dur-SCENE_SEC)/3),9)
    fontsize=35 if len(scene["title"])<25 else 29
    filt=(
       f"scale={W}:{H}:force_original_aspect_ratio=increase,"
       f"crop={W}:{H},setsar=1,fps={FPS},"
       "drawbox=x=0:y=0:w=iw:h=225:color=0x071b2b@0.82:t=fill,"
       "drawbox=x=0:y=1129:w=iw:h=151:color=0x071b2b@0.70:t=fill,"
       f"drawtext=fontfile={FONT_BOLD}:textfile={title_file}:fontcolor=white:"
       f"fontsize={fontsize}:x=35:y=106,"
       f"drawtext=fontfile={FONT_NORMAL}:textfile={subtitle_file}:fontcolor=0xCDE5EC:"
       "fontsize=20:x=38:y=165,"
       f"drawtext=fontfile={FONT_BOLD}:text='MOTION BLUEPRINT LAB  EP05':"
       "fontcolor=0x71E4E5:fontsize=17:x=37:y=37,"
       "drawtext=fontfile="+FONT_NORMAL+":text='AUTHENTIC FOOTAGE':"
       "fontcolor=0xB8EDF2:fontsize=15:x=35:y=1154"
    )
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-ss",f"{ss:.2f}","-i",input_path,"-t",str(SCENE_SEC),
         "-vf",filt,"-an","-c:v","libx264","-crf","21","-preset","veryfast",
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
            path=outdir/f"EP05_voice_orig_{i:02d}.wav"
            target=outdir/f"EP05_voice_atempo_{i:02d}.wav"
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
    path=outdir/"EP05_Narration_English_Kokoro.wav"
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
    path=outdir/"EP05_English_Subtitles.srt"
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
    path=outdir/"EP05_Original_Ambience.wav"
    sf.write(path,a,sr)
    return path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",default="out_EP05_R3_NEW_CLIPS")
    ap.add_argument("--out-dir",default="out_EP05_R3")
    args=ap.parse_args()
    raw=json.loads(DOC.read_text(encoding="utf-8"))
    scenes=raw["scenes"]
    assert raw["episode"]=="EP05" and raw["revision"]=="R3" and len(scenes)==12
    assert [x["n"] for x in scenes]==list(range(1,13))
    assert sum(x["type"]=="real" for x in scenes)==9
    assert {x["mechanism"] for x in scenes if x["type"]=="animation"}=={
        "penstock_head","runner_vanes","magnetic_induction"}
    footage_dir=pathlib.Path(args.source_dir)
    sources=json.loads((footage_dir/"EP05_R3_New_Footage_Manifest.json").read_text(encoding="utf-8"))
    selected=choose_clips(scenes,footage_dir,sources)
    out=pathlib.Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    segments=[]
    for s in scenes:
        dest=out/f"EP05_chapter_{s['n']:02d}.mp4"
        if s["type"]=="real":
            src=footage_dir/(selected[s["n"]]["slug"]+".mp4")
            render_real(s,src,dest,out)
        else:
            render_animation(s,dest)
        segments.append(dest)
        print("SCENE",s["n"],"OK",dest.stat().st_size,flush=True)
    listfile=out/"EP05_concat.txt"
    listfile.write_text("\n".join("file '"+x.name+"'" for x in segments)+"\n")
    merged=out/"EP05_Merged_Silent.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-f","concat","-safe","0","-i",listfile,
         "-c","copy",merged])
    vox,speachtimes,sr,data=voice_scenes(scenes,out)
    mus=ambience(sr,len(data),out)
    sub,ncues=subtitles(scenes,speachtimes,out)
    final=out/"EP05_Hydropower_R3_Documentary_173s_PRIVATE_QA.mp4"
    filt=f"subtitles='{sub}':force_style='FontName=DejaVu Sans,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00151515,Outline=2,Shadow=0,Alignment=2,MarginV=138'"
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
        thumb=out/f"EP05_shot_{k+1:02d}.jpg"
        run(["ffmpeg","-v","error","-y","-ss",f"{(k+.45)*SCENE_SEC:.3f}",
             "-i",final,"-frames:v","1",thumb])
        frame=Image.open(thumb).convert("RGB").resize((180,320))
        contact.paste(frame,((k%4)*180,(k//4)*320))
    contact.save(out/"EP05_R3_Actual12Shot_Storyboard.jpg",quality=94)
    credits=[dict(chapter=n,slug=r["slug"],pexels_id=r["pexels_id"],creator=r["contributor"],
                  source_url=r["page"],asset_url=r["url"],
                  source_sha256=sha256(footage_dir/(r["slug"]+".mp4")),
                  source_duration=r["duration"],licence_url=r["license"],
                  modification="Reframed, color adjusted, trimmed to unique 14.45s scene, source sound discarded")
             for n,r in sorted(selected.items())]
    report={
        "episode":"EP05","revision":"R3","status":"TECHNICAL_QA_PASSED_VISUAL_RIGHTS_REVIEW_PENDING",
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
    (out/"EP05_R3_Technical_Source_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("EP05_PRIVATE_REVIEW_SUCCESS",final,duration,final.stat().st_size,sha256(final),flush=True)


if __name__=="__main__":
    main()
