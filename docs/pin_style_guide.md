# Handy Hearts — Pin Visual System

The binding style contract for all 66 missing Handy Hearts pin images. Every prompt in
`docs/pin_prompts/` inherits this. Do not deviate per-pin; vary the subject, not the look.

## Non-negotiables

**Aspect ratio 2:3, output 1000 × 1500 px.** Pinterest's standard pin. Taller than 2:3
gets truncated in feed; square loses reach.

**No text in the generated image.** Generate clean artwork, then add the headline in
Canva. Image models produce mangled, unfixable lettering, and baked-in text can't be
corrected or A/B tested later. Every prompt therefore reserves a **quiet zone** — an
uncluttered area of low detail in either the top third or bottom third — for the overlay.
The prompt states which.

**No identifiable faces.** This is both an aesthetic and a practical rule. The romance
Pinterest convention is hands, backs of heads, silhouettes, cropped torsos, and objects
that imply a person. It also keeps you clear of likeness problems and avoids the
uncanny-face failure common to generated portraits. Dana and Don are never shown
face-on.

## Palette

Warm neutral base, one cool accent. Do not let it drift teal-and-orange.

| Role | Colour | Where |
|---|---|---|
| Base | weathered cedar, warm mid-brown | wood, porch, tools |
| Light | honey gold, late-afternoon | the dominant light source |
| Soft | cream, unbleached linen | fabric, curtains, paper |
| Cool accent | dusty sage green | wildflowers, painted trim, foliage |
| Deep | faded denim blue | shirts, shadow, dusk sky |
| Accent, sparingly | rust orange | brick, a coffee mug, hardware |

## Look

- **35mm film, Kodak Portra 400.** Visible fine grain, gentle halation on highlights,
  slightly lifted blacks. Photographic, not illustrated, not 3D.
- **Natural light only.** Golden hour or overcast soft light. No studio strobes, no
  neon, no rim-light glamour.
- **Shallow-to-medium depth of field.** f/2.8–f/4. Background soft but legible as a
  place, never abstract mush.
- **Composition:** single clear subject, off-centre, generous negative space. Pinterest
  is browsed at thumbnail size — one idea per pin, readable at 200 px wide.
- **Emotional register:** quiet, lived-in, a little melancholy. Warmth without sweetness.
  The series tagline is "Grief doesn't end. It changes shape." Every image should feel
  like the moment just after something, not the event itself.

## Setting truth

**Cedar Hollow is in OKLAHOMA** — Muskogee County, population 1,847. Not Tennessee.
This matters visually: eastern Oklahoma is oak and hickory woodland, red clay soil,
rolling green hills, big sky. It is **not** Appalachian mountains, not blue ridges, not
misty peaks. Think Green Country: farm ponds, blackjack oak, cross-timbers, gravel
county roads, sandstone outcrops.

Recurring locations: Dana's house with the collapsed back porch · the Hollow Bean Café
(Nancy Beaumont's, warm wood and mismatched china) · Don's truck and toolbox · a small
main street of low brick storefronts.

## Character objects, never faces

- **Don Rourke** — handyman, 42, ex-Navy Seabee. Worn canvas work jacket, faded denim,
  scuffed leather boots. Hands: calloused, marked, a little dirty. Tools are well-kept
  and old. A steel thermos.
- **Dana Whitfield** — widow, fourteen months. Honey-blonde. **Still wears her wedding
  ring** — this is the series' central image, so hands with a plain gold band recur.
  Cream cardigan, garden clogs, a chipped mug.
- **Nancy Beaumont** — the Hollow Bean Café. Ceramic, steam, morning light on a counter.

## Anti-slop constraints

Add to every prompt: no floating dust particles or lens flare, no teal-and-orange
grading, no plastic or waxy skin, no illegible pseudo-text on signs or labels, no
oversaturated HDR, no Appalachian mountain ranges, no wedding-photography glow, no
stock-photo staging or eye contact with the camera.

## Text overlay, done after generation

In Canva, at 1000 × 1500:

- Headline in the reserved quiet zone. Serif for emotional pins (Playfair Display,
  Cormorant), clean sans for utility pins like ARC recruitment or preorder CTAs
  (Inter, Montserrat).
- Max ~7 words. It must be readable in the feed at thumbnail size.
- Cream `#F4EDE4` type over dark areas, deep cedar `#3B2B22` over light ones. Check
  contrast; skip drop shadows in favour of a subtle dark scrim at 15–25% if needed.
- Small `D.K. GRISSOM` and `SEPTEMBER 8` line at the base of every pin.
- The `pinterest_title` in each prompt file is the intended overlay text.

## Filing the finished images

Save each with **the exact filename given in its prompt** — the scheduler builds a
`raw.githubusercontent.com` URL from that path, so a renamed file still 404s and the
pin still fails.

```bash
# from the repo root, after dropping images into brands/grissom/assets/
git add brands/grissom/assets/ && git commit -m "feat(assets): add Handy Hearts pin images [skip ci]" && git push
```

Verify before trusting it:

```bash
python3 - <<'EOF'
import re,pathlib
missing=[m.group(2) for f in pathlib.Path('brands').glob('*/posts/*.md')
         for m in re.finditer(r'^(image|video):\s*(\S+)', f.read_text(), re.M)
         if not pathlib.Path(m.group(2)).exists()]
print(f"{len(missing)} still missing"); [print(" ",p) for p in sorted(set(missing))[:10]]
EOF
```

That count must fall as you add files. It started at 82.
