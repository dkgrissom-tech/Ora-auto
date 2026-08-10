"""Pinterest via Buffer.

Pinterest's own API 401s behind an app review this account does not have, so
pins publish through Buffer instead. The behaviour that matters: when a Buffer
Pinterest channel exists the slot publishes for real, and when it does not the
old fan-out to Instagram/Bluesky still happens rather than the post vanishing.

Run: DRY_RUN=true python3 tests/test_buffer_pinterest.py
"""
import os
import sys
import pathlib

os.environ["DRY_RUN"] = "true"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_scheduler as rs  # noqa: E402

LINES = []
rs.log = lambda m: (LINES.append(str(m)), print("     ", m))[0]

CHANNEL = {
    "id": "6b0000000000000000000001",
    "name": "Grissom Press",
    "service": "pinterest",
    "isDisconnected": False,
    "metadata": {"boards": [
        {"id": "b1", "name": "Cozy Goth Coloring", "serviceId": "9111111111"},
        {"id": "b2", "name": "Handy Hearts", "serviceId": "9222222222"},
    ]},
}

SENT = []
failures = []


def fake_gql(channels):
    def _g(query, variables, attempts=4):
        if "ChannelsWithBoards" in query:
            return {"channels": channels}, None
        SENT.append(variables["input"])
        return {"createPost": {"__typename": "PostActionSuccess",
                               "post": {"id": "p1", "status": "sent", "sentAt": "now"}}}, None
    return _g


def reset(channels, token="tok", **env):
    rs._buffer_pinterest = "unresolved"
    rs.buffer_token = lambda: token
    rs.buffer_gql = fake_gql(channels)
    for k in ("BUFFER_CHANNEL_PINTEREST", "BUFFER_PINTEREST_BOARD"):
        os.environ.pop(k, None)
    os.environ.update(env)
    LINES.clear()
    SENT.clear()


POST = {
    "body": "**Sawdust and silence.** A man with a toolbox and no small talk.",
    "image": "brands/grissom/assets/hh-pin-aug11-don-pin2-sawdust-and-silence-2026-08-11.jpg",
    "platforms": ["pinterest"],
    "pinterest_title": None,
    "pinterest_url": None,
}

# 1. Channel connected: the slot routes to Pinterest, not to the fallbacks.
print("\n1. Pinterest channel connected")
reset([CHANNEL])
routed = rs.route(["pinterest"])
print("      routed ->", routed)
if routed != ["buffer_pinterest"]:
    failures.append(f"1: expected ['buffer_pinterest'], got {routed}")

status, detail = rs.deliver("grissom", POST, "buffer_pinterest")
print(f"      deliver -> {status} ({detail})")
if status != "ok":
    failures.append(f"1: deliver returned {status} {detail}")

# 2. Dry run must not have hit createPost, but metadata must still be built.
print("\n2. metadata shape")
reset([CHANNEL])
rs.DRY_RUN = False
rs.deliver("grissom", POST, "buffer_pinterest")
rs.DRY_RUN = True
if not SENT:
    failures.append("2: no createPost input was built")
else:
    inp = SENT[0]
    meta = (inp.get("metadata") or {}).get("pinterest") or {}
    print("      channelId      ", inp.get("channelId"))
    print("      title          ", repr(meta.get("title")))
    print("      url            ", meta.get("url"))
    print("      boardServiceId ", meta.get("boardServiceId"))
    print("      asset          ", (inp.get("assets") or [{}])[0].get("image", {}).get("url", "")[-46:])
    if inp.get("channelId") != CHANNEL["id"]:
        failures.append("2: wrong channelId")
    # Only these three fields exist on PinterestPostMetadataInput.
    extra = set(meta) - {"title", "url", "boardServiceId"}
    if extra:
        failures.append(f"2: fields not in the Buffer schema: {extra}")
    if not meta.get("title"):
        failures.append("2: pin has no title")
    if "**" in (meta.get("title") or ""):
        failures.append("2: markdown leaked into the pin title")
    if meta.get("url") != "https://cedarhollow.pplx.app":
        failures.append(f"2: expected the brand fallback link, got {meta.get('url')}")
    if meta.get("boardServiceId") != "9111111111":
        failures.append("2: did not default to the first board")

# 3. An explicit board name is honoured.
print("\n3. BUFFER_PINTEREST_BOARD='Handy Hearts'")
reset([CHANNEL], BUFFER_PINTEREST_BOARD="Handy Hearts")
rs.DRY_RUN = False
rs.deliver("grissom", POST, "buffer_pinterest")
rs.DRY_RUN = True
got = ((SENT[0].get("metadata") or {}).get("pinterest") or {}).get("boardServiceId")
print("      boardServiceId ", got)
if got != "9222222222":
    failures.append(f"3: board override ignored, got {got}")

# 4. Queue-supplied title and url win over the derived ones.
print("\n4. queue supplies title + url")
reset([CHANNEL])
rs.DRY_RUN = False
rs.deliver("grissom", dict(POST, pinterest_title="Handy Hearts - Sept 8",
                           pinterest_url="https://cedarhollow.pplx.app/porch-before"),
           "buffer_pinterest")
rs.DRY_RUN = True
meta = (SENT[0].get("metadata") or {}).get("pinterest") or {}
print("      title", repr(meta.get("title")), "url", meta.get("url"))
if meta.get("title") != "Handy Hearts - Sept 8":
    failures.append("4: queue title ignored")
if meta.get("url") != "https://cedarhollow.pplx.app/porch-before":
    failures.append("4: queue url ignored")

# 5. No Pinterest channel: the old fan-out must still happen.
print("\n5. no Pinterest channel in Buffer")
reset([{"id": "x", "name": "ig", "service": "instagram", "isDisconnected": False,
        "metadata": {}}])
routed = rs.route(["pinterest"])
print("      routed ->", routed)
if routed != rs.PINTEREST_FALLBACK:
    failures.append(f"5: expected fallback {rs.PINTEREST_FALLBACK}, got {routed}")
if not any("no Pinterest channel connected" in l for l in LINES):
    failures.append("5: did not explain why it rerouted")

# 6. No Buffer token at all: must not crash, must reroute.
print("\n6. no Buffer token")
reset([CHANNEL], token="")
routed = rs.route(["pinterest"])
print("      routed ->", routed)
if routed != rs.PINTEREST_FALLBACK:
    failures.append(f"6: expected fallback, got {routed}")

# 7. Channel present but disconnected: reroute rather than fail every pin.
print("\n7. channel disconnected")
reset([dict(CHANNEL, isDisconnected=True)])
routed = rs.route(["pinterest"])
print("      routed ->", routed)
if routed != rs.PINTEREST_FALLBACK:
    failures.append(f"7: expected fallback, got {routed}")
if not any("disconnected" in l for l in LINES):
    failures.append("7: did not say the channel was disconnected")

# 8. A pin with no image must not be sent - Pinterest rejects it.
print("\n8. pin with no image")
reset([CHANNEL])
status, detail = rs.deliver("grissom", dict(POST, image=None), "buffer_pinterest")
print(f"      deliver -> {status} ({detail})")
if status != "skip":
    failures.append(f"8: expected skip for a media-less pin, got {status}")

print()
if failures:
    for f in failures:
        print("FAIL", f)
    sys.exit(1)
print("all buffer pinterest tests passed")
