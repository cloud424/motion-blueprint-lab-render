#!/usr/bin/env python3
"""EP04 R3 supplemental: retrieve only inspected Pexels source pages; no paid generation or publishing."""
import json, pathlib, urllib.request, urllib.error, subprocess, concurrent.futures, shutil, time
out=pathlib.Path("out_EP04_R3_SUPP");out.mkdir(parents=True,exist_ok=True)
# (slug, Pexels ID, full source page, contributor, fps hints, dimension)
sources=[
("lathe_close","9737962","https://www.pexels.com/video/close-up-of-spinning-machinery-9737962/","Kelly",[24],"landscape"),
("real_gears","6641561","https://www.pexels.com/video/video-of-working-machinery-6641561/","Dr.Vivasayam YouTube Channel",[30,25,24],"landscape"),
("old_grid","10008388","https://www.pexels.com/video/transformers-at-the-electrical-substation-10008388/","Andrey Kirievskiy",[30,25,24,50,60],"landscape"),
("worker_panel","30295544","https://www.pexels.com/video/worker-operating-industrial-control-panel-efficiently-30295544/","aksinfo7 universe",[24,25,30,60],"landscape"),
("rotor_motor","9737962","https://www.pexels.com/video/close-up-of-spinning-machinery-9737962/","Kelly",[25,30],"landscape"),
("power_grid","10008320","https://www.pexels.com/video/transformers-at-an-electrical-station-10008320/","Andrey Kirievskiy",[24,25,30,50,60],"landscape")
]
def fetch(s):
 slug,vid,page,author,ratehints,orient=s
 target=out/(slug+".mp4")
 dimensions=["960_540","640_360","1280_720","540_960","360_640","720_1280","960_432"] if orient=="landscape" else ["540_960","360_640","720_1280","960_540"]
 queries=[]
 for dim in dimensions:
  for rt in ratehints:
   for kind in ["sd","hd"]:
    u=f"https://videos.pexels.com/video-files/{vid}/{vid}-{kind}_{dim}_{rt}fps.mp4"
    queries.append(u)
 for u in queries[:30]:
  try:
   req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0","Accept":"video/mp4"})
   with urllib.request.urlopen(req,timeout=9) as resp,open(target,"wb") as fw:
    shutil.copyfileobj(resp,fw)
   if target.stat().st_size<90000:raise ValueError("tiny")
   inf=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(target)]))
   dur=float(inf["format"]["duration"]);ss=[x for x in inf["streams"] if x.get("codec_type")=="video"]
   if not ss or dur<4:raise ValueError("invalid video")
   print("SUCCESS",slug,round(dur,2),round(target.stat().st_size/1024**2,2),flush=True)
   return dict(slug=slug,pexels_id=vid,page=page,contributor=author,url=u,duration=dur,bytes=target.stat().st_size,license="https://www.pexels.com/license/",width=ss[0].get("width"),height=ss[0].get("height"),sound="original source audio will be removed")
  except urllib.error.HTTPError as e:
   if target.exists():target.unlink()
   if e.code not in (403,404,429,500,502):print("HTTP",slug,e.code,flush=True)
   if e.code==429:break
  except Exception as e:
   if target.exists():target.unlink()
   print("ERR",slug,str(e)[:80],flush=True)
 print("UNAVAILABLE",slug,flush=True)
 return None
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 records=[r for r in ex.map(fetch,sources) if r is not None]
(out/"EP04_R3_Supplement_Manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
print("COMPLETE",len(records),"OF",len(sources),flush=True)
if not records:raise SystemExit("No supplemental varied footage found; use 12 already licensed main sources")
