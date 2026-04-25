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
  if (auth !== '1') {
    /* not authenticated — bounce to default login */
    if (!location.pathname.endsWith('login.html')
     && !location.pathname.endsWith('login-contador.html')
     && !location.pathname.endsWith('login-gerente.html')) {
      location.replace('login.html');
      return;
    }
  }

  /* ensure role + entity defaults from DATA.user (data.js loaded earlier) */
  if (typeof DATA !== 'undefined') {
    if (!sessionStorage.getItem('contabia_role')) {
      sessionStorage.setItem('contabia_role', DATA.user.default_role);
    }
    if (!sessionStorage.getItem('contabia_entity')) {
      sessionStorage.setItem('contabia_entity', DATA.user.default_entity);
    }
  }
})();
