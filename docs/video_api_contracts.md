# Video API Contracts

Reference doc for debugging n8n Workflow 2 calls to both video generators.

---

## Auth Header (both APIs)

Every request must include:
```
X-API-Key: <value of YT_STUDIO_API_KEY or CIG_API_KEY>
```

Missing or wrong key → `401 {"error": "Invalid or missing X-API-Key header"}`

---

## YT Studio API (`$vars.YT_STUDIO_API_URL`)

Production URL (after deploy): `https://yt-studio-grissom.replit.app`
Custom domain (after Cloudflare): `https://studio.grissompress.com`

### Health Check
```
GET /health
Response: { "status": "ok", "service": "yt-studio-api" }
```

### POST /api/research
```json
// Request
{ "niche": "romance authors", "profession": "indie novelist", "count": 10 }

// Response
{
  "topics": [
    { "title": "How I Published My First Romance in 30 Days", "hook": "I had no idea what I was doing.", "score": 8 },
    ...
  ]
}
```

### POST /api/scripts
```json
// Request
{
  "topic": "3 tools every indie romance author needs",
  "hook": "Most authors waste 40% of their time on this.",
  "template": "hook-problem-shift-tools-close"
}

// Response
{
  "script": {
    "hook": "Most authors waste 40% of their time on formatting.",
    "problem": "You write a book. Then spend 6 hours in Word trying to make it look right...",
    "shift": "There are tools that do this in 4 minutes. Here are 3 of them.",
    "tools": "Vellum formats your ebook and print version simultaneously...",
    "close": "Pick one. Set it up this week. Stop bleeding time on formatting."
  },
  "estimated_duration_sec": 52
}
```

Templates available: `hook-problem-shift-tools-close`, `listicle`, `story`

### POST /api/voice
```json
// Request
{
  "script_text": "Most authors waste 40% of their time on formatting. Here are 3 tools...",
  "voice_id": "pNInz6obpgDQGcFmaJgB"
}

// Response
{
  "audio_url": "https://yt-studio-grissom.replit.app/api/audio/<uuid>",
  "audio_id": "<uuid>",
  "timestamps": [
    { "word": "Most", "start": 0.0, "end": 0.3 },
    { "word": "authors", "start": 0.35, "end": 0.65 },
    ...
  ],
  "duration_sec": 52.4
}
```

Voice IDs (ElevenLabs): Get from ElevenLabs dashboard → Voices → click voice → copy ID from URL.

### POST /api/video
```json
// Request
{
  "script_text": "Most authors waste 40% of their time on formatting...",
  "audio_url": "https://yt-studio-grissom.replit.app/api/audio/<uuid>",
  "timestamps": [ { "word": "Most", "start": 0.0, "end": 0.3 }, ... ],
  "template": "scrolling-text-gradient",
  "aspect": "9:16"
}

// Response (immediate — job submitted)
{ "job_id": "<uuid>", "status": "queued" }
```

Templates: `scrolling-text-gradient`, `minimal-dark`, `bold-yellow`, `neon-outline`
Aspects: `9:16` (TikTok/Reels/Shorts), `16:9` (YouTube long-form), `1:1` (LinkedIn/Instagram feed)

### GET /api/video/:job_id
```json
// While rendering
{ "status": "rendering", "video_url": null, "error": null, "started_at": 1722000000 }

// When done
{ "status": "done", "video_url": "https://yt-studio-grissom.replit.app/api/video-file/<uuid>", "completed_at": 1722000120 }

// If failed
{ "status": "failed", "error": "ffmpeg error: ...", "failed_at": 1722000060 }
```

### POST /api/thumbnail
```json
// Request
{
  "template": "viral-yellow",
  "headline": "I Published 12 Books Last Year",
  "sub": "Here's exactly how",
  "badge": "VIRAL"
}

// Response
{ "thumbnail_url": "https://yt-studio-grissom.replit.app/api/thumbnail-file/<uuid>", "thumbnail_id": "<uuid>" }
```

Templates: `viral-yellow`, `dark-bold`, `clean-white`, `grissom-press`

---

## Content Ideas Generator API (`$vars.CIG_API_URL`)

Production URL (after deploy): `https://content-ideas-grissom.replit.app`
Custom domain (after Cloudflare): `https://videos.grissompress.com`

### POST /api/generate-video
```json
// Request
{
  "beat_sheet": [
    { "scene_type": "title", "text": "You're waking up wrong", "duration_sec": 3 },
    { "scene_type": "stat", "text": "87% of people check their phone first", "duration_sec": 4 },
    { "scene_type": "quote", "text": "Win the morning, win the day", "duration_sec": 3 },
    { "scene_type": "callout", "text": "Do THIS instead →", "duration_sec": 3 }
  ],
  "voice_id": "pNInz6obpgDQGcFmaJgB",
  "aspect": "9:16",
  "music_mood": "energetic"
}

// Response (immediate)
{ "job_id": "<uuid>", "status": "queued" }
```

Scene types:
- `title`: Large centered text, often hook/opening
- `stat`: Statistic or fact, usually highlighted differently
- `quote`: Styled quote block
- `callout`: CTA or punchy emphasis line

Music moods: `warm`, `energetic`, `calm`

### GET /api/video/:job_id
Same response format as YT Studio.

---

## n8n Integration Sequence (Workflow 2)

```
IF video_source == "yt-studio":
  1. POST /api/scripts        → { script, estimated_duration_sec }
  2. POST /api/voice          → { audio_url, timestamps, duration_sec }
  3. POST /api/video          → { job_id }
  4. LOOP: GET /api/video/:job_id every 30s until status == "done"
  5. Use video_url from step 4 response

IF video_source == "content-ideas-generator":
  1. POST /api/generate-video → { job_id }
  2. LOOP: GET /api/video/:job_id every 30s until status == "done"
  3. Use video_url from step 2 response

Both: video_url is a direct mp4 link — pass it to platform upload nodes.
```

---

## Common Debug Steps

**401 from video API**: Check `X-API-Key` header matches the env var on Replit exactly (no spaces, copy-paste from secret manager).

**Job stuck in "queued"**: Replit app is sleeping (dev preview mode). Deploy to Autoscale. After deploy, hit `/health` in browser to wake it.

**Job "failed" with ffmpeg error**: ffmpeg may not be installed in Replit. Add to replit.nix: `pkgs.ffmpeg`. Or use Replit's nix package manager in the Shell tab: `nix-env -iA nixpkgs.ffmpeg`.

**Remotion render fails (CIG)**: Check `REMOTION_DIR` env var points to the correct folder in Replit. Run `npx remotion versions` in the Replit shell to verify Remotion is installed.

**Video URL not publicly accessible**: Replit dev preview URLs are not publicly accessible. Must deploy to Autoscale first. After deploy, test: `curl -H "X-API-Key: <key>" https://yt-studio-grissom.replit.app/health`
