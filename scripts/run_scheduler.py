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
import re
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
            "alt": meta.get("alt"),
            "video": meta.get("video"),
            "pinterest_title": meta.get("pinterest_title"),
            "pinterest_url": meta.get("pinterest_url"),
            "body": "\n".join(body_lines).strip(),
        })
    return posts

def derive_pin_title(body):
    """Pinterest needs a title. 61 of the 66 Aug 4-18 pins ship no pinterest_title,
    so derive one from the first real line of the body instead of falling back to
    the bare brand name."""
    for raw in (body or "").splitlines():
        line = re.sub(r"<!--.*?-->", "", raw).strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^#+\s*", "", line)
        line = line.replace("**", "")
        line = re.sub(r"[*_`]", "", line)
        line = re.sub(r"[\"\u201c\u201d]", "", line)
        line = re.sub(r"\s*\|\s*", " - ", line)
        return re.sub(r"\s{2,}", " ", line).strip()[:100]
    return ""

# A pin with no destination link cannot drive a preorder, so fall back to each
# brand's canonical page. Override with {BRAND}_PINTEREST_LINK.
DEFAULT_PIN_LINKS = {
    "grissom": "https://cedarhollow.pplx.app",
    "familybook": "https://familybookcreator.app",
}

def pin_link(brand, dest_url):
    return (dest_url
            or os.environ.get(f"{brand.upper()}_PINTEREST_LINK")
            or DEFAULT_PIN_LINKS.get(brand, ""))

def asset_url(path):
    return f"https://raw.githubusercontent.com/dkgrissom-tech/Ora-auto/main/{path}"

# Bluesky uploads images as blobs rather than by URL, and the PDS rejects any
# blob over ~976KB. Every other platform here takes an asset_url() instead, so
# this is the only path that needs the actual bytes.
BLUESKY_BLOB_LIMIT = 976_560

def load_asset_bytes(brand, path):
    """Return raw bytes for a repo-relative asset path, or None.

    Prefers the local checkout: Actions already has the file, so this avoids
    both a network round trip and raw.githubusercontent's propagation delay on
    freshly committed assets. Falls back to HTTP for assets that exist upstream
    but not in this checkout."""
    if not path:
        return None
    local = ROOT / path
    if local.exists():
        return local.read_bytes()
    try:
        import requests
        r = requests.get(asset_url(path), timeout=30)
        if r.status_code == 200:
            return r.content
        log(f"[{brand}] asset fetch got {r.status_code} for {path}")
    except Exception as e:
        log(f"[{brand}] asset fetch failed for {path}: {e}")
    return None

def post_bluesky(brand, text, image_path=None, alt_text=None):
    from atproto import Client
    handle_raw = secret(brand, "BLUESKY_HANDLE") or ""
    password_raw = secret(brand, "BLUESKY_APP_PASSWORD") or ""
    # Normalize handle: strip whitespace, leading @, and lowercase.
    # Bluesky handles are case-insensitive but the client is strict about
    # formatting: no @, no spaces, no smart quotes.
    handle = handle_raw.strip().lstrip("@").strip().lower()
    # If user stored just a username without a domain, assume default bsky.social.
    # (Custom-domain handles like 'dkgrissom.com' contain a dot and are left alone.)
    if handle and "." not in handle:
        handle = f"{handle}.bsky.social"
    # Normalize app password: strip whitespace only. Preserve hyphens/case.
    password = password_raw.strip()
    if not (handle and password):
        log(f"[{brand}] Bluesky keys missing — not configured")
        return None
    # Log a fingerprint (character count + shape) that GitHub can't mask
    # because it doesn't match the secret value directly.
    h_len = len(handle)
    h_dots = handle.count(".")
    h_endswith_bsky = handle.endswith(".bsky.social")
    pw_len = len(password)
    pw_hyphens = password.count("-")
    log(f"[{brand}] Bluesky login fingerprint: handle_len={h_len} dots={h_dots} ends_bsky_social={h_endswith_bsky} pw_len={pw_len} pw_hyphens={pw_hyphens}")
    # Resolve the image before the DRY_RUN gate so a dry run surfaces a missing
    # or oversized asset instead of hiding it until the first real post.
    blob = load_asset_bytes(brand, image_path) if image_path else None
    if image_path and blob is None:
        log(f"[{brand}] Bluesky image {image_path} unavailable - posting text only")
    if blob and len(blob) > BLUESKY_BLOB_LIMIT:
        log(f"[{brand}] Bluesky image {image_path} is {len(blob)}B, over the "
            f"{BLUESKY_BLOB_LIMIT}B blob limit - posting text only. "
            f"Re-export it smaller.")
        blob = None

    # Bluesky shows alt text prominently and flags images without it.
    alt = (alt_text or "").strip()
    if blob and not alt:
        alt = derive_pin_title(text)
        log(f"[{brand}] Bluesky alt text derived from body - add 'alt:' to the "
            f"queue entry for a real image description")

    if DRY_RUN:
        detail = f" with image {image_path} ({len(blob)}B)" if blob else ""
        log(f"[{brand}] [DRY] Bluesky post{detail}: {text[:60]}...")
        return True
    try:
        client = Client()
        client.login(handle, password)
        if blob:
            client.send_image(text=text[:300], image=blob, image_alt=alt[:1000])
            log(f"[{brand}] Bluesky posted OK with image {image_path}")
        else:
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
        log(f"[{brand}] LinkedIn keys missing — not configured")
        return None
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
        log(f"[{brand}] Threads keys missing — not configured")
        return None
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
        log(f"[{brand}] Instagram missing keys or image — not configured")
        return None
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
    title = title or brand
    dest_url = dest_url or ""
    if not (token and board and image_path):
        log(f"[{brand}] Pinterest missing keys/image — not configured")
        return None
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
                **({"link": dest_url} if dest_url else {}),
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
        log(f"[{brand}] TikTok missing keys/video — not configured")
        return None
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

