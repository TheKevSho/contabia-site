/* ============================================================
   ContabIA Portal — theme.js
   Applies + persists light/dark/system appearance. Loaded in
   <head> (before body paint) so there's no flash of the wrong
   theme. The toggle UI itself lives in the sidebar footer
   (rendered by nav.js), which calls back into the functions here.
   ============================================================ */
(function () {
  function systemPrefersDark() {
    try { return window.matchMedia('(prefers-color-scheme: dark)').matches; }
    catch (e) { return false; }
  }

  function getStoredTheme() {
    try { return localStorage.getItem('contabia-theme') || 'system'; }
    catch (e) { return 'system'; }
  }

  function applyTheme(t) {
    const isDark = t === 'dark' || (t === 'system' && systemPrefersDark());
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }

  applyTheme(getStoredTheme());

  window.getContabiaTheme = getStoredTheme;
  window.setContabiaTheme = function (t) {
    try { localStorage.setItem('contabia-theme', t); } catch (e) {}
    applyTheme(t);
    if (typeof renderAppearancePopover === 'function') renderAppearancePopover();
  };

  try {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
      if (getStoredTheme() === 'system') applyTheme('system');
    });
  } catch (e) {}
})();
