#!/usr/bin/env python3
"""EP06 R3: retrieve only inspected Pexels source pages; no paid generation or publishing."""
import json, pathlib, urllib.request, urllib.error, subprocess, concurrent.futures, shutil, time, re
import imageio_ffmpeg
out=pathlib.Path("out_EP06_R3_NEW_CLIPS");out.mkdir(parents=True,exist_ok=True)
# (slug, Pexels ID, full source page, contributor, fps hints, dimension)
sources=[
("ship_open_ocean","32599129","https://www.pexels.com/video/aerial-view-of-cargo-ship-navigating-calm-waters-32599129/","Eslam Mohammed Abdelmaksoud",[60,30,29],"portrait"),
("ship_colorful","36233044","https://www.pexels.com/video/large-cargo-ship-with-colorful-containers-at-sea-36233044/","Phạm Công Thành",[25,24,30],"landscape"),
("ship_docked","35872107","https://www.pexels.com/video/aerial-view-of-cargo-ship-docked-at-industrial-port-35872107/","willy one",[24,25,30],"landscape"),
("ship_port","30262129","https://www.pexels.com/video/aerial-view-of-container-ship-at-busy-port-30262129/","Toàn BDS",[60,30,59],"landscape"),
("ship_tug","30262141","https://www.pexels.com/video/aerial-view-of-busy-container-terminal-30262141/","Toàn BDS",[60,30,59],"landscape"),
("ship_harbor","34974517","https://www.pexels.com/video/aerial-view-of-cargo-ship-in-busy-harbor-34974517/","Stephan Leuzinger",[24,25,30],"landscape"),
("ship_coast","30583751","https://www.pexels.com/video/aerial-view-of-cargo-ship-navigating-coastline-30583751/","Julien Goettelmann",[30,29,25],"portrait"),
("ship_river","35860972","https://www.pexels.com/video/cargo-ship-on-river-with-containers-35860972/","willy one",[24,25,30],"landscape"),
("ship_freighter","13898678","https://www.pexels.com/video/freighter-on-water-13898678/","Edward Rode",[30,29,25],"landscape"),
("ship_calm","30917928","https://www.pexels.com/video/aerial-view-of-cargo-ship-at-sea-30917928/","Toàn BDS",[60,30,59],"landscape"),
("ship_loading","3058057","https://www.pexels.com/video/heavy-machinery-used-in-seaports-unloading-containers-from-a-cargo-ship-3058057/","Tom Fisk",[30,29,25],"landscape"),
("ship_stacks","10458151","https://www.pexels.com/video/filled-with-containers-ship-in-commercial-dock-10458151/","Glenn Langhorst",[30,25,24],"landscape"),
("ship_yard","6595362","https://www.pexels.com/video/aerial-view-of-container-freight-station-6595362/","K",[24,25,30],"landscape"),
("ship_crane","37656182","https://www.pexels.com/video/efficient-container-yard-crane-operation-37656182/","TwoSix ZeroFive",[30,25,24],"portrait"),
("ship_bustle","30899477","https://www.pexels.com/video/aerial-view-of-bustling-container-port-operations-30899477/","Toàn BDS",[60,30,59],"landscape"),
("ship_riverport","30840767","https://www.pexels.com/video/aerial-view-of-cargo-ships-on-a-river-port-30840767/","Toàn BDS",[60,30,59],"landscape"),
("ship_bermuda","36599214","https://www.pexels.com/video/aerial-view-of-busy-port-at-sunset-in-bermuda-36599214/","Brandon Morrison",[60,30,59],"landscape"),
("ship_dock","37099185","https://www.pexels.com/video/massive-cargo-ship-docked-at-european-port-37099185/","Wolfgang Weiser",[25,24,30],"landscape"),
("ship_parade","13843737","https://www.pexels.com/video/boat-on-sea-in-slow-motion-13843737/","wowi allinsky",[60,30,25],"landscape"),
("ship_commercial","10452360","https://www.pexels.com/video/container-ship-in-harbor-10452360/","Glenn Langhorst",[30,24,25],"landscape"),
("ship_aerial_dock","30899932","https://www.pexels.com/video/aerial-view-of-industrial-docks-and-ships-30899932/","Toàn BDS",[60,30,25],"landscape"),
("ship_mooring","28459798","https://www.pexels.com/video/a-view-of-a-harbor-with-a-large-container-ship-28459798/","Sururi Ballıdağ",[30,24,25],"portrait"),
("ship_loaders","31750579","https://www.pexels.com/video/container-loader-operating-at-a-busy-shipping-port-31750579/","Dominik Zítka",[25,24,30],"landscape"),
("ship_sunset","5091870","https://www.pexels.com/video/aerial-view-of-a-shipping-port-5091870/","Wildo Ríos Méndez",[30,29,25],"landscape"),
("ship_cruise","30522944","https://www.pexels.com/video/aerial-view-of-container-ship-docked-at-port-30522944/","Toàn BDS",[60,30,59],"landscape"),
("ship_drone_aerial","6857819","https://www.pexels.com/video/aerial-footage-of-cargo-ship-6857819/","Alexander Bobrov",[24,23,25,30],"landscape"),
("ship_evergreen","6595370","https://www.pexels.com/video/aerial-footage-of-cargo-contains-on-a-ship-6595370/","K",[24,25,30],"landscape"),
("ship_night","35907900","https://www.pexels.com/video/aerial-view-of-busy-cargo-ship-at-night-35907900/","willy one",[25,24,30],"landscape"),
("ship_navigating_harbor","35800894","https://www.pexels.com/video/aerial-view-of-container-ship-in-busy-harbor-35800894/","willy one",[25,24,30],"landscape"),
("ship_coastline","34043264","https://www.pexels.com/video/aerial-view-of-cargo-ship-passing-coastal-city-34043264/","Victor Cedini",[30,29,25],"landscape"),
("ship_calm_vertical","37512687","https://www.pexels.com/video/large-cargo-ship-sailing-through-calm-waters-37512687/","Alina Zhabynska",[60,59,30],"portrait"),
("ship_dockside","29625863","https://www.pexels.com/video/dockside-view-of-passing-cargo-ship-29625863/","Eyüp Can Çağlar",[60,30,59],"portrait"),
("ship_mountain_ocean","9102726","https://www.pexels.com/video/drone-footage-of-a-ship-passing-by-9102726/","Shoot With Riyas",[50,25,30],"landscape"),
("ship_clear_ocean","16992876","https://www.pexels.com/video/a-large-cargo-ship-is-traveling-through-the-ocean-16992876/","Seven Seil",[30,29,25],"landscape"),
("ship_columbia","6979838","https://www.pexels.com/video/ship-is-stopped-at-sea-6979838/","Stephen Pierce",[30,29,25],"landscape"),
("ship_shore","2910038","https://www.pexels.com/video/a-container-ship-with-cargoes-on-the-harbor-2910038/","K",[24,25,30],"landscape"),
("ship_dock_aerial_new","30522944","https://www.pexels.com/video/aerial-view-of-container-ship-docked-at-port-30522944/","Toàn BDS",[60,59,30],"landscape"),
("ship_mono","40622209","https://www.pexels.com/video/aerial-view-of-cargo-ship-in-ocean-40622209/","Efrem Efre",[60,59,30],"landscape"),
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
   exe=imageio_ffmpeg.get_ffmpeg_exe()
   checked=subprocess.run([exe,"-hide_banner","-i",str(target),"-frames:v","1","-an","-f","null","-"],capture_output=True,text=True,timeout=45)
   head=checked.stderr
   dm=re.search(r"Duration:\\s*(\\d+):(\\d+):([\\d.]+)",head)
   vm=re.search(r"Video:[^\\n]*?(\\d{3,5})x(\\d{3,5})",head)
   if checked.returncode!=0 or not dm or not vm:raise ValueError("unverified real video")
   dur=int(dm.group(1))*3600+int(dm.group(2))*60+float(dm.group(3))
   ss=[{"width":int(vm.group(1)),"height":int(vm.group(2))}]
   if dur<14.45:raise ValueError("video shorter than one 14.45s scene")
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
(out/"EP06_R3_New_Footage_Manifest.json").write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
print("COMPLETE",len(records),"OF",len(sources),flush=True)
if len({r["pexels_id"] for r in records})<9:raise SystemExit("Insufficient 9 different licensed cargo-ship clips; no render and no publication")
