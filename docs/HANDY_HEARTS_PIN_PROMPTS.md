# Handy Hearts — 66 Pin Image Prompts

Everything needed to produce the missing Pinterest artwork for the *Handy Hearts*
preorder campaign (D.K. Grissom, launches **Tuesday Sept 8 2026**).

## Why this exists

66 of the 70 Pinterest posts already scheduled in `brands/grissom/posts/` point at image
files that were never created. The scheduler builds a `raw.githubusercontent.com` URL
from each path, so a missing file 404s and **Pinterest rejects the pin**. The posts fail
at the platform even though the publishing code is now correct. Full list:
`docs/MISSING_MEDIA_AUDIT.md`.

## How to use this

1. Read the visual system below once. It is what makes 66 images look like one campaign
   instead of 66 unrelated pictures.
2. Work through the prompts. Paste each **Prompt** block into your image generator; paste
   the **Avoid** line into a negative-prompt field if your tool has one, or append it.
3. Set output to **2:3, 1000 × 1500 px**. If your tool only offers 3:4 or 9:16, pick 3:4
   and crop to 2:3 — do not pick 9:16, it gets truncated in the Pinterest feed.
4. **Save each file under the exact `Save as:` path.** A renamed file still 404s and the
   pin still fails. This is the single most common way to waste the whole batch.
5. Add the **Overlay text** in Canva afterwards. The prompts deliberately generate no
   text and reserve a quiet zone for it — see the overlay section of the visual system.

### Which tool

Any competent photo-realistic model works, because none of these prompts require the
model to render text. If you want text baked in instead of using Canva, you need a
model specifically good at typography — but generated lettering can't be edited or
A/B tested later, so Canva is the better path for a 66-pin batch.

### Priority order if you can't do all 66

Do these first — earliest scheduled, so they fail soonest:

| Pin | Date | Why |
|---|---|---|
| 01–05 | Aug 4–8 | already past or publishing now |
| 06–14 | Aug 8–10 | this weekend |
| the ARC-recruitment pins | Aug 14 | they drive your launch team |

Everything from Aug 19 onward has no scheduled post yet, so it is not urgent.

---

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

---

## Batch 1 — pins 01–22

### Pin 01 — Wedding ring
**Save as:** `brands/grissom/assets/hh-pin-aug4-batch-pin1-she-still-wears-her-wedding-ring-2026-08-04.jpg`
**Scheduled:** 2026-08-04 14:00 UTC  (09:00 CDT)
**Overlay text:** She Still Wears Her Ring

**Prompt**
2:3 vertical photograph, 1000 × 1500 px. Extreme close-up of Dana’s left hand resting on a weathered cedar porch rail, a plain gold wedding band sharply in focus; a chipped rust-orange mug and soft oak-and-hickory yard fall behind at f/2.8. No identifiable face or person, only her cream cardigan cuff and hand. Late-afternoon sun comes from camera left, catching the band with restrained honey light. Use 35mm Kodak Portra 400 grain, lifted blacks, warm cedar-and-honey with dusty sage foliage. Place the hand off-centre low right; leave a quiet, low-detail top third for a Canva overlay, with no text in image.

**Avoid**
Extra jewelry, manicured fashion-ad hands, a diamond ring, wedding-photography glow, legible text, floating dust, lens flare, teal-orange grading, plastic skin, HDR, Appalachian peaks, stock staging, or eye contact.

### Pin 02 — Collapsed porch
**Save as:** `brands/grissom/assets/hh-pin-aug4-batch-pin2-the-porch-that-started-everything-2026-08-04.jpg`
**Scheduled:** 2026-08-04 17:00 UTC  (12:00 CDT)
**Overlay text:** The Porch That Started Everything

**Prompt**
2:3 vertical exterior detail, 1000 × 1500 px. Show Dana’s aging farmhouse back porch from knee height: one sagging cedar step has broken downward, loose boards reveal dark joists, and a single faded-denim work glove rests near a well-kept hammer. No identifiable faces; no people are visible. Soft overcast light reveals wood splinters, red-clay soil, and oak-and-hickory woodland of eastern Oklahoma without drama. Photograph on 35mm Kodak Portra 400 with fine grain, f/4, gently lifted blacks, warm cedar-and-honey tones and a dusty sage-painted porch post. Keep the damage off-centre left and reserve a quiet, low-detail bottom third for the Canva overlay; no text in image.

**Avoid**
Freshly renovated boards, catastrophic storm damage, construction crews, labels, floating dust, lens flare, teal-orange grading, HDR, misty mountain scenery, wedding glow, stock staging, or faces.

### Pin 03 — Don’s toolbox
**Save as:** `brands/grissom/assets/hh-pin-aug4-batch-pin3-he-fixes-things-with-his-hands-because-w-2026-08-04.jpg`
**Scheduled:** 2026-08-04 20:00 UTC  (15:00 CDT)
**Overlay text:** He Fixes Things With His Hands

**Prompt**
2:3 vertical still life, 1000 × 1500 px. An open, well-kept metal toolbox sits on the faded-denim tailgate of Don’s truck: hammer, wood plane, tape measure, screw tin, and steel thermos. No identifiable face or person; only a cropped canvas-jacket elbow may enter at the edge. Golden-hour light from behind right warms scuffed steel and cedar handles, while eastern Oklahoma oak leaves and red clay soften at f/3.5. Photograph in 35mm Kodak Portra 400 with grain, lifted blacks, warm cedar-and-honey and a dusty sage glove. Make the toolbox the single off-centre subject at right; reserve a quiet, low-detail top third for Canva overlay, with no text in image.

**Avoid**
Pristine showroom tools, branded labels, multiple toolboxes, messy clutter, floating dust, lens flare, teal-orange grading, waxy skin, oversaturated HDR, mountains, wedding glow, stock staging, or faces.

### Pin 04 — Grief changes shape
**Save as:** `brands/grissom/assets/hh-pin-aug4-batch-pin4-grief-does-not-end-it-changes-shape-2026-08-04.jpg`
**Scheduled:** 2026-08-04 23:00 UTC  (18:00 CDT)
**Overlay text:** Grief Does Not End. It Changes Shape.

**Prompt**
2:3 vertical interior still life, 1000 × 1500 px. A plain gold wedding band lies beside an unlit cream taper on a cedar bedside table, near Dana’s folded cream cardigan; make the ring the single clear subject. No identifiable face or person appears. Soft overcast daylight enters from the left through unbleached-linen curtains, keeping the farmhouse room quiet. Use 35mm Kodak Portra 400 film texture, f/2.8, gentle halation, lifted blacks, warm cedar-and-honey neutrals, and a faded-denim throw at the edge. Suggest eastern Oklahoma through worn wood and screen-window light. Position the ring low left and leave a quiet, low-detail top third for Canva overlay; no text in image.

**Avoid**
Funeral imagery, religious symbols, a portrait photo, ornate jewelry, heavy darkness, floating dust, lens flare, teal-orange grading, plastic fabric, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 05 — Cedar Hollow porch
**Save as:** `brands/grissom/assets/hh-pin-aug4-batch-pin5-small-town-old-porch-slow-burn-2026-08-04.jpg`
**Scheduled:** 2026-08-05 02:00 UTC  (21:00 CDT)
**Overlay text:** Small Town, Old Porch, Slow Burn

**Prompt**
2:3 vertical exterior wide photograph, 1000 × 1500 px. Frame Dana’s timeworn cedar porch and farmhouse across a red-clay drive; Don’s faded work truck sits beside the collapsed rear steps, with no people visible. No identifiable faces or figures. Early golden-hour sun from low right casts oak-leaf shadows across the porch; eastern Oklahoma cross-timbers and big sky remain legible at f/4. Shoot in 35mm Kodak Portra 400 with fine grain, lifted blacks, warm cedar-and-honey, dusty sage trim, and a faded-denim truck accent. Make the house the single off-centre subject at right and leave generous quiet, low-detail sky in the top third for Canva overlay; no text in image.

**Avoid**
Mansions, southern plantation styling, mountain backdrops, porch crowds, spotless new construction, readable signs, floating dust, lens flare, teal-orange grading, HDR, wedding glow, stock staging, or faces.

### Pin 06 — The diner starts stories
**Save as:** `brands/grissom/assets/hh-pin-aug5-batch-pin1-the-cedar-hollow-diner-where-every-story-2026-08-05.jpg`
**Scheduled:** 2026-08-05 14:00 UTC  (09:00 CDT)
**Overlay text:** The Diner Where Stories Start

**Prompt**
2:3 vertical interior counter scene, 1000 × 1500 px. At the Hollow Bean Café, coffee steams beside a slice of pie on a chipped cream plate; worn cedar counter grain is sharp, while stools and a Main Street window blur at f/3.2. No identifiable face or person; Nancy is implied by a cropped cardigan sleeve at the edge. Morning window light from left warms the scene. Use 35mm Kodak Portra 400 grain, lifted blacks, honey wood, cream ceramic, dusty sage tile, and a rust-orange napkin. Make the mug the single off-centre lower-right subject and reserve a quiet, low-detail top third for Canva overlay, with no text in image.

**Avoid**
Chain-coffee branding, diner neon, crowded patrons, faux menu lettering, food glamour styling, floating dust, lens flare, teal-orange grading, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 07 — Quietly showing up
**Save as:** `brands/grissom/assets/hh-pin-aug5-batch-pin2-in-cedar-hollow-you-cannot-keep-a-secret-2026-08-05.jpg`
**Scheduled:** 2026-08-05 17:00 UTC  (12:00 CDT)
**Overlay text:** Cedar Hollow Never Keeps Secrets

**Prompt**
2:3 vertical documentary-style detail, 1000 × 1500 px. A faded-denim-sleeved hand sets a covered homemade pie on Dana’s weathered porch bench beside a brown bottle and folded cream dish towel, as if neighbors arrived and left. Crop at the wrist: no identifiable face or person. Golden light from right catches the pie tin and cedar grain; eastern Oklahoma oak, hickory, red clay, and a dusty sage porch post soften at f/3.5. Use 35mm Kodak Portra 400 grain, lifted blacks, warm cedar-and-honey, and a rust-orange bottle cap. Make the pie the single off-centre left subject; retain a quiet, low-detail bottom third for Canva overlay, with no text in image.

