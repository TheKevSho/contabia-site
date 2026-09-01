/* ============================================================
   ContabIA Portal — agent-widget.js
   Floating agent. Open state, position, and THREAD persist across
   pages (sessionStorage). Send stays in the popup — never routes
   to chat.html. chat.html reads/writes the same thread.
   ============================================================ */

const AGENT_THREAD_KEY = 'contabia_agent_thread';
const AGENT_CONTEXT_KEY = 'contabia_agent_context';

const RELATED_MD = {
  'EX-J07-06': ['(sin PDF marina en bóveda — decisión de retención)'],
  'EX-J07-07': ['Olímpica COMK5038 — bill still open in Alegra dump'],
  'EX-J07-09': ['DetallePlanilla_38244858_2026_07_E.pdf'],
  'EX-J07-10': ['July-2026-JE-Package-v2.md'],
  'EX-J07-11': ['78100001780_JUL2026.xlsx', 'Extracto_BBVA-CtaCte-014857-FondoDigital-004841_2026-07.md'],
  'EX-J07-12': ['Bold_Transacciones_2026-07.md', 'Bold_Transacciones_2026-07.xlsx'],
  'EX-J07-15': ['(July OTA-GYG / OTA-Viator xlsx missing — Jan–Jun in vault)'],
  'AJ-J07-01': ['Bold_Transacciones_2026-07.md', 'EX-J07-12'],
  'AJ-J06-REVERSE': ['Bold_Transacciones_2026-07.md', 'EX-J07-12'],
  'R-11-JUL': ['July-2026-JE-Package-v2.md', 'EX-J07-10'],
  'R-11-CATCHUP': ['July-2026-JE-Package-v2.md', 'EX-J07-10', 'EX-J07-13'],
  'R-14-JUL': ['July-2026-JE-Package-v2.md', 'EX-J07-10'],
};

let _agentDragging = false;
let _agentDragOffset = { x: 0, y: 0 };
let _agentPos = null;
let _agentSending = false;

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

