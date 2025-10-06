// web/news.js (debug)
document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('newsGrid');
  const search = document.getElementById('newsSearch');
  const refreshBtn = document.getElementById('newsRefresh');

  function log(msg, extra) {
    console.log('[news]', msg, extra || '');
    const el = document.createElement('div');
    el.className = 'card';
    el.style.fontSize = '12px';
    el.textContent = `[news] ${msg}`;
    // comment the next line after debugging if it's too noisy
    // grid.prepend(el);
  }

  function timeAgo(ts) {
    const d = Date.now() - Number(ts || 0);
    const mins = Math.max(0, Math.floor(d / 60000));
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  }

  function esc(s = '') {
    return String(s).replace(/[&<>"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  function newsCard(n) {
    const hasImg = n.image && n.image !== '/news-placeholder.png';
    const imgPart = hasImg
      ? `<img class="news-img" src="${esc(n.image)}" alt="">`
      : `<div class="news-img placeholder"></div>`;
    const caption = (n.description || '').slice(0, 140);

    return `
      <article class="news-card">
        <a class="news-link" href="${esc(n.link)}" target="_blank" rel="noopener noreferrer">
          ${imgPart}
          <div class="news-body">
            <h3 class="news-title">${esc(n.title || '')}</h3>
            <p class="news-caption">${esc(caption)}</p>
            <div class="news-meta">
              <span>${esc(n.domain || n.source || '')}</span>
              <span>•</span>
              <span>${timeAgo(n.publishedAt)}</span>
              <span class="news-read">Read →</span>
            </div>
          </div>
        </a>
      </article>
    `;
  }

  async function loadNews() {
    const q = (search?.value || '').trim();
    const u = new URL('/api/news', location.origin);
    if (q) u.searchParams.set('q', q);
    u.searchParams.set('limit', '18');

    grid.innerHTML = `<div class="card">Loading news…</div>`;
    log('GET ' + u.toString());

    try {
      const res = await fetch(u.toString(), { headers: { 'Accept': 'application/json' } });
      log('status ' + res.status);
      const data = await res.json();

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      log('items ' + (data.items?.length || 0));

      if (!data.items?.length) {
        grid.innerHTML = `<div class="card">No news found. Try a different search.</div>`;
        return;
      }
      grid.innerHTML = data.items.map(newsCard).join('');
    } catch (e) {
      console.error('[news] error', e);
      grid.innerHTML = `<div class="card">News error: ${String(e.message || e)}</div>`;
    }
  }

  refreshBtn?.addEventListener('click', loadNews);
  search?.addEventListener('keydown', (e) => { if (e.key === 'Enter') loadNews(); });

  // prove DOM is found
  if (!grid) {
    console.error('[news] #newsGrid not found');
    alert('news.js: element #newsGrid not found — check index.html IDs');
    return;
  }

  // Initial load
  loadNews();
});