**Avoid**
Visible pie labels, party decorations, extra hands, picnic-table styling, faces, floating dust, lens flare, teal-orange grading, waxy skin, HDR, mountains, wedding glow, or stock staging.

### Pin 08 — The town witnesses
**Save as:** `brands/grissom/assets/hh-pin-aug5-batch-pin3-small-towns-do-not-let-you-hide-2026-08-05.jpg`
**Scheduled:** 2026-08-05 20:00 UTC  (15:00 CDT)
**Overlay text:** Small Towns Do Not Let You Hide

**Prompt**
2:3 vertical view from inside Dana’s parked truck, 1000 × 1500 px. Through a rain-speckled windshield, show one unfamiliar faded-denim work truck parked next door on a red-clay drive; its toolbox catches overcast light. Dana’s ringed hand rests out of focus at lower left. No identifiable faces or people. Oak and hickory trees, low brick roofs, and rolling eastern Oklahoma ground remain readable at f/4, never mountainous. Render with 35mm Kodak Portra 400 grain, lifted blacks, warm cedar-and-honey interior tones, and dusty sage foliage. Make the truck the single off-centre right subject; leave a quiet, low-detail top third of pale sky for Canva overlay, with no text in image.

**Avoid**
Rearview reflections of faces, dramatic rainstorm, police or surveillance cues, readable truck badges, floating dust, lens flare, teal-orange grading, plastic skin, HDR, Appalachian peaks, wedding glow, or stock staging.

### Pin 09 — Porch coffee
**Save as:** `brands/grissom/assets/hh-pin-aug5-batch-pin4-coffee-quiet-and-a-cedar-hollow-morning-2026-08-05.jpg`
**Scheduled:** 2026-08-05 23:00 UTC  (18:00 CDT)
**Overlay text:** Coffee, Quiet, and a Cedar Hollow Morning

**Prompt**
2:3 vertical extreme close-up, 1000 × 1500 px. A chipped rust-orange mug of coffee cools on a cedar porch railing; a steam thread, cream cardigan cuff, and gold band on the hand holding it tell Dana’s story. No identifiable face or person. Soft early sunlight from behind left traces the mug rim and oak leaves; a work truck is a faded-denim blur beyond a red-clay drive at f/2.8. Use 35mm Kodak Portra 400 fine grain, gentle halation, lifted blacks, honey cedar, and dusty sage foliage. Make the mug the single off-centre left subject and reserve a quiet, low-detail bottom third for Canva overlay, with no text in image.

**Avoid**
Latte art, café branding, visible faces, excessive steam, polished lifestyle props, floating dust, lens flare, teal-orange grading, waxy skin, HDR, mountain scenery, wedding glow, or stock staging.

### Pin 10 — Oklahoma slow
**Save as:** `brands/grissom/assets/hh-pin-aug5-batch-pin5-oklahoma-slow-2026-08-05.jpg`
**Scheduled:** 2026-08-06 02:00 UTC  (21:00 CDT)
**Overlay text:** Oklahoma Slow, Love Takes Time

**Prompt**
2:3 vertical landscape photograph, 1000 × 1500 px. From the far end of a broad cedar porch, look across a farm pond toward rolling eastern Oklahoma hills, blackjack oak, hickory, red-clay track, and wide pale summer sky; an empty cream mug anchors the foreground. No identifiable faces or people. Soft overcast morning light keeps the pond matte, foliage dusty sage, and a faded-denim porch chair subdued. Shoot at f/4 on 35mm Kodak Portra 400 with fine grain, lifted blacks, and warm cedar-and-honey neutrals. Make the mug the single off-centre lower-right subject; leave a quiet, low-detail top third of open sky for Canva overlay, with no text in image.

**Avoid**
Mountains, blue ridges, lake-resort scenery, misty peaks, spectacular sunset, people, readable signs, floating dust, lens flare, teal-orange grading, HDR, wedding glow, or stock staging.

### Pin 11 — Tropes, made tangible
**Save as:** `brands/grissom/assets/hh-pin-aug6-batch-pin1-all-the-tropes-in-handy-hearts-2026-08-06.jpg`
**Scheduled:** 2026-08-06 14:00 UTC  (09:00 CDT)
**Overlay text:** Every Slow Burn Trope You Love

**Prompt**
2:3 vertical overhead still life, 1000 × 1500 px. On a worn cedar worktable, place a hammer, tape measure, Dana’s plain gold band on a cream glove, two separated coffee mugs, and a blank cream notebook with no writing; together they suggest contractor hero, widow heroine, forced proximity, and slow burn. No identifiable face or person. Soft window light enters from upper left at f/4, giving short natural shadows. Use 35mm Kodak Portra 400 grain, lifted blacks, warm cedar-and-honey, dusty sage pencil, faded-denim mug, and rust-orange hardware. Make the hammer the single off-centre lower-left anchor and keep a quiet, low-detail top third for Canva overlay; no text in image.

**Avoid**
Lettered notebook pages, trope labels, romance-novel clichés, scattered clutter, extra rings, floating dust, lens flare, teal-orange grading, plastic skin, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 12 — Author desk
**Save as:** `brands/grissom/assets/hh-pin-aug6-batch-pin2-dk-grissom-2026-08-06.jpg`
**Scheduled:** 2026-08-06 17:00 UTC  (12:00 CDT)
**Overlay text:** D.K. Grissom’s Small-Town Romance Aesthetic

**Prompt**
2:3 vertical writer’s-desk detail, 1000 × 1500 px. Chipped rust-orange mug, phone face-down with a wired earbud, sharpened pencil, and blank cream notebook sit on a cedar desk by an open truck window; red clay and eastern Oklahoma oak leaves appear beyond. No identifiable face or person, only a cropped faded-denim sleeve at the edge. Late-afternoon light from right catches ceramic glaze and paper at f/3.2. Photograph in 35mm Kodak Portra 400 with fine grain, gentle halation, lifted blacks, cedar-and-honey tones, and dusty sage notebook ribbon. Make the mug the single off-centre lower-right subject; reserve a quiet, low-detail top third for Canva overlay, with no text in image.

**Avoid**
Legible notes, laptop screens, desk neon, generic office decor, branded phone UI, floating dust, lens flare, teal-orange grading, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 13 — Unsaid things
**Save as:** `brands/grissom/assets/hh-pin-aug6-batch-pin3-a-romance-with-no-stupid-miscommunicatio-2026-08-06.jpg`
**Scheduled:** 2026-08-06 20:00 UTC  (15:00 CDT)
**Overlay text:** A Romance With No Stupid Miscommunication

**Prompt**
2:3 vertical close crop at a farmhouse doorway, 1000 × 1500 px. Don’s calloused hand in a worn canvas work jacket rests on a cedar doorframe inches from Dana’s ringed hand holding a chipped mug; their hands do not touch. No identifiable faces, heads, or bodies. Soft overcast daylight reveals peeling dusty sage trim, red-clay threshold dust, and a hint of eastern Oklahoma oak at f/2.8. Use 35mm Kodak Portra 400 fine grain, lifted blacks, warm cedar-and-honey, faded-denim, and cream accents. Make the space between hands the single off-centre lower-left subject; leave a quiet, low-detail top third of doorway shadow for Canva overlay, with no text in image.

**Avoid**
Hands touching, embrace, engagement ring, doorway kiss, glossy skin, floating dust, lens flare, teal-orange grading, HDR, mountain background, wedding glow, stock staging, or faces.

### Pin 14 — Repair work
**Save as:** `brands/grissom/assets/hh-pin-aug6-batch-pin4-heroes-who-fix-things-with-their-hands-2026-08-06.jpg`
**Scheduled:** 2026-08-06 23:00 UTC  (18:00 CDT)
**Overlay text:** Heroes Who Fix Things With Hands

**Prompt**
2:3 vertical action detail, 1000 × 1500 px. Crop on Don’s calloused, dirty hands guiding a hand plane along one weathered cedar porch board; pale curled shavings collect beside a square and leather boot. Show no identifiable face, only a cropped canvas-jacket torso and faded denim. Low golden-hour light from right reveals wood grain and red clay, while oak-and-hickory cross-timbers soften at f/3.5. Use 35mm Kodak Portra 400 fine grain, slight halation, lifted blacks, cedar-and-honey warmth, and dusty sage trim. Make the plane and hands the single off-centre right subject; retain a quiet, low-detail bottom third of shaded porch floor for Canva overlay, with no text in image.

**Avoid**
Power tools, spotless hands, splinters in skin, safety signage, posed labor-model styling, floating dust, lens flare, teal-orange grading, waxy skin, HDR, mountains, wedding glow, or faces.

### Pin 15 — The almost touch
**Save as:** `brands/grissom/assets/hh-pin-aug6-batch-pin5-slow-burn-that-actually-pays-off-2026-08-06.jpg`
**Scheduled:** 2026-08-07 02:00 UTC  (21:00 CDT)
**Overlay text:** A Slow Burn That Pays Off

**Prompt**
2:3 vertical medium detail, 1000 × 1500 px. On a porch step, Dana’s ringed hand and Don’s calloused hand reach toward a steel thermos, separated by one inch; make the pause between fingertips the subject. No identifiable faces or people beyond cropped cream cardigan, worn canvas sleeve, and faded-denim knees. Late-afternoon light from left reflects softly on thermos and cedar; red clay and oak-hickory foliage remain legible at f/2.8. Render on 35mm Kodak Portra 400 with fine grain, lifted blacks, warm cedar-and-honey, dusty sage trim, and faded-denim accent. Keep the hands off-centre lower right and reserve a quiet, low-detail top third for Canva overlay; no text in image.

**Avoid**
Touching hands, kiss, dramatic romance pose, diamond jewelry, excessive bokeh, floating dust, lens flare, teal-orange grading, plastic skin, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 16 — Cover reveal
**Save as:** `brands/grissom/assets/hh-pin-preorder-batch-pin1-cover-reveal-handy-hearts-by-dk-grissom-2026-08-07.jpg`
**Scheduled:** 2026-08-07 14:00 UTC  (09:00 CDT)
**Overlay text:** Cover Reveal For Handy Hearts

