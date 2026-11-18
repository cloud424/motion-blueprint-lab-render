#!/usr/bin/env python3
"""EP05 R3: retrieve only inspected Pexels source pages; no paid generation or publishing."""
import json, pathlib, urllib.request, urllib.error, subprocess, concurrent.futures, shutil, time
out=pathlib.Path("out_EP05_R3_NEW_CLIPS");out.mkdir(parents=True,exist_ok=True)
# (slug, Pexels ID, full source page, contributor, fps hints, dimension)
sources=[
("upper_reservoir","5701349","https://www.pexels.com/video/aerial-view-of-slapy-reservoir-5701349/","Jozef Papp",[30,29,25],"landscape"),
("tennessee_dam","2835981","https://www.pexels.com/video/a-hydroelectric-dam-built-in-tennessee-river-2835981/","K",[30,25,24],"landscape"),
("dam_drone","2835988","https://www.pexels.com/video/drone-footage-of-a-hydroelectric-dam-2835988/","K",[30,25,24],"landscape"),
("powerplant_dam","6132733","https://www.pexels.com/video/drone-footage-of-power-plant-dam-6132733/","CityXcape",[30,25,24],"landscape"),
("spillway_rush","9193308","https://www.pexels.com/video/time-lapse-footage-of-strong-current-of-water-on-a-dam-9193308/","Max O",[30,31,25],"landscape"),
("dam_waterfall","4694126","https://www.pexels.com/video/water-flowing-from-a-dam-4694126/","Ambient Nature Atmosphere",[30,25,24],"landscape"),
("mountain_dam","4833567","https://www.pexels.com/video/a-dam-built-on-a-mountain-river-4833567/","WeStarMoney Rec",[30,25,24],"landscape"),
("powerful_water","31372221","https://www.pexels.com/video/aerial-view-of-powerful-dam-water-flow-31372221/","Tom Fisk",[30,29,60],"landscape"),
("reservoir_view","30320760","https://www.pexels.com/video/aerial-view-of-a-majestic-dam-and-reservoir-30320760/","David Pickup",[30,29,24],"landscape"),
("river_dam","37216416","https://www.pexels.com/video/aerial-view-of-hydroelectric-dam-and-river-37216416/","William Bellhouse",[60,30,24],"landscape"),
("forest_dam","36034925","https://www.pexels.com/video/aerial-view-of-hydroelectric-dam-in-lush-forest-36034925/","Aman Sandhu",[30,24,25],"landscape"),
("dam_gate","30320744","https://www.pexels.com/video/aerial-view-of-large-dam-water-overflow-30320744/","David Pickup",[30,24,25],"landscape"),
("flowing_over","36034929","https://www.pexels.com/video/aerial-view-of-water-flowing-over-dam-spillway-36034929/","Aman Sandhu",[30,24,25],"landscape"),
("spillway_top","31358303","https://www.pexels.com/video/aerial-view-of-hydroelectric-dam-spillway-31358303/","Tom Fisk",[30,29,60],"landscape"),
("green_hydro","30734269","https://www.pexels.com/video/stunning-aerial-view-of-hydroelectric-dam-30734269/","Duy Nguyen",[30,24,25],"landscape"),
("water_cascade","28963707","https://www.pexels.com/video/aerial-view-of-water-flowing-over-dam-spillway-28963707/","K",[30,24,25],"landscape"),
("dam_flow_aerial","27771115","https://www.pexels.com/video/a-large-dam-with-water-flowing-out-of-it-27771115/","ARGA",[30,24,25],"landscape"),
("scenic_dam","30912498","https://www.pexels.com/video/scenic-hydro-dam-with-flowing-waterfalls-30912498/","Sergio Scandroglio",[24,30,25],"landscape"),
("curved_reservoir","36034927","https://www.pexels.com/video/breathtaking-aerial-view-of-scenic-lake-dam-36034927/","Aman Sandhu",[30,25,24],"landscape"),
("spillway_spiral","28934195","https://www.pexels.com/video/aerial-view-of-reservoir-spillway-spiral-28934195/","David Pickup",[30,25,24],"landscape"),
("electric_lines","7796797","https://www.pexels.com/video/time-lapse-of-transmission-tower-and-clouds-7796797/","Edouard Matte",[30,25,24],"landscape"),
("grid_clouds","15357264","https://www.pexels.com/video/moving-clouds-over-a-transmission-tower-15357264/","C A",[24,25,30],"landscape"),
("substation_1","10008388","https://www.pexels.com/video/transformers-at-the-electrical-substation-10008388/","Andrey Kirievskiy",[25,24,30],"landscape"),
("grid_aerial","30915831","https://www.pexels.com/video/aerial-view-of-power-substation-infrastructure-30915831/","Toan BDS",[30,24,25],"landscape"),
("electric_panel","28886877","https://www.pexels.com/video/technician-operating-electrical-control-panel-28886877/","ranjeet",[30,24,25],"landscape")
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
(out/"EP05_R3_New_Footage_Manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
print("COMPLETE",len(records),"OF",len(sources),flush=True)
if len({r["pexels_id"] for r in records})<9:raise SystemExit("Insufficient 9 different licensed hydropower clips; no render and no publication")
