'use strict';
/* SpeicherPilot – Oberfläche */

const TOKEN = window.SP_TOKEN;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ------------------------------------------------------------------ Icons */
const ICONS = {
  home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
  sparkles: '<path d="M12 3l1.8 4.7 4.7 1.8-4.7 1.8L12 16l-1.8-4.7-4.7-1.8 4.7-1.8z"/><path d="M19 15l.8 2.2 2.2.8-2.2.8L19 21l-.8-2.2-2.2-.8 2.2-.8z"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  flame: '<path d="M12 3c1 3.5 5 5.5 5 10a5 5 0 0 1-10 0c0-2 1-3.5 2-4.5 0 2 1 3 2 3 0-3-1-5 1-8.5z"/>',
  map: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 12h9M12 3v18M12 16h9"/>',
  trash: '<path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  open: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v1"/><path d="M3 7v10a2 2 0 0 0 2 2h12.5a1.5 1.5 0 0 0 1.4-1l2.4-7A1 1 0 0 0 20.4 10H8.6a2 2 0 0 0-1.9 1.4L4.5 19"/>',
  file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>',
  doc: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
  video: '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="m16 10 5-3v10l-5-3z"/>',
  archive: '<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9M10 13h4"/>',
  disc: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/>',
  game: '<rect x="2" y="7" width="20" height="11" rx="5"/><path d="M7 11v3M5.5 12.5h3M15.5 12h.01M18 14h.01"/>',
  code: '<path d="m8 8-5 4 5 4M16 8l5 4-5 4M14 5l-4 14"/>',
  cpu: '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
  cloud: '<path d="M7 18a4.5 4.5 0 0 1-.5-9 6 6 0 0 1 11.5 1.5A3.75 3.75 0 0 1 17.5 18z"/>',
  download: '<path d="M12 3v12M7 10l5 5 5-5M4 19h16"/>',
  shield: '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/>',
  alert: '<path d="M10.3 4.2 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 4.2a2 2 0 0 0-3.4 0z"/><path d="M12 10v4M12 17h.01"/>',
  check: '<path d="m5 12 5 5 9-10"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
  refresh: '<path d="M20 11a8 8 0 0 0-14.8-4M4 4v4h4M4 13a8 8 0 0 0 14.8 4M20 20v-4h-4"/>',
  play: '<path d="M7 4v16l13-8z"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="2"/>',
  hdd: '<rect x="2" y="12" width="20" height="8" rx="2"/><path d="M5 12 7.5 5h9L19 12M6 16h.01M10 16h.01"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
  box: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
  package: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8M7.5 5.5l9 5"/>',
  image: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/>',
  music: '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  chev: '<path d="m9 6 6 6-6 6"/>',
  up: '<path d="m6 15 6-6 6 6"/>',
  zap: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
  monitor: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
};
const icon = (n, cls = '') => `<svg class="i ${cls}" viewBox="0 0 24 24">${ICONS[n] || ICONS.folder}</svg>`;

/* ------------------------------------------------------------------ Formatierung */
const nf = (d) => new Intl.NumberFormat('de-DE', { maximumFractionDigits: d, minimumFractionDigits: 0 });
function fmtBytes(b) {
  if (!b || b < 0) return '0 B';
  const u = ['B', 'KB', 'MB', 'GB', 'TB'];
  let i = 0;
  while (b >= 1024 && i < u.length - 1) { b /= 1024; i++; }
  const d = i >= 3 ? (b < 10 ? 2 : b < 100 ? 1 : 0) : 0;
  return `${nf(d).format(b)} ${u[i]}`;
}
const fmtNum = (n) => nf(0).format(n || 0);
function ago(days) {
  if (days == null || days > 50000) return 'unbekannt';
  if (days < 1 / 24) return 'gerade eben';
  if (days < 1) return `vor ${Math.floor(days * 24)} Std.`;
  if (days < 2) return 'gestern';
  if (days < 30) return `vor ${Math.floor(days)} Tagen`;
  if (days < 60) return 'vor 1 Monat';
  if (days < 365) return `vor ${Math.max(2, Math.floor(days / 30.4))} Monaten`;
  const y = days / 365;
  if (y < 2) { const m = Math.floor((days - 365) / 30.4); return m >= 2 ? `vor 1 Jahr, ${m} Mon.` : 'vor über 1 Jahr'; }
  return `vor ${Math.floor(y)} Jahren`;
}
const daysSince = (ts) => (ts ? (Date.now() / 1000 - ts) / 86400 : 99999);
const ageClass = (d) => (d > 730 ? 'veryold' : d > 365 ? 'old' : '');

