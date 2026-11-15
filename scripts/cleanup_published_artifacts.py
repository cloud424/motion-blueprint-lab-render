#!/usr/bin/env python3
"""Delete GitHub Actions *video artifacts* for episodes confirmed live on all 4 platforms.

Never delete repository source files, release history, draft/pending episodes or artifacts
for a partially published episode. GitHub workflow runs and logs are not deleted.
Receipts live in published/EPxx.json and must hold independently checked public URLs.
"""
import argparse
import json
import os
import pathlib
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

EP_RE = re.compile(r"^EP[0-9]{2,}$")
STAGING_RELEASE_TAGS = {"EP02": "mbl-ep02-r2-media-staging"}  # Only expressly owned temporary media releases
ALLOWED = {
    "youtube": {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"},
    "facebook": {"facebook.com", "www.facebook.com", "m.facebook.com"},
    "instagram": {"instagram.com", "www.instagram.com"},
    "tiktok": {"tiktok.com", "www.tiktok.com", "m.tiktok.com"},
}
EVIDENCE = {
    "youtube": {"youtube_api", "public_page"},
    "facebook": {"facebook_graph_api", "public_page"},
    "instagram": {"instagram_graph_api", "public_page"},
    "tiktok": {"tiktok_native_page", "tiktok_public_api"},
}

def verified_receipt(data):
    ep = data.get("episode")
    if not isinstance(ep, str) or not EP_RE.fullmatch(ep):
        return False, "bad episode"
    if data.get("publication_state") != "complete":
        return False, "episode not fully published"
    places = data.get("platforms")
    if not isinstance(places, dict):
        return False, "platform records missing"
    for site, domains in ALLOWED.items():
        item = places.get(site)
        if not isinstance(item, dict):
            return False, site + " not recorded"
        if item.get("status") != "public_verified":
            return False, site + " not verified public"
        if item.get("verification_method") not in EVIDENCE[site]:
            return False, site + " lacks acceptable verification evidence"
        if not item.get("verified_at"):
            return False, site + " has no verification time"
        url = item.get("url", "")
        if not isinstance(url, str):
            return False, site + " invalid URL"
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in domains or not parsed.path.strip("/"):
            return False, site + " invalid public URL"
    return True, ep

def matching_artifacts(ep, artifacts):
    return [a for a in artifacts if re.match("^" + re.escape(ep) + r"(?:[_-]|$)", a.get("name", "")) and not a.get("expired", False)]

def request_json(url, token, method="GET"):
    req = Request(url, headers={"Accept":"application/vnd.github+json",
        "Authorization":"Bearer "+token,
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"MotionBlueprintLab-PublishedArtifactCleaner"},
        method=method)
    with urlopen(req,timeout=30) as resp:
        if method == "DELETE":
            return {"status":resp.status}
        return json.load(resp)

def list_artifacts(repo, token):
    base="https://api.github.com/repos/"+repo+"/actions/artifacts"
    output=[]
    for page in range(1,21):
        result=request_json(base+"?per_page=100&page="+str(page),token)
        batch=result.get("artifacts",[])
        output.extend(batch)
        if len(batch)<100:break
    return output

def cleanup(directory, repo, token, execute=False):
    docs=sorted(pathlib.Path(directory).glob("EP*.json"))
    artifacts=list_artifacts(repo,token) if docs else []
    kept=[];removed=[];released=[]
    for file in docs:
        try:
            receipt=json.loads(file.read_text(encoding="utf-8"))
        except Exception as exc:
            kept.append({"file":file.name,"reason":"unreadable receipt "+str(exc)})
            continue
        good, ep_or_reason=verified_receipt(receipt)
        if not good or file.stem!=receipt.get("episode"):
            kept.append({"file":file.name,"reason":ep_or_reason if not good else "filename mismatch"})
            continue
        for artifact in matching_artifacts(ep_or_reason, artifacts):
            item={"episode":ep_or_reason,"id":artifact["id"],"name":artifact["name"]}
            if execute:
                request_json("https://api.github.com/repos/"+repo+"/actions/artifacts/"+str(artifact["id"]),token,"DELETE")
                removed.append(item)
            else:
                kept.append({**item,"reason":"dry run"})
        # Temporary public GitHub release media must not be kept after verified distribution.
        tag=STAGING_RELEASE_TAGS.get(ep_or_reason)
        if tag:
            endpoint="https://api.github.com/repos/"+repo+"/releases/tags/"+tag
            try:
                release=request_json(endpoint,token)
                if execute:
                    request_json("https://api.github.com/repos/"+repo+"/releases/"+str(release['id']),token,"DELETE")
                    released.append({"episode":ep_or_reason,"tag":tag,"releaseId":release['id']})
                else:
                    kept.append({"episode":ep_or_reason,"tag":tag,"reason":"release dry run"})
            except HTTPError as err:
                if err.code != 404:raise
                kept.append({"episode":ep_or_reason,"tag":tag,"reason":"staging release already absent"})
    return {"mode":"execute" if execute else "dry-run","receipts":len(docs),"deleted":removed,"staging_releases_deleted":released,"kept":kept}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receipts",default="published")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    repo=os.environ.get("GITHUB_REPOSITORY","")
    token=os.environ.get("GH_TOKEN","")
    if not repo or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repo):
        raise SystemExit("Missing valid GITHUB_REPOSITORY")
    if not token:raise SystemExit("Missing GH_TOKEN")
    result=cleanup(a.receipts,repo,token,execute=a.execute)
    print(json.dumps(result,indent=2))
    if result["deleted"]:print("Published EP artifacts cleaned: "+str(len(result["deleted"])))

if __name__=="__main__":
    main()
