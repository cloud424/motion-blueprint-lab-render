#!/usr/bin/env python3
"""Private footage contact sheet: actual decoded frames, not mocked thumbnails."""
import json
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path("out_EP07_sources")
manifest=json.loads((ROOT/"EP07_Source_Acquisition_Report.json").read_text(encoding="utf-8"))
items=[v["meta"] for v in manifest["outputs"] if v.get("result")=="downloaded_valid_media_not_release_approved"]
if not items:
    raise SystemExit("NO_REAL_SOURCE_FRAMES")
w,h=960,218
canvas=Image.new("RGB",(w,h*len(items)),(13,24,37))
dr=ImageDraw.Draw(canvas)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
font_file="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=ImageFont.truetype(font_file,17)
small=ImageFont.truetype(font_file,13)
with tempfile.TemporaryDirectory() as scratch:
    for row,m in enumerate(items):
        slug=m["slug"];ext=".webm" if m.get("source_type")=="wikimedia_commons" else ".mp4"
        src=ROOT/(slug+ext)
        title=f"{row+1:02}. {slug[:47]} | {float(m['duration']):.1f}s"
        dr.text((10,row*h+5),title,font=font,fill=(245,246,247))
        dr.text((10,row*h+27),f"{m.get('role','unknown')} | {m.get('contributor','?')[:45]}",font=small,fill=(163,216,231))
        for k,frac in enumerate((.16,.48,.82)):
            time=float(m["duration"])*frac
            target=Path(scratch)/f"shot_{row}_{k}.jpg"
            p=subprocess.run([ffmpeg,"-hide_banner","-loglevel","error","-y",
                "-ss",f"{time:.3f}","-i",str(src),"-frames:v","1",
                "-vf","scale=320:164:force_original_aspect_ratio=decrease,"
                "pad=320:164:(ow-iw)/2:(oh-ih)/2:black",str(target)],
                capture_output=True,text=True,timeout=45)
            if p.returncode or not target.exists():
                dr.rectangle((k*320,row*h+52,k*320+319,row*h+216),fill=(85,41,41))
                dr.text((k*320+7,row*h+70),"FRAME DECODE ERROR",font=small,fill=(255,224,224))
                continue
            with Image.open(target) as im:
                canvas.paste(im.convert("RGB"),(k*320,row*h+52))
canvas.save(ROOT/"EP07_Source_RealFrames.jpg",quality=87,optimize=True)
print("EP07_ACTUAL_SOURCE_PREVIEW",len(items),str(ROOT/"EP07_Source_RealFrames.jpg"))
