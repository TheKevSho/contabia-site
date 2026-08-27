/* ============================================================
   ContabIA Portal — auth.js
   Session check. Runs on every protected portal page.

   - Reads contabia_auth from sessionStorage.
   - If missing → redirect to login.html (the three login landings
     are the only unprotected pages; they don't include this file).
   - Ensures contabia_role + contabia_entity are populated with
     defaults if absent (from DATA.user).

   Password ("Scrooge") lives in the login landings.
   ============================================================ */
(function() {
  const auth = sessionStorage.getItem('contabia_auth');
  /* match login pages with or without .html (Cloudflare Pages pretty URLs) */
  const isLoginPage = /\/(login|login-contador|login-gerente)(\.html)?\/?$/.test(location.pathname);
  if (auth !== '1') {
    if (!isLoginPage) {
      location.replace('login.html');
      return;
    }
  }

  /* ensure role + entity defaults. Live sessions never inherit
     DATA.user.default_entity (cantamar-001). */
  if (typeof isLiveMode === 'function' && isLiveMode()) {
    if (!sessionStorage.getItem('contabia_role')) {
      const rec = (() => { try { return JSON.parse(sessionStorage.getItem('contabia_user') || 'null'); } catch (e) { return null; } })();
      sessionStorage.setItem('contabia_role', (rec && rec.role) || 'owner');
    }
    sessionStorage.setItem('contabia_entity', 'sonata-001');
  } else if (typeof DATA !== 'undefined') {
    if (!sessionStorage.getItem('contabia_role')) {
      sessionStorage.setItem('contabia_role', DATA.user.default_role);
    }
    if (!sessionStorage.getItem('contabia_entity')) {
      sessionStorage.setItem('contabia_entity', DATA.user.default_entity);
    }
  }
})();
