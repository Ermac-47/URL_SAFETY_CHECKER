/* ═══════════════════════════════════════════════════════════════
   SHIELDSCAN — scripts.js
   Shared across login.html + dashboard.html
   API: POST /login  /signup  /check  /check-batch
   ═══════════════════════════════════════════════════════════════ */

'use strict';

/* ─────────────────────────────────────────────────────────────
   1. CONSTANTS
───────────────────────────────────────────────────────────── */
const API_BASE       = 'http://127.0.0.1:5000';
const STORAGE_KEY    = 'shieldscan_history';
const USER_KEY       = 'shieldscan_user';
const MAX_HISTORY    = 200;
const SCAN_TIMEOUT_MS= 30000;          // 30 s per URL

/* ─────────────────────────────────────────────────────────────
   2. STATE
───────────────────────────────────────────────────────────── */
let scanHistory   = [];                // loaded in initDashboard()
let historyFilter = 'all';
let sortCol       = 'scannedAt';
let sortDir       = 'desc';
let batchMode     = false;
let pieChart      = null;
let barChart      = null;

/* ─────────────────────────────────────────────────────────────
   3. UTILITY — DOM
───────────────────────────────────────────────────────────── */
const $  = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function show(el) { if (el) el.style.display = ''; }
function hide(el) { if (el) el.style.display = 'none'; }
function toggleClass(el, cls, force) { if (el) el.classList.toggle(cls, force); }

/* ─────────────────────────────────────────────────────────────
   4. UTILITY — RIPPLE EFFECT
───────────────────────────────────────────────────────────── */
function addRipple(btn) {
  btn.addEventListener('click', function (e) {
    const r   = document.createElement('span');
    r.className = 'ripple';
    const rect = this.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    r.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX-rect.left-size/2}px;top:${e.clientY-rect.top-size/2}px;`;
    this.appendChild(r);
    setTimeout(() => r.remove(), 600);
  });
}

/* ─────────────────────────────────────────────────────────────
   5. TOAST SYSTEM
───────────────────────────────────────────────────────────── */
function showToast(msg, type = 'success', duration = 3500) {
  let stack = $('#toastStack');
  if (!stack) {
    stack = document.createElement('div');
    stack.id = 'toastStack';
    stack.className = 'toast-stack';
    document.body.appendChild(stack);
  }

  const icons = { success:'fa-circle-check', error:'fa-circle-xmark', warning:'fa-triangle-exclamation', info:'fa-circle-info' };
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `<i class="fa-solid ${icons[type] || icons.info} toast-icon"></i><span>${msg}</span>`;
  stack.appendChild(t);

  const dismiss = () => {
    t.classList.add('hide');
    setTimeout(() => t.remove(), 350);
  };
  t.addEventListener('click', dismiss);
  setTimeout(dismiss, duration);
}

/* ─────────────────────────────────────────────────────────────
   6. BUTTON LOADING STATE
───────────────────────────────────────────────────────────── */
function setBtnLoading(btn, loading) {
  if (!btn) return;
  toggleClass(btn, 'loading', loading);
  btn.disabled = loading;
}

/* ─────────────────────────────────────────────────────────────
   7. FIELD VALIDATION HELPERS
───────────────────────────────────────────────────────────── */
function fieldError(inputId, errId, show) {
  const inp = $(`#${inputId}`);
  const err = $(`#${errId}`);
  if (inp) toggleClass(inp, 'is-error', show);
  if (err) toggleClass(err, 'show', show);
}
function clearFieldErrors(...pairs) {
  pairs.forEach(([i, e]) => fieldError(i, e, false));
}

function isValidEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }
function isValidURL(v)   {
  try { new URL(v.startsWith('http') ? v : 'https://' + v); return true; }
  catch { return false; }
}

/* ─────────────────────────────────────────────────────────────
   8. PASSWORD STRENGTH METER
───────────────────────────────────────────────────────────── */
function updateStrength(val) {
  const fill  = $('#strengthFill');
  const label = $('#strengthLabel');
  if (!fill || !label) return;

  let score = 0;
  if (val.length >= 8)         score++;
  if (/[A-Z]/.test(val))       score++;
  if (/[0-9]/.test(val))       score++;
  if (/[^A-Za-z0-9]/.test(val))score++;

  const map = [
    { w:'0%',   c:'transparent',     t:'' },
    { w:'25%',  c:'var(--danger)',    t:'Weak' },
    { w:'55%',  c:'var(--suspicious)',t:'Fair' },
    { w:'80%',  c:'var(--accent)',    t:'Good' },
    { w:'100%', c:'var(--safe)',      t:'Strong ✓' },
  ];
  const s = val ? map[score] : map[0];
  fill.style.width      = s.w;
  fill.style.background = s.c;
  label.textContent     = s.t;
  label.style.color     = s.c;
}

/* ─────────────────────────────────────────────────────────────
   9. PASSWORD VISIBILITY TOGGLE
───────────────────────────────────────────────────────────── */
function togglePw(inputId, btn) {
  const inp  = $(`#${inputId}`);
  const icon = btn.querySelector('i');
  if (!inp) return;
  const isHidden = inp.type === 'password';
  inp.type  = isHidden ? 'text' : 'password';
  if (icon) icon.className = isHidden ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye';
}

