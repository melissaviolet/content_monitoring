// For the dashboard page 
    const API = '/api';

    // ── Helpers ──
    function showToast(msg, isError = false) {
      const t = document.getElementById('toast');
      const icon = t.querySelector('.toast-icon');
      document.getElementById('toast-msg').textContent = msg;
      icon.className = isError
        ? 'bi bi-exclamation-circle-fill toast-icon'
        : 'bi bi-check-circle-fill toast-icon';
      icon.style.color = isError ? '#EF4444' : '#F5A623';
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 3000);
    }

    function setSpinner(id, show) {
      const el = document.getElementById(id);
      el.style.display = show ? 'block' : 'none';
    }

    function scoreClass(s) {
      if (s >= 70) return 'score-high';
      if (s >= 40) return 'score-mid';
      return 'score-low';
    }

    // ── Load stats ──
    async function loadStats() {
      try {
        const [flagsRes, kwRes] = await Promise.all([
          fetch(`${API}/flags/`),
          fetch(`${API}/keywords/`)
        ]);
        const flags    = await flagsRes.json();
        const keywords = await kwRes.json();

        const pending    = flags.filter(f => f.status === 'pending').length;
        const relevant   = flags.filter(f => f.status === 'relevant').length;
        const irrelevant = flags.filter(f => f.status === 'irrelevant').length;

        animateCount('stat-pending',    pending);
        animateCount('stat-relevant',   relevant);
        animateCount('stat-irrelevant', irrelevant);
        animateCount('stat-keywords',   keywords.length);

        // sidebar badge
        document.getElementById('sidebar-pending-count').textContent = pending;

        renderFlags(flags.slice(0, 8));
        renderKeywords(keywords);

      } catch (e) {
        showToast('Could not reach the API. Is Django running?', true);
      }
    }

    // ── Animate number count-up ──
    function animateCount(id, target) {
      const el = document.getElementById(id);
      let current = 0;
      const step = Math.max(1, Math.ceil(target / 20));
      const tick = () => {
        current = Math.min(current + step, target);
        el.textContent = current;
        if (current < target) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }

    // ── Render flags table ──
    function renderFlags(flags) {
      const tbody = document.getElementById('flags-tbody');
      if (!flags.length) return;

      tbody.innerHTML = flags.map(f => `
        <tr>
          <td>
            <div class="article-title">${f.content_item_title || 'Article #' + f.content_item}</div>
            <div class="article-source">${f.content_item_source || ''}</div>
          </td>
          <td style="font-family:'Roboto Mono',monospace;font-size:12px;color:#1A1A2E">
            ${f.keyword_name || '#' + f.keyword}
          </td>
          <td>
            <span class="score-badge ${scoreClass(f.score)}">${f.score}</span>
          </td>
          <td>
            <span class="status-pill status-${f.status}">${f.status}</span>
          </td>
        </tr>
      `).join('');
    }

    // ── Render keywords ──
    function renderKeywords(keywords) {
      const el = document.getElementById('keyword-list');
      if (!keywords.length) return;
      el.innerHTML = keywords.map(k => `
        <span class="kw-pill">
          <span class="kw-dot"></span>${k.name}
        </span>
      `).join('');
    }

    // ── Import content ──
    async function importContent() {
      setSpinner('import-spinner', true);
      try {
        const res = await fetch(`${API}/import-content/`, { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'Content imported.');
        loadStats();
      } catch (e) {
        showToast('Import failed. Is Django running?', true);
      } finally {
        setSpinner('import-spinner', false);
      }
    }

    // ── Run scan ──
    async function runScan() {
      setSpinner('scan-spinner', true);
      try {
        const res = await fetch(`${API}/scan/`, { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'Scan complete.');
        loadStats();
      } catch (e) {
        showToast('Scan failed. Is Django running?', true);
      } finally {
        setSpinner('scan-spinner', false);
      }
    }

    // ── Init ──
    loadStats();
