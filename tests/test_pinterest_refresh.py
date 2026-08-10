"""Pinterest v5 token refresh.

v5 access tokens die after 30 days. Before this there was no refresh path at all,
so the Pinterest lane went dark roughly monthly and auto_post.yml still exited 0.

The behaviour that matters:
  - a configured refresh triple produces a fresh token, and the static token is
    never used when refresh succeeds
  - a failed refresh falls back to the static token rather than losing the slot
  - DRY_RUN never touches the network
  - the refresh happens once per brand per run, not once per pin

Run: python3 tests/test_pinterest_refresh.py
"""
import base64
import os
import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

os.environ["DRY_RUN"] = "false"
import run_scheduler as rs  # noqa: E402

LINES = []
rs.log = lambda m: (LINES.append(str(m)), print("     ", m))[0]

CALLS = []
failures = []


class Resp:
    def __init__(self, code, payload=None, text=""):
        self.status_code = code
        self._payload = payload
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def install_requests(token_resp, pin_resp=Resp(201, {})):
    """Fake `requests` covering both the token endpoint and the pins endpoint."""
    mod = types.ModuleType("requests")

    def post(url, headers=None, json=None, data=None, timeout=None):
        CALLS.append({"url": url, "headers": headers or {}, "json": json, "data": data})
        if url == rs.PINTEREST_TOKEN_URL:
            if isinstance(token_resp, Exception):
                raise token_resp
            return token_resp
        return pin_resp

    mod.post = post
    sys.modules["requests"] = mod


def reset(dry=False, **env):
    CALLS.clear()
    LINES.clear()
    rs._pin_tokens.clear()
    rs.DRY_RUN = dry
    for k in list(os.environ):
        if "PINTEREST" in k:
            del os.environ[k]
    os.environ["GRISSOM_PINTEREST_BOARD_ID"] = "board123"
    for k, v in env.items():
        if v is not None:
            os.environ[f"GRISSOM_PINTEREST_{k}"] = v


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label} {detail}")
        failures.append(label)


TRIPLE = dict(REFRESH_TOKEN="r3fresh", APP_ID="app1", APP_SECRET="sh4h")
PIN = ("grissom", "body text", "Pin Title", "https://cedarhollow.pplx.app", "brands/grissom/assets/x.jpg")

# ---------------------------------------------------------------- 1. happy path
print("\n1. refresh triple present, static token also present")
reset(**TRIPLE, ACCESS_TOKEN="STALE")
install_requests(Resp(200, {"access_token": "FRESH", "expires_in": 2592000}))
res = rs.post_pinterest(*PIN)
check("returns True", res is True, res)
tok_call = [c for c in CALLS if c["url"] == rs.PINTEREST_TOKEN_URL]
pin_call = [c for c in CALLS if c["url"].endswith("/v5/pins")]
check("hit the token endpoint once", len(tok_call) == 1, len(tok_call))
check("form-encoded refresh_token grant",
      tok_call[0]["data"] == {"grant_type": "refresh_token", "refresh_token": "r3fresh"},
      tok_call[0]["data"])
expect_basic = "Basic " + base64.b64encode(b"app1:sh4h").decode()
check("Basic auth from app id/secret", tok_call[0]["headers"]["Authorization"] == expect_basic,
      tok_call[0]["headers"]["Authorization"])
check("pin used the FRESH token, not the stale one",
      pin_call[0]["headers"]["Authorization"] == "Bearer FRESH",
      pin_call[0]["headers"]["Authorization"])
check("board id still sent", pin_call[0]["json"]["board_id"] == "board123")
check("logged the refresh", any("token refreshed" in l for l in LINES))

# ------------------------------------------------- 2. refresh fails -> fallback
print("\n2. refresh returns 401, static token present")
reset(**TRIPLE, ACCESS_TOKEN="STATIC")
install_requests(Resp(401, {}, '{"message":"bad refresh"}'))
res = rs.post_pinterest(*PIN)
check("still posts", res is True, res)
pin_call = [c for c in CALLS if c["url"].endswith("/v5/pins")]
check("fell back to the static token",
      pin_call[0]["headers"]["Authorization"] == "Bearer STATIC",
      pin_call[0]["headers"]["Authorization"])
check("logged the refresh failure", any("Pinterest refresh FAIL: 401" in l for l in LINES))