/* ─────────────────────────────────────────────────────────────
   10. AUTH PANEL SWITCHER
───────────────────────────────────────────────────────────── */
function showPanel(name) {
  $$('.auth-panel').forEach(p => p.classList.remove('active'));
  $$('.tab-btn').forEach(b => b.classList.remove('active'));

  const panel = $(`#panel-${name}`);
  const tab   = $(`#tab-${name}`);
  if (panel) panel.classList.add('active');
  if (tab)   tab.classList.add('active');

  // clear global alerts
  ['#globalError','#globalSuccess'].forEach(sel => {
    const el = $(sel); if (el) el.classList.remove('show');
  });
}

function showAuthAlert(type, msg) {
  const error   = $('#globalError');
  const success = $('#globalSuccess');
  const errMsg  = $('#globalErrorMsg');
  const sucMsg  = $('#globalSuccessMsg');

  if (error)   error.classList.remove('show');
  if (success) success.classList.remove('show');

  if (type === 'error' && error && errMsg) {
    errMsg.textContent = msg; error.classList.add('show');
    error.classList.add('shake');
    setTimeout(() => error.classList.remove('shake'), 450);
  } else if (type === 'success' && success && sucMsg) {
    sucMsg.textContent = msg; success.classList.add('show');
  }
}

/* ─────────────────────────────────────────────────────────────
   11. LOGIN
───────────────────────────────────────────────────────────── */
async function handleLogin() {
  const username = ($('#loginUser')?.value  || '').trim();
  const password =  $('#loginPass')?.value  || '';

  clearFieldErrors(['loginUser','err-loginUser'], ['loginPass','err-loginPass']);
  showAuthAlert('', '');

  let valid = true;
  if (!username) { fieldError('loginUser','err-loginUser', true); valid = false; }
  if (!password) { fieldError('loginPass','err-loginPass', true); valid = false; }
  if (!valid) return;

  const btn = $('#loginBtn');
  setBtnLoading(btn, true);

  try {
    const res  = await fetchWithTimeout(`${API_BASE}/login`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (data.status === 'success') {
      localStorage.setItem(USER_KEY, username);
      showAuthAlert('success', 'Login successful — redirecting…');
      setTimeout(() => { window.location.href = 'dashboard.html'; }, 900);
    } else {
      showAuthAlert('error', data.message || 'Invalid credentials.');
    }
  } catch (e) {
    showAuthAlert('error', 'Cannot reach the server. Is Flask running on :5000?');
  } finally {
    setBtnLoading(btn, false);
  }
}

/* ─────────────────────────────────────────────────────────────
   12. REGISTER
───────────────────────────────────────────────────────────── */
async function handleRegister() {
  const first  = ($('#regFirst')?.value  || '').trim();
  const last   = ($('#regLast')?.value   || '').trim();
  const email  = ($('#regEmail')?.value  || '').trim();
  const user   = ($('#regUser')?.value   || '').trim();
  const pass   =  $('#regPass')?.value   || '';
  const pass2  =  $('#regPass2')?.value  || '';

  const fields = [['regFirst','err-regFirst'],['regLast','err-regLast'],
                  ['regEmail','err-regEmail'],['regUser','err-regUser'],
                  ['regPass','err-regPass'],  ['regPass2','err-regPass2']];
  clearFieldErrors(...fields);
  showAuthAlert('', '');

  let valid = true;
  if (!first)                             { fieldError('regFirst','err-regFirst',true); valid=false; }
  if (!last)                              { fieldError('regLast', 'err-regLast', true); valid=false; }
  if (!isValidEmail(email))              { fieldError('regEmail','err-regEmail',true); valid=false; }
  if (!user)                              { fieldError('regUser', 'err-regUser', true); valid=false; }
  if (!pass || pass.length < 8)          { fieldError('regPass', 'err-regPass', true); valid=false; }
  if (pass !== pass2)                    { fieldError('regPass2','err-regPass2',true);valid=false; }
  if (!valid) return;

  const btn = $('#registerBtn');
  setBtnLoading(btn, true);

  try {
    const res  = await fetchWithTimeout(`${API_BASE}/signup`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ username: user, password: pass })
    });
    const data = await res.json();

    if (data.status === 'success') {
      showAuthAlert('success', 'Account created! Signing you in…');
      setTimeout(() => showPanel('login'), 1400);
    } else {
      showAuthAlert('error', data.message || 'Registration failed.');
    }
  } catch (e) {
    showAuthAlert('error', 'Cannot reach the server. Is Flask running on :5000?');
  } finally {
    setBtnLoading(btn, false);
  }
}

/* ─────────────────────────────────────────────────────────────
   13. FORGOT PASSWORD (simulated — no backend endpoint yet)
───────────────────────────────────────────────────────────── */
function handleForgot() {
  const email = ($('#forgotEmail')?.value || '').trim();
  if (!isValidEmail(email)) { showAuthAlert('error','Enter a valid email address.'); return; }
  showAuthAlert('success','If that email is registered, a reset link has been sent.');
}

/* ─────────────────────────────────────────────────────────────
   14. OTP (simulated — wire backend when ready)
───────────────────────────────────────────────────────────── */
function sendOTP() {
  const phone = ($('#otpPhone')?.value || '').trim();
  if (!phone) { showAuthAlert('error','Enter a valid mobile number.'); return; }
  const disp = $('#otpPhoneDisplay');
  if (disp) disp.textContent = phone;
  hide($('#otpStep1'));
  show($('#otpStep2'));
  showAuthAlert('success','OTP sent! (Simulated — backend integration needed.)');
}

