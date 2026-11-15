#!/usr/bin/env python3
"""EP04 R3: retrieve only inspected Pexels source pages; no paid generation or publishing."""
import json, pathlib, urllib.request, urllib.error, subprocess, concurrent.futures, shutil, time
out=pathlib.Path("out_EP04_R3_NEW_CLIPS");out.mkdir(parents=True,exist_ok=True)
# (slug, Pexels ID, full source page, contributor, fps hints, dimension)
sources=[
("dawn_farm","35440356","https://www.pexels.com/video/aerial-view-of-wind-turbines-at-sunrise-35440356/","Tom Schönmann",[30],"landscape"),
("vertical_green","34078191","https://www.pexels.com/video/aerial-view-of-wind-turbines-in-open-field-34078191/","Matthias Groeneveld",[30,29],"portrait"),
("offshore_sea","32572367","https://www.pexels.com/video/majestic-wind-turbines-over-calm-sea-32572367/","Matthias Groeneveld",[30,29],"portrait"),
("aerial_coast","9161618","https://www.pexels.com/video/aerial-footage-of-wind-turbines-9161618/","Vitaliy Todo",[60,30],"landscape"),
("blade_close","4230063","https://www.pexels.com/video/wind-turbine-rotating-4230063/","Kaboompics",[50,25,30],"landscape"),
("propeller_close","4404143","https://www.pexels.com/video/a-close-up-shot-of-a-wind-turbine-propeller-4404143/","K",[24],"landscape"),
("blade_sky","31048771","https://www.pexels.com/video/aerial-view-of-wind-turbines-against-clear-sky-31048771/","Ali Akdemir",[30],"portrait"),
("farm_land","28443570","https://www.pexels.com/video/a-wind-turbine-in-a-field-with-green-grass-28443570/","Sascha Weber",[60],"landscape"),
("wind_single","11208878","https://www.pexels.com/video/aerial-view-of-wind-turbine-11208878/","Tom Fisk",[30,29],"landscape"),
("coastal_beach","18474762","https://www.pexels.com/video/an-aerial-view-of-the-beach-and-wind-turbines-18474762/","JIUN-JE LIN",[30],"landscape"),
("turbine_ice","11740591","https://www.pexels.com/video/close-up-of-wind-turbine-11740591/","Alex Kad",[60],"landscape"),
("sunset_field","29095957","https://www.pexels.com/video/drone-filming-wind-turbines-at-sunset-in-autumn-29095957/","Sascha Weber",[60,30],"landscape"),
("lowangle_sky","5274187","https://www.pexels.com/video/low-angle-shot-of-a-wind-turbine-5274187/","Neil Hedley",[25,24,30],"landscape"),
("sun_behind","9067336","https://www.pexels.com/video/low-angle-shot-of-a-wind-turbine-9067336/","I Am Sorin",[30],"landscape"),
("blade_cloud","9403173","https://www.pexels.com/video/close-up-of-a-wind-turbine-9403173/","Steve B",[24,25,30],"landscape"),
("wind_meadow","4404125","https://www.pexels.com/video/windmills-in-the-farmland-4404125/","K",[30,24],"landscape"),
("winds_urban","7047314","https://www.pexels.com/video/done-footage-of-wind-turbines-7047314/","ROMAN ODINTSOV",[30,29],"landscape"),
("wind_nearshore","855766","https://www.pexels.com/video/low-angle-shot-of-wind-turbine-855766/","Pixabay",[25],"landscape"),
("wind_farfield","855792","https://www.pexels.com/video/video-of-wind-turbine-855792/","Pixabay",[25,24,30],"landscape"),
("substation","10008388","https://www.pexels.com/video/transformers-at-the-electrical-substation-10008388/","Andrey Kirievskiy",[25,24,30],"landscape"),
("substation_b","10008320","https://www.pexels.com/video/transformers-at-an-electrical-station-10008320/","Andrey Kirievskiy",[25,24,30],"landscape"),
("industrial_panel","28886877","https://www.pexels.com/video/technician-operating-electrical-control-panel-28886877/","ranjeet .",[30,24,25],"landscape"),
("worker_panel","30295544","https://www.pexels.com/video/worker-operating-industrial-control-panel-efficiently-30295544/","aksinfo7 universe",[30,24,25],"landscape"),
("power_aerial","30915831","https://www.pexels.com/video/aerial-view-of-power-substation-infrastructure-30915831/","Toan BDS",[30,24,25],"landscape"),
("industrial_gears","35069286","https://www.pexels.com/video/industrial-gear-machining-in-action-35069286/","Diego Castro Calderon",[30],"landscape")
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
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
 records=[r for r in ex.map(fetch,sources) if r is not None]
(out/"EP04_R3_New_Footage_Manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
print("COMPLETE",len(records),"OF",len(sources),flush=True)
if len(records)<9:raise SystemExit("Insufficient 9 unique genuine licensed wind documentary clips; NO RELEASE")