**Prompt**
2:3 vertical book-object photograph, 1000 × 1500 px. An unlettered cream hardback sits on a cedar porch table, its cover carrying an embossed cedar-board texture and gold ring motif, with no readable text. No identifiable face or person; a cropped calloused hand in canvas steadies it from behind. Golden-hour light from left makes the embossing tactile; dusty sage leaves, red-clay drive, and eastern Oklahoma oak woodland soften at f/3.5. Use 35mm Kodak Portra 400 fine grain, lifted blacks, warm cedar-and-honey, and faded-denim shadow. Make the book the single off-centre right subject, leaving a quiet, low-detail top third of pale sky for Canva overlay; no text in image.

**Avoid**
Generated title lettering, visible author name, ornate fantasy cover art, stacked books, bookstore shelf, floating dust, lens flare, teal-orange grading, waxy skin, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 17 — Preorder announcement
**Save as:** `brands/grissom/assets/hh-pin-preorder-batch-pin2-preorder-handy-hearts-out-september-8-20-2026-08-07.jpg`
**Scheduled:** 2026-08-07 17:00 UTC  (12:00 CDT)
**Overlay text:** Preorder Handy Hearts Out September 8

**Prompt**
2:3 vertical tabletop arrangement, 1000 × 1500 px. An unlettered cream paperback tied with twine and a dusty sage wildflower stem rests beside Don’s steel thermos on a cedar packing table; a blank kraft mailer lies behind with no labels. No identifiable face or person, only a cropped cream-cardigan hand adjusting twine. Soft overcast window light from left reveals paper fibers and scuffed metal at f/3.5. Shoot in 35mm Kodak Portra 400 with fine grain, lifted blacks, honey wood, faded-denim shadow, and a rust-orange sealing-wax accent. Make the book the single off-centre lower-left subject; reserve a quiet, low-detail top third for Canva overlay, with no text in image.

**Avoid**
Readable cover copy, shipping labels, QR codes, online-store screens, gift-bow excess, floating dust, lens flare, teal-orange grading, plastic skin, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 18 — Why preorders matter
**Save as:** `brands/grissom/assets/hh-pin-preorder-batch-pin3-why-you-should-preorder-handy-hearts-now-2026-08-07.jpg`
**Scheduled:** 2026-08-07 20:00 UTC  (15:00 CDT)
**Overlay text:** Why Preorder Handy Hearts Now

**Prompt**
2:3 vertical bookstore counter detail, 1000 × 1500 px. A bookseller’s unidentifiable hand places one unlettered cream paperback onto a short aligned stack; worn cedar counter, coppery bookend, and dusty sage sprig frame the book. No identifiable faces or bodies; show no covers, labels, or signage. Natural morning light from a front window crosses a low-brick Cedar Hollow Main Street, softly visible at f/4. Render in 35mm Kodak Portra 400 with fine grain, gentle halation, lifted blacks, warm cedar-and-honey, faded-denim window shadow, and rust-orange metal. Make the stack the single off-centre right subject; leave a quiet, low-detail bottom third of counter for Canva overlay, with no text in image.

**Avoid**
Readable book covers, store logos, cash registers, crowds, pointing hands, floating dust, lens flare, teal-orange grading, waxy skin, HDR, mountains, wedding glow, stock staging, or faces.

### Pin 19 — Don and Dana
**Save as:** `brands/grissom/assets/hh-pin-preorder-batch-pin4-meet-don-and-dana-before-september-8-2026-08-07.jpg`
**Scheduled:** 2026-08-07 23:00 UTC  (18:00 CDT)
**Overlay text:** Meet Don and Dana First

**Prompt**
2:3 vertical two-character object detail, 1000 × 1500 px. Dana’s ringed hand in a cream cardigan rests beside Don’s calloused hand in a canvas sleeve on cedar; they do not touch. No identifiable faces, heads, or bodies. Golden-hour light from right warms ring and wood; eastern Oklahoma oak-and-hickory leaves and red-clay drive soften at f/2.8. Use 35mm Kodak Portra 400 fine grain, lifted blacks, dusty sage trim, faded-denim sleeve shadow, and a rust-orange mug at the edge. Make the paired hands the single off-centre left subject and reserve a quiet, low-detail top third for Canva overlay; no text in image.

**Avoid**
Face-on couple portrait, touching or entwined hands, diamond ring, engagement pose, glamorous sunset, floating dust, lens flare, teal-orange grading, plastic skin, HDR, mountains, wedding glow, or stock staging.

### Pin 20 — Grief, not a fix
**Save as:** `brands/grissom/assets/hh-pin-preorder-batch-pin5-grief-does-not-end-it-changes-shape-2026-08-07.jpg`
**Scheduled:** 2026-08-08 02:00 UTC  (21:00 CDT)
**Overlay text:** Grief Does Not End, It Changes Shape

**Prompt**
2:3 vertical quiet exterior still life, 1000 × 1500 px. An empty cedar rocking chair faces an eastern Oklahoma yard after rain; Dana’s cream cardigan drapes over one arm, with a plain gold ring catching a pool of soft light on the rail. No identifiable face or person. Overcast light from left leaves red clay dark, dusty sage grass muted, and oak and hickory trunks readable at f/4; no mountains. Use 35mm Kodak Portra 400 grain, lifted blacks, warm cedar-and-honey, faded-denim shadows, and halation. Make the chair the single off-centre right subject; leave a quiet, low-detail bottom third of porch boards for Canva overlay, with no text in image.

**Avoid**
Funeral props, abandoned-house horror, visible photograph, rainstorm drama, extra chairs, floating dust, lens flare, teal-orange grading, HDR, Appalachian peaks, wedding glow, stock staging, or faces.

### Pin 21 — Cedar Hollow morning
**Save as:** `brands/grissom/assets/hh-pin-aug8-batch-pin1-cedar-hollow-morning-2026-08-08.jpg`
**Scheduled:** 2026-08-08 14:00 UTC  (09:00 CDT)
**Overlay text:** A Morning in Cedar Hollow

**Prompt**
2:3 vertical exterior wide, 1000 × 1500 px. From a porch railing, frame coffee cooling, a gravel county road and distant work truck, then rolling oak-and-hickory cross-timbers under a broad pale morning sky.No identifiable faces or people. Cool overcast light warms cedar; red clay, dusty sage pasture, and faded-denim truck balance scene. Photograph at f/4 on 35mm Kodak Portra 400 with fine grain and lifted blacks. Make the mug the single off-centre lower-left subject; reserve a quiet, low-detail top third of sky for Canva overlay, with no text in image.
**Avoid**
Appalachian ridges, dramatic fog, lake scenery, visible driver, road signs, oversized steam, floating dust, lens flare, teal-orange grading, HDR, wedding glow, stock staging, or faces, misty mountain peaks, blue-ridge silhouettes.
### Pin 22 — Nancy’s diner
**Save as:** `brands/grissom/assets/hh-pin-aug8-batch-pin2-small-town-diner-2026-08-08.jpg`
**Scheduled:** 2026-08-08 17:00 UTC  (12:00 CDT)
**Overlay text:** Inside Cedar Hollow’s Small-Town Diner

**Prompt**
2:3 vertical diner-booth interior, 1000 × 1500 px. At the Hollow Bean Café, a slice of pie on a chipped cream plate sits on a cedar booth table; A cardigan-sleeved hand withdraws, implying care. No identifiable face or person. Morning window light catches pie crust, china, and faded-denim booth upholstery; low-brick Cedar Hollow storefronts blur outside at f/3.5. Use 35mm Kodak Portra 400 fine grain, lifted blacks, warm honey wood, dusty sage window trim, and a rust-orange sugar packet with no lettering. Make the plate the single off-centre lower-right subject and leave a quiet, low-detail top third for Canva overlay; no text in image.

**Avoid**
Readable menus, chain-diner logos, neon, crowded tables, food-advertising gloss, floating dust, lens flare, teal-orange grading, waxy skin, HDR, mountains, wedding glow, stock staging, or faces.

## Batch 1 summary

| Pin number | Filename | Shot type | Quiet zone |
|---|---|---|---|
| 01 | hh-pin-aug4-batch-pin1-she-still-wears-her-wedding-ring-2026-08-04.jpg | extreme close-up | top |
| 02 | hh-pin-aug4-batch-pin2-the-porch-that-started-everything-2026-08-04.jpg | exterior repair detail | bottom |
| 03 | hh-pin-aug4-batch-pin3-he-fixes-things-with-his-hands-because-w-2026-08-04.jpg | toolbox still life | top |
| 04 | hh-pin-aug4-batch-pin4-grief-does-not-end-it-changes-shape-2026-08-04.jpg | interior ring still life | top |
| 05 | hh-pin-aug4-batch-pin5-small-town-old-porch-slow-burn-2026-08-04.jpg | exterior wide | top |
| 06 | hh-pin-aug5-batch-pin1-the-cedar-hollow-diner-where-every-story-2026-08-05.jpg | diner counter | top |
| 07 | hh-pin-aug5-batch-pin2-in-cedar-hollow-you-cannot-keep-a-secret-2026-08-05.jpg | porch delivery detail | bottom |
| 08 | hh-pin-aug5-batch-pin3-small-towns-do-not-let-you-hide-2026-08-05.jpg | truck interior view | top |
| 09 | hh-pin-aug5-batch-pin4-coffee-quiet-and-a-cedar-hollow-morning-2026-08-05.jpg | mug extreme close-up | bottom |
| 10 | hh-pin-aug5-batch-pin5-oklahoma-slow-2026-08-05.jpg | landscape wide | top |
| 11 | hh-pin-aug6-batch-pin1-all-the-tropes-in-handy-hearts-2026-08-06.jpg | overhead still life | top |
| 12 | hh-pin-aug6-batch-pin2-dk-grissom-2026-08-06.jpg | writer’s-desk detail | top |
| 13 | hh-pin-aug6-batch-pin3-a-romance-with-no-stupid-miscommunicatio-2026-08-06.jpg | doorway close crop | top |
| 14 | hh-pin-aug6-batch-pin4-heroes-who-fix-things-with-their-hands-2026-08-06.jpg | repair action detail | bottom |
| 15 | hh-pin-aug6-batch-pin5-slow-burn-that-actually-pays-off-2026-08-06.jpg | almost-touch detail | top |
| 16 | hh-pin-preorder-batch-pin1-cover-reveal-handy-hearts-by-dk-grissom-2026-08-07.jpg | book-object photograph | top |
| 17 | hh-pin-preorder-batch-pin2-preorder-handy-hearts-out-september-8-20-2026-08-07.jpg | preorder tabletop | top |
| 18 | hh-pin-preorder-batch-pin3-why-you-should-preorder-handy-hearts-now-2026-08-07.jpg | bookstore counter detail | bottom |
| 19 | hh-pin-preorder-batch-pin4-meet-don-and-dana-before-september-8-2026-08-07.jpg | paired-hand detail | top |
| 20 | hh-pin-preorder-batch-pin5-grief-does-not-end-it-changes-shape-2026-08-07.jpg | exterior grief still life | bottom |
| 21 | hh-pin-aug8-batch-pin1-cedar-hollow-morning-2026-08-08.jpg | porch landscape wide | top |
| 22 | hh-pin-aug8-batch-pin2-small-town-diner-2026-08-08.jpg | diner booth interior | top |

