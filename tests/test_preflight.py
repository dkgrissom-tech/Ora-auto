"""Pre-flight validation and scheduler loud-failure checks.

Run: python3 tests/test_preflight.py
"""
import datetime as dt
import os
import pathlib
import shutil
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import ingest_clone_drafts as ic  # noqa: E402
import run_scheduler as rs  # noqa: E402


class IngestPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.original = (ic.ROOT, ic.DRAFTS_DIR, ic.BRANDS_DIR, ic.LOG_DIR)
        ic.ROOT = self.tmp
        ic.DRAFTS_DIR = self.tmp / "clone_drafts"
        ic.BRANDS_DIR = self.tmp / "brands"
        ic.LOG_DIR = self.tmp / "logs"
        ic.LOG_DIR.mkdir(parents=True)
        self.path = ic.DRAFTS_DIR / "ora" / "draft.md"
        self.path.parent.mkdir(parents=True)

    def tearDown(self):
        ic.ROOT, ic.DRAFTS_DIR, ic.BRANDS_DIR, ic.LOG_DIR = self.original
        shutil.rmtree(self.tmp, ignore_errors=True)

    def block(self, **meta):
        return {"meta": meta, "body": "A pre-flight test post."}

    def test_missing_destination_names_the_offending_file(self):
        with self.assertRaisesRegex(ic.DraftValidationError, r"draft\.md.*destination"):
            ic.validate_required_frontmatter(
                self.path, [self.block(platforms="bluesky", stage="capture")]
            )

    def test_unapproved_destination_names_url_and_allow_list(self):
        with self.assertRaises(ic.DraftValidationError) as error:
            ic.validate_required_frontmatter(
                self.path,
                [self.block(
                    platforms="bluesky",
                    destination="https://evil.example.com",
                    stage="capture",
                )],
            )
        self.assertIn("https://evil.example.com", str(error.exception))
        self.assertIn("Allowed destinations:", str(error.exception))

    def test_valid_destination_and_capture_stage_pass(self):
        block = self.block(
            date="2026-08-15",
            time="14:00",
            platforms="bluesky",
            destination="https://cedarhollow.pplx.app/porch-before",
            stage="capture",
        )
        ic.validate_required_frontmatter(self.path, [block])
        post = ic.validate_and_normalize("ora", block, {})
        self.assertEqual(post["destination"], "https://cedarhollow.pplx.app/porch-before")
        self.assertEqual(post["stage"], "capture")


class SchedulerPreflightTests(unittest.TestCase):
    def setUp(self):
        self.original = {
            "BRANDS": rs.BRANDS,
            "DRY_RUN": rs.DRY_RUN,
            "parse_today": rs.parse_today,
            "route": rs.route,
            "load_ledger": rs.load_ledger,
            "save_ledger": rs.save_ledger,
            "log": rs.log,
        }
        self.logs = []
        rs.BRANDS = ["ora"]
        rs.DRY_RUN = False
        rs.log = self.logs.append
        rs.load_ledger = lambda: set()
        rs.save_ledger = lambda _keys: None
        rs.route = lambda platforms: platforms
        rs.parse_today = lambda _brand: [{
            "brand": "ora",
            "hour": dt.datetime.utcnow().hour,
            "platforms": ["bluesky"],
            "image": None,
            "alt": None,
            "tags": None,
            "video": None,
            "destination": "https://meetora-app.pplx.app",
            "stage": "capture",
            "pinterest_title": None,
            "pinterest_url": None,
            "body": "No credentials should fail loudly.",
        }]

    def tearDown(self):
        for name, value in self.original.items():
            setattr(rs, name, value)

    def test_dry_run_missing_keys_exits_nonzero_with_summary(self):
        os.environ.pop("ORA_BLUESKY_HANDLE", None)
        os.environ.pop("ORA_BLUESKY_APP_PASSWORD", None)
        result = rs.main(["--dry-run"])
        self.assertEqual(result, 1)
        summary = next(line for line in self.logs if line.startswith("SCHEDULER FAILED:"))
        self.assertIn("1 of 1 posts failed", summary)
        self.assertIn("ora/bluesky", summary)

    def test_destination_cta_is_final_line_without_duplicate(self):
        destination = "https://meetora-app.pplx.app"
        self.assertEqual(
            rs.append_destination_url("A useful post.", destination),
            "A useful post.\nhttps://meetora-app.pplx.app",
        )
        existing = "A useful post.\nhttps://elsewhere.example/page"
        self.assertEqual(rs.append_destination_url(existing, destination), existing)


if __name__ == "__main__":
    unittest.main(verbosity=2)