function loadAgentThread() {
  try {
    const raw = sessionStorage.getItem(AGENT_THREAD_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch (e) {}
  return null;
}

function saveAgentThread(msgs) {
  try { sessionStorage.setItem(AGENT_THREAD_KEY, JSON.stringify(msgs || [])); }
  catch (e) {}
}

function defaultAgentThread() {
  const e = (typeof currentEntityData === 'function') ? currentEntityData() : { closeSummary: {} };
  const user = (typeof currentUser === 'function') ? currentUser() : { name: '' };
  if (typeof buildAgentIntroThread === 'function') return buildAgentIntroThread(e, user);
  return [{ who: 'agent', text: 'Hola. Soy el agente ContabIA de Tayrona Sailing.' }];
}

function getAgentThread() {
  return loadAgentThread() || defaultAgentThread();
}

function renderAgentBody(msgs) {
  const body = document.getElementById('agent-body');
  if (!body) return;
  body.innerHTML = (msgs || []).map(m =>
    `<div class="msg ${m.who}">${escapeAgentHtml(m.text)}</div>`
  ).join('');
  body.scrollTop = body.scrollHeight;
}

function escapeAgentHtml(s) {
  return String(s || '')
    .replace(/&/g, '&' + 'amp;')
    .replace(/</g, '&' + 'lt;')
    .replace(/>/g, '&' + 'gt;')
    .replace(/\n/g, '<br>');
}

function mountAgentWidget(page) {
  /* Popup lives on every page including chat.html so open-state + thread
     survive navigation. On chat.html we still mount the FAB; the full-page
     thread is a second view of the same store. */
  if (document.getElementById('agent-fab')) return;

  const widget = document.createElement('div');
  widget.id = 'agent-widget';
  widget.className = 'agent-widget';
  widget.innerHTML = `
    <div id="agent-panel" class="agent-panel">
      <div class="agent-head" id="agent-head">
        <div class="av">A</div>
        <div class="info">
          <div class="t">Su agente</div>
          <div class="s"><span class="dot"></span>WhatsApp · cola julio</div>
        </div>
        <div class="act" title="Pantalla completa" onclick="event.stopPropagation(); location.href='chat.html'">⤢</div>
        <div class="act" title="Minimizar" onclick="event.stopPropagation(); closeAgentPanel()">✕</div>
      </div>
      <div class="agent-body" id="agent-body"></div>
      <div class="agent-foot">
        <input type="text" id="agent-fab-input" placeholder="Escriba a su agente…" autocomplete="off">
        <div class="send" onclick="sendFromAgentWidget()">↑</div>
      </div>
    </div>
    <div id="agent-fab" class="agent-fab" title="Su agente">
      <span class="glyph">A</span>
      <span class="wa-dot"><svg viewBox="0 0 24 24" width="11" height="11" fill="#fff"><path d="M12 2a10 10 0 0 0-8.5 15.3L2 22l4.8-1.5A10 10 0 1 0 12 2zm0 2a8 8 0 1 1-4.2 14.8l-.3-.2-2.6.8.8-2.5-.2-.3A8 8 0 0 1 12 4z"/></svg></span>
    </div>`;
  document.body.appendChild(widget);

  const msgs = getAgentThread();
  if (!loadAgentThread()) saveAgentThread(msgs);
  renderAgentBody(msgs);

  document.getElementById('agent-fab').addEventListener('click', toggleAgentPanel);
  document.getElementById('agent-fab-input').addEventListener('keypress', (ev) => {
    if (ev.key === 'Enter') sendFromAgentWidget();
  });
  document.getElementById('agent-head').addEventListener('pointerdown', startAgentDrag);

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

function openAgentPanel() {
  const panel = document.getElementById('agent-panel');
  if (!panel) return;
  panel.classList.add('open');
  document.body.classList.add('chat-open');
  _setStoredAgentOpen(true);
}

function closeAgentPanel() {
  const panel = document.getElementById('agent-panel');
  if (!panel) return;
  panel.classList.remove('open');
  document.body.classList.remove('chat-open');
  _setStoredAgentOpen(false);
}

function appendAgentMessage(who, text) {
  const msgs = getAgentThread();
  msgs.push({ who, text });
  saveAgentThread(msgs);
  renderAgentBody(msgs);
  if (typeof window.onAgentThreadChange === 'function') window.onAgentThreadChange(msgs);
}

async function sendFromAgentWidget() {
  const input = document.getElementById('agent-fab-input');
  const text = (input && input.value || '').trim();
  if (!text || _agentSending) return;
  input.value = '';
  await dispatchAgentUserMessage(text);
}

async function dispatchAgentUserMessage(text) {
  if (!text || _agentSending) return;
  _agentSending = true;
  let outbound = text;
  try {
    const ctx = sessionStorage.getItem(AGENT_CONTEXT_KEY);
    if (ctx) outbound = ctx + '\n\nPregunta: ' + text;
  } catch (e) {}
  appendAgentMessage('user', text);
  appendAgentMessage('agent', '…');
  try {
    let reply = '';
    if (typeof isLiveMode === 'function' && isLiveMode() && typeof postLiveChat === 'function') {
      const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
      const sessionId = sessionStorage.getItem('contabia_chat_session') || null;
      const res = await postLiveChat('sonata-001', outbound, lang, sessionId);
      if (res && res.session_id) sessionStorage.setItem('contabia_chat_session', res.session_id);
      reply = (res && (res.reply || res.message)) || 'Sin respuesta.';
    } else if (typeof agentReply === 'function') {
      reply = agentReply(text);
    } else {
      reply = 'Agente no conectado. Reenvíe por WhatsApp a su chat personal de Hermes.';
    }
    const msgs = getAgentThread();
    if (msgs.length && msgs[msgs.length - 1].text === '…') msgs.pop();
    msgs.push({ who: 'agent', text: reply });
    saveAgentThread(msgs);
    renderAgentBody(msgs);
    if (typeof window.onAgentThreadChange === 'function') window.onAgentThreadChange(msgs);
  } catch (err) {
    const msgs = getAgentThread();
    if (msgs.length && msgs[msgs.length - 1].text === '…') msgs.pop();
    msgs.push({ who: 'agent', text: 'No pude contactar al agente: ' + err.message });
    saveAgentThread(msgs);
    renderAgentBody(msgs);
  } finally {
    _agentSending = false;
  }
}

function relatedDocsFor(id) {
  return RELATED_MD[id] || [];
}

function openAgentOnItem(kind, item) {
  if (!item) return;
  const id = item.id || '';
  const title = item.title || item.description || id;
  const docs = relatedDocsFor(id);
  const extra = (item.linked_exceptions || []).map(relatedDocsFor).flat();
  const allDocs = Array.from(new Set(docs.concat(extra)));
  const lang = (typeof currentLang === 'function' ? currentLang() : 'es');
  const docLine = allDocs.length
    ? (lang === 'en' ? 'Related notes: ' : 'Notas / docs: ') + allDocs.join(' · ')
    : (lang === 'en' ? 'No related .md on file for this id.' : 'Sin .md vinculado a este id.');
  const rec = item.ai_recommendation || item.description || '';
  const ctx =
    (kind === 'je' ? 'JE ' : 'Excepción ') + id + '\n' +
    title + '\n' +
    (rec ? rec + '\n' : '') +
    docLine;
  try { sessionStorage.setItem(AGENT_CONTEXT_KEY, ctx); } catch (e) {}
  const note = lang === 'en'
    ? `Looking at ${id}. ${docLine} Ask me about this item — I will not invent figures.`
    : `Viendo ${id}. ${docLine} Pregúnteme sobre este ítem. No invento cifras.`;
  appendAgentMessage('agent', note);
  if (!document.getElementById('agent-fab')) {
    try { sessionStorage.setItem('contabia-agent-open', '1'); } catch (e) {}
    return;
  }
  openAgentPanel();
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
