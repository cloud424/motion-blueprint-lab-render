# Motion Blueprint Lab | Cloud Video Render
This is the dedicated public GitHub Actions **engineering explainer preview renderer** for **Motion Blueprint Lab**. It is not the HitWave Charts or Momo & Pip production system.

## Live project wiring
- ChatGPT EP production/recovery automation (Asia/Taipei 05:00, 11:00, 17:00, 23:00 every six hours; enabled 2026-11-28): `6af660f40f34819199ff6e00c8532f21`\n- Make QA-only release scheduler Mon/Wed/Fri 02:00 Asia/Taipei: scenario `7091723`
- Make team: `3423562`
- Make episode project queue: Data Store `201478`
- Make approved-video four-site dispatcher: scenario `7035615`
- Already released: EP01 Taipei 101. This repository starts at **EP02**. Production target for each new release: **about 3 minutes, ideally 2:45-2:55, vertical 720x1280**, subject to original licensed real footage, genuine moving engineering diagrams and approved Grady English narration.

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

**Status 2026-11-28:** EP06 four-site native public verified on 2026-11-25. EP07 traditional sugar is IN PRODUCTION, with no final QA-approved MP4 yet. Research, candidates, private GitHub footage acquisition, stage-state ledger and automatic retries exist; never mistake a successful release check for a published EP. See `episodes/EP07_Recovery_State.json` and `episodes/EP07_TraditionalSugar_R3_Draft.json`. Only mark Make queue ready after a real 165-175s film passes source/license/motion/voice/subtitle/full-decode gates. No footage or automated publication of EP07 is confirmed.
## Mandatory visual production baseline — EP02 R2 approved (2026-11-14)

The channel owner approved **EP02 Panama Canal R2** as the minimum standard for all future engineering documentaries. An approximately three-minute vertical film needs authentic licensed real-world footage, at least **six distinct technically accurate original animated engineering views**, and meaningful changes of shot or information approximately every 10–15 seconds. Examples: aerial/overhead operation, detailed moving joints and mechanical gates, hydraulic culverts, distributed inlets, pressure / buoyancy forces, and system-level sequencing. **Never pad the runtime with the same ship-and-water-level diagram bobbing up and down, blank backgrounds, or static slides.** Audio remains English, preferably the approved Grady voice when rights/cost permit.

**Important:** This commits only the editorial standard. The GitHub Actions EP02 pilot renderer is still an older R1-style design until its code is actually revised and retested. The locally prepared R2 preview is not uploaded into this repository. EP02 R2 user approval of visual density is not authorization to publish without final audio/footage-rights QA.
