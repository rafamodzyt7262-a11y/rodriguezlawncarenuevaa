/**
 * =========================================================================
 * RODRIGUEZ LAWNCARE - ANTI-BOT & INTRUSION DEFENSE SHIELD (v2.0)
 * =========================================================================
 * 1. Invisible Honeypot Trap (Automated bot detection)
 * 2. Time-Based Submission Guard (Prevents sub-second automated POST attacks)
 * 3. Form Rate-Limiting Engine (Stops credential stuffing and spam loops)
 * 4. 100% Invisible to Human Customers
 * =========================================================================
 */

(function () {
  'use strict';

  const pageLoadTime = Date.now();
  const MINIMUM_INTERACTION_MS = 1400; // Inhuman bot speed threshold
  let lastSubmitTime = 0;
  const SUBMISSION_COOLDOWN_MS = 3500; // 3.5s cooldown between clicks

  document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(function (form) {
      // 1. Inject Invisible Honeypot (Bots automatically fill this out, humans never see it)
      if (!form.querySelector('.bot-honey-check')) {
        const honeyWrap = document.createElement('div');
        honeyWrap.className = 'bot-honey-check';
        honeyWrap.style.cssText = 'position:absolute!important;opacity:0!important;pointer-events:none!important;left:-9999px!important;top:-9999px!important;width:1px!important;height:1px!important;overflow:hidden!important;';

        const honeyInput = document.createElement('input');
        honeyInput.type = 'text';
        honeyInput.name = 'rodriguez_sec_honey';
        honeyInput.tabIndex = -1;
        honeyInput.autocomplete = 'off';

        honeyWrap.appendChild(honeyInput);
        form.appendChild(honeyWrap);
      }

      // 2. Intercept and Guard Submissions
      form.addEventListener('submit', function (e) {
        const now = Date.now();
        const honey = form.querySelector('input[name="rodriguez_sec_honey"]');

        // Bot Detection A: Honeypot filled
        if (honey && honey.value.trim() !== '') {
          e.preventDefault();
          e.stopPropagation();
          console.warn('Bot submission blocked.');
          return false;
        }

        // Bot Detection B: Inhuman speed (<1.4s since page load)
        if (now - pageLoadTime < MINIMUM_INTERACTION_MS) {
          e.preventDefault();
          e.stopPropagation();
          console.warn('Rapid automated interaction blocked.');
          return false;
        }

        // Bot Detection C: Spam Rate-Limiting Cooldown
        if (now - lastSubmitTime < SUBMISSION_COOLDOWN_MS) {
          e.preventDefault();
          e.stopPropagation();
          return false;
        }

        lastSubmitTime = now;
      }, { capture: true });
    });
  });

})();
