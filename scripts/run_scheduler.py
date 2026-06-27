"""
Ora auto-post scheduler.
Reads posts/YYYY-MM-DD.md, parses scheduled blocks, and posts anything
scheduled for the current UTC hour to the listed platforms.

Each post block in the markdown file looks like:

    ## 13:00 UTC  (08:00 CDT)
    platforms: x, linkedin, threads, instagram, pinterest, tiktok
    image: assets/zara_drop1.png      # optional
    video: assets/ora_demo.mp4         # optional, tiktok needs this
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
POSTS_DIR = ROOT / "posts"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

def log(msg):
    ts = dt.datetime.utcnow().isoformat() + "Z"
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_DIR / "scheduler.log", "a") as f:
        f.write(line + "\n")

def parse_today():
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    f = POSTS_DIR / f"{today}.md"
    if not f.exists():
        log(f"No posts file for {today}")
        return []
    text = f.read_text()
    posts = []
    blocks = text.split("\n## ")[1:]
    for b in blocks:
        header, *rest = b.split("\n", 1)
        body_section = rest[0] if rest else ""
        # header looks like "13:00 UTC  (08:00 CDT)"
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
            "hour": hh,
            "platforms": [p.strip() for p in meta.get("platforms", "").split(",") if p.strip()],
            "image": meta.get("image"),
            "video": meta.get("video"),
            "pinterest_title": meta.get("pinterest_title"),
            "pinterest_url": meta.get("pinterest_url"),
            "body": "\n".join(body_lines).strip(),
        })
    return posts

def post_x(text):
    import tweepy
    keys = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]
    if not all(os.environ.get(k) for k in keys):
        log("X keys missing — skipping")
        return False
    try:
        client = tweepy.Client(
            consumer_key=os.environ["X_API_KEY"],
            consumer_secret=os.environ["X_API_SECRET"],
            access_token=os.environ["X_ACCESS_TOKEN"],
            access_token_secret=os.environ["X_ACCESS_SECRET"],
        )
        if DRY_RUN:
            log(f"[DRY] X post: {text[:60]}...")
            return True
        client.create_tweet(text=text[:280])
        log(f"X posted OK: {text[:60]}...")
        return True
    except Exception as e:
        log(f"X FAIL: {e}")
        return False

def post_linkedin(text):
    import requests
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    urn = os.environ.get("LINKEDIN_AUTHOR_URN")
    if not (token and urn):
        log("LinkedIn keys missing — skipping")
        return False
    if DRY_RUN:
        log(f"[DRY] LinkedIn post: {text[:60]}...")
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
            log("LinkedIn posted OK")
            return True
        log(f"LinkedIn FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"LinkedIn FAIL: {e}")
        return False

def post_threads(text):
    import requests
    token = os.environ.get("META_LONG_TOKEN")
    user = os.environ.get("THREADS_USER_ID")
    if not (token and user):
        log("Threads keys missing — skipping")
        return False
    if DRY_RUN:
        log(f"[DRY] Threads post: {text[:60]}...")
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
                log("Threads posted OK")
                return True
        log(f"Threads FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"Threads FAIL: {e}")
        return False

def post_instagram(text, image_path):
    import requests
    token = os.environ.get("META_LONG_TOKEN")
    user = os.environ.get("INSTAGRAM_USER_ID")
    if not (token and user and image_path):
        log("Instagram missing keys or image — skipping")
        return False
    image_url = f"https://raw.githubusercontent.com/dkgrissom-tech/ora-auto/main/{image_path}"
    if DRY_RUN:
        log(f"[DRY] Instagram post with image {image_url}: {text[:60]}...")
        return True
    try:
        r = requests.post(
            f"https://graph.facebook.com/v21.0/{user}/media",
            params={"image_url": image_url, "caption": text, "access_token": token}, timeout=30,
        )
        if r.status_code == 200:
            cid = r.json().get("id")
            r2 = requests.post(
                f"https://graph.facebook.com/v21.0/{user}/media_publish",
                params={"creation_id": cid, "access_token": token}, timeout=30,
            )
            if r2.status_code == 200:
                log("Instagram posted OK")
                return True
        log(f"Instagram FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"Instagram FAIL: {e}")
        return False

def post_pinterest(text, title, dest_url, image_path):
    import requests
    token = os.environ.get("PINTEREST_ACCESS_TOKEN")
    board = os.environ.get("PINTEREST_BOARD_ID")
    if not (token and board and image_path):
        log("Pinterest missing keys/image — skipping")
        return False
    image_url = f"https://raw.githubusercontent.com/dkgrissom-tech/ora-auto/main/{image_path}"
    if DRY_RUN:
        log(f"[DRY] Pinterest pin: {title}")
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
                "media_source": {"source_type": "image_url", "url": image_url},
            }, timeout=30,
        )
        if r.status_code in (200, 201):
            log("Pinterest posted OK")
            return True
        log(f"Pinterest FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"Pinterest FAIL: {e}")
        return False

def post_tiktok(text, video_path):
    # TikTok upload-by-URL flow
    import requests
    token = os.environ.get("TIKTOK_ACCESS_TOKEN")
    if not (token and video_path):
        log("TikTok missing keys/video — skipping")
        return False
    video_url = f"https://raw.githubusercontent.com/dkgrissom-tech/ora-auto/main/{video_path}"
    if DRY_RUN:
        log(f"[DRY] TikTok: {video_url}")
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
                    "video_url": video_url,
                },
            }, timeout=30,
        )
        if r.status_code == 200:
            log("TikTok posted OK")
            return True
        log(f"TikTok FAIL: {r.status_code} {r.text[:200]}")
        return False
    except Exception as e:
        log(f"TikTok FAIL: {e}")
        return False

def main():
    now = dt.datetime.utcnow()
    log(f"Scheduler tick @ {now.isoformat()}Z (hour={now.hour})")
    posts = parse_today()
    matched = [p for p in posts if p["hour"] == now.hour]
    if not matched:
        log(f"No posts scheduled for hour {now.hour}")
        return
    for p in matched:
        log(f"Posting to {p['platforms']}: {p['body'][:80]}...")
        for plat in p["platforms"]:
            if plat == "x":
                post_x(p["body"])
            elif plat == "linkedin":
                post_linkedin(p["body"])
            elif plat == "threads":
                post_threads(p["body"])
            elif plat == "instagram":
                post_instagram(p["body"], p.get("image"))
            elif plat == "pinterest":
                post_pinterest(p["body"], p.get("pinterest_title", "Ora"),
                               p.get("pinterest_url", "https://meetora-app.pplx.app"),
                               p.get("image"))
            elif plat == "tiktok":
                post_tiktok(p["body"], p.get("video"))

if __name__ == "__main__":
    main()
