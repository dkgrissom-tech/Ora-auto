"""
Token health checker — runs weekly (Sundays 8am CT via token_health.yml).

For each brand × platform combination that has an expiring token, this
script opens a GitHub Issue with the days-remaining and refresh steps.
If an issue already exists for that brand/platform, it updates it instead
of opening a duplicate.

Platforms checked:
  - Meta long-lived token (Instagram + Threads share one token per brand)
  - Pinterest refresh token (expiry tracked via logs/token_created.json)

Platforms intentionally skipped:
  - Bluesky (app passwords — no expiry)
  - Buffer access token (no expiry unless revoked)
  - MailerLite API key (no expiry)
  - LinkedIn (disabled, Path C decision)

Environment variables required:
  ORA_META_LONG_TOKEN, ORA_META_APP_ID, ORA_META_APP_SECRET
  GRISSOM_META_LONG_TOKEN, GRISSOM_META_APP_ID, GRISSOM_META_APP_SECRET
  FAMILYBOOK_META_LONG_TOKEN, FAMILYBOOK_META_APP_ID, FAMILYBOOK_META_APP_SECRET
  GH_TOKEN  (provided automatically by GitHub Actions as secrets.GITHUB_TOKEN)
"""
import os
import sys
import json
import datetime as dt
import urllib.request
import urllib.parse
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

TOKEN_CREATED_PATH = LOG_DIR / "token_created.json"

WARN_DAYS = 10          # open an issue when this many days or fewer remain
PINTEREST_TOKEN_LIFETIME_DAYS = 60  # Pinterest refresh tokens last 60 days

BRANDS = ["ora", "grissom", "familybook"]

# GitHub repo in "owner/repo" form — derived from GITHUB_REPOSITORY env var
# that Actions always sets. Falls back to the known value for local testing.
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "dkgrissom-tech/Ora-auto")
GH_TOKEN = os.environ.get("GH_TOKEN", "")
GH_API = "https://api.github.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def secret(brand, key):
    """Read a brand-prefixed env var: secret('ora', 'META_LONG_TOKEN') → ORA_META_LONG_TOKEN."""
    return os.environ.get(f"{brand.upper()}_{key}", "").strip()


def gh_request(method, path, payload=None):
    """Make a GitHub API request. Returns (status_code, response_dict)."""
    url = f"{GH_API}{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.getcode(), json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[token-health] GitHub API {method} {path} → {e.code}: {body[:200]}")
        return e.code, {}
    except Exception as e:
        print(f"[token-health] GitHub API error: {e}")
        return 0, {}


def load_token_created():
    """Load the token-creation timestamp log (used for Pinterest expiry tracking)."""
    if not TOKEN_CREATED_PATH.exists():
        return {}
    try:
        return json.loads(TOKEN_CREATED_PATH.read_text())
    except Exception:
        return {}


def save_token_created(data):
    """Persist token-creation timestamps."""
    try:
        TOKEN_CREATED_PATH.write_text(json.dumps(data, indent=2))
    except Exception as e:
        print(f"[token-health] could not write token_created.json: {e}")


# ---------------------------------------------------------------------------
# Platform-specific expiry checkers
# ---------------------------------------------------------------------------

def check_meta_token(brand):
    """Query Meta debug_token endpoint. Returns days_remaining or None on error.

    Uses the graph.facebook.com/debug_token endpoint which works for both
    Meta long-lived tokens (used for Instagram Graph API) and is also the
    canonical way to check Threads tokens (same token, same endpoint).
    """
    token = secret(brand, "META_LONG_TOKEN")
    app_id = secret(brand, "META_APP_ID")
    app_secret = secret(brand, "META_APP_SECRET")

    if not token:
        print(f"[token-health] {brand}/meta: META_LONG_TOKEN not set — skipping")
        return None
    if not (app_id and app_secret):
        print(f"[token-health] {brand}/meta: META_APP_ID/SECRET not set — skipping")
        return None

    access_token = f"{app_id}|{app_secret}"
    params = urllib.parse.urlencode({
        "input_token": token,
        "access_token": access_token,
    })
    url = f"https://graph.facebook.com/debug_token?{params}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"[token-health] {brand}/meta: debug_token request failed: {e}")
        return None

    inner = data.get("data", {})
    if not inner.get("is_valid"):
        error = inner.get("error", {})
        print(f"[token-health] {brand}/meta: token is INVALID — {error.get('message', 'no detail')}")
        return 0  # expired/invalid → 0 days → always opens an issue

    expires_at = inner.get("expires_at", 0)
    if not expires_at:
        # Token has no expiry (developer token or mis-issued) — treat as long-lived
        print(f"[token-health] {brand}/meta: no expiry returned (may be long-lived or developer token)")
        return None

    expiry = dt.datetime.fromtimestamp(expires_at, tz=dt.timezone.utc)
    now = dt.datetime.now(dt.timezone.utc)
    days = (expiry - now).days
    print(f"[token-health] {brand}/meta: expires {expiry.date()} ({days} days)")
    return days


