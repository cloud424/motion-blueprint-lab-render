#!/usr/bin/env python3
"""EP05 footage ingress: fail-closed real video checks, no publication/paid AI calls.
Candidates are discoverable pages, not proof of source provenance. Inspect clips
before human/agent QA sets the Make episode flag to ready_for_autopublish.
"""
import concurrent.futures, hashlib, json, pathlib, re, shutil, subprocess, urllib.error, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"episodes/EP05_HydraulicExcavator_Plan.json"
OUT=ROOT/"out_EP05_ingest"
OUT.mkdir(parents=True,exist_ok=True)
m=json.loads(MANIFEST.read_text(encoding="utf-8"))
assert m["episode"]=="EP05"
results=[]
def probe(path):
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)]))
    stream=next((s for s in info["streams"] if s.get("codec_type")=="video"),None)
    if stream is None:raise ValueError("no video stream")
    return (float(info["format"]["duration"]),int(stream.get("width") or 0),int(stream.get("height") or 0))
def get(clip):
    ident=clip["id"]; name="EP05_Real_"+ident+".mp4"
    target=OUT/name
    candidate=[]
    for res in ["960_540","540_960","1280_720","720_1280","640_360","360_640"]:
        for fps in [30,24,25,60]:
            for fmt in ["sd","hd"]:
                candidate.append(f"https://videos.pexels.com/video-files/{ident}/{ident}-{fmt}_{res}_{fps}fps.mp4")
    seen=set()
    for url in candidate:
        if url in seen:continue
        seen.add(url)
        try:
            request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"video/mp4"})
            with urllib.request.urlopen(request,timeout=7) as resp:
                if int(resp.headers.get("Content-Length","0") or 0)>75_000_000:
                    continue
                with target.open("wb") as f:
                    shutil.copyfileobj(resp,f,length=1024*1024)
            if target.stat().st_size<100_000:raise ValueError("video too small")
            duration,w,h=probe(target)
            if duration<14.45:raise ValueError("shorter than required single-use scene")
            sha=hashlib.sha256(target.read_bytes()).hexdigest()
            return {"id":ident,"page":clip["url"],"contributor_page_claim":clip["contributor"],
                    "local_file":name,"source_mp4_url":url,"seconds":duration,
                    "size_bytes":target.stat().st_size,"width":w,"height":h,
                    "sha256":sha,"status":"downloaded_awaiting_rights_and_visual_QA"}
        except (urllib.error.URLError,TimeoutError,ValueError,subprocess.CalledProcessError,OSError):
            if target.exists():target.unlink()
            continue
    return {"id":ident,"page":clip["url"],"status":"unavailable_or_too_short"}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    for r in pool.map(get,m["footageCandidates"]):
        results.append(r)
        print(r["id"],r["status"],flush=True)
verified=[r for r in results if r["status"]=="downloaded_awaiting_rights_and_visual_QA"]
report={"episode":"EP05","candidate_count":len(results),"downloaded_duration_valid":len(verified),
        "required_unique_footage":9,"release_approved":False,
        "candidates":results,"note":"Downloaded bytes only. License ownership, scientific visuals, captions, audio, and final MP4 still need independent QA."}
(OUT/"EP05_DownloadedSourceInventory.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("SUCCEEDED:",len(verified),"of 9 required sources",flush=True)
if len(verified)<9:
    raise SystemExit("BLOCKED: fewer than nine eligible distinct 14.45-second real videos; never grant publication QA.")
