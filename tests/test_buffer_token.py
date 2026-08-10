"""Buffer token name resolution.

The secret lives in GitHub under the truncated name BUFFER_ACCESS_TOKE. Publishing
worked anyway because buffer_token() silently fell back to it — which is exactly
why nobody noticed. The canonical name now wins and the legacy name warns.

Run: python3 tests/test_buffer_token.py
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

os.environ["DRY_RUN"] = "true"
import run_scheduler as rs  # noqa: E402

LINES = []
rs.log = lambda m: LINES.append(str(m))

failures = []
PRINTED = []
_real_print = print


def capture_print(*a, **k):
    PRINTED.append(" ".join(str(x) for x in a))


def reset(canonical=None, legacy=None, actions=False):
    LINES.clear()
    PRINTED.clear()
    rs._warned.clear()
    for k in (rs.BUFFER_TOKEN_CANONICAL, rs.BUFFER_TOKEN_LEGACY, "GITHUB_ACTIONS"):
        os.environ.pop(k, None)
    if canonical is not None:
        os.environ[rs.BUFFER_TOKEN_CANONICAL] = canonical
    if legacy is not None:
        os.environ[rs.BUFFER_TOKEN_LEGACY] = legacy
    if actions:
        os.environ["GITHUB_ACTIONS"] = "true"


def check(label, cond, detail=""):
    if cond:
        _real_print(f"  ok   {label}")
    else:
        _real_print(f"  FAIL {label} {detail}")
        failures.append(label)


def warned(fragment):
    return any(fragment in l for l in LINES)


# ------------------------------------------------- 1. today's actual repo state
_real_print("\n1. only the truncated name is set (the repo's state right now)")
reset(legacy="tok-legacy")
tok = rs.buffer_token()
check("still returns the token — publishing does not break", tok == "tok-legacy", tok)
check("warns about the truncated name", warned("truncated name BUFFER_ACCESS_TOKE"))
check("names the remediation", warned("Add BUFFER_ACCESS_TOKEN with the same"))

# ----------------------------------------------------- 2. after Don's paste
_real_print("\n2. both set to the same value (mid-rename)")
reset(canonical="tok", legacy="tok")
tok = rs.buffer_token()
check("prefers the canonical name", tok == "tok", tok)
check("says the legacy secret is now redundant", warned("is redundant now that"))
check("does not emit the not-configured warning", not warned("only under the truncated"))

# --------------------------------------------------------- 3. rename complete
_real_print("\n3. only the canonical name is set (the end state)")
reset(canonical="tok")
tok = rs.buffer_token()
check("returns the token", tok == "tok", tok)
check("completely silent", not LINES, LINES)

# ---------------------------------------------------- 4. the dangerous case
_real_print("\n4. both set but DIFFERENT values")
reset(canonical="new", legacy="stale")
tok = rs.buffer_token()
check("canonical wins", tok == "new", tok)
check("warns that they differ", warned("is set and differs from"))

# ------------------------------------------------------------ 5. neither set
_real_print("\n5. neither set")
reset()
tok = rs.buffer_token()
check("empty string, not None", tok == "", repr(tok))
check("no warning — absent Buffer is a valid config", not LINES, LINES)

# --------------------------------------------- 6. whitespace is still stripped
_real_print("\n6. whitespace around the value")
reset(canonical="  tok\n")
check("stripped", rs.buffer_token() == "tok", repr(rs.buffer_token()))
reset(legacy="\ttok  ")
check("stripped on the legacy path too", rs.buffer_token() == "tok")

# ----------------------------------------- 7. blank canonical falls through
_real_print("\n7. canonical present but empty (an unset GitHub secret)")
reset(canonical="", legacy="tok-legacy")
tok = rs.buffer_token()
check("falls through to legacy", tok == "tok-legacy", tok)
check("and still warns", warned("truncated name"))

# ------------------------------------------- 8. Actions annotation is emitted
_real_print("\n8. inside GitHub Actions, emits a ::warning:: annotation")
reset(legacy="tok-legacy", actions=True)
import builtins  # noqa: E402
builtins.print = capture_print
try:
    rs.buffer_token()
finally:
    builtins.print = _real_print
check("annotation emitted", any(p.startswith("::warning::") for p in PRINTED), PRINTED)
check("annotation names the secret",
      any("BUFFER_ACCESS_TOKEN" in p for p in PRINTED), PRINTED)

_real_print("\n9. outside Actions, no annotation")
reset(legacy="tok-legacy")
builtins.print = capture_print
try:
    rs.buffer_token()
finally:
    builtins.print = _real_print
check("no ::warning:: line", not [p for p in PRINTED if p.startswith("::warning::")], PRINTED)

# ------------------------------------------------- 10. warn only fires once
_real_print("\n10. six callers in one run produce one warning")
reset(legacy="tok-legacy")
for _ in range(6):
    rs.buffer_token()
check("exactly one warning line", len(LINES) == 1, LINES)

_real_print("\n" + "=" * 60)
if failures:
    _real_print(f"{len(failures)} FAILED: {failures}")
    sys.exit(1)
_real_print("all buffer token name checks passed")