def check_pinterest_token(brand, token_created_data):
    """Estimate Pinterest refresh-token expiry from creation timestamp.

    Pinterest has no introspection endpoint for refresh tokens. We track when
    the secret was last rotated in logs/token_created.json. First-run: assume
    token was created today (60 days until expiry) and log the assumption.
    """
    refresh = secret(brand, "PINTEREST_REFRESH_TOKEN")
    if not refresh:
        print(f"[token-health] {brand}/pinterest: PINTEREST_REFRESH_TOKEN not set — skipping")
        return None, token_created_data

    key = f"{brand}/pinterest_refresh"
    if key not in token_created_data:
        # First run — record today as the assumed creation date.
        today = dt.datetime.now(dt.timezone.utc).isoformat()
        token_created_data[key] = today
        print(f"[token-health] {brand}/pinterest: first run — assuming token created today, 60 days to expiry")
        return PINTEREST_TOKEN_LIFETIME_DAYS, token_created_data

    created_str = token_created_data[key]
    try:
        created = dt.datetime.fromisoformat(created_str.rstrip("Z")).replace(
            tzinfo=dt.timezone.utc
        )
    except ValueError:
        print(f"[token-health] {brand}/pinterest: bad timestamp in token_created.json — resetting")
        token_created_data[key] = dt.datetime.now(dt.timezone.utc).isoformat()
        return PINTEREST_TOKEN_LIFETIME_DAYS, token_created_data

    expiry = created + dt.timedelta(days=PINTEREST_TOKEN_LIFETIME_DAYS)
    days = (expiry - dt.datetime.now(dt.timezone.utc)).days
    print(f"[token-health] {brand}/pinterest: estimated expiry {expiry.date()} ({days} days)")
    return days, token_created_data


# ---------------------------------------------------------------------------
# GitHub Issue management
# ---------------------------------------------------------------------------

ISSUE_LABEL = "token-expiry"

def ensure_label():
    """Create the token-expiry label if it doesn't exist yet."""
    status, _ = gh_request("GET", f"/repos/{GITHUB_REPO}/labels/{ISSUE_LABEL}")
    if status == 404:
        gh_request("POST", f"/repos/{GITHUB_REPO}/labels", {
            "name": ISSUE_LABEL,
            "color": "e4e669",
            "description": "Token expiry warning — action required",
        })


def find_open_issue(brand, platform):
    """Return the issue number if an open token-expiry issue exists for brand/platform."""
    title_prefix = f"[TOKEN] {brand}/{platform}"
    status, data = gh_request(
        "GET",
        f"/repos/{GITHUB_REPO}/issues?state=open&labels={ISSUE_LABEL}&per_page=50",
    )
    if status != 200:
        return None
    for issue in data:
        if isinstance(issue, dict) and issue.get("title", "").startswith(title_prefix):
            return issue["number"]
    return None


