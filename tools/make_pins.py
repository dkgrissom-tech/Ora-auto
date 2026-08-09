#!/usr/bin/env python3
"""
Generate every missing post image referenced by the brand queues.

Scans brands/<brand>/posts/*.md, finds each block with an `image:` (or `video:`
cover) whose file is absent, and renders a branded typographic card at the right
aspect ratio for its platform.

Filenames are taken verbatim from the queue, so output drops straight into place
and `asset_url()` in scripts/run_scheduler.py resolves it on raw.githubusercontent.

Usage:
    python3 tools/make_pins.py               # render all missing
    python3 tools/make_pins.py --from 2026-08-09   # only dates >= given
    python3 tools/make_pins.py --force       # re-render even if present
    python3 tools/make_pins.py --only hh-pin-aug9  # substring filter
"""
import argparse
import hashlib
import random
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"

SERIF = FONTS / "PlayfairDisplay.ttf"
SANS = FONTS / "Inter.ttf"

# ---------------------------------------------------------------- canvas specs
# Pinterest 2:3 is the format Pinterest itself recommends; Instagram feed is 4:5
# and Reels/Stories covers are 9:16.
SPECS = {
    "pin":      (1000, 1500),
    "carousel": (1080, 1350),
    "reel":     (1080, 1920),
}

# --------------------------------------------------------------- brand palettes
# Cedar Hollow is small-town Oklahoma: warm, wooded, lamplit. Four variants keep
# a 5-pin daily batch from looking like one image printed five times.
PALETTES = [
    {"bg": (31, 58, 46),   "bg2": (18, 36, 29),  "ink": (245, 239, 227),
     "accent": (214, 148, 74),  "muted": (150, 173, 152)},
    {"bg": (245, 239, 227), "bg2": (228, 216, 196), "ink": (43, 38, 32),
     "accent": (166, 84, 45),   "muted": (122, 110, 94)},
    {"bg": (61, 42, 38),   "bg2": (38, 26, 24),  "ink": (243, 232, 216),
     "accent": (206, 150, 96),  "muted": (166, 141, 121)},
    {"bg": (44, 62, 72),   "bg2": (26, 39, 47),  "ink": (240, 238, 231),
     "accent": (198, 141, 88),  "muted": (144, 163, 172)},
]

BRAND_LINES = {
    "grissom":    ("A CEDAR HOLLOW ROMANCE", "D.K. GRISSOM"),
    "ora":        ("ORA", "JUST SAY ORA"),
    "familybook": ("FAMILY BOOK CREATOR", "MADE FOR YOUR KID"),
}


