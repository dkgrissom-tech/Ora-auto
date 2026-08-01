"""
Smoke tests for send_clone_emails.py.

Runs in a temp dir. Uses stdlib only. `requests` is never imported by the
paths under test (build_create_payload, md_to_html, validate, parse, dedupe).
"""
import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import send_clone_emails as se  # noqa: E402


class EmailTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        se.ROOT = self.tmp
        se.DRAFTS_DIR = self.tmp / "email_drafts"
        se.LOG_DIR = self.tmp / "logs"
        se.LOG_DIR.mkdir(parents=True, exist_ok=True)
        (se.DRAFTS_DIR / "ora").mkdir(parents=True, exist_ok=True)
        (se.DRAFTS_DIR / "grissom").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --------------------- parse ---------------------

    def test_parse_valid(self):
        p = se.DRAFTS_DIR / "ora" / "one.md"
        p.write_text(
            "---\n"
            "subject: Hi\n"
            "from_name: Don\n"
            "from_email: don@example.com\n"
            "---\n"
            "# Hello\n\nBody goes here.\n"
        )
        d = se.parse_email_draft(p)
        self.assertIsNotNone(d)
        self.assertEqual(d["meta"]["subject"], "Hi")
        self.assertIn("Hello", d["body_md"])

    def test_parse_missing_fence(self):
        p = se.DRAFTS_DIR / "ora" / "bad.md"
        p.write_text("subject: no fence\nbody here")
        self.assertIsNone(se.parse_email_draft(p))

    def test_parse_empty_body(self):
        p = se.DRAFTS_DIR / "ora" / "empty.md"
        p.write_text("---\nsubject: x\nfrom_name: y\nfrom_email: a@b.com\n---\n\n")
        self.assertIsNone(se.parse_email_draft(p))

    # --------------------- validate ---------------------

    def test_validate_missing_required(self):
        draft = {
            "meta": {"subject": "hi", "from_name": "Don"},
            "body_md": "hi",
            "source": "x.md",
        }
        self.assertIsNone(se.validate(draft))

    def test_validate_schedule_in_past_rejected(self):
        draft = {
            "meta": {
                "subject": "hi",
                "from_name": "Don",
                "from_email": "d@x.com",
                "schedule": "2020-01-01 12:00 UTC",
            },
            "body_md": "hi",
            "source": "x.md",
        }
        self.assertIsNone(se.validate(draft))

    def test_validate_bad_schedule_format(self):
        draft = {
            "meta": {
                "subject": "hi",
                "from_name": "Don",
                "from_email": "d@x.com",
                "schedule": "next tuesday",
            },
            "body_md": "hi",
            "source": "x.md",
        }
        self.assertIsNone(se.validate(draft))

    def test_validate_ok_no_schedule(self):
        draft = {
            "meta": {"subject": "hi", "from_name": "Don", "from_email": "d@x.com"},
            "body_md": "hi",
            "source": "x.md",
        }
        v = se.validate(draft)
        self.assertIsNotNone(v)
        self.assertIsNone(v["schedule"])

    def test_validate_future_schedule(self):
        future = (dt.datetime.utcnow() + dt.timedelta(days=1)).strftime("%Y-%m-%d 12:00 UTC")
        draft = {
            "meta": {
                "subject": "hi", "from_name": "Don", "from_email": "d@x.com",
                "schedule": future,
            },
            "body_md": "hi",
            "source": "x.md",
        }
        v = se.validate(draft)
        self.assertIsNotNone(v)
        self.assertIsNotNone(v["schedule"])
        self.assertIn("date", v["schedule"])
        self.assertEqual(v["schedule"]["hours"], "12")

    # --------------------- markdown ---------------------

    def test_md_heading_and_paragraph(self):
        html = se.md_to_html("# Title\n\nHello world.")
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<p>Hello world.</p>", html)

    def test_md_link_and_bold(self):
        html = se.md_to_html("Click [here](https://example.com) for **bold** stuff.")
        self.assertIn('<a href="https://example.com">here</a>', html)
        self.assertIn("<strong>bold</strong>", html)

    def test_md_bullet_list(self):
        html = se.md_to_html("- one\n- two\n- three")
        self.assertIn("<ul>", html)
        self.assertEqual(html.count("<li>"), 3)

    def test_md_escapes_html(self):
        html = se.md_to_html("<script>alert(1)</script>")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    # --------------------- payload ---------------------

    def test_build_create_payload_shape(self):
        email = {
            "subject": "Ora launches",
            "from_name": "Don",
            "from_email": "hi@meetora.app",
            "reply_to": "don@grissom.tech",
            "schedule": None,
            "body_md": "# Ora\n\nBody.",
            "source": "x.md",
        }
        p = se.build_create_payload(email, group_id="999")
        self.assertEqual(p["type"], "regular")
        self.assertEqual(p["groups"], ["999"])
        self.assertEqual(len(p["emails"]), 1)
        e = p["emails"][0]
        self.assertEqual(e["subject"], "Ora launches")
        self.assertEqual(e["from_name"], "Don")
        self.assertEqual(e["from"], "hi@meetora.app")
        self.assertEqual(e["reply_to"], "don@grissom.tech")
        self.assertIn("<h1>Ora</h1>", e["content"])

    def test_schedule_payload_instant_vs_scheduled(self):
        p_instant = se.build_schedule_payload({"schedule": None})
        self.assertEqual(p_instant, {"delivery": "instant"})
        p_sched = se.build_schedule_payload({"schedule": {"date": "2027-01-01", "hours": "14", "minutes": "30"}})
        self.assertEqual(p_sched["delivery"], "scheduled")
        self.assertEqual(p_sched["schedule"]["date"], "2027-01-01")

    # --------------------- dedupe ---------------------

    def test_content_id_stable(self):
        e1 = {"subject": "hi", "from_email": "a@b.com", "body_md": "x"}
        e2 = {"subject": "hi", "from_email": "a@b.com", "body_md": "x"}
        e3 = {"subject": "hi", "from_email": "a@b.com", "body_md": "y"}
        self.assertEqual(se.content_id(e1), se.content_id(e2))
        self.assertNotEqual(se.content_id(e1), se.content_id(e3))

    def test_already_sent_detects_prior_send(self):
        email = {"subject": "hi", "from_email": "a@b.com", "body_md": "x"}
        self.assertFalse(se.already_sent("ora", email))
        sent_dir = se.DRAFTS_DIR / "ora" / "_sent"
        sent_dir.mkdir(parents=True, exist_ok=True)
        (sent_dir / f"20260801T000000Z__{se.content_id(email)}__x.md").write_text("archived")
        self.assertTrue(se.already_sent("ora", email))

    # --------------------- integration (dry-run) ---------------------

    def test_dry_run_skips_when_no_secrets(self):
        p = se.DRAFTS_DIR / "ora" / "test.md"
        p.write_text(
            "---\n"
            "subject: Hello\n"
            "from_name: Don\n"
            "from_email: d@x.com\n"
            "---\n"
            "# Hi\n\nBody.\n"
        )
        # No env secrets set → skipped-config
        stats = se.process_brand("ora", dry_run=True)
        self.assertEqual(stats["skipped-config"], 1)
        self.assertTrue(p.exists(), "draft should stay in place when config is missing")

    def test_dry_run_with_secrets_does_not_call_api(self):
        p = se.DRAFTS_DIR / "ora" / "test.md"
        p.write_text(
            "---\n"
            "subject: Hello\n"
            "from_name: Don\n"
            "from_email: d@x.com\n"
            "---\n"
            "# Hi\n\nBody.\n"
        )
        os.environ["ORA_MAILERLITE_API_KEY"] = "sk_fake"
        os.environ["ORA_MAILERLITE_GROUP_ID"] = "1234"
        try:
            stats = se.process_brand("ora", dry_run=True)
        finally:
            del os.environ["ORA_MAILERLITE_API_KEY"]
            del os.environ["ORA_MAILERLITE_GROUP_ID"]
        self.assertEqual(stats["dry-run"], 1)
        self.assertTrue(p.exists(), "draft should stay in place in dry-run")


if __name__ == "__main__":
    unittest.main(verbosity=2)