---

## Batch 2 — pins 23–44

### Pin 23 — Storm porch
**Save as:** `brands/grissom/assets/hh-pin-aug8-batch-pin3-old-porch-summer-storm-chapter-3-2026-08-08.jpg`
**Scheduled:** 2026-08-08 20:00 UTC  (15:00 CDT)
**Overlay text:** Old Porch. Summer Storm. Chapter 3.

**Prompt**
2:3 vertical exterior wide photograph of a weathered cedar back porch after a summer storm: part of the railing and floor has collapsed, rain darkens the boards, and a tipped cream mug lies near one displaced chair. Oak and hickory woodland, red clay, rolling eastern Oklahoma hills, and broad gray sky stay legible beyond. Soft overcast side light; 35mm Kodak Portra 400 grain, f/4, cedar-honey with dusty sage foliage. Make the broken porch one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
intact or pristine porch, dramatic tornado scene, people posed romantically, Appalachian ridges, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 24 — Working hands
**Save as:** `brands/grissom/assets/hh-pin-aug8-batch-pin4-heroes-who-work-with-their-hands-2026-08-08.jpg`
**Scheduled:** 2026-08-08 23:00 UTC  (18:00 CDT)
**Overlay text:** Heroes Who Work with Their Hands

**Prompt**
2:3 vertical extreme close-up of a handyman’s calloused, lightly sawdust-marked hands measuring a cedar board with an old brass tape measure on a porch workbench. A steel thermos and folded faded-denim canvas jacket blur behind; show no face. Golden-hour light enters from frame left, catching rough grain and honey-colored shavings; eastern Oklahoma oak leaves remain softly legible. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with faded denim accent. Make the hands one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
spotless manicure, power-tool advertisement look, extra hands, readable measuring labels, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 25 — Golden-hour repair
**Save as:** `brands/grissom/assets/hh-pin-aug8-batch-pin5-golden-hour-in-cedar-hollow-2026-08-08.jpg`
**Scheduled:** 2026-08-09 02:00 UTC  (21:00 CDT)
**Overlay text:** Golden Hour in Cedar Hollow

**Prompt**
2:3 vertical exterior wide photograph toward a partially rebuilt farmhouse porch in late afternoon: cedar sawhorse and closed toolbox sit off-centre, with a cold chipped coffee mug on the step. Fresh sawdust rests at the red-clay edge; oak, hickory, cross-timbers, rolling eastern Oklahoma hills, and big sky remain legible. Low honey sunlight rakes across the wood from the right. 35mm Kodak Portra 400 grain, f/4, cedar-honey with dusty sage trim. Keep the sawhorse the single subject with generous negative space. Quiet bottom third for Canva overlay. No text or identifiable faces.
**Avoid**
two people kissing, finished luxury deck, sunset mountains, cluttered construction site, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 26 — Sunday reading nook
**Save as:** `brands/grissom/assets/hh-pin-aug9-sunday-pin1-sunday-reading-list-2026-08-09.jpg`
**Scheduled:** 2026-08-09 14:00 UTC  (09:00 CDT)
**Overlay text:** Sunday Reading List Small-Town Romance

**Prompt**
2:3 vertical interior still life of a worn cream armchair beside a farmhouse window, holding a closed unmarked paperback, chipped rust-orange mug, and unbleached-linen throw. Soft Sunday overcast light passes through cream curtains from left; oak and hickory branches outside establish eastern Oklahoma. A faded-denim cushion and dusty sage window trim are restrained accents. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey palette. Make the chair one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
legible book cover, busy library shelves, fireplace glamour, mountain cabin view, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 27 — Coffee left behind
**Save as:** `brands/grissom/assets/hh-pin-aug9-sunday-pin2-the-quiet-before-the-feeling-2026-08-09.jpg`
**Scheduled:** 2026-08-09 17:00 UTC  (12:00 CDT)
**Overlay text:** The Quiet Before the Feeling

**Prompt**
2:3 vertical porch-detail photograph of one half-finished black coffee on a wide cedar railing beside a carpenter’s pencil and two clean screws, implying a handyman who just stepped away. Behind it, a soft-overcast eastern Oklahoma yard of red clay, oak trunks, and dusty sage foliage remains recognizable. Natural side light pools gently on the mug rim. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with faded denim shadow. Make the mug one off-centre subject with generous negative space. Quiet bottom third for Canva overlay. No text or identifiable faces.
**Avoid**
two matching mugs, love-note props, steam shaped like hearts, readable writing on tools, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 28 — Unhurried porch
**Save as:** `brands/grissom/assets/hh-pin-aug9-sunday-pin3-rest-day-in-cedar-hollow-2026-08-09.jpg`
**Scheduled:** 2026-08-09 20:00 UTC  (15:00 CDT)
**Overlay text:** Rest Day in Cedar Hollow

**Prompt**
2:3 vertical exterior wide shot of a quiet farmhouse porch on an Oklahoma Sunday; one empty weathered rocking chair sits off-centre beneath dusty sage trim. eastern Oklahoma pond, oak, red clay, sky beyond. No people: the chair’s worn cedar arms and creased cream cushion suggest recent use. Late-afternoon sunlight comes from behind the house, casting long honey-colored board shadows. 35mm Kodak Portra 400 grain, f/4, cedar-honey with faded denim sky. Keep the chair the single subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
swing set, mountain valley, porch packed with décor, people staring at camera, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 29 — Same square footage
**Save as:** `brands/grissom/assets/hh-pin-aug10-tropes-pin1-forced-proximity-done-right-2026-08-10.jpg`
**Scheduled:** 2026-08-10 14:00 UTC  (09:00 CDT)
**Overlay text:** Forced Proximity Done Right Handy Hearts

**Prompt**
2:3 vertical waist-level porch scene: a ringed hand in a cream cardigan offers one chipped coffee mug toward a handyman’s cropped faded-denim torso; place both at far right and show no faces. Cedar boards and an old toolbox establish repair. Soft overcast daylight crosses the red-clay eastern Oklahoma yard, oak, and hickory behind. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with dusty sage trim. Make the offered mug one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
face-to-face portrait, touching hands, kiss, construction-worker costume or hard hats, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 30 — Full person
**Save as:** `brands/grissom/assets/hh-pin-aug10-tropes-pin2-widow-heroines-in-romance-2026-08-10.jpg`
**Scheduled:** 2026-08-10 17:00 UTC  (12:00 CDT)
**Overlay text:** Widow Heroines in Romance TBR List

**Prompt**
2:3 vertical over-the-shoulder interior photograph of Dana alone at a cedar kitchen counter; honey-blonde hair is seen from behind; her cream sleeve aligns repair receipts. A plain gold wedding band, unwashed chipped mug, and dusty sage window trim make the room lived-in; no face is visible. Soft overcast light reveals oak branches outside in eastern Oklahoma. 35mm Kodak Portra 400 grain, f/4, cedar-honey with faded denim shadow. Make her hands one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
mourning veil, funeral props, glamorous widow pose, readable paperwork, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 31 — Everybody notices
**Save as:** `brands/grissom/assets/hh-pin-aug10-tropes-pin3-small-towns-that-mind-their-business-but-2026-08-10.jpg`
**Scheduled:** 2026-08-10 20:00 UTC  (15:00 CDT)
**Overlay text:** Small Towns That Mind Their Business

**Prompt**
2:3 vertical street-level exterior view from a low brick storefront window: an older pickup is the off-centre subject, parked by Dana’s farmhouse with a closed toolbox in its bed. Café reflections imply neighbors. Red-clay shoulders, oak, hickory, low storefronts, and broad eastern Oklahoma sky replace mountain scenery. Late-afternoon side light softens the brick and faded-denim truck shadow. 35mm Kodak Portra 400 grain, f/4, cedar-honey with dusty sage accent. Keep the truck the single subject with generous negative space. Quiet bottom third for Canva overlay. No text or identifiable faces.
**Avoid**
readable shop signs, gossipy faces in window, modern luxury pickup, city streetscape, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 32 — Built to hold
**Save as:** `brands/grissom/assets/hh-pin-aug10-tropes-pin4-ex-military-contractor-hero-2026-08-10.jpg`
**Scheduled:** 2026-08-10 23:00 UTC  (18:00 CDT)
**Overlay text:** Ex-Military Contractor Hero Handy Hearts Romance

**Prompt**
2:3 vertical low-angle detail shot of a sturdy cedar porch support being fastened by one pair of calloused hands using an old well-kept ratchet; scuffed leather boots and faded denim blur behind, with no face shown. The new joint is the subject, showing he makes things hold. Honey light from right catches the grain; red-clay eastern Oklahoma ground, oak, and hickory blur beyond. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with dusty sage accent. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
uniform, medals, combat scene, tactical gear, shiny new tools, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 33 — What to expect
**Save as:** `brands/grissom/assets/hh-pin-aug10-tropes-pin5-tropes-in-handy-hearts-2026-08-10.jpg`
**Scheduled:** 2026-08-11 02:00 UTC  (21:00 CDT)
**Overlay text:** Tropes in Handy Hearts What to Expect

