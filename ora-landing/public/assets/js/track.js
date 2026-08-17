/**
 * Ora landing page tracker.
 *
 * NOTE FOR DON: the build brief points at "PR #10" for a tracker snippet to
 * copy verbatim, but PR #10 in dkgrissom-tech/Ora-auto is an unrelated
 * Instagram-posting bugfix, and none of the referenced context docs
 * (ora-auto-pr10-claude-direction.md, etc.) exist in this repo. This file
 * is a fresh, minimal implementation of the behavior Step 7 of the brief
 * describes (page_view / cta_click / email_capture -> TRACKER_ENDPOINT).
 * Swap it for the real PR #10 tracker.js if it differs from this.
 */
(function () {
  var ENDPOINT = (window.ORA_TRACKER_ENDPOINT || 'https://track.grissompress.com') + '/collect';

  function utmParams() {
    var params = new URLSearchParams(window.location.search);
    return {
      utm_source: params.get('utm_source') || '',
      utm_medium: params.get('utm_medium') || '',
      utm_campaign: params.get('utm_campaign') || '',
      utm_content: params.get('utm_content') || '',
    };
  }

  function send(event, props) {
    var payload = Object.assign(
      {
        event: event,
        page: window.location.pathname,
        referrer: document.referrer || '',
        ts: new Date().toISOString(),
      },
      utmParams(),
      props || {}
    );

    var body = JSON.stringify(payload);

    if (navigator.sendBeacon) {
      var blob = new Blob([body], { type: 'application/json' });
      navigator.sendBeacon(ENDPOINT, blob);
      return;
    }

    fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body,
      keepalive: true,
    }).catch(function (err) {
      console.error('Tracker send failed', err);
    });
  }

  window.oraTrack = send;

  document.addEventListener('DOMContentLoaded', function () {
    send('page_view');

    document.querySelectorAll('[data-track="cta"]').forEach(function (el) {
      el.addEventListener('click', function () {
        send('cta_click', { cta_name: el.getAttribute('data-cta-name') || '' });
      });
    });
  });
})();
