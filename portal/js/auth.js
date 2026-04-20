/* ============================================================
   ContabIA Portal — auth.js
   Password gate — shared across all portal pages
   Password: Scrooge
   ============================================================ */
(function() {
  if (sessionStorage.getItem('contabia_auth') === '1') return;
  // Not authenticated — show gate
  const gate = document.createElement('div');
  gate.id = 'authGate';
  gate.innerHTML = `
    <div style="position:fixed;inset:0;background:#1B2A4A;display:flex;align-items:center;justify-content:center;z-index:99999;font-family:'Source Sans 3',system-ui,sans-serif">
      <div style="background:#FFF8F0;border-radius:16px;padding:40px;width:100%;max-width:380px;box-shadow:0 8px 32px rgba(0,0,0,.3);text-align:center">
        <div style="font-family:'DM Serif Display',Georgia,serif;font-size:28px;color:#1B2A4A;margin-bottom:6px">Contab<span style="color:#D4704A">IA</span></div>
        <div style="font-size:13px;color:#8B8178;margin-bottom:28px">Portal del cliente</div>
        <input id="gateInput" type="password" placeholder="Contraseña"
          style="width:100%;padding:10px 14px;border:1.5px solid #E8E2DB;border-radius:8px;font-size:15px;outline:none;margin-bottom:12px;text-align:center;background:white"
          onkeypress="if(event.key==='Enter')document.getElementById('gateBtn').click()">
        <div id="gateErr" style="color:#C0392B;font-size:12px;margin-bottom:8px;min-height:16px"></div>
        <button id="gateBtn"
          style="width:100%;background:#D4704A;color:white;border:none;padding:11px;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer"
          onclick="
            if(document.getElementById('gateInput').value==='Scrooge'){
              sessionStorage.setItem('contabia_auth','1');
              document.getElementById('authGate').remove();
            } else {
              document.getElementById('gateErr').textContent='Contraseña incorrecta';
              document.getElementById('gateInput').value='';
              document.getElementById('gateInput').focus();
            }
          ">Entrar</button>
      </div>
    </div>`;
  document.body.appendChild(gate);
  // Focus input after render
  setTimeout(() => { const i = document.getElementById('gateInput'); if(i) i.focus(); }, 50);
})();
