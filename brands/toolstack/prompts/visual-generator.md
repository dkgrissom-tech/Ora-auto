# Visual Generator — Toolstack Animal Shorts

Two supported routes. Prefer Higgsfield when the account/API is live;
fall back to fal.ai Flux Pro + FFmpeg motion for cost-controlled tests.

## Route A — Higgsfield (motion video)

Repo: `dkgrissom-tech/tiktok-product-video-machine`
Module: `lib/higgsfield.ts`
Env: `HIGGSFIELD_API_KEY` in that project's deployment env.

Prompt template:

```
Cinematic vertical 9:16. <character>, <setting>, <one action beat>,
<one reaction beat>, <payoff visual>. Expressive animal face, quick
cuts, <tone> lighting, playful comedy tone.
```

Duration: 20–25 seconds. Aspect: 9:16. Output: MP4.

## Route B — Flux Pro scenes + FFmpeg (cheap fallback)

- 5–7 stills at 1080×1920 from fal.ai Flux Pro
- Reuse a character reference image per series to keep faces consistent
- Ken Burns zoom + cuts every 2–3 seconds via FFmpeg
- ElevenLabs VO in a consistent voice per character
- Burned-in captions (FFmpeg drawtext or ASS subtitle)

## Character reference discipline

Save one canonical reference image per character in
`brands/toolstack/assets/refs/`:

- `refs/milo.png` — orange tabby, small blue tie, expressive
- `refs/rita.png` — clever raccoon, suburban vibe
- `refs/barkley.png` — golden retriever, rumpled trench coat
- `refs/hamster-ceo.png` — hamster in suit, tiny desk

Pass the matching ref as an image conditioning input on every scene
generation so faces stay recognizable across episodes.