/* ------------------------------------------------------------------ API */
async function api(path, body) {
  const opts = { headers: { 'X-Token': TOKEN } };
  if (body !== undefined) {
    opts.method = 'POST';
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const r = await fetch(path, opts);
  let j;
  try { j = await r.json(); } catch { j = { error: 'Ungültige Antwort vom Dienst' }; }
  if (!r.ok || (j && j.error)) throw new Error((j && j.error) || r.statusText);
  return j;
}

/* ------------------------------------------------------------------ Zustand */
const S = {
  info: null, drives: [], recycle: { size: 0, items: 0 },
  scan: { state: 'idle' }, scope: new Set(), custom: [],
  junk: null, junkSel: new Set(), junkTouched: false, junkKeep: {}, uKeep: {},
  unused: [], unusedTotal: 0, uSel: new Map(),
  uOpt: { days: 180, min: 100, basis: 'modified', hideKeep: true, level: 'all', q: '' },
  large: [], lSel: new Map(), lOpt: { min: 500, kind: 'all' },
  tree: null, view: 'overview', sessionFreed: 0, loaded: false,
  games: null, gSel: new Map(), gSort: 'size',
};
const LEVEL_LABEL = { safe: 'Sicher löschbar', likely: 'Empfohlen', review: 'Bitte prüfen', uninstall: 'Deinstallieren', keep: 'Behalten' };
const LEVEL_COLOR = { safe: 'var(--safe)', likely: 'var(--likely)', review: 'var(--review)', uninstall: 'var(--uninstall)', keep: 'var(--keep)' };
const pill = (lv) => `<span class="pill lv-${lv}">${LEVEL_LABEL[lv] || lv}</span>`;
const SEL = (src) => ({ unused: S.uSel, large: S.lSel, games: S.gSel })[src] || S.uSel;
const LIST = (src) => ({ unused: S.unused, large: S.large, games: S.games?.leftovers || [] })[src] || [];
const isFolderSrc = (src) => src === 'unused' || src === 'games';
const findFolder = (path) => S.unused.find((u) => u.path === path) || S.games?.leftovers.find((u) => u.path === path);

/* ------------------------------------------------------------------ Navigation */
const VIEWS = [
  { id: 'overview', label: 'Übersicht', icon: 'home' },
  { id: 'junk', label: 'Schnellreinigung', icon: 'sparkles' },
  { id: 'unused', label: 'Lange nicht benutzt', icon: 'clock' },
  { id: 'large', label: 'Riesige Dateien', icon: 'flame' },
  { id: 'games', label: 'Spiele', icon: 'game' },
  { id: 'map', label: 'Speicherkarte', icon: 'map' },
];
function renderNav() {
  const junkSize = junkSelectedSize(true);
  const rec = S.unused.filter((u) => ['safe', 'likely'].includes(u.info.level)).length;
  const huge = S.large.filter((f) => f.size >= 5 * 2 ** 30).length;
  const badges = {
    junk: S.junk ? `<span class="badge good">${fmtBytes(junkSize)}</span>` : '',
    unused: S.unused.length ? `<span class="badge">${rec || S.unused.length}</span>` : '',
    games: S.games?.leftovers?.length ? `<span class="badge good" title="Überreste deinstallierter Spiele">${fmtBytes(S.games.leftovers.reduce((a, b) => a + b.size, 0))}</span>`
      : S.games?.installed?.length ? `<span class="badge">${S.games.installed.length}</span>` : '',
    large: S.large.length ? `<span class="badge ${huge ? 'hot' : ''}">${huge || S.large.length}</span>` : '',
  };
  $('#nav').innerHTML = VIEWS.map((v) => `
    <button class="nav-item ${S.view === v.id ? 'active' : ''}" data-act="nav" data-view="${v.id}">
      ${icon(v.icon)}<span class="lbl">${v.label}</span>${badges[v.id] || ''}
    </button>`).join('');
}
function go(view) {
  S.view = view;
  $$('.view').forEach((v) => v.classList.toggle('active', v.id === `view-${view}`));
  renderNav();
  renderView(view);
  $('#main').scrollTop = 0;
  hideTooltip();
}
function renderView(v = S.view) {
  ({ overview: renderOverview, junk: renderJunk, unused: renderUnused, large: renderLarge, games: renderGames, map: renderMap })[v]();
  renderActionbar();
}

/* ------------------------------------------------------------------ Sidebar unten */
function renderBin() {
  const b = S.recycle;
  $('#binCard').innerHTML = `
    <div class="ricon" style="width:36px;height:36px">${icon('trash')}</div>
    <div class="t"><b>Papierkorb</b><span>${b.items ? `${fmtBytes(b.size)} · ${fmtNum(b.items)} Elemente` : 'leer'}</span></div>
    ${b.items ? `<button class="btn sm ghost" data-act="bin-view">Ansehen</button>` : ''}`;
}
let freedShown = 0;
function setSessionFreed(v) {
  const el = $('#sessionFreed');
  const from = freedShown, to = v, t0 = performance.now();
  freedShown = v;
  const step = (t) => {
    const k = Math.min(1, (t - t0) / 1200), e = 1 - Math.pow(1 - k, 3);
    el.textContent = fmtBytes(from + (to - from) * e);
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ------------------------------------------------------------------ Übersicht */
function driveCard(d, i) {
  const pct = d.total ? d.used / d.total : 0;
  const C = 2 * Math.PI * 52;
  const col = pct > 0.9 ? ['#f43f5e', '#f97316'] : pct > 0.75 ? ['#f59e0b', '#f97316'] : ['#8b5cf6', '#22d3ee'];
  return `
  <div class="card drive">
    <div class="ring">
      <svg viewBox="0 0 128 128">
        <defs><linearGradient id="rg${i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${col[0]}"/><stop offset="1" stop-color="${col[1]}"/></linearGradient></defs>
        <circle class="track" cx="64" cy="64" r="52" stroke-width="12" fill="none"/>
        <circle class="val" cx="64" cy="64" r="52" stroke-width="12" fill="none" stroke="url(#rg${i})" stroke-linecap="round"
          stroke-dasharray="${C}" stroke-dashoffset="${C}" data-target="${C * (1 - pct)}"/>
      </svg>
      <div class="center"><div class="pct">${Math.round(pct * 100)}<small>%</small></div><div class="lbl">belegt</div></div>
    </div>
    <div class="drive-info">
      <div class="drive-name">${icon('hdd')} ${esc(d.letter)}:${d.system ? ' <span class="tag">System</span>' : ''}${d.type === 'removable' ? ' <span class="tag">Wechseldatenträger</span>' : ''}</div>
      <div class="drive-label">${esc(d.label)} · ${esc(d.fs)}</div>
      <div class="drive-stats">
        <div class="stat-mini"><div class="k">Frei</div><div class="v">${fmtBytes(d.free)}</div></div>
        <div class="stat-mini"><div class="k">Gesamt</div><div class="v">${fmtBytes(d.total)}</div></div>
      </div>
      ${pct > 0.9 ? `<div class="warnline">${icon('alert')} Fast voll – Windows wird langsamer.</div>` : ''}
    </div>
  </div>`;
}

function potential() {
  const junk = junkSelectedSize(true);
  const unusedRec = S.unused.filter((u) => ['safe', 'likely'].includes(u.info.level) && !u.info.protect);
  const uSize = unusedRec.reduce((a, b) => a + b.size, 0);
  const lc = (p) => p.toLowerCase();
  const largeRec = S.large.filter((f) => ['safe', 'likely'].includes(f.info.level) && !f.info.protect
    && !unusedRec.some((u) => lc(f.path).startsWith(lc(u.path) + '\\')));
  const lSize = largeRec.reduce((a, b) => a + b.size, 0);
  const bin = S.recycle.size || 0;
  const gameRec = (S.games?.leftovers || []).filter((g) => !unusedRec.some((u) => u.path === g.path || lc(g.path).startsWith(lc(u.path) + '\\')));
  const gSize = gameRec.reduce((a, b) => a + folderSize(b), 0);
  return { junk, uSize, lSize, bin, gSize, total: junk + uSize + lSize + bin + gSize, unusedRec, largeRec };
}

function scopeChips() {
  const chips = S.drives.filter((d) => d.type === 'fixed').map((d) => ({ root: d.root, label: `${d.letter}: ${d.label}`, ic: 'hdd' }));
  if (S.info) chips.push({ root: S.info.home, label: 'Nur Benutzerordner', ic: 'user' });
  S.custom.forEach((c) => chips.push({ root: c, label: c.split('\\').filter(Boolean).pop() || c, ic: 'folder', custom: true }));
  return `<div class="chips">${chips.map((c) => `
    <button class="chip ${S.scope.has(c.root) ? 'on' : ''}" data-act="scope" data-root="${esc(c.root)}" title="${esc(c.root)}">
      ${icon(c.ic)} ${esc(c.label)}${c.custom ? `<span class="x" data-act="scope-remove" data-root="${esc(c.root)}">${icon('x')}</span>` : ''}
    </button>`).join('')}
    <button class="chip" data-act="pick-folder">${icon('plus')} Ordner wählen …</button></div>`;
}

function scanCard() {
  const st = S.scan;
  if (st.state === 'scanning') {
    return `
    <div class="card scan-card" id="scanCard">
      <div class="card-head"><div><h2>${icon('search')} Analyse läuft …</h2><div class="card-sub">Du kannst währenddessen schon die Schnellreinigung nutzen.</div></div>
        <button class="btn ghost" data-act="scan-cancel">${icon('stop')} Abbrechen</button></div>
      <div class="scan-live">
        <div class="radar"></div>
        <div class="scan-stats">
          <div><div class="v" id="sFiles">0</div><div class="k">Dateien</div></div>
          <div><div class="v" id="sDirs">0</div><div class="k">Ordner</div></div>
          <div><div class="v" id="sBytes">0 B</div><div class="k">erfasst</div></div>
        </div>
      </div>
      <div class="progress ${st.expected ? '' : 'indet'}" id="sProg"><i style="width:0%"></i></div>
      <div class="current-path" id="sPath">…</div>
    </div>`;
  }
  const done = st.state === 'done';
  return `
  <div class="card scan-card" id="scanCard">
    <div class="card-head"><div>
      <h2>${icon('search')} ${done ? 'Analyse abgeschlossen' : 'Speicher analysieren'}</h2>
      <div class="card-sub">${done
        ? `${fmtNum(st.files)} Dateien in ${nf(0).format(st.elapsed)} s untersucht · ${fmtBytes(st.bytes)} erfasst`
        : 'Findet ungenutzte Ordner, riesige Dateien und erklärt dir, was du gefahrlos löschen kannst.'}</div>
    </div></div>
    <div class="scan-scope">${scopeChips()}</div>
    <div class="scan-cta">
      <button class="btn primary big" data-act="scan-start" ${S.scope.size ? '' : 'disabled'}>${icon(done ? 'refresh' : 'play')} ${done ? 'Neu analysieren' : 'Analyse starten'}</button>
      <span class="hint">${icon('shield')} Es wird nur gelesen – gelöscht wird nichts ohne deine Bestätigung.</span>
    </div>
  </div>`;
}

function renderOverview() {
  const el = $('#view-overview');
  const p = potential();
  const scanned = S.scan.state === 'done';
  const user = S.info?.user ? `, ${esc(S.info.user)}` : '';
  const recs = [
    ...p.unusedRec.map((u) => ({ ...u, src: 'unused' })),
    ...p.largeRec.map((f) => ({ ...f, src: 'large' })),
  ].sort((a, b) => b.size - a.size).slice(0, 6);
  const giants = S.large.slice(0, 4);
  const segs = [
    { k: 'Schnellreinigung', v: p.junk, c: 'linear-gradient(90deg,#34d399,#2dd4bf)', view: 'junk' },
    { k: 'Lange nicht benutzt', v: p.uSize, c: 'linear-gradient(90deg,#8b5cf6,#6366f1)', view: 'unused' },
    { k: 'Riesige Dateien', v: p.lSize, c: 'linear-gradient(90deg,#f97316,#f43f5e)', view: 'large' },
    { k: 'Überreste deinstallierter Spiele', v: p.gSize, c: 'linear-gradient(90deg,#a855f7,#d946ef)', view: 'games' },
    { k: 'Papierkorb', v: p.bin, c: 'linear-gradient(90deg,#94a3b8,#64748b)', view: 'junk' },
  ];
  el.innerHTML = `
    <div class="page-head">
      <div><h1>Hallo${user}! <span class="grad-text">Lass uns Platz schaffen.</span></h1>
      <div class="sub">Hier siehst du auf einen Blick, wie voll deine Laufwerke sind und wie viel du freiräumen kannst.</div></div>
    </div>
    ${adminBanner()}
    <div class="grid drives">${S.drives.map(driveCard).join('')}</div>
    <div class="grid two">
      ${scanCard()}
      <div class="card potential">
        <h2>${icon('sparkles')} Freiräumbar</h2>
        <div class="big grad-text" id="potBig">${fmtBytes(p.total)}</div>
        <div class="card-sub">${scanned ? 'Empfehlungen aus Analyse, Schnellreinigung und Papierkorb' : 'Bisher nur Schnellreinigung & Papierkorb – starte die Analyse für mehr.'}</div>
        <div class="stack">${segs.map((s) => `<i style="width:${p.total ? (s.v / p.total) * 100 : 0}%;background:${s.c}"></i>`).join('')}</div>
        <div class="legend">${segs.map((s) => `
          <button data-act="nav" data-view="${s.view}"><span class="dot" style="background:${s.c}"></span><span class="n">${s.k}</span><span class="v">${fmtBytes(s.v)}</span>${icon('chev')}</button>`).join('')}
        </div>
      </div>
    </div>
    ${scanned && recs.length ? `
    <div class="grid two">
      <div class="card">
        <div class="card-head"><div><h2>${icon('check')} Top-Empfehlungen</h2><div class="card-sub">Die größten Brocken, die du sehr wahrscheinlich nicht mehr brauchst.</div></div></div>
        <div class="recs">${recs.map((r) => `
          <div class="rec">
            <div class="ricon" style="color:${LEVEL_COLOR[r.info.level]}">${icon(r.info.icon)}</div>
            <div style="min-width:0"><div class="n">${esc(r.name)}</div><div class="d">${esc(r.info.title)} · geändert ${ago(r.age)}</div></div>
            <div class="sz">${fmtBytes(r.size)}</div>
            <button class="btn sm ghost" data-act="nav" data-view="${r.src}">Ansehen ${icon('chev')}</button>
          </div>`).join('')}</div>
      </div>
      <div class="card">
        <div class="card-head"><div><h2>${icon('flame')} Größte Einzeldateien</h2><div class="card-sub">Diese Dateien fallen besonders ins Gewicht.</div></div>
          <button class="btn sm ghost" data-act="nav" data-view="large">Alle ${icon('chev')}</button></div>
        <div class="giants">${giants.map((g) => `
          <div class="giant" title="${esc(g.path)}"><div class="gs">${fmtBytes(g.size)}</div><div class="gn">${esc(g.name)}</div><div class="gk">${esc(g.info.title)}</div></div>`).join('')}</div>
      </div>
    </div>` : ''}
  `;
  requestAnimationFrame(() => setTimeout(() => $$('.ring .val', el).forEach((c) => c.setAttribute('stroke-dashoffset', c.dataset.target)), 60));
  if (S.scan.state === 'scanning') updateScanProgress();
}

function adminBanner() {
  if (!S.info || S.info.admin) return '';
  const needs = S.junk?.categories?.filter((c) => c.needsAdmin) || [];
  if (!needs.length) return '';
  return `<div class="banner">${icon('zap')}
    <div class="t"><b>Ein paar Bereiche brauchen Administratorrechte</b>
    <span>${needs.map((n) => esc(n.name)).join(', ')} – starte SpeicherPilot als Administrator, um auch diese zu bereinigen.</span></div>
    <button class="btn" data-act="elevate">${icon('shield')} Als Administrator neu starten</button></div>`;
}

/* ------------------------------------------------------------------ Scan */
let pollTimer = null;
async function startScan() {
  try {
    const r = await api('/api/scan', { roots: [...S.scope] });
    if (!r.ok) return toast('err', 'Analyse nicht gestartet', r.error);
    S.scan = { state: 'scanning', expected: 0 };
    renderOverview();
    pollScan();
  } catch (e) { toast('err', 'Fehler', e.message); }
}
function pollScan() {
  clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    try {
      const st = await api('/api/status');
      const was = S.scan.state;
      S.scan = st;
      if (st.state === 'scanning') { if (S.view === 'overview') updateScanProgress(); return; }
      clearInterval(pollTimer);
      if (st.state === 'done') {
        await loadResults();
        toast('ok', 'Analyse abgeschlossen', `${fmtNum(st.files)} Dateien · ${fmtBytes(st.bytes)} untersucht`);
      } else if (was === 'scanning') {
        toast('info', 'Analyse abgebrochen', st.error || '');
      }
      renderView();
      renderNav();
    } catch (e) { /* nächster Versuch */ }
  }, 450);
}
function updateScanProgress() {
  const st = S.scan;
  if (!$('#sFiles')) return;
  $('#sFiles').textContent = fmtNum(st.files);
  $('#sDirs').textContent = fmtNum(st.dirs);
  $('#sBytes').textContent = fmtBytes(st.bytes);
  $('#sPath').textContent = st.current || '…';
  const prog = $('#sProg');
  if (st.expected) {
    prog.classList.remove('indet');
    prog.firstElementChild.style.width = `${Math.min(97, (st.bytes / st.expected) * 100)}%`;
  }
}
async function loadResults() {
  await Promise.all([loadUnused(), loadLarge(), refreshDrives(), loadGames()]);
  S.tree = null;
}
async function loadUnused() {
  const o = S.uOpt;
  const r = await api(`/api/unused?days=${o.days}&min=${o.min}&basis=${o.basis}`);
  S.unused = r.items; S.unusedTotal = r.total;
  const keep = new Set(S.unused.map((u) => u.path));
  [...S.uSel.keys()].forEach((k) => { if (!keep.has(k)) S.uSel.delete(k); });
}
async function loadLarge() {
  const r = await api(`/api/large?min=100`);
  S.large = r.items;
}
async function refreshDrives() {
  const r = await api('/api/drives');
  S.drives = r.drives; S.recycle = r.recycleBin;
  renderBin();
}

/* ------------------------------------------------------------------ Schnellreinigung */
const mapSum = (m) => (m ? [...m.values()].reduce((a, b) => a + b, 0) : 0);
const junkSize = (c) => Math.max(0, c.size - mapSum(S.junkKeep[c.id]));
const folderSize = (it) => Math.max(0, it.size - mapSum(S.uKeep[it.path]));
function junkSelectedSize(defaults = false) {
  if (!S.junk) return 0;
  return S.junk.categories.filter((c) => (defaults && !S.junkTouched ? c.default : S.junkSel.has(c.id)) && c.id !== 'recyclebin')
    .reduce((a, c) => a + junkSize(c), 0);
}
async function loadJunk() {
  try {
    const j = await api('/api/junk');
    const first = !S.junk;
    S.junk = j;
    if (first && !S.junkTouched) j.categories.forEach((c) => c.default && S.junkSel.add(c.id));
    if (j.measuring || j.categories.some((c) => !c.measured)) setTimeout(loadJunk, 900);
    renderNav();
    if (S.view === 'junk' || S.view === 'overview') renderView();
  } catch (e) { setTimeout(loadJunk, 2000); }
}
function renderJunk() {
  const el = $('#view-junk');
  const j = S.junk;
  const cards = (j?.categories || []).map((c) => {
    const on = S.junkSel.has(c.id);
    const eff = junkSize(c);
    const kept = S.junkKeep[c.id]?.size || 0;
    const size = c.measured ? `<div class="jsize ${eff ? '' : 'zero'}">${eff ? fmtBytes(eff) : kept ? 'Alles behalten' : 'Sauber ✓'}</div>` : '<div class="skeleton"></div>';
    return `
      <div class="card jcard ${on ? 'on' : ''}" data-act="junk-toggle" data-id="${c.id}">
        <div class="jtop"><div class="bubble">${icon(c.icon)}</div>
          <label class="check" onclick="event.preventDefault()"><input type="checkbox" ${on ? 'checked' : ''}><span></span></label></div>
        <div class="jname">${esc(c.name)}</div>
        ${size}
        <div class="jtext">${esc(c.text)}</div>
        <div class="jfoot">${pill(c.level)}
          ${c.files ? `<span class="tag">${fmtNum(c.files)} ${c.id === 'recyclebin' ? 'Elemente' : 'Dateien'}</span>` : ''}
          ${c.method === 'recycle' ? '<span class="tag">→ Papierkorb</span>' : ''}
          ${c.id === 'recyclebin' ? '<span class="tag warn">endgültig</span>' : ''}
          ${c.needsAdmin ? `<span class="tag warn">${icon('zap')} Admin nötig</span>` : ''}
          ${kept ? `<span class="tag keep">${icon('shield')} ${kept} behalten</span>` : ''}</div>
        ${c.measured && (c.files || kept) ? `<button class="btn sm details-btn" data-act="junk-details" data-id="${c.id}">${icon('search')} Inhalt ansehen &amp; auswählen</button>` : ''}
      </div>`;
  }).join('');
  const extras = (j?.extras || []).map((x) => `
    <div class="card extra"><div class="ricon">${icon('info')}</div>
      <div style="flex:1"><div class="rtitle"><b>${esc(x.name)}</b><span class="tag">${fmtBytes(x.size)}</span></div>
      <div class="rtext">${esc(x.text)}</div>
      ${x.action ? `<button class="btn sm" style="margin-top:10px" data-act="action" data-target="${x.action}">${icon('settings')} Einstellungen öffnen</button>` : ''}</div>
    </div>`).join('');
  el.innerHTML = `
    <div class="page-head">
      <div><h1>Schnellreinigung</h1><div class="sub">Digitaler Staub, den Programme und Windows automatisch neu erzeugen. Sichere Kategorien sind vorausgewählt – ein Klick und weg.</div></div>
      <button class="btn ghost" data-act="junk-measure" ${j?.measuring ? 'disabled' : ''}>${icon('refresh')} Neu messen</button>
    </div>
    ${adminBanner()}
    <div class="jgrid">${cards}</div>
    ${extras ? `<h2 style="margin:28px 0 4px;font-size:18px">Weitere Tipps</h2><div class="card-sub" style="color:var(--muted)">Diese Brocken lassen sich nur über Windows selbst entfernen.</div><div class="extras">${extras}</div>` : ''}
  `;
}
async function cleanJunk(onlyIds) {
  const ids = Array.isArray(onlyIds) ? onlyIds : [...S.junkSel];
  const cats = S.junk.categories.filter((c) => ids.includes(c.id));
  const total = cats.reduce((a, c) => a + junkSize(c), 0);
  const binSel = ids.includes('recyclebin');
  const keptTotal = cats.reduce((a, c) => a + (S.junkKeep[c.id]?.size || 0), 0);
  const ok = await modal({
    title: `${cats.length === 1 ? `„${cats[0].name}“` : `${cats.length} Kategorien`} bereinigen?`,
    sub: `Bis zu ${fmtBytes(total)} werden freigegeben. Dateien, die gerade benutzt werden, überspringt SpeicherPilot automatisch.${keptTotal ? ` ${keptTotal} von dir ausgewählte Einträge bleiben erhalten.` : ''}`,
    list: cats.map((c) => [c.name + (S.junkKeep[c.id]?.size ? ` (${S.junkKeep[c.id].size} behalten)` : ''), fmtBytes(junkSize(c))]),
    warn: binSel ? 'Die Papierkorb-Einträge werden endgültig gelöscht – das lässt sich nicht rückgängig machen.' : null,
    confirm: 'Jetzt bereinigen', danger: binSel,
  });
  if (!ok) return;
  const btn = $('#abBtn') || $('#dRun');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Bereinige …'; }
  const exclude = {};
  ids.forEach((id) => { if (S.junkKeep[id]?.size) exclude[id] = [...S.junkKeep[id].keys()]; });
  try {
    const r = await api('/api/junk/clean', { ids, exclude });
    S.junk = r.junk;
    S.sessionFreed = r.sessionFreed;
    setSessionFreed(r.sessionFreed);
    const skipped = r.results.reduce((a, x) => a + (x.skipped || 0), 0);
    toast('ok', `${fmtBytes(r.freed)} freigegeben`, skipped ? `${fmtNum(skipped)} Dateien waren in Benutzung und wurden übersprungen.` : 'Alles erledigt.');
    if (r.freed > 0) burst(btn);
    closeDrawer();
    ids.forEach((id) => S.junkSel.delete(id));
    S.junkTouched = true;
    await refreshDrives();
  } catch (e) { toast('err', 'Bereinigung fehlgeschlagen', e.message); }
  renderView(); renderNav();
}

/* ------------------------------------------------------------------ Ungenutzte Ordner */
function needScan(title, text, ic) {
  if (S.scan.state === 'scanning') {
    return `<div class="empty"><div class="ill">${icon('search')}</div><h2>Analyse läuft …</h2><p>Sobald sie fertig ist, erscheinen hier die Ergebnisse.</p>
      <button class="btn" data-act="nav" data-view="overview">Fortschritt ansehen</button></div>`;
  }
  return `<div class="empty"><div class="ill">${icon(ic)}</div><h2>${title}</h2><p>${text}</p>
    <button class="btn primary big" data-act="nav" data-view="overview">${icon('play')} Zur Analyse</button></div>`;
}
function filteredUnused() {
  const o = S.uOpt, q = o.q.trim().toLowerCase();
  return S.unused.filter((u) => {
    if (o.hideKeep && u.info.level === 'keep') return false;
    if (o.level !== 'all' && u.info.level !== o.level) return false;
    if (q && !(u.path.toLowerCase().includes(q) || u.info.title.toLowerCase().includes(q))) return false;
    return true;
  });
}
function seg(act, cur, opts) {
  return `<div class="seg">${opts.map(([v, l]) => `<button class="${String(cur) === String(v) ? 'on' : ''}" data-act="${act}" data-v="${v}">${l}</button>`).join('')}</div>`;
}
function itemActions(it, src) {
  const a = [];
  if (it.info.action === 'apps') a.push(`<button class="btn sm" data-act="action" data-target="apps" title="Einstellungen › Apps öffnen">${icon('settings')} Apps</button>`);
  if (it.info.action === 'steam') a.push(`<button class="btn sm" data-act="action" data-target="steam" title="Steam-Bibliothek öffnen">${icon('game')} Steam</button>`);
  if (it.info.action === 'steam-uninstall') a.push(`<button class="btn sm" data-act="action" data-target="steam-uninstall" data-appid="${esc(it.info.appid)}" title="Öffnet den Deinstallieren-Dialog von Steam">${icon('game')} In Steam deinstallieren</button>`);
  if (it.info.action === 'storage') a.push(`<button class="btn sm" data-act="action" data-target="storage">${icon('settings')} Speicher</button>`);
  if (isFolderSrc(src) && !it.info.protect) a.push(`<button class="btn sm" data-act="folder-details" data-path="${esc(it.path)}" title="Inhalt ansehen und einzelne Einträge behalten">${icon('search')} Inhalt</button>`);
  a.push(`<button class="btn sm icon-btn ghost" data-act="open" data-path="${esc(it.path)}" title="Im Explorer zeigen">${icon('open')}</button>`);
  a.push(`<button class="btn sm icon-btn ghost" data-act="del-one" data-src="${src}" data-path="${esc(it.path)}" ${it.info.protect ? `disabled title="${esc(it.info.protect)}"` : 'title="Löschen"'}>${icon('trash')}</button>`);
  return a.join('');
}
function rowHTML(it, src, max, extraClass = '', badge = '') {
  const sel = SEL(src).has(it.path);
  const lv = it.info.level;
  const ageTxt = `zuletzt geändert ${ago(it.age)}`;
  return `
  <div class="row ${sel ? 'sel' : ''} ${extraClass}" data-path="${esc(it.path)}">
    <span class="lvl-bar" style="background:${LEVEL_COLOR[lv]}"></span>
    <label class="check"><input type="checkbox" data-chk="${src}" data-path="${esc(it.path)}" ${sel ? 'checked' : ''} ${it.info.protect ? 'disabled' : ''}><span></span></label>
    <div class="ricon" style="color:${LEVEL_COLOR[lv]}">${icon(it.info.icon)}</div>
    <div class="rmain">
      <div class="rtitle"><span class="name" title="${esc(it.name)}">${esc(it.name)}</span>${badge}${pill(lv)}<span class="tag">${esc(it.info.title)}</span>${isFolderSrc(src) && S.uKeep[it.path]?.size ? `<span class="tag keep">${icon('shield')} ${S.uKeep[it.path].size} behalten</span>` : ''}</div>
      <div class="rpath" title="${esc(it.path)}">${esc(it.path)}</div>
      <div class="rtext">${esc(it.info.text)}${it.info.protect ? ` <b>Löschen hier gesperrt:</b> ${esc(it.info.protect)}.` : ''}</div>
      ${it.contents?.length ? `<div class="contents"><span>Enthält vor allem:</span>${it.contents.map((c) => `<span class="cchip">${esc(c.label)} <b>${c.pct} %</b></span>`).join('')}${it.files ? `<span class="cnum">${fmtNum(it.files)} Dateien</span>` : ''}</div>` : ''}
    </div>
    <div class="rmeta">
      <div class="rsize">${fmtBytes(isFolderSrc(src) ? folderSize(it) : it.size)}</div>
      ${isFolderSrc(src) && S.uKeep[it.path]?.size ? `<div class="rage">von ${fmtBytes(it.size)}</div>` : ''}
      <div class="sizebar"><i style="width:${Math.max(2, (it.size / max) * 100)}%"></i></div>
      <div class="rage ${ageClass(it.age)}">${icon('clock')} ${ageTxt}</div>
    </div>
    <div class="ractions">${itemActions(it, src)}</div>
  </div>`;
}
function renderUnused() {
  const el = $('#view-unused');
  const head = `<div class="page-head"><div><h1>Lange nicht benutzt</h1>
    <div class="sub">Ordner, die du seit Langem weder geöffnet noch verändert hast – jeweils mit Erklärung, was drin steckt, und einer Empfehlung.</div></div></div>`;
  if (S.scan.state !== 'done') { el.innerHTML = head + needScan('Noch keine Analyse', 'Starte zuerst eine Analyse deiner Laufwerke. Danach siehst du hier alle Ordner, die du lange nicht benutzt hast.', 'clock'); return; }
  const o = S.uOpt;
  const items = filteredUnused();
  const max = Math.max(1, ...items.map((i) => i.size));
  const total = items.reduce((a, b) => a + b.size, 0);
  const rec = items.filter((i) => ['safe', 'likely'].includes(i.info.level) && !i.info.protect);
  const recSize = rec.reduce((a, b) => a + b.size, 0);
  el.innerHTML = head + `
    <div class="filters">
      <span class="lab">Nicht benutzt seit</span>${seg('u-days', o.days, [[90, '3 Monaten'], [180, '6 Monaten'], [365, '1 Jahr'], [730, '2 Jahren']])}
      <span class="lab">ab</span>${seg('u-min', o.min, [[50, '50 MB'], [100, '100 MB'], [500, '500 MB'], [1024, '1 GB']])}
    </div>
    <div class="filters">
      <div class="chips">${[['all', 'Alle'], ['safe', 'Sicher löschbar'], ['likely', 'Empfohlen'], ['review', 'Bitte prüfen'], ['uninstall', 'Deinstallieren'], ['keep', 'Behalten']]
        .map(([v, l]) => `<button class="chip ${o.level === v ? 'on' : ''}" data-act="u-level" data-v="${v}">${v !== 'all' ? `<span class="pill lv-${v}" style="padding:0;border:0;background:none"></span>` : ''}${l}</button>`).join('')}</div>
      <div class="search">${icon('search')}<input id="uSearch" placeholder="Suchen …" value="${esc(o.q)}"></div>
      <label class="toggle"><input type="checkbox" data-opt="hideKeep" ${o.hideKeep ? 'checked' : ''}><span class="sw"></span>„Behalten“ ausblenden</label>
      <label class="toggle" title="Windows aktualisiert die Zugriffszeit oft auch durch Virenscanner oder Suche – daher zählt standardmäßig nur das Änderungsdatum. Eingeschaltet ist die Liste vorsichtiger, aber oft fast leer."><input type="checkbox" data-opt="basis" ${o.basis === 'used' ? 'checked' : ''}><span class="sw"></span>Auch Zugriffe berücksichtigen</label>
    </div>
    <div class="summary">
      <div class="s"><b>${fmtNum(items.length)}</b><span>Ordner</span></div><div class="sep"></div>
      <div class="s"><b>${fmtBytes(total)}</b><span>zusammen</span></div><div class="sep"></div>
      <div class="s"><b style="color:var(--safe)">${fmtBytes(recSize)}</b><span>davon empfohlen</span></div>
      <div class="grow"></div>
      ${rec.length ? `<button class="btn" data-act="u-select-rec">${icon('check')} Alle Empfehlungen auswählen</button>` : ''}
      ${S.uSel.size ? `<button class="btn ghost" data-act="u-clear">Auswahl aufheben</button>` : ''}
    </div>
    <div class="list">${items.length ? items.map((i) => rowHTML(i, 'unused', max)).join('')
      : `<div class="empty"><div class="ill">${icon('check')}</div><h2>Nichts gefunden</h2><p>Mit diesen Filtern gibt es keine ungenutzten Ordner. Probiere einen kürzeren Zeitraum oder eine kleinere Mindestgröße.</p></div>`}</div>`;
  const s = $('#uSearch');
  s.addEventListener('input', () => { o.q = s.value; const pos = s.selectionStart; renderUnused(); const n = $('#uSearch'); n.focus(); n.setSelectionRange(pos, pos); renderActionbar(); });
}

/* ------------------------------------------------------------------ Große Dateien */
const KIND_GROUPS = [
  { k: 'video', label: 'Videos', color: '#f43f5e', kinds: ['video'] },
  { k: 'game', label: 'Spiele & Abbilder', color: '#a855f7', kinds: ['game', 'disk'] },
  { k: 'archive', label: 'Archive & Installer', color: '#f59e0b', kinds: ['archive', 'installer', 'download'] },
  { k: 'vm', label: 'VMs & KI-Modelle', color: '#22d3ee', kinds: ['vm', 'ai'] },
  { k: 'system', label: 'System', color: '#64748b', kinds: ['system', 'program', 'appdata'] },
  { k: 'junk', label: 'Müll (Logs, Dumps, Temp)', color: '#34d399', kinds: ['dump', 'temp', 'logs', 'cache', 'dev'] },
  { k: 'other', label: 'Sonstiges', color: '#818cf8', kinds: [] },
];
const groupOf = (f) => KIND_GROUPS.find((g) => g.kinds.includes(f.info.kind)) || KIND_GROUPS[KIND_GROUPS.length - 1];
const heat = (s) => (s >= 20 * 2 ** 30 ? 4 : s >= 5 * 2 ** 30 ? 3 : s >= 2 ** 30 ? 2 : 1);
const HEAT_LABEL = { 4: 'GIGANTISCH', 3: 'RIESIG', 2: 'SEHR GROSS' };

function donut(groups, total) {
  const C = 2 * Math.PI * 80;
  let off = 0;
  const arcs = groups.filter((g) => g.v > 0).map((g) => {
    const len = (g.v / total) * C;
    const s = `<circle cx="100" cy="100" r="80" fill="none" stroke="${g.color}" stroke-width="26" stroke-dasharray="${Math.max(0, len - 2)} ${C}" stroke-dashoffset="${-off}"><title>${g.label}: ${fmtBytes(g.v)}</title></circle>`;
    off += len;
    return s;
  }).join('');
  return `<div class="donut"><svg viewBox="0 0 200 200"><circle cx="100" cy="100" r="80" fill="none" stroke="var(--border)" stroke-width="26"/>${arcs}</svg>
    <div class="center"><b>${fmtBytes(total)}</b><span>in großen Dateien</span></div></div>`;
}
function renderLarge() {
  const el = $('#view-large');
  const head = `<div class="page-head"><div><h1>Riesige Dateien</h1>
    <div class="sub">Einzelne Dateien, die übermäßig viel Platz belegen – farblich nach Größe hervorgehoben, mit Erklärung und Empfehlung.</div></div></div>`;
  if (S.scan.state !== 'done') { el.innerHTML = head + needScan('Noch keine Analyse', 'Nach der Analyse siehst du hier die größten Dateien auf deinem PC.', 'flame'); return; }
  const o = S.lOpt;
  const minB = o.min * 2 ** 20;
  let items = S.large.filter((f) => f.size >= minB);
  const groups = KIND_GROUPS.map((g) => ({ ...g, v: 0, n: 0 }));
  items.forEach((f) => { const g = groups.find((x) => x.k === groupOf(f).k); g.v += f.size; g.n++; });
  if (o.kind !== 'all') items = items.filter((f) => groupOf(f).k === o.kind);
  const total = groups.reduce((a, g) => a + g.v, 0);
  const max = Math.max(1, ...items.map((i) => i.size));
  const rec = items.filter((i) => ['safe', 'likely'].includes(i.info.level) && !i.info.protect);
  el.innerHTML = head + `
    <div class="large-top">
      <div class="card donut-wrap">${donut(groups, total || 1)}</div>
      <div class="card">
        <div class="card-head"><div><h2>${icon('flame')} Wer frisst den Platz?</h2><div class="card-sub">Klicke auf eine Gruppe, um nur diese anzuzeigen.</div></div></div>
        <div class="legend">
          <button data-act="l-kind" data-v="all" style="${o.kind === 'all' ? 'background:var(--panel-2);border-color:var(--border)' : ''}"><span class="dot" style="background:var(--grad)"></span><span class="n">Alle Gruppen</span><span class="v">${fmtNum(groups.reduce((a, g) => a + g.n, 0))} Dateien</span></button>
          ${groups.filter((g) => g.n).map((g) => `
          <button data-act="l-kind" data-v="${g.k}" style="${o.kind === g.k ? 'background:var(--panel-2);border-color:var(--border)' : ''}"><span class="dot" style="background:${g.color}"></span><span class="n">${g.label} <span style="color:var(--dim)">· ${g.n}</span></span><span class="v">${fmtBytes(g.v)}</span></button>`).join('')}
        </div>
      </div>
    </div>
    <div class="filters">
      <span class="lab">Mindestgröße</span>${seg('l-min', o.min, [[100, '100 MB'], [500, '500 MB'], [1024, '1 GB'], [5120, '5 GB'], [20480, '20 GB']])}
      <div class="grow" style="flex:1"></div>
      ${rec.length ? `<button class="btn" data-act="l-select-rec">${icon('check')} Empfohlene auswählen (${rec.length})</button>` : ''}
      ${S.lSel.size ? `<button class="btn ghost" data-act="l-clear">Auswahl aufheben</button>` : ''}
    </div>
    <div class="list">${items.length ? items.map((f) => {
      const h = heat(f.size);
      return rowHTML(f, 'large', max, `heat-${h}`, HEAT_LABEL[h] ? `<span class="heat-badge h${h}">${HEAT_LABEL[h]}</span>` : '');
    }).join('') : `<div class="empty"><div class="ill">${icon('check')}</div><h2>Keine Dateien in dieser Größe</h2><p>Wähle eine kleinere Mindestgröße.</p></div>`}</div>`;
}

/* ------------------------------------------------------------------ Spiele */
const LAUNCHER_COLOR = {
  Steam: '#3b82f6', GOG: '#a855f7', 'Epic Games': '#e5e7eb', 'Ubisoft Connect': '#38bdf8', 'Rockstar Games': '#f59e0b',
  'Riot Client': '#f43f5e', 'EA app': '#fb7185', 'Battle.net': '#60a5fa', Xbox: '#22c55e',
};
async function loadGames() {
  try {
    S.games = await api('/api/games');
    const keep = new Set((S.games.leftovers || []).map((g) => g.path));
    [...S.gSel.keys()].forEach((k) => { if (!keep.has(k)) S.gSel.delete(k); });
    if (S.games.state === 'running' || S.games.state === 'idle') setTimeout(loadGames, 1000);
    renderNav();
    if (S.view === 'games' || S.view === 'overview') renderView();
  } catch (e) { setTimeout(loadGames, 2500); }
}
function gameCard(g, max) {
  const active = daysSince(g.lastActive);
  const played = g.lastPlayed ? `zuletzt gespielt ${ago(daysSince(g.lastPlayed))}` : g.lastActive ? `zuletzt aktiv ${ago(active)}` : 'Spielzeit unbekannt';
  const idle = g.lastActive && active > 180;
  const col = LAUNCHER_COLOR[g.launcher] || '#94a3b8';
  return `
  <div class="card game ${idle ? 'idle' : ''}">
    <div class="gtop">
      <span class="launcher" style="--lc:${col}">${esc(g.launcher)}</span>
      ${idle ? `<span class="tag warn">${icon('clock')} lange nicht gespielt</span>` : `<span class="pill lv-keep">wird gebraucht</span>`}
    </div>
    <div class="gname" title="${esc(g.name)}">${esc(g.name)}</div>
    <div class="gsize">${fmtBytes(g.total)}</div>
    <div class="sizebar"><i style="width:${Math.max(2, (g.total / max) * 100)}%"></i></div>
    <div class="gmeta"><span class="${ageClass(active)}">${icon('clock')} ${played}</span></div>
    <div class="gparts">
      <div><span>${icon('folder')} Installation</span><b>${fmtBytes(g.size)}</b></div>
      ${g.data.map((d) => `<div title="${esc(d.path)}"><span>${icon('game')} ${esc(d.label)}</span><b>${fmtBytes(d.size)}</b></div>`).join('')}
    </div>
    <div class="gpath" title="${esc(g.path)}">${esc(g.path)}</div>
    ${idle ? `<div class="ghint">Du hast es seit ${ago(active).replace('vor ', '')} nicht gespielt – deinstallieren gibt ${fmtBytes(g.total)} frei.</div>` : ''}
    <div class="gact">
      ${g.launcher === 'Steam' && g.appid ? `<button class="btn sm" data-act="action" data-target="steam-uninstall" data-appid="${esc(g.appid)}">${icon('trash')} In Steam deinstallieren</button>`
        : `<button class="btn sm" data-act="action" data-target="apps" title="Einstellungen › Apps öffnen">${icon('settings')} Deinstallieren …</button>`}
      <button class="btn sm icon-btn ghost" data-act="open" data-path="${esc(g.path)}" title="Ordner öffnen">${icon('open')}</button>
    </div>
  </div>`;
}
function renderGames() {
  const el = $('#view-games');
  const G = S.games;
  const head = `<div class="page-head"><div><h1>Spiele</h1>
    <div class="sub">Alle installierten Spiele mit ihren Spielständen und Daten – die werden noch gebraucht. Darüber: Reste von Spielen, die du schon deinstalliert hast. Die kannst du bedenkenlos aufräumen.</div></div>
    <button class="btn ghost" data-act="g-refresh" ${G?.state === 'running' ? 'disabled' : ''}>${icon('refresh')} Neu erkennen</button></div>`;
  if (!G || (G.state !== 'done' && !G.installed?.length)) {
    el.innerHTML = head + `<div class="empty"><div class="ill">${icon('game')}</div><h2>Spiele werden gesucht …</h2><p>Steam, GOG, Epic, Ubisoft, Rockstar, Riot, EA und Xbox werden durchsucht.</p></div>`;
    return;
  }
  const inst = [...G.installed];
  if (S.gSort === 'idle') inst.sort((a, b) => (a.lastActive || 9e12) - (b.lastActive || 9e12));
  else if (S.gSort === 'name') inst.sort((a, b) => a.name.localeCompare(b.name, 'de'));
  const max = Math.max(1, ...inst.map((g) => g.total));
  const instSize = inst.reduce((a, g) => a + g.total, 0);
  const idle = inst.filter((g) => g.lastActive && daysSince(g.lastActive) > 180);
  const lo = G.leftovers;
  const loSize = lo.reduce((a, b) => a + folderSize(b), 0);
  const loMax = Math.max(1, ...lo.map((i) => i.size));
  el.innerHTML = head + `
    <div class="summary">
      <div class="s"><b>${inst.length}</b><span>installierte Spiele</span></div><div class="sep"></div>
      <div class="s"><b>${fmtBytes(instSize)}</b><span>inkl. Spielstände & Daten</span></div><div class="sep"></div>
      <div class="s"><b style="color:var(--likely)">${idle.length}</b><span>lange nicht gespielt (${fmtBytes(idle.reduce((a, g) => a + g.total, 0))})</span></div><div class="sep"></div>
      <div class="s"><b style="color:var(--safe)">${fmtBytes(loSize)}</b><span>Reste deinstallierter Spiele</span></div>
    </div>
    <div class="sec-head"><h2>${icon('trash')} Reste deinstallierter Spiele</h2>
      ${lo.length ? `<button class="btn" data-act="g-select-rec">${icon('check')} Alle auswählen</button>` : ''}</div>
    <div class="card-sub" style="margin:-6px 0 12px">Zu diesen Daten ist kein installiertes Spiel mehr vorhanden. Ganz oben stehen die sicheren Fälle (Spieldateien, Shader-Caches). Darunter folgen Einstellungen und Spielstände.</div>
    <div class="list">${lo.length ? lo.map((i) => rowHTML(i, 'games', loMax)).join('')
      : `<div class="card" style="text-align:center;color:var(--muted)">${icon('check')} Keine Überreste gefunden – sauber!</div>`}</div>
    <div class="sec-head" style="margin-top:30px"><h2>${icon('game')} Installierte Spiele</h2>
      ${seg('g-sort', S.gSort, [['size', 'Größte zuerst'], ['idle', 'Am längsten nicht gespielt'], ['name', 'Name']])}</div>
    <div class="ggrid">${inst.map((g) => gameCard(g, max)).join('')}</div>`;
}

/* ------------------------------------------------------------------ Hell/Dunkel */
function setTheme(t) {
  try { if (t === 'system') localStorage.removeItem('sp-theme'); else localStorage.setItem('sp-theme', t); } catch { /* egal */ }
  if (t === 'system') document.documentElement.removeAttribute('data-theme');
  else document.documentElement.setAttribute('data-theme', t);
  renderThemeSwitch();
}
function renderThemeSwitch() {
  let cur = 'system';
  try { cur = localStorage.getItem('sp-theme') || 'system'; } catch { /* egal */ }
  $('#themeSwitch').innerHTML = [['light', 'sun', 'Hell'], ['dark', 'moon', 'Dunkel'], ['system', 'monitor', 'System']]
    .map(([v, ic, l]) => `<button class="${cur === v ? 'on' : ''}" data-act="theme" data-v="${v}" title="${l}">${icon(ic)} ${l}</button>`).join('');
}

/* ------------------------------------------------------------------ Speicherkarte */
const AGE_STOPS = [[0, [45, 212, 191]], [30, [56, 189, 248]], [180, [129, 140, 248]], [365, [245, 158, 11]], [1095, [244, 63, 94]]];
function ageColor(days) {
  const t = (d) => Math.log10(1 + Math.max(0, d));
  const x = t(Math.min(days, 1095));
  for (let i = 1; i < AGE_STOPS.length; i++) {
    const [d0, c0] = AGE_STOPS[i - 1], [d1, c1] = AGE_STOPS[i];
    if (x <= t(d1)) {
      const k = (x - t(d0)) / (t(d1) - t(d0) || 1);
      const c = c0.map((v, j) => Math.round(v + (c1[j] - v) * k));
      return `rgb(${c.join(',')})`;
    }
  }
  return 'rgb(244,63,94)';
}
function squarify(items, x, y, w, h) {
  const out = [];
  const total = items.reduce((a, b) => a + b.size, 0);
  if (!total || w <= 0 || h <= 0) return out;
  const scale = (w * h) / total;
  const rest = items.map((it) => ({ it, a: it.size * scale }));
  const worst = (row, side) => {
    const s = row.reduce((a, r) => a + r.a, 0);
    const mx = Math.max(...row.map((r) => r.a)), mn = Math.min(...row.map((r) => r.a));
    return Math.max((side * side * mx) / (s * s), (s * s) / (side * side * mn));
  };
  const layout = (row) => {
    const s = row.reduce((a, r) => a + r.a, 0);
    if (w >= h) {
      const cw = s / h; let yy = y;
      row.forEach((r) => { const rh = r.a / cw; out.push({ ...r, x, y: yy, w: cw, h: rh }); yy += rh; });
      x += cw; w -= cw;
    } else {
      const rh = s / w; let xx = x;
      row.forEach((r) => { const rw = r.a / rh; out.push({ ...r, x: xx, y, w: rw, h: rh }); xx += rw; });
      y += rh; h -= rh;
    }
  };
  let row = [];
  while (rest.length) {
    const side = Math.min(w, h);
    const c = rest[0];
    if (!row.length || worst([...row, c], side) <= worst(row, side)) { row.push(rest.shift()); }
    else { layout(row); row = []; }
  }
  if (row.length) layout(row);
  return out;
}
async function loadTree(path) {
  try {
    S.tree = await api(`/api/tree?path=${encodeURIComponent(path || '')}`);
  } catch (e) { toast('err', 'Ordner nicht verfügbar', e.message); }
  if (S.view === 'map') renderMap();
}
function renderMap() {
  const el = $('#view-map');
  const head = `<div class="page-head"><div><h1>Speicherkarte</h1>
    <div class="sub">Jede Fläche ist so groß wie ihr Platzbedarf. Die Farbe zeigt, wie lange sich dort nichts mehr verändert hat. Klicke, um hineinzuzoomen.</div></div></div>`;
  if (S.scan.state !== 'done') { el.innerHTML = head + needScan('Noch keine Analyse', 'Die Speicherkarte zeigt dir nach der Analyse, wo dein Platz hingeht.', 'map'); return; }
  if (!S.tree) { el.innerHTML = head + '<div class="treemap"></div>'; loadTree(''); return; }
  const t = S.tree, n = t.node;
  const info = n.info;
  const age = daysSince(n.mtime);
  const canDel = info && !info.protect && n.kind === 'dir';
  el.innerHTML = head + `
    <div class="crumbs">${t.crumbs.map((c, i) => `${i ? icon('chev') : ''}<button data-act="map-go" data-path="${esc(c.path)}">${i === 0 ? icon('home') + ' ' : ''}${esc(c.name)}</button>`).join('')}</div>
    <div class="map-layout">
      <div class="treemap" id="treemap"></div>
      <div class="card side-panel">
        <div class="ricon" style="margin-bottom:12px;color:${info ? LEVEL_COLOR[info.level] : 'var(--accent-2)'}">${icon(info ? info.icon : (n.kind === 'drive' ? 'hdd' : 'globe'))}</div>
        <h3>${esc(n.name)}</h3>
        ${info ? `<div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">${pill(info.level)}<span class="tag">${esc(info.title)}</span></div>` : ''}
        <div class="kv">
          <span class="k">Größe</span><span class="v">${fmtBytes(n.size)}</span>
          <span class="k">Dateien</span><span class="v">${fmtNum(n.files)}</span>
          <span class="k">Unterordner</span><span class="v">${fmtNum(n.dirs)}</span>
          ${n.kind !== 'virtual' ? `<span class="k">Zuletzt geändert</span><span class="v">${ago(age)}</span>` : ''}
        </div>
        ${info ? `<div class="rtext">${esc(info.text)}</div>` : ''}
        ${n.denied ? `<div class="warnbox">${icon('alert')} Auf Teile dieses Ordners hatte SpeicherPilot keinen Zugriff.</div>` : ''}
        <div style="display:flex;gap:8px;margin-top:16px;flex-wrap:wrap">
          ${t.crumbs.length > 1 ? `<button class="btn sm" data-act="map-go" data-path="${esc(t.crumbs[t.crumbs.length - 2].path)}">${icon('up')} Ebene hoch</button>` : ''}
          ${n.path && n.kind !== 'virtual' ? `<button class="btn sm" data-act="open" data-path="${esc(n.path)}">${icon('open')} Explorer</button>` : ''}
          ${canDel ? `<button class="btn sm danger" data-act="del-map" data-path="${esc(n.path)}">${icon('trash')} Löschen</button>` : ''}
        </div>
        <div class="age-legend"><div class="card-sub">Zuletzt geändert</div><div class="age-scale"></div>
          <div class="age-ticks"><span>heute</span><span>1 Mon.</span><span>6 Mon.</span><span>1 J.</span><span>3 J.+</span></div></div>
      </div>
    </div>`;
  drawTreemap();
}
function drawTreemap() {
  const box = $('#treemap');
  if (!box || !S.tree) return;
  const W = box.clientWidth, H = box.clientHeight;
  const kids = S.tree.children.filter((c) => c.size > 0).sort((a, b) => b.size - a.size);
  const rects = squarify(kids, 0, 0, W, H);
  const colorOf = (c) => (c.kind === 'system' ? 'rgb(71,85,105)' : c.kind === 'other' ? 'rgb(100,116,139)' : ageColor(daysSince(c.mtime)));
  const subRects = [];
  box.innerHTML = rects.map((r, i) => {
    const c = r.it;
    const drill = c.path && c.kind !== 'system';
    const kids = (c.kids || []).filter((k) => k.size > 0);
    const nest = kids.length > 1 && r.w > 120 && r.h > 90;
    const attrs = `data-i="${i}" ${drill ? `data-act="map-go" data-path="${esc(c.path)}"` : ''}`;
    const style = `left:${r.x}px;top:${r.y}px;width:${r.w}px;height:${r.h}px;background-color:${colorOf(c)};animation-delay:${Math.min(i * 12, 400)}ms`;
    if (nest) {
      const sub = squarify(kids, 3, 24, r.w - 10, r.h - 31);
      subRects[i] = sub;
      return `<div class="tile nest ${drill ? '' : 'nodrill'}" style="${style}" ${attrs}>
        <div class="th"><span class="tn">${esc(c.name)}</span><span class="ts">${fmtBytes(c.size)}</span></div>
        ${sub.map((s, j) => {
          const k = s.it, kd = k.path && k.kind !== 'system';
          return `<div class="tile sub ${kd ? '' : 'nodrill'}" style="left:${s.x}px;top:${s.y}px;width:${s.w}px;height:${s.h}px;background-color:${colorOf(k)}"
            data-i="${i}" data-j="${j}" ${kd ? `data-act="map-go" data-path="${esc(k.path)}"` : ''}>
            ${s.w > 70 && s.h > 32 ? `<div class="tn">${esc(k.name)}</div><div class="ts">${fmtBytes(k.size)}</div>` : ''}</div>`;
        }).join('')}</div>`;
    }
    const label = r.w > 64 && r.h > 34;
    return `<div class="tile ${drill ? '' : 'nodrill'} ${r.w > 220 && r.h > 90 ? 'big' : ''}" style="${style}" ${attrs}>
      ${label ? `<div class="tn">${esc(c.name)}</div><div class="ts">${fmtBytes(c.size)}</div>` : ''}</div>`;
  }).join('');
  box.onmousemove = (e) => {
    const tile = e.target.closest('.tile');
    if (!tile) return hideTooltip();
    const c = tile.dataset.j != null ? subRects[+tile.dataset.i][+tile.dataset.j].it : rects[+tile.dataset.i].it;
    const age = daysSince(c.mtime);
    const extra = c.kind === 'system' ? 'Windows, Auslagerungsdatei, geschützte Ordner & Bereiche ohne Zugriff'
      : c.kind === 'files' ? 'Einzelne Dateien in diesem Ordner' : `zuletzt geändert ${ago(age)}`;
    showTooltip(e, `<b>${esc(c.name)}</b>${fmtBytes(c.size)} · ${(c.size / S.tree.node.size * 100).toFixed(1).replace('.', ',')} %<br><span>${extra}</span>`);
  };
  box.onmouseleave = hideTooltip;
}
window.addEventListener('resize', () => { if (S.view === 'map') drawTreemap(); });

/* ------------------------------------------------------------------ Löschen */
async function deleteItems(items, src) {
  if (!items.length) return;
  const eff = (i) => (S.uKeep[i.path]?.size ? folderSize(i) : i.size);
  const total = items.reduce((a, b) => a + eff(b), 0);
  const review = items.filter((i) => !['safe', 'likely'].includes(i.info?.level));
  const keptN = items.reduce((a, i) => a + (S.uKeep[i.path]?.size || 0), 0);
  const res = await modal({
    title: `${items.length === 1 ? `„${items[0].name}“` : `${items.length} Elemente`} löschen?`,
    sub: `Zusammen ${fmtBytes(total)}.${keptN ? ` ${keptN} von dir markierte Einträge bleiben erhalten.` : ''}`,
    list: items.map((i) => [i.path + (S.uKeep[i.path]?.size ? ` (${S.uKeep[i.path].size} behalten)` : ''), fmtBytes(eff(i))]),
    modePick: true,
    warn: review.length ? `${review.length === 1 ? 'Ein Element ist' : `${review.length} Elemente sind`} als „Bitte prüfen“ markiert – stelle sicher, dass du ${review.length === 1 ? 'es' : 'sie'} wirklich nicht mehr brauchst.` : null,
    confirm: 'Löschen', danger: true,
  });
  if (!res) return;
  const paths = items.map((i) => i.path);
  const btn = $('#abBtn') || $('#dRun');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Lösche …'; }
  paths.forEach((p) => $$(`.row[data-path="${CSS.escape(p)}"]`).forEach((r) => r.style.opacity = '.5'));
  const keep = {};
  paths.forEach((p) => { if (S.uKeep[p]?.size) keep[p] = [...S.uKeep[p].keys()]; });
  const keptPaths = Object.values(keep).flat().map((k) => k.toLowerCase());
  try {
    const r = await api('/api/delete', { paths, mode: res.mode, keep });
    const rect = btn?.getBoundingClientRect();
    closeDrawer();
    const okSet = new Set(r.results.filter((x) => x.ok).map((x) => x.path));
    okSet.forEach((p) => $$(`.row[data-path="${CSS.escape(p)}"]`).forEach((row) => row.classList.add('removing')));
    await new Promise((ok) => setTimeout(ok, 380));
    S.unused = S.unused.filter((u) => !okSet.has(u.path));
    if (S.games) S.games.leftovers = S.games.leftovers.filter((u) => !okSet.has(u.path));
    const lc = (s) => s.toLowerCase();
    S.large = S.large.filter((f) => keptPaths.some((k) => lc(f.path) === k || lc(f.path).startsWith(k + '\\'))
      || (!okSet.has(f.path) && ![...okSet].some((p) => lc(f.path).startsWith(lc(p) + '\\'))));
    okSet.forEach((p) => { S.uSel.delete(p); S.lSel.delete(p); S.gSel.delete(p); delete S.uKeep[p]; });
    S.recycle = r.recycleBin; renderBin();
    S.sessionFreed = r.sessionFreed; setSessionFreed(r.sessionFreed);
    const failed = r.results.filter((x) => !x.ok);
    if (okSet.size || r.freed) {
      burst(rect ? { getBoundingClientRect: () => rect } : null);
      if (r.mode === 'recycle') {
        toast('ok', `${fmtBytes(r.freed)} in den Papierkorb verschoben`, 'Der Platz wird frei, sobald du den Papierkorb leerst.', { label: 'Papierkorb ansehen', act: 'bin-view' });
      } else {
        toast('ok', `${fmtBytes(r.freed)} freigegeben`, `${okSet.size} ${okSet.size === 1 ? 'Element' : 'Elemente'} endgültig gelöscht.`);
      }
    }
    failed.forEach((f) => toast('err', f.partial ? 'Teilweise gelöscht' : 'Nicht gelöscht', `${f.path.split('\\').pop()}: ${f.error}`));
    if (src === 'map') { const cr = S.tree.crumbs; await loadTree(cr.length > 1 ? cr[cr.length - 2].path : ''); }
    else if (S.tree) S.tree = null;
    refreshDrives().then(() => S.view === 'overview' && renderOverview());
  } catch (e) { toast('err', 'Löschen fehlgeschlagen', e.message); }
  renderView(); renderNav();
}
async function emptyBin() {
  const ok = await modal({
    title: 'Papierkorb leeren?',
    sub: `${fmtNum(S.recycle.items)} Elemente mit ${fmtBytes(S.recycle.size)} werden endgültig gelöscht.`,
    warn: 'Das kann nicht rückgängig gemacht werden.', confirm: 'Endgültig leeren', danger: true,
  });
  if (!ok) return;
  try {
    const r = await api('/api/recyclebin/empty', {});
    S.recycle = r.recycleBin; renderBin();
    toast('ok', `${fmtBytes(r.freed)} freigegeben`, 'Der Papierkorb ist leer.');
    burst($('#binCard'));
    await refreshDrives();
    loadJunk();
    renderView();
  } catch (e) { toast('err', 'Fehler', e.message); }
}

/* ------------------------------------------------------------------ Detail-Panel (was steckt dahinter?) */
const D = { open: false, kind: null, key: null, items: [], total: 0, keep: new Map(), q: '', sort: 'size', loading: false };
const EXT_ICON = [
  [/\.(mp4|mkv|mov|avi|wmv|m4v|webm|flv|ts|mts)$/i, 'video'], [/\.(jpe?g|png|gif|webp|heic|bmp|psd|raw|tiff?)$/i, 'image'],
  [/\.(zip|rar|7z|tar|gz|tgz|xz|cab)$/i, 'archive'], [/\.(exe|msi|msix|appx)$/i, 'package'], [/\.(iso|img)$/i, 'disc'],
  [/\.(mp3|wav|flac|m4a|aac|ogg)$/i, 'music'], [/\.(pdf|docx?|xlsx?|pptx?|txt)$/i, 'doc'], [/\.(dmp|log)$/i, 'alert'],
  [/\.(stl|obj|fbx|blend|3mf|lys)$/i, 'box'],
];
const fileIcon = (name, isDir) => (isDir ? 'folder' : (EXT_ICON.find(([re]) => re.test(name)) || [0, 'file'])[1]);

async function openDrawer(kind, key) {
  Object.assign(D, { open: true, kind, key, items: [], total: 0, q: '', sort: kind === 'bin' ? 'size' : 'size', loading: true });
  D.keep = new Map(kind === 'folder' ? S.uKeep[key] || [] : S.junkKeep[key] || []);
  if (kind === 'junk' && key === 'recyclebin') D.kind = 'bin';
  renderDrawer();
  $('#drawer').classList.add('show');
  try {
    const url = kind === 'folder' ? `/api/folder/items?path=${encodeURIComponent(key)}` : `/api/junk/items?id=${encodeURIComponent(key)}`;
    const r = await api(url);
    D.items = r.items; D.total = r.total;
    // behaltene Einträge, die es nicht mehr gibt, vergessen
    const exists = new Set(D.items.map((i) => i.path));
    [...D.keep.keys()].forEach((k) => { if (!exists.has(k)) D.keep.delete(k); });
  } catch (e) { toast('err', 'Inhalt konnte nicht geladen werden', e.message); }
  D.loading = false;
  renderDrawer();
}
function closeDrawer() {
  D.open = false;
  $('#drawer').classList.remove('show');
}
function drawerMeta() {
  if (D.kind === 'folder') {
    const it = findFolder(D.key);
    return { title: it?.name || D.key, sub: D.key, ic: it?.info.icon || 'folder', it };
  }
  const c = S.junk?.categories.find((x) => x.id === D.key);
  return { title: c?.name || '', sub: c?.text || '', ic: c?.icon || 'sparkles', cat: c };
}
function drawerList() {
  const q = D.q.trim().toLowerCase();
  let list = D.items.filter((i) => !q || i.name.toLowerCase().includes(q) || (i.orig || i.sub || '').toLowerCase().includes(q));
  const by = { size: (a, b) => b.size - a.size, date: (a, b) => (a.mtime || 0) - (b.mtime || 0), name: (a, b) => a.name.localeCompare(b.name, 'de') };
  return list.sort(by[D.sort]);
}
function renderDrawer() {
  const el = $('#drawer');
  if (!D.open) return;
  const m = drawerMeta();
  const list = drawerList();
  const shown = list.slice(0, 400);
  const keptSize = mapSum(D.keep);
  const allSize = D.items.reduce((a, b) => a + b.size, 0);
  const delSize = Math.max(0, (D.kind === 'folder' ? m.it?.size || allSize : allSize) - keptSize);
  const delCount = D.total - D.keep.size;
  const isBin = D.kind === 'bin';
  const dateLbl = isBin ? 'gelöscht' : 'geändert';
  const hint = isBin
    ? 'Das hier liegt im Papierkorb. Entferne das Häkchen bei allem, was du behalten willst – oder lege es mit „Zurücklegen“ wieder an seinen alten Platz.'
    : D.kind === 'folder'
      ? 'Das liegt direkt in diesem Ordner. Entferne das Häkchen bei allem, was du behalten willst – der Rest wird gelöscht.'
      : 'Das würde bereinigt. Entferne das Häkchen bei allem, was du behalten willst.';
  el.innerHTML = `
    <div class="drawer-back" data-act="d-close"></div>
    <aside class="drawer-panel" role="dialog" aria-modal="true">
      <div class="dhead">
        <div class="bubble">${icon(m.ic)}</div>
        <div class="dt"><h2>${esc(m.title)}</h2><span title="${esc(m.sub)}">${esc(D.kind === 'folder' ? m.sub : `${fmtNum(D.total)} Einträge · ${fmtBytes(allSize)}`)}</span></div>
        <button class="btn icon-btn ghost" data-act="d-close" title="Schließen (Esc)">${icon('x')}</button>
      </div>
      <div class="dhint">${icon('info')}<span>${hint}</span></div>
      <div class="dtools">
        <div class="search">${icon('search')}<input id="dSearch" placeholder="Suchen …" value="${esc(D.q)}"></div>
        ${seg('d-sort', D.sort, [['size', 'Größe'], ['date', 'Datum'], ['name', 'Name']])}
        <div style="flex:1"></div>
        <button class="btn sm ghost" data-act="d-all">Alle löschen</button>
        <button class="btn sm ghost" data-act="d-none">Alle behalten</button>
      </div>
      <div class="dlist">
        ${D.loading ? Array.from({ length: 7 }, () => '<div class="ditem"><span class="skeleton" style="width:100%;height:34px"></span></div>').join('')
          : shown.length ? shown.map((i) => {
            const kept = D.keep.has(i.path);
            const age = daysSince(i.mtime);
            return `<div class="ditem ${kept ? 'kept' : ''}" data-act="d-toggle" data-path="${esc(i.path)}">
              <span class="check"><input type="checkbox" tabindex="-1" ${kept ? '' : 'checked'}><span></span></span>
              <div class="ricon">${icon(fileIcon(i.name, i.isDir))}</div>
              <div class="dm"><div class="dn" title="${esc(i.name)}">${esc(i.name)}</div>
                <div class="ds" title="${esc(i.orig || i.sub || '')}">${esc(i.orig || i.sub || '')}${i.isDir && i.count > 1 ? ` · ${fmtNum(i.count)} Dateien` : ''}</div></div>
              <div class="dr"><b>${fmtBytes(i.size)}</b><span class="${ageClass(age)}">${dateLbl} ${ago(age)}</span></div>
              <div class="da">${kept ? `<span class="tag keep">${icon('shield')} behalten</span>` : ''}
                ${isBin ? `<button class="btn sm" data-act="d-restore" data-path="${esc(i.path)}" title="An den ursprünglichen Ort zurücklegen">${icon('up')} Zurücklegen</button>`
                  : `<button class="btn sm icon-btn ghost" data-act="open" data-path="${esc(i.path)}" title="Im Explorer zeigen">${icon('open')}</button>`}</div>
            </div>`;
          }).join('') + (list.length > shown.length ? `<div class="dmore">… und ${fmtNum(list.length - shown.length)} weitere – nutze die Suche.</div>` : '')
            + (D.total > D.items.length ? `<div class="dmore">Angezeigt werden die ${fmtNum(D.items.length)} größten von ${fmtNum(D.total)} Einträgen.</div>` : '')
          : `<div class="empty" style="padding:40px"><h2>Nichts gefunden</h2><p>${D.q ? 'Keine Treffer für diese Suche.' : 'Hier ist nichts (mehr) zu bereinigen.'}</p></div>`}
      </div>
      <div class="dfoot">
        <div class="dsum"><b>${fmtBytes(delSize)}</b> werden gelöscht<span>${fmtNum(Math.max(0, delCount))} von ${fmtNum(D.total)} Einträgen${D.keep.size ? ` · <em>${D.keep.size} behalten (${fmtBytes(keptSize)})</em>` : ''}</span></div>
        <button class="btn ghost" data-act="d-apply">Übernehmen</button>
        <button class="btn danger" id="dRun" data-act="d-run" ${delCount > 0 && !D.loading ? '' : 'disabled'}>${icon(D.kind === 'folder' ? 'trash' : 'sparkles')} ${D.kind === 'folder' ? 'Jetzt löschen …' : 'Jetzt bereinigen …'}</button>
      </div>
    </aside>`;
  const s = $('#dSearch');
  s.addEventListener('input', () => { D.q = s.value; const pos = s.selectionStart; renderDrawer(); const n = $('#dSearch'); n.focus(); n.setSelectionRange(pos, pos); });
}
function applyDrawer() {
  const keep = new Map(D.keep);
  const somethingLeft = D.total - keep.size > 0;
  if (D.kind === 'folder') {
    if (keep.size) S.uKeep[D.key] = keep; else delete S.uKeep[D.key];
    const it = findFolder(D.key);
    const sel = S.unused.includes(it) ? S.uSel : S.gSel;
    if (it && somethingLeft) sel.set(it.path, it);
    if (it && !somethingLeft) sel.delete(it.path);
  } else {
    if (keep.size) S.junkKeep[D.key] = keep; else delete S.junkKeep[D.key];
    S.junkTouched = true;
    if (somethingLeft) S.junkSel.add(D.key); else S.junkSel.delete(D.key);
  }
}
async function restoreFromBin(path) {
  const it = D.items.find((i) => i.path === path);
  try {
    const r = await api('/api/recyclebin/restore', { paths: [path] });
    const res = r.results[0];
    if (!res.ok) return toast('err', 'Nicht zurückgelegt', res.error);
    D.items = D.items.filter((i) => i.path !== path); D.total--; D.keep.delete(path);
    toast('ok', `„${it?.name}“ zurückgelegt`, res.restored);
    S.recycle = r.recycleBin; renderBin();
    renderDrawer();
    setTimeout(loadJunk, 800);
  } catch (e) { toast('err', 'Fehler', e.message); }
}

/* ------------------------------------------------------------------ Actionbar */
function renderActionbar() {
  const bar = $('#actionbar');
  let html = '';
  if (S.view === 'junk' && S.junk) {
    const cats = S.junk.categories.filter((c) => S.junkSel.has(c.id));
    const size = cats.reduce((a, c) => a + junkSize(c), 0);
    if (cats.length) html = `<div class="info"><b>${fmtBytes(size)}</b><span>${cats.length} ${cats.length === 1 ? 'Kategorie' : 'Kategorien'} ausgewählt</span></div>
      <button class="btn primary big" id="abBtn" data-act="junk-clean" ${size ? '' : 'disabled'}>${icon('sparkles')} Jetzt bereinigen</button>`;
  } else if (S.view === 'unused' || S.view === 'large' || S.view === 'games') {
    const sel = SEL(S.view);
    if (sel.size) {
      const size = [...sel.values()].reduce((a, b) => a + (isFolderSrc(S.view) ? folderSize(b) : b.size), 0);
      html = `<div class="info"><b>${fmtBytes(size)}</b><span>${sel.size} ${sel.size === 1 ? 'Element' : 'Elemente'} ausgewählt</span></div>
        <button class="btn ghost" data-act="${({ unused: 'u-clear', large: 'l-clear', games: 'g-clear' })[S.view]}">Aufheben</button>
        <button class="btn danger big" id="abBtn" data-act="del-selected">${icon('trash')} Löschen …</button>`;
    }
  }
  bar.innerHTML = html;
  bar.classList.toggle('show', !!html);
}

/* ------------------------------------------------------------------ Modal, Toast, Tooltip, Effekte */
function modal({ title, sub, list, warn, confirm = 'OK', danger = false, modePick = false }) {
  return new Promise((resolve) => {
    const wrap = $('#modal');
    const shown = (list || []).slice(0, 60);
    wrap.innerHTML = `<div class="modal" role="dialog" aria-modal="true">
      <h2>${esc(title)}</h2><div class="msub">${esc(sub || '')}</div>
      ${modePick ? `<div class="mode-pick">
        <label><input type="radio" name="mode" value="recycle" checked><div>${icon('trash')}</div><div><b>In den Papierkorb</b><span>Sicher – lässt sich wiederherstellen. Platz wird erst beim Leeren frei.</span></div></label>
        <label><input type="radio" name="mode" value="permanent"><div>${icon('zap')}</div><div><b>Endgültig löschen</b><span>Platz ist sofort frei. Nicht rückgängig zu machen.</span></div></label>
      </div>` : ''}
      ${shown.length ? `<div class="modal-list">${shown.map(([a, b]) => `<div><span class="p" title="${esc(a)}">${esc(a)}</span><b>${esc(b)}</b></div>`).join('')}
        ${list.length > shown.length ? `<div><span class="p">… und ${list.length - shown.length} weitere</span></div>` : ''}</div>` : ''}
      ${warn ? `<div class="warnbox">${icon('alert')}<span>${esc(warn)}</span></div>` : ''}
      <div class="modal-actions"><button class="btn ghost" data-m="0">Abbrechen</button><button class="btn ${danger ? 'danger' : 'primary'}" data-m="1">${esc(confirm)}</button></div>
    </div>`;
    wrap.classList.add('show');
    const close = (v) => { wrap.classList.remove('show'); wrap.onclick = null; document.removeEventListener('keydown', key); resolve(v); };
    const key = (e) => { if (e.key === 'Escape') close(false); };
    document.addEventListener('keydown', key);
    wrap.onclick = (e) => {
      if (e.target === wrap) return close(false);
      const b = e.target.closest('[data-m]');
      if (!b) return;
      if (b.dataset.m === '0') return close(false);
      close(modePick ? { mode: $('input[name=mode]:checked', wrap).value } : true);
    };
    setTimeout(() => $('[data-m="1"]', wrap).focus(), 50);
  });
}
function toast(type, title, text, action) {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<div class="ti">${icon(type === 'ok' ? 'check' : type === 'err' ? 'alert' : 'info')}</div>
    <div class="tt"><b>${esc(title)}</b>${text ? `<span>${esc(text)}</span>` : ''}</div>
    ${action ? `<button class="btn sm" data-act="${action.act}">${esc(action.label)}</button>` : ''}`;
  $('#toasts').appendChild(t);
  setTimeout(() => { t.classList.add('hide'); setTimeout(() => t.remove(), 320); }, action ? 9000 : 5200);
}
function showTooltip(e, html) {
  const tt = $('#tooltip');
  tt.innerHTML = html;
  tt.classList.add('show');
  const r = tt.getBoundingClientRect();
  let x = e.clientX + 16, y = e.clientY + 16;
  if (x + r.width > innerWidth - 8) x = e.clientX - r.width - 16;
  if (y + r.height > innerHeight - 8) y = e.clientY - r.height - 16;
  tt.style.left = `${x}px`; tt.style.top = `${y}px`;
}
function hideTooltip() { $('#tooltip').classList.remove('show'); }
function burst(anchor) {
  const fx = $('#fx');
  const r = anchor?.getBoundingClientRect?.() || { left: innerWidth / 2, top: innerHeight / 2, width: 0, height: 0 };
  const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  const colors = ['#8b5cf6', '#22d3ee', '#34d399', '#fbbf24', '#f43f5e', '#ffffff'];
  for (let i = 0; i < 46; i++) {
    const s = document.createElement('i');
    s.className = 'spark';
    const a = Math.random() * Math.PI * 2, d = 80 + Math.random() * 180;
    s.style.cssText = `left:${cx}px;top:${cy}px;background:${colors[i % colors.length]};--dx:${Math.cos(a) * d}px;--dy:${Math.sin(a) * d - 60}px;--r:${Math.random() * 720}deg;animation-delay:${Math.random() * 80}ms`;
    fx.appendChild(s);
    setTimeout(() => s.remove(), 1300);
  }
}

/* ------------------------------------------------------------------ Ereignisse */
const ACTIONS = {
  nav: (d) => go(d.view),
  scope: (d) => {
    const r = d.root;
    if (S.scope.has(r)) S.scope.delete(r); else S.scope.add(r);
    renderOverview();
  },
  'scope-remove': (d, e) => { e.stopPropagation(); S.custom = S.custom.filter((c) => c !== d.root); S.scope.delete(d.root); renderOverview(); },
  'pick-folder': async () => {
    toast('info', 'Ordnerauswahl geöffnet', 'Das Auswahlfenster kann hinter diesem Fenster liegen.');
    const r = await api('/api/pick-folder', {});
    if (r.path) { if (!S.custom.includes(r.path)) S.custom.push(r.path); S.scope.add(r.path); renderOverview(); }
  },
  'scan-start': startScan,
  'scan-cancel': () => api('/api/scan/cancel', {}),
  'junk-toggle': (d) => { S.junkTouched = true; S.junkSel.has(d.id) ? S.junkSel.delete(d.id) : S.junkSel.add(d.id); renderJunk(); renderActionbar(); renderNav(); },
  'junk-clean': cleanJunk,
  'junk-measure': async () => { await api('/api/junk/measure', {}); S.junk.measuring = true; S.junk.categories.forEach((c) => c.measured = false); renderJunk(); setTimeout(loadJunk, 600); },
  'bin-empty': emptyBin,
  'bin-view': () => { if (S.view !== 'junk') go('junk'); openDrawer('junk', 'recyclebin'); },
  'junk-details': (d, e) => { e.stopPropagation(); openDrawer('junk', d.id); },
  'folder-details': (d) => openDrawer('folder', d.path),
  'd-close': closeDrawer,
  'd-toggle': (d) => {
    const it = D.items.find((i) => i.path === d.path);
    if (!it) return;
    if (D.keep.has(it.path)) D.keep.delete(it.path); else D.keep.set(it.path, it.size);
    renderDrawer();
  },
  'd-all': () => { drawerList().forEach((i) => D.keep.delete(i.path)); renderDrawer(); },
  'd-none': () => { drawerList().forEach((i) => D.keep.set(i.path, i.size)); renderDrawer(); },
  'd-sort': (d) => { D.sort = d.v; renderDrawer(); },
  'd-restore': (d, e) => { e.stopPropagation(); return restoreFromBin(d.path); },
  'd-apply': () => {
    applyDrawer();
    const n = D.keep.size;
    closeDrawer();
    renderView(); renderNav();
    toast('ok', 'Auswahl übernommen', n ? `${n} ${n === 1 ? 'Eintrag bleibt' : 'Einträge bleiben'} erhalten.` : 'Alles wird bereinigt.');
  },
  'd-run': async () => {
    applyDrawer();
    renderView(); renderNav();
    if (D.kind === 'folder') {
      const it = findFolder(D.key);
      if (it) await deleteItems([it], S.unused.includes(it) ? 'unused' : 'games');
    } else {
      await cleanJunk([D.key]);
    }
  },
  'u-days': async (d) => { S.uOpt.days = +d.v; await loadUnused(); renderUnused(); renderNav(); renderActionbar(); },
  'u-min': async (d) => { S.uOpt.min = +d.v; await loadUnused(); renderUnused(); renderNav(); renderActionbar(); },
  'u-level': (d) => { S.uOpt.level = d.v; renderUnused(); },
  'u-select-rec': () => { filteredUnused().filter((i) => ['safe', 'likely'].includes(i.info.level) && !i.info.protect).forEach((i) => S.uSel.set(i.path, i)); renderUnused(); renderActionbar(); },
  'u-clear': () => { S.uSel.clear(); renderView(); },
  'l-min': (d) => { S.lOpt.min = +d.v; renderLarge(); },
  'l-kind': (d) => { S.lOpt.kind = d.v; renderLarge(); },
  'l-select-rec': () => { S.large.filter((i) => i.size >= S.lOpt.min * 2 ** 20 && ['safe', 'likely'].includes(i.info.level) && !i.info.protect && (S.lOpt.kind === 'all' || groupOf(i).k === S.lOpt.kind)).forEach((i) => S.lSel.set(i.path, i)); renderLarge(); renderActionbar(); },
  'l-clear': () => { S.lSel.clear(); renderView(); },
  'g-clear': () => { S.gSel.clear(); renderView(); },
  'g-select-rec': () => { (S.games?.leftovers || []).forEach((i) => S.gSel.set(i.path, i)); renderGames(); renderActionbar(); },
  'g-sort': (d) => { S.gSort = d.v; renderGames(); },
  'g-refresh': async () => { await api('/api/games/refresh', {}); S.games.state = 'running'; renderGames(); setTimeout(loadGames, 700); },
  theme: (d) => setTheme(d.v),
  open: (d) => api('/api/open', { path: d.path }).catch((e) => toast('err', 'Konnte nicht öffnen', e.message)),
  action: (d) => api('/api/action', { target: d.target, path: d.path, appid: d.appid }).catch((e) => toast('err', 'Konnte nicht öffnen', e.message)),
  'del-one': (d) => {
    const list = LIST(d.src);
    const it = list.find((x) => x.path === d.path);
    if (it) deleteItems([it], d.src);
  },
  'del-selected': () => deleteItems([...SEL(S.view).values()], S.view),
  'del-map': () => {
    const n = S.tree.node;
    deleteItems([{ path: n.path, name: n.name, size: n.size, info: n.info }], 'map');
  },
  'map-go': (d) => { hideTooltip(); loadTree(d.path); },
  elevate: async () => {
    try {
      const r = await api('/api/elevate', {});
      if (!r.ok) return toast('err', 'Nicht gestartet', 'Die Administrator-Anfrage wurde abgelehnt.');
      document.body.insertAdjacentHTML('beforeend', `<div class="overlay-msg"><div><div class="empty"><div class="ill">${icon('shield')}</div>
        <h2>SpeicherPilot startet mit Administratorrechten neu</h2><p>Ein neues Fenster öffnet sich gleich. Dieses Fenster kannst du schließen.</p></div></div></div>`);
      setTimeout(() => window.close(), 2500);
    } catch (e) { toast('err', 'Fehler', e.message); }
  },
};
document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-act]');
  if (!el || el.disabled) return;
  const fn = ACTIONS[el.dataset.act];
  if (fn) { e.preventDefault(); Promise.resolve(fn(el.dataset, e)).catch((err) => toast('err', 'Fehler', err.message)); }
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && D.open && !$('#modal').classList.contains('show')) closeDrawer();
});
document.addEventListener('change', async (e) => {
  const t = e.target;
  if (t.dataset.chk) {
    const src = t.dataset.chk, sel = SEL(src);
    const list = LIST(src);
    const it = list.find((x) => x.path === t.dataset.path);
    if (t.checked && it) sel.set(it.path, it); else sel.delete(t.dataset.path);
    t.closest('.row').classList.toggle('sel', t.checked);
    renderActionbar();
  } else if (t.dataset.opt === 'hideKeep') {
    S.uOpt.hideKeep = t.checked; renderUnused();
  } else if (t.dataset.opt === 'basis') {
    S.uOpt.basis = t.checked ? 'used' : 'modified'; await loadUnused(); renderUnused(); renderNav();
  }
});