# ---------------------------------------------------------------------------
# Buffer publishing
#
# Buffer is a single account (not per-brand), reached through one GraphQL
# endpoint. It is how Instagram gets published: the direct Meta Graph path in
# post_instagram() needs a reviewed Facebook app, which this account does not
# have, so Buffer is the working route.
#
# Schema verified live against api.buffer.com on 2026-08-09:
#   createPost(input: CreatePostInput!)
#   CreatePostInput { channelId: ChannelId!  assets: [AssetInput!]!
#                     mode: ShareMode!  schedulingType: SchedulingType!
#                     needsApproval: Boolean!  text: String
#                     metadata: PostInputMetaData }
#   ShareMode      = addToQueue | customScheduled | shareNext | shareNow
#   SchedulingType = automatic | notification
#   ImageAssetInput { url: String!  thumbnailUrl  metadata { altText: String! } }
#   InstagramPostMetadataInput { shouldShareToFeed: Boolean!  type: PostType!
#                                firstComment  link  ... }
#   PostType = carousel | reel | story | post | thread | short | ...
# ---------------------------------------------------------------------------

BUFFER_API = "https://api.buffer.com"

# Channel IDs resolved from the live account. Override with env vars if the
# channels are ever reconnected (reconnecting changes the ID).
BUFFER_CHANNELS = {
    "instagram": os.environ.get("BUFFER_CHANNEL_INSTAGRAM", "6a4aa7984048344628728874"),
    "tiktok":    os.environ.get("BUFFER_CHANNEL_TIKTOK",    "6a236b76c687a22dd4667858"),
    "youtube":   os.environ.get("BUFFER_CHANNEL_YOUTUBE",   "6a4aa6ec40483446287286c9"),
    # No hardcoded default: Pinterest was not connected in Buffer when the
    # others were resolved. Left blank so resolve_buffer_pinterest() discovers
    # it the moment the channel is connected, with no code change needed.
    "pinterest": os.environ.get("BUFFER_CHANNEL_PINTEREST", ""),
}

# Cache the lookup for the life of the process. One Actions run publishes a
# handful of posts and the channel list will not change mid-run.
_buffer_pinterest = "unresolved"


