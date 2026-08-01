"""
Smoke tests for ingest_clone_drafts.py.

Runs in a temp dir that mirrors the Ora-auto layout, so we can verify:
- parse_draft_file splits blocks correctly
- validate_and_normalize enforces the platform/image/video rules
- append_post_to_daily_file writes idempotent blocks
- brand TikTok policy is enforced
- auto-slotting avoids collisions
"""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Import the module under test from the sibling scripts/ dir
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import ingest_clone_drafts as ic  # noqa: E402


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        # rewire ROOT paths
        ic.ROOT = self.tmp
        ic.DRAFTS_DIR = self.tmp / "clone_drafts"
        ic.BRANDS_DIR = self.tmp / "brands"
        ic.LOG_DIR = self.tmp / "logs"
        ic.LOG_DIR.mkdir(parents=True, exist_ok=True)
        (ic.DRAFTS_DIR / "ora").mkdir(parents=True, exist_ok=True)
        (ic.DRAFTS_DIR / "grissom").mkdir(parents=True, exist_ok=True)
        (ic.BRANDS_DIR / "ora" / "posts").mkdir(parents=True, exist_ok=True)
        (ic.BRANDS_DIR / "grissom" / "posts").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------ parse ------------------------

    def test_parse_two_blocks(self):
        p = ic.DRAFTS_DIR / "ora" / "day.md"
        p.write_text(
            "---\n"
            "date: 2026-08-05\n"
            "time: 14:00\n"
            "platforms: bluesky, threads\n"
            "---\n"
            "First body.\n"
            "Line two.\n"
            "---\n"
            "---\n"
            "date: 2026-08-05\n"
            "time: 18:00\n"
            "platforms: linkedin\n"
            "---\n"
            "Second body.\n"
            "---\n"
        )
        blocks = ic.parse_draft_file(p)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0]["meta"]["time"], "14:00")
        self.assertIn("First body.", blocks[0]["body"])
        self.assertEqual(blocks[1]["meta"]["platforms"], "linkedin")

    # ---------------------- validation ---------------------

    def test_instagram_requires_image(self):
        block = {
            "meta": {"date": "2026-08-05", "time": "14:00", "platforms": "instagram"},
            "body": "hi",
        }
        result = ic.validate_and_normalize("ora", block, {})
        self.assertIsNone(result)

    def test_tiktok_blocked_for_grissom(self):
        block = {
            "meta": {
                "date": "2026-08-05",
                "time": "14:00",
                "platforms": "bluesky, tiktok",
                "video": "brands/grissom/assets/x.mp4",
            },
            "body": "hi",
        }
        result = ic.validate_and_normalize("grissom", block, {})
        self.assertIsNotNone(result)
        self.assertNotIn("tiktok", result["platforms"])
        self.assertIn("bluesky", result["platforms"])

    def test_tiktok_requires_video(self):
        block = {
            "meta": {"date": "2026-08-05", "time": "14:00", "platforms": "tiktok"},
            "body": "hi",
        }
        result = ic.validate_and_normalize("ora", block, {})
        self.assertIsNone(result)

    def test_auto_slot_when_time_missing(self):
        used = {}
        block = {
            "meta": {"date": "2026-08-05", "platforms": "bluesky"},
            "body": "hi",
        }
        result = ic.validate_and_normalize("ora", block, used)
        self.assertIsNotNone(result)
        # ora's first default slot is 13:00
        self.assertEqual(result["time"], "13:00")
        # subsequent block that day should get 18:00
        block2 = {"meta": {"date": "2026-08-05", "platforms": "bluesky"}, "body": "hi2"}
        result2 = ic.validate_and_normalize("ora", block2, used)
        self.assertEqual(result2["time"], "18:00")

    # ----------------------- emit --------------------------

    def test_append_and_dedupe(self):
        post = {
            "brand": "ora",
            "date": "2026-08-05",
            "time": "14:00",
            "platforms": ["bluesky", "threads"],
            "image": None, "video": None,
            "pinterest_title": None, "pinterest_url": None,
            "body": "hello world",
        }
        r1 = ic.append_post_to_daily_file(post, dry_run=False)
        r2 = ic.append_post_to_daily_file(post, dry_run=False)
        self.assertEqual(r1, "wrote")
        self.assertEqual(r2, "skip-duplicate")
        f = ic.BRANDS_DIR / "ora" / "posts" / "2026-08-05.md"
        text = f.read_text()
        self.assertIn("## 14:00 UTC", text)
        self.assertIn("<!-- CLONE:START id=", text)
        self.assertIn("<!-- CLONE:END -->", text)
        self.assertEqual(text.count("hello world"), 1)  # not duplicated

    def test_scheduler_format_compat(self):
        """Rendered block must match the parser in run_scheduler.py."""
        post = {
            "brand": "ora",
            "date": "2026-08-05",
            "time": "14:00",
            "platforms": ["bluesky", "threads", "instagram", "pinterest"],
            "image": "brands/ora/assets/drop1_8am_listening.png",
            "video": None,
            "pinterest_title": "Just say Ora",
            "pinterest_url": "https://meetora-app.pplx.app",
            "body": "Say it and it starts listening.",
        }
        ic.append_post_to_daily_file(post, dry_run=False)
        f = ic.BRANDS_DIR / "ora" / "posts" / "2026-08-05.md"
        text = f.read_text()
        # Mirror run_scheduler.py's block parser exactly.
        blocks = text.split("\n## ")[1:]
        self.assertGreaterEqual(len(blocks), 1)
        header, rest = blocks[0].split("\n", 1)
        self.assertTrue(header.startswith("14:00 UTC"))
        # meta block ends at first ---
        meta_section = rest.split("\n---\n", 1)[0]
        self.assertIn("platforms: bluesky, threads, instagram, pinterest", meta_section)
        self.assertIn("image: brands/ora/assets/drop1_8am_listening.png", meta_section)
        self.assertIn("pinterest_title: Just say Ora", meta_section)

    def test_slot_collision_with_existing_file(self):
        """If today's file already has 13:00, auto-slot must skip to 18:00."""
        f = ic.BRANDS_DIR / "ora" / "posts" / "2026-08-05.md"
        f.write_text("# existing\n\n## 13:00 UTC  (08:00 CDT)\nplatforms: bluesky\n---\nold\n---\n")
        used_seed = {"2026-08-05": ic.existing_hours_in_file(f)}
        self.assertIn(13, used_seed["2026-08-05"])
        block = {"meta": {"date": "2026-08-05", "platforms": "bluesky"}, "body": "new"}
        result = ic.validate_and_normalize("ora", block, used_seed)
        self.assertEqual(result["time"], "18:00")


if __name__ == "__main__":
    unittest.main(verbosity=2)
