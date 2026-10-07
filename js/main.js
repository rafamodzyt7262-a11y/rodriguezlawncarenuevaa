/**
 * RODRIGUEZ LAWN CARE & LANDSCAPING - MASTER JAVASCRIPT
 * Interactive features: Language switch, Before/After Slider,
 * Dynamic Price Calculator, Service Area Checker, Contact & WhatsApp Integration.
 */

// --- Translation Dictionary (ES / EN) ---
const translations = {
  en: {
    // Top Bar & Nav
    top_badge: '🤝 Direct Homeowners & Contractors Welcome',
    top_hours: 'Mon - Sat: 7:00 AM - 7:00 PM',
    top_free_quote: '24/7 AI Estimate: (254) 852-8163',
    nav_services: 'Services',
    nav_before_after: 'Before & After',
    nav_calculator: 'Live Calculator',
    nav_why_us: 'About Us',
    nav_reviews: 'Reviews',
    nav_contact: 'Contact',
    nav_quote_btn: 'Get Free Quote',

    // Hero
    hero_badge: '🌿 Professional Lawn Care & Landscaping',
    hero_title_1: 'Your Dream Lawn,',
    hero_title_2: 'Flawlessly Maintained',
    hero_desc: 'Crisp commercial stripe mowing, razor-sharp concrete edging, and premium landscape care. Available for direct homeowner jobs and general contractors.',
    hero_cta_calc: 'Calculate Instant Price',
    hero_cta_call: 'Call (254) 852-8163 (24/7 AI)',
    hero_trust_1: 'Direct Work & Contractor Jobs',
    hero_trust_2: 'Total Satisfaction Guaranteed',
    hero_trust_3: '10+ Years Making Yards Beautiful',

    // Hero Card
    hero_card_title: 'Quick 1-Minute Estimate',
    hero_card_sub: 'Get your free, no-obligation quote today',
    form_name: 'Full Name',
    form_phone: 'Phone Number',
    form_service_select: 'Services Needed (Check all that apply)',
    form_opt_mowing: 'Recurring Mowing & Edging',
    form_opt_mulch: 'Mulch & Flower Bed Refresh',
    form_opt_cleanup: 'Seasonal Deep Yard Cleanup',
    form_opt_trimming: 'Shrub & Hedge Trimming',
    form_opt_commercial: 'Commercial Grounds Maintenance',
    hero_card_btn: 'Get My Free Estimate',
    hero_feat_no_contract: 'No Long-Term Contracts',
    hero_feat_free_est: '100% Free Estimates',

    // Before & After
    ba_badge_sec: 'Proven Results',
    ba_title: 'See the Dramatic Transformation',
    ba_sub: 'Slide left and right to inspect the real difference our professional equipment and detail make.',
    ba_tag_before: 'Before: Overgrown',
    ba_tag_after: 'After: Rodriguez Lawn Care',
    ba_before_title: 'Before Our Visit',
    ba_before_1: 'Wild overgrown weeds and tall unkempt grass',
    ba_before_2: 'Ragged overgrown sidewalk edges',
    ba_before_3: 'Dry, neglected flower beds full of dandelions',
    ba_after_title: 'After Rodriguez Service',
    ba_after_1: 'Uniform cut with immaculate mowing stripes',
    ba_after_2: '90-degree crisp sidewalk edging & blown clean',
    ba_after_3: 'Fresh rich dark mulch & precision trimmed shrubs',

    // Calculator
    calc_badge: 'Transparent Pricing',
    calc_title: 'Instant Online Lawn Quote Calculator',
    calc_sub: 'Select your property specs to get an immediate estimated price per visit.',
    calc_step_1: '1. Select Your Property Size',
    calc_size_sm: 'Small Yard',
    calc_size_sm_sub: 'Up to 3,000 sq ft (~compact lawn)',
    calc_size_md: 'Medium Yard',
    calc_size_md_sub: '3,000 - 8,000 sq ft (~typical suburban)',
    calc_size_lg: 'Large Yard',
    calc_size_lg_sub: '8,000 - 15,000 sq ft (~corner or estate)',
    calc_step_2: '2. Services You Need',
    calc_srv_mowing: 'Lawn Mowing & Edging',
    calc_srv_mowing_sub: 'Includes perimeter edging & blowing',
    calc_srv_trim: 'Shrub & Hedge Trimming',
    calc_srv_trim_sub: 'Sculpted neat bush shaping',
    calc_srv_mulch: 'Fresh Garden Bed Mulching',
    calc_srv_mulch_sub: 'Retains moisture & stops weeds',
    calc_srv_clean: 'Seasonal Leaf & Debris Cleanup',
    calc_srv_clean_sub: 'Total leaf haul & yard clearing',
    calc_step_3: '3. Service Frequency',
    calc_freq_weekly: 'Weekly',
    calc_freq_weekly_sub: 'Save 15% - Most Popular',
    calc_freq_biweekly: 'Bi-Weekly',
    calc_freq_biweekly_sub: 'Save 10%',
    calc_freq_onetime: 'One-Time',
    calc_freq_onetime_sub: 'Standard Rate',
    calc_sum_badge: 'Instant Estimate',
    calc_sum_title: 'Your Estimated Rate',
    calc_sum_label: 'Estimated Price Per Visit',
    calc_feat_1: 'No mandatory contracts - cancel anytime',
    calc_feat_2: 'Commercial equipment with blades sharpened daily',
    calc_feat_3: 'Pet-friendly crews & latched gates guaranteed',
    calc_lock_btn: 'Lock In Rate & Schedule Service',

    // Services
    srv_badge: 'Our Services',
    srv_title: 'Expert Solutions for Every Outdoor Space',
    srv_sub: 'From weekly precision mowing to complete landscape revamps.',
    srv_mow_title: 'Front & Back Yard Cut + Edging',
    srv_mow_desc: 'Cutting at optimal turf height for both front and back yards, crisp sidewalk string edging, and complete concrete blowing.',
    srv_trim_title: 'Shrub & Hedge Trimming',
    srv_trim_desc: 'Health-promoting pruning and geometric shaping to keep your shrubs healthy, tidy, and complementing your curb appeal.',
    srv_tree_cut_title: 'Tree Cutting & Trimming',
    srv_tree_cut_desc: 'Safe limb removal, canopy elevation pruning, storm hazard branch cutting, and complete wood haul-away.',
    srv_tree_plant_title: 'Tree Planting & Installation',
    srv_tree_plant_desc: 'Expert planting of shade and ornamental trees, rich organic soil fertilization, staking, and deep hydration.',
    srv_clean_title: 'Leaf Cleanup & Raking',
    srv_clean_desc: 'Intensive leaf raking, seasonal yard bed clearing, lawn vacuuming, and organic haul-away to keep turf breathing.',
    srv_junk_title: 'Yard Debris Clearing & Junk Removal',
    srv_junk_desc: 'Clearing backyard debris, fallen limbs, bulky unwanted items, scrap, and full-service junk removal and hauling.',

    // Why us
    why_badge: 'Why Rodriguez Lawn Care?',
    why_title: 'Family Pride, Professional Execution',
    why_desc: 'At Rodriguez Lawn Care, we treat every lawn like our own. We aren’t a faceless corporate app; we are a dedicated family team committed to perfection every time.',
    pillar_1_title: 'Dependable Reliability',
    pillar_1_desc: 'We assign a dedicated service day so you always know when we are coming. Gates are always firmly latched.',
    pillar_2_title: 'Top-Grade Commercial Gear',
    pillar_2_desc: 'We use commercial zero-turn mowers with blades sharpened daily to ensure a clean, healthy cut without bruising the grass.',
    pillar_3_title: 'Warm, Clear Communication',
    pillar_3_desc: 'Quick responses to calls and messages. Fully fluent in both English and Spanish for seamless coordination.',
    pillar_4_title: 'Transparent, Honest Quotes',
    pillar_4_desc: 'Straightforward, upfront pricing with zero hidden fees. Easy payments via Zelle, cards, or checks.',

    // Stats
    stat_1_num: '1,500+',
    stat_1_lbl: 'Yards Beautified',
    stat_2_num: '99.8%',
    stat_2_lbl: 'Satisfied Homeowners',
    stat_3_num: '10+',
    stat_3_lbl: 'Years of Experience',
    stat_4_num: '5.0★',
    stat_4_lbl: 'Average Rating',

    // Area Checker
    area_badge: 'Service Area',
    area_title: 'Do We Service Your Neighborhood?',
    area_sub: 'Enter your ZIP Code or City to check service in Killeen, Harker Heights, Copperas Cove, or Belton.',
    area_placeholder: 'e.g. Killeen, Harker Heights, Copperas Cove, Belton',
    area_btn: 'Check Availability',

    // Testimonials
    rev_badge: 'Customer Reviews',
    rev_title: 'What Your Neighbors Are Saying',
    rev_sub: 'Real feedback from homeowners and businesses who trust Rodriguez Lawn Care.',

    // FAQ
    faq_badge: 'Frequently Asked Questions',
    faq_title: 'Got Questions? We Have Answers',
    faq_sub: 'Everything you need to know about starting service with us.',
    faq_q1: 'Do I need to be home during service?',
    faq_a1: 'No, you do not need to be home. As long as our crew has safe gate access to the backyard and pets are safely inside, we take care of everything and send you a confirmation photo.',
    faq_q2: 'What payment methods do you accept?',
    faq_a2: 'We make payment effortless: we accept Zelle, credit/debit cards, bank transfers, checks, and cash. Instant digital receipts are sent to your email or phone.',
    faq_q3: 'What happens if it rains on my scheduled day?',
    faq_a3: 'To protect your lawn from rutting and soggy soil damage, wet weather delays are automatically rescheduled to the very next dry day available.',
    faq_q4: 'Are you fully insured?',
    faq_a4: 'Yes, Rodriguez Lawn Care carries full Commercial General Liability Insurance for total peace of mind on every single property.',

    // Contact
    contact_badge: 'Get in Touch',
    contact_title: 'Ready for an Immaculate Lawn?',
    contact_sub: 'Send us a message or call today. We respond within 30 minutes.',
    contact_info_title: 'Contact Information',
    contact_info_desc: 'We work directly with private homeowners and partner with general contractors. Request your custom estimate or schedule an on-site visit today.',
    contact_call: '24/7 AI Estimate Line',
    contact_whatsapp: 'Owner Direct WhatsApp',
    contact_email: 'Email Address',
    contact_hours: 'Working Hours',
    contact_form_title: 'Schedule a Visit or Estimate',
    booking_form_heading: 'Schedule an On-Site Visit or Estimate',
    booking_form_subheading: 'Enter your details, preferred date & time, and describe what you need. Your info will reach the owner instantly.',
    form_lbl_name: '👤 Full Name',
    form_lbl_phone: '📱 Contact Phone',
    form_lbl_address: '📍 Full Property Address',
    form_lbl_date: '📅 Preferred Visit Date',
    form_lbl_time: '⏰ Preferred Time Window',
    form_lbl_service: '🌿 Services Needed (Check all that apply)',
    form_lbl_freq: '🔄 Preferred Frequency',
    form_lbl_desc: '📝 Job Description (Write whatever you need)',
    form_submit_btn: '🚀 Send Request to Rodriguez LawnCare',
    srv_opt_lawn: 'Front & Back Yard Cut',
    srv_opt_edging: 'Perimeter Edging (Sidewalks & Driveways)',
    srv_opt_trimming: 'Shrub & Hedge Trimming',
    srv_opt_tree_cut: 'Tree Cutting & Trimming',
    srv_opt_tree_plant: 'Tree Planting & Installation',
    srv_opt_leaves: 'Leaf Cleanup & Raking',
    srv_opt_debris: 'Yard Debris & Brush Clearing',
    srv_opt_junk: 'Junk Removal & Hauling',

    // Modal
    modal_title: 'Request Ready to Send!',
    modal_desc: 'Your details are ready. Click below to send your request directly to Rodriguez LawnCare at (254) 612-1399.',
    modal_whatsapp_btn: '💬 Send Details via WhatsApp to (254) 612-1399',
    modal_close: 'Close window'
  }
};

