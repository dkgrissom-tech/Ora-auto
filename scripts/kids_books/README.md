# Kids Books — Halloween Page-Turner Pipeline

## What lives here

- `page-turner-generator.ts` — Express route to add to YT Studio. Takes a story concept and produces MP4 + KDP interior PDF + narration.
- `halloween-book-concepts.md` — Story concepts for Pip / Bibi / Midnight (the 3 Halloween launches).

## How it plugs into the existing v3 video pipeline

1. Run the generator route on YT Studio Replit for each of the 3 books.
2. Upload the finished MP4 as a public asset (S3, Cloudflare R2, or GitHub Release).
3. Update the corresponding draft in `video_drafts/grissom/` — replace `video_url: PLACEHOLDER_UPDATE_AFTER_GENERATOR_RUNS` with the real URL.
4. Commit + push. `workflow_video_pipeline_v3_postiz.json` will pick it up on the next :15 tick and publish to TikTok + Instagram at the scheduled time.

## Env vars

Already in Railway per PLAYBOOK.md:
- `ANTHROPIC_API_KEY`
- `ELEVENLABS_API_KEY`

New for kids books (add to Railway + GitHub Actions if generator runs in CI):
- `FAL_API_KEY` — from fal.ai/dashboard/keys after signup

## Cost per book (~$1.50)

- Claude story: ~$0.02
- fal.ai Flux Pro illustrations (21 images): ~$1.05
- ElevenLabs narration (Rachel voice for kids, ~90 sec): ~$0.40