def font(path, size, weight=None):
    f = ImageFont.truetype(str(path), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def text_w(draw, s, f, tracking=0):
    if not s:
        return 0
    w = draw.textlength(s, font=f)
    return w + tracking * max(len(s) - 1, 0)


def draw_tracked(draw, xy, s, f, fill, tracking=0, anchor_center_x=None):
    """Draw with letter-spacing. Pillow has no tracking, so step per glyph."""
    x, y = xy
    if anchor_center_x is not None:
        x = anchor_center_x - text_w(draw, s, f, tracking) / 2
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking


def wrap(draw, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, s, path, max_w, max_h, hi, lo=18, weight=None, leading=1.16):
    """Largest size at which `s` wraps inside max_w x max_h. Never overflows."""
    best = None
    while hi >= lo:
        mid = (hi + lo) // 2
        f = font(path, mid, weight)
        lines = wrap(draw, s, f, max_w)
        lh = int(mid * leading)
        if len(lines) * lh <= max_h and all(
            draw.textlength(l, font=f) <= max_w for l in lines
        ):
            best = (f, lines, lh, mid)
            lo = mid + 1
        else:
            hi = mid - 1
    if best is None:
        f = font(path, lo, weight)
        best = (f, wrap(draw, s, f, max_w), int(lo * leading), lo)
    return best


def background(size, pal, seed):
    """Vertical gradient, corner vignette, and fine grain — flat fills read cheap."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        t = t * t * (3 - 2 * t)  # smoothstep, keeps the midtone from banding
        px[0, y] = tuple(
            int(pal["bg"][i] + (pal["bg2"][i] - pal["bg"][i]) * t) for i in range(3)
        )
    img = img.resize((w, h))

    rnd = random.Random(seed)
    grain = Image.new("L", (w // 3, h // 3))
    grain.putdata([128 + rnd.randint(-16, 16) for _ in range((w // 3) * (h // 3))])
    grain = grain.resize((w, h), Image.BILINEAR)
    img = Image.blend(img, Image.merge("RGB", (grain, grain, grain)), 0.055)
    return img


def render(spec_key, title, eyebrow, footer_l, footer_r, kicker, seed, out):
    W, H = SPECS[spec_key]
    pal = PALETTES[seed % len(PALETTES)]
    img = background((W, H), pal, seed)
    d = ImageDraw.Draw(img)

    margin = int(W * 0.085)
    inner = int(W * 0.038)

    # hairline frame
    d.rectangle([inner, inner, W - inner - 1, H - inner - 1],
                outline=pal["muted"] + (0,) if False else pal["muted"], width=2)

    cx = W // 2
    top = margin + int(H * 0.055)

    # eyebrow
    ey_f = font(SANS, int(W * 0.026), 600)
    tracking = int(W * 0.0075)
    draw_tracked(d, (0, top), eyebrow.upper(), ey_f, pal["accent"],
                 tracking, anchor_center_x=cx)
    top += int(W * 0.026) + int(H * 0.028)

    # short rule under eyebrow
    rw = int(W * 0.07)
    d.line([cx - rw, top, cx + rw, top], fill=pal["accent"], width=2)
    top += int(H * 0.045)

    # footer reserved first so the title can never collide with it
    foot_f = font(SANS, int(W * 0.0225), 500)
    foot_y = H - margin - int(W * 0.0225) - int(H * 0.012)
    kick_f = font(SERIF, int(W * 0.032), 500)
    kick_h = int(W * 0.032) + int(H * 0.03) if kicker else 0

    title_max_h = foot_y - top - kick_h - int(H * 0.06)
    title_max_w = W - 2 * margin

    f, lines, lh, sz = fit_block(
        d, title, SERIF, title_max_w, title_max_h,
        hi=int(W * 0.115), weight=600, leading=1.14,
    )
    block_h = len(lines) * lh
    y = top + max((title_max_h - block_h) // 2, 0)
    for ln in lines:
        d.text((cx, y), ln, font=f, fill=pal["ink"], anchor="ma")
        y += lh

    # kicker (teaser line) sits between title and footer
    if kicker:
        kf, klines, klh, _ = fit_block(
            d, kicker, SERIF, int(W * 0.74), kick_h + int(H * 0.02),
            hi=int(W * 0.034), weight=400, leading=1.25,
        )
        if len(klines) > 2:
            # clipping silently mid-sentence reads like a bug; mark the cut
            last = klines[1]
            while last and d.textlength(last + "\u2026", font=kf) > int(W * 0.74):
                last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
            klines = [klines[0], last.rstrip(" ,;:-") + "\u2026"]
        ky = foot_y - int(H * 0.055) - len(klines) * klh
        for ln in klines:
            d.text((cx, ky), ln, font=kf, fill=pal["muted"], anchor="ma")
            ky += klh

    # footer rule + marks
    d.line([margin, foot_y - int(H * 0.022), W - margin, foot_y - int(H * 0.022)],
           fill=pal["muted"], width=1)
    tr = int(W * 0.004)
    d.text((margin, foot_y), footer_l.upper(), font=foot_f, fill=pal["muted"])
    rw2 = text_w(d, footer_r.upper(), foot_f, tr)
    draw_tracked(d, (W - margin - rw2, foot_y), footer_r.upper(), foot_f,
                 pal["accent"], tr)

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in (".jpg", ".jpeg"):
        img.save(out, "JPEG", quality=90, optimize=True)
    else:
        img.save(out, "PNG", optimize=True)


# ------------------------------------------------------------------ queue parse
# Playfair/Inter carry no emoji glyphs, so anything outside their coverage would
# render as a tofu box. Strip it rather than ship a broken card.
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002190-\U000021FF\U00002B00-\U00002BFF\uFE0F\u200d]+"
)


def clean(s):
    s = EMOJI.sub("", s or "")
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    return re.sub(r"\s{2,}", " ", s).strip(" -\u2013\u2014|")


def headline(s, limit=68):
    """Queue titles are slug-ish ('X - Y - Z'). Keep the hook, drop the SEO tail."""
    s = clean(s)
    parts = [p.strip() for p in re.split(r"\s+[-\u2013\u2014|]\s+", s) if p.strip()]
    if parts:
        s = parts[0]
        # a bare fragment is a worse headline than two joined fragments
        if len(s) < 18 and len(parts) > 1:
            s = f"{parts[0]} \u2014 {parts[1]}"
    # stop at the first sentence end if that already reads as a full thought
    m = re.match(r"^(.{18,%d}?[.!?])\s" % limit, s)
    if m:
        s = m.group(1)
    return trim(s, limit)


def whole_sentences(s):
    """A teaser that trails off mid-clause looks like a rendering bug. Keep only
    complete sentences; if there are none, show nothing."""
    s = (s or "").strip()
    if not s:
        return ""
    if s.endswith("\u2026") or re.search(r"[.!?][\"')]?$", s):
        return s
    m = list(re.finditer(r"[.!?][\"')]?(?=\s|$)", s))
    return s[: m[-1].end()].strip() if m else ""


def trim(s, limit):
    """Never cut mid-word; prefer a sentence boundary, else ellipsis."""
    s = clean(s)
    if len(s) <= limit:
        return s
    cut = s[:limit]
    for stop in (".", "!", "?"):
        i = cut.rfind(stop)
        if i >= limit * 0.5:
            return cut[: i + 1]
    i = cut.rfind(" ")
    return (cut[:i] if i > 0 else cut).rstrip(" ,;:-") + "\u2026"


def derive_title(body):
    for raw in (body or "").splitlines():
        line = re.sub(r"<!--.*?-->", "", raw).strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^#+\s*", "", line).replace("**", "")
        line = re.sub(r"[*_`]", "", line)
        line = re.sub(r"[\"\u201c\u201d]", "", line)
        line = re.sub(r"\s*\|\s*", " - ", line)
        return re.sub(r"\s{2,}", " ", line).strip()
    return ""


def teaser(body):
    """Bodies are hard-wrapped at ~70 chars, so a raw line is a fragment, not a
    sentence. Rejoin each paragraph before picking the hook."""
    text = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    paras = []
    for chunk in re.split(r"\n\s*\n", text):
        joined = " ".join(l.strip() for l in chunk.splitlines() if l.strip())
        joined = re.sub(r"[*_`]", "", joined).strip()
        if not joined:
            continue
        if joined.startswith("#") or joined.startswith("http"):
            continue  # hashtag block or bare link, never a teaser
        paras.append(re.sub(r"\s{2,}", " ", joined))
    if len(paras) < 2:
        return ""
    # paragraph 1 is the headline; paragraph 2 is the body copy
    return paras[1]


def spec_for(path, platforms):
    n = path.lower()
    if "reel" in n or "story" in n:
        return "reel"
    if "carousel" in n or ("instagram" in platforms and "pin" not in n):
        return "carousel"
    return "pin"


def title_from_filename(path):
    """Fallback when a block has no usable body: the slug carries the concept."""
    stem = Path(path).stem
    stem = re.sub(r"-2026-\d{2}-\d{2}$", "", stem)
    stem = re.sub(r"^hh-pin-aug\d+-", "", stem)
    stem = re.sub(r"^hh-pin-", "", stem)
    stem = re.sub(r"^handy-hearts-ig-(carousel|reel)-", "", stem)
    stem = re.sub(r"^[a-z]+-batch-", "", stem)
    stem = re.sub(r"^pin\d+-", "", stem)
    stem = re.sub(r"^[a-z0-9]+-pin\d+-", "", stem)
    return stem.replace("-", " ").strip().title()


def collect(from_date=None, only=None, force=False):
    items = []
    for f in sorted(ROOT.joinpath("brands").glob("*/posts/*.md")):
        if from_date and f.stem < from_date:
            continue
        brand = f.parts[-3]
        for blk in f.read_text().split("\n## ")[1:]:
            header, *rest = blk.split("\n", 1)
            sec = rest[0] if rest else ""
            meta, body, in_body, started = {}, [], False, False
            for line in sec.splitlines():
                if line.strip() == "---":
                    if not started:
                        started, in_body = True, True
                        continue
                    break
                if in_body:
                    body.append(line)
                elif ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            img = meta.get("image")
            if not img:
                continue
            if only and only not in img:
                continue
            dest = ROOT / img
            if dest.exists() and not force:
                continue
            plats = meta.get("platforms", "")
            body_s = "\n".join(body).strip()
            raw_title = (meta.get("pinterest_title")
                         or derive_title(body_s)
                         or title_from_filename(img))
            title = headline(raw_title)
            kicker = trim(teaser(body_s), 96)
            # if the headline dropped a meaningful tail and there's no teaser,
            # promote the tail rather than leaving dead space
            if not kicker:
                tail = clean(raw_title)[len(title):].strip(" -\u2013\u2014|")
                kicker = trim(tail, 96)
            kicker = whole_sentences(kicker)
            items.append({
                "path": img, "dest": dest, "brand": brand,
                "spec": spec_for(img, plats),
                "title": title or title_from_filename(img),
                "kicker": kicker,
                "date": f.stem,
            })
    # de-dup: the same asset can be referenced by more than one block
    seen, out = set(), []
    for it in items:
        if it["path"] in seen:
            continue
        seen.add(it["path"])
        out.append(it)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="from_date", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    items = collect(a.from_date, a.only, a.force)
    if a.limit:
        items = items[: a.limit]
    if not items:
        print("Nothing to render — every referenced image already exists.")
        return 0

    print(f"Rendering {len(items)} image(s)\n")
    for it in items:
        eyebrow, sign = BRAND_LINES.get(it["brand"], (it["brand"].upper(), ""))
        seed = int(hashlib.md5(it["path"].encode()).hexdigest()[:8], 16)
        render(
            it["spec"], it["title"], eyebrow,
            footer_l=sign,
            footer_r="Sept 8, 2026" if it["brand"] == "grissom" else "",
            kicker=it["kicker"], seed=seed, out=it["dest"],
        )
        print(f"  [{it['spec']:8}] {it['path']}")
    print(f"\nDone. {len(items)} file(s) written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
