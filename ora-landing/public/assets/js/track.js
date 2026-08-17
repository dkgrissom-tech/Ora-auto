(function () {
  var ENDPOINT = "https://track.grissompress.com/e";
  var BRAND = (document.currentScript && document.currentScript.dataset.brand) || "grissom";

  var sid = sessionStorage.getItem("_gpsid");
  if (!sid) {
    sid = Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
    sessionStorage.setItem("_gpsid", sid);
  }

  var q = new URLSearchParams(location.search);
  var ctx = {
    brand: BRAND,
    post_id:      q.get("utm_content") || null,
    platform:     q.get("utm_source")  || null,
    utm_content:  q.get("utm_content"),
    utm_campaign: q.get("utm_campaign"),
    session_id:   sid,
    page_url:     location.href,
    referrer:     document.referrer || null,
  };

  function send(event, extra) {
    var body = Object.assign({}, ctx, { event: event }, extra || {});
    var blob = new Blob([JSON.stringify(body)], { type: "application/json" });
    if (navigator.sendBeacon) navigator.sendBeacon(ENDPOINT, blob);
    else fetch(ENDPOINT, { method: "POST", body: JSON.stringify(body), keepalive: true, headers: { "content-type": "application/json" } });
  }

  send("page_view");

  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-cta], a[href*='gumroad.com'], a[href*='cedarhollow']");
    if (!el) return;
    send("cta_click", { cta: el.getAttribute("data-cta") || el.getAttribute("href") });
  });

  document.addEventListener("submit", function (e) {
    var f = e.target.closest("form[data-capture='email']");
    if (!f) return;
    send("email_capture");
  });

  window.gp = { track: send };
})();
