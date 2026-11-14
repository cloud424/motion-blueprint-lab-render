# Motion Blueprint Lab | Cloud Video Render
This is the dedicated public GitHub Actions **engineering explainer preview renderer** for **Motion Blueprint Lab**. It is not the HitWave Charts or Momo & Pip production system.

## Live project wiring
- ChatGPT weekly automation (Asia/Taipei Monday 02:00): `6af660f40f34819199ff6e00c8532f21`
- Make team: `3423562`
- Make episode project queue: Data Store `201478`
- Make approved-video four-site dispatcher: scenario `7035615`
- Already released: EP01 Taipei 101. This repository starts at **EP02**.

## Safe rendering
1. GitHub Actions generates an EP02 **technical preview only** while its manifest has `status: script_ready_render_pending`.
2. The preview is a **silent, watermarked technical test**, delivered as a GitHub Actions artifact; it is not published to video platforms.
3. Only a licensed actual-footage URL and verified Grady voice asset may enable a real full-video render.
4. This repository does **not** automatically publish to YouTube, Facebook, Instagram or TikTok, and does **not** automatically spend paid voice/video credits.
5. Rights, the final visuals, sound, uniqueness and original editorial value must be checked **from the actual finished file**. A checklist or flags in JSON cannot replace this review.
6. The downstream Make dispatcher itself blocks missing approval and pending QA flags; it must only receive evidence-backed approvals.

## Use
From the GitHub repository: Actions > Motion Blueprint Lab - safe preview renderer > Run workflow > choose EP02. The workflow runs on commits to its source/manifest, and may also be manually triggered.

Development and tests use `python -m py_compile scripts/render_episode.py`, `python -m pip install Pillow`, `ffmpeg`, and `python scripts/render_episode.py --episode episodes/EP02_PanamaCanal_GravityLocks.json --outdir out --test-only --duration 2`.

## Licensing
Facts: https://pancanal.com/en/design-of-the-locks/
US Navy footage candidate: https://commons.wikimedia.org/wiki/File:Continuing_Promise_transits_the_Panama_Canal-ZLIWzvfdisQ-248%2B251.webm
Commercial reuse and embedded third-party media require verification before real use.

**Status 2026-11-14:** preview pipeline deployment, **not full unattended weekly production**.