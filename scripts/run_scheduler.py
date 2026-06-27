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
    platforms: x, linkedin, threads, instagram, pinterest, tiktok
    image: brands/ora/assets/zara_drop1.png      # optional
    video: brands/ora/assets/ora_demo.mp4         # optional, tiktok needs this
    pinterest_title: Just say Ora
    pinterest_url: https://meetora-app.pplx.app
    ---
    Body of the post goes here.
    Multiple lines OK.
    ---
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
            "body": "\n".join(body_lines).strip(),
        })
    return posts

def asset_url(path):
    return f"https://raw.githubusercontent.com/dkgrissom-tech/Ora-auto/main/{path}"

def post_x(brand, text):
    import tweepy
    keys = {k: secret(brand, k) for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")}
    if not all(keys.values()):
        log(f"[{brand}] X keys missing — skipping")
        return False
    try:
        client = tweepy.Client(
            consumer_key=keys["X_API_KEY"],
            consumer_secret=keys["X_API_SECRET"],
            access_token=keys["X_ACCESS_TOKEN"],
            access_token_secret=keys["X_ACCESS_SECRET"],
        )
        if DRY_RUN:
            log(f"[{brand}] [DRY] X post: {text[:60]}...")
            return True
        client.create_tweet(text=text[:280])
        log(f"[{brand}] X posted OK: {text[:60]}...")
        return True
    except Exception as e:
        log(f"[{brand}] X FAIL: {e}")
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
                if plat == "x":
                    post_x(brand, p["body"])
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
    if total_matched == 0:
        log(f"No posts scheduled across any brand for hour {now.hour}")

if __name__ == "__main__":
    main()