**Prompt**
2:3 vertical tabletop still life on a weathered cedar porch: a folded carpenter’s tape measure, old hammer, plain gold ring on a cream napkin, and chipped coffee mug form one compact off-centre arrangement without labels. Cedar shavings, dusty sage leaves, and faded-denim canvas imply contractor, widow, and slow-burn tension through objects. Soft overcast light from upper left preserves texture; a blurred red-clay eastern Oklahoma yard with oak and hickory stays legible. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey palette. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
ring box or proposal styling, item grid, handwritten trope list, cluttered flat lay, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 34 — Porch light
**Save as:** `brands/grissom/assets/hh-pin-aug11-don-pin1-don-rourke-2026-08-11.jpg`
**Scheduled:** 2026-08-11 14:00 UTC  (09:00 CDT)
**Overlay text:** Don Rourke Blue Eyes Blond Going Silver

**Prompt**
2:3 vertical upward-looking exterior photograph of a man’s cropped back replacing an old farmhouse porch light; one arm is raised, with canvas jacket and silvering blond hair at the nape—never his face. Cedar siding and blurred eastern Oklahoma oak sit behind. Golden side light catches fixture and leather belt. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with dusty sage trim. Make the raised arm one off-centre subject with generous negative space. Quiet bottom third for Canva overlay. No text or identifiable faces.
**Avoid**
visible face or blue-eye close-up, heroic superhero pose, ornate lantern, ladder accident, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 35 — Sawdust schedule
**Save as:** `brands/grissom/assets/hh-pin-aug11-don-pin2-sawdust-and-silence-2026-08-11.jpg`
**Scheduled:** 2026-08-11 17:00 UTC  (12:00 CDT)
**Overlay text:** Sawdust and Silence Don Rourke Handy Hearts

**Prompt**
2:3 vertical macro texture photograph of honey-colored sawdust settled in weathered cedar workbench grooves, with the corner of a folded faded-denim canvas jacket and one old hand plane entering at lower right. No person is present; precise quiet work is the single subject. Soft overcast daylight slides from left across the shavings, while an oak-and-hickory eastern Oklahoma yard remains legible beyond the bench edge. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with dusty sage flecks. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
airborne sawdust, glossy workshop, tool-brand labels, abstract blur that hides the setting, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 36 — Toolbox, no small talk
**Save as:** `brands/grissom/assets/hh-pin-aug11-don-pin3-a-man-with-a-toolbox-and-no-small-talk-2026-08-11.jpg`
**Scheduled:** 2026-08-11 20:00 UTC  (15:00 CDT)
**Overlay text:** Toolbox and No Small Talk

**Prompt**
2:3 vertical still life at a farmhouse porch edge: an open old metal toolbox, tools cleaned and deliberately ordered, sits off-centre beside plain black coffee in a chipped mug. Its closed lid casts a faded-denim-blue shadow over cedar boards; dusty sage paint peels from the porch post. Late-afternoon light from left shows red-clay soil, oak, and hickory in eastern Oklahoma behind. 35mm Kodak Portra 400 grain, f/4, cedar-honey palette. Keep the toolbox the single subject with generous negative space. Quiet bottom third for Canva overlay. No text or identifiable faces.
**Avoid**
brand labels, overflowing tools, rustic craft flat-lay styling, coffee-shop scene, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 37 — Twenty years building
**Save as:** `brands/grissom/assets/hh-pin-aug11-don-pin4-navy-seabee-hero-2026-08-11.jpg`
**Scheduled:** 2026-08-11 23:00 UTC  (18:00 CDT)
**Overlay text:** Navy Seabee Hero Handy Hearts D.K.

**Prompt**
2:3 vertical exterior medium shot from behind of a solitary handyman carrying two cedar boards toward an aging eastern Oklahoma farmhouse. Canvas jacket and scuffed boots show; no identifiable face is visible. Thermos and toolbox in hand make work the focus. Red clay, sandstone, oak and hickory woodland, rolling hills, and open pale sky establish Cedar Hollow. Soft overcast light models rough grain. 35mm Kodak Portra 400 grain, f/4, cedar-honey with dusty sage accent. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
uniform or insignia, combat imagery, patriotic flag display, face-forward action pose, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 38 — He shows up
**Save as:** `brands/grissom/assets/hh-pin-aug11-don-pin5-the-quiet-heroes-are-the-best-ones-2026-08-11.jpg`
**Scheduled:** 2026-08-12 02:00 UTC  (21:00 CDT)
**Overlay text:** Quiet Heroes Are the Best Ones

**Prompt**
2:3 vertical roadside exterior shot at golden hour: a faded-denim pickup carrying cedar waits off-centre on a gravel road before a farmhouse. No person; the truck’s arrival tells the story. Red clay, oak, pond, and eastern Oklahoma sky set the place. Honey light comes from behind the truck and glances across lumber edges without flare. 35mm Kodak Portra 400 grain, f/4, cedar-honey with dusty sage vegetation. Keep the truck the single subject with generous negative space. Quiet bottom third for Canva overlay. No text or identifiable faces.
**Avoid**
new luxury truck, highway traffic, visible logo, mountain road, heroic action scene, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 39 — Ring stays on
**Save as:** `brands/grissom/assets/hh-pin-aug12-dana-pin1-she-still-wears-her-ring-2026-08-12.jpg`
**Scheduled:** 2026-08-12 14:00 UTC  (09:00 CDT)
**Overlay text:** She Still Wears Her Ring

**Prompt**
2:3 vertical extreme close-up of a woman’s left hand, plain gold wedding band visible, wrapped around a chipped cream coffee mug on a weathered cedar porch rail. Cream cuff and honey-blonde hair edge the frame; no face. Overcast light catches gold and glaze; eastern Oklahoma oak blurs behind. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with dusty sage foliage. Make the hand one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
engagement-ring sparkle, ring box, hand model manicure, face in background, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 40 — Coffee that could strip paint
**Save as:** `brands/grissom/assets/hh-pin-aug12-dana-pin2-honey-blonde-green-eyes-freckles-2026-08-12.jpg`
**Scheduled:** 2026-08-12 17:00 UTC  (12:00 CDT)
**Overlay text:** Honey-Blonde Green Eyes Freckles Dana Whitfield

**Prompt**
2:3 vertical interior medium shot of Dana from shoulders down and behind: honey-blonde hair catches light, a cream-cardigan sleeve holds a chipped rust-orange mug of very dark coffee, and a plain gold band is visible. No face. Midday overcast light through a dusty sage-trimmed window falls from right; eastern Oklahoma oak and hickory appear outside. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with faded denim shadow. Make the mug one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
visible face, fashion portrait, latte art, white showroom kitchen, perfect hair, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 41 — Grief has room
**Save as:** `brands/grissom/assets/hh-pin-aug12-dana-pin3-grief-in-romance-done-right-2026-08-12.jpg`
**Scheduled:** 2026-08-12 20:00 UTC  (15:00 CDT)
**Overlay text:** Grief in Romance Done Right Handy Hearts

**Prompt**
2:3 vertical quiet interior wide shot of a lived-in farmhouse bedroom: one cream cardigan drapes over a wooden chair beside a neatly made bed, and a chipped mug rests on the sill. No people, props, or photographs; the chair is the subject. Overcast window light reveals cedar and linen; eastern Oklahoma oak sits outside. 35mm Kodak Portra 400 grain, f/4, cedar-honey with dusty sage curtain tie and faded denim shadow. Position the chair low and right with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
funeral shrine, black clothing, dramatic crying figure, sterile minimalist bedroom, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 42 — Lumber joke
**Save as:** `brands/grissom/assets/hh-pin-aug12-dana-pin4-a-heroine-who-makes-bad-lumber-puns-2026-08-12.jpg`
**Scheduled:** 2026-08-12 23:00 UTC  (18:00 CDT)
**Overlay text:** A Heroine Who Makes Bad Lumber Puns

**Prompt**
2:3 vertical waist-level porch photograph of a cream-cardigan torso and hands holding a short cedar offcut like a microphone, caught just after a joke; crop the head out completely. Tape measure, chipped mug, and fresh boards sit behind. Honey sunlight catches grain and wedding band; eastern Oklahoma oak sits beyond. 35mm Kodak Portra 400 grain, f/2.8, cedar-honey with faded denim accent. Make the offcut one off-centre subject with generous negative space. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
speech bubbles, literal written pun, laugh-face portrait, novelty comedy props, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 43 — On her own schedule
**Save as:** `brands/grissom/assets/hh-pin-aug12-dana-pin5-green-eyes-and-quiet-strength-2026-08-12.jpg`
**Scheduled:** 2026-08-13 02:00 UTC  (21:00 CDT)
**Overlay text:** Green Eyes and Quiet Strength Dana

**Prompt**
2:3 vertical exterior detail photograph of garden clogs on red clay beside a step ladder and dusty sage watering can, with one ringed hand steadying the ladder at frame edge; no face is shown. The practical ladder placed beside the farmhouse porch is the single subject, not a rescue scene. Soft early-evening overcast light from left shows worn cedar siding, oak and hickory woodland, and rolling eastern Oklahoma hills. 35mm Kodak Portra 400 grain, f/4, cedar-honey with faded denim shadow. Quiet top third for Canva overlay. No text or identifiable faces.
**Avoid**
man rescuing her, fashion boots, posed garden glamour, mountain landscape, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

### Pin 44 — First sight of the porch
**Save as:** `brands/grissom/assets/hh-pin-aug13-firstline-arc-pin1-first-line-of-handy-hearts-2026-08-13.jpg`
**Scheduled:** 2026-08-13 14:00 UTC  (09:00 CDT)
**Overlay text:** First Line of Handy Hearts D.K. Grissom