def resolve_buffer_pinterest():
    """Return (channel_id, board_service_id) for Pinterest via Buffer, or None.

    Both values are discovered from the live account so that connecting
    Pinterest in Buffer is the only action required - no IDs to copy into
    secrets. Env vars still win if either needs pinning down:
      BUFFER_CHANNEL_PINTEREST    channel id
      BUFFER_PINTEREST_BOARD      board name to match, or a board id
    """
    global _buffer_pinterest
    if _buffer_pinterest != "unresolved":
        return _buffer_pinterest

    _buffer_pinterest = None
    if not buffer_token():
        return None

    want_board = (os.environ.get("BUFFER_PINTEREST_BOARD") or "").strip()
    data, err = buffer_gql(CHANNELS_WITH_BOARDS, {})
    if err:
        log(f"Buffer channel lookup failed: {err}")
        return None

    pins = [c for c in ((data or {}).get("channels") or [])
            if (c.get("service") or "").lower() == "pinterest"]
    if not pins:
        log("Buffer has no Pinterest channel connected - "
            "connect it at buffer.com to restore the Pinterest slot")
        return None

    ch = pins[0]
    if os.environ.get("BUFFER_CHANNEL_PINTEREST"):
        ch = next((c for c in pins
                   if c.get("id") == os.environ["BUFFER_CHANNEL_PINTEREST"]), ch)
    if len(pins) > 1:
        log(f"Buffer has {len(pins)} Pinterest channels; using "
            f"{ch.get('name') or ch.get('id')}. Set BUFFER_CHANNEL_PINTEREST to pin it.")
    if ch.get("isDisconnected"):
        log(f"Buffer Pinterest channel {ch.get('name') or ch.get('id')} "
            "is disconnected - reconnect it at buffer.com")
        return None

    boards = (((ch.get("metadata") or {}).get("boards")) or [])
    board = None
    if want_board:
        board = next((b for b in boards
                      if want_board.lower() in (b.get("name") or "").lower()
                      or want_board in (b.get("serviceId") or "")), None)
        if board is None:
            log(f"BUFFER_PINTEREST_BOARD={want_board!r} matched none of "
                f"{[b.get('name') for b in boards]}")
    if board is None and boards:
        board = boards[0]
        if len(boards) > 1:
            log(f"Pinning to board {board.get('name')!r} of "
                f"{[b.get('name') for b in boards]}. "
                "Set BUFFER_PINTEREST_BOARD to choose another.")

    if not boards:
        # Buffer can publish to the channel default when no board is given.
        log("Buffer Pinterest channel reports no boards - letting Buffer "
            "choose the destination board")

    _buffer_pinterest = (ch.get("id"), (board or {}).get("serviceId"))
    log(f"Buffer Pinterest resolved: channel={ch.get('name') or ch.get('id')} "
        f"board={(board or {}).get('name') or 'default'}")
    return _buffer_pinterest


CHANNELS_WITH_BOARDS = """
query ChannelsWithBoards {
  channels {
    id
    name
    service
    isDisconnected
    metadata {
      ... on PinterestMetadata {
        boards { id name serviceId }
      }
    }
  }
}
"""


def buffer_token():
    # The secret was saved with a truncated name in GitHub; accept both so a
    # rename does not silently disable posting.
    return (os.environ.get("BUFFER_ACCESS_TOKEN")
            or os.environ.get("BUFFER_ACCESS_TOKE") or "").strip()


def buffer_gql(query, variables, attempts=4):
    """Buffer intermittently answers a valid token with 401 UNAUTHENTICATED -
    observed repeatedly on 2026-08-09, with identical requests succeeding
    seconds apart. Treat auth, rate-limit and 5xx responses as transient and
    retry; only a GraphQL validation error is worth failing immediately."""
    import time
    import requests
    last = "no attempt made"
    for i in range(attempts):
        try:
            r = requests.post(
                BUFFER_API,
                headers={"Authorization": f"Bearer {buffer_token()}",
                         "Content-Type": "application/json"},
                json={"query": query, "variables": variables}, timeout=45,
            )
        except Exception as e:
            last = f"transport: {e}"
        else:
            try:
                payload = r.json()
            except Exception:
                payload = {}
            if r.status_code < 400 and not payload.get("errors"):
                return payload.get("data"), None
            msgs = "; ".join(e.get("message", "?") for e in payload.get("errors") or [])
            last = f"HTTP {r.status_code}: {msgs or r.text[:200]}"
            # A malformed query will never succeed - do not burn retries on it.
            codes = {(e.get("extensions") or {}).get("code")
                     for e in payload.get("errors") or []}
            if "GRAPHQL_VALIDATION_FAILED" in codes:
                return None, last
            if r.status_code < 500 and r.status_code not in (401, 408, 429):
                return None, last
        if i < attempts - 1:
            wait = 2 ** i
            log(f"Buffer transient error ({last[:80]}) - retrying in {wait}s")
            time.sleep(wait)
    return None, f"{last} (after {attempts} attempts)"


