#!/usr/bin/env python3
"""EP05 R3: retrieve only inspected Pexels source pages; no paid generation or publishing."""
import json, pathlib, urllib.request, urllib.error, subprocess, concurrent.futures, shutil, time
out=pathlib.Path("out_EP05_R3_SUPP");out.mkdir(parents=True,exist_ok=True)
# (slug, Pexels ID, full source page, contributor, fps hints, dimension)
sources=[
("lake_dam_reflections","30278658","https://www.pexels.com/video/scenic-aerial-view-of-tranquil-reservoir-30278658/","David Pickup",[30,29,25],"landscape"),
("dam_new_gravity","30278267","https://www.pexels.com/video/aerial-view-of-majestic-dam-and-reservoir-30278267/","David Pickup",[30,29,25],"landscape"),
("dam_turquoise","28963688","https://www.pexels.com/video/aerial-view-of-scenic-dam-and-reservoir-28963688/","K",[24,25,30,60],"landscape"),
("dam_veryhigh","31669420","https://www.pexels.com/video/aerial-view-of-dam-and-reservoir-top-view-31669420/","Ferdie Cayanga",[30,24,25],"landscape"),
("dam_above_stream","15214300","https://www.pexels.com/video/view-of-a-dam-from-above-15214300/","Jiri Maly",[30,24,25,60],"landscape"),
("dam_river_2","20350208","https://www.pexels.com/video/an-aerial-view-of-a-dam-and-river-20350208/","DeLuca G",[60,30,24],"landscape"),
("dam_low_reservoir","37533792","https://www.pexels.com/video/aerial-view-of-dramatic-dam-and-dry-reservoir-37533792/","Philipp Kappler",[30,24,25],"landscape"),
("dam_small_stream","13448387","https://www.pexels.com/video/flowing-water-from-dam-on-river-13448387/","Mat CutFilms",[30,24,25],"landscape"),
("dam_watergate","28142315","https://www.pexels.com/video/an-aerial-view-of-a-dam-with-water-flowing-through-it-28142315/","David Pickup",[30,24,25],"landscape"),
("dam_drone_new","5053182","https://www.pexels.com/video/drone-footage-of-a-water-dam-5053182/","Pavel Danilyuk",[30,25,24],"landscape"),
("dam_flowtop","6602519","https://www.pexels.com/video/top-view-of-a-dam-with-flowing-water-6602519/","Hide",[30,24,25],"landscape"),
("water_discharge_pipe","10884417","https://www.pexels.com/video/water-flowing-through-a-discharge-pipe-10884417/","Diego da Silva",[30,25,24],"landscape"),
("dam_steady","40665179","https://www.pexels.com/video/aerial-view-of-river-dam-flowing-steadily-40665179/","MAYANKSTER",[30,24,25],"landscape"),
("water_dam_pour","2835984","https://www.pexels.com/video/dam-on-river-2835984/","K",[30,25,24],"landscape"),
("hydro_dam_from_above","20350207","https://www.pexels.com/video/an-aerial-view-of-a-dam-and-water-20350207/","DeLuca G",[60,30,24],"landscape")
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
   if not ss or dur<14.4:raise ValueError("video shorter than one 14.45s scene")
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
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 records=[r for r in ex.map(fetch,sources) if r is not None]
(out/"EP05_R3_Supplement_Manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
print("COMPLETE",len(records),"OF",len(sources),flush=True)
if len({r["pexels_id"] for r in records})<2:raise SystemExit("Insufficient new distinct hydro clips. No render and no publication.")