**Prompt**
2:3 vertical exterior establishing photograph of Dana’s visibly failing back porch: bowed cedar steps, loose railing, sagging floorboards, and a weathered cream curtain moving inside the dark doorway. Keep the porch as the single off-centre subject; no people or faces. Side light reveals worn boards; red clay, oak, and broad eastern Oklahoma sky sit beyond. 35mm Kodak Portra 400 grain, f/4, cedar-honey with dusty sage trim and faded denim sky. Give the porch generous negative space. Quiet bottom third for Canva overlay. No text or identifiable faces.
**Avoid**
perfect renovated porch, storm catastrophe, people on the steps, Appalachian scenery

## Batch 2 summary

| Pin number | Filename | Shot type | Quiet zone |
|---:|---|---|---|
| 23 | `hh-pin-aug8-batch-pin3-old-porch-summer-storm-chapter-3-2026-08-08.jpg` | exterior wide | top |
| 24 | `hh-pin-aug8-batch-pin4-heroes-who-work-with-their-hands-2026-08-08.jpg` | extreme close-up | top |
| 25 | `hh-pin-aug8-batch-pin5-golden-hour-in-cedar-hollow-2026-08-08.jpg` | exterior wide | bottom |
| 26 | `hh-pin-aug9-sunday-pin1-sunday-reading-list-2026-08-09.jpg` | interior still life | top |
| 27 | `hh-pin-aug9-sunday-pin2-the-quiet-before-the-feeling-2026-08-09.jpg` | porch detail | bottom |
| 28 | `hh-pin-aug9-sunday-pin3-rest-day-in-cedar-hollow-2026-08-09.jpg` | exterior wide | top |
| 29 | `hh-pin-aug10-tropes-pin1-forced-proximity-done-right-2026-08-10.jpg` | waist-level medium | top |
| 30 | `hh-pin-aug10-tropes-pin2-widow-heroines-in-romance-2026-08-10.jpg` | over-the-shoulder interior | top |
| 31 | `hh-pin-aug10-tropes-pin3-small-towns-that-mind-their-business-but-2026-08-10.jpg` | street-level exterior | bottom |
| 32 | `hh-pin-aug10-tropes-pin4-ex-military-contractor-hero-2026-08-10.jpg` | low-angle detail | top |
| 33 | `hh-pin-aug10-tropes-pin5-tropes-in-handy-hearts-2026-08-10.jpg` | tabletop still life | top |
| 34 | `hh-pin-aug11-don-pin1-don-rourke-2026-08-11.jpg` | upward-looking exterior | bottom |
| 35 | `hh-pin-aug11-don-pin2-sawdust-and-silence-2026-08-11.jpg` | macro texture | top |
| 36 | `hh-pin-aug11-don-pin3-a-man-with-a-toolbox-and-no-small-talk-2026-08-11.jpg` | porch still life | bottom |
| 37 | `hh-pin-aug11-don-pin4-navy-seabee-hero-2026-08-11.jpg` | exterior medium | top |
| 38 | `hh-pin-aug11-don-pin5-the-quiet-heroes-are-the-best-ones-2026-08-11.jpg` | roadside exterior | bottom |
| 39 | `hh-pin-aug12-dana-pin1-she-still-wears-her-ring-2026-08-12.jpg` | extreme close-up | top |
| 40 | `hh-pin-aug12-dana-pin2-honey-blonde-green-eyes-freckles-2026-08-12.jpg` | cropped interior medium | top |
| 41 | `hh-pin-aug12-dana-pin3-grief-in-romance-done-right-2026-08-12.jpg` | interior wide | top |
| 42 | `hh-pin-aug12-dana-pin4-a-heroine-who-makes-bad-lumber-puns-2026-08-12.jpg` | waist-level porch | top |
| 43 | `hh-pin-aug12-dana-pin5-green-eyes-and-quiet-strength-2026-08-12.jpg` | exterior detail | top |
| 44 | `hh-pin-aug13-firstline-arc-pin1-first-line-of-handy-hearts-2026-08-13.jpg` | exterior establishing | bottom |, dust, flare, teal-orange grade, plastic skin, pseudo-text, HDR, Appalachian mountains, wedding glow, stock staging, eye contact.

---

## Batch 3 — pins 45–66

### Pin 45 — ARC readers wanted
**Save as:** `brands/grissom/assets/hh-pin-aug13-firstline-arc-pin2-arc-readers-wanted-2026-08-13.jpg`
**Scheduled:** 2026-08-13 17:00 UTC  (12:00 CDT)
**Overlay text:** ARC Readers Wanted: Handy Hearts

**Prompt**
2:3 vertical photograph, a clean top-down ARC application still life on a weathered cedar table: one unmarked cream manuscript packet, a blank reply card, a pencil, and a dented steel thermos, arranged with the packet off-centre in the lower right. No text, logos, or readable writing anywhere. Reserve a quiet, low-detail top third of softly lit cedar for the Canva overlay. Soft overcast window light, 35mm film with Kodak Portra 400 fine grain and gentle lifted blacks, f/4. Warm cedar-and-honey palette with a single dusty sage paperclip; no people or identifiable faces.

**Avoid**
Illegible lettering on papers, busy desk clutter, stock-library flat-lay staging, floating dust, lens flare, teal-and-orange grading.

### Pin 46 — Before launch day
**Save as:** `brands/grissom/assets/hh-pin-aug13-firstline-arc-pin3-get-handy-hearts-before-launch-day-2026-08-13.jpg`
**Scheduled:** 2026-08-13 20:00 UTC  (15:00 CDT)
**Overlay text:** Get Handy Hearts Before Launch Day

**Prompt**
2:3 vertical photograph of a single unbranded cream advance-reading copy standing upright in an open weathered cedar mailbox, off-centre in the upper left; its cover is completely blank with no text. A gravel county drive, red clay verge, blackjack oak, and wide eastern Oklahoma sky recede softly behind it. Keep the softly focused, uncluttered gravel drive in the bottom third as the quiet Canva-overlay zone. Use natural honey-gold side light, 35mm Kodak Portra 400 grain, gentle halation, f/4, warm cedar-and-honey with faded denim mailbox-shadow accents. No people or identifiable faces.

**Avoid**
Readable book covers, suburban curbside mailboxes, Appalachian peaks, oversaturated HDR sky, staged product-ad lighting.

### Pin 47 — He stopped counting
**Save as:** `brands/grissom/assets/hh-pin-aug13-firstline-arc-pin4-he-stopped-counting-2026-08-13.jpg`
**Scheduled:** 2026-08-13 23:00 UTC  (18:00 CDT)
**Overlay text:** He Stopped Counting: Opening Lines

**Prompt**
2:3 vertical extreme close-up of a calloused man’s hand resting beside three old steel nails on a cedar porch board, the hand entering from the lower right and deliberately not showing a face. Put the nails and fingertips in crisp focus and leave the top third of porch grain plain and low-detail for the Canva overlay; no words, tally marks, or text. Natural golden-hour light rakes across the wood and catches a faint honey highlight. 35mm film, Kodak Portra 400 fine grain, lifted blacks, f/2.8; warm cedar-and-honey palette with a faded denim cuff at the edge.

**Avoid**
Extra fingers, shiny manicured hands, symbolic numbers or writing, lens flare, waxy skin, wedding-photography glow.

### Pin 48 — Be a first reader
**Save as:** `brands/grissom/assets/hh-pin-aug13-firstline-arc-pin5-be-a-first-reader-2026-08-13.jpg`
**Scheduled:** 2026-08-14 02:00 UTC  (21:00 CDT)
**Overlay text:** Be a First Reader: Handy Hearts

**Prompt**
2:3 vertical interior photograph of an empty cream cardigan draped over a wooden kitchen chair, with a single closed, completely unmarked paperback placed on its seat; the book is the off-centre subject in the upper right. A chipped rust-orange mug and a small dusty sage plant sit blurred behind, implying a first quiet reading morning. Leave the plain honey-lit wood floor across the bottom third low-detail for the Canva overlay; no visible or readable text. Soft overcast window light, 35mm Kodak Portra 400 grain, f/3.5, warm cedar-and-honey palette. No people or identifiable faces.

**Avoid**
Readable covers, an occupied chair with a face, cluttered cottage décor, plastic fabric texture, artificial studio light.

### Pin 49 — The porch scene
**Save as:** `brands/grissom/assets/hh-pin-aug14-porch-storm-pin1-the-porch-scene-2026-08-14.jpg`
**Scheduled:** 2026-08-14 14:00 UTC  (09:00 CDT)
**Overlay text:** The Porch Scene: Chapter Three

**Prompt**
2:3 vertical mid-action photograph from knee to shoulder only: a worn canvas work-jacketed man catches a woman in a cream cardigan by both forearms as one porch board tilts beneath her garden clog. Their faces remain completely outside the crop; show no identifiable faces. Place the catching moment off-centre in the lower right, with a low-detail rain-softened oak-and-hickory yard filling the top third for the Canva overlay; no text. Natural storm overcast light, damp cedar darkening under rain, 35mm Kodak Portra 400 grain, f/3.2; warm cedar-and-honey with faded denim and dusty sage accents, eastern Oklahoma red clay visible below.

**Avoid**
Face-on romance posing, dramatic falling body, mountain backdrop, glossy rain effects, lens flare, wedding-photo glow.

### Pin 50 — Rain on an Oklahoma porch
**Save as:** `brands/grissom/assets/hh-pin-aug14-porch-storm-pin2-rain-on-a-oklahoma-porch-2026-08-14.jpg`
**Scheduled:** 2026-08-14 17:00 UTC  (12:00 CDT)
**Overlay text:** Rain on an Oklahoma Porch

**Prompt**
2:3 vertical detail photograph of rainwater gathering in the shallow grooves of one weathered cedar porch rail, the rail running diagonally from lower right toward centre. Beyond it, a single dusty sage porch post and the soft, rain-blurred green of eastern Oklahoma oak woodland remain legible, not abstract. Hold the rain-darkened, plain cedar porch floor across the bottom third almost empty for the Canva overlay; no text and no people or identifiable faces. Use natural soft overcast light, 35mm Kodak Portra 400 grain, f/4, damp warm cedar-and-honey palette with faded denim-grey rain shadow.

