/* ============================================================
   ContabIA Portal — agent-widget.js
   Floating agent bubble, visible on every page except chat.html
   (redundant there). Sending a message from here hands it off
   to chat.html via sessionStorage, where the real agent-reply
   logic already lives (no logic duplicated here).
   ============================================================ */

let _agentDragging = false;
let _agentDragOffset = { x: 0, y: 0 };
let _agentPos = null; /* {left, top} once dragged; null = default anchored position */

/* open/closed state — persisted across pages, same pattern as
   theme.js's contabia-theme. */
function _getStoredAgentOpen() {
  try { return sessionStorage.getItem('contabia-agent-open') === '1'; }
  catch (e) { return false; }
}
function _setStoredAgentOpen(v) {
  try { sessionStorage.setItem('contabia-agent-open', v ? '1' : '0'); }
  catch (e) {}
}
function _getStoredAgentPos() {
  try {
    const raw = sessionStorage.getItem('contabia-agent-pos');
    return raw ? JSON.parse(raw) : null;
  } catch (e) { return null; }
}
function _setStoredAgentPos(pos) {
  try {
    if (pos) sessionStorage.setItem('contabia-agent-pos', JSON.stringify(pos));
    else sessionStorage.removeItem('contabia-agent-pos');
  } catch (e) {}
}

function mountAgentWidget(page) {
  if (page === 'chat.html') return; /* redundant on the chat page itself */
  if (document.getElementById('agent-fab')) return;

  const e = currentEntityData();
  const user = currentUser();
  const cta = primaryCTA();

  /* single fixed flex column: panel (if open) stacks directly above
     the launcher via normal flow — no manual offset math needed. */
  const widget = document.createElement('div');
  widget.id = 'agent-widget';
  widget.className = 'agent-widget';

  const thread = buildAgentIntroThread(e, user);
  const threadHtml = thread.map(m => `<div class="msg ${m.who}">${m.text}</div>`).join('');

  widget.innerHTML = `
    <div id="agent-panel" class="agent-panel">
      <div class="agent-head" id="agent-head">
        <div class="av">A</div>
        <div class="info">
          <div class="t">Su agente</div>
          <div class="s"><span class="dot"></span>Sincronizado con WhatsApp</div>
        </div>
        <div class="act" title="Abrir conversación completa" onclick="event.stopPropagation(); location.href='chat.html'">⤢</div>
        <div class="act" title="Minimizar" onclick="event.stopPropagation(); closeAgentPanel()">✕</div>
      </div>
      <div class="agent-body">
        ${threadHtml}
      </div>
      <div class="agent-foot">
        <input type="text" id="agent-fab-input" placeholder="Escriba a su agente…" autocomplete="off">
        <div class="send" onclick="sendFromAgentWidget()">↑</div>
      </div>
    </div>
    <div id="agent-fab" class="agent-fab" title="Su agente · sincronizado con WhatsApp">
      <span class="glyph">A</span>
      <span class="wa-dot"><svg viewBox="0 0 24 24" width="11" height="11" fill="#fff"><path d="M12 2a10 10 0 0 0-8.5 15.3L2 22l4.8-1.5A10 10 0 1 0 12 2zm0 2a8 8 0 1 1-4.2 14.8l-.3-.2-2.6.8.8-2.5-.2-.3A8 8 0 0 1 12 4z"/></svg></span>
    </div>`;

  document.body.appendChild(widget);

  document.getElementById('agent-fab').addEventListener('click', toggleAgentPanel);
  document.getElementById('agent-fab-input').addEventListener('keypress', (ev) => {
    if (ev.key === 'Enter') sendFromAgentWidget();
  });

  const head = document.getElementById('agent-head');
  head.addEventListener('pointerdown', startAgentDrag);

  /* restore open state + dragged position from the last page */
  if (_getStoredAgentOpen()) {
    document.getElementById('agent-panel').classList.add('open');
    document.body.classList.add('chat-open');
  }
  _agentPos = _getStoredAgentPos();
  if (_agentPos) {
    const panel = document.getElementById('agent-panel');
    panel.classList.add('dragged');
    panel.style.left = _agentPos.left + 'px';
    panel.style.top = _agentPos.top + 'px';
  }
}

function toggleAgentPanel() {
  const panel = document.getElementById('agent-panel');
  if (!panel) return;
  panel.classList.toggle('open');
  const isOpen = panel.classList.contains('open');
  document.body.classList.toggle('chat-open', isOpen);
  _setStoredAgentOpen(isOpen);
}

function closeAgentPanel() {
  const panel = document.getElementById('agent-panel');
  if (!panel) return;
  panel.classList.remove('open');
  document.body.classList.remove('chat-open');
  _setStoredAgentOpen(false);
  /* reset position so it always reopens stacked above the launcher */
  _agentPos = null;
  _setStoredAgentPos(null);
  panel.classList.remove('dragged');
  panel.style.left = '';
  panel.style.top = '';
}

function sendFromAgentWidget() {
  const input = document.getElementById('agent-fab-input');
  const text = (input.value || '').trim();
  if (!text) return;
  try { sessionStorage.setItem('contabia_pending_msg', text); } catch (e) {}
  location.href = 'chat.html';
}

function startAgentDrag(ev) {
  const panel = document.getElementById('agent-panel');
  if (!panel) return;
  const rect = panel.getBoundingClientRect();
  _agentDragOffset = { x: ev.clientX - rect.left, y: ev.clientY - rect.top };
  _agentDragging = true;
  window.addEventListener('pointermove', duringAgentDrag);
  window.addEventListener('pointerup', endAgentDrag);
}
function duringAgentDrag(ev) {
  if (!_agentDragging) return;
  const panel = document.getElementById('agent-panel');
  if (!panel) return;
  panel.classList.add('dragged');
  let left = ev.clientX - _agentDragOffset.x;
  let top = ev.clientY - _agentDragOffset.y;
  left = Math.max(8, Math.min(left, window.innerWidth - 60));
  top = Math.max(8, Math.min(top, window.innerHeight - 60));
  panel.style.left = left + 'px';
  panel.style.top = top + 'px';
}
function endAgentDrag() {
  _agentDragging = false;
  window.removeEventListener('pointermove', duringAgentDrag);
  window.removeEventListener('pointerup', endAgentDrag);
  const panel = document.getElementById('agent-panel');
  if (panel && panel.classList.contains('dragged')) {
    _agentPos = { left: parseFloat(panel.style.left) || 0, top: parseFloat(panel.style.top) || 0 };
    _setStoredAgentPos(_agentPos);
  }
}
