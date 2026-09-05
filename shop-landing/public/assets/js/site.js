(function () {
  const forms = document.querySelectorAll('form[data-capture="email"]');

  forms.forEach((form) => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = form.querySelector('input[type="email"]').value.trim();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalLabel = submitBtn.textContent;

      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        showError(form, "That doesn't look like an email.");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';

      // Pull UTM params from URL
      const params = new URLSearchParams(window.location.search);
      const payload = {
        email,
        utm_source: params.get('utm_source') || '',
        utm_medium: params.get('utm_medium') || '',
        utm_campaign: params.get('utm_campaign') || '',
        utm_content: params.get('utm_content') || '',
        page: window.location.pathname,
      };

      try {
        const res = await fetch('/subscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        // Fire tracker
        if (window.oraTrack) {
          window.oraTrack('email_capture', {
            form_id: form.id,
            utm_source: payload.utm_source,
            utm_content: payload.utm_content,
          });
        }

        // Show success
        form.hidden = true;
        const thanks = form.parentElement.querySelector('.hero-thanks');
        if (thanks) thanks.hidden = false;

      } catch (err) {
        console.error('Subscribe failed', err);
        showError(form, "Something went wrong. Please try again or email hello@meetora.app.");
        submitBtn.disabled = false;
        submitBtn.textContent = originalLabel;
      }
    });
  });

  function showError(form, message) {
    let errEl = form.querySelector('.form-error');
    if (!errEl) {
      errEl = document.createElement('p');
      errEl.className = 'form-error';
      form.appendChild(errEl);
    }
    errEl.textContent = message;
    errEl.style.color = '#ef4444';
    errEl.style.marginTop = '8px';
  }
})();
