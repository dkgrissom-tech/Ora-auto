"""Tumblr publishing.

Tumblr is the only platform here that needs OAuth 1.0a request signing, and the
signature is hand-rolled from the standard library so auto_post.yml does not
have to install a signing library. An almost-correct signature returns the same
opaque 401 as an expired token, so the signature is pinned against a fixed
vector rather than merely exercised.

That vector was produced by oauthlib 3.x (`oauthlib.oauth1.Client.sign`) for the
inputs below and verified byte-for-byte against this implementation. The secrets
deliberately contain '&', '%20' and '~' - the three characters that break a
naive percent-encoder. oauthlib is NOT a test dependency; only its output is.

Run: DRY_RUN=true python3 tests/test_tumblr.py
"""
import os
import pathlib
import re
import sys

os.environ["DRY_RUN"] = "true"

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_scheduler as rs  # noqa: E402

LINES = []
rs.log = lambda m: (LINES.append(m), print("   ", m))[0]

CREDS = {
    "GRISSOM_TUMBLR_BLOG": "grissompress.tumblr.com",
    "GRISSOM_TUMBLR_CONSUMER_KEY": "ckey",
    "GRISSOM_TUMBLR_CONSUMER_SECRET": "csecret",
    "GRISSOM_TUMBLR_OAUTH_TOKEN": "atoken",
    "GRISSOM_TUMBLR_OAUTH_TOKEN_SECRET": "asecret",
}
IMG = "brands/grissom/assets/hh-03-tumblr-4x5.jpg"
BODY = "**Grief doesn't end.**\n\nIt changes shape.\n\n#romance"
FAILURES = []


