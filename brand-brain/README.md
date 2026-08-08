# brand-brain

Two-stage voice/persona system for multi-brand content generation.

**Pattern:** one hand-editable JSON "brain map" per persona → per-role agent prompts that inherit it → structured output the Ora-auto posting rail can consume.

## Layout

```
brand-brain/
  brands/<persona>/
    corpus/              # raw source material (git-tracked, read-only for the pipeline)
      social/            # past posts, threads, captions (one .md per source)
      long_form/         # blog posts, book excerpts, transcripts
      voice/             # coaching-call transcripts, voice memos (text form)
      product/           # PRDs, landing pages, launch notes
    brain/
      brain_map.json     # Stage 1 output — hand-edit after generation
      style_examples.jsonl  # 20-40 verbatim snippets tagged by mode
    agents/
      ig_poster.md       # Stage 2 — role prompt (Jinja-style {{placeholders}})
      # (more agents added as needed)
  scripts/
    build_brain.py       # Stage 1 runner
    agent_run.py         # Stage 2 runner
  schemas/
    brain_map.schema.json
```

## Personas vs. brands

A **persona** is one voice (Zara, Don-as-Grissom-Press-author, Family Book Creator narrator).
A **brand** in the parent `brands/` folder is a distribution surface (ora, grissom, familybook).
One brand can host multiple personas — Zara is a persona hosted on the Ora brand.

## Stage 1 — Build the brain

```bash
export ANTHROPIC_API_KEY=...
python brand-brain/scripts/build_brain.py --persona zara
```

Reads everything under `brands/zara/corpus/**`, produces `brain/brain_map.json` and `brain/style_examples.jsonl`.

**After the first run: hand-edit `brain_map.json`.** The whole point of this stack over UgenticIQ is that the DNA card is inspectable and correctable. Commit the hand edits.

Weekly re-runs use `--diff` mode: Claude proposes updates as a patch, hand-edits survive.

## Stage 2 — Generate

```bash
python brand-brain/scripts/agent_run.py \
  --persona zara \
  --agent ig_poster \
  --task "Day 3 Ora launch, video zara_meetora_9x16.mp4, angle: meeting recap that actually captures the interruption"
```

Outputs JSON to stdout (caption + hashtags + alt_text + 5 hook variants). Pipe into the Ora-auto post-file writer as a later PR.

## Cost

One Sonnet call per brain rebuild (~$0.30–0.80 depending on corpus size), one per agent invocation (~$0.01–0.03). Weekly rebuild + ~50 agent calls/week ≈ $1–3/persona/month.
