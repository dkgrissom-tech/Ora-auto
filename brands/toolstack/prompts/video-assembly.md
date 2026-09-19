# Video Assembly — Toolstack Animal Shorts

## Target spec

- 9:16, 1080×1920
- 18–28 seconds
- 24 or 30 fps
- Burned-in captions (never rely on TikTok auto-captions)
- Audio: -14 LUFS integrated, -1 dBTP peak
- MP4 (H.264 + AAC)

## Assembly order

1. Scenes → concatenate with 200ms crossfades
2. VO track (ElevenLabs) aligned to script timing
3. Music bed at -20 dB under VO, ducked
4. Burned captions, 3–5 words per beat, high-contrast
5. Final CTA card, 1.5 seconds, "Follow for [character]'s next [thing]"

## FFmpeg baseline

```bash
ffmpeg -y \
  -i vo.wav -i music.mp3 -i scenes.mp4 \
  -filter_complex "[1:a]volume=0.15[m];[0:a][m]amix=inputs=2:duration=first[a]" \
  -map 2:v -map "[a]" \
  -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 20 \
  -c:a aac -b:a 160k -ar 48000 \
  -movflags +faststart \
  brands/toolstack/assets/<creative_id>.mp4
```

## Naming

Finished MP4 must be saved at:

```
brands/toolstack/assets/<CREATIVE_ID>.mp4
```

The queued post file's `video:` field already points there. Rendering
into that exact path is what activates the post (along with removing
`publish: false` and adding `toolstack` to the video pipeline BRANDS
list).