def check(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(label)


def with_creds(**extra):
    for k, v in {**CREDS, **extra}.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def clear_creds():
    for k in CREDS:
        os.environ.pop(k, None)


# --- 1. the signature itself ------------------------------------------------
URL = "https://api.tumblr.com/v2/blog/grissompress.tumblr.com/post"
VEC_BODY = {
    "type": "photo", "state": "published", "format": "html",
    "source": f"https://raw.githubusercontent.com/dkgrissom-tech/Ora-auto/main/{IMG}",
    "caption": "<p>Grief doesn't end. It changes shape.</p>",
    "tags": "romance,small town romance",
    "link": "https://cedarhollow.pplx.app",
}
EXPECTED_SIG = "2xL%2BxwND%2FWcftGz0rKxXEsRSxIg%3D"

hdr = rs.oauth1_header("POST", URL, VEC_BODY, "ckey", "csecret&%20odd",
                       "atoken", "asecret~tilde",
                       nonce="abc123deadbeef", timestamp=1786000000)
got = re.search(r'oauth_signature="([^"]+)"', hdr).group(1)
check("signature matches the oauthlib reference vector", got == EXPECTED_SIG,
      f"got {got} want {EXPECTED_SIG}")
check("header declares HMAC-SHA1", 'oauth_signature_method="HMAC-SHA1"' in hdr)
check("header carries the token", 'oauth_token="atoken"' in hdr)
check("nonce and timestamp are sent", 'oauth_nonce="abc123deadbeef"' in hdr
      and 'oauth_timestamp="1786000000"' in hdr)
check("consumer secret never leaks into the header", "csecret" not in hdr)

# A changed body must change the signature, or the body is not really signed.
alt = rs.oauth1_header("POST", URL, {**VEC_BODY, "tags": "different"},
                       "ckey", "csecret&%20odd", "atoken", "asecret~tilde",
                       nonce="abc123deadbeef", timestamp=1786000000)
check("body parameters are inside the signature base",
      re.search(r'oauth_signature="([^"]+)"', alt).group(1) != EXPECTED_SIG)

# --- 2. caption HTML --------------------------------------------------------
cap = rs.tumblr_caption(rs.plain(BODY), "https://cedarhollow.pplx.app")
check("markdown bold is stripped, not rendered literally", "**" not in cap)
check("paragraphs become <p>", cap.count("<p>") >= 2)
check("destination link is appended as an anchor",
      '<a href="https://cedarhollow.pplx.app">' in cap)
check("html is escaped", "&" not in rs.tumblr_caption("a & b", None) or
      "&amp;" in rs.tumblr_caption("a & b", None))

# --- 3. not configured is a skip, not a failure -----------------------------
clear_creds()
check("no credentials returns None so it logs as skip",
      rs.post_tumblr("grissom", BODY, IMG) is None)
check("the skip names the missing secrets",
      any("GRISSOM_TUMBLR_CONSUMER_KEY" in ln for ln in LINES),
      "\n".join(LINES))

LINES.clear()
with_creds(GRISSOM_TUMBLR_OAUTH_TOKEN_SECRET=None)
check("one missing secret is still a skip",
      rs.post_tumblr("grissom", BODY, IMG) is None)
check("the partial-config skip names only what is missing",
      any("TUMBLR_OAUTH_TOKEN_SECRET" in ln for ln in LINES)
      and not any("CONSUMER_KEY" in ln for ln in LINES))

# --- 4. photo vs text -------------------------------------------------------
with_creds()
LINES.clear()
check("configured photo post succeeds in dry run",
      rs.post_tumblr("grissom", BODY, IMG, "romance,cedar hollow") is True)
joined = "\n".join(LINES)
check("photo posts send type=photo", "Tumblr photo" in joined, joined)
check("the image is sent as a remote source URL",
      f"src=https://raw.githubusercontent.com/dkgrissom-tech/Ora-auto/main/{IMG}" in joined,
      joined)
check("the brand default link is used when no dest_url is given",
      "link=https://cedarhollow.pplx.app" in joined, joined)

LINES.clear()
check("text-only post succeeds when there is no image",
      rs.post_tumblr("grissom", BODY, None) is True)
check("no image falls back to type=text rather than an invalid photo post",
      "Tumblr text" in "\n".join(LINES), "\n".join(LINES))

LINES.clear()
rs.post_tumblr("grissom", BODY, IMG, None, "https://grissompress.pplx.app/free-printable")
check("an explicit dest_url overrides the brand default",
      "link=https://grissompress.pplx.app/free-printable" in "\n".join(LINES))

# --- 5. wiring: dispatch + queue meta --------------------------------------
post = {"hour": 17, "body": BODY, "image": IMG, "video": None, "alt": None,
        "tags": "romance,cedar hollow", "pinterest_title": None,
        "pinterest_url": None, "platforms": ["tumblr"]}
LINES.clear()
status, detail = rs.deliver("grissom", post, "tumblr")
check("deliver() routes tumblr instead of 'unknown platform'",
      status == "ok" and "unknown platform" not in detail, f"{status} {detail}")

clear_creds()
LINES.clear()
status, detail = rs.deliver("grissom", post, "tumblr")
check("unconfigured tumblr reports skip, not fail", status == "skip",
      f"{status} {detail}")

md = """## 17:00 UTC
platforms: tumblr
image: brands/grissom/assets/hh-03-tumblr-4x5.jpg
tags: romance, cedar hollow
---
She asked for a porch repair.
"""
tmp = ROOT / "brands" / "grissom" / "posts" / "_test_tumblr.md"
tmp.write_text("# test\n\n" + md)
try:
    import datetime as dt
    real = tmp.with_name(dt.datetime.utcnow().strftime("%Y-%m-%d") + ".md")
    backup = real.read_text() if real.exists() else None
    real.write_text("# test\n\n" + md)
    parsed = rs.parse_today("grissom")
    if backup is None:
        real.unlink()
    else:
        real.write_text(backup)
finally:
    tmp.unlink(missing_ok=True)

check("parse_today reads the new tags meta key",
      bool(parsed) and parsed[0].get("tags") == "romance, cedar hollow",
      repr(parsed[:1]))
check("parse_today keeps tumblr as a platform",
      bool(parsed) and "tumblr" in parsed[0]["platforms"], repr(parsed[:1]))

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILED: " + "; ".join(FAILURES))
    sys.exit(1)
print("all tumblr tests passed")
