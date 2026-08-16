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
            # Tumblr discovery is tag-driven, so a Tumblr post with no tags is
            # nearly invisible.
            "tags": meta.get("tags"),
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
    # atproto's Client.login() calls get_profile() internally which sometimes
    # times out even when auth is valid. Retry once with a longer timeout
    # before giving up. Also log exception type since some atproto exceptions
    # stringify to empty (InvokeTimeoutError, etc.).
    last_exc = None
    for attempt in (1, 2):
        try:
            client = Client()
            # Bump the default 5s httpx timeout to 30s to survive slow profile fetches.
            try:
                client.request._client.timeout = 30.0  # type: ignore[attr-defined]
            except Exception:
                pass
            client.login(handle, password)
            if blob:
                client.send_image(text=text[:300], image=blob, image_alt=alt[:1000])
                log(f"[{brand}] Bluesky posted OK with image {image_path}")
            else:
                client.send_post(text=text[:300])
                log(f"[{brand}] Bluesky posted OK")
            return True
        except Exception as e:
            last_exc = e
            err_repr = f"{type(e).__name__}: {str(e) or repr(e)}"
            if attempt == 1:
                log(f"[{brand}] Bluesky attempt 1 failed ({err_repr}) - retrying")
                continue
            log(f"[{brand}] Bluesky FAIL: {err_repr}")
            return False
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

PINTEREST_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"

# Fresh access tokens are fetched once per brand per process. Every workflow tick
# is a fresh process, so this is a within-run cache only — it deliberately does
# NOT try to persist across runs (see the _ig_sent_today bug in docs/).
_pin_tokens = {}


