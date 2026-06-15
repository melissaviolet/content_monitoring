// =============================================
// FlagWatch — Content Page JS
// Talks to: GET /api/flags/ (for sidebar count)
//           POST /api/import-content/
//           POST /api/scan/
//           GET /api/flags/ (to show flags per article)
// =============================================

const API = '/api';

// ── Run when page loads ──
loadContent();
loadPendingCount();

// ── Fetch all content items from Django ──
async function loadContent() {
  showSkeletons();

  try {
    // We don't have a /api/content/ endpoint that lists articles
    // So we fetch flags and extract the content items from them
    // This is a workaround since your backend doesn't expose ContentItem directly
    const res   = await fetch(`${API}/flags/`);
    const flags = await res.json();

    // Build a map of content items from the flags data
    // A "map" here means an object where the key is the content item ID
    // and the value is info about that article
    const contentMap = {};

    flags.forEach(flag => {
      const id = flag.content_item;

      if (!contentMap[id]) {
        // First time we see this content item — create an entry
        contentMap[id] = {
          id:     id,
          title:  flag.content_item_title  || 'Article #' + id,
          source: flag.content_item_source || '—',
          flags:  []
        };
      }

      // Add this flag to the article's flag list
      contentMap[id].flags.push(flag);
    });

    // Convert the map into an array so we can loop over it
    const articles = Object.values(contentMap);

    renderContent(articles);

  } catch (e) {
    showToast('Could not reach the API. Is Django running?', true);
  }
}

// ── Render articles ──
function renderContent(articles) {
  const list = document.getElementById('content-list');
  document.getElementById('article-count').textContent = articles.length;

  if (articles.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📄</div>
        <div class="empty-title">No content imported yet</div>
        <div class="empty-sub">Click "Import Content" then "Run Scan" to get started.</div>
      </div>`;
    return;
  }

  list.innerHTML = articles.map(article => buildArticleCard(article)).join('');
}

// ── Build HTML for one article card ──
function buildArticleCard(article) {
  const total      = article.flags.length;
  const pending    = article.flags.filter(f => f.status === 'pending').length;
  const relevant   = article.flags.filter(f => f.status === 'relevant').length;
  const irrelevant = article.flags.filter(f => f.status === 'irrelevant').length;

  // Build small flag summary badges
  const flagSummary = total === 0
    ? `<span style="color:var(--text-muted);font-size:12px">No flags</span>`
    : `
      ${pending    ? `<span class="status-pill status-pending">${pending} pending</span>`    : ''}
      ${relevant   ? `<span class="status-pill status-relevant">${relevant} relevant</span>` : ''}
      ${irrelevant ? `<span class="status-pill status-irrelevant">${irrelevant} suppressed</span>` : ''}
    `;

  return `
    <div class="article-card">
      <div class="article-header">
        <div>
          <div class="article-title">${article.title}</div>
          <div class="article-source">
            <i class="bi bi-journal-text"></i> ${article.source}
          </div>
        </div>
        <div class="article-flag-count">
          <i class="bi bi-flag-fill" style="color:var(--amber)"></i>
          ${total} flag${total !== 1 ? 's' : ''}
        </div>
      </div>
      <div class="article-footer">
        <div class="flag-summary">${flagSummary}</div>
      </div>
    </div>`;
}

// ── Import content ──
async function importContent() {
  setSpinner('import-spinner', true);
  setButtonDisabled('btn-import', true);

  try {
    const res  = await fetch(`${API}/import-content/`, { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'Content imported.');
    loadContent(); // refresh the list
  } catch (e) {
    showToast('Import failed. Is Django running?', true);
  } finally {
    // finally runs whether the try succeeded or failed
    setSpinner('import-spinner', false);
    setButtonDisabled('btn-import', false);
  }
}

// ── Run scan ──
async function runScan() {
  setSpinner('scan-spinner', true);
  setButtonDisabled('btn-scan', true);

  try {
    const res  = await fetch(`${API}/scan/`, { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'Scan complete.');
    loadContent(); // refresh so flag counts update
  } catch (e) {
    showToast('Scan failed. Is Django running?', true);
  } finally {
    setSpinner('scan-spinner', false);
    setButtonDisabled('btn-scan', false);
  }
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

// ── Helpers ──

function setSpinner(id, show) {
  document.getElementById(id).style.display = show ? 'block' : 'none';
}

function setButtonDisabled(id, disabled) {
  document.getElementById(id).disabled = disabled;
}

function showSkeletons() {
  const list = document.getElementById('content-list');
  list.innerHTML = [1, 2, 3].map(() => `
    <div class="article-card">
      <div class="article-header">
        <div style="flex:1">
          <div class="skeleton" style="width:55%;margin-bottom:10px"></div>
          <div class="skeleton" style="width:30%;height:12px"></div>
        </div>
        <div class="skeleton" style="width:60px;height:20px"></div>
      </div>
      <div class="article-footer">
        <div class="skeleton" style="width:200px;height:22px"></div>
      </div>
    </div>
  `).join('');
}

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