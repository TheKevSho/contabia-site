/* ============================================================
   ContabIA Portal — nav.js
   Injects shared sidebar into any page
   ============================================================ */

function renderSidebar(activeHref) {
  return `
  <aside class="sidebar">
    <div class="sidebar-logo">
      <div class="wordmark">Contab<span>IA</span></div>
      <div class="tagline">Su agente cierra sus libros.</div>
    </div>
    <div class="sidebar-client">
      <div class="client-name">Cantamar Beach Hostel</div>
      <span class="period-badge">Marzo 2026</span>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section-label">Principal</div>
      <a href="index.html" class="nav-item${activeHref==='index.html'?' active':''}">
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
        Resumen
      </a>
      <a href="tracker.html" class="nav-item${activeHref==='tracker.html'?' active':''}">
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>
        Seguimiento de Cierre
      </a>

      <div class="nav-section-label">Revisión</div>
      <a href="exceptions.html" class="nav-item${activeHref==='exceptions.html'?' active':''}">
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        Excepciones
        <span class="nav-badge critical">7</span>
      </a>
      <a href="journal-entries.html" class="nav-item${activeHref==='journal-entries.html'?' active':''}">
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        Comprobantes (JEs)
        <span class="nav-badge">5</span>
      </a>

      <div class="nav-section-label">Informes</div>
      <a href="deliverables.html" class="nav-item${activeHref==='deliverables.html'?' active':''}">
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
        Entregables
      </a>

      <div class="nav-section-label">Agente</div>
      <a href="chat.html" class="nav-item${activeHref==='chat.html'?' active':''}">
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
        Chat con el Agente
      </a>
    </nav>
    <div class="sidebar-footer">
      <div class="user-name">Kevin Carey</div>
      <div>Propietario · <a href="login.html" style="color:rgba(255,248,240,.4)">Salir</a></div>
    </div>
  </aside>`;
}

// Auto-inject sidebar on pages that have id="sidebar-mount"
document.addEventListener('DOMContentLoaded', () => {
  const mount = document.getElementById('sidebar-mount');
  if (!mount) return;

  const page = window.location.pathname.split('/').pop() || 'index.html';
  mount.innerHTML = renderSidebar(page);

  // --- Mobile nav: hamburger button + backdrop (hidden on desktop via CSS) ---
  if (!document.getElementById('sidebar-toggle')) {
    const toggle = document.createElement('button');
    toggle.id = 'sidebar-toggle';
    toggle.className = 'sidebar-toggle';
    toggle.setAttribute('aria-label', 'Abrir menú');
    toggle.innerHTML = '<span></span><span></span><span></span>';
    document.body.appendChild(toggle);
  }
  if (!document.getElementById('sidebar-backdrop')) {
    const backdrop = document.createElement('div');
    backdrop.id = 'sidebar-backdrop';
    backdrop.className = 'sidebar-backdrop';
    document.body.appendChild(backdrop);
  }

  const sidebar  = document.querySelector('.sidebar');
  const toggle   = document.getElementById('sidebar-toggle');
  const backdrop = document.getElementById('sidebar-backdrop');

  const openSidebar  = () => { sidebar.classList.add('open');  backdrop.classList.add('open');  document.body.classList.add('no-scroll'); };
  const closeSidebar = () => { sidebar.classList.remove('open'); backdrop.classList.remove('open'); document.body.classList.remove('no-scroll'); };

  toggle.addEventListener('click', () => {
    sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
  });
  backdrop.addEventListener('click', closeSidebar);
  // Close after tapping any nav link (so navigation feels clean on mobile)
  sidebar.querySelectorAll('.nav-item').forEach(a => a.addEventListener('click', closeSidebar));
  // Close on Escape
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSidebar(); });
});