def pinterest_refresh(brand):
    """Exchange the 1-year refresh token for a fresh 30-day access token.

    Pinterest v5 access tokens expire after 30 days. Returns None when refresh
    is not configured or the exchange fails, so callers fall back to the static
    PINTEREST_ACCESS_TOKEN rather than losing the slot.
    """
    import base64
    import requests
    refresh = secret(brand, "PINTEREST_REFRESH_TOKEN")
    app_id = secret(brand, "PINTEREST_APP_ID")
    app_secret = secret(brand, "PINTEREST_APP_SECRET")
    if not (refresh and app_id and app_secret):
        return None
    basic = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    try:
        r = requests.post(
            PINTEREST_TOKEN_URL,
            headers={"Authorization": f"Basic {basic}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "refresh_token", "refresh_token": refresh},
            timeout=30,
        )
        if r.status_code == 200:
            tok = (r.json() or {}).get("access_token")
            if tok:
                log(f"[{brand}] Pinterest token refreshed")
                return tok
            log(f"[{brand}] Pinterest refresh: 200 but no access_token in body")
            return None
        log(f"[{brand}] Pinterest refresh FAIL: {r.status_code} {r.text[:200]}")
        return None
    except Exception as e:
        log(f"[{brand}] Pinterest refresh FAIL: {e}")
        return None


def pinterest_token(brand):
    """Refresh-first, static-token fallback. Cached per brand for this run."""
    if brand in _pin_tokens:
        return _pin_tokens[brand]
    tok = pinterest_refresh(brand) or secret(brand, "PINTEREST_ACCESS_TOKEN")
    _pin_tokens[brand] = tok
    return tok


def pinterest_configured(brand):
    """True when either a static token or a full refresh triple is present.

    Checked before any network call so DRY_RUN never hits the token endpoint.
    """
    return bool(
        secret(brand, "PINTEREST_ACCESS_TOKEN")
        or (secret(brand, "PINTEREST_REFRESH_TOKEN")
            and secret(brand, "PINTEREST_APP_ID")
            and secret(brand, "PINTEREST_APP_SECRET"))
    )


def post_pinterest(brand, text, title, dest_url, image_path):
    import requests
    board = secret(brand, "PINTEREST_BOARD_ID")
    title = title or brand
    dest_url = dest_url or ""
    if not (pinterest_configured(brand) and board and image_path):
        log(f"[{brand}] Pinterest missing keys/image — not configured")
        return None
    if DRY_RUN:
        log(f"[{brand}] [DRY] Pinterest pin: {title}")
        return True
    token = pinterest_token(brand)
    if not token:
        log(f"[{brand}] Pinterest no usable token (refresh failed, no static fallback)")
        return False
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

# ---------------------------------------------------------------------------
# Postiz (self-hosted) — Pinterest routing
#
# Postiz is a self-hosted open-source scheduler that handles Pinterest's OAuth
# and posting on our behalf, sidestepping Pinterest v5's Trial-tier sandbox and
# Standard-access video review. One shared instance for all brands. Each brand
# selects its own Pinterest integration inside Postiz and exposes the resulting
# integration ID via {BRAND}_POSTIZ_PINTEREST_ID (e.g. GRISSOM_POSTIZ_PINTEREST_ID).
#
# Requires env:
#   POSTIZ_URL           https://postiz-v2113-production-a347.up.railway.app
#   POSTIZ_API_KEY       (from Postiz Settings > Developers > Public API)
#   {BRAND}_POSTIZ_PINTEREST_ID     Postiz integration ID for that brand's Pinterest
#   {BRAND}_POSTIZ_PINTEREST_BOARD  (optional) board slug to pin to
#
# Auth header format is `Authorization: <key>` (NO `Bearer` prefix) per Postiz docs.
# Rate limit is 90 create-post req/hr per instance.
# ---------------------------------------------------------------------------

def postiz_configured(brand):
    return bool(
        os.environ.get("POSTIZ_URL")
        and os.environ.get("POSTIZ_API_KEY")
        and secret(brand, "POSTIZ_PINTEREST_ID")
    )


def post_postiz_pinterest(brand, text, title, dest_url, image_path):
    """Publish a Pinterest pin through a self-hosted Postiz instance.

    Uploads the image to Postiz first, then submits a scheduled post with
    `type: now`. Returns True on 200/201, False on API failure, None when
    the brand isn't configured for Postiz."""
    import requests
    if not (postiz_configured(brand) and image_path):
        return None
    base = os.environ["POSTIZ_URL"].rstrip("/")
    key = os.environ["POSTIZ_API_KEY"]
    integ_id = secret(brand, "POSTIZ_PINTEREST_ID")
    board = secret(brand, "POSTIZ_PINTEREST_BOARD") or None
    title = (title or brand)[:100]
    dest_url = dest_url or ""
    if DRY_RUN:
        log(f"[{brand}] [DRY] Postiz Pinterest pin: {title}")
        return True
    try:
        img_bytes = load_asset_bytes(brand, image_path)
        if not img_bytes:
            log(f"[{brand}] Postiz: image not readable {image_path}")
            return False
        # 1) upload
        ext = os.path.splitext(image_path)[1].lower() or ".jpg"
        mime = "image/png" if ext == ".png" else "image/jpeg"
        up = requests.post(
            f"{base}/public/v1/upload",
            headers={"Authorization": key},
            files={"file": (f"pin{ext}", img_bytes, mime)},
            timeout=60,
        )
        if up.status_code not in (200, 201):
            log(f"[{brand}] Postiz upload FAIL: {up.status_code} {up.text[:200]}")
            return False
        uj = up.json()
        img_obj = {"id": uj.get("id"), "path": uj.get("path")}
        if not img_obj["id"]:
            log(f"[{brand}] Postiz upload: no id in response")
            return False
        # 2) create post
        pin_settings = {"__type": "pinterest", "title": title}
        if dest_url:
            pin_settings["link"] = dest_url
        if board:
            pin_settings["board"] = board
        body = {
            "type": "now",
            "shortLink": False,
            "tags": [],
            "posts": [{
                "integration": {"id": integ_id},
                "value": [{"content": text[:500], "image": [img_obj]}],
                "settings": pin_settings,
            }],
        }
        cp = requests.post(
            f"{base}/public/v1/posts",
            headers={"Authorization": key, "Content-Type": "application/json"},
            json=body,
            timeout=60,
        )
        if cp.status_code in (200, 201):
            log(f"[{brand}] Postiz Pinterest posted OK")
            return True
        log(f"[{brand}] Postiz Pinterest FAIL: {cp.status_code} {cp.text[:300]}")
        return False
    except Exception as e:
        log(f"[{brand}] Postiz Pinterest FAIL: {e}")
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

    # FAST PATH: If both channel ID and board service ID are pinned in env,
    # skip all lookup queries. Verified live values as of 2026-08-11 (see
    # BUFFER_GRISSOM_PINTEREST_CHANNEL_ID / _BOARD_ID GH secrets). This is
    # the bulletproof path — no org lookup, no scope requirements, just post.
    pinned_channel = (os.environ.get("BUFFER_GRISSOM_PINTEREST_CHANNEL_ID") or "").strip()
    pinned_board_service_id = (os.environ.get("BUFFER_GRISSOM_PINTEREST_BOARD_SERVICE_ID") or "").strip()
    if pinned_channel and pinned_board_service_id:
        log(f"Buffer Pinterest resolved via pinned env: channel={pinned_channel[:8]}... board={pinned_board_service_id}")
        _buffer_pinterest = (pinned_channel, pinned_board_service_id)
        return _buffer_pinterest

    want_board = (os.environ.get("BUFFER_PINTEREST_BOARD") or "").strip()
    # Discover the org ID from the token itself. Different Buffer tokens see
    # different orgs, so a hardcoded/env-provided ID may be wrong for THIS
    # token. Fall back to BUFFER_ORGANIZATION_ID env var only if discovery fails.
    org_id = ""
    # Buffer Public API tokens can't read currentOrganization (FORBIDDEN),
    # but they CAN read the organizations list. Use that.
    me_data, me_err = buffer_gql("{ account { organizations { id name } } }", {})
    if me_err:
        log(f"Buffer 'me' lookup failed: {me_err}")
    else:
        try:
            orgs = (me_data or {}).get("account", {}).get("organizations") or []
            org_id = (orgs[0].get("id") if orgs else "") or ""
            if org_id:
                log(f"Buffer org ID auto-discovered: {org_id[:8]}...")
        except Exception as e:
            log(f"Buffer org ID parse failed: {e}")
    if not org_id:
        org_id = (os.environ.get("BUFFER_ORGANIZATION_ID") or "").strip()
        if org_id:
            log(f"Falling back to env BUFFER_ORGANIZATION_ID: {org_id[:8]}...")
    if not org_id:
        log("No Buffer org ID available (auto-discovery failed, no env fallback). "
            "Verify BUFFER_ACCESS_TOKEN has 'read:account' scope.")
        return None
    data, err = buffer_gql(CHANNELS_WITH_BOARDS, {"input": {"organizationId": org_id}})
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


# Buffer's GraphQL v2 requires `channels(input: {organizationId: $orgId})`.
# The old zero-arg form returns HTTP 200 with a schema error, which is why
# Pinterest discovery was silently failing before this was added.
CHANNELS_WITH_BOARDS = """
query ChannelsWithBoards($input: ChannelsInput!) {
  channels(input: $input) {
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


BUFFER_TOKEN_CANONICAL = "BUFFER_ACCESS_TOKEN"
BUFFER_TOKEN_LEGACY = "BUFFER_ACCESS_TOKE"

_warned = set()


def warn(msg):
    """Log once per run, and surface it in the GitHub Actions run annotation.

    Plain log lines scroll past unread — the truncated Buffer secret name lived
    for a day behind a silent fallback. ::warning:: puts it on the run summary.
    """
    if msg in _warned:
        return
    _warned.add(msg)
    log(f"WARNING: {msg}")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning::{msg}", flush=True)


def buffer_token():
    """Buffer API token, canonical name first.

    The secret was originally saved under the truncated name BUFFER_ACCESS_TOKE.
    Both are accepted so a rename can never disable publishing mid-flight, but
    relying on the truncated one now warns every run. A fallback that says
    nothing is how a typo survives.
    """
    canonical = (os.environ.get(BUFFER_TOKEN_CANONICAL) or "").strip()
    legacy = (os.environ.get(BUFFER_TOKEN_LEGACY) or "").strip()
    if canonical:
        if legacy and legacy != canonical:
            warn(f"{BUFFER_TOKEN_LEGACY} is set and differs from "
                 f"{BUFFER_TOKEN_CANONICAL}. Using {BUFFER_TOKEN_CANONICAL}. "
                 f"Delete the truncated secret.")
        elif legacy:
            warn(f"{BUFFER_TOKEN_LEGACY} is redundant now that "
                 f"{BUFFER_TOKEN_CANONICAL} is set. Delete the truncated secret.")
        return canonical
    if legacy:
        warn(f"Buffer token found only under the truncated name "
             f"{BUFFER_TOKEN_LEGACY}. Add {BUFFER_TOKEN_CANONICAL} with the same "
             f"value, then delete {BUFFER_TOKEN_LEGACY}. Publishing works for now "
             f"but depends on a misspelled secret.")
        return legacy
    return ""


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


def is_reel_named_stillframe(image_path):
    """True when the asset filename says 'reel' but the extension is not a
    video type. Buffer's Instagram channel (at least the one connected here)
    rejects such posts with 'Instagram Reels require a video' even when the
    API payload sets type=post, so we skip them at delivery time with an
    actionable message instead of letting the run go red.
    """
    n = (image_path or "").lower()
    if not n or "reel" not in n:
        return False
    video_exts = (".mp4", ".mov", ".m4v", ".webm")
    return not n.endswith(video_exts)


def ig_post_type(image_path):
    """Buffer needs the post type declared. Infer it the same way the art
    pipeline does, from the filename.

    Buffer's Instagram API accepts only 'post', 'story', or 'reel' as valid
    types — NOT 'carousel'. A multi-image carousel is still type='post';
    Buffer decides it's a carousel automatically when multiple media are
    attached. Verified against error 'InvalidInputError - Invalid post:
    Instagram does not support the \'carousel\' post type' on 2026-08-12.

    Buffer also rejects type='reel' unless the attached asset is a video
    ('InvalidInputError - Invalid post: Instagram Reels require a video.'
    2026-08-11 and 2026-08-14). Reel-named still images publish just fine as
    a standard 9:16 feed post, so gate the reel type on the file extension
    and fall through to 'post' otherwise.
    """
    n = (image_path or "").lower()
    video_exts = (".mp4", ".mov", ".m4v", ".webm")
    if "reel" in n and n.endswith(video_exts):
        return "reel"
    if "story" in n and n.endswith(video_exts):
        return "story"
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

# Both routes land on the same Instagram account, so both consume the same
# daily budget and both must be counted. Only the reroute is capped, though -
# see the buffer_instagram branch in deliver().
IG_PLATFORMS = ("instagram", "buffer_instagram")

# Deliveries made earlier in *this process*. The ledger is only written once,
# at the end of main(), so within a single run it cannot see posts this run
# already made. The real count is ledger + this.
_ig_sent_this_run = 0


def ig_sent_today(ledger=None):
    """Count today's Instagram deliveries from the delivery ledger.

    This used to be a bare module-level counter, which meant it reset on every
    process start - and every cron tick is a new process, so a "daily" cap of 2
    was really a per-run cap of 2. Reading the ledger makes it genuinely daily
    across runs.
    """
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    keys = load_ledger() if ledger is None else ledger
    n = 0
    for k in keys:
        parts = k.split("|")
        if len(parts) >= 4 and parts[0] == today and parts[3] in IG_PLATFORMS:
            n += 1
    return n + _ig_sent_this_run


# ---------------------------------------------------------------------------
# Tumblr
#
# Tumblr is OAuth 1.0a only - there is no app-password or bearer-token path -
# so requests must be signed. auto_post.yml installs only `requests atproto`,
# and pulling in a signing library would make every run depend on it, so the
# signature is built from the standard library instead. Same reasoning that
# keeps PIL out of this file.
# ---------------------------------------------------------------------------

TUMBLR_API = "https://api.tumblr.com/v2"


def _oauth_quote(s):
    """RFC 3986 percent-encoding. urllib's default safe set is wrong for OAuth:
    it leaves '/' unescaped and escapes '~'."""
    import urllib.parse
    return urllib.parse.quote(str(s), safe="~")


def oauth1_header(method, url, params, consumer_key, consumer_secret,
                  token, token_secret, nonce=None, timestamp=None):
    """Build an OAuth 1.0a HMAC-SHA1 Authorization header.

    `params` must be every form-encoded body parameter plus any query
    parameters - for x-www-form-urlencoded bodies the spec folds them into the
    signature base string, and omitting them yields a 401.
    """
    import base64
    import hashlib
    import hmac
    import secrets
    import time

    oauth = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": nonce or secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(timestamp or int(time.time())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }

    # Parameters are sorted after encoding, by key then value.
    joined = "&".join(
        f"{k}={v}" for k, v in sorted(
            (_oauth_quote(k), _oauth_quote(v))
            for k, v in list(params.items()) + list(oauth.items())
        )
    )
    base = "&".join([method.upper(), _oauth_quote(url), _oauth_quote(joined)])
    signing_key = f"{_oauth_quote(consumer_secret)}&{_oauth_quote(token_secret)}"
    oauth["oauth_signature"] = base64.b64encode(
        hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()

    inner = ", ".join(f'{_oauth_quote(k)}="{_oauth_quote(v)}"'
                      for k, v in sorted(oauth.items()))
    return f"OAuth {inner}"


def tumblr_caption(text, link):
    """Tumblr renders HTML, not markdown. Turn blank-line-separated prose into
    paragraphs and append the destination link, since a post with no link
    cannot drive anything."""
    import html
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text or "") if b.strip()]
    out = ["<p>" + html.escape(b).replace("\n", "<br>") + "</p>" for b in blocks]
    if link:
        out.append(f'<p><a href="{html.escape(link)}">{html.escape(link)}</a></p>')
    return "".join(out)


def post_tumblr(brand, text, image_path=None, tags=None, dest_url=None):
    """Publish to Tumblr via the legacy /post endpoint.

    Legacy rather than NPF deliberately: type=photo accepts `source` as a remote
    image URL, so the asset rides the same public raw.githubusercontent path
    every platform except Bluesky already uses. NPF would require a multipart
    media upload for the same result.
    """
    import requests

    blog = secret(brand, "TUMBLR_BLOG")
    ck = secret(brand, "TUMBLR_CONSUMER_KEY")
    cs = secret(brand, "TUMBLR_CONSUMER_SECRET")
    tok = secret(brand, "TUMBLR_OAUTH_TOKEN")
    ts = secret(brand, "TUMBLR_OAUTH_TOKEN_SECRET")

    missing = [n for n, v in (("TUMBLR_BLOG", blog), ("TUMBLR_CONSUMER_KEY", ck),
                              ("TUMBLR_CONSUMER_SECRET", cs),
                              ("TUMBLR_OAUTH_TOKEN", tok),
                              ("TUMBLR_OAUTH_TOKEN_SECRET", ts)) if not v]
    if missing:
        log(f"[{brand}] Tumblr not configured - missing "
            f"{', '.join(f'{brand.upper()}_{m}' for m in missing)}")
        return None

    link = dest_url or pin_link(brand, None)
    body = {"state": "published", "format": "html"}
    if tags:
        body["tags"] = tags if isinstance(tags, str) else ",".join(tags)

    if image_path:
        body.update({
            "type": "photo",
            "source": asset_url(image_path),
            "caption": tumblr_caption(text, link),
        })
        if link:
            body["link"] = link
    else:
        # A photo post with no photo is rejected, so fall back to text rather
        # than sending an invalid payload.
        title = derive_pin_title(text)
        body.update({"type": "text", "body": tumblr_caption(text, link)})
        if title:
            body["title"] = title[:120]

    url = f"{TUMBLR_API}/blog/{blog}/post"

    if DRY_RUN:
        log(f"[{brand}] [DRY] Tumblr {body['type']} to {blog}"
            + (f" src={body.get('source')}" if image_path else "")
            + f" link={link or 'none'}: {(text or '')[:60]}...")
        return True

    try:
        r = requests.post(
            url, data=body, timeout=45,
            headers={"Authorization": oauth1_header("POST", url, body, ck, cs, tok, ts),
                     "Content-Type": "application/x-www-form-urlencoded"},
        )
    except Exception as e:
        log(f"[{brand}] Tumblr FAIL: transport: {e}")
        return False

    if r.status_code in (200, 201):
        try:
            pid = ((r.json() or {}).get("response") or {}).get("id_string", "?")
        except Exception:
            pid = "?"
        log(f"[{brand}] Tumblr posted OK (id={pid} blog={blog})")
        return True

    # 401 here is almost always a dead token rather than a bad signature, but
    # both look identical from outside, so say so instead of guessing.
    hint = ""
    if r.status_code == 401:
        hint = (" - the OAuth token or the signature was rejected; re-mint the "
                "token at tumblr.com/oauth/apps if it was working before")
    elif r.status_code == 404:
        hint = f" - blog '{blog}' not found; TUMBLR_BLOG wants the full host, e.g. name.tumblr.com"
    log(f"[{brand}] Tumblr FAIL: {r.status_code} {r.text[:200]}{hint}")
    return False


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


# TikTok is only enabled for Ora (handle @toolstack-y4g). Defined in
# brand_policy so the ingester enforces the same rule - it previously allowed
# grissom, which queued posts this script then skipped every single day.
from brand_policy import TIKTOK_ALLOWED_BRANDS  # noqa: E402


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
    global _ig_sent_this_run
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
        # Reels-named still image (2026-08-14 18:00 UTC failure): the block was
        # `image: handy-hearts-ig-reel-porch-scene-2026-08-14.jpg` and Buffer's
        # Instagram channel is configured Reels-only, so it rejected the post
        # even though ig_post_type() correctly returned 'post'. Rather than let
        # Buffer fail the whole run, catch the mismatch at delivery time and
        # emit a skip with a clear editorial fix (rename the asset or attach a
        # real video).
        if is_reel_named_stillframe(image):
            return "skip", (f"asset '{image}' has 'reel' in the name but is not "
                            f"a video - rename it or provide an .mp4/.mov")
        # Prefer Buffer; the direct Meta Graph route needs an app review this
        # account does not have. Fall back to it only if Buffer is unconfigured.
        if buffer_token() and BUFFER_CHANNELS.get("instagram"):
            res = post_buffer(brand, body, image, "instagram")
        else:
            res = post_instagram(brand, body, image)
        if res:
            # Counts toward today's budget even though it is never capped, so a
            # scheduled post plus reroutes cannot together overrun the account.
            _ig_sent_this_run += 1
        return outcome(res, "via Buffer" if buffer_token() else "via Meta Graph")

    if platform == "buffer_instagram":
        # See note in the 'instagram' branch above.
        if is_reel_named_stillframe(image):
            return "skip", (f"asset '{image}' has 'reel' in the name but is not "
                            f"a video - rename it or provide an .mp4/.mov")
        # Only the Pinterest reroute is capped. A post explicitly scheduled to
        # Instagram is a deliberate editorial choice and always goes; the cap
        # exists to stop rerouted pins from flooding the account.
        sent = ig_sent_today()
        if IG_DAILY_CAP and sent >= IG_DAILY_CAP:
            return "skip", (f"Instagram daily cap reached "
                            f"({sent}/{IG_DAILY_CAP} today)")
        res = post_buffer(brand, body, image, "instagram")
        if res:
            _ig_sent_this_run += 1
        return outcome(res, "via Buffer")

    if platform == "postiz_pinterest":
        # Preferred Pinterest route: self-hosted Postiz handles OAuth + posting
        # so we sidestep Pinterest v5's Trial-tier sandbox and the Standard
        # access video review. Requires POSTIZ_URL, POSTIZ_API_KEY, and the
        # per-brand {BRAND}_POSTIZ_PINTEREST_ID. route() only sends the slot
        # here when postiz_configured(brand) is True.
        return outcome(post_postiz_pinterest(
            brand, body,
            post.get("pinterest_title"),
            post.get("pinterest_url") or pin_link(brand, None),
            image,
        ), "via Postiz")

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

    if platform == "tumblr":
        return outcome(post_tumblr(brand, body, image, post.get("tags"),
                                   post.get("pinterest_url")))

    if platform == "tiktok":
        if brand not in TIKTOK_ALLOWED_BRANDS:
            return "skip", "TikTok disabled for this brand by policy"
        return outcome(post_tiktok(brand, body, post.get("video")))

    return "skip", f"unknown platform '{platform}'"


def route(platforms, brand=None):
    """Expand the queue's declared platforms into ones that can actually
    publish today. Pinterest fans out to its fallbacks.

    `brand` is required for Postiz routing (each brand has its own Pinterest
    integration ID). If not given, Postiz is skipped and we fall back to the
    old Buffer-then-reroute behavior."""
    out = []
    for p in platforms:
        if p == "pinterest":
            # Priority order:
            #   1. Postiz self-hosted (native Pinterest, our own OAuth)
            #   2. Buffer Pinterest channel (if a channel resolved)
            #   3. PINTEREST_FALLBACK (buffer_instagram, bluesky) - miscrops 2:3
            # Postiz takes precedence when configured for the brand; Buffer is
            # kept as failover so nothing breaks if Postiz is down.
            if brand and postiz_configured(brand):
                if "postiz_pinterest" not in out:
                    out.append("postiz_pinterest")
                continue
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


# How many previous UTC hours to sweep for undelivered blocks on every tick.
# GitHub Actions cron drift routinely skips a scheduled hour when the runner
# queue is busy (2026-08-15 skipped 02:xx entirely: last tick at 01:52, next
# at 03:07), which orphaned the 02:00 Grissom block forever under the old
# `hour == now.hour` filter. Sweeping the current hour plus the previous two
# gives cron up to ~2h of drift to recover from. Idempotency is enforced by
# the ledger (see post_key), so a block delivered on its own hour will not
# be re-sent on the catch-up sweep.
CATCHUP_HOURS = 2


def main():
    now = dt.datetime.utcnow()
    log(f"Scheduler tick @ {now.isoformat()}Z (hour={now.hour})")
    # Surface credential-naming problems on every tick, not only on ticks that
    # happen to have a post due. The truncated BUFFER_ACCESS_TOKE secret went
    # unnoticed because the only code that looked at it ran during publishing.
    buffer_token()
    ledger = load_ledger()
    results = []

    # Sweep the current hour and up to CATCHUP_HOURS previous hours so a
    # cron-drift gap does not silently drop posts. Same-day only: a block
    # at 23:00 missed by a tick that fires past 00:00 UTC is not recovered
    # because parse_today() reads today's file.
    eligible_hours = {(now.hour - i) % 24 for i in range(CATCHUP_HOURS + 1)}

    for brand in BRANDS:
        for p in parse_today(brand):
            if p["hour"] not in eligible_hours:
                continue
            if p["hour"] != now.hour:
                log(f"[{brand}] catching up {p['hour']:02d}:00 block on {now.hour:02d}:00 tick")
            targets = route(p["platforms"], brand=brand)
            log(f"[{brand}] {p['platforms']} -> {targets}: {p['body'][:70]}...")
            for plat in targets:
                key = post_key(brand, p, plat)
                if key in ledger:
                    log(f"[{brand}] {plat} already delivered - skipping")
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
        # Only red-X the whole run when every attempted post failed. A single
        # malformed IG draft should not kill an otherwise successful tick;
        # individual failures already log loudly and show up red in the run
        # summary table so nothing goes silent. But if we tried to publish
        # and nothing landed, exit non-zero — that is the outage signal we
        # actually want (Pinterest ran silent-green for five days before the
        # exit(1) went in on 2026-08-06).
        if ok == 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
