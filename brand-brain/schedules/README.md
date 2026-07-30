# brand-brain/schedules

One YAML file per brand describes what to generate each week: which persona
speaks, which platforms fire, which hours, which agent template to use, and
any brand-level gates.

The `generate_posts.yml` workflow reads these on Sunday night, runs
`generate_week.py`, and opens a draft PR with next week's post files under
`brands/<brand>/posts/YYYY-MM-DD.md`.

## Schema

```yaml
brand: ora                  # required: matches brands/<brand>/ directory
persona: zara               # required: matches brand-brain/brands/<persona>/
enabled: true               # if false, skipped entirely
gates:
  # Optional. Each gate is a file path that must exist relative to repo root.
  # Missing any gate = generation aborts for this brand with a clear log line.
  # Use for launch blockers like Build 100 (see below).
  - path: .gates/build-100-shipped
    reason: "Ora launch content is gated on the interruption-safe recap"

slots:
  # Each slot is one scheduled post per day.
  # day_of_week: mon|tue|wed|thu|fri|sat|sun|weekday|weekend|all
  # hour_utc:    integer 0-23 (matches the ## HH:00 UTC block header)
  # platforms:   list; must be a subset of the scheduler's supported platforms
  # agent:       matches brand-brain/brands/<persona>/agents/<agent>.md
  # angle:       optional day-specific hint; passed to the agent as {{angle}}
  #              (leave blank for "surprise me based on brain map")
  # asset:       optional; image or video path relative to repo root

  - day_of_week: mon
    hour_utc: 14
    platforms: [bluesky, linkedin, threads]
    agent: bluesky_thread   # long-form for LinkedIn, adapted for Bluesky/Threads
    angle: "week-open teach: one specific problem with Otter/Fireflies"

  - day_of_week: mon
    hour_utc: 18
    platforms: [bluesky, threads, instagram, tiktok]
    agent: ig_poster
    angle: "peer-story hook: 'a founder tried Ora after…'"
    asset: brands/ora/assets/zara_meetora_9x16.mp4

  - day_of_week: weekday
    hour_utc: 22
    platforms: [linkedin]
    agent: linkedin_post
    angle: "close-of-day insight, single beat, no CTA"
```

## Gate files

Any file listed under `gates:` must exist for generation to proceed. Use
these to block content generation on unmet product prerequisites.

- **Build 100 gate** for Ora: create `.gates/build-100-shipped` (empty file
  is fine) once the interruption-safe recap ships. Until then, the workflow
  refuses to generate new Ora launch content, matching Don's rule that
  launch stays paused until this ships.

- **KDP-live gate** for Grissom: create `.gates/kdp-book-live` when the
  first Cedar Hollow book is live on KDP. Blocks Grissom Press posts that
  need a live buy link.

Add new gates by dropping a file into `.gates/` and referencing it here.

## Generation cost

At ~$0.02 per agent call, a full brand-week of 15 slots ≈ $0.30.
Three brands × weekly ≈ $1/week in generation costs.

## Dry-run

Run manually before enabling the cron:

```bash
python brand-brain/scripts/generate_week.py --brand ora --dry-run
```

Prints what would be written, without calling Anthropic or touching files.