def refresh_steps(brand, platform, days, expiry_date):
    """Return the body text for a token-expiry issue."""
    secret_names = {
        "meta": [
            f"{brand.upper()}_META_LONG_TOKEN",
            f"{brand.upper()}_META_APP_ID",
            f"{brand.upper()}_META_APP_SECRET",
        ],
        "pinterest": [
            f"{brand.upper()}_PINTEREST_REFRESH_TOKEN",
            f"{brand.upper()}_PINTEREST_APP_ID",
            f"{brand.upper()}_PINTEREST_APP_SECRET",
        ],
    }

    refresh_instructions = {
        "meta": (
            "1. Go to [Meta for Developers](https://developers.facebook.com/) → "
            "your app → Tools → Graph API Explorer.\n"
            "2. Generate a new long-lived user token (60-day expiry).\n"
            "3. Extend it: `GET /oauth/access_token?grant_type=fb_exchange_token&...`\n"
            "4. Copy the new token value."
        ),
        "pinterest": (
            "1. Go to [Pinterest Developer Portal](https://developers.pinterest.com/).\n"
            "2. Open your app → Authorization → OAuth 2.0 flow to obtain a new refresh token.\n"
            "3. Note the new creation date so the health check resets its 60-day clock.\n"
            "4. Copy the new refresh token value."
        ),
    }

    secrets_list = "\n".join(f"- `{s}`" for s in secret_names.get(platform, []))
    steps = refresh_instructions.get(platform, "See docs/gates/ for platform-specific steps.")

    expiry_str = expiry_date.strftime("%Y-%m-%d") if expiry_date else "unknown"
    days_str = f"{days} day{'s' if days != 1 else ''}" if days > 0 else "**EXPIRED**"

    return f"""Token: {brand}/{platform}
Expires in: {days_str} ({expiry_str} UTC)

## Refresh steps
{steps}

## After refresh
Update these secrets in **Settings → Secrets and variables → Actions → New repository secret**:
{secrets_list}

Close this issue after the secrets are updated and the next `token_health` workflow run confirms >10 days remaining.
"""


def open_or_update_issue(brand, platform, days, expiry_date):
    """Open a new issue or update the body of an existing open issue."""
    title = f"[TOKEN] {brand}/{platform} expires in {days} day{'s' if days != 1 else ''}"
    body = refresh_steps(brand, platform, days, expiry_date)

    existing = find_open_issue(brand, platform)
    if existing:
        status, _ = gh_request("PATCH", f"/repos/{GITHUB_REPO}/issues/{existing}", {
            "title": title,
            "body": body,
        })
        if status in (200, 201):
            print(f"[token-health] Updated existing issue #{existing}: {title}")
        else:
            print(f"[token-health] Failed to update issue #{existing} (HTTP {status})")
    else:
        status, resp = gh_request("POST", f"/repos/{GITHUB_REPO}/issues", {
            "title": title,
            "body": body,
            "labels": [ISSUE_LABEL],
        })
        if status in (200, 201):
            print(f"[token-health] Opened issue #{resp.get('number')}: {title}")
        else:
            print(f"[token-health] Failed to open issue (HTTP {status})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not GH_TOKEN:
        print("[token-health] ERROR: GH_TOKEN not set — cannot create/update GitHub Issues")
        sys.exit(1)

    ensure_label()

    token_created_data = load_token_created()
    now = dt.datetime.now(dt.timezone.utc)
    any_warning = False

    for brand in BRANDS:
        # --- Meta (Instagram + Threads share one token) ---
        days = check_meta_token(brand)
        if days is not None and days <= WARN_DAYS:
            expiry = now + dt.timedelta(days=days) if days > 0 else now
            open_or_update_issue(brand, "meta", days, expiry)
            any_warning = True

        # --- Pinterest refresh token ---
        days_pin, token_created_data = check_pinterest_token(brand, token_created_data)
        if days_pin is not None and days_pin <= WARN_DAYS:
            expiry_pin = now + dt.timedelta(days=days_pin) if days_pin > 0 else now
            open_or_update_issue(brand, "pinterest", days_pin, expiry_pin)
            any_warning = True

    # Persist any first-run Pinterest timestamps
    save_token_created(token_created_data)

    if any_warning:
        print("[token-health] ⚠️  One or more tokens expire within the warning window — issues opened/updated.")
    else:
        print("[token-health] ✅ All checked tokens have >10 days remaining — no issues opened.")


if __name__ == "__main__":
    main()
