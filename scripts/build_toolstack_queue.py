#!/usr/bin/env python3
"""Generate 30 days x 2 posts = 60 talking-animal shorts into queue.csv.

Rotates the four seed characters (milo, rita, barkley, milo2) and stamps a
scheduled_date and time slot on each row.

Each row has three beat prompts anchored to a shared character reference.
Every prompt explicitly locks the character (single subject on camera) and the
voice (whiny deadpan male for Milo, etc.) to prevent the drift bugs we hit
during manual test-rendering.

Re-running this overwrites queue.csv from CHARACTERS + SCRIPTS below. Once
GitHub Actions marks rows `rendered`, running this again would clobber that
status — so guard with a git check when editing.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_CSV = ROOT / "brands" / "toolstack" / "queue.csv"

CHARACTERS = {
    "milo": {
        "look": "single fluffy orange tabby cat, big green eyes, small white chest, loose sky-blue tie",
        "voice": "slightly whiny, deadpan, put-upon male cat voice",
        "setting_default": "cramped corporate office",
    },
    "rita": {
        "look": "single clever raccoon, dark eye mask, small pink backpack",
        "voice": "confident, mischievous female raccoon voice",
        "setting_default": "suburban front porch at dusk",
    },
    "barkley": {
        "look": "single golden retriever detective, rumpled trench coat, fedora tilted low",
        "voice": "hardboiled, gravelly male dog voice",
        "setting_default": "shabby detective office",
    },
    "milo2": {
        "look": "single fluffy orange tabby cat, big green eyes, small white chest, loose sky-blue tie",
        "voice": "slightly whiny, deadpan, put-upon male cat voice",
        "setting_default": "cramped corporate office",
    },
}

# 30 talking-animal scripts. Each is (series, hook, beat1_action, beat2_action, beat3_action).
# The pipeline injects the character's look and voice into every beat prompt.
SCRIPTS = [
    ("milo",    "The CEO fired me for sleeping in the meeting.",
     "sits at a small desk, rubs his eyes and says the hook to camera",
     "hops onto a chair, opens a laptop, taps the screen with a paw, leans in and says: But he doesn't know I had the security cam running.",
     "grins smugly to camera as a small pigeon on his laptop screen behind him drags papers into a vent, and says: Turns out the pigeon in accounting has been leaking to Finance."),
    ("rita",   "A package showed up on my porch. Not mine.",
     "creeps up to a cardboard box on a porch and whispers the hook to camera",
     "pulls out a small pink notebook, licks a paw, and says: Standard procedure — inspect the label, then eat the treats.",
     "holds up an empty snack bag with a proud grin and says: Case closed. Amazon has my address now."),
    ("barkley", "The evidence disappeared from the desk. Rookie mistake.",
     "leans against a filing cabinet under a flickering light and says the hook to camera",
     "opens his own mouth like a filing drawer and says: I ate it. It was compelling.",
     "tips his hat to camera and says: My gut says we crack this case tomorrow. Or lunch. Whichever."),
    ("milo2",   "HR called about the incident in the break room.",
     "peeks over a cubicle wall, sighs, and says the hook to camera",
     "opens the fridge, points a paw at empty tuna cans, says: I did not, quote, sabotage the meeting snacks.",
     "holds up a printout of an email chain and says: But whoever labeled the tuna 'Karen' has a real problem."),
    ("milo",    "They gave the promotion to a golden retriever.",
     "slumps at his desk with his tie crooked and says the hook to camera",
     "opens a laptop and pulls up a resume with more paw prints than words, says: I have twelve years of experience napping in strategic locations.",
     "stares dead into the camera and says: I'm not bitter. I'm just going to become the pigeon's boss."),
    ("rita",    "The neighborhood dogs have a group chat.",
     "hides behind a mailbox holding a phone with too many notifications, and says the hook",
     "scrolls the phone with wide eyes and says: Apparently I'm 'the raccoon problem'. Rude. I have a resume.",
     "smirks to camera as a small bag of chips falls from a delivery drone, and says: Also they're wrong. I'm the raccoon solution."),
    ("barkley", "The mailman is running a smuggling ring.",
     "peers through venetian blinds and says the hook to camera in a low growl",
     "opens a manilla folder full of chewed-up envelopes and says: Every package. Every day. Same suspicious tail wag.",
     "adjusts his hat and says: Backup arrives in the form of the squirrel across the street. She owes me one."),
    ("milo2",   "My cat-boss took credit for my quarterly report.",
     "sits at a laptop with a spreadsheet open, glares at camera, and says the hook",
     "holds up a coffee mug that reads BOSS with the S covered by a sticky note that reads SIER, and says: I have receipts. Literally.",
     "leans back with his paws behind his head and says: HR loves receipts. So does the pigeon in accounting."),
    ("milo",    "I got assigned a mandatory team-building retreat.",
     "reads a printed email at his desk, ears flattening, says the hook to camera",
     "packs a tiny duffel with three sardines and a taser, and says: I am legally required to trust-fall onto Kevin.",
     "wipes his brow at the camera and says: Update: Kevin didn't catch me. Kevin is no longer with the company."),
    ("rita",    "Someone tried to raccoon-proof the trash.",
     "circles a shiny new locking trash can and says the hook, deadpan",
     "pops the lid open with one paw and says: They put a code on it. The code is: raccoons can read.",
     "poses next to the open can holding a half-eaten pizza slice and says: This block has been under new management since Tuesday."),
    ("barkley", "The cat next door has an alibi. It stinks.",
     "flips through a small notebook, sniffs the air, says the hook",
     "holds up a photo of an empty fishbowl and says: The witness claims she was napping. The bowl claims otherwise.",
     "narrows his eyes at camera and says: In this town, tuna breath is a confession."),
    ("milo2",   "The office coffee machine started leaving passive-aggressive notes.",
     "stares at the coffee machine, which has a Post-It on it, and says the hook to camera",
     "reads the Post-It out loud and says: 'Descale me or perish.' That's a threat, Karen.",
     "sips from a mug with a smug expression and says: I brought my own French press. The pigeon consulted."),
    ("milo",    "My performance review had a whole section on 'attitude'.",
     "sits across from an empty chair at his desk, deadpan, and says the hook",
     "flips a page in his review with a claw and says: Apparently 'sleeping through Q2' is not, quote, a personality.",
     "leans on the desk and says: I've decided to unionize. There are already three cats and a pigeon."),
    ("rita",    "A raccoon influencer moved onto the block.",
     "watches a shinier raccoon posing for a phone on a fence, says the hook",
     "narrows her eyes and says: She has a ring light. In an alley. This is a war crime.",
     "smiles slyly at camera as the ring light flickers off, and says: Batteries are so temperamental, aren't they?"),
    ("barkley", "The pigeon lawyered up.",
     "leans on his desk with a coffee cup, hardboiled, says the hook",
     "opens a folder that says PIGEON, INC. and says: His counsel is a very well-dressed magpie. I don't trust her hat.",
     "puts on sunglasses at his own desk and says: Court's at nine. Bring bagels. And bail money."),
    ("milo2",   "My cat-boss started micromanaging my nap schedule.",
     "sits stiffly at his desk with a spreadsheet titled NAP LOG open, says the hook",
     "highlights a cell that says 12:04 - 12:47 UNAPPROVED DOZE and says: This is a hostile work environment. Also I don't remember 12:04.",
     "smiles into the camera and says: Good news — the pigeon is now my union rep."),
    ("milo",    "IT sent an email about 'suspicious activity from your workstation'.",
     "sits at his desk looking innocent, keyboard covered in tuna, says the hook",
     "opens the email with a claw and reads: 'You logged in from Ohio at 3am.' I have never been to Ohio. I have been to the fridge.",
     "leans back with paws crossed and says: The pigeon uses my badge sometimes. He has commitments."),
    ("rita",    "There's a new food-delivery robot in the neighborhood.",
     "hides behind a bush watching a small delivery bot roll past, says the hook",
     "sniffs its wheels and says: It smells like burritos and betrayal.",
     "poses beside the bot with a burrito, grinning at camera, and says: Turns out its Achilles heel is a curb and a friendly smile."),
    ("barkley", "The client wants me to tail her husband. He tails easy.",
     "leans against a lamppost in a rumpled trench coat, hardboiled, says the hook",
     "flips open a small notebook and says: Subject visited a florist, a bakery, and a jeweler. Something is very wrong.",
     "tips his hat toward the camera and says: Or very right. That's the problem with love — the paperwork is identical."),
    ("milo2",   "Accounting flagged my snack expenses.",
     "sits with a printed spreadsheet titled 'Q3 SNACKS' in his paws, says the hook",
     "underlines a line item labeled TUNA-RELATED and says: These were, quote, 'team-building tuna'. Kevin ate three of them.",
     "leans toward the camera and says: The pigeon confirmed it in writing. In pigeon."),
    ("milo",    "There's a new intern. He's a golden retriever. I'm doomed.",
     "peeks around a cubicle at a golden retriever wagging his tail at everything, says the hook",
     "pulls up a shared calendar and says: He has already scheduled 'coffee chats' with six executives. He is nineteen.",
     "sighs at the camera and says: I've decided to mentor him. He's carrying my lunch by Friday."),
    ("rita",    "Somebody put motion lights on my favorite fence.",
     "creeps toward a fence as a floodlight flicks on, freezes, says the hook",
     "poses in the light like a magazine cover and says: If they wanted a photo shoot, they should have asked.",
     "smirks at camera as the light goes dark, and says: My contract requires hair, makeup, and one uncovered bin."),
    ("barkley", "The parrot witness recanted.",
     "sits across from a bird cage with an empty perch, deadpan, says the hook",
     "opens a file that says WITNESS: MR. FEATHERS and says: Yesterday she said 'the cat did it'. Today she says 'cracker'.",
     "adjusts his hat at camera and says: In this business, a witness with treats is not a witness. She's a suspect."),
    ("milo2",   "The office plant has been reporting me.",
     "narrows his eyes at a small potted plant on his desk, says the hook",
     "leans in and whispers to the plant, then to camera: HR knew about the tuna within eleven minutes. Coincidence?",
     "sips from his mug and says: I've replaced the plant with an identical plant. The pigeon handled logistics."),
    ("milo",    "Someone put a bell on me while I was asleep.",
     "sits up on a desk with a small bell around his neck jingling, deadpan to camera, says the hook",
     "walks two steps, jingles, sighs at camera and says: This is discrimination. Kevin doesn't have a bell. Kevin is a person.",
     "grins slowly at camera as the bell is now on the pigeon flying past, and says: Kevin's next."),
    ("rita",    "The block launched a neighborhood watch app.",
     "peers at a phone with 47 notifications, says the hook",
     "scrolls the app and says: I have my own tag now. It says: RACCOON — DO NOT ENGAGE. Rude. I engage plenty.",
     "poses on a fence, grinning at camera, and says: I've reported myself twice. My reviews are excellent."),
    ("barkley", "The cat coalition offered me a bribe.",
     "sits at his desk with an envelope and a small tin of sardines, hardboiled, says the hook",
     "opens the envelope with a claw and says: Twelve sardines and a note that says 'walk away'. I've walked away for less.",
     "tips his hat at camera and says: But this time I'm not walking. I'm running. Toward the tuna."),
    ("milo2",   "My cat-boss wants me to lead the all-hands.",
     "reads an email at his laptop with growing horror, says the hook",
     "practices in a small mirror on his desk and says: 'Team, our synergy is up.' No it isn't. Kevin is asleep on the printer.",
     "sighs at camera and says: I've delegated the whole thing to the pigeon. He owes me a favor. And a report."),
    ("milo",    "There's a new office rule about 'personal fragrances'.",
     "reads a memo pinned to his cubicle, deadpan to camera, says the hook",
     "sniffs his own tie and says: This is my natural musk. It's expensive. It's fish.",
     "leans on his desk and says: I've filed a complaint. Kevin agreed to sign it. Kevin will sign anything."),
    ("rita",    "The city put out those fake owl statues to scare us.",
     "sits eye-to-eye with a fake plastic owl, unimpressed, says the hook",
     "boops the owl on the beak and says: You have the same expression at midnight as you do at noon. You're not an owl. You're a stapler.",
     "poses on top of the owl and says: The trash can beneath you is now mine. Congratulations on your promotion, stapler."),
]

# Ensure we have 30 scripts (each rendered twice per day = 60 posts)
assert len(SCRIPTS) >= 30, f"need >=30 scripts, have {len(SCRIPTS)}"

TIMES = ["morning", "evening"]

START_DATE = date(2026, 9, 21)

# Beat template — inject character look and voice so every beat is anchored.
def build_prompt(char_key: str, action: str) -> str:
    c = CHARACTERS[char_key]
    return (
        "Cartoonish 3D animated vertical 9:16 video, Pixar-style. "
        f"The reference image is the ONLY main character on camera in this scene: {c['look']}. "
        f"Character {action}. "
        f"The character speaks in a {c['voice']}, mouth in sync. "
        "Exaggerated cartoon expressions, warm lighting. "
        "No other characters speak in this scene. No other characters appear on camera unless described."
    )


def main() -> None:
    QUEUE_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "creative_id", "scheduled_date", "time_slot", "series",
        "hook", "beat1_prompt", "beat2_prompt", "beat3_prompt",
        "ref_url", "status", "rendered_at",
    ]
    rows = []
    day = 0
    for i in range(30):
        script = SCRIPTS[i % len(SCRIPTS)]
        series, hook, a1, a2, a3 = script
        for j, slot in enumerate(TIMES):
            n = i * 2 + j + 1
            cid = f"{series.upper()}-D{i+1:02d}-{slot.upper()[:3]}"
            rows.append({
                "creative_id": cid,
                "scheduled_date": (START_DATE + timedelta(days=i)).isoformat(),
                "time_slot": slot,
                "series": series,
                "hook": hook,
                "beat1_prompt": build_prompt(series, a1),
                "beat2_prompt": build_prompt(series, a2),
                "beat3_prompt": build_prompt(series, a3),
                "ref_url": "",
                "status": "queued",
                "rendered_at": "",
            })
    with QUEUE_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {QUEUE_CSV}")


if __name__ == "__main__":
    main()
