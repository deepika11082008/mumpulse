/**
 * MomCare — Frontend API Helper
 * ─────────────────────────────
 * Include this in every HTML page:
 *   <script src="api.js"></script>
 *
 * All pages already use localStorage keys:
 *   mom_name, mom_dob, mom_weeks, mom_token,
 *   completed_days, voice_recordings, q_score, q_answers
 *
 * This file syncs those with the real backend.
 */

const API_BASE = 'http://localhost:5000/api';

/* ── TOKEN HELPERS ── */
function getToken()       { return localStorage.getItem('mom_token'); }
function setToken(t)      { localStorage.setItem('mom_token', t); }
function clearToken()     { localStorage.removeItem('mom_token'); }
function isLoggedIn()     { return !!getToken(); }

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + getToken(),
  };
}

/* ── LOW-LEVEL REQUEST ── */
async function apiRequest(method, path, body = null, isFormData = false) {
  const options = { method, headers: isFormData ? { 'Authorization': 'Bearer ' + getToken() } : authHeaders() };
  if (body) options.body = isFormData ? body : JSON.stringify(body);
  try {
    const res  = await fetch(API_BASE + path, options);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  } catch (err) {
    console.error('[MomCare API]', method, path, err.message);
    throw err;
  }
}


/* ══════════════════════════════════════════
   AUTH  —  index.html
══════════════════════════════════════════ */

/**
 * Register a new mother account.
 * Called from index.html handleLogin().
 */
async function apiRegister(name, dob, weeks, password) {
  const data = await apiRequest('POST', '/auth/register', {
    name, date_of_birth: dob, weeks_postpartum: parseInt(weeks), password
  });
  setToken(data.token);
  localStorage.setItem('mom_name',  data.mother.name);
  localStorage.setItem('mom_dob',   data.mother.date_of_birth);
  localStorage.setItem('mom_weeks', data.mother.weeks_postpartum);
  return data;
}

/**
 * Login an existing mother.
 */
async function apiLogin(name, password) {
  const data = await apiRequest('POST', '/auth/login', { name, password });
  setToken(data.token);
  localStorage.setItem('mom_name',  data.mother.name);
  localStorage.setItem('mom_dob',   data.mother.date_of_birth);
  localStorage.setItem('mom_weeks', data.mother.weeks_postpartum);
  return data;
}


/* ══════════════════════════════════════════
   VOICE  —  screening.html
══════════════════════════════════════════ */

/**
 * Upload recorded audio blob for a day.
 * @param {number} dayNumber  1–5
 * @param {Blob|null} audioBlob  null in simulation mode
 * @param {string} duration  e.g. "01:23"
 */
async function apiSaveVoice(dayNumber, audioBlob, duration) {
  if (audioBlob) {
    // real audio — multipart upload
    const form = new FormData();
    form.append('day_number', dayNumber);
    form.append('duration',   duration);
    form.append('audio',      audioBlob, `day${dayNumber}.webm`);
    return await apiRequest('POST', '/voice/upload', form, true);
  } else {
    // simulation mode — JSON only
    return await apiRequest('POST', '/voice/complete', { day_number: dayNumber, duration });
  }
}

/**
 * Fetch completed days from server and sync to localStorage.
 */
async function apiLoadProgress() {
  const data = await apiRequest('GET', '/voice/progress');
  localStorage.setItem('completed_days',    JSON.stringify(data.completed_days));
  localStorage.setItem('voice_recordings',  JSON.stringify(
    data.entries.reduce((acc, e) => { acc['day' + e.day_number] = { duration: e.duration }; return acc; }, {})
  ));
  return data.completed_days;
}


/* ══════════════════════════════════════════
   QUESTIONNAIRE  —  screening.html
══════════════════════════════════════════ */

/**
 * Submit 5 questionnaire answers.
 * @param {number[]} answers  Array of 5 ints (0–3)
 */
async function apiSubmitQuestionnaire(answers) {
  const data = await apiRequest('POST', '/questionnaire/submit', { answers });
  localStorage.setItem('q_score',   data.total_score);
  localStorage.setItem('q_answers', JSON.stringify(
    answers.reduce((acc, val, i) => { acc[i] = val; return acc; }, {})
  ));
  return data;
}

/**
 * Fetch latest questionnaire result.
 */
async function apiGetResult() {
  const data = await apiRequest('GET', '/questionnaire/result');
  localStorage.setItem('q_score',   data.total_score);
  return data;
}


/* ══════════════════════════════════════════
   DASHBOARD  —  dashboard.html
══════════════════════════════════════════ */

/**
 * Load full dashboard data and sync localStorage.
 */
async function apiLoadDashboard() {
  const data = await apiRequest('GET', '/dashboard');
  localStorage.setItem('mom_name',          data.mother.name);
  localStorage.setItem('mom_dob',           data.mother.date_of_birth);
  localStorage.setItem('mom_weeks',         data.mother.weeks_postpartum);
  localStorage.setItem('completed_days',    JSON.stringify(data.completed_days));
  if (data.questionnaire) {
    localStorage.setItem('q_score', data.questionnaire.total_score);
  }
  return data;
}


/* ══════════════════════════════════════════
   AUTO-INIT  —  runs on every page load
══════════════════════════════════════════ */
(function init() {
  const page = window.location.pathname.split('/').pop();

  // If not logged in and not on login page → redirect
  if (!isLoggedIn() && page !== 'index.html' && page !== '') {
    window.location.href = 'index.html';
    return;
  }

  // Sync progress in background on screening / dashboard / result pages
  if (isLoggedIn() && ['screening.html', 'dashboard.html', 'result.html'].includes(page)) {
    apiLoadProgress().catch(() => {});
  }
})();