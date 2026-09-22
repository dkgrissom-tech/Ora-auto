#!/usr/bin/env python3
"""Build a 60-row Handy Hearts trailer queue: 30 days x 2 slots (morning/evening),
starting tomorrow. Mixes 5 hook types on rotation so the feed never feels same-y:

  1. Vibe trailer     — the master trailer (Cedar Hollow + broken porch + cover)
  2. Character POV    — Dana (librarian), Don (carpenter), Wes (best friend/vet)
  3. Trope tease      — small-town, grumpy-widower, second-chance, fix-it, slow-burn
  4. Emotional beat   — grief / found family / healing / hope quotes
  5. Countdown pull   — days-to-launch reminders that get more urgent
"""
from __future__ import annotations
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "brands" / "handyhearts"
QUEUE_CSV = BRAND_DIR / "queue.csv"

FIELDS = [
    "creative_id", "scheduled_date", "time_slot", "hook_type",
    "hook", "caption", "tags", "pinterest_title",
    "script",
    "scene1_start", "scene1_end", "scene1_prompt",
    "scene2_start", "scene2_end", "scene2_prompt",
    "scene3_start", "scene3_end", "scene3_prompt",
    "scene4_start", "scene4_end", "scene4_prompt",
    "status", "rendered_at",
]

# ---------------------------------------------------------------------------
# Reusable scene prompts
# ---------------------------------------------------------------------------
# Every scene ends with "No text, no books, no author names anywhere in the
# frame" — this is what stopped VideoGen from fabricating fake covers in test
# renders. The final scene ALWAYS closes on an empty rustic table so the real
# cover overlays cleanly.

CEDAR_HOLLOW_TOWN = (
    "Vertical shot: Cedar Hollow small Southern town at golden hour, wildflowers "
    "by a country road, wooden storefronts and covered porches, warm painterly "
    "light. No text, no books, no author names."
)
CARPENTER_HANDS = (
    "Vertical close-up: weathered blue-collar carpenter hands working with a "
    "hammer on wood on a covered porch, warm evening light, sawdust in the air. "
    "No text, no books, no author names."
)
BROKEN_PORCH = (
    "Vertical wide shot of an old wooden Southern porch in disrepair, weathered "
    "peeling paint, a broken step board and sagging railing, wildflowers "
    "growing around the base, warm golden hour light. No text, no books, no "
    "author names."
)
LIBRARY_INTERIOR = (
    "Vertical warm interior shot: small-town library with tall wooden shelves, "
    "soft afternoon light streaming through arched windows, a single reading "
    "chair by a window, wildflowers on a table. No text, no books visible on "
    "shelves, no author names."
)
COUNTRY_ROAD_TRUCK = (
    "Vertical shot: an old red pickup truck driving down a country dirt road "
    "past wildflower fields at golden hour, Cedar Hollow town sign in the "
    "distance. No text, no books, no author names."
)
PORCH_SWING_CHAIN = (
    "Vertical close-up: an empty wooden porch swing hanging crookedly from one "
    "rusted chain, sagging on an old covered porch, wildflowers growing "
    "through the floorboards. No text, no books, no author names."
)
FIREFLY_FIELD = (
    "Vertical shot: a wildflower meadow at dusk with fireflies rising, warm "
    "amber glow on the horizon, distant lights of a small town. No text, no "
    "books, no author names."
)
FRONT_PORCH_ROCKER = (
    "Vertical shot: a wooden rocking chair on a covered Southern porch at "
    "sunset, two mismatched coffee mugs on a small table, wildflowers in a "
    "mason jar. No text, no books, no author names."
)
CHURCH_STEEPLE_SUNSET = (
    "Vertical shot: a small white Southern church steeple against a burning "
    "orange sunset, wildflowers in the foreground, warm painterly light. No "
    "text, no books, no author names."
)
FIX_IT_TOOLS = (
    "Vertical close-up: a leather tool belt, hammer, and coiled measuring tape "
    "resting on weathered wooden porch boards, golden hour light. No text, no "
    "books, no author names."
)
GENERAL_STORE = (
    "Vertical shot: the porch of a small-town Southern general store, wooden "
    "clapboard, wildflowers in planters, an old bicycle leaning against a "
    "post. No text, no books, no author names."
)
FRONT_DOOR_WREATH = (
    "Vertical close-up: a weathered red front door with a wildflower wreath, "
    "warm afternoon light, chipped white paint on the porch. No text, no "
    "books, no author names."
)