let currentLang = 'en';

// --- Initialize DOM on Load ---
document.addEventListener('DOMContentLoaded', () => {
  initLanguage();
  initBeforeAfterSlider();
  initPriceCalculator();
  initAreaChecker();
  initFaqAccordion();
  initBookingForms();
  initNavbarScroll();
  initMobileMenu();
});

// --- 1. LANGUAGE INITIALIZATION (100% ENGLISH) ---
function initLanguage() {
  localStorage.removeItem('rodriguez_lawn_lang');
  setLanguage('en');
}

function setLanguage(lang) {
  currentLang = 'en';

  // Update all elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations.en[key]) {
      el.innerHTML = translations.en[key];
    }
  });

  // Update placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (translations.en[key]) {
      el.setAttribute('placeholder', translations.en[key]);
    }
  });

  // Recalculate price text
  updateCalculatorDisplay();
}

// --- 2. BEFORE & AFTER INTERACTIVE SLIDER ---
function initBeforeAfterSlider() {
  const container = document.getElementById('baSlider');
  const afterImage = document.getElementById('baAfterImg');
  const handle = document.getElementById('baHandle');

  if (!container || !afterImage || !handle) return;

  let isDragging = false;

  function setSliderPosition(xPos) {
    const rect = container.getBoundingClientRect();
    let offsetX = xPos - rect.left;
    let percentage = (offsetX / rect.width) * 100;

    // Clamp between 5% and 95%
    if (percentage < 5) percentage = 5;
    if (percentage > 95) percentage = 95;

    afterImage.style.width = `${percentage}%`;
    handle.style.left = `${percentage}%`;
  }

  // Mouse Events
  container.addEventListener('mousedown', (e) => {
    isDragging = true;
    setSliderPosition(e.clientX);
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    setSliderPosition(e.clientX);
  });

  // Touch Events for Mobile
  container.addEventListener('touchstart', (e) => {
    isDragging = true;
    setSliderPosition(e.touches[0].clientX);
  }, { passive: true });

  window.addEventListener('touchend', () => {
    isDragging = false;
  });

  window.addEventListener('touchmove', (e) => {
    if (!isDragging) return;
    setSliderPosition(e.touches[0].clientX);
  }, { passive: true });
}