function otpNext(el, idx) {
  const cells = $$('.otp-cell');
  if (el.value && idx < 5) cells[idx + 1]?.focus();
}

function verifyOTP() {
  const otp = $$('.otp-cell').map(c => c.value).join('');
  if (otp.length < 6) { showAuthAlert('error','Enter all 6 digits.'); return; }
  showAuthAlert('success','OTP verified! (Simulated — connect to backend to complete login.)');
}

/* ─────────────────────────────────────────────────────────────
   15. FETCH WITH TIMEOUT
───────────────────────────────────────────────────────────── */
function fetchWithTimeout(url, opts, ms = SCAN_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  return fetch(url, { ...opts, signal: controller.signal })
    .finally(() => clearTimeout(timer));
}

/* ─────────────────────────────────────────────────────────────
   16. SCAN LOGIC
───────────────────────────────────────────────────────────── */
async function runScan() {
  const raw = ($('#urlInput')?.value || '').trim();
  if (!raw) { showToast('Paste a URL first.', 'error'); return; }

  const urls = batchMode
    ? raw.split('\n').map(u => u.trim()).filter(Boolean)
    : [raw];

  if (!urls.length) { showToast('No valid URLs found.', 'error'); return; }

  const btn = $('#scanBtn');
  setBtnLoading(btn, true);

  try {
    let results = [];

    if (urls.length === 1) {
      const res  = await fetchWithTimeout(`${API_BASE}/check`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ url: urls[0] })
      });
      results = [await res.json()];
    } else {
      const res  = await fetchWithTimeout(`${API_BASE}/check-batch`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ urls })
      });
      const data = await res.json();
      results = data.results || [];
    }

    // Persist
    const now = new Date().toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit' });
    results.forEach(r => {
      if (!r.error) {
        scanHistory.unshift({ ...r, scannedAt: now, id: uniqueId() });
      }
    });
    saveHistory();

    renderScanResults(results);
    renderHistoryTable();
    updateStatCards();
    updateCharts();

    // Update protection ring from last clean result
    const clean = results.find(r => !r.error);
    if (clean) setRingScore(Math.round((1 - clean.final_score) * 100));

    showToast(`✓ ${results.length} URL${results.length > 1 ? 's' : ''} analysed.`, 'success');

  } catch (e) {
    const msg = e.name === 'AbortError'
      ? 'Request timed out. The backend took too long.'
      : 'Cannot reach backend. Is Flask running on port 5000?';
    showToast(msg, 'error');
  } finally {
    setBtnLoading(btn, false);
  }
}

function uniqueId() { return Date.now().toString(36) + Math.random().toString(36).slice(2); }

/* ─────────────────────────────────────────────────────────────
   17. RENDER SCAN RESULT ROWS (inline list)
───────────────────────────────────────────────────────────── */
function renderScanResults(results) {
  const area = $('#scanResultArea');
  const list = $('#resultList');
  if (!area || !list) return;

  show(area);
  list.innerHTML = '';

  results.forEach((item, i) => {
    const row = document.createElement('div');
    row.className = 'result-row';
    row.style.animationDelay = `${i * 60}ms`;

    if (item.error) {
      row.innerHTML = `
        <span class="badge badge-suspicious">ERROR</span>
        <span class="result-url" title="${escHtml(item.url)}">${escHtml(item.url)}</span>
        <span style="font-size:12px;color:var(--danger);margin-left:auto;">${escHtml(item.error)}</span>`;
      list.appendChild(row);
      return;
    }

    const verdict   = item.verdict || 'UNKNOWN';
    const cls       = verdictClass(verdict);
    const score     = Math.round((item.final_score || 0) * 100);
    const fillColor = verdictColor(verdict);

    row.innerHTML = `
      <span class="badge badge-${cls}">${verdict}</span>
      <span class="result-url" title="${escHtml(item.url)}">${escHtml(item.url)}</span>
      <div class="result-score-col">
        <div class="result-score-label">Risk: ${score}%</div>
        <div class="result-mini-bar">
          <div class="result-mini-fill" data-w="${score}" style="width:0;background:${fillColor};"></div>
        </div>
      </div>
      <button class="btn btn-ghost" style="padding:0 12px;height:34px;font-size:12px;"
        onclick="openModal(${JSON.stringify(JSON.stringify(item))})">
        <i class="fa-solid fa-arrow-up-right-from-square"></i> Report
      </button>`;

    list.appendChild(row);
  });

  // Animate bars after paint
  requestAnimationFrame(() => {
    $$('.result-mini-fill', list).forEach(el => {
      el.style.transition = 'width 0.9s ease';
      el.style.width = el.dataset.w + '%';
    });
  });
}

/* ─────────────────────────────────────────────────────────────
   18. VERDICT HELPERS
───────────────────────────────────────────────────────────── */
function verdictClass(v) {
  return v === 'SAFE' ? 'safe' : v === 'SUSPICIOUS' ? 'suspicious' : 'phishing';
}
function verdictColor(v) {
  return v === 'SAFE' ? 'var(--safe)' : v === 'SUSPICIOUS' ? 'var(--suspicious)' : 'var(--danger)';
}
function verdictIcon(v) {
  return v === 'SAFE'
    ? 'fa-circle-check'
    : v === 'SUSPICIOUS'
      ? 'fa-triangle-exclamation'
      : 'fa-skull-crossbones';
}

