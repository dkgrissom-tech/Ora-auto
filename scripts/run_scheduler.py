"""
Multi-brand auto-post scheduler.

Reads brands/<brand>/posts/YYYY-MM-DD.md for each registered brand,
parses scheduled blocks, and posts anything scheduled for the current
UTC hour to the listed platforms using that brand's API keys.

Each brand has its own set of secrets, prefixed with the brand name in caps:
  ORA_X_API_KEY, ORA_LINKEDIN_ACCESS_TOKEN, ...
  GRISSOM_X_API_KEY, GRISSOM_PINTEREST_ACCESS_TOKEN, ...
  FAMILYBOOK_X_API_KEY, FAMILYBOOK_PINTEREST_ACCESS_TOKEN, ...

Each post block in a markdown file looks like:

    ## 13:00 UTC  (08:00 CDT)
    platforms: x, linkedin, threads, instagram, pinterest, tiktok, buffer, tailwind
    image: brands/ora/assets/zara_drop1.png      # optional
    video: brands/ora/assets/ora_demo.mp4         # optional, tiktok needs this
    pinterest_title: Just say Ora
    pinterest_url: https://meetora-app.pplx.app
    tailwind_board_id: 123456789                  # optional, Tailwind pin target
    ---
    Body of the post goes here.
    Multiple lines OK.
    ---

Supported platforms:
  bluesky        — direct API, free
  x              — manual-only by policy (skipped auto)
  linkedin       — direct API, free
  threads        — direct API, free (Meta app-review may apply)
  instagram      — direct API, free (Meta business + app-review required)
  pinterest      — direct API, free (Pinterest app-review required)
  tiktok         — direct API, Ora brand only by policy
  buffer         — optional paid fallback, queues to Buffer's schedule
  tailwind       — optional paid Pinterest fallback, requires image + board_id
"""
import os
import sys
import datetime as dt
from pathlib import Path

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
ROOT = Path(__file__).resolve().parent.parent
BRANDS_DIR = ROOT / "brands"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Brands registered to this poster
BRANDS = ["ora", "grissom", "familybook"]

def log(msg):
    ts = dt.datetime.utcnow().isoformat() + "Z"
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_DIR / "scheduler.log", "a") as f:
        f.write(line + "\n")

def secret(brand, key):
    """Read a brand-prefixed secret from env. e.g. secret('ora', 'X_API_KEY')
    looks for ORA_X_API_KEY."""
    full = f"{brand.upper()}_{key}"
    return os.environ.get(full)

def parse_today(brand):
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    f = BRANDS_DIR / brand / "posts" / f"{today}.md"
    if not f.exists():
        return []
    text = f.read_text()
    posts = []
    blocks = text.split("\n## ")[1:]
    for b in blocks:
        header, *rest = b.split("\n", 1)
        body_section = rest[0] if rest else ""
        try:
            hh = int(header.strip().split(":")[0])
        except ValueError:
            continue
        meta = {}
        body_lines = []
        in_body = False
        body_started = False
        for line in body_section.splitlines():
            if line.strip() == "---":
                if not body_started:
                    body_started = True
                    in_body = True
                    continue
                else:
                    break
            if not in_body:
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            else:
                body_lines.append(line)
        posts.append({
            "brand": brand,
            "hour": hh,
            "platforms": [p.strip() for p in meta.get("platforms", "").split(",") if p.strip()],
            "image": meta.get("image"),
            "video": meta.get("video"),
            "pinterest_title": meta.get("pinterest_title"),
            "pinterest_url": meta.get("pinterest_url"),
            "tailwind_board_id": meta.get("tailwind_board_id", ""),
            "body": "\n".join(body_lines).strip(),
        })
    return posts

def asset_url(path):
    return f"https://raw.githubusercontent.com/dkgrissom-tech/Ora-auto/main/{path}"

def post_bluesky(brand, text):
    from atproto import Client
    handle = secret(brand, "BLUESKY_HANDLE")
    password = secret(brand, "BLUESKY_APP_PASSWORD")
    if not (handle and password):
        log(f"[{brand}] Bluesky keys missing — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] Bluesky post: {text[:60]}...")
        return True
    try:
        client = Client()
        client.login(handle, password)
        client.send_post(text=text[:300])
        log(f"[{brand}] Bluesky posted OK")
        return True
    except Exception as e:
        log(f"[{brand}] Bluesky FAIL: {e}")
        return False

