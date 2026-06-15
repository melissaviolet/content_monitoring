// For the flags page
    const API = '/api';

    // ── State ──
    // We keep ALL flags in memory here
    // When the user filters, we don't re-fetch — we just re-render from this list
    let allFlags = [];
    let currentFilter = 'all';

    // ── On page load ──
    loadFlags();

    // ── Fetch all flags from Django ──
    async function loadFlags() {
      // Show loading skeletons while we wait
      showSkeletons();

      try {
        const res  = await fetch(`${API}/flags/`);
        const data = await res.json();
        allFlags = data;

        updateCounts();
        renderFlags();

      } catch (e) {
        showToast('Could not reach the API. Is Django running?', true);
      }
    }

    // ── Count how many flags are in each status group ──
    function updateCounts() {
      const total      = allFlags.length;
      const pending    = allFlags.filter(f => f.status === 'pending').length;
      const relevant   = allFlags.filter(f => f.status === 'relevant').length;
      const irrelevant = allFlags.filter(f => f.status === 'irrelevant').length;

      // Update the little number badges on the tabs
      document.getElementById('count-all').textContent       = total;
      document.getElementById('count-pending').textContent   = pending;
      document.getElementById('count-relevant').textContent  = relevant;
      document.getElementById('count-irrelevant').textContent= irrelevant;

      // Update sidebar badge
      document.getElementById('sidebar-pending-count').textContent = pending;
    }

    // ── Filter tab clicked ──
    function setFilter(filter, tabEl) {
      // Remember which filter is active
      currentFilter = filter;

      // Move the "active" class to the clicked tab
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      tabEl.classList.add('active');

      // Re-render with the new filter
      renderFlags();
    }

    // ── Render the flags list ──
    function renderFlags() {
      const list = document.getElementById('flags-list');

      // Filter the in-memory list
      const visible = currentFilter === 'all'
        ? allFlags
        : allFlags.filter(f => f.status === currentFilter);

      // If nothing to show
      if (visible.length === 0) {
        list.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <div class="empty-title">No flags here</div>
            <div class="empty-sub">
              ${currentFilter === 'all'
                ? 'Import content and run a scan to generate flags.'
                : `No flags marked as "${currentFilter}" yet.`}
            </div>
          </div>`;
        return;
      }

      // Build one card per flag and join them all into one HTML string
      list.innerHTML = visible.map(flag => buildFlagCard(flag)).join('');
    }

    // ── Build the HTML for one flag card ──
    function buildFlagCard(flag) {
      const scoreClass = flag.score >= 70 ? 'score-high'
                       : flag.score >= 40 ? 'score-mid'
                       : 'score-low';

      // The action buttons change depending on current status
      let actions = '';
      if (flag.status === 'pending') {
        // Pending flags get both buttons
        actions = `
          <button class="btn-relevant"   onclick="reviewFlag(${flag.id}, 'relevant')">
            <i class="bi bi-check-lg"></i> Relevant
          </button>
          <button class="btn-irrelevant" onclick="reviewFlag(${flag.id}, 'irrelevant')">
            <i class="bi bi-x-lg"></i> Irrelevant
          </button>`;
      } else {
        // Already reviewed — just show a label
        actions = `<span class="btn-reviewed">Reviewed</span>`;
      }

      return `
        <div class="flag-card status-${flag.status}" id="flag-card-${flag.id}">
          <div class="flag-info">
            <div class="flag-title">
              ${flag.content_item_title || 'Article #' + flag.content_item}
            </div>
            <div class="flag-meta">
              <span class="flag-keyword">${flag.keyword_name || 'Keyword #' + flag.keyword}</span>
              <span>Source: ${flag.content_item_source || '—'}</span>
            </div>
          </div>
          <span class="score-badge ${scoreClass}">${flag.score}</span>
          <span class="status-pill status-${flag.status}">${flag.status}</span>
          <div class="flag-actions">${actions}</div>
        </div>`;
    }

    // ── Mark a flag as relevant or irrelevant ──
    async function reviewFlag(flagId, newStatus) {
      try {
        // Send PATCH request to Django with the new status
        // PATCH means "update just this one field" (not the whole object)
        const res = await fetch(`${API}/flags/${flagId}/`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
          //      ↑ convert JS object to JSON string to send it
        });

        const updated = await res.json();

        // Find this flag in our in-memory list and update it
        // so we don't need to re-fetch everything from Django
        const index = allFlags.findIndex(f => f.id === flagId);
        allFlags[index] = updated;

        // Update counts and re-render
        updateCounts();
        renderFlags();

        showToast(`Marked as ${newStatus}.`);

      } catch (e) {
        showToast('Could not update flag. Try again.', true);
      }
    }

    // ── Loading skeletons (shown while fetching) ──
    function showSkeletons() {
      const list = document.getElementById('flags-list');
      list.innerHTML = [1,2,3,4].map(() => `
        <div class="flag-card status-pending" style="gap:16px">
          <div style="flex:1">
            <div class="skeleton" style="width:60%;margin-bottom:10px"></div>
            <div class="skeleton" style="width:35%;height:12px"></div>
          </div>
          <div class="skeleton" style="width:52px;height:28px"></div>
          <div class="skeleton" style="width:80px;height:28px"></div>
          <div class="skeleton" style="width:140px;height:32px"></div>
        </div>
      `).join('');
    }

    // ── Toast notification ──
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