/* ─────────────────────────────────────────────────────────────
   19. PROTECTION SCORE RING
───────────────────────────────────────────────────────────── */
function setRingScore(score) {
  const fill    = $('#ringFill');
  const numEl   = $('#ringNum');
  const subEl   = $('#ringSub');
  const caption = $('#ringCaption');
  if (!fill) return;

  const circumference = 351;

  if (score === null || score === undefined) {
    fill.style.strokeDashoffset = circumference;
    if (numEl) numEl.textContent = '—';
    if (subEl) { subEl.textContent = 'SCORE'; subEl.style.color = 'var(--text-muted)'; }
    if (caption) caption.textContent = 'Scan a URL to compute your score';
    return;
  }

  // Animate number
  animateNumber(numEl, parseInt(numEl?.textContent) || 0, score, 1400);

  const offset = circumference - (score / 100) * circumference;
  fill.style.strokeDashoffset = offset;

  const color = score >= 70 ? 'var(--safe)' : score >= 40 ? 'var(--suspicious)' : 'var(--danger)';
  if (numEl) numEl.style.color = color;
  if (subEl) { subEl.style.color = color; subEl.textContent = score >= 70 ? 'SECURE' : score >= 40 ? 'CAUTION' : 'AT RISK'; }
  if (caption) caption.textContent = score >= 70 ? 'Strong protection' : score >= 40 ? 'Moderate risk detected' : 'High risk — take action';
}

