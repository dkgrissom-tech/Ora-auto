"""
Daily digest emailer — reads logs/failures.jsonl, logs/successes.jsonl,
and logs/transients.jsonl, filters to the last 24h, and sends one
summary email via MailerLite transactional API.

Runs via .github/workflows/daily_digest.yml at 09:00 CT (14:00 UTC).

Environment variables required:
  MAILERLITE_API_KEY   — MailerLite API key (already wired for Ora-auto)
  DIGEST_RECIPIENT     — destination email (set via DIGEST_RECIPIENT_EMAIL secret)
"""
import os
import sys
import json
import datetime as dt
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
WINDOW_HOURS = 24

MAILERLITE_TRANSACTIONAL_URL = "https://connect.mailerlite.com/api/emails"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_jsonl(filename):
    """Return all records from logs/<filename>, silently returning [] if missing."""
    path = LOG_DIR / filename
    if not path.exists():
        return []
    records = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # skip corrupted lines
    return records


def within_window(ts_str, hours=WINDOW_HOURS):
    """True when the ISO-8601 timestamp is within the last <hours> hours."""
    try:
        ts = dt.datetime.fromisoformat(ts_str.rstrip("Z")).replace(
            tzinfo=dt.timezone.utc
        )
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
        return ts >= cutoff
    except Exception:
        return False