**Avoid**
Raindrop freeze-frame spectacle, misty mountain ridges, heavy fog, excessive bokeh, teal colour cast, lens flare.

### Pin 51 — He catches her
**Save as:** `brands/grissom/assets/hh-pin-aug14-porch-storm-pin3-he-catches-her-2026-08-14.jpg`
**Scheduled:** 2026-08-14 20:00 UTC  (15:00 CDT)
**Overlay text:** He Catches Her: Slow Burn

**Prompt**
2:3 vertical high-angle close crop of two hands at the instant after a catch: a broad, calloused hand closes gently around a woman’s cream-cardigan sleeve just above her wrist, while her hand with a plain gold wedding band steadies against wet cedar. No faces or full bodies visible. Keep the hands off-centre in the lower left and reserve a bare, rain-darkened bottom third of porch boards for the Canva overlay; no text. Natural overcast summer-storm light, 35mm Kodak Portra 400 grain, f/2.8, warm cedar-and-honey wood with a faded denim cuff and dusty sage paint flecks.

**Avoid**
Extra hands or fingers, romantic hand modelling, shiny skin, visible faces, saturated storm drama, pseudo-texture lettering.

### Pin 52 — Neither says anything
**Save as:** `brands/grissom/assets/hh-pin-aug14-porch-storm-pin4-neither-of-them-says-anything-2026-08-14.jpg`
**Scheduled:** 2026-08-14 23:00 UTC  (18:00 CDT)
**Overlay text:** Neither of Them Says Anything

**Prompt**
2:3 vertical interior-facing porch photograph of two anonymous silhouettes seen only from behind, standing close but not touching in an open doorway after rain. Their heads and faces are turned away and softened by shallow focus; one cream cardigan and one faded denim work shirt identify the moment. Set them off-centre in the lower right. The quiet, low-detail cream interior wall fills the top third for the Canva overlay, with no text. Natural overcast daylight, wet cedar threshold, 35mm Kodak Portra 400 grain, f/3.5, warm honey shadows with a dusty sage doorframe.

**Avoid**
Face detail, embrace or kiss, melodramatic backlighting, foggy peaks, lens flare, glossy fashion-editorial styling.

### Pin 53 — Porch repair as romance
**Save as:** `brands/grissom/assets/hh-pin-aug14-porch-storm-pin5-porch-repair-as-romance-2026-08-14.jpg`
**Scheduled:** 2026-08-15 02:00 UTC  (21:00 CDT)
**Overlay text:** Porch Repair as Romance in Handy Hearts

**Prompt**
2:3 vertical workbench detail photograph of one carefully maintained vintage hand plane resting diagonally on a freshly cut cedar porch board, its curled wood shavings catching warm light. The tool is the single off-centre subject in the upper left; a faded denim work sleeve is just visible at the edge, with no face or person shown. Preserve a plain, low-detail stretch of cedar board across the bottom third for the Canva overlay and include no text. Natural late-afternoon side light, 35mm Kodak Portra 400 fine grain, f/2.8, honey wood, dusty sage paint chips, and soft lifted blacks.

**Avoid**
Modern power-tool showroom look, excessive sawdust in air, unreadable labels, hands with extra fingers, HDR orange-and-teal grading.

### Pin 54 — Handy Hearts mood board
**Save as:** `brands/grissom/assets/hh-pin-aug15-blitz-pin1-handy-hearts-mood-board-2026-08-15.jpg`
**Scheduled:** 2026-08-15 14:00 UTC  (09:00 CDT)
**Overlay text:** Handy Hearts Mood Board: Cedar Hollow

**Prompt**
2:3 vertical still life centred on one dented steel thermos resting on weathered cedar boards, placed off-centre in the lower right. Nearby but secondary: a chipped rust-orange mug, a few sawdust curls, and a blurred rain-wet hickory leaf; keep the arrangement sparse. Reserve the top third as a quiet, low-detail view of a honey-lit porch wall for the Canva overlay; no words, labels, or text. Natural golden-hour side light, 35mm Kodak Portra 400 fine grain and lifted blacks, f/3.5, warm cedar-and-honey palette with a dusty sage leaf accent. No people or identifiable faces.

**Avoid**
Overstuffed mood-board collage, branded thermos markings, floating dust, lens flare, artificial coffee steam, teal-orange grading.

### Pin 55 — Every trope in Handy Hearts
**Save as:** `brands/grissom/assets/hh-pin-aug15-blitz-pin2-every-trope-in-handy-hearts-2026-08-15.jpg`
**Scheduled:** 2026-08-15 17:00 UTC  (12:00 CDT)
**Overlay text:** Every Trope in Handy Hearts

**Prompt**
2:3 vertical exterior photograph of a single old cedar toolbox open on a collapsed porch step, off-centre in the upper left, with its orderly hammer, tape measure, and nails visible but no labels, writing, or text. A cream cardigan hangs out of focus over the rail beyond, while a fast-moving summer storm gathers over rolling eastern Oklahoma oak woodland and red clay. Reserve the low-detail, rain-darkened porch floor in the bottom third for the Canva overlay. Natural overcast light, 35mm Kodak Portra 400 grain, f/4, warm cedar-and-honey palette with dusty sage foliage and faded denim shadow. No people or identifiable faces.

**Avoid**
Tool clutter, readable measurement marks, tornado imagery, Appalachian mountains, oversaturated HDR storm clouds, stock-photo staging.

### Pin 56 — Don and Dana
**Save as:** `brands/grissom/assets/hh-pin-aug15-blitz-pin3-don-and-dana-2026-08-15.jpg`
**Scheduled:** 2026-08-15 20:00 UTC  (15:00 CDT)
**Overlay text:** Don and Dana in Cedar Hollow

**Prompt**
2:3 vertical ground-level photograph of two pairs of feet paused on an old porch: scuffed leather work boots facing cream garden clogs, separated by one loose cedar board. Keep them as the single paired subject off-centre in the lower right; include no faces, bodies, or text. A woman’s hand with a plain gold band rests loosely at the cardigan hem, cropped at the frame edge. The softly blurred oak-and-hickory yard and wide afternoon sky occupy a quiet, low-detail top third for the Canva overlay. Golden-hour natural light, 35mm Kodak Portra 400 grain, f/3.5, warm cedar-and-honey with dusty sage foliage and faded denim.

**Avoid**
Face reveal, posed couple feet, high heels, wedding imagery, mountain scenery, waxy skin, lens flare.

### Pin 57 — Cedar Hollow aesthetic
**Save as:** `brands/grissom/assets/hh-pin-aug15-blitz-pin4-cedar-hollow-aesthetic-2026-08-15.jpg`
**Scheduled:** 2026-08-15 23:00 UTC  (18:00 CDT)
**Overlay text:** Cedar Hollow Aesthetic: Small-Town Oklahoma Romance

**Prompt**
2:3 vertical exterior wide photograph of one low red-brick café storefront at the edge of a tiny eastern Oklahoma main street, off-centre in the lower right. A dusty sage painted door, empty cedar bench, gravel parking edge, and a single pickup truck sit beneath a broad, quiet big sky; show no text or readable signage. Keep the uncluttered red-clay roadside in the bottom third low-detail for the Canva overlay. Natural late-day honey light, 35mm Kodak Portra 400 fine grain, f/4, warm brick and cedar palette with faded denim shadows, oak-and-hickory hills in the far distance. No people or identifiable faces.

**Avoid**
Legible storefront signs, busy urban traffic, café patrons facing camera, mountain ranges, neon, HDR saturation.

### Pin 58 — Preorder before September 8
**Save as:** `brands/grissom/assets/hh-pin-aug15-blitz-pin5-preorder-handy-hearts-before-september-8-2026-08-15.jpg`
**Scheduled:** 2026-08-16 02:00 UTC  (21:00 CDT)
**Overlay text:** Preorder Handy Hearts Before September 8

**Prompt**
2:3 vertical close still life of a single blank cream paperback wrapped in plain brown paper and tied with thin faded-denim twine, waiting on a weathered cedar porch rail. It sits off-centre in the lower left; no cover design, words, date, or shipping label is visible. Reserve the sun-warmed, low-detail cedar siding in the top third for the Canva overlay. Natural golden-hour side light, 35mm Kodak Portra 400 grain, f/2.8, warm cedar-and-honey palette with one dusty sage leaf caught near the package. No people or identifiable faces.

**Avoid**
Readable book title, ecommerce packing labels, gift-bow excess, floating dust, strong lens flare, staged product-photo glare.

### Pin 59 — Cedar Hollow Q&A
**Save as:** `brands/grissom/assets/hh-pin-aug16-sunday-pin1-cedar-hollow-qa-2026-08-16.jpg`
**Scheduled:** 2026-08-16 14:00 UTC  (09:00 CDT)
**Overlay text:** Cedar Hollow Q&A: Handy Hearts

**Prompt**
2:3 vertical overhead writer’s-desk photograph with one blank cream note card and a sharpened cedar pencil laid off-centre in the lower right beside a small cup of black coffee. The card must contain absolutely no marks or text; a loose plain gold ring rests near its corner, suggesting an unanswered question without showing a person or face. Leave the top third as quiet, low-detail weathered cedar desktop for the Canva overlay. Soft overcast morning window light, 35mm Kodak Portra 400 fine grain, f/3.5, warm cedar-and-honey palette with a dusty sage pencil band and faded denim shadow.

**Avoid**
Handwritten words, question marks, branded stationery, cluttered author desk, fake ink splatters, teal-orange grading.

### Pin 60 — Does Wes get his own book?
**Save as:** `brands/grissom/assets/hh-pin-aug16-sunday-pin2-does-wes-get-his-own-book-2026-08-16.jpg`
**Scheduled:** 2026-08-16 17:00 UTC  (12:00 CDT)
**Overlay text:** Does Wes Get His Own Book?

**Prompt**
2:3 vertical tailgate still life: one cold unbranded amber bottle stands on the faded-denim blue tailgate of an old truck, off-centre in the upper right, with a second bottle only a soft background shape. A man’s worn work boot and canvas-jacket hem are cropped at the far edge; no face, body detail, labels, or text. Reserve the plain faded-denim tailgate across the bottom third as the quiet Canva-overlay zone. Natural late-afternoon light, 35mm Kodak Portra 400 grain, f/2.8, warm cedar-and-honey tones with dusty sage grass.