/* ─────────────────────────────────────────────────────────────
   20. COUNT-UP ANIMATION
───────────────────────────────────────────────────────────── */
function animateNumber(el, from, to, duration = 600) {
  if (!el) return;
  if (from === to) { el.textContent = to; return; }
  const start = performance.now();
  const diff  = to - from;
  function step(now) {
    const t = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);      // ease-out-cubic
    el.textContent = Math.round(from + diff * eased);
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function animateCount(id, target) {
  const el = $(`#${id}`);
  if (!el) return;
  animateNumber(el, parseInt(el.textContent) || 0, target);
}

/* ─────────────────────────────────────────────────────────────
   21. STAT CARDS UPDATE
───────────────────────────────────────────────────────────── */
function updateStatCards() {
  const total     = scanHistory.length;
  const safe      = scanHistory.filter(r => r.verdict === 'SAFE').length;
  const suspicious= scanHistory.filter(r => r.verdict === 'SUSPICIOUS').length;
  const phishing  = scanHistory.filter(r => r.verdict === 'PHISHING').length;

  animateCount('statTotal',      total);
  animateCount('statSafe',       safe);
  animateCount('statSuspicious', suspicious);
  animateCount('statPhishing',   phishing);
  animateCount('heroTotal',      total);
  animateCount('heroSafe',       safe);
  animateCount('heroSuspicious', suspicious);
  animateCount('heroPhishing',   phishing);

  const badge = $('#historyBadge');
  if (badge) badge.textContent = total;
}

/* ─────────────────────────────────────────────────────────────
   22. CHARTS
───────────────────────────────────────────────────────────── */
const CHART_FONT = { color: '#94a3b8', size: 11 };
const CHART_GRID = 'rgba(255,255,255,0.04)';

function initCharts() {
  const pieCtx = $('#pieChart');
  const barCtx = $('#barChart');
  if (!pieCtx || !barCtx || typeof Chart === 'undefined') return;

  // Doughnut
  pieChart = new Chart(pieCtx, {
    type: 'doughnut',
    data: {
      labels: ['Safe', 'Suspicious', 'Phishing'],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: ['rgba(34,197,94,0.80)','rgba(245,158,11,0.80)','rgba(239,68,68,0.80)'],
        borderColor:     ['rgba(34,197,94,0.25)','rgba(245,158,11,0.25)','rgba(239,68,68,0.25)'],
        borderWidth: 1, hoverOffset: 10,
        hoverBorderColor: ['#22c55e','#f59e0b','#ef4444'],
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '68%',
      animation: { animateRotate: true, duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#94a3b8', font: { size: 12 }, boxWidth: 12, padding: 16 }
        },
        tooltip: {
          backgroundColor: '#0b1525',
          borderColor: 'rgba(255,255,255,0.10)',
          borderWidth: 1,
          titleColor: '#f1f5f9', bodyColor: '#94a3b8',
          padding: 10, cornerRadius: 8,
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed} URL${ctx.parsed !== 1 ? 's' : ''}`
          }
        }
      }
    }
  });

  // Bar (score distribution)
  barChart = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: ['0–20%','21–40%','41–60%','61–80%','81–100%'],
      datasets: [{
        label: 'URLs',
        data: [0,0,0,0,0],
        backgroundColor: [
          'rgba(34,197,94,0.75)', 'rgba(56,189,248,0.75)',
          'rgba(245,158,11,0.75)','rgba(251,146,60,0.75)','rgba(239,68,68,0.75)'
        ],
        borderRadius: 6, borderSkipped: false,
        hoverBackgroundColor: [
          'rgba(34,197,94,1)','rgba(56,189,248,1)',
          'rgba(245,158,11,1)','rgba(251,146,60,1)','rgba(239,68,68,1)'
        ]
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 800, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0b1525', borderColor: 'rgba(255,255,255,0.10)',
          borderWidth: 1, titleColor: '#f1f5f9', bodyColor: '#94a3b8',
          padding: 10, cornerRadius: 8,
          callbacks: { label: ctx => ` ${ctx.parsed.y} URL${ctx.parsed.y !== 1 ? 's' : ''}` }
        }
      },
      scales: {
        x: {
          grid: { color: CHART_GRID },
          ticks: { color: '#94a3b8', font: { size: 11 } }
        },
        y: {
          grid: { color: CHART_GRID },
          ticks: { color: '#94a3b8', font: { size: 11 }, stepSize: 1, precision: 0 },
          beginAtZero: true
        }
      }
    }
  });

  updateCharts();
}

function updateCharts() {
  if (!pieChart || !barChart) return;

  const safe       = scanHistory.filter(r => r.verdict === 'SAFE').length;
  const suspicious = scanHistory.filter(r => r.verdict === 'SUSPICIOUS').length;
  const phishing   = scanHistory.filter(r => r.verdict === 'PHISHING').length;
  pieChart.data.datasets[0].data = [safe, suspicious, phishing];
  pieChart.update('active');

  const buckets = [0,0,0,0,0];
  scanHistory.forEach(r => {
    const s = (r.final_score || 0) * 100;
    if      (s <= 20) buckets[0]++;
    else if (s <= 40) buckets[1]++;
    else if (s <= 60) buckets[2]++;
    else if (s <= 80) buckets[3]++;
    else              buckets[4]++;
  });
  barChart.data.datasets[0].data = buckets;
  barChart.update('active');
}

/* ─────────────────────────────────────────────────────────────
   23. HISTORY TABLE
───────────────────────────────────────────────────────────── */
function renderHistoryTable() {
  const tbody = $('#historyBody');
  if (!tbody) return;

  const query = ($('#historySearch')?.value || '').toLowerCase().trim();

  let data = [...scanHistory];

  // Filter by verdict
  if (historyFilter !== 'all') data = data.filter(r => r.verdict === historyFilter);

  // Filter by search
  if (query) data = data.filter(r => (r.url || '').toLowerCase().includes(query));

  // Sort
  data.sort((a, b) => {
    let av = a[sortCol] ?? '', bv = b[sortCol] ?? '';
    if (typeof av === 'number') return sortDir === 'asc' ? av - bv : bv - av;
    return sortDir === 'asc'
      ? String(av).localeCompare(String(bv))
      : String(bv).localeCompare(String(av));
  });

  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="table-empty">
      <i class="fa-solid fa-inbox"></i>
      ${scanHistory.length === 0
        ? 'No scans yet — paste a URL above to get started'
        : 'No results match your current filter'}
    </td></tr>`;
    return;
  }

  tbody.innerHTML = data.map((r, i) => {
    const cls    = verdictClass(r.verdict);
    const sColor = verdictColor(r.verdict);
    const score  = Math.round((r.final_score  || 0) * 100);
    const ml     = Math.round((r.ml_score     || 0) * 100);
    const rule   = Math.round((r.rule_score   || 0) * 100);
    const llm    = Math.round((r.llm_score    || 0) * 100);
    const encoded= encodeURIComponent(JSON.stringify(r));
    return `
    <tr>
      <td style="color:var(--text-muted);font-size:12px;width:36px;">${i + 1}</td>
      <td><span class="td-url" title="${escHtml(r.url)}">${escHtml(r.url)}</span></td>
      <td><span class="badge badge-${cls}">${r.verdict}</span></td>
      <td class="td-score" style="color:${sColor};">${score}%</td>
      <td style="font-size:12px;color:var(--text-muted);">${ml}%</td>
      <td style="font-size:12px;color:var(--text-muted);">${rule}%</td>
      <td style="font-size:12px;color:var(--text-muted);">${llm}%</td>
      <td class="td-time">${r.scannedAt || '—'}</td>
      <td><div class="td-actions">
        <button class="td-btn" title="View Report"
          onclick="openModal(decodeURIComponent('${encoded}'))">
          <i class="fa-solid fa-eye"></i>
        </button>
        <button class="td-btn del" title="Delete" onclick="deleteHistoryRecord('${r.id}')">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div></td>
    </tr>`;
  }).join('');
}

function setHistoryFilter(val, btn) {
  historyFilter = val;
  $$('.filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderHistoryTable();
}

function filterHistory() { renderHistoryTable(); }

function setSort(col, btn) {
  if (sortCol === col) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
  else { sortCol = col; sortDir = 'desc'; }
  $$('.data-table th').forEach(th => {
    th.classList.remove('sort-active');
    const arrow = th.querySelector('.sort-arrow');
    if (arrow) arrow.textContent = '↕';
  });
  if (btn) {
    btn.classList.add('sort-active');
    const arrow = btn.querySelector('.sort-arrow');
    if (arrow) arrow.textContent = sortDir === 'asc' ? '↑' : '↓';
  }
  renderHistoryTable();
}

function deleteHistoryRecord(id) {
  scanHistory = scanHistory.filter(r => r.id !== id);
  saveHistory();
  renderHistoryTable();
  updateStatCards();
  updateCharts();
  showToast('Record removed.', 'info');
}

function clearHistory() {
  if (!confirm('Clear all scan history? This cannot be undone.')) return;
  scanHistory = [];
  saveHistory();
  renderHistoryTable();
  updateStatCards();
  updateCharts();
  setRingScore(null);
  const area = $('#scanResultArea');
  if (area) hide(area);
  showToast('Scan history cleared.', 'info');
}

/* ─────────────────────────────────────────────────────────────
   24. CSV EXPORT
───────────────────────────────────────────────────────────── */
function exportCSV() {
  if (!scanHistory.length) { showToast('Nothing to export yet.', 'warning'); return; }

  const headers = ['#','URL','Verdict','Risk Score','ML Score','Rule Score','LLM Score',
                   'Domain','IP Address','Domain Age (days)','Scanned At'];

  const rows = scanHistory.map((r, i) => [
    i + 1,
    `"${(r.url || '').replace(/"/g,'""')}"`,
    r.verdict,
    Math.round((r.final_score || 0) * 100) + '%',
    Math.round((r.ml_score    || 0) * 100) + '%',
    Math.round((r.rule_score  || 0) * 100) + '%',
    Math.round((r.llm_score   || 0) * 100) + '%',
    r.domain      || '',
    r.ip_address  || '',
    r.domain_age_days >= 0 ? r.domain_age_days : '',
    r.scannedAt   || ''
  ].join(','));

  const csv  = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href  = URL.createObjectURL(blob);
  link.download = `shieldscan_${new Date().toISOString().slice(0,10)}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast('CSV exported successfully.', 'success');
}

/* ─────────────────────────────────────────────────────────────
   25. DETAIL MODAL
───────────────────────────────────────────────────────────── */
function openModal(rawData) {
  let data;
  try {
    data = typeof rawData === 'string' ? JSON.parse(rawData) : rawData;
  } catch { showToast('Could not parse report data.', 'error'); return; }

  const verdict = (data.verdict || 'UNKNOWN').toUpperCase();
  const cls     = verdictClass(verdict);
  const color   = verdictColor(verdict);
  const score   = Math.round((data.final_score || 0) * 100);
  const ml      = Math.round((data.ml_score    || 0) * 100);
  const rule    = Math.round((data.rule_score  || 0) * 100);
  const llm     = Math.round((data.llm_score   || 0) * 100);

  const icon = verdictIcon(verdict);
  const domAge = data.domain_age_days >= 0 ? data.domain_age_days + ' days' : 'Unknown';
  const ssl    = (data.url || '').startsWith('https')
    ? '<span style="color:var(--safe);"><i class="fa-solid fa-lock"></i> HTTPS Verified</span>'
    : '<span style="color:var(--danger);"><i class="fa-solid fa-lock-open"></i> No HTTPS</span>';

  const scoreColor = (s) => s > 60 ? 'var(--danger)' : s > 30 ? 'var(--suspicious)' : 'var(--safe)';
  const scoreFill  = (s) => s > 60 ? 'progress-fill-danger' : s > 30 ? 'progress-fill-suspicious' : 'progress-fill-safe';

  // Reasons
  const reasonsHtml = (data.reasons || []).map(r =>
    `<div class="reason-item bad"><i class="fa-solid fa-circle-exclamation" style="color:var(--danger);"></i>${escHtml(r)}</div>`
  ).join('') || `<div class="reason-item good"><i class="fa-solid fa-circle-check" style="color:var(--safe);"></i>No suspicious patterns detected.</div>`;

  // Recommended actions
  const actionsHtml = verdict === 'SAFE'
    ? `<div class="action-item"><i class="fa-solid fa-circle-check" style="color:var(--safe);"></i>This URL appears safe. Exercise caution with unsolicited links.</div>`
    : verdict === 'SUSPICIOUS'
      ? `<div class="action-item"><i class="fa-solid fa-eye"></i>Do not enter personal or payment information on this page.</div>
         <div class="action-item"><i class="fa-solid fa-globe"></i>Verify the link through the organisation's official website directly.</div>
         <div class="action-item"><i class="fa-solid fa-shield-halved"></i>Report this URL to your security administrator.</div>`
      : `<div class="action-item" style="border-color:rgba(239,68,68,0.3);"><i class="fa-solid fa-ban" style="color:var(--danger);"></i><strong>Do NOT visit this URL.</strong> High probability of phishing attack.</div>
         <div class="action-item"><i class="fa-solid fa-user-shield"></i>If already visited, change passwords and monitor your accounts immediately.</div>
         <div class="action-item"><i class="fa-solid fa-bell"></i>Block the sender and report to your IT/security team.</div>`;

  const body = $('#modalBody');
  if (!body) return;

  body.innerHTML = `
    <!-- Verdict Banner -->
    <div class="verdict-banner ${cls}">
      <div class="verdict-ico ${cls}"><i class="fa-solid ${icon}"></i></div>
      <div class="verdict-txt">
        <h2 style="color:${color};">${verdict}</h2>
        <p>${escHtml(data.url || '')}</p>
      </div>
      <div class="verdict-score-box">
        <div class="verdict-score-num" style="color:${color};">${score}%</div>
        <div class="verdict-score-lbl">Risk Score</div>
      </div>
    </div>

    <!-- Detection Scores -->
    <div>
      <div class="divider-title"><i class="fa-solid fa-sliders"></i> Detection Scores</div>
      <div class="meters-grid">
        ${['ML Model|' + ml, 'Rule Engine|' + rule, 'LLM Analysis|' + llm].map(pair => {
          const [lbl, val] = pair.split('|');
          const v = parseInt(val);
          return `<div class="meter-box">
            <div class="meter-lbl">${lbl}</div>
            <div class="meter-val" style="color:${scoreColor(v)};">${v}%</div>
            <div class="progress"><div class="progress-fill ${scoreFill(v)}" data-w="${v}" style="width:0;"></div></div>
          </div>`;
        }).join('')}
      </div>
    </div>

    <!-- Domain Intelligence -->
    <div>
      <div class="divider-title"><i class="fa-solid fa-globe"></i> Domain Intelligence</div>
      <div class="info-grid">
        <div class="info-box"><div class="info-box-lbl">Domain</div>
          <div class="info-box-val">${escHtml(data.domain || '—')}</div></div>
        <div class="info-box"><div class="info-box-lbl">IP Address</div>
          <div class="info-box-val">${escHtml(data.ip_address || '—')}</div></div>
        <div class="info-box"><div class="info-box-lbl">Domain Age</div>
          <div class="info-box-val">${domAge}</div></div>
        <div class="info-box"><div class="info-box-lbl">SSL / TLS</div>
          <div class="info-box-val">${ssl}</div></div>
      </div>
    </div>

    <!-- Detected Issues -->
    <div>
      <div class="divider-title"><i class="fa-solid fa-bug"></i> Detected Issues</div>
      <div class="reasons-list">${reasonsHtml}</div>
    </div>

    <!-- AI Explanation -->
    ${data.llm_explanation ? `
    <div>
      <div class="divider-title"><i class="fa-solid fa-robot"></i> AI Security Analysis</div>
      <div class="ai-box">
        <div class="ai-box-header"><i class="fa-solid fa-microchip"></i> Llama-3.1 via Groq</div>
        ${escHtml(data.llm_explanation)}
      </div>
    </div>` : ''}

    <!-- Recommended Actions -->
    <div>
      <div class="divider-title"><i class="fa-solid fa-shield-halved"></i> Recommended Actions</div>
      <div class="reasons-list">${actionsHtml}</div>
    </div>
  `;

  const overlay = $('#detailModal');
  if (overlay) overlay.classList.add('show');

  // Animate progress bars after DOM paint
  requestAnimationFrame(() => {
    $$('.progress-fill[data-w]', body).forEach(el => {
      el.style.transition = 'width 1s ease';
      el.style.width = el.dataset.w + '%';
    });
  });
}

function closeDetailModal() {
  const overlay = $('#detailModal');
  if (overlay) overlay.classList.remove('show');
}

function modalOverlayClick(e) {
  if (e.target === $('#detailModal')) closeDetailModal();
}

/* ─────────────────────────────────────────────────────────────
   26. EXTENSION STATUS CHECK
───────────────────────────────────────────────────────────── */
async function pingAPI() {
  const el = $('#extApiStatus');
  if (!el) return;
  try {
    const r = await fetchWithTimeout(`${API_BASE}/check`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ url:'https://google.com' })
    }, 4000);
    el.innerHTML = r.ok
      ? '<span style="color:var(--safe);">Online</span>'
      : '<span style="color:var(--danger);">Error</span>';
  } catch {
    el.innerHTML = '<span style="color:var(--danger);">Offline</span>';
  }
}

function checkExtension() {
  const chip = $('#extInstallChip');
  if (!chip) return;
  const detected = (typeof chrome !== 'undefined' && !!chrome.runtime);
  chip.className = `ext-chip ${detected ? 'on' : 'off'}`;
  chip.innerHTML = detected
    ? '<i class="fa-solid fa-circle-check"></i> Installed & Connected'
    : '<i class="fa-solid fa-circle-xmark"></i> Not Detected';
  showToast(
    detected ? 'Extension detected — Protected Browsing Enabled.' : 'Extension not found. Install from the Chrome Web Store.',
    detected ? 'success' : 'warning'
  );
}

/* ─────────────────────────────────────────────────────────────
   27. SCAN MODE TOGGLE
───────────────────────────────────────────────────────────── */
function setScanMode(mode, btn) {
  batchMode = (mode === 'batch');
  $$('.scan-tab').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const ta = $('#urlInput');
  if (!ta) return;
  ta.classList.toggle('multi', batchMode);
  ta.placeholder = batchMode
    ? 'Paste multiple URLs — one per line…'
    : 'https://example.com — paste a URL to analyse…';
  ta.rows = batchMode ? 4 : 1;
}

/* ─────────────────────────────────────────────────────────────
   28. SIDEBAR / NAV
───────────────────────────────────────────────────────────── */
function toggleSidebar() {
  $('#sidebar')?.classList.toggle('open');
}

function scrollToSection(id) {
  const el = $(`#${id}`);
  if (el) el.scrollIntoView({ behavior:'smooth', block:'start' });
  $('#sidebar')?.classList.remove('open');

  // Mark active nav item
  $$('.nav-link').forEach(l => l.classList.remove('active'));
  const active = $$(`.nav-link[data-section="${id}"]`);
  active.forEach(l => l.classList.add('active'));
}

function handleLogout() {
  localStorage.removeItem(USER_KEY);
  window.location.href = 'login.html';
}

/* ─────────────────────────────────────────────────────────────
   29. PERSISTENCE
───────────────────────────────────────────────────────────── */
function saveHistory() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scanHistory.slice(0, MAX_HISTORY)));
  } catch { /* quota exceeded — trim and retry */ }
}

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch { return []; }
}

