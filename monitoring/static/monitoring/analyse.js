// =============================================
// FlagWatch — Analyse Page JS
// Talks to: POST /api/analyse/  (our new Django view)
// =============================================

const API = '/api';

// ── Load sidebar badge on page load ──
loadPendingCount();

// ── Main function — send article to Ollama via Django ──
async function analyseArticle() {
  const text = document.getElementById('article-input').value.trim();

  // Don't send empty text
  if (!text) {
    showToast('Please paste an article first.', true);
    return;
  }

  // Show loading state
  setLoading(true);
  document.getElementById('result-area').style.display = 'none';
  document.getElementById('error-area').style.display = 'none';

  try {
    const res = await fetch(`${API}/analyse/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });

    if (!res.ok) {
      throw new Error('API returned an error');
    }

    const data = await res.json();

    if (data.error) {
      showError(data.error);
      return;
    }

    // Show the result
    renderResult(data);

  } catch (e) {
    showError('Could not reach the API or Ollama. Make sure both Django and Ollama are running.');
  } finally {
    setLoading(false);
  }
}

// ── Render the AI result ──
function renderResult(data) {
  const area = document.getElementById('result-area');

  // Summary
  document.getElementById('result-summary').textContent = data.summary || '—';

  // Relevance badge
  const relevance = (data.relevance || 'low').toLowerCase();
  const badgeEl   = document.getElementById('result-relevance');
  badgeEl.textContent = relevance;
  badgeEl.className   = `relevance-badge relevance-${relevance}`;

  // Reason
  document.getElementById('result-reason').textContent = data.reason || '—';

  // Matched keywords
  const kwContainer = document.getElementById('result-keywords');
  const keywords    = data.matched_keywords || [];

  if (keywords.length === 0) {
    kwContainer.innerHTML = `<span style="color:var(--text-muted);font-size:13px">No tracked keywords matched.</span>`;
  } else {
    kwContainer.innerHTML = keywords.map(kw => `
      <span class="matched-kw">${kw}</span>
    `).join('');
  }

  // Show the result area with a smooth animation
  area.style.display = 'block';
  area.style.animation = 'fadeIn 0.3s ease both';
}

// ── Show an error message ──
function showError(msg) {
  const area = document.getElementById('error-area');
  document.getElementById('error-msg').textContent = msg;
  area.style.display = 'block';
}

// ── Toggle loading state ──
function setLoading(isLoading) {
  const btn      = document.getElementById('analyse-btn');
  const spinner  = document.getElementById('analyse-spinner');
  const btnText  = document.getElementById('btn-text');

  btn.disabled        = isLoading;
  spinner.style.display = isLoading ? 'block' : 'none';
  btnText.textContent   = isLoading ? 'Analysing...' : 'Analyse with AI';
}

// ── Clear everything ──
function clearAll() {
  document.getElementById('article-input').value = '';
  document.getElementById('result-area').style.display  = 'none';
  document.getElementById('error-area').style.display   = 'none';
}

// ── Load pending count for sidebar badge ──
async function loadPendingCount() {
  try {
    const res   = await fetch(`${API}/flags/`);
    const flags = await res.json();
    const count = flags.filter(f => f.status === 'pending').length;
    document.getElementById('sidebar-pending-count').textContent = count;
  } catch (e) { /* silently fail */ }
}

// ── Toast ──
function showToast(msg, isError = false) {
  const t    = document.getElementById('toast');
  const icon = t.querySelector('.toast-icon');
  document.getElementById('toast-msg').textContent = msg;
  icon.className = isError
    ? 'bi bi-exclamation-circle-fill toast-icon'
    : 'bi bi-check-circle-fill toast-icon';
  icon.style.color = isError ? '#EF4444' : '#F5A623';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}