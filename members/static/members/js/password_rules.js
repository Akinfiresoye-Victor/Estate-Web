/* ═══════════════════════════════════════════════════
   password_rules.js — Live password requirement checker
   Works on all 3 register pages (customer, agent, company)
   ═══════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── Requirements ────────────────────────────────── */
  const RULES = [
    { id: 'req-length',   label: 'At least 8 characters',          test: v => v.length >= 8 },
    { id: 'req-upper',    label: 'At least one uppercase letter',   test: v => /[A-Z]/.test(v) },
    { id: 'req-lower',    label: 'At least one lowercase letter',   test: v => /[a-z]/.test(v) },
    { id: 'req-number',   label: 'At least one number',            test: v => /\d/.test(v) },
    { id: 'req-special',  label: 'At least one special character (@, #, !, etc.)', test: v => /[^A-Za-z0-9]/.test(v) },
  ];

  /* ── Build the requirements UI ───────────────────── */
  function buildPanel() {
    const panel = document.createElement('div');
    panel.id = 'pw-requirements-panel';
    panel.style.cssText = [
      'background:#1c2733',
      'border:1.5px solid rgba(193,155,118,.22)',
      'border-radius:8px',
      'padding:0.85rem 1rem',
      'margin-top:8px',
      'display:none',
      'animation:fadeUp .25s ease',
    ].join(';');

    const title = document.createElement('p');
    title.textContent = 'Password must contain:';
    title.style.cssText = 'font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:rgba(255,255,255,.4);margin:0 0 8px;font-family:Poppins,sans-serif;';
    panel.appendChild(title);

    const list = document.createElement('ul');
    list.style.cssText = 'list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:5px;';

    RULES.forEach(function (rule) {
      const li = document.createElement('li');
      li.id = rule.id;
      li.style.cssText = 'display:flex;align-items:center;gap:7px;font-size:.78rem;font-family:Poppins,sans-serif;color:rgba(255,255,255,.4);transition:color .2s;';
      li.innerHTML = `<i class="bi bi-circle" style="font-size:.7rem;flex-shrink:0;transition:color .2s;"></i> ${rule.label}`;
      list.appendChild(li);
    });

    panel.appendChild(list);
    return panel;
  }

  /* ── Update requirement colours ──────────────────── */
  function updateRules(value) {
    RULES.forEach(function (rule) {
      const li = document.getElementById(rule.id);
      if (!li) return;
      const icon = li.querySelector('i');
      const pass = rule.test(value);

      if (pass) {
        li.style.color = '#86efac';           /* green */
        icon.className = 'bi bi-check-circle-fill';
        icon.style.color = '#86efac';
      } else {
        li.style.color = 'rgba(255,255,255,.4)';
        icon.className = 'bi bi-circle';
        icon.style.color = 'rgba(255,255,255,.4)';
      }
    });
  }

  /* ── Confirm password match indicator ────────────── */
  function buildMatchIndicator() {
    const el = document.createElement('p');
    el.id = 'pw-match-indicator';
    el.style.cssText = 'font-size:.75rem;margin-top:6px;font-family:Poppins,sans-serif;font-weight:600;display:none;';
    return el;
  }

  function updateMatch(pw1, pw2) {
    const el = document.getElementById('pw-match-indicator');
    if (!el || !pw2) { if (el) el.style.display = 'none'; return; }
    el.style.display = 'block';
    if (pw1 === pw2) {
      el.textContent = '✓ Passwords match';
      el.style.color = '#86efac';
    } else {
      el.textContent = '✕ Passwords do not match';
      el.style.color = '#fca5a5';
    }
  }

  /* ── Strength bar ────────────────────────────────── */
  function buildStrengthBar() {
    const wrap = document.createElement('div');
    wrap.style.cssText = 'margin-top:8px;display:none;';
    wrap.id = 'pw-strength-wrap';

    const bar = document.createElement('div');
    bar.style.cssText = 'height:4px;background:rgba(255,255,255,.1);border-radius:4px;overflow:hidden;';

    const fill = document.createElement('div');
    fill.id = 'pw-strength-fill';
    fill.style.cssText = 'height:100%;width:0%;border-radius:4px;transition:width .3s ease,background .3s ease;';

    const label = document.createElement('p');
    label.id = 'pw-strength-label';
    label.style.cssText = 'font-size:.68rem;margin-top:4px;font-family:Poppins,sans-serif;font-weight:700;color:rgba(255,255,255,.4);';

    bar.appendChild(fill);
    wrap.appendChild(bar);
    wrap.appendChild(label);
    return wrap;
  }

  function updateStrength(value) {
    const wrap  = document.getElementById('pw-strength-wrap');
    const fill  = document.getElementById('pw-strength-fill');
    const label = document.getElementById('pw-strength-label');
    if (!wrap || !fill || !label) return;

    if (!value) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';

    const passed = RULES.filter(r => r.test(value)).length;

    const levels = [
      { pct: '20%', color: '#ef4444', text: 'Very Weak' },
      { pct: '40%', color: '#f97316', text: 'Weak' },
      { pct: '60%', color: '#f59e0b', text: 'Fair' },
      { pct: '80%', color: '#84cc16', text: 'Strong' },
      { pct: '100%',color: '#22c55e', text: 'Very Strong' },
    ];

    const level = levels[Math.min(passed - 1, 4)];
    if (level) {
      fill.style.width      = level.pct;
      fill.style.background = level.color;
      label.textContent     = level.text;
      label.style.color     = level.color;
    } else {
      fill.style.width = '0%';
      label.textContent = '';
    }
  }

  /* ── Toggle password visibility ──────────────────── */
  function addToggle(input) {
    if (!input) return;
    
    // Create a dedicated relative wrapper so the eye icon is perfectly centered
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    wrapper.style.display = 'flex';
    wrapper.style.alignItems = 'center';
    wrapper.style.width = '100%';
    
    // Insert the wrapper in the DOM tree right before the input, then move input inside it
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Toggle password visibility');
    btn.style.cssText = [
      'position:absolute',
      'right:0',
      'top:0',
      'height:100%',
      'width:44px',
      'background:none',
      'border:none',
      'cursor:pointer',
      'color:rgba(255,255,255,.5)',
      'font-size:1.15rem',
      'display:flex',
      'align-items:center',
      'justify-content:center',
      'transition:all .2s',
      'z-index: 10'
    ].join(';');
    btn.innerHTML = '<i class="bi bi-eye"></i>';

    btn.addEventListener('click', function () {
      const isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.querySelector('i').className = isHidden ? 'bi bi-eye-slash' : 'bi bi-eye';
      btn.style.color = isHidden ? 'rgba(193,155,118,.9)' : 'rgba(255,255,255,.5)';
    });

    btn.addEventListener('mouseenter', function () { 
      this.style.color = 'rgba(193,155,118, 1)'; 
      this.style.transform = 'scale(1.1)';
    });
    btn.addEventListener('mouseleave', function () {
      this.style.transform = 'scale(1)';
      if (input.type === 'password') this.style.color = 'rgba(255,255,255,.5)';
      else this.style.color = 'rgba(193,155,118,.9)';
    });

    // Add padding so text doesn't hide behind the eye button
    input.style.paddingRight = '3rem';
    
    wrapper.appendChild(btn);
  }

  /* ── Inject keyframe animation ───────────────────── */
  if (!document.getElementById('pw-rules-style')) {
    const style = document.createElement('style');
    style.id = 'pw-rules-style';
    style.textContent = `
      @keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
      input::-ms-reveal, input::-ms-clear { display: none; }
    `;
    document.head.appendChild(style);
  }

  /* ── Init on DOMContentLoaded ────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {

    // django-allauth and traditional Django forms use these common IDs
    const loginPw = document.getElementById('id_password');
    const registerPw1 = document.getElementById('id_password1');
    const registerPw2 = document.getElementById('id_password2');

    // 1. Apply eye toggle to ANY password input found
    if (loginPw) addToggle(loginPw);
    if (registerPw1) addToggle(registerPw1);
    if (registerPw2) addToggle(registerPw2);

    // 2. Only proceed with registration rules if id_password1 is present
    if (!registerPw1) return;

    /* -- Build and insert the requirements panel after registerPw1's wrapper -- */
    const panel = buildPanel();
    const strengthWrap = buildStrengthBar();

    // Insert after registerPw1's form-group wrapper
    const pw1Group = registerPw1.closest('.form-group') || registerPw1.parentElement;
    pw1Group.appendChild(strengthWrap);
    pw1Group.appendChild(panel);

    /* -- Build and insert match indicator after registerPw2's wrapper -- */
    const matchIndicator = buildMatchIndicator();
    if (registerPw2) {
      const pw2Group = registerPw2.closest('.form-group') || registerPw2.parentElement;
      pw2Group.appendChild(matchIndicator);
    }

    /* -- Show panel when registerPw1 is focused -- */
    registerPw1.addEventListener('focus', function () {
      panel.style.display = 'block';
      strengthWrap.style.display = 'block';
    });

    /* -- Live update rules and strength on registerPw1 input -- */
    registerPw1.addEventListener('input', function () {
      updateRules(this.value);
      updateStrength(this.value);
      if (registerPw2) updateMatch(this.value, registerPw2.value);
    });

    /* -- Live match check on registerPw2 input -- */
    if (registerPw2) {
      registerPw2.addEventListener('input', function () {
        updateMatch(registerPw1.value, this.value);
      });
    }

    /* -- Prevent form submit if requirements not met -- */
    const form = registerPw1.closest('form');
    if (form) {
      form.addEventListener('submit', function (e) {
        const allPassed = RULES.every(r => r.test(registerPw1.value));
        if (!allPassed) {
          e.preventDefault();
          panel.style.display = 'block';
          registerPw1.style.borderColor = '#fca5a5';
          registerPw1.style.boxShadow = '0 0 0 3px rgba(252,165,165,.18)';
          registerPw1.focus();
          // Reset border after user starts typing again
          registerPw1.addEventListener('input', function reset() {
            registerPw1.style.borderColor = '';
            registerPw1.style.boxShadow = '';
            registerPw1.removeEventListener('input', reset);
          });
          return;
        }
        if (registerPw2 && registerPw1.value !== registerPw2.value) {
          e.preventDefault();
          registerPw2.style.borderColor = '#fca5a5';
          registerPw2.style.boxShadow = '0 0 0 3px rgba(252,165,165,.18)';
          registerPw2.focus();
          registerPw2.addEventListener('input', function reset() {
            registerPw2.style.borderColor = '';
            registerPw2.style.boxShadow = '';
            registerPw2.removeEventListener('input', reset);
          });
        }
      });
    }

  });

}());