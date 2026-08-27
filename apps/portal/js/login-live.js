/* Shared login helper for the three role landings.
   Live users POST /auth/login (kevin / edwin / nick). Always live — no toggle.
   Demo is a separate account: username `demo`, password `Scrooge`.
   Marketing CTAs still land with ?demo=1. */
(function (global) {
  const DEMO_USER = 'demo';
  const DEMO_PASSWORD = 'Scrooge';
  const API_BASE = window.CONTABIA_API_BASE ||
    (location.protocol === 'https:' ? 'https://api.contabia.co' : 'http://localhost:8000');

  function enterDemo(role, redirect) {
    sessionStorage.setItem('contabia_auth', '1');
    sessionStorage.setItem('contabia_role', role);
    sessionStorage.setItem('contabia_entity', 'cantamar-001');
    sessionStorage.setItem('contabia_demo', '1');
    sessionStorage.removeItem('contabia_live');
    sessionStorage.removeItem('contabia_api_token');
    sessionStorage.setItem('contabia_user', JSON.stringify({
      username: 'demo', name: 'Demo ContabIA', email: 'demo@contabia.co', role: role
    }));
    location.href = redirect;
  }

  function enterLive(data, fallbackRole, redirect) {
    const user = data.user || {};
    const role = user.role || fallbackRole;
    const entity = data.default_entity || user.default_entity || 'sonata-001';
    sessionStorage.setItem('contabia_auth', '1');
    sessionStorage.setItem('contabia_role', role);
    sessionStorage.setItem('contabia_entity', entity);
    sessionStorage.setItem('contabia_api_token', data.token);
    sessionStorage.setItem('contabia_live', '1');
    sessionStorage.setItem('contabia_user', JSON.stringify({
      username: user.username, name: user.name, email: user.email, role: role
    }));
    sessionStorage.removeItem('contabia_demo');
    location.href = redirect;
  }

  function isDemoAttempt(user, pw) {
    const u = (user || '').trim().toLowerCase();
    const userPart = u.includes('@') ? u.split('@')[0] : u;
    return userPart === DEMO_USER && pw === DEMO_PASSWORD;
  }

  global.contabiaAttemptLogin = async function (opts) {
    const role = opts.role;
    const redirect = opts.redirect;
    const user = (document.getElementById('email').value || '').trim().toLowerCase();
    const pw = document.getElementById('password').value;
    const err = document.getElementById('error');

    if (isDemoAttempt(user, pw)) {
      enterDemo(role, redirect);
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pw }),
      });
      if (res.ok) {
        const data = await res.json();
        enterLive(data, role, redirect);
        return;
      }
    } catch (e) { /* API unreachable */ }

    err.textContent = typeof t === 'function' ? t('login.error') : 'Credenciales incorrectas.';
    document.getElementById('password').value = '';
    document.getElementById('password').focus();
  };

  global.contabiaMaybeDemo = function (role, redirect) {
    const params = new URLSearchParams(location.search);
    if (params.get('demo') === '1') enterDemo(role, redirect);
  };
})(window);