// --- 3. DYNAMIC PRICE CALCULATOR ---
let calcState = {
  size: 'md',
  sizeBase: 65,
  services: {
    mowing: true,
    trim: false,
    mulch: false,
    clean: false
  },
  frequency: 'weekly',
  freqDiscount: 0.15
};

const serviceRates = {
  mowing: 0, // Included in base yard size
  trim: 30,
  mulch: 55,
  clean: 45
};

const sizeRates = {
  sm: 47, // Yields $40 on weekly (15% off)
  md: 65, // Yields $55 on weekly (15% off)
  lg: 94  // Yields $80 on weekly (15% off)
};

function initPriceCalculator() {
  // Size Cards Click
  const sizeCards = document.querySelectorAll('.size-option-card');
  sizeCards.forEach(card => {
    card.addEventListener('click', () => {
      sizeCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const sizeVal = card.getAttribute('data-size');
      calcState.size = sizeVal;
      calcState.sizeBase = sizeRates[sizeVal];
      updateCalculatorDisplay();
    });
  });

  // Service Checkboxes
  const serviceItems = document.querySelectorAll('.service-calc-item');
  serviceItems.forEach(item => {
    const chk = item.querySelector('input[type="checkbox"]');
    const srvKey = item.getAttribute('data-srv');
    
    // Core base mowing is always included in the base rate
    if (srvKey === 'mowing') {
      item.style.cursor = 'default';
      return;
    }

    item.addEventListener('click', (e) => {
      // Toggle checked state cleanly
      chk.checked = !chk.checked;
      calcState.services[srvKey] = chk.checked;
      
      if (chk.checked) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
      updateCalculatorDisplay();
    });
  });

  // Frequency Radios
  const freqPills = document.querySelectorAll('.freq-pill');
  freqPills.forEach(pill => {
    pill.addEventListener('click', () => {
      freqPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const freqVal = pill.getAttribute('data-freq');
      calcState.frequency = freqVal;
      if (freqVal === 'weekly') calcState.freqDiscount = 0.15;
      else if (freqVal === 'biweekly') calcState.freqDiscount = 0.10;
      else calcState.freqDiscount = 0.0;
      updateCalculatorDisplay();
    });
  });

  // Lock Rate Button Click -> Transfers to Booking Form
  const lockBtn = document.getElementById('lockRateBtn');
  if (lockBtn) {
    lockBtn.addEventListener('click', () => {
      const contactSection = document.getElementById('contact');
      if (contactSection) {
        contactSection.scrollIntoView({ behavior: 'smooth' });

        // Pre-fill form service checkboxes based on calculator
        if (calcState.services.mowing) {
          const cb = document.querySelector('#mainServiceCheckboxes input[value="Front & Back Yard Cut"]');
          if (cb) { cb.checked = true; cb.closest('.service-checkbox-item')?.classList.add('checked'); }
          const cbEdge = document.querySelector('#mainServiceCheckboxes input[value="Perimeter Edging"]');
          if (cbEdge) { cbEdge.checked = true; cbEdge.closest('.service-checkbox-item')?.classList.add('checked'); }
        }
        if (calcState.services.trim) {
          const cb = document.querySelector('#mainServiceCheckboxes input[value="Shrub & Hedge Trimming"]');
          if (cb) { cb.checked = true; cb.closest('.service-checkbox-item')?.classList.add('checked'); }
        }
        if (calcState.services.clean) {
          const cb = document.querySelector('#mainServiceCheckboxes input[value="Leaf Cleanup & Raking"]');
          if (cb) { cb.checked = true; cb.closest('.service-checkbox-item')?.classList.add('checked'); }
        }
        if (calcState.services.mulch) {
          const cb = document.querySelector('#mainServiceCheckboxes input[value="Yard Debris Clearing"]');
          if (cb) { cb.checked = true; cb.closest('.service-checkbox-item')?.classList.add('checked'); }
        }

        const formFreq = document.getElementById('formFrequency');
        const formDesc = document.getElementById('formDescription');

        if (formFreq) {
          formFreq.value = calcState.frequency === 'weekly' ? 'Weekly (15% OFF)' : (calcState.frequency === 'biweekly' ? 'Bi-Weekly (10% OFF)' : 'One-Time Service');
        }

        if (formDesc) {
          const estimatedPrice = calculateTotalPrice();
          const noteText = `Online estimated quote: ~$${estimatedPrice}/visit (Size: ${calcState.size.toUpperCase()}, Frequency: ${calcState.frequency}). Looking to confirm visit availability.`;
          formDesc.value = noteText;
        }
      }
    });
  }

  updateCalculatorDisplay();
}