# The closing "cover-drop" scene ALWAYS renders an empty table so the ffmpeg
# overlay of the real cover has clean space to land on.
EMPTY_TABLE_CLOSE = (
    "Vertical hero shot: an empty rustic wooden table surface in warm golden "
    "light, with a steaming mug of coffee to one side and dried wildflowers to "
    "the other. Leave the center of the table completely empty. No books, no "
    "text, no covers, no author names anywhere in the frame."
)

# ---------------------------------------------------------------------------
# Hook library — 60 unique creatives on rotation
# ---------------------------------------------------------------------------
# Each entry is (hook_type, hook, script). The hook goes on TikTok/Instagram
# as caption + first-line hook and doubles as the Pinterest title. The script
# is what VideoGen turns into voiceover + captions.

VIBE = "vibe"
POV = "pov"
TROPE = "trope"
BEAT = "beat"
COUNTDOWN = "countdown"

CREATIVES: list[tuple[str, str, str]] = [
    # 1 — the master vibe trailer (approved template)
    (VIBE, "Some hearts are built to be fixed.",
     "In Cedar Hollow, small hands can heal a whole town. Handy Hearts is the first book in a heartfelt new romance series about a widowed carpenter, a broken porch, and the librarian who noticed. Coming soon from D.K. Grissom."),
    (POV, "He fixes broken things. He forgot he was one of them.",
     "Meet Don. Widowed carpenter, three years in, still eating supper standing up. He fixes broken porches. He forgot he was one of them. Handy Hearts. Coming soon from D.K. Grissom."),
    (POV, "She noticed him before she noticed the porch.",
     "Meet Dana. Librarian, transplant, brand new to Cedar Hollow. She noticed him before she noticed the porch. She noticed everything. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "One busted porch. One quiet librarian. One second chance.",
     "One busted porch. One quiet librarian. One widowed carpenter who thought he was done. In Cedar Hollow, small hands can heal a whole town. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "Grief doesn't leave. But sometimes it makes room.",
     "Grief doesn't leave. But sometimes, on a warm porch in a small town, it makes room for something new. Handy Hearts. A Cedar Hollow novel. Coming soon from D.K. Grissom."),

    # 6-10
    (VIBE, "Welcome to Cedar Hollow.",
     "Welcome to Cedar Hollow. Population eight hundred and change. Home to porches that need fixing and hearts that need finding. Handy Hearts. Book One of a new small-town romance series. Coming soon from D.K. Grissom."),
    (POV, "He never talks. She's got questions.",
     "Meet Don. He never talks. Meet Dana. She's got questions. And a stack of overdue library cards. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Small town. Big secrets. One porch swing.",
     "Small town. Big secrets. One broken porch, and the woman who kept walking by. Handy Hearts. A Cedar Hollow novel. Coming soon from D.K. Grissom."),
    (BEAT, "Some love stories start with a hammer.",
     "Some love stories start with roses. This one starts with a hammer, a hurt man, and a woman who saw right through him. Handy Hearts. Coming soon from D.K. Grissom."),
    (COUNTDOWN, "The Cedar Hollow series starts soon.",
     "The Cedar Hollow series starts soon. Book One is Handy Hearts, a small-town romance about a widowed carpenter and the librarian who noticed. Coming soon from D.K. Grissom."),

    # 11-15
    (VIBE, "Where the porches sag and the hearts don't.",
     "Cedar Hollow, Tennessee. Where the porches sag and the hearts don't. Handy Hearts. Book One. Coming soon from D.K. Grissom."),
    (POV, "Wes tried to warn her. Nobody warns Dana.",
     "Meet Wes. Local vet. Don's best friend since the third grade. He tried to warn her. But nobody warns Dana. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Grumpy widower. Sunshine librarian. You know how this ends.",
     "Grumpy widower. Sunshine librarian. Small town where everybody knows. You already know how this one ends. And you're gonna love every page. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "Broken things can be beautiful, too.",
     "Broken things can be beautiful, too. That's the first thing Cedar Hollow will teach you. Handy Hearts. A Cedar Hollow novel. Coming soon from D.K. Grissom."),
    (POV, "He hadn't laughed in three years. She made him laugh in three minutes.",
     "He hadn't laughed in three years. She made him laugh in three minutes. Then she asked about the porch. Handy Hearts. Coming soon from D.K. Grissom."),

    # 16-20
    (VIBE, "Cedar Hollow is waiting.",
     "Cedar Hollow is waiting. There's a broken porch on Magnolia Street, and a librarian who just moved in across the way. Handy Hearts. Book One. Coming soon from D.K. Grissom."),
    (POV, "The librarian brought casseroles. He didn't know what to do with casseroles.",
     "The librarian brought casseroles. She brought books. She brought light. He didn't know what to do with any of it. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Second chance romance done right.",
     "Second chance romance done right. Small town. Slow burn. One carpenter who forgot how to hope, and the librarian who reminded him. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "You don't rebuild a life. You just start hammering.",
     "You don't rebuild a life all at once. You just start hammering, one board at a time. Handy Hearts. A Cedar Hollow novel. Coming soon from D.K. Grissom."),
    (COUNTDOWN, "Handy Hearts is coming.",
     "Handy Hearts is coming. The first book in a new heartfelt Southern romance series, from D.K. Grissom. Cedar Hollow. Book One. Coming soon."),

    # 21-30
    (VIBE, "There are no strangers in Cedar Hollow. Only stories.",
     "There are no strangers in Cedar Hollow. Only stories waiting to be swapped over a porch rail. Handy Hearts. Book One. Coming soon from D.K. Grissom."),
    (POV, "She read to the kids on Saturdays. He listened from the truck.",
     "She read to the kids on Saturdays at the library steps. He parked his truck across the street and pretended not to listen. Everyone knew he was listening. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Widowed hero. Small town. Big feelings.",
     "Widowed hero. Small Southern town. Big feelings and slow-burning love. If that's your shelf, Handy Hearts is your next read. Coming soon from D.K. Grissom."),
    (BEAT, "Healing looks a lot like a Saturday morning porch.",
     "Turns out healing doesn't look like a mountaintop. It looks like a Saturday morning porch, two mugs of coffee, and someone who stayed. Handy Hearts. Coming soon from D.K. Grissom."),
    (POV, "His late wife loved wildflowers. Dana didn't know that yet.",
     "Don's late wife planted wildflowers in every corner of the yard. Dana didn't know that yet. She'd learn. She always did. Handy Hearts. Coming soon from D.K. Grissom."),
    (VIBE, "One town. One porch. One hammer. One heart.",
     "One town. One busted porch. One weathered hammer. One heart that forgot how to open. Handy Hearts. Cedar Hollow, Book One. Coming soon from D.K. Grissom."),
    (POV, "Dana asked for a library card. She left with more than that.",
     "Dana walked into Cedar Hollow with a suitcase and a plan. The plan lasted about four days. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Handyman-turns-hero. Librarian who sees him first.",
     "The handyman who fixes everything but himself. The librarian who saw him first. If that's your kind of story, Handy Hearts is your next one. Coming soon from D.K. Grissom."),
    (BEAT, "Love doesn't fix you. It stands beside you while you fix yourself.",
     "Love doesn't fix you. It stands beside you on a porch in Cedar Hollow while you fix yourself, one board at a time. Handy Hearts. Coming soon from D.K. Grissom."),
    (COUNTDOWN, "The launch is close.",
     "The launch is close. Handy Hearts, Book One in the Cedar Hollow romance series, is almost here. From D.K. Grissom. Coming soon."),

    # 31-40
    (VIBE, "This is a Cedar Hollow love story.",
     "This is a Cedar Hollow love story. Slow. Warm. A little bit broken. Handy Hearts. Book One. Coming soon from D.K. Grissom."),
    (POV, "The whole town noticed before they did.",
     "The whole town noticed before they did. That's how it works in Cedar Hollow. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Slow burn. Sweet payoff. Southern porch.",
     "Slow burn. Sweet payoff. A Southern porch, a broken step, and a widowed carpenter who finally looked up. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "Some people fix houses. Some people fix each other.",
     "Some people fix houses. Some people fix each other. In Cedar Hollow, sometimes it's the same person. Handy Hearts. Coming soon from D.K. Grissom."),
    (POV, "He hadn't touched the porch swing in three years.",
     "He hadn't touched the porch swing in three years. Then Dana asked why. Handy Hearts. Coming soon from D.K. Grissom."),
    (VIBE, "Cedar Hollow. Book One. Handy Hearts.",
     "Cedar Hollow. Population eight hundred. Book One is Handy Hearts. And it starts with a broken porch. Coming soon from D.K. Grissom."),
    (POV, "The librarian brought casseroles. And a question.",
     "The librarian brought casseroles, and one question nobody in Cedar Hollow had ever asked out loud. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Emotional. Southern. Slow-burning. Yours.",
     "Emotional. Small-town. Southern. Slow-burning. If that's your shelf, this book is yours. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "Grief and hope can share a porch.",
     "Grief and hope can share a porch. That's the first thing you'll learn in Cedar Hollow. Handy Hearts. Coming soon from D.K. Grissom."),
    (COUNTDOWN, "Almost time.",
     "Almost time. Handy Hearts, the first Cedar Hollow romance from D.K. Grissom, is coming soon. Add it to your reading list."),

    # 41-50
    (VIBE, "A new small-town series is coming.",
     "A new small-town Southern romance series is coming. It starts with a widowed carpenter and a broken porch. Handy Hearts. Book One. Coming soon from D.K. Grissom."),
    (POV, "He was the strongest man she'd ever met. He never knew it.",
     "He was the strongest man Dana had ever met. He never knew it. That was the part she planned to fix. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Small-town gossip. Handyman hero. Librarian heroine.",
     "Small-town gossip. Church-potluck matchmaking. A handyman hero and the librarian who moved in across the road. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "Sometimes healing sounds like a hammer.",
     "Sometimes healing sounds like a hammer, and looks like two mugs of coffee on a Saturday porch. Handy Hearts. Coming soon from D.K. Grissom."),
    (POV, "Dana didn't come to Cedar Hollow for love. She came to disappear.",
     "Dana didn't come to Cedar Hollow for love. She came to disappear. Cedar Hollow, of course, had other plans. Handy Hearts. Coming soon from D.K. Grissom."),
    (VIBE, "Where every broken thing has a story.",
     "Cedar Hollow. Where every broken thing has a story, and every story has a porch. Handy Hearts. Book One. Coming soon from D.K. Grissom."),
    (POV, "Wes said it first. Nobody listened.",
     "Wes, the vet, saw it before anyone. He said it out loud on the porch of the general store. Nobody listened. They didn't need to. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Grumpy sunshine. Widow's hope. Southern warm.",
     "Grumpy widower. Sunshine librarian. A whole town leaning on the porch rail waiting to see what happens next. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "Your favorite next read is almost here.",
     "Your favorite next read is almost here. Small town. Slow burn. Southern warm. Handy Hearts, from D.K. Grissom. Coming soon."),
    (COUNTDOWN, "Cedar Hollow is close.",
     "Cedar Hollow is close. Handy Hearts, Book One, is almost here. From D.K. Grissom. Coming soon to Kindle and paperback."),

    # 51-60 — final stretch, more urgent
    (VIBE, "The porch is broken. The story starts here.",
     "The porch is broken. The town is waiting. The story starts here. Handy Hearts. Book One of Cedar Hollow. Coming soon from D.K. Grissom."),
    (POV, "He needed to be seen. She saw him.",
     "He needed to be seen. Not fixed. Not saved. Just seen. She saw him. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "Second chance done Southern.",
     "Second chance romance done Southern. Warm, slow, and worth the wait. Handy Hearts. Coming soon from D.K. Grissom."),
    (BEAT, "You can rebuild anything on a porch.",
     "You can rebuild anything on a porch, if you have coffee and someone who stays. Handy Hearts. Coming soon from D.K. Grissom."),
    (POV, "The town knew before he did.",
     "The town knew before he did. In Cedar Hollow, they always do. Handy Hearts. Coming soon from D.K. Grissom."),
    (VIBE, "One porch. One town. One love story.",
     "One porch. One town. One quiet love story that's been three years in the making. Handy Hearts. Coming soon from D.K. Grissom."),
    (POV, "Dana's grandmother grew wildflowers, too.",
     "Dana's grandmother grew wildflowers, just like Don's late wife. Dana didn't know that yet. But she would. Handy Hearts. Coming soon from D.K. Grissom."),
    (TROPE, "A Cedar Hollow romance.",
     "A Cedar Hollow romance. Slow-burn. Small-town. Big-hearted. Handy Hearts, from D.K. Grissom. Coming soon."),
    (BEAT, "Not every love story starts loud.",
     "Not every love story starts loud. Some start on a Saturday morning porch, with a hammer and a hello. Handy Hearts. Coming soon from D.K. Grissom."),
    (COUNTDOWN, "It's almost here.",
     "It's almost here. Handy Hearts. Book One in the Cedar Hollow romance series, from D.K. Grissom. Add it to your list. Coming soon."),
]