/* ─────────────────────────────────────────────────────────────
   30. HTML ESCAPE (XSS prevention)
───────────────────────────────────────────────────────────── */
function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;');
}

/* ─────────────────────────────────────────────────────────────
   31. INTERSECTION OBSERVER — AOS fallback + on-screen stat pop
───────────────────────────────────────────────────────────── */
function initIntersectionEffects() {
  if (!('IntersectionObserver' in window)) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('stat-appear');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  $$('.card').forEach(c => obs.observe(c));
}

/* ─────────────────────────────────────────────────────────────
   32. KEYBOARD SHORTCUTS
───────────────────────────────────────────────────────────── */
function initKeyboard() {
  document.addEventListener('keydown', e => {
    // Escape closes modal
    if (e.key === 'Escape') closeDetailModal();

    // Enter to scan (single mode, when input focused)
    if (e.key === 'Enter' && !batchMode) {
      const active = document.activeElement;
      if (active?.id === 'urlInput') { e.preventDefault(); runScan(); }
    }

    // Enter to login
    if (e.key === 'Enter') {
      const panel = $('.auth-panel.active');
      if (panel?.id === 'panel-login')    handleLogin();
      if (panel?.id === 'panel-register') handleRegister();
    }

    // / to focus scan input
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      const inp = $('#urlInput');
      if (inp) { e.preventDefault(); inp.focus(); }
    }
  });
}

