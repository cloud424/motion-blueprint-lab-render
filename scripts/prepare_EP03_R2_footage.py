#!/usr/bin/env python3
"""Download hand-verified Pexels salt-making clips to a short-lived private GH artifact.
Only the explicitly attributed clips; no image/video scraping.
"""
from pathlib import Path
import urllib.request,subprocess,json,shutil,sys,time
OUT=Path("out_EP03_R2_FOOTAGE");OUT.mkdir(parents=True,exist_ok=True)
sources=[
 ("workers","15574383",24,19,"https://www.pexels.com/video/two-workers-harvesting-salt-by-the-sea-15574383/","khanhhoangminh"),
 ("shoveling","15574396",24,15,"https://www.pexels.com/video/a-worker-shoveling-salt-into-a-wheelbarrow-15574396/","khanhhoangminh"),
 ("sunset","15574456",24,36,"https://www.pexels.com/video/silhouette-of-a-man-harvesting-salt-at-sunset-15574456/","khanhhoangminh"),
 ("sunset2","15574457",24,18,"https://www.pexels.com/video/silhouette-of-a-worker-harvesting-salt-at-sunset-15574457/","khanhhoangminh"),
 ("colorponds","8414932",25,28,"https://www.pexels.com/video/aerial-footage-of-salt-ponds-8414932/","Mikhail Nilov"),
 ("coxs_pans","33251053",60,10,"https://www.pexels.com/video/aerial-view-of-salt-pans-in-cox-s-bazar-region-33251053/","Emrul Kausar Emon"),
 ("thai_fields","16878722",24,16,"https://www.pexels.com/video/a-large-glass-window-with-a-view-of-the-desert-16878722/","HUAHIN PILOT LAND & REAL ESTATE DRONER"),
 ("coxs_pans2","33251055",60,10,"https://www.pexels.com/video/aerial-view-of-salt-pans-in-cox-s-bazar-33251055/","Emrul Kausar Emon")
]
records=[]
for slug,vid,fps,expected,page,author in sources:
  dst=OUT/(slug+".mp4")
  urls=[]
  for kind,wh in (("sd","960_540"),("hd","1920_1080"),("sd","640_360")):
    for rate in [fps,24,25,30,60]:
      u=f"https://videos.pexels.com/video-files/{vid}/{vid}-{kind}_{wh}_{rate}fps.mp4"
      if u not in urls:urls.append(u)
  ok=False
  for u in urls:
    try:
      req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0","Accept":"video/mp4"})
      with urllib.request.urlopen(req,timeout=12) as resp,open(dst,"wb") as out:
        shutil.copyfileobj(resp,out)
      if dst.stat().st_size<100000:raise RuntimeError("Short download")
      dat=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-of","json",str(dst)]))
      secs=float(dat["format"]["duration"])
      if secs<4:raise RuntimeError("Video shorter than 4 sec")
      print("SUCCESS",slug,secs,dst.stat().st_size,flush=True)
      records.append(dict(slug=slug,id=vid,page=page,author=author,source_url=u,duration=secs,bytes=dst.stat().st_size,license_url="https://www.pexels.com/license/"))
      ok=True
      break
    except Exception as ex:
      if dst.exists():dst.unlink()
      if not isinstance(ex,urllib.error.HTTPError) or ex.code!=404:
        print("WARNING",slug,str(ex)[:150],flush=True)
  if not ok:print("UNAVAILABLE",slug,flush=True)
(OUT/"EP03_R2_Original_Footage_Manifest.json").write_text(json.dumps(records,indent=2))
if not {"workers","shoveling","sunset"}.issubset({x["slug"] for x in records}):
  raise RuntimeError("Need three genuine salt-harvest video clips to build real-footage R2; do not fake")
print("READY",len(records),flush=True)
