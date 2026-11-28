#!/usr/bin/env python3
"""EP07 private source acquisition only. Never publishes or sets approved flags."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request

import imageio_ffmpeg

ROOT = Path("out_EP07_sources")
ROOT.mkdir(parents=True, exist_ok=True)
SOURCE_FILE = Path("episodes/EP07_Source_Candidates.json")
REQ_SECONDS = 14.45
MAX_BYTES = 70_000_000
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
DATA = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
CANDIDATES = DATA["source_candidates"]
CACHE_REPORT = ROOT / "EP07_Source_Acquisition_Report.json"
PREVIOUS = {}
if CACHE_REPORT.is_file():
    try:
        old_report = json.loads(CACHE_REPORT.read_text(encoding="utf-8"))
        PREVIOUS = {
            z["meta"]["slug"]: z["meta"]
            for z in old_report.get("outputs", [])
            if z.get("result") == "downloaded_valid_media_not_release_approved"
            and isinstance(z.get("meta"), dict)
        }
        print("RESTORED PRIVATE SOURCE MANIFEST", len(PREVIOUS), flush=True)
    except (OSError, ValueError, KeyError) as exc:
        print("Cached report unreadable; acquire originals normally:", str(exc)[:180], flush=True)



def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe_portable(path):
    p = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(path), "-frames:v", "1",
         "-an", "-f", "null", "-"],
        capture_output=True, text=True, timeout=55
    )
    msg = p.stderr
    d = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", msg)
    v = re.search(r"Video:\s*([a-zA-Z0-9_]+)[^\n]*?(\d{3,5})x(\d{3,5})", msg)
    if p.returncode or not d or not v:
        raise ValueError("Video decode/probe failed: " + msg[-280:])
    return {
        "duration": int(d.group(1))*3600+int(d.group(2))*60+float(d.group(3)),
        "codec": v.group(1),
        "width": int(v.group(2)),
        "height": int(v.group(3))
    }


def candidates(item):
    """Only try plausible paths. No 50-URL brute-force loops for missing files."""
    if item.get("source_type") == "wikimedia_commons":
        yield item["direct_url"]
        return

    vid = item["id"]
    vertical = item.get("orientation") == "portrait"
    if vertical:
        sizes = ["1080_1920", "720_1280", "540_960", "360_640"]
    else:
        sizes = ["1920_1080", "1280_720", "960_540", "640_360"]
    yield f"https://www.pexels.com/download/video/{vid}/"
    # Pexels commonly uses HD 1920x1080 / HD 1080x1920.
    # Never infer a source is valid just because a filename looks plausible.
    for dim in sizes:
        for fps in [30, 25, 60, 24]:
            for kind in ["hd", "sd"]:
                yield f"https://videos.pexels.com/video-files/{vid}/{vid}-{kind}_{dim}_{fps}fps.mp4"


def source_page_download(item, target):
    """Use the provider's public file metadata, never guess a non-existing CDN path.

    Original footage is PRIVATE QA only; creator/page/license are recorded separately.
    """
    if not item.get("page_verified"):
        return None, "Unverified source page"
    cmd = ["yt-dlp", "--no-playlist", "--no-warnings", "--no-overwrites",
           "--socket-timeout", "18", "--retries", "2", "--fragment-retries", "2",
           "-f", "best[height<=720]/source/best", "-o", str(target)]
    if item.get("source_type") != "wikimedia_commons":
        cmd.extend(["--impersonate", "chrome"])
    cmd.append(item["url"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=110)
        if result.returncode:
            return None, "yt-dlp source-page fetch rejected: " + (result.stderr or result.stdout)[-240:]
        if not target.is_file() or target.stat().st_size < 100000:
            return None, "yt-dlp did not write actual video bytes"
        if target.stat().st_size > MAX_BYTES:
            target.unlink(missing_ok=True)
            return None, "source-page media exceeds QA byte bound"
        info = ffprobe_portable(target)
        if info["duration"] < REQ_SECONDS:
            target.unlink(missing_ok=True)
            return None, "source-page clip shorter than 14.45 seconds"
        out = {
            "slug": item["slug"], "pexels_id": item["id"], "page": item["url"],
            "contributor": item["author"],
            "contributor_page_verified": bool(item.get("page_verified")),
            "role": item["stage"], "license": item.get("license", DATA["license"]),
            "source_type": item.get("source_type", "pexels"),
            "asset_url": item["url"], "sha256": sha256(target), "bytes": target.stat().st_size,
            "audio": "original audio excluded from final render",
            "process_visual_qa": "pending_manual_frame_and_motion_review",
            "rights_qa": "pending_actual_video_and_third_party_review",
            **info
        }
        print("DOWNLOADED_FROM_SOURCE_PAGE", item["slug"], info["duration"], info["width"], info["height"], flush=True)
        return {"result":"downloaded_valid_media_not_release_approved", "meta":out}, None
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return None, type(exc).__name__ + ": " + str(exc)[:200]


def try_download(item):
    slug, vid = item["slug"], item["id"]
    target = ROOT / (slug + (".webm" if item.get("source_type") == "wikimedia_commons" else ".mp4"))
    if item.get("skip_reason"):
        return {"result":"excluded_from_candidate_pool", "id":vid, "slug":slug,
                "stage":item["stage"], "reason":item["skip_reason"]}
    if item.get("duration_hint_seconds", 1000) < REQ_SECONDS:
        return {"result":"source_known_too_short_for_one_scene", "id":vid, "slug":slug,
                "stage":item["stage"], "duration_hint_seconds":item["duration_hint_seconds"]}
    cached = PREVIOUS.get(slug)
    if cached and str(cached.get("pexels_id")) == str(vid) and cached.get("page") == item["url"] and target.is_file():
        try:
            if (target.stat().st_size == cached.get("bytes")
                and sha256(target) == cached.get("sha256")):
                meta = ffprobe_portable(target)
                if meta["duration"] >= REQ_SECONDS and abs(meta["duration"] - cached["duration"]) < 0.15:
                    print("REUSED_VERIFIED_BYTES", slug, target.stat().st_size, flush=True)
                    return {"result":"downloaded_valid_media_not_release_approved", "meta":cached}
        except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
            print("Cached source invalid; re-acquiring",slug,str(exc)[:125],flush=True)
        target.unlink(missing_ok=True)
    failures = []
    attempts = 0
    # The source-page extractor resolved a licensed 2017 Commons film that raw URL
    # requests got HTTP 429. Newer Pexels videos may also lack legacy CDN paths.
    if item.get("source_type") == "wikimedia_commons" or int(str(vid).split(":")[0]) >= 30000000:
        found, reason = source_page_download(item, target)
        attempts += 1
        if found:
            return found
        failures.append(reason or "source-page downloader returned no video")
    # No repeated Wikimedia direct-URL retries after its provider CDN returns 429.
    if item.get("source_type") == "wikimedia_commons":
        return {"result":"unavailable_or_short", "id":vid, "slug":slug, "stage":item["stage"],
                "attempts":attempts, "first_errors":failures[:4], "last_errors":failures[-5:]}
    for url in list(candidates(item))[:16]:
        attempts += 1
        if attempts > 2 and attempts % 8 == 0:
            time.sleep(1.5)
        try:
            # Probe using a HEAD request first; only retrieve a bounded real video.
            # Some official download endpoints disallow HEAD but allow GET.
            if "www.pexels.com/download/video/" not in url and item.get("source_type") != "wikimedia_commons":
                head = urllib.request.Request(url, method="HEAD", headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(head, timeout=9) as resp:
                    size = int(resp.headers.get("Content-Length") or 0)
                    if size > MAX_BYTES:
                        failures.append("source over byte limit")
                        continue
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0", "Accept":"video/mp4"})
            with urllib.request.urlopen(req, timeout=16) as resp, target.open("wb") as out:
                total = 0
                while True:
                    block = resp.read(256*1024)
                    if not block:
                        break
                    total += len(block)
                    if total > MAX_BYTES:
                        raise ValueError("download exceeded 70MB limit")
                    out.write(block)
            if target.stat().st_size < 100_000:
                raise ValueError("missing real video content")
            meta = ffprobe_portable(target)
            if meta["duration"] < REQ_SECONDS:
                failures.append(f"real clip too short ({meta['duration']:.1f}s)")
                target.unlink(missing_ok=True)
                continue
            result = {
                "slug": slug, "pexels_id": vid, "page": item["url"],
                "contributor": item["author"],
                "contributor_page_verified": bool(item["page_verified"]),
                "role": item["stage"], "license": item.get("license", DATA["license"]),
                "source_type": item.get("source_type", "pexels"),
                "asset_url": url, "sha256": sha256(target), "bytes": target.stat().st_size,
                "audio": "original audio excluded from any future EP07 edit",
                "process_visual_qa": "pending_manual_frame_and_motion_review",
                "rights_qa": "pending_actual_video_and_third_party_review",
                **meta
            }
            print("DOWNLOADED", slug, meta["duration"], meta["width"], meta["height"], flush=True)
            return {"result":"downloaded_valid_media_not_release_approved","meta":result}
        except (urllib.error.URLError, TimeoutError, ValueError, subprocess.TimeoutExpired) as exc:
            failures.append(type(exc).__name__ + ": " + str(exc)[:105])
            target.unlink(missing_ok=True)
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                time.sleep(4)
            continue
    return {"result":"unavailable_or_short", "id": vid, "slug": slug,
            "stage": item["stage"], "attempts": attempts,
            "first_errors": failures[:4], "last_errors": failures[-5:]}


def main():
    results = []
    # Restricted to a small, human-curated set. Not an open-ended Pexels crawler.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(try_download, CANDIDATES):
            results.append(result)
    good = [r["meta"] for r in results if r["result"].startswith("downloaded")]
    kinds = {r["role"] for r in good if not r["role"].startswith("illustrative")}
    distinct = len({r["pexels_id"] for r in good})
    report = {
        "episode":"EP07", "status":"private_source_qa_only",
        "unique_downloaded_video_files":distinct,
        "roles":sorted(kinds),
        "ready_to_render":False,
        "QA_APPROVED":False,
        "stage_ready":bool(distinct>=8 and {"harvest","crush","boil"}.issubset(kinds)),
        "reason":"Downloaded originals require independent motion, accuracy, variety and rights inspection; never turn QA flags green automatically.",
        "outputs":results
    }
    (ROOT/"EP07_Source_Acquisition_Report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("EP07 PRIVATE SOURCE RESULTS", distinct, sorted(kinds), flush=True)
    if not report["stage_ready"]:
        raise SystemExit("INCOMPLETE_SOURCE_STAGE: insufficient eligible distinct craft footage; retry or change leads")
    print("Source download stage only; video still NOT QA approved.", flush=True)


if __name__ == "__main__":
    main()
