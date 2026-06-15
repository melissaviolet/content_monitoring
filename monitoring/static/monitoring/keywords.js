// For the keywords page

    const API = '/api';

    // ── Load keywords when page opens ──
    loadKeywords();

    async function loadKeywords() {
      showSkeletons();

      try {
        const res  = await fetch(`${API}/keywords/`);
        const data = await res.json();
        renderKeywords(data);
        loadPendingCount(); // update sidebar badge
      } catch (e) {
        showToast('Could not reach the API. Is Django running?', true);
      }
    }

    // ── Render all keyword cards ──
    function renderKeywords(keywords) {
      const grid = document.getElementById('keywords-grid');
      document.getElementById('kw-total').textContent = keywords.length;

      if (keywords.length === 0) {
        grid.innerHTML = `
          <div class="empty-state" style="grid-column:1/-1">
            <div class="empty-icon">🏷️</div>
            <div class="empty-title">No keywords yet</div>
            <div class="empty-sub">Add your first keyword above to start monitoring.</div>
          </div>`;
        return;
      }

      grid.innerHTML = keywords.map(kw => `
        <div class="kw-card" id="kw-card-${kw.id}">
          <div class="kw-card-left">
            <div class="kw-dot"></div>
            <div>
              <div class="kw-name">${kw.name}</div>
              <div class="kw-id">ID: ${kw.id}</div>
            </div>
          </div>
          <button class="kw-delete" onclick="deleteKeyword(${kw.id})" title="Delete keyword">
            <i class="bi bi-trash3"></i>
          </button>
        </div>
      `).join('');
    }

    // ── Add a new keyword ──
    async function addKeyword() {
      // 1. Get whatever the user typed
      const input = document.getElementById('kw-input');
      const name  = input.value.trim(); // .trim() removes accidental spaces

      // 2. Don't send an empty keyword
      if (!name) {
        showToast('Please type a keyword first.', true);
        return;
      }

      try {
        // 3. POST to Django — sending the name as JSON
        const res = await fetch(`${API}/keywords/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: name })
        });

        if (!res.ok) {
          showToast('Could not add keyword.', true);
          return;
        }

        // 4. Clear the input box ready for the next one
        input.value = '';

        // 5. Reload the list so the new keyword appears
        loadKeywords();
        showToast(`"${name}" added.`);

      } catch (e) {
        showToast('Could not add keyword.', true);
      }
    }

    // ── Delete a keyword ──
    async function deleteKeyword(kwId) {
      // Ask the user to confirm before deleting
      if (!confirm('Delete this keyword? Any flags linked to it will also be deleted.')) return;

      try {
        // DELETE request — no body needed, the ID is in the URL
        await fetch(`${API}/keywords/${kwId}/`, {
          method: 'DELETE'
        });

        // Remove just this card from the page without reloading everything
        const card = document.getElementById(`kw-card-${kwId}`);
        card.style.opacity = '0';
        card.style.transform = 'scale(0.95)';
        card.style.transition = 'opacity 0.2s, transform 0.2s';

        // After the animation finishes, remove from DOM and reload
        setTimeout(() => loadKeywords(), 250);

        showToast('Keyword deleted.');

      } catch (e) {
        showToast('Could not delete keyword.', true);
      }
    }

    // ── Allow pressing Enter to add keyword ──
    document.getElementById('kw-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter') addKeyword();
    });
    // ↑ This is an "event listener" — it watches for a specific event on an element
    //   'keydown' fires every time a key is pressed while the input is focused
    //   e.key tells us which key it was

    // ── Load pending flags count for sidebar badge ──
    async function loadPendingCount() {
      try {
        const res   = await fetch(`${API}/flags/`);
        const flags = await res.json();
        const count = flags.filter(f => f.status === 'pending').length;
        document.getElementById('sidebar-pending-count').textContent = count;
      } catch (e) { /* silently fail, not critical */ }
    }

    // ── Loading skeletons ──
    function showSkeletons() {
      const grid = document.getElementById('keywords-grid');
      grid.innerHTML = [1,2,3,4,5,6].map(() => `
        <div class="kw-card-skeleton">
          <div class="skeleton" style="width:8px;height:8px;border-radius:50%;flex-shrink:0"></div>
          <div style="flex:1">
            <div class="skeleton" style="width:70%;margin-bottom:8px"></div>
            <div class="skeleton" style="width:40%;height:11px"></div>
          </div>
        </div>
      `).join('');
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