def send_via_mailerlite(api_key, to_email, subject, body_text, body_html):
    """POST to MailerLite transactional /emails endpoint."""
    import urllib.request
    payload = json.dumps({
        "from": {"email": "noreply@ora-auto.app", "name": "Ora-auto"},
        "to": [{"email": to_email}],
        "subject": subject,
        "text": body_text,
        "html": body_html,
    }).encode()
    req = urllib.request.Request(
        MAILERLITE_TRANSACTIONAL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.getcode()
            body = resp.read().decode()
            print(f"[digest] MailerLite response {status}: {body[:200]}")
            return status in (200, 201, 202)
    except Exception as e:
        print(f"[digest] MailerLite send failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Build email content
# ---------------------------------------------------------------------------

def build_digest(failures, successes, transients):
    """Return (subject, text_body, html_body)."""

    n_fail = len(failures)
    n_ok = len(successes)

    # Group failures by brand/channel
    by_brand_channel = collections.defaultdict(list)
    for r in failures:
        key = f"{r.get('brand','?')}/{r.get('channel','?')}"
        by_brand_channel[key].append(r)

    # Transients: count per brand/channel and flag if >20 in 24h
    transient_counts = collections.Counter(
        f"{r.get('brand','?')}/{r.get('channel','?')}" for r in transients
    )
    promoted_transients = {k: v for k, v in transient_counts.items() if v > 20}

    # ---- plain text --------------------------------------------------------
    lines = [f"Failures by brand/channel:"]
    if not by_brand_channel and not promoted_transients:
        lines = []

    for key, events in sorted(by_brand_channel.items()):
        lines.append(f"  {key}: {len(events)} failure{'s' if len(events) != 1 else ''}")
        for ev in events:
            ts = ev.get("ts", "?")[:19].replace("T", " ")
            etype = ev.get("error_type", "Error")
            emsg = ev.get("error_msg", "")[:120]
            lines.append(f"    - {ts} UTC: {etype} {emsg}")

    if promoted_transients:
        lines.append("")
        lines.append("Elevated transient errors (>20 in 24h — platform may be down):")
        for key, count in sorted(promoted_transients.items()):
            lines.append(f"  {key}: {count} transient errors")

    if transient_counts and not promoted_transients:
        total_t = sum(transient_counts.values())
        lines.append("")
        lines.append(f"Transient issues: {total_t} (auto-retrying, below alert threshold)")

    lines.append("")
    lines.append(f"Successes: {n_ok} post{'s' if n_ok != 1 else ''} published in last 24h")

    text_body = "\n".join(lines)

    # ---- HTML --------------------------------------------------------------
    html_rows = ""
    for key, events in sorted(by_brand_channel.items()):
        html_rows += f"<tr><td colspan='2' style='padding:8px 0 2px;font-weight:bold'>{key} — {len(events)} failure(s)</td></tr>"
        for ev in events:
            ts = ev.get("ts", "?")[:19].replace("T", " ")
            etype = ev.get("error_type", "Error")
            emsg = ev.get("error_msg", "")[:120]
            html_rows += (
                f"<tr><td style='padding:2px 16px;color:#666'>{ts} UTC</td>"
                f"<td style='padding:2px 4px;color:#c00'>{etype}: {emsg}</td></tr>"
            )

    promoted_html = ""
    if promoted_transients:
        promoted_html = "<p><strong>⚠️ Elevated transient errors (&gt;20/24h — platform may be down):</strong></p><ul>"
        for key, count in sorted(promoted_transients.items()):
            promoted_html += f"<li>{key}: {count} transient errors</li>"
        promoted_html += "</ul>"

    transient_note = ""
    if transient_counts and not promoted_transients:
        total_t = sum(transient_counts.values())
        transient_note = f"<p style='color:#888'>Transient issues: {total_t} (auto-retrying, below alert threshold)</p>"

    html_body = f"""<!DOCTYPE html>
<html><body style='font-family:sans-serif;max-width:600px;margin:auto'>
<h2 style='color:#333'>[Ora-auto] Daily Digest</h2>
{'<table style="border-collapse:collapse;width:100%">' + html_rows + '</table>' if html_rows else '<p style="color:green">✅ No failures in last 24h.</p>'}
{promoted_html}
{transient_note}
<hr>
<p>✅ <strong>{n_ok} post{'s' if n_ok != 1 else ''}</strong> published successfully in the last 24h.</p>
<p style='color:#aaa;font-size:11px'>Ora-auto daily digest · failures need action · transients auto-retry next tick</p>
</body></html>"""

    return f"[Ora-auto] Daily digest: {n_fail} failure{'s' if n_fail != 1 else ''} in last 24h", text_body, html_body


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_key = os.environ.get("MAILERLITE_API_KEY", "").strip()
    recipient = os.environ.get("DIGEST_RECIPIENT", "").strip()

    if not api_key:
        print("[digest] ERROR: MAILERLITE_API_KEY not set — cannot send digest")
        sys.exit(1)
    if not recipient:
        print("[digest] ERROR: DIGEST_RECIPIENT not set — cannot send digest")
        sys.exit(1)

    # Load and filter to last 24h
    all_failures = [r for r in load_jsonl("failures.jsonl") if within_window(r.get("ts", ""))]
    all_successes = [r for r in load_jsonl("successes.jsonl") if within_window(r.get("ts", ""))]
    all_transients = [r for r in load_jsonl("transients.jsonl") if within_window(r.get("ts", ""))]

    n_fail = len(all_failures)
    n_ok = len(all_successes)
    n_trans = len(all_transients)
    print(f"[digest] Last 24h: {n_fail} failures, {n_trans} transients, {n_ok} successes")

    if n_fail == 0 and not any(v > 20 for v in
                                collections.Counter(
                                    f"{r.get('brand','?')}/{r.get('channel','?')}"
                                    for r in all_transients
                                ).values()):
        print("[digest] No failures and no elevated transients in last 24h — skipping digest email")
        sys.exit(0)

    subject, text_body, html_body = build_digest(all_failures, all_successes, all_transients)
    print(f"[digest] Sending: {subject}")
    print(f"[digest] To: {recipient}")

    ok = send_via_mailerlite(api_key, recipient, subject, text_body, html_body)
    if ok:
        print("[digest] Email sent successfully")
    else:
        print("[digest] Email send FAILED — check MailerLite key and account")
        sys.exit(1)


if __name__ == "__main__":
    main()