function calculateTotalPrice() {
  let subtotal = calcState.sizeBase;

  // Add selected additional services
  Object.keys(calcState.services).forEach(key => {
    if (calcState.services[key] && serviceRates[key]) {
      subtotal += serviceRates[key];
    }
  });

  // Apply discount with $40 minimum floor
  const finalPrice = Math.max(40, Math.round(subtotal * (1 - calcState.freqDiscount)));
  return finalPrice;
}

function updateCalculatorDisplay() {
  const priceEl = document.getElementById('calculatedPrice');
  if (!priceEl) return;

  const targetPrice = calculateTotalPrice();
  animateCounter(priceEl, targetPrice);

  const periodEl = document.getElementById('pricePeriod');
  if (periodEl) {
    if (calcState.frequency === 'weekly') {
      periodEl.textContent = '/ weekly visit';
    } else if (calcState.frequency === 'biweekly') {
      periodEl.textContent = '/ bi-weekly visit';
    } else {
      periodEl.textContent = '/ one-time service';
    }
  }
}

function animateCounter(element, target) {
  const current = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
  if (current === target) return;

  const duration = 250;
  const stepTime = 20;
  const steps = duration / stepTime;
  const increment = (target - current) / steps;
  let currentVal = current;
  let step = 0;
  const timer = setInterval(() => {
    step++;
    currentVal += increment;
    if (step >= steps) {
      clearInterval(timer);
      element.textContent = target;
    } else {
      element.textContent = Math.round(currentVal);
    }
  }, stepTime);
}

