# brands/toolstack — Animal Shorts test queue

Staged content lane for the `@toolstack-y4g` TikTok audience-growth
account. Nothing in this folder publishes until it's activated in a
separate change.

## Layout

```
brands/toolstack/
  brand.md                     brand rules + activation gates
  README.md                    this file
  posts/
    2026-09-20.md              Milo #1 + Rita #1
    2026-09-21.md              Barkley #1 + Milo #2
  assets/                      finished MP4s land here as <CREATIVE_ID>.mp4
  prompts/
    story-generator.md
    visual-generator.md
    video-assembly.md
  learnings/
    performance.csv            per-post results log
```

## Activation checklist (do NOT run any of these yet)

1. Render four MP4s into `assets/` using the Higgsfield generator in
   `dkgrissom-tech/tiktok-product-video-machine`.
2. Verify a Postiz TikTok channel exists and is authorized for
   `@toolstack-y4g`.
3. Add `'toolstack'` to the BRANDS list in:
   - `n8n_workflows/workflow_video_pipeline_v3_postiz.json`
   - `scripts/run_scheduler.py` (if the scheduler is used)
4. Remove `publish: false` and change `platforms: staging` to
   `platforms: tiktok` in each queued post block.
5. Run one post as a dry-run first, verify the destination account,
   then release the remaining three.

None of the four steps above has been performed. This commit only
stages content and configuration.