# ---------------------------------------------------------------------------
# Scene selector per hook type
# ---------------------------------------------------------------------------
# Every creative uses a 4-scene structure: establish → mood → theme → empty
# table (for cover overlay). The middle two scenes rotate by hook_type so a
# character POV pulls the carpenter/library scenes and a trope tease pulls
# the tool-belt/wreath scenes.

SCENE_MAPS = {
    VIBE:      [CEDAR_HOLLOW_TOWN, BROKEN_PORCH, FIREFLY_FIELD, EMPTY_TABLE_CLOSE],
    POV:       [CEDAR_HOLLOW_TOWN, CARPENTER_HANDS, LIBRARY_INTERIOR, EMPTY_TABLE_CLOSE],
    TROPE:     [CEDAR_HOLLOW_TOWN, FIX_IT_TOOLS, FRONT_PORCH_ROCKER, EMPTY_TABLE_CLOSE],
    BEAT:      [FIREFLY_FIELD, BROKEN_PORCH, FRONT_PORCH_ROCKER, EMPTY_TABLE_CLOSE],
    COUNTDOWN: [CEDAR_HOLLOW_TOWN, COUNTRY_ROAD_TRUCK, CHURCH_STEEPLE_SUNSET, EMPTY_TABLE_CLOSE],
}