# ------------------------------------- 3. refresh fails, no static -> no posting
print("\n3. refresh returns 401, no static token")
reset(**TRIPLE)
install_requests(Resp(401, {}, "nope"))
res = rs.post_pinterest(*PIN)
check("returns False, not None", res is False, res)
check("never called the pins endpoint",
      not [c for c in CALLS if c["url"].endswith("/v5/pins")])
check("logged no-usable-token", any("no usable token" in l for l in LINES))

# ----------------------------------------------------- 4. transport blows up
print("\n4. token endpoint raises")
reset(**TRIPLE, ACCESS_TOKEN="STATIC")
install_requests(RuntimeError("connection reset"))
res = rs.post_pinterest(*PIN)
check("exception is caught and we fall back", res is True, res)
check("logged the exception", any("connection reset" in l for l in LINES))

# ------------------------------------------- 5. 200 but malformed body
print("\n5. token endpoint returns 200 with no access_token")
reset(**TRIPLE, ACCESS_TOKEN="STATIC")
install_requests(Resp(200, {"expires_in": 100}))
res = rs.post_pinterest(*PIN)
check("falls back to static", res is True, res)
pin_call = [c for c in CALLS if c["url"].endswith("/v5/pins")]
check("used static", pin_call[0]["headers"]["Authorization"] == "Bearer STATIC")
check("logged the malformed body", any("no access_token" in l for l in LINES))

# --------------------------------- 6. no refresh configured -> legacy behaviour
print("\n6. no refresh triple, static token only (today's config)")
reset(ACCESS_TOKEN="STATIC")
install_requests(Resp(200, {"access_token": "FRESH"}))
res = rs.post_pinterest(*PIN)
check("posts", res is True, res)
check("token endpoint never touched",
      not [c for c in CALLS if c["url"] == rs.PINTEREST_TOKEN_URL])
pin_call = [c for c in CALLS if c["url"].endswith("/v5/pins")]
check("used the static token", pin_call[0]["headers"]["Authorization"] == "Bearer STATIC")

# ------------------------------- 7. partial triple is not "configured" for auth
print("\n7. refresh token but no app secret, and no static token")
reset(REFRESH_TOKEN="r3fresh", APP_ID="app1")
install_requests(Resp(200, {"access_token": "FRESH"}))
res = rs.post_pinterest(*PIN)
check("returns None (not configured), no network", res is None, res)
check("nothing was called", not CALLS, CALLS)
check("logged not-configured", any("not configured" in l for l in LINES))

# ------------------------------------- 8. refresh triple alone IS enough
print("\n8. refresh triple with no static token at all")
reset(**TRIPLE)
install_requests(Resp(200, {"access_token": "FRESH"}))
res = rs.post_pinterest(*PIN)
check("posts using only the refreshed token", res is True, res)
pin_call = [c for c in CALLS if c["url"].endswith("/v5/pins")]
check("bearer FRESH", pin_call[0]["headers"]["Authorization"] == "Bearer FRESH")

# ---------------------------------------------------------- 9. DRY_RUN is inert
print("\n9. DRY_RUN never touches the network")
reset(dry=True, **TRIPLE, ACCESS_TOKEN="STATIC")
install_requests(Resp(200, {"access_token": "FRESH"}))
res = rs.post_pinterest(*PIN)
check("returns True", res is True, res)
check("zero HTTP calls", not CALLS, CALLS)

# ------------------------------------------- 10. one refresh per brand per run
print("\n10. five pins in one run cause one refresh")
reset(**TRIPLE)
install_requests(Resp(200, {"access_token": "FRESH"}))
for _ in range(5):
    rs.post_pinterest(*PIN)
tok_call = [c for c in CALLS if c["url"] == rs.PINTEREST_TOKEN_URL]
pin_call = [c for c in CALLS if c["url"].endswith("/v5/pins")]
check("5 pins sent", len(pin_call) == 5, len(pin_call))
check("but only 1 token exchange", len(tok_call) == 1, len(tok_call))

# --------------------------------- 11. missing board is still a hard skip
print("\n11. refresh configured but no board id")
reset(**TRIPLE)
del os.environ["GRISSOM_PINTEREST_BOARD_ID"]
install_requests(Resp(200, {"access_token": "FRESH"}))
res = rs.post_pinterest(*PIN)
check("returns None", res is None, res)
check("no network", not CALLS, CALLS)

print("\n" + "=" * 60)
if failures:
    print(f"{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("all pinterest refresh checks passed")
