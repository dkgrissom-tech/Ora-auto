# Zara corpus

Drop source files here before running `build_brain.py --persona zara`.

## What to add

- **social/** — past Zara posts, threads, captions. One `.md` per source. If you have a batch export, split by post; the file boundaries help Claude count repetitions correctly.
- **long_form/** — any long-form Zara writing (character bio, backstory doc, blog posts written in her voice, script excerpts).
- **voice/** — transcripts of Zara voice content (ElevenLabs script inputs, video VO scripts, coaching-call transcripts if she's used as a coach persona).
- **product/** — Ora landing-page copy Zara has narrated, launch notes, PRD sections that describe her stance.

## Minimum viable corpus for a first brain map

- 20-30 short social captions (or the 5-day launch bundle currently in `brands/ora/posts/`)
- 1-2 long-form pieces (character bio + one launch essay)
- 3-5 voice-over scripts

If you have less than this, the brain map will be thin and you'll be hand-editing more than you'd like. That's fine for a first pass — the diff mode preserves your edits when you add more corpus later.

## What NOT to add

- Files written by *other* personas (Don-as-founder, Grissom Press author voice). Those get their own persona directory.
- Raw AI-generated content that hasn't been human-approved as "on-voice." You'll poison the brain map with generic AI-ese.
- Analytics/metrics files. Those belong in the future D0/D7 feedback loop, not the voice corpus.