TAG_MAPS = {
    VIBE:      "#BookTok #SmallTownRomance #CedarHollow #HandyHearts #DKGrissom",
    POV:       "#BookTok #Romance #CedarHollow #HandyHearts #DKGrissom #BookLovers",
    TROPE:     "#BookTok #SlowBurn #GrumpySunshine #CedarHollow #HandyHearts #DKGrissom",
    BEAT:      "#BookTok #Romance #HealingLove #CedarHollow #HandyHearts #DKGrissom",
    COUNTDOWN: "#ComingSoon #BookTok #NewRelease #CedarHollow #HandyHearts #DKGrissom",
}


def scenes_for(hook_type: str) -> list[tuple[float, float, str]]:
    prompts = SCENE_MAPS[hook_type]
    return [
        (0.0, 4.0, prompts[0]),
        (4.0, 8.0, prompts[1]),
        (8.0, 12.0, prompts[2]),
        (12.0, 17.5, prompts[3]),
    ]


def build_queue() -> list[dict]:
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
    slots = ["morning", "evening"]
    rows: list[dict] = []
    for i, (hook_type, hook, script) in enumerate(CREATIVES):
        day_offset = i // 2
        slot = slots[i % 2]
        date = tomorrow + timedelta(days=day_offset)
        cid = f"HH-D{day_offset+1:02d}-{slot[:3].upper()}"
        scenes = scenes_for(hook_type)
        row = {
            "creative_id": cid,
            "scheduled_date": date.strftime("%Y-%m-%d"),
            "time_slot": slot,
            "hook_type": hook_type,
            "hook": hook,
            "caption": hook,  # same as hook for now; can hand-edit later
            "tags": TAG_MAPS[hook_type],
            "pinterest_title": f"Handy Hearts: {hook.rstrip('.')}"[:100],
            "script": script,
            "scene1_start": scenes[0][0], "scene1_end": scenes[0][1], "scene1_prompt": scenes[0][2],
            "scene2_start": scenes[1][0], "scene2_end": scenes[1][1], "scene2_prompt": scenes[1][2],
            "scene3_start": scenes[2][0], "scene3_end": scenes[2][1], "scene3_prompt": scenes[2][2],
            "scene4_start": scenes[3][0], "scene4_end": scenes[3][1], "scene4_prompt": scenes[3][2],
            "status": "queued",
            "rendered_at": "",
        }
        rows.append(row)
    return rows


def main() -> None:
    rows = build_queue()
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    with QUEUE_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {QUEUE_CSV}")


if __name__ == "__main__":
    main()