def post_linkedin(brand, text):
    import requests
    token = secret(brand, "LINKEDIN_ACCESS_TOKEN")
    urn = secret(brand, "LINKEDIN_AUTHOR_URN")
    if not (token and urn):
        log(f"[{brand}] LinkedIn keys missing — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] LinkedIn post: {text[:60]}...")
        return True
    body = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text[:3000]},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    try:
        r = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers={"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0"},
            json=body, timeout=30,
        )
        if r.status_code in (200, 201):
            log(f"[{brand}] LinkedIn posted OK")
            return True
        log(f"[{brand}] LinkedIn FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"[{brand}] LinkedIn FAIL: {e}")
        return False

def post_threads(brand, text):
    import requests
    token = secret(brand, "META_LONG_TOKEN")
    user = secret(brand, "THREADS_USER_ID")
    if not (token and user):
        log(f"[{brand}] Threads keys missing — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] Threads post: {text[:60]}...")
        return True
    try:
        r = requests.post(
            f"https://graph.threads.net/v1.0/{user}/threads",
            params={"media_type": "TEXT", "text": text[:500], "access_token": token},
            timeout=30,
        )
        if r.status_code == 200:
            cid = r.json().get("id")
            r2 = requests.post(
                f"https://graph.threads.net/v1.0/{user}/threads_publish",
                params={"creation_id": cid, "access_token": token}, timeout=30,
            )
            if r2.status_code == 200:
                log(f"[{brand}] Threads posted OK")
                return True
        log(f"[{brand}] Threads FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"[{brand}] Threads FAIL: {e}")
        return False

def post_instagram(brand, text, image_path):
    import requests
    token = secret(brand, "META_LONG_TOKEN")
    user = secret(brand, "INSTAGRAM_USER_ID")
    if not (token and user and image_path):
        log(f"[{brand}] Instagram missing keys or image — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] Instagram post with image {image_path}: {text[:60]}...")
        return True
    try:
        r = requests.post(
            f"https://graph.facebook.com/v21.0/{user}/media",
            params={"image_url": asset_url(image_path), "caption": text, "access_token": token}, timeout=30,
        )
        if r.status_code == 200:
            cid = r.json().get("id")
            r2 = requests.post(
                f"https://graph.facebook.com/v21.0/{user}/media_publish",
                params={"creation_id": cid, "access_token": token}, timeout=30,
            )
            if r2.status_code == 200:
                log(f"[{brand}] Instagram posted OK")
                return True
        log(f"[{brand}] Instagram FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"[{brand}] Instagram FAIL: {e}")
        return False

def post_pinterest(brand, text, title, dest_url, image_path):
    import requests
    token = secret(brand, "PINTEREST_ACCESS_TOKEN")
    board = secret(brand, "PINTEREST_BOARD_ID")
    if not (token and board and image_path):
        log(f"[{brand}] Pinterest missing keys/image — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] Pinterest pin: {title}")
        return True
    try:
        r = requests.post(
            "https://api.pinterest.com/v5/pins",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "board_id": board,
                "title": title[:100],
                "description": text[:500],
                "link": dest_url,
                "media_source": {"source_type": "image_url", "url": asset_url(image_path)},
            }, timeout=30,
        )
        if r.status_code in (200, 201):
            log(f"[{brand}] Pinterest posted OK")
            return True
        log(f"[{brand}] Pinterest FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"[{brand}] Pinterest FAIL: {e}")
        return False

def post_tiktok(brand, text, video_path):
    import requests
    token = secret(brand, "TIKTOK_ACCESS_TOKEN")
    if not (token and video_path):
        log(f"[{brand}] TikTok missing keys/video — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] TikTok: {video_path}")
        return True
    try:
        r = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "post_info": {
                    "title": text[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": asset_url(video_path),
                },
            }, timeout=30,
        )
        if r.status_code == 200:
            log(f"[{brand}] TikTok posted OK")
            return True
        log(f"[{brand}] TikTok FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"[{brand}] TikTok FAIL: {e}")
        return False

# TikTok is only enabled for Ora (handle @toolstack-y4g).
# Grissom Press and Family Book do not have TikTok accounts by design.
TIKTOK_ALLOWED_BRANDS = {"ora"}

# -----------------------------------------------------------------------------
# Buffer + Tailwind — optional paid scheduling fallback path.
#
# Both are opt-in per post block. If the block lists `buffer` or `tailwind` in
# platforms and the brand has the required secrets, the handler queues the
# post into that service's schedule and lets it fan out to the connected
# platforms. If secrets are missing, the handler no-ops with a clear log line.
#
# Buffer secrets per brand (only add for brands you actually pay for):
#   <BRAND>_BUFFER_ACCESS_TOKEN         # OAuth2 token from Buffer
#   <BRAND>_BUFFER_PROFILE_IDS          # comma-separated list of profile IDs
#                                       # (one per connected channel in that
#                                       #  Buffer account)
#
# Tailwind secrets per brand:
#   <BRAND>_TAILWIND_API_KEY            # Tailwind API key
#   <BRAND>_TAILWIND_BOARD_ID           # optional default Pinterest board ID
#                                       # (falls back to block-level
#                                       #  `tailwind_board_id: ...` meta)
#
# Design intent: use Buffer as a fallback for platforms whose direct-API rail
# is blocked on app-review (e.g. Instagram business, Threads for a new brand),
# and Tailwind specifically for Pinterest volume once the direct Pinterest
# rail proves rate-limiting. The direct-API handlers above stay the default.
# -----------------------------------------------------------------------------

def post_buffer(brand, text, image_path=None, video_path=None):
    import requests
    token = secret(brand, "BUFFER_ACCESS_TOKEN")
    profile_ids_raw = secret(brand, "BUFFER_PROFILE_IDS")
    if not (token and profile_ids_raw):
        log(f"[{brand}] Buffer keys missing — skipping")
        return False
    profile_ids = [p.strip() for p in profile_ids_raw.split(",") if p.strip()]
    if not profile_ids:
        log(f"[{brand}] Buffer profile IDs empty — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] Buffer queue to {len(profile_ids)} profile(s): {text[:60]}...")
        return True

    # Buffer's classic REST API queues an update against one or more profiles.
    # See https://buffer.com/developers/api/updates
    payload = {
        "profile_ids[]": profile_ids,
        "text": text[:2400],
        "shorten": "false",
        "now": "false",  # queue rather than post immediately
    }
    media_url = None
    if video_path:
        media_url = asset_url(video_path)
    elif image_path:
        media_url = asset_url(image_path)
    if media_url:
        payload["media[link]"] = media_url
        payload["media[photo]"] = media_url

    try:
        r = requests.post(
            "https://api.bufferapp.com/1/updates/create.json",
            headers={"Authorization": f"Bearer {token}"},
            data=payload, timeout=30,
        )
        if r.status_code in (200, 201):
            log(f"[{brand}] Buffer queued OK ({len(profile_ids)} profile(s))")
            return True
        log(f"[{brand}] Buffer FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"[{brand}] Buffer FAIL: {e}")
        return False


def post_tailwind(brand, text, image_path=None, dest_url="", board_id=""):
    import requests
    api_key = secret(brand, "TAILWIND_API_KEY")
    if not api_key:
        log(f"[{brand}] Tailwind keys missing — skipping")
        return False
    board = board_id or secret(brand, "TAILWIND_BOARD_ID") or ""
    if not board:
        log(f"[{brand}] Tailwind board_id missing (no block meta, no default secret) — skipping")
        return False
    if not image_path:
        log(f"[{brand}] Tailwind requires an image — skipping")
        return False
    if DRY_RUN:
        log(f"[{brand}] [DRY] Tailwind pin → board {board}: {text[:60]}...")
        return True

    # Tailwind's public Create Pin endpoint. Auth is Bearer <api_key>.
    # https://developer.tailwindapp.com/
    payload = {
        "board_id": board,
        "image_url": asset_url(image_path),
        "description": text[:500],
        "destination_url": dest_url or "",
    }
    try:
        r = requests.post(
            "https://api.tailwindapp.com/v1/pins",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload, timeout=30,
        )
        if r.status_code in (200, 201, 202):
            log(f"[{brand}] Tailwind pin scheduled OK (board {board})")
            return True
        log(f"[{brand}] Tailwind FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"[{brand}] Tailwind FAIL: {e}")
        return False

def main():
    now = dt.datetime.utcnow()
    log(f"Scheduler tick @ {now.isoformat()}Z (hour={now.hour})")
    total_matched = 0
    for brand in BRANDS:
        posts = parse_today(brand)
        matched = [p for p in posts if p["hour"] == now.hour]
        if not matched:
            continue
        total_matched += len(matched)
        for p in matched:
            log(f"[{brand}] Posting to {p['platforms']}: {p['body'][:80]}...")
            for plat in p["platforms"]:
                if plat == "bluesky":
                    post_bluesky(brand, p["body"])
                elif plat == "x":
                    log(f"[{brand}] X is manual-only by policy — skipping auto-post")
                elif plat == "linkedin":
                    post_linkedin(brand, p["body"])
                elif plat == "threads":
                    post_threads(brand, p["body"])
                elif plat == "instagram":
                    post_instagram(brand, p["body"], p.get("image"))
                elif plat == "pinterest":
                    post_pinterest(brand, p["body"], p.get("pinterest_title", brand),
                                   p.get("pinterest_url", ""),
                                   p.get("image"))
                elif plat == "tiktok":
                    if brand not in TIKTOK_ALLOWED_BRANDS:
                        log(f"[{brand}] TikTok disabled for this brand by policy — skipping")
                        continue
                    post_tiktok(brand, p["body"], p.get("video"))
                elif plat == "buffer":
                    post_buffer(brand, p["body"], p.get("image"), p.get("video"))
                elif plat == "tailwind":
                    post_tailwind(
                        brand,
                        p["body"],
                        image_path=p.get("image"),
                        dest_url=p.get("pinterest_url", ""),
                        board_id=p.get("tailwind_board_id", ""),
                    )
                else:
                    log(f"[{brand}] Unknown platform '{plat}' — skipping")
    if total_matched == 0:
        log(f"No posts scheduled across any brand for hour {now.hour}")

if __name__ == "__main__":
    main()
