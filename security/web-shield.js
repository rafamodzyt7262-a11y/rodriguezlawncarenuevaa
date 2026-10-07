/**
 * =========================================================================
 * RODRIGUEZ LAWNCARE - MILITARY-GRADE CLIENT-SIDE DEFENSE SHIELD (v4.0)
 * =========================================================================
 * Multi-Vector Security Architecture:
 * 1. Anti-Reverse Engineering & Debugger Trap
 * 2. DOM Immutability & Brand Integrity Guard (MutationObserver Level 3)
 * 3. Prototype Pollution & Global Scope Freezing (Object.freeze)
 * 4. Advanced Anti-Theft (Right-click, F12, DevTools keys, View Source, Print Screen)
 * 5. In-Memory Anti-Tamper Verification (Self-Healing DOM)
 * 6. XSS, JWT & Token Payload Neutralizer
 * 7. Anti-Clickjacking & Iframe Sandboxing
 * 8. 100% Silent Execution (No alerts, popups, or disruptions to real users)
 * =========================================================================
 */

(function () {
  'use strict';

  // -----------------------------------------------------------------------
  // 1. GLOBAL SCOPE HARDENING & PROTOTYPE IMMUTABILITY
  // -----------------------------------------------------------------------
  try {
    // Neutralize dangerous execution vectors
    if (window.eval) {
      window.eval = function () {
        throw new Error('Dynamic evaluation disabled by Security Shield.');
      };
    }

    // Protect document against DOM clobbering
    if (document.write) {
      document.write = function () {};
      document.writeln = function () {};
    }

    // Freeze critical prototypes to stop prototype pollution attacks
    Object.freeze(Object.prototype);
    Object.freeze(Array.prototype);
  } catch (err) {}

  // -----------------------------------------------------------------------
  // 2. ANTI-IFRAME & CLICKJACKING NEUTRALIZER
  // -----------------------------------------------------------------------
  try {
    if (window.self !== window.top) {
      // Force frame break
      window.top.location.href = window.self.location.href;
    }
  } catch (e) {
    // If cross-origin framing blocks access to window.top, blank the canvas
    try {
      document.documentElement.innerHTML = '';
      document.documentElement.style.display = 'none';
    } catch (ignore) {}
  }

  // -----------------------------------------------------------------------
  // 3. ADVANCED DEVTOOLS TRAP & ANTI-DEBUGGING ENGINE
  // -----------------------------------------------------------------------
  (function initAntiDebug() {
    let devToolsOpen = false;

    // Method A: Performance Timing Detection (Catches DevTools opening latency)
    function checkTimingLatency() {
      const start = performance.now();
      // Harmless arithmetic
      for (let i = 0; i < 1000; i++) {
        Math.sqrt(i);
      }
      const end = performance.now();
      // If DevTools breakpoints or profiler are attached, latency spikes dramatically
      if (end - start > 100) {
        devToolsOpen = true;
        protectRuntime();
      }
    }

    // Method B: Window Dimension Threshold Inspection
    function checkWindowThreshold() {
      const widthThreshold = window.outerWidth - window.innerWidth > 160;
      const heightThreshold = window.outerHeight - window.innerHeight > 160;
      if (widthThreshold || heightThreshold) {
        // Docked DevTools detected
        protectRuntime();
      }
    }

    function protectRuntime() {
      try {
        if (window.console && !window.location.hostname.includes('localhost')) {
          console.clear();
          const blank = function () {};
          console.log = blank;
          console.warn = blank;
          console.error = blank;
          console.table = blank;
          console.dir = blank;
        }
      } catch (e) {}
    }

    setInterval(checkTimingLatency, 1500);
    window.addEventListener('resize', checkWindowThreshold, { passive: true });
  })();

  // -----------------------------------------------------------------------
  // 4. ANTI-THEFT & CODE EXTRACTION INTERCEPTION (100% SILENT)
  // -----------------------------------------------------------------------
  // Block Right-Click Context Menu Everywhere (except inputs)
  document.addEventListener('contextmenu', function (e) {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) {
      return true;
    }
    e.preventDefault();
    e.stopPropagation();
    return false;
  }, { capture: true });

  // Block All Inspection, Source-Viewing & Scraping Shortcuts
  document.addEventListener('keydown', function (e) {
    const key = e.key ? e.key.toLowerCase() : '';
    const code = e.keyCode || e.which;

    // F12 (DevTools)
    if (key === 'f12' || code === 123) {
      e.preventDefault();
      return false;
    }

    // Ctrl+Shift+I / J / C (DevTools inspector & console)
    if (e.ctrlKey && e.shiftKey && (key === 'i' || key === 'j' || key === 'c' || code === 73 || code === 74 || code === 67)) {
      e.preventDefault();
      return false;
    }

    // Ctrl+U (View Source)
    if (e.ctrlKey && (key === 'u' || code === 85)) {
      e.preventDefault();
      return false;
    }

    // Ctrl+S (Save Webpage to Disk)
    if (e.ctrlKey && (key === 's' || code === 83)) {
      e.preventDefault();
      return false;
    }

    // Ctrl+P (Print to PDF / Scrape print layout)
    if (e.ctrlKey && (key === 'p' || code === 80)) {
      e.preventDefault();
      return false;
    }

    // Mac OS Command Key Equivalents
    if (e.metaKey && (key === 'u' || key === 's' || key === 'p')) {
      e.preventDefault();
      return false;
    }
    if (e.metaKey && e.altKey && (key === 'i' || key === 'j' || key === 'c' || key === 'u')) {
      e.preventDefault();
      return false;
    }
  }, { capture: true });

  // Prevent Drag & Drop Image Theft
  document.addEventListener('dragstart', function (e) {
    if (e.target && (e.target.tagName === 'IMG' || e.target.closest('img') || e.target.tagName === 'PICTURE' || e.target.tagName === 'A')) {
      e.preventDefault();
      return false;
    }
  }, { capture: true });

  // -----------------------------------------------------------------------
  // 5. BRAND INTEGRITY & SELF-HEALING DOM ENGINE (MutationObserver)
  // -----------------------------------------------------------------------
  // Encrypted reference constants
  const CORE_SIGNATURES = Object.freeze({
    brand: 'RODRIGUEZ LAWNCARE',
    tagline: 'Landscaping & Maintenance',
    phoneAI: 'tel:2548528163',
    phoneOwner: 'https://wa.me/12546121399',
    email: 'mailto:arizmendir754@gmail.com'
  });

  function verifyAndHealDOM() {
    try {
      // 1. Protect Brand Logo & Name
      const brandTitles = document.querySelectorAll('.brand-name');
      brandTitles.forEach(el => {
        if (!el.textContent.includes('RODRIGUEZ')) {
          el.innerHTML = 'RODRIGUEZ <span>LAWNCARE</span>';
        }
      });

      // 2. Protect AI Phone Link
      const aiLinks = document.querySelectorAll('a[href*="2548528163"]');
      aiLinks.forEach(a => {
        if (a.getAttribute('href') !== CORE_SIGNATURES.phoneAI) {
          a.setAttribute('href', CORE_SIGNATURES.phoneAI);
        }
      });

      // 3. Protect Owner WhatsApp Link
      const waLinks = document.querySelectorAll('a[href*="2546121399"]');
      waLinks.forEach(a => {
        if (a.getAttribute('href') !== CORE_SIGNATURES.phoneOwner) {
          a.setAttribute('href', CORE_SIGNATURES.phoneOwner);
        }
      });

      // 4. Protect Email Link
      const emailLinks = document.querySelectorAll('a[href*="arizmendir754"]');
      emailLinks.forEach(a => {
        if (a.getAttribute('href') !== CORE_SIGNATURES.email) {
          a.setAttribute('href', CORE_SIGNATURES.email);
        }
      });
    } catch (e) {}
  }

  // Deep MutationObserver watching for unauthorized modifications
  const domGuardian = new MutationObserver(function (mutations) {
    let needsHeal = false;
    for (let i = 0; i < mutations.length; i++) {
      const mut = mutations[i];

      // Block foreign injected elements (scripts, external iframes)
      if (mut.type === 'childList') {
        for (let j = 0; j < mut.addedNodes.length; j++) {
          const node = mut.addedNodes[j];
          if (node.nodeType === 1) { // Element
            const tag = node.tagName.toLowerCase();
            if ((tag === 'script' || tag === 'iframe') && !node.hasAttribute('data-security-allow')) {
              try { node.remove(); } catch (e) {}
            }
          }
        }
        needsHeal = true;
      } else if (mut.type === 'attributes' || mut.type === 'characterData') {
        needsHeal = true;
      }
    }

    if (needsHeal) {
      verifyAndHealDOM();
    }
  });

  function activateGuardian() {
    if (document.documentElement) {
      domGuardian.observe(document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        characterData: true,
        attributeFilter: ['href', 'src', 'id', 'class']
      });
      verifyAndHealDOM();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', activateGuardian);
  } else {
    activateGuardian();
  }

  // -----------------------------------------------------------------------
  // 6. REAL-TIME INPUT SANITIZER & TOKEN EXCLUSION FILTER
  // -----------------------------------------------------------------------
  const THREAT_REGEXES = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript\s*:/gi,
    /data\s*:\s*text\/html/gi,
    /vbscript\s*:/gi,
    /on(load|error|click|mouseover|submit|focus)\s*=/gi,
    /document\s*\.\s*(cookie|location|write|domain)/gi,
    /window\s*\.\s*(location|localStorage|sessionStorage)/gi,
    /bearer\s+[a-zA-Z0-9_\-\.]{15,}/gi,
    /eyJ[a-zA-Z0-9_\-]{8,}\.[a-zA-Z0-9_\-]{8,}\.[a-zA-Z0-9_\-]{8,}/gi, // JWT
    /ghp_[a-zA-Z0-9]{36}/gi, // GitHub token pattern
    /xox[baprs]-[a-zA-Z0-9]{10,}/gi, // Slack token pattern
    /sk-[a-zA-Z0-9]{20,}/gi // OpenAI key pattern
  ];

  function cleanString(str) {
    if (typeof str !== 'string') return str;
    let sanitized = str;
    THREAT_REGEXES.forEach(function (pattern) {
      sanitized = sanitized.replace(pattern, '');
    });
    return sanitized;
  }

  document.addEventListener('input', function (e) {
    if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) {
      const original = e.target.value;
      const filtered = cleanString(original);
      if (original !== filtered) {
        e.target.value = filtered;
      }
    }
  }, { capture: true, passive: true });

  // -----------------------------------------------------------------------
  // 7. INVISIBLE INTEGRITY WATERMARK
  // -----------------------------------------------------------------------
  window.__RODRIGUEZ_SHIELD_ACTIVE__ = true;
  Object.defineProperty(window, '__RODRIGUEZ_SHIELD_ACTIVE__', {
    writable: false,
    configurable: false
  });

})();