# createPost returns the union PostActionPayload. Every member is handled
# explicitly - an unhandled member would look like a silent success.
# Verified members: PostActionSuccess, InvalidInputError, LimitReachedError,
# NotFoundError, RestProxyError, UnauthorizedError, UnexpectedError.
CREATE_POST = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id status sentAt } }
    ... on RestProxyError    { code message }
    ... on InvalidInputError  { message }
    ... on LimitReachedError  { message }
    ... on NotFoundError      { message }
    ... on UnauthorizedError  { message }
    ... on UnexpectedError    { message }
  }
}
"""


def ig_post_type(image_path):
    """Buffer needs the post type declared. Infer it the same way the art
    pipeline does, from the filename."""
    n = (image_path or "").lower()
    if "reel" in n or "story" in n:
        return "reel"
    if "carousel" in n:
        return "carousel"
    return "post"


def post_buffer(brand, text, image_path, service="instagram", alt_text=None,
                pin_title=None, pin_url=None, board_id=None):
    """Publish immediately through Buffer to one connected channel."""
    channel = BUFFER_CHANNELS.get(service)
    token = buffer_token()
    if not token:
        log(f"[{brand}] Buffer token missing - not configured")
        return None
    if not channel:
        log(f"[{brand}] Buffer has no {service} channel configured")
        return None
    # Neither Instagram nor Pinterest will accept a post with no media.
    if service in ("instagram", "pinterest") and not image_path:
        log(f"[{brand}] Buffer/{service} needs an image - not configured")
        return None

    assets = []
    if image_path:
        assets.append({"image": {
            "url": asset_url(image_path),
            "metadata": {"altText": (alt_text or text or brand)[:400]},
        }})

    variables = {"input": {
        "channelId": channel,
        "text": (text or "")[:2200],
        "assets": assets,
        "mode": "shareNow",
        "schedulingType": "automatic",
        "needsApproval": False,
        "source": "ora-auto",
    }}
    if service == "instagram":
        variables["input"]["metadata"] = {"instagram": {
            "shouldShareToFeed": True,
            "type": ig_post_type(image_path),
        }}
    elif service == "pinterest":
        # A pin with no title and no destination link cannot drive anything, so
        # both are always populated - title derived from the body when the queue
        # entry omits it, link falling back to the brand's canonical page.
        meta = {"title": (pin_title or derive_pin_title(text) or brand)[:100]}
        link = pin_link(brand, pin_url)
        if link:
            meta["url"] = link
        if board_id:
            meta["boardServiceId"] = board_id
        variables["input"]["metadata"] = {"pinterest": meta}

    if DRY_RUN:
        shape = (variables["input"].get("metadata") or {}).get(service) or {}
        detail = (f"title={shape.get('title')!r} url={shape.get('url')} "
                  f"board={shape.get('boardServiceId') or 'default'}"
                  if service == "pinterest" else ig_post_type(image_path))
        log(f"[{brand}] [DRY] Buffer/{service} ({detail}): {(text or '')[:60]}...")
        return True

    data, err = buffer_gql(CREATE_POST, variables)
    if err:
        log(f"[{brand}] Buffer/{service} FAIL: {err}")
        return False

    result = (data or {}).get("createPost") or {}
    kind = result.get("__typename")
    if kind != "PostActionSuccess":
        detail = result.get("message") or "no detail returned"
        code = result.get("code")
        log(f"[{brand}] Buffer/{service} FAIL: {kind or 'empty response'} - "
            f"{detail}{f' (code {code})' if code else ''}")
        return False

    post = result.get("post") or {}
    log(f"[{brand}] Buffer/{service} posted OK "
        f"(id={post.get('id', '?')} status={post.get('status', '?')} "
        f"sentAt={post.get('sentAt') or 'pending'})")
    return True


# ---------------------------------------------------------------------------
# Platform routing
#
# Pinterest is unreachable: the developer app was denied API access and the
# Buffer plan has no Pinterest channel. Rather than let 42 queued pins fail
# silently every day, route them to the channels that do work.
#
# Instagram is rate-limited on purpose. The queue holds roughly five pins a
# day; pushing all of them to a young Instagram account is a good way to get
# throttled, so the overflow goes to Bluesky only. Raise or disable the cap
# with BUFFER_IG_DAILY_CAP (0 = unlimited).
# ---------------------------------------------------------------------------

PINTEREST_FALLBACK = ["buffer_instagram", "bluesky"]
IG_DAILY_CAP = int(os.environ.get("BUFFER_IG_DAILY_CAP", "2"))
_ig_sent_today = 0


# ---------------------------------------------------------------------------
# Delivery ledger
#
# Two schedulers have historically fired at :05 (this workflow and a legacy
# n8n flow), and GitHub reruns a failed job on demand. Either can publish the
# same block twice. The ledger makes delivery idempotent: a given post is only
# ever sent once per platform, no matter how many times the tick runs.
# ---------------------------------------------------------------------------

import hashlib
import json

LEDGER = LOG_DIR / "posted.json"


def load_ledger():
    try:
        return set(json.loads(LEDGER.read_text()))
    except Exception:
        return set()


def post_key(brand, post, platform):
    digest = hashlib.sha1((post["body"] or "").encode()).hexdigest()[:10]
    date = dt.datetime.utcnow().strftime("%Y-%m-%d")
    return f"{date}|{brand}|{post['hour']:02d}|{platform}|{digest}"


def save_ledger(keys):
    # A dry run must never record a delivery, or the real post that follows
    # would be skipped as already sent.
    if DRY_RUN:
        log("[DRY] ledger not written")
        return
    # Keep the file from growing without bound; 30 days is plenty to cover
    # any realistic duplicate window.
    cutoff = (dt.datetime.utcnow() - dt.timedelta(days=30)).strftime("%Y-%m-%d")
    keep = sorted(k for k in keys if k.split("|", 1)[0] >= cutoff)
    LEDGER.write_text(json.dumps(keep, indent=0))


# TikTok is only enabled for Ora (handle @toolstack-y4g).
# Grissom Press and Family Book do not have TikTok accounts by design.
TIKTOK_ALLOWED_BRANDS = {"ora"}


def plain(text):
    """Queue bodies are markdown, but no social network renders it - the live
    Instagram test went out with literal ** around the headline. Strip the
    syntax and keep the words. Hashtags and emoji are left alone."""
    t = text or ""
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)   # images -> alt text
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 \2", t)  # links -> text + url
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.S)  # bold
    t = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", t, flags=re.S)  # underscore italic
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", t, flags=re.S)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"^\s{0,3}#{1,6}\s+", "", t, flags=re.M)  # headings, not hashtags
    t = re.sub(r"^\s{0,3}>\s?", "", t, flags=re.M)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def outcome(res, detail=""):
    """Three states, not two. None means the platform was never configured, so
    it is a skip; only an attempted-and-refused post counts as a failure."""
    if res is None:
        return "skip", (detail or "not configured")
    return ("ok" if res else "fail"), detail


def deliver(brand, post, platform):
    """Send one post to one platform. Returns (status, detail) where status is
    'ok', 'fail', or 'skip'. Every branch must return - a platform that falls
    through silently is exactly the bug this rewrite exists to kill."""
    global _ig_sent_today
    body = plain(post["body"])
    image = post.get("image")

    if platform == "bluesky":
        return outcome(post_bluesky(brand, body, image, post.get("alt")))

    if platform == "x":
        return "skip", "X is manual-only by policy"

    if platform == "linkedin":
        return outcome(post_linkedin(brand, body))

    if platform == "threads":
        return outcome(post_threads(brand, body))

    if platform == "instagram":
        # Prefer Buffer; the direct Meta Graph route needs an app review this
        # account does not have. Fall back to it only if Buffer is unconfigured.
        if buffer_token() and BUFFER_CHANNELS.get("instagram"):
            return outcome(post_buffer(brand, body, image, "instagram"), "via Buffer")
        return outcome(post_instagram(brand, body, image), "via Meta Graph")

    if platform == "buffer_instagram":
        if IG_DAILY_CAP and _ig_sent_today >= IG_DAILY_CAP:
            return "skip", f"Instagram daily cap reached ({IG_DAILY_CAP})"
        res = post_buffer(brand, body, image, "instagram")
        if res:
            _ig_sent_today += 1
        return outcome(res, "via Buffer")

    if platform in ("pinterest", "buffer_pinterest"):
        # Pinterest's own API returns 401 behind an app review this account does
        # not have, so publish through Buffer, which already carries Instagram,
        # TikTok and YouTube for this org. route() only sends the slot here when
        # a Pinterest channel actually resolves; otherwise it fans out to
        # PINTEREST_FALLBACK and this branch is never reached.
        resolved = resolve_buffer_pinterest()
        if not resolved:
            return "skip", "no Buffer Pinterest channel - rerouted"
        channel_id, board_id = resolved
        prev = BUFFER_CHANNELS.get("pinterest")
        BUFFER_CHANNELS["pinterest"] = channel_id
        try:
            res = post_buffer(brand, body, image, "pinterest",
                              pin_title=post.get("pinterest_title"),
                              pin_url=post.get("pinterest_url"),
                              board_id=board_id)
        finally:
            BUFFER_CHANNELS["pinterest"] = prev
        return outcome(res, "via Buffer")

    if platform == "tiktok":
        if brand not in TIKTOK_ALLOWED_BRANDS:
            return "skip", "TikTok disabled for this brand by policy"
        return outcome(post_tiktok(brand, body, post.get("video")))

    return "skip", f"unknown platform '{platform}'"


def route(platforms):
    """Expand the queue's declared platforms into ones that can actually
    publish today. Pinterest fans out to its fallbacks."""
    out = []
    for p in platforms:
        if p == "pinterest":
            # Only fan out when Pinterest genuinely has nowhere to go. With a
            # Buffer Pinterest channel connected the slot publishes for real,
            # and the reroute - which miscrops 2:3 pins into Instagram's 4:5 -
            # stops entirely.
            if resolve_buffer_pinterest():
                if "buffer_pinterest" not in out:
                    out.append("buffer_pinterest")
                continue
            for fb in PINTEREST_FALLBACK:
                if fb not in out:
                    out.append(fb)
        elif p not in out:
            out.append(p)
    return out


def write_summary(results, hour):
    """Surface the outcome in the Actions run summary. A green check on a run
    that published nothing is how five days of failure went unnoticed."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    ok = sum(1 for r in results if r["status"] == "ok")
    failed = [r for r in results if r["status"] == "fail"]
    skipped = [r for r in results if r["status"] == "skip"]
    lines = [
        f"## Auto-post tick - {hour:02d}:00 UTC",
        "",
        f"**{ok} published · {len(failed)} failed · {len(skipped)} skipped**",
        "",
    ]
    if results:
        lines += ["| Result | Brand | Platform | Detail | Post |",
                  "|---|---|---|---|---|"]
        icon = {"ok": "published", "fail": "FAILED", "skip": "skipped"}
        for r in results:
            preview = (r["preview"] or "").replace("|", "\\|")[:60]
            lines.append(f"| {icon[r['status']]} | {r['brand']} | {r['platform']} "
                         f"| {r['detail']} | {preview} |")
    else:
        lines.append("_Nothing was scheduled for this hour._")
    if failed:
        lines += ["", "### Failures need attention",
                  "These posts did not publish and will not be retried automatically."]
    with open(path, "a") as f:
        f.write("\n".join(lines) + "\n")