// --- 4. SERVICE AREA ZIP CODE CHECKER ---
function initAreaChecker() {
  const areaForm = document.getElementById('areaForm');
  const zipInput = document.getElementById('zipInput');
  const resultBox = document.getElementById('areaResult');

  if (!areaForm || !zipInput || !resultBox) return;

  areaForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = zipInput.value.trim().toLowerCase();

    if (!query) return;

    // Service areas: Killeen, Harker Heights, Copperas Cove, Belton & their ZIP codes
    const coveredKeywords = [
      'killeen', 'harker heights', 'harker', 'copperas cove', 'copperas', 'cove', 'belton',
      '76540', '76541', '76542', '76543', '76544', '76547', '76548', '76549',
      '76522', '76513'
    ];

    const isCovered = coveredKeywords.some(keyword => query.includes(keyword));

    resultBox.className = 'area-result-box';
    if (isCovered) {
      resultBox.classList.add('success');
      resultBox.innerHTML = `<span>✓</span> <strong>Great news! We service your area.</strong> We have active routes and weekly openings in Killeen, Harker Heights, Copperas Cove, and Belton.`;
    } else {
      resultBox.classList.add('warning');
      resultBox.innerHTML = `<span>ℹ</span> We exclusively service Killeen, Harker Heights, Copperas Cove, and Belton. Please call us at (254) 612-1399 for nearby inquiries!`;
    }
    resultBox.style.display = 'flex';
  });
}