**Avoid**
Readable beer labels, party scene, visible face, luxury truck gloss, mountains, neon colours, beer-commercial styling.

### Pin 61 — Sunday slow
**Save as:** `brands/grissom/assets/hh-pin-aug16-sunday-pin3-sunday-slow-2026-08-16.jpg`
**Scheduled:** 2026-08-16 20:00 UTC  (15:00 CDT)
**Overlay text:** Sunday Slow: Small-Town Romance TBR

**Prompt**
2:3 vertical interior photograph of a chipped rust-orange mug beside one closed, unmarked paperback on a faded denim quilt, the pair off-centre in the lower right. A cream curtain lifts slightly at an open window, beyond which eastern Oklahoma oak leaves are softly legible under a calm overcast Sunday. Keep the plain cream curtain and wall across the top third quiet and low-detail for the Canva overlay; no text and no people or identifiable faces. Natural soft window light, 35mm Kodak Portra 400 fine grain, f/3.5, warm cedar-and-honey palette with a dusty sage leaf outside.

**Avoid**
Readable book cover, staged breakfast tray, overly cozy cottage clutter, artificial steam, face in window, lens flare.

### Pin 62 — Three weeks until Handy Hearts
**Save as:** `brands/grissom/assets/hh-pin-aug17-countdown-pin1-3-weeks-until-handy-hearts-2026-08-17.jpg`
**Scheduled:** 2026-08-17 14:00 UTC  (09:00 CDT)
**Overlay text:** 3 Weeks Until Handy Hearts

**Prompt**
2:3 vertical porch-repair detail photograph of three newly cut cedar boards stacked neatly on an old worktable, their clean ends facing the camera and the stack placed off-centre in the upper right. A steel thermos and blurred toolbox remain secondary in shadow. Include no calendar, numbers, labels, or text. Reserve the low-detail sunlit porch floor in the bottom third for the Canva overlay. Natural golden-hour side light reveals wood grain, 35mm Kodak Portra 400 fine grain and soft halation, f/4, warm cedar-and-honey palette with a faded denim rag and dusty sage paint chip. No people or identifiable faces.

**Avoid**
Visible numerals, construction-site chaos, power tools in action, sawdust haze, lens flare, oversaturated orange grading.

### Pin 63 — Why I wrote grief this way
**Save as:** `brands/grissom/assets/hh-pin-aug17-countdown-pin2-why-i-wrote-grief-this-way-2026-08-17.jpg`
**Scheduled:** 2026-08-17 17:00 UTC  (12:00 CDT)
**Overlay text:** Why I Wrote Grief This Way

**Prompt**
2:3 vertical intimate close-up of a woman’s hand with a plain gold wedding band resting against a rain-marked windowpane, shown from the side with no face reflected or visible. Her cream cardigan sleeve enters from the lower right; beyond the glass are soft eastern Oklahoma oak branches and red-clay driveway blur. Keep the pale overcast sky in the top third broad, empty, and low-detail for the Canva overlay; no text. Natural window light, 35mm Kodak Portra 400 fine grain, f/2.8, muted warm cedar-and-honey interior tones with a dusty sage outdoor accent and gently lifted blacks.

**Avoid**
Tears or face reflection, funeral symbols, melodramatic rain, waxy hand skin, misty mountains, wedding-photography glow.

### Pin 64 — Preorder before it sells out
**Save as:** `brands/grissom/assets/hh-pin-aug17-countdown-pin3-preorder-before-it-sells-out-2026-08-17.jpg`
**Scheduled:** 2026-08-17 20:00 UTC  (15:00 CDT)
**Overlay text:** Preorder Before It Sells Out Handy Hearts

**Prompt**
2:3 vertical exterior still life of a single blank cream paperback waiting on the worn cedar seat of an empty porch swing, off-centre in the lower left. Its cover and spine carry no words, marks, or title. The swing chain, a dusty sage porch post, and softly focused rolling oak-and-hickory hills place it in eastern Oklahoma; preserve the simple honey-lit siding across the top third for the Canva overlay. Natural golden-hour light, 35mm Kodak Portra 400 grain, f/3.5, warm cedar-and-honey palette with faded denim-blue shadow. No people or identifiable faces.

**Avoid**
Readable cover art, occupied swing, gift-box staging, Appalachian scenery, heavy bokeh, artificial glow, lens flare.

### Pin 65 — ARC spots closing soon
**Save as:** `brands/grissom/assets/hh-pin-aug17-countdown-pin4-arc-spots-closing-soon-2026-08-17.jpg`
**Scheduled:** 2026-08-17 23:00 UTC  (18:00 CDT)
**Overlay text:** ARC Spots Closing Soon: Handy Hearts

**Prompt**
2:3 vertical utility-led café-counter photograph of one remaining blank cream manuscript packet standing in a small cedar tray, off-centre in the upper right; several empty divider slots imply that the other copies are gone. There must be no readable page, label, logo, or text. A chipped mug, mismatched china saucer, and warm wood counter sit softly behind it at the Hollow Bean Café. Leave the plain warm-wood counter in the bottom third quiet and low-detail for the Canva overlay. Natural soft morning window light, 35mm Kodak Portra 400 grain, f/4, warm cedar-and-honey palette with dusty sage ceramic accent. No people or identifiable faces.

**Avoid**
Fake manuscript lettering, crowded café patrons, sales-sign graphics, stock-photo desk styling, lens flare, teal-orange grading.

### Pin 66 — Almost here
**Save as:** `brands/grissom/assets/hh-pin-aug17-countdown-pin5-almost-here-2026-08-17.jpg`
**Scheduled:** 2026-08-18 02:00 UTC  (21:00 CDT)
**Overlay text:** Almost Here: Handy Hearts Cedar Hollow

**Prompt**
2:3 vertical exterior wide photograph at late golden hour: an old work truck is parked in a red-clay driveway beside Dana’s nearly repaired cedar porch, with one fresh board still leaning against the rail. The truck is the single off-centre subject in the lower right; no person, identifiable face, text, signage, or readable license plate is visible. Let the broad quiet sky and open oak-and-hickory cross-timbers fill a low-detail top third for the Canva overlay. Natural honey side light, 35mm Kodak Portra 400 fine grain, f/4, warm cedar-and-honey with dusty sage trim and faded denim truck shadow.

**Avoid**
Readable plate or truck badge, people in frame, new luxury vehicle, Appalachian mountains, tornado drama, HDR saturation, lens flare.

## Batch 3 summary

| Pin number | Filename | Shot type | Quiet zone (top/bottom) |
|---:|---|---|---|
| 45 | hh-pin-aug13-firstline-arc-pin2-arc-readers-wanted-2026-08-13.jpg | Top-down utility still life | Top |
| 46 | hh-pin-aug13-firstline-arc-pin3-get-handy-hearts-before-launch-day-2026-08-13.jpg | Exterior mailbox product still life | Bottom |
| 47 | hh-pin-aug13-firstline-arc-pin4-he-stopped-counting-2026-08-13.jpg | Extreme hand-and-nail close-up | Top |
| 48 | hh-pin-aug13-firstline-arc-pin5-be-a-first-reader-2026-08-13.jpg | Interior reader still life | Bottom |
| 49 | hh-pin-aug14-porch-storm-pin1-the-porch-scene-2026-08-14.jpg | Cropped mid-action | Top |
| 50 | hh-pin-aug14-porch-storm-pin2-rain-on-a-oklahoma-porch-2026-08-14.jpg | Rain-and-wood detail | Bottom |
| 51 | hh-pin-aug14-porch-storm-pin3-he-catches-her-2026-08-14.jpg | High-angle hand close-up | Bottom |
| 52 | hh-pin-aug14-porch-storm-pin4-neither-of-them-says-anything-2026-08-14.jpg | Backlit doorway silhouettes | Top |
| 53 | hh-pin-aug14-porch-storm-pin5-porch-repair-as-romance-2026-08-14.jpg | Tool-and-shavings workbench detail | Bottom |
| 54 | hh-pin-aug15-blitz-pin1-handy-hearts-mood-board-2026-08-15.jpg | Thermos-led mood still life | Top |
| 55 | hh-pin-aug15-blitz-pin2-every-trope-in-handy-hearts-2026-08-15.jpg | Exterior porch-and-toolbox wide | Bottom |
| 56 | hh-pin-aug15-blitz-pin3-don-and-dana-2026-08-15.jpg | Ground-level footwear pairing | Top |
| 57 | hh-pin-aug15-blitz-pin4-cedar-hollow-aesthetic-2026-08-15.jpg | Main-street exterior wide | Bottom |
| 58 | hh-pin-aug15-blitz-pin5-preorder-handy-hearts-before-september-8-2026-08-15.jpg | Wrapped-book close still life | Top |
| 59 | hh-pin-aug16-sunday-pin1-cedar-hollow-qa-2026-08-16.jpg | Writer-desk overhead still life | Top |
| 60 | hh-pin-aug16-sunday-pin2-does-wes-get-his-own-book-2026-08-16.jpg | Truck-tailgate still life | Bottom |
| 61 | hh-pin-aug16-sunday-pin3-sunday-slow-2026-08-16.jpg | Interior book-and-mug still life | Top |
| 62 | hh-pin-aug17-countdown-pin1-3-weeks-until-handy-hearts-2026-08-17.jpg | Lumber-stack repair detail | Bottom |
| 63 | hh-pin-aug17-countdown-pin2-why-i-wrote-grief-this-way-2026-08-17.jpg | Ringed-hand window close-up | Top |
| 64 | hh-pin-aug17-countdown-pin3-preorder-before-it-sells-out-2026-08-17.jpg | Porch-swing product still life | Top |
| 65 | hh-pin-aug17-countdown-pin4-arc-spots-closing-soon-2026-08-17.jpg | Café counter utility still life | Bottom |
| 66 | hh-pin-aug17-countdown-pin5-almost-here-2026-08-17.jpg | Exterior truck-and-porch wide | Top |
