/* ============================================================
   ContabIA Portal — entregables-tree.js

   Dense ledger of the v5 Sonata Mas model (not KPI tiles).
   Presente = 15 cols, Ene–Jul REAL sourced, Ago–Dic blank
     (xlsx forecast cells are empty formulas — do not invent).
   Modelado = 27 cols + palancas. Forecast fill is Jul × factor
     labeled PROY / demo. Never shown as REAL. 2027 stays blank
     unless the user overrides a cell.

   Source: master_data.py + SonataMas_Dashboard_2026_ES.xlsx
   data_only. July not closed. No Alegra POST.
   ============================================================ */

(function () {
  const COP = function (n) {
    if (n == null || n === '') return '·';
    return (n < 0 ? '−' : '') + Math.abs(Math.round(n)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  };

  const MONTHS15_ES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago 1-15','Ago 16-31','Sep 1-15','Sep 16-30','Oct 1-15','Oct 16-31','Nov','Dic'];
  const MONTHS15_EN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug 1-15','Aug 16-31','Sep 1-15','Sep 16-30','Oct 1-15','Oct 16-31','Nov','Dec'];
  const Y27_ES = ['Ene27','Feb27','Mar27','Abr27','May27','Jun27','Jul27','Ago27','Sep27','Oct27','Nov27','Dic27'];
  const Y27_EN = ['Jan27','Feb27','Mar27','Apr27','May27','Jun27','Jul27','Aug27','Sep27','Oct27','Nov27','Dec27'];

  const kind = function (i) { return i < 7 ? 'real' : (i < 13 ? 'qinc' : 'proy'); };

  /* Sourced Ene–Jul. Jan cash_end unknown — not invented.
     GOP / neta from workbook stored values (not live formula cells). */
  const ACT = {
    cash_begin: [155509521, null, 43300803, 6937762, 24026296, 25171246, 31240004],
    cash_end:   [null, 43300803, 6937762, 24026296, 25171246, 31240004, 62762964],
    netrev: [169174454, 83827575, 121425005, 134064673, 99222750, 105435060, 158706596],
    ventas: [169220454, 83951575, 122081005, 135341673, 99222750, 105515222, 160424759],
    ret:    [-46000, -124000, -656000, -1277000, 0, -80162, -1718163],
    direct: [-55480191, -25131201, -52086134, -40777066, -36349647, -36984882, -39950165],
    cogs:   [-2762643, -1677400, -2376434, -1432031, -1724517, -1776378, -2082490],
    cos:    [-52717548, -23453801, -49709700, -39345035, -34625130, -35208504, -37867675],
    gross:  [113694263, 58696374, 69338871, 93287607, 62873103, 68450178, 118756431],
    undist: [-49354933, -59754856, -53407434, -50950559, -42276210, -36375527, -45781839],
    temp:   [-4113915, -3258255, -5227530, -7524962, -3937685, -2654235, -6663375],
    nom:    [-35511362, -32316470, -32742946, -29196377, -30029387, -22320158, -28866282],
    gen:    [-9444241, -23570073, -14956980, -13445647, -7679345, -10653937, -9601688],
    svc:    [-285415, -610058, -479978, -783573, -629793, -747197, -650494],
    gop:    [64339330, -1058482, 15931437, 42337048, 20596893, 32074651, 72974592],
    neta:   [50036940, -10749239, -4257084, 30540062, 12099171, 24554831, 65952046],
    depr:   [-1038987, -1038987, -1038987, -1038987, -1038987, 0, -1038987],
    fin:    [-6062309, -5211080, -6870502, -4835665, -5721680, -5588726, -4323219],
    tax:    [-7205884, -3253543, -7613411, -5369597, -1559069, -1442611, -1055706],
    assets: [null, 735214985, 724372220, 718560973, 713612812, 719864941, 412235708],
    liab:   [null, 452977317, 446408439, 404596868, 390917399, 358026590, 336897086],
    equity: [301054443, 282237668, 277963781, 313964106, 322695414, 361838351, 75338622],
    kcomp:  [null, null, null, null, null, null, 8976900],
  };

  let tab = 'presente';
  let open = { caja: true, pl: true, bs: false, sh: false };
  let child = { caja: false, ing: false, cos: false, gast: false, nop: false, act: false, pas: false, pat: false, sA: false, sB: false, sC: false, sE: false };
  let overrides = {};
  let rootEl = null;

  function tt(key, fallback) {
    if (typeof t !== 'function') return fallback;
    const v = t(key);
    return (v && v !== key) ? v : fallback;
  }

  function lang() {
    return (typeof currentLang === 'function' ? currentLang() : 'es');
  }

  function months() {
    const en = lang() === 'en';
    const m15 = en ? MONTHS15_EN : MONTHS15_ES;
    if (tab === 'modelado') return m15.concat(en ? Y27_EN : Y27_ES);
    return m15;
  }

  function jul(key) { return ACT[key][6]; }

  function series(key) {
    const n = tab === 'modelado' ? 27 : 15;
    const out = new Array(n).fill(null);
    for (let i = 0; i < 7; i++) out[i] = ACT[key] ? ACT[key][i] : null;
    if (tab !== 'modelado') return out;
    const pvEl = document.getElementById('del-p-ventas');
    const pnEl = document.getElementById('del-p-nom');
    const loanEl = document.getElementById('del-p-loan');
    const pv = pvEl ? (+pvEl.value) / 100 : 1;
    const pn = pnEl ? (+pnEl.value) / 100 : 1;
    const loan = loanEl ? loanEl.checked : false;
    const fillKeys = {
      ventas: pv, netrev: pv, ret: 1, direct: 1, cogs: 1, cos: 1, gross: pv,
      undist: pn, temp: pn, nom: pn, gen: 1, svc: 1,
      gop: null, neta: null, cash_end: null, cash_begin: null,
      depr: 1, fin: loan ? 0 : 1, tax: 1,
      assets: null, liab: null, equity: null, kcomp: 1,
    };
    for (let i = 7; i < n; i++) {
      const id = key + '|' + i;
      if (overrides[id] != null) { out[i] = overrides[id]; continue; }
      if (i >= 15) continue;
      const f = fillKeys[key];
      if (f == null) out[i] = null;
      else out[i] = Math.round(jul(key) * f);
    }
    return out;
  }

  function gopSeries() {
    const n = tab === 'modelado' ? 27 : 15;
    const gross = series('gross');
    const undist = series('undist');
    const out = new Array(n).fill(null);
    for (let i = 0; i < 7; i++) out[i] = ACT.gop[i];
    if (tab === 'modelado') {
      for (let i = 7; i < n; i++) {
        const id = 'gop|' + i;
        if (overrides[id] != null) { out[i] = overrides[id]; continue; }
        if (i >= 15) continue;
        out[i] = (gross[i] != null && undist[i] != null) ? gross[i] + undist[i] : null;
      }
    }
    return out;
  }

  function netaSeries() {
    const g = gopSeries();
    const depr = series('depr');
    const fin = series('fin');
    const tax = series('tax');
    const n = g.length;
    const out = new Array(n).fill(null);
    for (let i = 0; i < 7; i++) out[i] = ACT.neta[i];
    if (tab === 'modelado') {
      for (let i = 7; i < n; i++) {
        const id = 'neta|' + i;
        if (overrides[id] != null) { out[i] = overrides[id]; continue; }
        if (i >= 15) continue;
        out[i] = ([g[i], depr[i], fin[i], tax[i]].every(function (x) { return x != null; })
          ? g[i] + depr[i] + fin[i] + tax[i] : null);
      }
    }
    return out;
  }

  function cell(key, i, val, editable) {
    const k = kind(i);
    let cls = 'num ' + k;
    if (val == null) cls += ' blank';
    else if (val < 0) cls += ' neg';
    if (tab === 'modelado' && i >= 7 && i < 15 && val != null) cls += ' demo';
    if (editable && tab === 'modelado' && i >= 7) cls += ' edit';
    if (overrides[key + '|' + i] != null) cls += ' over';
    const txt = val == null ? '·' : COP(val);
    const extra = (editable && tab === 'modelado' && i >= 7)
      ? ' data-k="' + key + '" data-i="' + i + '" contenteditable="true"'
      : '';
    return '<td class="' + cls + '"' + extra + '>' + txt + '</td>';
  }

  function row(opts) {
    const id = opts.id;
    const label = opts.label;
    const vals = opts.vals;
    const total = opts.total;
    const rk = opts.kind;
    const indent = opts.indent;
    const childrenOf = opts.childrenOf;
    const editableKey = opts.editableKey;
    if (childrenOf && !child[childrenOf]) return '';
    let cls = rk || '';
    if (indent === 1) cls += ' child';
    if (indent === 2) cls += ' gchild';
    if (total) cls += ' tot';
    const hasKids = opts.kids;
    const tog = hasKids
      ? '<span class="tog" data-child="' + hasKids + '">' + (child[hasKids] ? '−' : '+') + '</span>'
      : '<span class="tog empty">+</span>';
    const tds = vals.map(function (v, i) {
      return cell(editableKey || id, i, v, !!editableKey && i >= 7);
    }).join('');
    return '<tr class="' + cls + '"><td class="concepto">' + tog + label + '</td>' + tds + '</tr>';
  }

  function sec(id, label, n) {
    const tog = '<span class="tog" data-sec="' + id + '">' + (open[id] ? '−' : '+') + '</span>';
    return '<tr class="sec"><td class="concepto">' + tog + label + '</td><td colspan="' + n + '"></td></tr>';
  }

  function estadoLabel(i) {
    if (i < 7) return tt('del.col.real', 'REAL');
    if (i < 13) return tt('del.col.quincena', 'QUINCENA');
    return tt('del.col.proy', 'PROY.');
  }

  function render() {
    if (!rootEl) return;
    const cols = months();
    const n = cols.length;
    const gop = gopSeries();
    const neta = netaSeries();
    const pvEl = document.getElementById('del-p-ventas');
    const pnEl = document.getElementById('del-p-nom');
    if (pvEl) {
      const v = rootEl.querySelector('#del-v-ventas');
      if (v) v.textContent = pvEl.value + '%';
    }
    if (pnEl) {
      const v = rootEl.querySelector('#del-v-nom');
      if (v) v.textContent = pnEl.value + '%';
    }
    const tp = rootEl.querySelector('#del-t-p');
    const tm = rootEl.querySelector('#del-t-m');
    if (tp) tp.classList.toggle('on', tab === 'presente');
    if (tm) tm.classList.toggle('on', tab === 'modelado');
    const pal = rootEl.querySelector('#del-palancas');
    if (pal) pal.classList.toggle('show', tab === 'modelado');
    rootEl.classList.toggle('modelado', tab === 'modelado');
    const banner = rootEl.querySelector('#del-banner');
    if (banner) {
      banner.className = 'del-note' + (tab === 'modelado' ? ' warn' : '');
      banner.innerHTML = tab === 'presente'
        ? tt('del.banner.presente', '<b>Presente</b> — 15 columnas. Ene–Jul REAL. Ago–Dic vacíos (el xlsx no tiene valores de proyección). Julio no cerrado. Sombra incluida, colapsada.')
        : tt('del.banner.modelado', '<b>Modelado</b> — 27 columnas. Palancas primero; clic en celda de proyección para override. Relleno demo = Jul × factor, marcado PROY — no es cierre oficial.');
    }
    const stamp = rootEl.querySelector('#del-modelo-stamp');
    if (stamp) stamp.hidden = tab !== 'modelado';

    let h = '<table class="del-grid"><thead><tr><th class="concepto">' + tt('del.concepto', 'Concepto') + '</th>'
      + cols.map(function (c, i) { return '<th class="' + kind(i) + '">' + c + '</th>'; }).join('')
      + '</tr><tr><th class="concepto sub">' + tt('del.estado', 'Estado') + '</th>'
      + cols.map(function (_, i) { return '<th class="sub">' + estadoLabel(i) + '</th>'; }).join('')
      + '</tr></thead><tbody>';

    h += sec('caja', tt('del.sec.caja', '1. Posición de caja'), n);
    if (open.caja) {
      h += row({ id: 'cash_begin', label: tt('del.row.cash_begin', 'Caja al inicio'), vals: series('cash_begin'), total: true, kind: 'cash', editableKey: 'cash_begin' });
      h += row({ id: 'cash_end', label: tt('del.row.cash_end', 'Caja al final — REAL Alegra (Ene–Jul)'), vals: series('cash_end'), total: true, kind: 'cash', editableKey: 'cash_end' });
      h += row({ id: 'caja_kids', label: tt('del.row.caja_kids', 'Actividades (operación / inversión / financiación)'), vals: cols.map(function () { return null; }), kids: 'caja' });
      if (child.caja) {
        h += row({ id: 'x1', label: tt('del.row.x1', 'Efectivo neto de operación — fórmulas vacías en xlsx'), vals: cols.map(function () { return null; }), indent: 1, childrenOf: 'caja' });
        h += row({ id: 'x2', label: tt('del.row.x2', 'Efectivo neto de inversión — fórmulas vacías en xlsx'), vals: cols.map(function () { return null; }), indent: 1, childrenOf: 'caja' });
        h += row({ id: 'x3', label: tt('del.row.x3', 'Efectivo neto de financiación — fórmulas vacías en xlsx'), vals: cols.map(function () { return null; }), indent: 1, childrenOf: 'caja' });
        h += row({ id: 'x4', label: tt('del.row.x4', 'Brecha no explicada (Edwin reclass — se muestra, no se tapona)'), vals: cols.map(function () { return null; }), indent: 1, childrenOf: 'caja' });
      }
    }

    h += sec('pl', tt('del.sec.pl', '2. Estado de resultados (causación)'), n);
    if (open.pl) {
      h += row({ id: 'netrev', label: tt('del.row.netrev', 'Total ingresos operacionales'), vals: series('netrev'), total: true, kids: 'ing', editableKey: 'netrev' });
      h += row({ id: 'ventas', label: tt('del.row.ventas', 'Ventas totales (Daytrips + Charters + Bar + Buceo)'), vals: series('ventas'), indent: 1, childrenOf: 'ing', editableKey: 'ventas' });
      h += row({ id: 'ret', label: tt('del.row.ret', 'Devoluciones en ventas'), vals: series('ret'), indent: 1, childrenOf: 'ing', editableKey: 'ret' });
      h += row({ id: 'direct', label: tt('del.row.direct', 'Total costos directos'), vals: series('direct'), total: true, kids: 'cos', editableKey: 'direct' });
      h += row({ id: 'cogs', label: tt('del.row.cogs', 'Costo de la mercancía vendida'), vals: series('cogs'), indent: 1, childrenOf: 'cos', editableKey: 'cogs' });
      h += row({ id: 'cos', label: tt('del.row.cos', 'Costo de los servicios vendidos'), vals: series('cos'), indent: 1, childrenOf: 'cos', editableKey: 'cos' });
      h += row({ id: 'gross', label: tt('del.row.gross', 'Utilidad bruta (departmental profit)'), vals: series('gross'), total: true, editableKey: 'gross' });
      h += row({ id: 'undist', label: tt('del.row.undist', 'Total gastos no distribuidos'), vals: series('undist'), total: true, kids: 'gast', editableKey: 'undist' });
      h += row({ id: 'temp', label: tt('del.row.temp', 'Personal temporal · nómina → 2ª quincena'), vals: series('temp'), indent: 1, childrenOf: 'gast', editableKey: 'temp' });
      h += row({ id: 'nom', label: tt('del.row.nom', 'Nómina administrativa fija · → 2ª quincena'), vals: series('nom'), indent: 1, childrenOf: 'gast', editableKey: 'nom' });
      h += row({ id: 'gen', label: tt('del.row.gen', 'Gastos generales'), vals: series('gen'), indent: 1, childrenOf: 'gast', editableKey: 'gen' });
      h += row({ id: 'svc', label: tt('del.row.svc', 'Servicios operacionales en venta'), vals: series('svc'), indent: 1, childrenOf: 'gast', editableKey: 'svc' });
      h += row({ id: 'gop', label: tt('del.row.gop', 'GOP — utilidad operativa bruta = EBITDA'), vals: gop, kind: 'gop', total: true, editableKey: 'gop' });
      h += row({ id: 'neta', label: tt('del.row.neta', 'Utilidad neta (causación)'), vals: neta, total: true, kids: 'nop', editableKey: 'neta' });
      h += row({ id: 'depr', label: tt('del.row.depr', 'Depreciación PPE'), vals: series('depr'), indent: 1, childrenOf: 'nop', editableKey: 'depr' });
      h += row({ id: 'fin', label: tt('del.row.fin', 'Gastos financieros (intereses)'), vals: series('fin'), indent: 1, childrenOf: 'nop', editableKey: 'fin' });
      h += row({ id: 'tax', label: tt('del.row.tax', 'Gastos por impuestos no acreditables'), vals: series('tax'), indent: 1, childrenOf: 'nop', editableKey: 'tax' });
    }

    h += sec('bs', tt('del.sec.bs', '3. Balance general (libros)'), n);
    if (open.bs) {
      h += row({ id: 'assets', label: tt('del.row.assets', 'Total activos'), vals: series('assets'), total: true, kids: 'act', editableKey: 'assets' });
      h += row({ id: 'liab', label: tt('del.row.liab', 'Total pasivos'), vals: series('liab'), total: true, kids: 'pas', editableKey: 'liab' });
      h += row({ id: 'equity', label: tt('del.row.equity', 'Total patrimonio'), vals: series('equity'), total: true, kids: 'pat', editableKey: 'equity' });
    }

    h += sec('sh', tt('del.sec.shadow', '4. Vista sombra — no se postea a libros'), n);
    if (open.sh) {
      h += row({ id: 'sA', label: tt('del.row.sA', '4A. Deuda real del velero — LIQUIDADA Feb-2026 (informativa)'), vals: cols.map(function () { return null; }), kind: 'shad', kids: 'sA' });
      if (child.sA) {
        h += row({ id: 'sA1', label: tt('del.row.sA1', 'Diferencia vs capital original USD ≈ −1.9% — stay in xlsx notes'), vals: cols.map(function () { return null; }), indent: 1, kind: 'shad', childrenOf: 'sA' });
      }
      h += row({ id: 'kcomp', label: tt('del.row.kcomp', '4B. Compensación Kevin — acumulado adeudado (Jul REAL 8.976.900)'), vals: series('kcomp'), kind: 'shad', kids: 'sB', editableKey: 'kcomp' });
      h += row({ id: 'sC', label: tt('del.row.sC', '4C. Distribución socios Kevin 46.081.000 / Nick 41.081.000 (estático)'), vals: cols.map(function () { return null; }), kind: 'shad', kids: 'sC' });
      h += row({ id: 'sD', label: tt('del.row.sD', '4D. Posición entre socios (Libro 1 empresa ≠ Libro 2 Nick)'), vals: cols.map(function () { return null; }), kind: 'shad' });
      h += row({ id: 'sE', label: tt('del.row.sE', '4E. Contingencias (OTA IVA, exposición IVA, laboral) — vigentes, no se proyectan'), vals: cols.map(function () { return null; }), kind: 'shad', kids: 'sE' });
    }

    h += '</tbody></table>';
    const wrap = rootEl.querySelector('#del-tree-wrap');
    if (!wrap) return;
    wrap.innerHTML = h;

    wrap.querySelectorAll('span.tog[data-sec]').forEach(function (el) {
      el.addEventListener('click', function (ev) {
        ev.preventDefault();
        const id = el.getAttribute('data-sec');
        open[id] = !open[id];
        render();
      });
    });
    wrap.querySelectorAll('span.tog[data-child]').forEach(function (el) {
      el.addEventListener('click', function (ev) {
        ev.preventDefault();
        const id = el.getAttribute('data-child');
        child[id] = !child[id];
        render();
      });
    });
    wrap.querySelectorAll('td.edit').forEach(function (td) {
      td.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); td.blur(); }
      });
      td.addEventListener('blur', function () {
        const raw = td.textContent.replace(/[.\s]/g, '').replace('−', '-').replace('—', '').replace('·', '');
        const k = td.dataset.k;
        const i = +td.dataset.i;
        if (!raw) { delete overrides[k + '|' + i]; render(); return; }
        const num = parseInt(raw, 10);
        if (Number.isFinite(num)) { overrides[k + '|' + i] = num; render(); }
      });
    });
  }

  function mountHtml() {
    return ''
      + '<div class="del-tree" id="del-tree">'
      +   '<div class="del-tabs">'
      +     '<button type="button" class="del-tab on" id="del-t-p">' + tt('del.tab.presente', 'Presente') + '</button>'
      +     '<button type="button" class="del-tab" id="del-t-m">' + tt('del.tab.modelado', 'Modelado') + '</button>'
      +     '<span class="stamp" id="del-modelo-stamp" hidden>' + tt('del.stamp.modelo', 'MODELO — no es cierre oficial') + '</span>'
      +   '</div>'
      +   '<div class="del-note" id="del-banner"></div>'
      +   '<div class="del-palancas" id="del-palancas">'
      +     '<label>' + tt('del.palanca.ventas', 'Ventas vs Jul') + ' <input id="del-p-ventas" type="range" min="50" max="150" value="100"> <span class="val" id="del-v-ventas">100%</span></label>'
      +     '<label>' + tt('del.palanca.nomina', 'Nómina vs Jul') + ' <input id="del-p-nom" type="range" min="50" max="150" value="100"> <span class="val" id="del-v-nom">100%</span></label>'
      +     '<label><input id="del-p-loan" type="checkbox"> ' + tt('del.palanca.loan', 'Aplazar préstamo (demo: sin salida de caja en proyección)') + '</label>'
      +     '<span class="pal-note">' + tt('del.palanca.demo', 'Palancas rellenan Ago–Dic 2026 como Jul × factor, en itálica / PROY. No se envían a Alegra. 2027 queda vacío.') + '</span>'
      +   '</div>'
      +   '<div class="del-tree-wrap" id="del-tree-wrap"></div>'
      + '</div>';
  }

  window.initEntregablesTree = function (slot) {
    rootEl = slot;
    slot.innerHTML = mountHtml();
    slot.querySelector('#del-t-p').addEventListener('click', function () { tab = 'presente'; render(); });
    slot.querySelector('#del-t-m').addEventListener('click', function () { tab = 'modelado'; render(); });
    ['del-p-ventas', 'del-p-nom', 'del-p-loan'].forEach(function (id) {
      const el = slot.querySelector('#' + id);
      if (!el) return;
      el.addEventListener(el.type === 'checkbox' ? 'change' : 'input', render);
    });
    render();
  };
})();