/* ------------------------------------------------------------------ Lebenszeichen */
setInterval(() => api('/api/heartbeat', {}).catch(() => {}), 10000);
window.addEventListener('pagehide', () => navigator.sendBeacon(`/api/bye?t=${encodeURIComponent(TOKEN)}`));

/* ------------------------------------------------------------------ Start */
async function init() {
  renderNav();
  renderThemeSwitch();
  try {
    const [info, drives, status] = await Promise.all([api('/api/info'), api('/api/drives'), api('/api/status')]);
    S.info = info; S.drives = drives.drives; S.recycle = drives.recycleBin; S.scan = status;
    S.sessionFreed = info.sessionFreed; setSessionFreed(info.sessionFreed);
    if (status.roots?.length) status.roots.forEach((r) => S.scope.add(r));
    else S.drives.filter((d) => d.type === 'fixed').forEach((d) => S.scope.add(d.root));
    status.roots?.forEach((r) => { if (!S.drives.some((d) => d.root === r) && r !== info.home) S.custom.push(r); });
    renderBin();
    if (status.state === 'done') await Promise.all([loadUnused(), loadLarge()]);
    if (status.state === 'scanning') pollScan();
  } catch (e) {
    toast('err', 'Verbindung fehlgeschlagen', e.message);
  }
  go('overview');
  loadJunk();
  loadGames();
  api('/api/heartbeat', {}).catch(() => {});
}
init();
