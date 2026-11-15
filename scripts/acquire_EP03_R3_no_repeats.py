#!/usr/bin/env python3
"""EP03 R3: retrieve only inspected Pexels source pages; no paid generation or publishing."""
import json, pathlib, urllib.request, urllib.error, subprocess, concurrent.futures, shutil, time
out=pathlib.Path("out_EP03_R3_NEW_CLIPS");out.mkdir(parents=True,exist_ok=True)
# (slug, Pexels ID, full source page, contributor, fps hints, dimension)
sources=[
("sunlit_workers","16807494","https://www.pexels.com/video/salt-is-being-made-in-a-large-salt-field-16807494/","Pexels source contributor",[30,29],"landscape"),
("traditional_harvest","36035491","https://www.pexels.com/video/salt-harvesting-in-traditional-salt-pans-36035491/","Circuit Occidental",[30,24],"landscape"),
("worker_gathering","36035490","https://www.pexels.com/video/worker-gathering-salt-at-a-salt-farm-36035490/","Circuit Occidental",[30,24,25],"landscape"),
("coastal_pan_a","33251053","https://www.pexels.com/video/aerial-view-of-salt-pans-in-cox-s-bazar-region-33251053/","Emrul Kausar Emon",[60,30],"landscape"),
("coastal_pan_b","33251055","https://www.pexels.com/video/aerial-view-of-salt-pans-in-cox-s-bazar-33251055/","Emrul Kausar Emon",[60,30],"landscape"),
("coastal_blue","37845479","https://www.pexels.com/video/scenic-coastal-salt-pans-by-the-ocean-37845479/","Alyona Nagel",[30,24],"landscape"),
("ponds_colors_b","8414931","https://www.pexels.com/video/drone-footage-of-salt-ponds-8414931/","Mikhail Nilov",[25,24],"landscape"),
("farm_flyover","4385172","https://www.pexels.com/video/a-fly-by-shot-over-a-salt-farm-4385172/","Joao Pinheiro",[30,25],"landscape"),
("rock_salt_pouring","7152168","https://www.pexels.com/video/a-footage-of-a-rock-salt-pouring-on-a-table-7152168/","Rudolfs Klintsons",[24,25],"landscape"),
("salt_closeup","9266800","https://www.pexels.com/video/close-up-of-rock-salt-9266800/","N S",[25,24,30],"portrait"),
("boiling_evaporation","8094291","https://www.pexels.com/video/water-evaporating-from-the-pan-8094291/","Mikhail Nilov",[25,24,30],"landscape"),
("salt_boiling","10431976","https://www.pexels.com/video/a-person-adding-a-salt-in-the-cooking-pot-10431976/","RDNE Stock project",[25,24,30],"portrait"),
("real_ocean","32040399","https://www.pexels.com/video/aerial-view-of-ocean-waves-hitting-sandy-beach-32040399/","Volkan Yilmaz",[50,30],"portrait"),
("salt_crust_vertical","36119246","https://www.pexels.com/video/aerial-view-of-salt-crystals-on-desert-plain-36119246/","Efrem Efre",[60,30],"portrait"),
("pan_sunrise","36295881","https://www.pexels.com/video/aerial-view-of-coastal-salt-pans-at-sunrise-36295881/","Emrul Kausar Emon",[30,24],"portrait"),
("salt_process_aerial","40135073","https://www.pexels.com/it-it/video/veduta-aerea-delle-saline-in-fase-di-produzione-40135073/","Rahim Saikat",[30,25],"landscape"),
("traditional_workers","36035479","https://www.pexels.com/video/traditional-salt-harvesting-in-vast-salt-pans-36035479/","Circuit Occidental",[30,24],"landscape"),
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
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 records=[r for r in ex.map(fetch,sources) if r is not None]
(out/"EP03_R3_New_Footage_Manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
print("COMPLETE",len(records),"OF",len(sources),flush=True)
if len(records)<5:raise SystemExit("Insufficient new genuine footage; no release")