// --- 5. FAQ ACCORDION ---
function initFaqAccordion() {
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');

    questionBtn.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      // Close all other items
      faqItems.forEach(other => {
        other.classList.remove('active');
        const otherAns = other.querySelector('.faq-answer');
        if (otherAns) otherAns.style.maxHeight = null;
      });

      if (!isActive) {
        item.classList.add('active');
        answer.style.maxHeight = answer.scrollHeight + 30 + 'px';
      }
    });
  });
}

// --- 6. BOOKING FORMS & MODAL ---
let activeWhatsAppUrl = 'https://wa.me/12546121399';

function initBookingForms() {
  const mainForm = document.getElementById('bookingForm');
  const heroForm = document.getElementById('heroQuickForm');
  const modal = document.getElementById('confirmationModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalCloseCross = document.getElementById('modalCloseCross');
  const whatsappModalBtn = document.getElementById('whatsappModalBtn');
  const modalSummaryContent = document.getElementById('modalSummaryContent');
  const dateInput = document.getElementById('formDate');

  // Set default & minimum date to tomorrow
  if (dateInput) {
    const today = new Date();
    dateInput.min = today.toISOString().split('T')[0];
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.value = tomorrow.toISOString().split('T')[0];
  }

  // Synchronize checkbox item styles on change
  document.querySelectorAll('.service-checkbox-item input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      const parent = checkbox.closest('.service-checkbox-item');
      if (parent) {
        if (checkbox.checked) {
          parent.classList.add('checked');
        } else {
          parent.classList.remove('checked');
        }
      }
    });
  });

  function getSelectedServices(containerId, defaultService) {
    const container = document.getElementById(containerId);
    if (!container) return [defaultService];
    const checked = Array.from(container.querySelectorAll('input[type="checkbox"]:checked'))
      .map(cb => cb.value.trim());
    return checked.length > 0 ? checked : [defaultService];
  }

  function handleAppointmentSubmit(data) {
    const servicesList = Array.isArray(data.services) && data.services.length > 0
      ? data.services
      : [data.service || 'Front & Back Yard Cut'];

    const servicesBullets = servicesList.map(s => `  • ${s}`).join('\n');

    // Build WhatsApp message (100% English)
    const waText = `🌱 *NEW SERVICE REQUEST - RODRIGUEZ LAWNCARE*

👤 *Name:* ${data.name}
📱 *Phone:* ${data.phone}
📍 *Address:* ${data.address}
📅 *Requested Date:* ${data.date}
⏰ *Time:* ${data.time}
🌿 *Requested Services:*
${servicesBullets}
🔄 *Frequency:* ${data.frequency}
📝 *Job Description:*
"${data.description}"`;

    activeWhatsAppUrl = `https://wa.me/12546121399?text=${encodeURIComponent(waText)}`;

    // Render detailed visual summary in modal (100% English)
    if (modalSummaryContent) {
      const pillsHtml = servicesList.map(s => `<span class="service-pill-tag">✓ ${s}</span>`).join('');
      modalSummaryContent.innerHTML = `
        <div class="modal-summary-row"><span class="modal-summary-label">👤 Customer:</span> <span class="modal-summary-val">${data.name}</span></div>
        <div class="modal-summary-row"><span class="modal-summary-label">📱 Phone:</span> <span class="modal-summary-val">${data.phone}</span></div>
        <div class="modal-summary-row"><span class="modal-summary-label">📍 Address:</span> <span class="modal-summary-val">${data.address}</span></div>
        <div class="modal-summary-row"><span class="modal-summary-label">📅 Date:</span> <span class="modal-summary-val">${data.date}</span></div>
        <div class="modal-summary-row"><span class="modal-summary-label">⏰ Time:</span> <span class="modal-summary-val">${data.time}</span></div>
        <div class="modal-summary-row" style="align-items: flex-start;">
          <span class="modal-summary-label">🌿 Services:</span>
          <div style="display: flex; flex-wrap: wrap; gap: 4px; max-width: 65%; justify-content: flex-end;">${pillsHtml}</div>
        </div>
        <div class="modal-summary-row" style="flex-direction: column; gap: 0.25rem;">
          <span class="modal-summary-label">📝 Description:</span>
          <span class="modal-summary-val" style="text-align: left; font-style: italic; background: #fff; padding: 0.5rem; border-radius: 6px; border: 1px solid #e2e8f0;">"${data.description}"</span>
        </div>
      `;
    }

    // Automatically trigger WhatsApp in new tab so owner receives it immediately
    window.open(activeWhatsAppUrl, '_blank');

    // Show modal on screen
    if (modal) {
      modal.classList.add('open');
    }
  }

  // Main Comprehensive Booking Form
  if (mainForm) {
    mainForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const services = getSelectedServices('mainServiceCheckboxes', 'Front & Back Yard Cut');
      const data = {
        name: document.getElementById('formName')?.value || 'Customer',
        phone: document.getElementById('formPhone')?.value || '',
        address: document.getElementById('formAddress')?.value || 'To be coordinated',
        date: document.getElementById('formDate')?.value || 'As soon as possible',
        time: document.getElementById('formTime')?.value || 'Flexible',
        services: services,
        service: services.join(', '),
        frequency: document.getElementById('formFrequency')?.value || 'To be decided',
        description: document.getElementById('formDescription')?.value || 'No additional notes'
      };

      handleAppointmentSubmit(data);
      mainForm.reset();
      const firstCb = document.querySelector('#mainServiceCheckboxes input[type="checkbox"]');
      if (firstCb) {
        firstCb.checked = true;
        firstCb.closest('.service-checkbox-item')?.classList.add('checked');
      }
      if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.value = tomorrow.toISOString().split('T')[0];
      }
    });
  }

  // Quick Hero Form
  if (heroForm) {
    heroForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const services = getSelectedServices('heroServiceCheckboxes', 'Front & Back Yard Cut');
      const data = {
        name: document.getElementById('heroName')?.value || 'Customer',
        phone: document.getElementById('heroPhone')?.value || '',
        address: 'To be confirmed by call/text',
        date: 'As soon as possible',
        time: 'Normal business hours',
        services: services,
        service: services.join(', '),
        frequency: 'To be decided',
        description: 'Quick request from website'
      };
      handleAppointmentSubmit(data);
      heroForm.reset();
      const firstHeroCb = document.querySelector('#heroServiceCheckboxes input[type="checkbox"]');
      if (firstHeroCb) {
        firstHeroCb.checked = true;
        firstHeroCb.closest('.service-checkbox-item')?.classList.add('checked');
      }
    });
  }

  function closeModal() {
    if (modal) modal.classList.remove('open');
  }

  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
  if (modalCloseCross) modalCloseCross.addEventListener('click', closeModal);
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }

  // WhatsApp Button inside Modal
  if (whatsappModalBtn) {
    whatsappModalBtn.addEventListener('click', () => {
      window.open(activeWhatsAppUrl, '_blank');
      closeModal();
    });
  }
}

// --- 7. NAVBAR SCROLL EFFECT ---
function initNavbarScroll() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

// --- 8. MOBILE MENU TOGGLE ---
function initMobileMenu() {
  const menuBtn = document.getElementById('mobileMenuBtn');
  const navLinks = document.getElementById('navLinks');

  if (!menuBtn || !navLinks) return;

  menuBtn.addEventListener('click', () => {
    navLinks.classList.toggle('mobile-active');
  });

  // Close mobile menu on link click
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('mobile-active');
    });
  });
}
