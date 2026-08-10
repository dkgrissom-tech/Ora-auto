"""Bluesky image attachment.

Bluesky is the only platform here that uploads image bytes as a blob rather than
taking an asset_url(), and its PDS rejects blobs over ~976KB. These tests cover
the three branches that decide whether an image rides along.

Run: DRY_RUN=true python3 tests/test_bluesky_image.py
"""
import os
import sys
import pathlib

os.environ["DRY_RUN"] = "true"
os.environ["GRISSOM_BLUESKY_HANDLE"] = "grissompress.bsky.social"
os.environ["GRISSOM_BLUESKY_APP_PASSWORD"] = "test-test-test-test"

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_scheduler as rs  # noqa: E402

LINES = []
rs.log = lambda m: (LINES.append(m), print("   ", m))[0]


def run(label, **kwargs):
    LINES.clear()
    print(f"\n{label}")
    ok = rs.post_bluesky("grissom", "She asked for a porch repair.", **kwargs)
    assert ok is True, f"{label}: expected a successful dry-run post"
    return "\n".join(LINES)


failures = []

# 1. A real committed asset, comfortably under the blob limit.
asset = "brands/grissom/assets/hh-02-bluesky-4x5.jpg"
size = (ROOT / asset).stat().st_size
out = run(f"1. real asset ({size}B)", image_path=asset, alt_text="Two hands on a weathered door.")
if f"with image {asset}" not in out:
    failures.append("1: image was not attached")
if "unavailable" in out or "blob limit" in out:
    failures.append("1: asset was wrongly rejected")

# 2. A path that does not exist anywhere - must degrade to text, not crash.
out = run("2. missing asset", image_path="brands/grissom/assets/does-not-exist.jpg")
if "unavailable - posting text only" not in out:
    failures.append("2: missing asset did not degrade to text")

# 3. Oversized asset - must be refused before upload, with the size named.
big = ROOT / "tests" / "_oversized.bin"
big.write_bytes(b"\xff" * (rs.BLUESKY_BLOB_LIMIT + 1))
try:
    out = run(f"3. oversized ({big.stat().st_size}B)", image_path="tests/_oversized.bin")
    if "over the" not in out or "blob limit" not in out:
        failures.append("3: oversized asset was not refused")
finally:
    big.unlink()

# 4. No image at all - the original text-only behaviour must be untouched.
out = run("4. text only")
if "with image" in out:
    failures.append("4: text-only post claimed an image")

# 5. Alt text is derived when the queue entry omits it.
out = run("5. alt omitted", image_path=asset)
if "alt text derived from body" not in out:
    failures.append("5: missing alt text was not flagged")

print()
if failures:
    for f in failures:
        print("FAIL", f)
    sys.exit(1)
print("all bluesky image tests passed")
