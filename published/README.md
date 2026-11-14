# Published-episode receipt format (the automatic storage-cleanup trigger)

GitHub Actions uploads short-lived video preview ZIPs as **workflow artifacts**. These are NOT tracked in the Git repository. To automatically delete them only after an EP has successfully gone live on all four platforms, the Motion Blueprint Lab weekly automation writes one SMALL JSON file:

`published/EP02.json` or `published/EP03.json` ...

The commit of that file to the repository default branch triggers `.github/workflows/cleanup_published_artifacts.yml` immediately. The runner authenticates with its short-lived GitHub Actions token; DO NOT store any credentials here.

Example schema (illustrative values only — NEVER commit these sample URLs as a real published receipt):

```json
{
  "episode": "EP02",
  "publication_state": "complete",
  "platforms": {
    "youtube": {
      "status": "public_verified",
      "verification_method": "youtube_api",
      "verified_at": "2026-11-16T02:00:00+08:00",
      "url": "https://www.youtube.com/shorts/REAL_VIDEO_ID"
    },
    "facebook": {
      "status": "public_verified",
      "verification_method": "facebook_graph_api",
      "verified_at": "2026-11-16T02:01:00+08:00",
      "url": "https://www.facebook.com/reel/REAL_REEL_ID/"
    },
    "instagram": {
      "status": "public_verified",
      "verification_method": "instagram_graph_api",
      "verified_at": "2026-11-16T02:02:00+08:00",
      "url": "https://www.instagram.com/reel/REAL_REEL_CODE/"
    },
    "tiktok": {
      "status": "public_verified",
      "verification_method": "tiktok_native_page",
      "verified_at": "2026-11-16T02:03:00+08:00",
      "url": "https://www.tiktok.com/@motionblueprintlab/video/REAL_VIDEO_ID"
    }
  }
}
```

The cleanup script requires all four exact `public_verified` statuses and supported evidence sources. **Buffer `sent` is NOT enough for TikTok**. If any platform is missing/unverified/failed, DO NOT write a `complete` receipt, do not delete the video artifact, and retry only that failed platform.

The cleanup job uses the GitHub REST API to delete only GitHub Actions artifacts with names beginning `EP02_`/`EP02-` (matching the receipt EP code). It **never deletes** source files, scripts, episode JSON, narration scripts, rights/credits, public URL receipts, or other brands' artifacts. It does not delete video stored in Cloudinary or already published on social platforms.

Actions artifacts automatically expire after their workflow retention period if an episode remains pending. For further savings, avoid committing any `.mp4`, `.webm`, `.wav`, `.zip` or large raw footage to Git in the first place (see `.gitignore`).

**Status as of 2026-11-14:** EP02 R2 visual quality was approved as a style standard, but EP02 has not completed all publication/licensing/audio checks. It must not receive a `published/EP02.json` receipt yet.