/* ─────────────────────────────────────────────────────────────
   33. RIPPLE — attach to all buttons on load
───────────────────────────────────────────────────────────── */
function initRipples() {
  $$('.btn, .btn-primary, .scan-btn, .ext-btn').forEach(addRipple);
}

/* ─────────────────────────────────────────────────────────────
   34. SCROLL SPY — highlight active sidebar link
───────────────────────────────────────────────────────────── */
function initScrollSpy() {
  const sections = [
    ['heroSection',      '[data-section="heroSection"]'],
    ['scannerSection',   '[data-section="scannerSection"]'],
    ['chartsSection',    '[data-section="chartsSection"]'],
    ['historySection',   '[data-section="historySection"]'],
    ['extensionSection', '[data-section="extensionSection"]'],
  ];

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        $$('.nav-link').forEach(l => {
          l.classList.toggle('active', l.dataset.section === id);
        });
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });

  sections.forEach(([id]) => {
    const el = $(`#${id}`); if (el) observer.observe(el);
  });
}

/* ─────────────────────────────────────────────────────────────
   35. INIT — DASHBOARD
───────────────────────────────────────────────────────────── */
function initDashboard() {
  // Load persisted history
  scanHistory = loadHistory();

  // Set user display name
  const user = localStorage.getItem(USER_KEY) || 'Analyst';
  const nameEl   = $('#userNameSidebar');
  const avatarEl = $('#userAvatarSidebar');
  if (nameEl)   nameEl.textContent   = user;
  if (avatarEl) avatarEl.textContent = user[0].toUpperCase();

  // Topbar greeting time
  const greeting = $('#topbarGreeting');
  if (greeting) {
    const h = new Date().getHours();
    greeting.textContent = h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
  }

  // Init subsystems
  if (typeof AOS !== 'undefined') AOS.init({ duration: 480, once: true, offset: 36 });
  initCharts();
  updateStatCards();
  renderHistoryTable();
  setRingScore(null);
  initIntersectionEffects();
  initKeyboard();
  initRipples();
  initScrollSpy();
  pingAPI();

  // Idle pulse on scan button
  const scanBtn = $('#scanBtn');
  if (scanBtn) scanBtn.classList.add('scan-btn-idle');

  // Sidebar click outside to close on mobile
  document.addEventListener('click', e => {
    const sidebar = $('#sidebar');
    const hamburger = $('.sidebar-hamburger');
    if (sidebar?.classList.contains('open')
        && !sidebar.contains(e.target)
        && !hamburger?.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });

  // Modal overlay click
  const overlay = $('#detailModal');
  if (overlay) overlay.addEventListener('click', modalOverlayClick);
}

/* ─────────────────────────────────────────────────────────────
   36. INIT — LOGIN PAGE
───────────────────────────────────────────────────────────── */
function initLogin() {
  initKeyboard();
  initRipples();

  // If already logged in, redirect
  if (localStorage.getItem(USER_KEY) && window.location.pathname.includes('login')) {
    window.location.href = 'dashboard.html';
  }

  // Password strength on register password field
  const regPass = $('#regPass');
  if (regPass) regPass.addEventListener('input', () => updateStrength(regPass.value));
}

/* ─────────────────────────────────────────────────────────────
   37. AUTO-BOOT
───────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Detect which page we're on
  if (document.body.dataset.page === 'dashboard' || $('#scanBtn')) {
    initDashboard();
  } else if (document.body.dataset.page === 'login' || $('#loginBtn')) {
    initLogin();
  }
});

/* ─────────────────────────────────────────────────────────────
   38. GLOBAL EXPORTS (for inline onclick= attributes in HTML)
───────────────────────────────────────────────────────────── */
Object.assign(window, {
  // Auth
  showPanel, handleLogin, handleRegister, handleForgot,
  sendOTP, otpNext, verifyOTP, togglePw, updateStrength,
  // Dashboard
  runScan, setScanMode, openModal, closeDetailModal, modalOverlayClick,
  setHistoryFilter, filterHistory, setSort,
  deleteHistoryRecord, clearHistory, exportCSV,
  checkExtension, toggleSidebar, scrollToSection, handleLogout,
  showToast,
});