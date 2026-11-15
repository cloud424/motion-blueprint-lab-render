#!/usr/bin/env python3
"""Finalize the existing EP03 Github artifact; no paid media APIs."""
import argparse, ast, json, math, pathlib, re, subprocess

TARGET=174.916667
def run(cmd):
    subprocess.run(cmd,check=True)

def fmt(t):
    ms=round(t*1000); h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def wrap(words,width=38):
    lines=[];line=""
    for word in words:
        if line and len(line)+1+len(word)>width:
            lines.append(line);line=word
        else:
            line=(line+" "+word).strip()
    if line:lines.append(line)
    return "\n".join(lines)

def chapters_from_renderer(pyfile):
    tree=ast.parse(pyfile.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="SCENES" for t in node.targets):
            return [s[1] for s in ast.literal_eval(node.value)]
    raise ValueError("EP03 narration missing")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="out")
    args=ap.parse_args()
    out=pathlib.Path(args.outdir);out.mkdir(parents=True,exist_ok=True)
    report=json.loads((out/"EP03_AncientSeaSalt_Report.json").read_text())
    scenes=chapters_from_renderer(pathlib.Path("scripts/render_EP03_seasalt.py"))
    assert len(scenes)==len(report["chapters"])==12
    assert report["episode"]=="EP03"
    src=out/report["file"]
    assert src.is_file() and src.stat().st_size>2000000
    dur=float(report["duration"])
    speed=dur/TARGET
    assert 0.95<speed<1.15,(dur,speed)
    entries=[]
    for ch,body in zip(report["chapters"],scenes):
        groups=[]
        for sentence in re.findall(r"[^.!?]+[.!?]?",body.strip()):
            words=sentence.strip().split()
            if not words:continue
            count=max(1,math.ceil(len(sentence.strip())/65))
            pos=0
            for k in range(count):
                take=round((len(words)-pos)/(count-k))
                if take:
                    groups.append(" ".join(words[pos:pos+take]));pos+=take
        assert groups,ch
        total=sum(len(g.split()) for g in groups)
        start=float(ch["start"])+.5; end=float(ch["end"])-1.0
        pos=start
        for k,g in enumerate(groups):
            nxt=end if k==len(groups)-1 else pos+(end-start)*len(g.split())/total
            entries.append((pos/speed,nxt/speed,wrap(g.split())))
            pos=nxt
    srt="\n\n".join(f"{i}\n{fmt(a)} --> {fmt(b)}\n{txt}" for i,(a,b,txt) in enumerate(entries,1))+"\n"
    sub=out/"EP03_AncientSeaSalt_English_Subtitles.srt"
    sub.write_text(srt,encoding="utf-8")
    dst=out/"EP03_AncientSeaSalt_TimeTravelEngineering_175s_FINAL.mp4"
    fc=(f"[0:v]setpts=PTS/{speed:.9f},fps=24,"
        "drawbox=x=40:y=1086:w=640:h=100:color=0x085975@1:t=fill,"
        f"subtitles='{sub}':force_style='FontName=DejaVu Sans,FontSize=7,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00333020,Outline=1,"
        "Shadow=0,Alignment=2,MarginV=24'[v];"
        f"[0:a]atempo={speed:.9f},loudnorm=I=-17:TP=-2:LRA=9[a]")
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(src),
         "-filter_complex",fc,"-map","[v]","-map","[a]","-c:v","libx264",
         "-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r","24",
         "-c:a","aac","-b:a","160k","-ar","48000","-t",str(TARGET),
         "-movflags","+faststart",str(dst)])
    dat=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(dst)]))
    secs=float(dat["format"]["duration"])
    assert 174.0<=secs<=175.6,secs
    assert any(s.get("codec_name")=="h264" and s.get("width")==720 and s.get("height")==1280 for s in dat["streams"])
    assert any(s.get("codec_name")=="aac" for s in dat["streams"])
    run(["ffmpeg","-v","error","-i",str(dst),"-f","null","-"])
    (out/"EP03_Final_Technical_QA.json").write_text(json.dumps(dict(episode="EP03",duration_seconds=secs,subtitle_events=len(entries),bytes=dst.stat().st_size,commercial_rights="Pexels license source evidence reviewed separately; no rights automatically granted",published=False),indent=2))
    print("SUCCESS: EP03 final staged for quality review",dst,secs,len(entries),flush=True)
if __name__=="__main__":main()