def main():
    now = dt.datetime.utcnow()
    log(f"Scheduler tick @ {now.isoformat()}Z (hour={now.hour})")
    ledger = load_ledger()
    results = []

    for brand in BRANDS:
        for p in parse_today(brand):
            if p["hour"] != now.hour:
                continue
            targets = route(p["platforms"])
            log(f"[{brand}] {p['platforms']} -> {targets}: {p['body'][:70]}...")
            for plat in targets:
                key = post_key(brand, p, plat)
                if key in ledger:
                    log(f"[{brand}] {plat} already delivered this hour - skipping")
                    continue
                try:
                    status, detail = deliver(brand, p, plat)
                except Exception as e:
                    status, detail = "fail", f"unhandled: {e}"
                    log(f"[{brand}] {plat} FAIL (unhandled): {e}")
                if status == "ok":
                    ledger.add(key)
                results.append({"brand": brand, "platform": plat, "status": status,
                                "detail": detail, "preview": p["body"][:60]})

    save_ledger(ledger)

    ok = sum(1 for r in results if r["status"] == "ok")
    failed = [r for r in results if r["status"] == "fail"]
    skipped = sum(1 for r in results if r["status"] == "skip")
    log(f"Tick complete: {ok} published, {len(failed)} failed, {skipped} skipped")
    write_summary(results, now.hour)

    if failed:
        for r in failed:
            log(f"FAILED: {r['brand']}/{r['platform']} {r['detail']}")
        # Exit non-zero so the run goes red. Silent green runs are why the
        # Pinterest outage ran for five days without anyone noticing.
        sys.exit(1)


if __name__ == "__main__":
    main()
