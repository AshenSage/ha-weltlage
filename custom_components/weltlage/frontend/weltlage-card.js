import './weltlage-globe.js?v=1.1.2';
/* Weltlage 1.1.2 — mobile-first Home Assistant card with locally bundled globe libraries. */
export const VERSION = '1.1.2';
const REGIONS = { world: 'Welt', chrs: 'CH / RS', europa: 'Europa', balkan: 'Balkan', ch: 'Schweiz', rs: 'Serbien' };
const TOPICS = { all: 'Alle Themen', politik: 'Politik & Diplomatie', konflikte: 'Konflikte', energie: 'Energie & Handel', wirtschaft: 'Wirtschaft', natur: 'Naturereignisse', technik: 'Technik' };
const LANGUAGES = { de: 'Deutsch', en: 'Englisch', sr: 'Serbisch' };
const SHAPES = {
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c5 5 5 13 0 18-5-5-5-13 0-18M5 7h14M5 17h14"/>',
  news: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 7h6M9 11h6M9 15h3M9 18h6"/>',
  alert: '<path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5M12 17v.1"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/>',
  refresh: '<path d="M20 8a8 8 0 1 0 0 8M20 3v5h-5"/>',
  arrow: '<path d="m9 5 7 7-7 7"/>',
  external: '<path d="M14 3h7v7M10 14 21 3M10 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1v-6"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  map: '<path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2V5ZM9 3v16M15 5v16"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
};
const icon = (name, cls = '') => `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${SHAPES[name] || SHAPES.globe}</svg>`;
export const escapeHTML = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export function safeLink(value) {
  try { const u = new URL(String(value)); return ['https:', 'http:'].includes(u.protocol) && !u.username && !u.password ? u.href : ''; } catch { return ''; }
}
export function age(value, now = Date.now()) {
  const ts = typeof value === 'number' ? value * 1000 : Date.parse(value);
  if (!Number.isFinite(ts)) return 'Datum fehlt';
  const mins = Math.floor((now - ts) / 60000);
  if (mins < -5) return 'Zeitangabe prüfen';
  if (mins < 1) return 'gerade eben';
  if (mins < 60) return `vor ${mins} Min.`;
  if (mins < 1440) return `vor ${Math.floor(mins / 60)} h`;
  return `vor ${Math.floor(mins / 1440)} Tagen`;
}
export function effectiveSourceStatus(s, now = Date.now()) {
  if (!s.last_success) return 'unavailable';
  if (s.status === 'error') return 'error';
  const elapsed = now - Date.parse(s.last_success);
  return !Number.isFinite(elapsed) || elapsed < -300000 || elapsed > Math.max(Number(s.interval || 900) * 2, 900) * 1000 ? 'stale' : 'ok';
}
export function regionMatches(regions, wanted) {
  if (wanted === 'world') return true;
  return wanted === 'chrs' ? ['ch', 'rs'].some(x => (regions || []).includes(x)) : (regions || []).includes(wanted);
}
export function filterArticles(articles, region, topic, hours, now = Date.now(), options = {}) {
  const words = String(options.query || '').trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  return (articles || []).filter(a => {
    const ts = a.published ?? a.first_seen;
    const text = [a.title, a.summary, ...(a.sources || []).map(s => s.name)].join(' ').toLocaleLowerCase();
    return Number.isFinite(ts) && now / 1000 - ts <= hours * 3600 && ts <= now / 1000 + 300 && regionMatches(a.regions, region)
      && (topic === 'all' || (a.topics || [a.category]).includes(topic))
      && (!options.language || a.language === options.language)
      && (!options.source || (a.sources || []).some(s => s.name === options.source))
      && words.every(word => text.includes(word));
  });
}
const array = v => Array.isArray(v) ? v : v == null ? [] : [v];
const capTime = value => typeof value === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/i.test(value) ? Date.parse(value) : NaN;
export function capAlerts(states, cfg, now = Date.now()) {
  const updated = states[cfg.alert_updated_entity];
  const counter = states[cfg.alert_count_entity];
  const last = capTime(updated?.state);
  const raw = Number(counter?.state);
  const rawValid = counter && !['unknown', 'unavailable', ''].includes(counter.state) && Number.isFinite(raw);
  const found = [];
  let incomplete = false;
  for (const [eid, state] of Object.entries(states)) {
    const a = state.attributes || {};
    if (!a.identifier || (!a.provider && !eid.includes('cap_alert'))) continue;
    if (cfg.alert_entities?.length && !cfg.alert_entities.includes(eid)) continue;
    const codes = Object.values(a.geocodes || {}).flatMap(array);
    if (cfg.alert_areas?.length && !cfg.alert_areas.some(code => codes.includes(code))) continue;
    found.push([eid, state]);
  }
  const active = [], upcoming = [], seen = new Set();
  for (const [eid, state] of found) {
    const a = state.attributes;
    if (state.state === 'unavailable' || a.stale) { incomplete = true; continue; }
    if ((a.status || 'Actual').toLowerCase() !== 'actual' || ['cancel', 'ack', 'error'].includes((a.msg_type || '').toLowerCase())) continue;
    const expires = capTime(a.expires);
    const onset = capTime(a.onset || a.effective || a.sent);
    if (!Number.isFinite(expires) || !Number.isFinite(onset)) { incomplete = true; continue; }
    if (expires <= now) continue;
    const awareness = parseInt(String(array(a.parameters?.awareness_level)[0] || ''), 10);
    // Meteoalarm green/Minor entries mean "no special awareness" and are not warnings.
    const severity = String(a.severity || a.severity_normalized || state.state).toLowerCase();
    const levels = { minor: 0, moderate: 1, severe: 2, extreme: 3 };
    const levelKnown = awareness >= 1 && awareness <= 4 || Object.hasOwn(levels, severity);
    if (!levelKnown) { incomplete = true; continue; }
    let level = awareness >= 1 && awareness <= 4 ? awareness - 1 : levels[severity];
    if (level < 1) continue;
    level = Math.min(3, level);
    if (seen.has(a.identifier)) continue;
    seen.add(a.identifier);
    const types = { 1: 'Wind', 2: 'Schnee / Eis', 3: 'Gewitter', 4: 'Nebel', 5: 'Hitze', 6: 'Tiefe Temperatur', 7: 'Küste', 8: 'Waldbrand', 9: 'Lawinen', 10: 'Regen', 11: 'Hochwasser', 12: 'Regen / Hochwasser' };
    const type = parseInt(String(array(a.parameters?.awareness_type)[0] || ''), 10);
    const item = { eid, id: a.identifier, title: types[type] || a.event_alt || a.event || a.headline || 'Wetterwarnung', original: a.headline || a.event || '', area: a.area_desc || cfg.alert_label, level, onset, expires, url: safeLink(a.web), description: String(a.description_alt || a.description || '').slice(0, 600) };
    (onset > now ? upcoming : active).push(item);
  }
  active.sort((a, b) => b.level - a.level || a.expires - b.expires);
  upcoming.sort((a, b) => a.onset - b.onset);
  const configured = Boolean(counter || updated || found.length);
  const stale = !Number.isFinite(last) || now - last > (cfg.alert_max_age || 90) * 60000 || last > now + 300000;
  const partial = incomplete || (rawValid && raw > 0 && !found.length) || (!rawValid && !found.length);
  return { active, upcoming, status: !configured ? 'not_configured' : stale ? 'stale' : partial ? 'partial' : 'ok', last_success: Number.isFinite(last) ? new Date(last).toISOString() : null };
}

const STYLE = `
:host{display:block;--w-bg:#0b141d;--w-panel:#111f2b;--w-line:#263c4e;--w-text:#edf4fa;--w-muted:#97adbf;--w-cyan:#49d5df;--w-amber:#ffc66b;--w-red:#fb838c;font-family:var(--paper-font-body1_-_font-family,system-ui),sans-serif;color:var(--w-text);container-type:inline-size}
*{box-sizing:border-box}ha-card{display:block;background:var(--w-bg);color:var(--w-text);border:1px solid var(--w-line);border-radius:22px;padding:20px;overflow:hidden;box-shadow:0 10px 38px #0002}button,select,a{font:inherit}button,select{color:inherit}button{cursor:pointer}button:disabled{opacity:.45;cursor:wait}button:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible{outline:2px solid var(--w-cyan);outline-offset:3px}button,a,summary,select{-webkit-tap-highlight-color:transparent}button{min-height:46px;border:1px solid var(--w-line);border-radius:12px;background:var(--w-panel);padding:10px 14px}.icon{height:23px;width:23px;flex:none;vertical-align:middle}.muted{color:var(--w-muted)}.small{font-size:13px;line-height:1.5}.cyan{color:var(--w-cyan)}.amber{color:var(--w-amber)}.red{color:var(--w-red)}.eyebrow{font:600 11px/1.5 ui-monospace,SFMono-Regular,monospace;letter-spacing:1.5px;color:var(--w-cyan)}.header{display:flex;gap:12px;align-items:center;justify-content:space-between;margin-bottom:12px}.brand{display:flex;align-items:center;gap:10px}.brand>.icon{width:32px;height:32px;color:var(--w-cyan)}h1{font-size:27px;line-height:1.2;margin:0;font-weight:750;letter-spacing:-.6px}.icon-button{width:46px;padding:0;display:grid;place-items:center}.status-line{font-size:13px;color:var(--w-muted);display:flex;align-items:center;gap:7px;min-height:22px;margin-bottom:16px}.dot{width:7px;height:7px;border-radius:50%;display:inline-block;background:var(--w-cyan);flex:none}.dot.warning{background:var(--w-amber)}.filters{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:12px}.filters button,.filters select{font-size:14px;font-weight:650;min-width:0}.filters button.selected{background:#153941;border-color:var(--w-cyan);color:var(--w-cyan)}select{min-height:46px;background:var(--w-panel);border:1px solid var(--w-line);border-radius:12px;padding:10px 8px;width:100%;max-width:100%}option{background:#111f2b;color:var(--w-text)}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}.metric{padding:14px;background:linear-gradient(135deg,#172a38,#101d28);border:1px solid var(--w-line);border-radius:14px;display:flex;gap:12px;align-items:center;min-width:0}.metric .icon{color:var(--w-cyan);width:27px;height:27px}.metric:nth-child(2) .icon{color:var(--w-amber)}.metric strong{display:block;font-size:26px;line-height:1.1}.metric span{font-size:12px;color:var(--w-muted);line-height:1.3;display:block;margin-top:4px}.alert-panel{padding:14px 15px;border:1px solid #755b32;background:#2b251b;border-radius:14px;margin-bottom:18px}.alert-panel.neutral{border-color:var(--w-line);background:var(--w-panel)}.alert-title{display:flex;align-items:center;gap:9px;font-size:15px;font-weight:650;margin-bottom:5px}.alert-title .icon{color:var(--w-amber)}.alert-row{margin-top:10px;padding-top:10px;border-top:1px solid #ffffff12;line-height:1.5}.alert-row a{color:var(--w-text)}.alert-row strong{font-size:15px}.alert-row p{margin:6px 0;font-size:14px;line-height:1.6}.level{font:600 10px/1.5 ui-monospace,monospace;letter-spacing:.5px;border:1px solid #ffffff30;border-radius:6px;padding:2px 5px;display:inline-block;margin-right:5px}.layout{display:grid;grid-template-columns:minmax(0,1fr);gap:16px}.news-pane,.side-pane{min-width:0}.section-header{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:4px 0 12px}.section-header h2{font-size:14px;letter-spacing:1px;margin:0;text-transform:uppercase}.section-header select{width:81px;min-height:44px;padding:5px 8px;font-size:13px}.topic-select{margin-bottom:12px;min-height:44px;font-size:14px}.news-list{display:grid;gap:10px}.news{border:1px solid var(--w-line);border-radius:15px;background:var(--w-panel);overflow:hidden}.news>summary{list-style:none;cursor:pointer;padding:16px;min-height:110px}.news>summary::-webkit-details-marker{display:none}.news h3{font-size:17px;font-weight:650;line-height:1.45;margin:7px 0 8px;overflow-wrap:anywhere}.news .summary-head{display:flex;justify-content:space-between;align-items:center;gap:10px}.news .meta{font-size:12px;color:var(--w-muted);display:flex;gap:6px;flex-wrap:wrap;align-items:center}.news .badge{font-size:11px;display:inline-flex;align-items:center;margin-top:9px;padding:3px 7px;border:1px solid var(--w-line);border-radius:7px;color:var(--w-muted)}.news .badge.cached{color:var(--w-amber);border-color:#755b32}.news-body{padding:0 16px 16px;border-top:1px solid #ffffff0a}.news-body p{font-size:15px;line-height:1.7;margin:13px 0;overflow-wrap:anywhere}.news-body a,.source-link{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--w-line);background:#172938;color:var(--w-text);padding:11px 12px;min-height:44px;border-radius:10px;text-decoration:none;margin:4px 5px 0 0;font-size:13px}.more{width:100%;margin-top:12px;color:var(--w-cyan);font-size:14px}.empty{border:1px dashed var(--w-line);border-radius:14px;padding:20px 16px;color:var(--w-muted);font-size:14px;line-height:1.6}.empty strong{display:block;color:var(--w-text);margin-bottom:5px}.panel{background:var(--w-panel);border:1px solid var(--w-line);border-radius:15px;margin-bottom:14px;overflow:hidden}.panel>summary{list-style:none;display:flex;gap:10px;align-items:center;justify-content:space-between;cursor:pointer;padding:16px;min-height:62px}.panel>summary::-webkit-details-marker{display:none}.panel-title{display:flex;gap:10px;align-items:center}.panel-title>.icon{color:var(--w-cyan)}.panel-title strong{font-size:15px;font-weight:650}.panel-body{padding:0 15px 15px}.sources-list{display:grid;gap:1px}.source-row{padding:12px 0;border-top:1px solid var(--w-line);font-size:13px;line-height:1.5}.source-row>div:first-child{display:flex;justify-content:space-between;gap:8px;align-items:start}.source-row .source-name{overflow-wrap:anywhere}.source-row .source-state{white-space:nowrap;font-size:12px}.hazard{padding:12px 0;border-top:1px solid var(--w-line);font-size:14px;line-height:1.6;overflow-wrap:anywhere}.hazard a{color:var(--w-text);text-decoration:none;display:block;min-height:44px}.map-open{width:100%;padding:17px;display:flex;align-items:center;justify-content:space-between;border:0;background:linear-gradient(135deg,#183343,#10202d);border-radius:0;text-align:left;min-height:96px}.map-open>.icon{width:31px;height:31px;color:var(--w-cyan)}.map-open strong{font-size:16px;display:block;margin-bottom:5px}.map-note{padding:0 16px 14px;color:var(--w-muted);font-size:12px;line-height:1.6}.map-note a{color:var(--w-cyan)}.intel-link{display:flex;align-items:center;justify-content:space-between;gap:12px;text-decoration:none;color:var(--w-text);padding:16px;min-height:62px}.intel-link strong{font-size:15px}.footnote{font-size:11px;color:var(--w-muted);line-height:1.6;margin:4px 0 0}.notice{border:1px solid #755b32;border-radius:12px;color:var(--w-amber);padding:13px 14px;line-height:1.6;font-size:14px;margin-bottom:16px}.loading .icon{animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}@media(prefers-reduced-motion:reduce){.loading .icon{animation:none}}
[hidden]{display:none!important}.status-line{flex-wrap:wrap}.status-text{flex:1;min-width:140px}.version-chip{font:500 10px/1.5 ui-monospace,monospace;border:1px solid var(--w-line);border-radius:6px;padding:2px 5px;white-space:nowrap}.version-info{padding:12px 0;border-top:1px solid var(--w-line)}.news .eyebrow{font-size:10px;letter-spacing:.6px}.news.compact>summary{padding:13px 14px;min-height:0}.news.compact h3{font-size:16px;line-height:1.4;margin:5px 0 7px}.news.compact:not([open]) h3{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;overflow:hidden}.news[open] .summary-head>.icon,.news-filters[open]>summary>.icon{transform:rotate(90deg)}.news-search{font:inherit;font-size:16px;min-height:46px;width:100%;min-width:0;border:1px solid var(--w-line);border-radius:12px;background:var(--w-panel);color:var(--w-text);padding:10px 12px;margin:0 0 8px}.news-search::placeholder{color:var(--w-muted)}.news-search:focus-visible{outline:2px solid var(--w-cyan);outline-offset:2px}.news-filters{margin-bottom:8px}.news-filters>summary{display:flex;justify-content:space-between;align-items:center;list-style:none;cursor:pointer;min-height:44px;font-size:12px;color:var(--w-muted);gap:8px}.news-filters>summary::-webkit-details-marker{display:none}.news-filters .icon{width:18px;height:18px}.filter-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 0 10px}.filter-grid label{min-width:0;font-size:12px;color:var(--w-muted)}.filter-grid select{font-size:13px;color:var(--w-text);margin-top:5px}.news-results{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:4px 8px;margin:0 0 10px}.news-count{font-size:11px;color:var(--w-muted)}.news-results button{font-size:12px;min-height:44px;padding:8px;color:var(--w-cyan);background:transparent;border:0}

dialog{max-width:none;width:100%;height:100dvh;max-height:none;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px);margin:0;inset:0;background:var(--w-bg);color:var(--w-text);border:0;overflow:hidden}dialog[open]{display:flex;flex-direction:column}.dialog-head,.map-filters,.dialog-note{flex:none}.iframe-holder{flex:1;min-height:0}dialog::backdrop{background:#000a}.dialog-head{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;gap:10px}.dialog-head strong{font-size:17px}.map-filters{display:flex;gap:8px;padding:0 14px 10px}.map-filters button{flex:1;font-size:13px}.map-filters .selected{border-color:var(--w-cyan);color:var(--w-cyan)}iframe{display:block;width:100%;height:100%;border:0;background:#101c27}.dialog-note{padding:10px 14px;font-size:12px;color:var(--w-muted);line-height:1.5}
@container(min-width:760px){.layout{grid-template-columns:minmax(0,1.45fr) minmax(0,1fr);gap:20px}.header h1{font-size:32px}.filters{max-width:540px}.metrics{max-width:540px}.alert-panel{margin-bottom:20px}}@container(max-width:370px){ha-card{padding:14px}.metric{padding:12px;gap:8px}.metric .icon{width:22px;height:22px}h1{font-size:25px}.news>summary{padding:14px}.news h3{font-size:16px}.filters{gap:6px}.filters button{padding:10px 8px}.metric span{font-size:11px}}
`;

export class WeltlageCard extends (globalThis.HTMLElement || class {}) {
  static getConfigElement() { return document.createElement('weltlage-card-editor'); }
  static getStubConfig() { return { type: 'custom:weltlage-card', title: 'Weltlage' }; }
  getCardSize() { return 12; }
  setConfig(config) {
    this._config = { title: 'Weltlage', region: 'world', max_items: 3, compact_news: true, show_map: true, show_globe: true, alert_count_entity: 'sensor.cap_alerts_wmo_alert_count', alert_updated_entity: 'sensor.cap_alerts_wmo_last_updated', alert_areas: ['RS010'], alert_label: 'Serbien · Šumadija', alert_max_age: 90, ...config };
    if (!REGIONS[this._config.region]) this._config.region = 'world';
    if (typeof this._config.alert_areas === 'string') this._config.alert_areas = this._config.alert_areas.split(',').map(s => s.trim()).filter(Boolean);
    this._region = this._config.region;
    this._topic = 'all'; this._hours = 24; this._limit = Math.max(1, Math.min(12, Number(this._config.max_items) || 3));
    this._query = ''; this._language = ''; this._source = ''; clearTimeout(this._searchTimer);
    this._lastNewsKey = null;
    this._init(); this._render();
  }
  set hass(hass) {
    this._hass = hass;
    if (!this._config) return;
    const state = this._state();
    const caps = Object.entries(hass.states).filter(([id, s]) => id === this._config.alert_count_entity || id === this._config.alert_updated_entity || s.attributes?.identifier && (s.attributes?.provider || id.includes('cap_alert'))).map(([id, s]) => [id, s]);
    const same = this._lastState === state && caps.length === this._lastCaps?.length && caps.every(([id, s], i) => this._lastCaps[i][0] === id && this._lastCaps[i][1] === s);
    if (!same) { this._lastState = state; this._lastCaps = caps; this._render(); }
  }
  connectedCallback() { if (!this._clock) this._clock = setInterval(() => this._render(), 60000); this._render(); }
  disconnectedCallback() { clearInterval(this._clock); clearTimeout(this._searchTimer); this._clock = null; this.shadowRoot?.querySelector('dialog')?.close(); this._clearMap(); }
  _state() { return this._hass?.states[this._config?.entity] || (!this._config?.entity && Object.values(this._hass?.states || {}).find(s => s.attributes?.integration === 'weltlage' && Array.isArray(s.attributes?.articles))); }
  _init() {
    if (this.shadowRoot) return;
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `<style>${STYLE}</style><ha-card>
      <div class="header"><div class="brand">${icon('globe')}<div><div class="eyebrow">GLOBAL / CH / RS</div><h1></h1></div></div><button class="icon-button" data-action="refresh" aria-label="Daten aktualisieren">${icon('refresh')}</button></div>
      <div class="status-line" aria-live="polite"></div><div class="setup"></div>
      <div class="globe-container"><weltlage-globe></weltlage-globe></div><div class="filters"><button data-region="world">Welt</button><button data-region="chrs">CH / RS</button><select aria-label="Weitere Regionen" class="region-select"><option value="">Weitere</option>${Object.entries(REGIONS).filter(([k]) => !['world', 'chrs'].includes(k)).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></div>
      <div class="metrics"></div><div class="alerts"></div>
      <div class="layout"><section class="news-pane"><div class="section-header"><h2>Heute im Fokus</h2><select class="period-select" aria-label="Zeitraum"><option value="24">24 h</option><option value="48">48 h</option><option value="72">72 h</option></select></div><select class="topic-select" aria-label="Thema">${Object.entries(TOPICS).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select><input class="news-search" type="search" aria-label="Meldungen durchsuchen" placeholder="Meldungen durchsuchen" maxlength="160"><details class="news-filters"><summary><span class="filter-summary">Sprache & Quelle</span>${icon('arrow')}</summary><div class="filter-grid"><label>Sprache<select class="language-select" aria-label="Sprache"></select></label><label>Quelle<select class="source-select" aria-label="Nachrichtenquelle"></select></label></div></details><div class="news-results"><span class="news-count" role="status"></span><button data-action="reset-news" hidden>Filter zurücksetzen</button></div><div class="news-list"></div><div class="news-more"></div><p class="footnote">Medienberichte · nach Zeit sortiert · mehrere Themen nach Stichworten möglich</p></section>
      <aside class="side-pane"><div class="map-container"><div class="panel"><button class="map-open" data-action="map"><div><strong>Weltkarte öffnen</strong><span class="small muted">Konflikte · Erdbeben · Wetter</span></div>${icon('map')}</button><div class="map-note">World Monitor · Gratis-Karte, Abruf stündlich.<br>Wird erst beim Öffnen geladen.</div></div></div><details class="panel hazards-panel"><summary><div class="panel-title">${icon('globe')}<div><strong>Naturereignisse</strong><div class="small muted hazard-summary"></div></div></div>${icon('arrow')}</summary><div class="panel-body hazards-list"></div></details>
      <details class="panel sources-panel"><summary><div class="panel-title">${icon('clock')}<div><strong>Quellen & Datenalter</strong><div class="small muted sources-summary"></div></div></div>${icon('arrow')}</summary><div class="panel-body sources-list"></div></details><div class="intel-container"></div><p class="footnote">Nachrichten sind Medienberichte. Naturereignisse und Warnungen werden separat geführt.</p></aside></div>
    </ha-card><dialog aria-label="Weltkarte"><div class="dialog-head"><strong>Weltkarte</strong><button class="icon-button" data-action="close-map" aria-label="Karte schliessen">${icon('close')}</button></div><div class="map-filters"><button data-map-region="world">Welt</button><button data-map-region="europa">Europa</button><button data-map-region="balkan">Balkan</button></div><div class="iframe-holder"></div><div class="dialog-note">World Monitor · Abruf stündlich. Quellen können verzögert oder unvollständig sein.</div></dialog>`;
    this.shadowRoot.addEventListener('click', e => this._click(e));
    this.shadowRoot.addEventListener('intel-request', e => this._fetchIntel(e.detail));
    this.shadowRoot.addEventListener('change', e => {
      if (e.target.matches('.region-select') && e.target.value) { this._region = e.target.value; this._resetLimit(); }
      if (e.target.matches('.period-select')) { this._hours = Number(e.target.value); this._resetLimit(); }
      if (e.target.matches('.topic-select')) { this._topic = e.target.value; this._resetLimit(); }
      if (e.target.matches('.language-select')) { this._language = e.target.value; this._resetLimit(); }
      if (e.target.matches('.source-select')) { this._source = e.target.value; this._resetLimit(); }
    });
    this.shadowRoot.addEventListener('input', e => {
      if (!e.target.matches('.news-search')) return;
      this._query = e.target.value.slice(0, 160); clearTimeout(this._searchTimer);
      this._searchTimer = setTimeout(() => this._resetLimit(), 180);
    });
    this.shadowRoot.querySelector('dialog').addEventListener('close', () => { if (!this.shadowRoot.querySelector('dialog').open) this._clearMap(); });
  }
  _resetLimit() { this._limit = Math.max(1, Math.min(12, Number(this._config.max_items) || 3)); this._render(); }
  _click(e) {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.region) { this._region = b.dataset.region; this._resetLimit(); }
    if (b.dataset.mapRegion) this._loadMap(b.dataset.mapRegion);
    if (b.dataset.action === 'map') { const d = this.shadowRoot.querySelector('dialog'); if (!d.open) d.showModal(); this._loadMap(['europa', 'balkan'].includes(this._region) ? this._region : ['ch', 'rs', 'chrs'].includes(this._region) ? 'europa' : 'world'); }
    if (b.dataset.action === 'close-map') this.shadowRoot.querySelector('dialog').close();
    if (b.dataset.action === 'more-news') { this._limit += 6; this._render(); }
    if (b.dataset.action === 'reset-news') { clearTimeout(this._searchTimer); this._query = ''; this._language = ''; this._source = ''; this._topic = 'all'; this._resetLimit(); }
    if (b.dataset.action === 'refresh') this._refresh(b);
  }
  _loadMap(region) {
    const views = { world: ['20,0', 1], europa: ['49,15', 3], balkan: ['44,20', 5] };
    const [center, zoom] = views[region] || views.world;
    const url = new URL('https://www.worldmonitor.app/embed');
    for (const [k, v] of Object.entries({ layers: 'conflicts,earthquakes,weather', center, zoom, theme: 'dark', variant: 'full' })) url.searchParams.set(k, v);
    let frame = this.shadowRoot.querySelector('iframe');
    if (!frame) { frame = document.createElement('iframe'); frame.title = 'World Monitor Weltkarte'; frame.referrerPolicy = 'strict-origin-when-cross-origin'; frame.setAttribute('allow', 'fullscreen'); this.shadowRoot.querySelector('.iframe-holder').append(frame); }
    if (frame.src !== url.href) frame.src = url.href;
    for (const b of this.shadowRoot.querySelectorAll('[data-map-region]')) b.classList.toggle('selected', b.dataset.mapRegion === region);
  }
  _clearMap() { this.shadowRoot?.querySelector('.iframe-holder')?.replaceChildren(); }
  async _refresh(b) {
    const refresh = this._config.refresh_entity || Object.entries(this._hass?.states || {}).find(([id, s]) => id.startsWith('button.') && s.attributes?.integration === 'weltlage' && s.attributes?.role === 'refresh')?.[0];
    if (!refresh || !this._hass) return;
    this._refreshing = true; b.disabled = true; b.classList.add('loading');
    try { await this._hass.callService('button', 'press', { entity_id: refresh }); }
    catch { this.shadowRoot.querySelector('.setup').innerHTML = '<div class="notice">Aktualisieren fehlgeschlagen. Verbindung zu Home Assistant prüfen.</div>'; }
    finally { this._refreshing = false; b.disabled = false; b.classList.remove('loading'); }
  }
  _date(ms) {
    try { return new Intl.DateTimeFormat('de-CH', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', timeZone: this._hass?.config?.time_zone || 'Europe/Belgrade' }).format(ms); } catch { return new Date(ms).toLocaleString('de-CH'); }
  }
  _render() {
    if (!this.shadowRoot || !this._config) return;
    const root = this.shadowRoot, state = this._state(), data = state?.attributes || {}, now = Date.now(), sources = data.sources || [];
    root.querySelector('h1').textContent = this._config.title;
    const good = sources.filter(s => effectiveSourceStatus(s, now) === 'ok').length;
    const staleCount = sources.length - good;
    const statusText = !state ? 'Integration noch nicht eingerichtet' : !sources.length ? 'Warte auf den ersten Abruf' : !good ? 'Keine aktuellen Quellen' : staleCount ? `${good} / ${sources.length} Quellen aktuell · teilweise Daten` : `${good} / ${sources.length} Quellen aktuell`;
    root.querySelector('.status-line').innerHTML = `<span class="dot ${staleCount || !sources.length ? 'warning' : ''}"></span><span class="status-text">${escapeHTML(statusText)}</span><span class="version-chip">Karte ${VERSION}</span>`;
    const mismatch = data.version && data.version !== VERSION;
    root.querySelector('.setup').innerHTML = !state ? '<div class="notice">Unter Einstellungen → Geräte & Dienste die Integration «Weltlage» hinzufügen. Die Karte findet das Lagebild danach automatisch.</div>' : state.state === 'unavailable' ? '<div class="notice">Weltlage ist nicht verfügbar. Gespeicherte Daten können veraltet sein.</div>' : mismatch ? `<div class="notice">Versionen unterscheiden sich: Karte ${VERSION}, Integration ${escapeHTML(data.version)}. In HACS Weltlage erneut herunterladen, Home Assistant neu starten und die App neu laden.</div>` : '';
    root.querySelector('[data-action="refresh"]').disabled = this._refreshing || !this._hass || !state;
    for (const b of root.querySelectorAll('[data-region]')) b.classList.toggle('selected', b.dataset.region === this._region);
    root.querySelector('.region-select').value = ['world', 'chrs'].includes(this._region) ? '' : this._region;
    root.querySelector('.topic-select').value = this._topic;
    root.querySelector('.period-select').value = String(this._hours);
    const cap = capAlerts(this._hass?.states || {}, this._config, now);
    this._renderNewsFilters(data.articles || []);
    const articles = filterArticles(data.articles, this._region, this._topic, this._hours, now, {query: this._query, language: this._language, source: this._source});
    const datedCount = articles.filter(a => a.published != null).length;
    const newsAvailable = articles.length > 0 || sources.some(s => s.kind === 'news' && effectiveSourceStatus(s, now) === 'ok');
    root.querySelector('.metrics').innerHTML = `<div class="metric">${icon('news')}<div><strong>${newsAvailable ? datedCount : '—'}</strong><span>Meldungen im Filter · ${this._hours} h</span></div></div><div class="metric">${icon('alert')}<div><strong>${cap.status === 'ok' ? cap.active.length : '—'}</strong><span>Warnungen · ${escapeHTML(this._config.alert_label)}</span></div></div>`;
    this._renderAlerts(cap, now);
    this._renderGlobe(data, cap);
    this._renderNews(articles, sources, now);
    root.querySelector('.map-container').hidden = !this._config.show_map;
    this._renderSources(sources, cap, now);
    const hazards = (data.hazards || []).filter(h => regionMatches(h.regions, this._region) && (h.expires == null || h.expires * 1000 > now));
    const hGood = sources.filter(s => s.kind !== 'news' && effectiveSourceStatus(s, now) === 'ok').length;
    root.querySelector('.hazard-summary').textContent = `${hazards.length} im Filter · USGS / GDACS`;
    root.querySelector('.hazards-list').innerHTML = `${hGood < 2 ? '<p class="small amber">Naturereignisdaten sind teilweise oder vollständig veraltet.</p>' : ''}<p class="small muted">USGS: Erdbeben M ≥ 4.5, letzte 24 h. GDACS: Orange / Rot, ohne doppelte Erdbeben.</p>${hazards.slice(0, 20).map(h => { const url = safeLink(h.url); return `<div class="hazard">${url ? `<a href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">` : '<div>'}<strong>${escapeHTML(h.title)}</strong>${url ? ` ${icon('external')}</a>` : '</div>'}<div class="small muted">${escapeHTML(h.source)} · ${escapeHTML(age(h.published, now))}${['orange', 'red'].includes(h.severity) ? ` · ${h.severity === 'red' ? 'Rot' : 'Orange'}` : ''}</div></div>`; }).join('') || '<p class="small muted">Keine Ereignisse im gewählten Filter erfasst.</p>'}`;
    const intel = safeLink(this._config.intel_url);
    root.querySelector('.intel-container').innerHTML = intel ? `<div class="panel"><a class="intel-link" href="${escapeHTML(intel)}" target="_blank" rel="noopener noreferrer"><div><strong>3D Intel öffnen</strong><div class="small muted">God’s Eye · separate Ansicht</div></div>${icon('external')}</a></div>` : '';
  }
  _renderGlobe(data, cap) {
    const holder = this.shadowRoot.querySelector('.globe-container');
    const visible = this._config.show_globe !== false;
    holder.hidden = !visible;
    let globe = holder.querySelector('weltlage-globe');
    if (!visible) { globe?.remove(); return; }
    if (!globe) { globe = document.createElement('weltlage-globe'); holder.append(globe); }
    const capPoints = (this._config.alert_areas || []).includes('RS010') ? [...cap.active, ...cap.upcoming].map(a => ({ id: a.id, name: a.title + (a.onset > Date.now() ? ' · kommend' : ''), latitude: 44.3, longitude: 20.7, source: 'CAP · Šumadija', url: a.url, description: (cap.status !== 'ok' ? 'Datenstand prüfen. ' : '') + 'Gebietsmitte Šumadija, keine exakte Ereignisposition. ' + a.description })) : [];
    globe.payload = { hazards: data.hazards || [], intel: data.intel || {}, stale_sources: (data.sources || []).filter(s => effectiveSourceStatus(s) !== 'ok').map(s => s.id), cap: capPoints };
  }
  async _fetchIntel(detail) {
    const globe = this.shadowRoot.querySelector('weltlage-globe');
    if (!this._hass || !this._state()) { globe?.setBusy(detail.kind, false, 'Zuerst die Weltlage-Integration einrichten.'); return; }
    globe?.setBusy(detail.kind, true);
    try {
      await this._hass.callService('weltlage', 'fetch_intel', detail);
      const data = this._state()?.attributes || {};
      this._renderGlobe(data, capAlerts(this._hass.states || {}, this._config));
      globe?.setBusy(detail.kind, false, detail.kind === 'flights' ? 'Flugaufnahme angefordert. Neue Abfrage frühestens nach 60 Sekunden; beim Drehen bleibt die zuletzt geladene Region bestehen.' : 'Bahndaten angefordert. Erneuter Abruf frühestens nach zwei Stunden.');
    } catch { globe?.setBusy(detail.kind, false, 'Abruf fehlgeschlagen. Integration aktualisieren, HA neu starten und Verbindung prüfen.'); }
  }
  _renderAlerts(cap, now) {
    const opened = new Set([...this.shadowRoot.querySelectorAll('.alert-row[open]')].map(n => n.dataset.key));
    let heading, note, neutral = true;
    if (cap.status === 'not_configured') { heading = 'Regionale Warnungen'; note = 'CAP Alerts ist noch nicht verbunden. Der Warnstatus ist unbekannt.'; }
    else if (cap.status !== 'ok') { heading = 'Warnstatus prüfen'; note = cap.status === 'stale' ? 'CAP-Daten fehlen oder sind veraltet. Erfasste Warnungen unten können älter sein.' : 'CAP-Daten sind unvollständig. Eine Entwarnung ist nicht möglich.'; neutral = false; }
    else if (cap.active.length) { heading = `${cap.active.length} aktive ${cap.active.length === 1 ? 'Warnung' : 'Warnungen'}`; note = this._config.alert_label; neutral = false; }
    else if (cap.upcoming.length) { heading = `${cap.upcoming.length} kommende ${cap.upcoming.length === 1 ? 'Warnung' : 'Warnungen'}`; note = 'Aktuell keine gelben, orangen oder roten Warnungen.'; }
    else { heading = 'Keine besonderen Wetterwarnungen'; note = `${this._config.alert_label} · CAP zuletzt ${age(cap.last_success, now)}`; }
    const rows = [...cap.active.slice(0, 4), ...cap.upcoming.slice(0, 3)];
    this.shadowRoot.querySelector('.alerts').innerHTML = `<div class="alert-panel ${neutral ? 'neutral' : ''}"><div class="alert-title">${icon(cap.status === 'ok' && !cap.active.length ? 'check' : 'alert')}<span>${escapeHTML(heading)}</span></div><div class="small muted">${escapeHTML(note)}</div>${rows.map(a => `<details class="alert-row" data-key="${escapeHTML(a.id)}" ${opened.has(a.id) ? 'open' : ''}><summary><span class="level ${a.level === 3 ? 'red' : 'amber'}">${['', 'GELB', 'ORANGE', 'ROT'][a.level]}</span><strong>${escapeHTML(a.title)}</strong><div class="small muted">${a.onset > now ? 'Ab ' + this._date(a.onset) : 'Bis ' + this._date(a.expires)} · ${escapeHTML(a.area)}</div></summary><p>${escapeHTML(a.description)}</p>${a.url ? `<a class="source-link" href="${escapeHTML(a.url)}" target="_blank" rel="noopener noreferrer">Amtliche Meldung ${icon('external')}</a>` : ''}</details>`).join('')}${cap.active.length > 4 || cap.upcoming.length > 3 ? '<p class="small muted">Weitere Warnungen in den CAP-Alerts-Entitäten.</p>' : ''}</div>`;
  }
  _renderNewsFilters(articles) {
    const root = this.shadowRoot;
    const languages = [...new Set(articles.map(a => a.language).filter(Boolean).concat(this._language || []))].sort();
    const publishers = [...new Set(articles.flatMap(a => (a.sources || []).map(s => s.name)).filter(Boolean).concat(this._source || []))].sort();
    const key = JSON.stringify([languages, publishers]);
    if (key !== this._lastFilterKey) {
      root.querySelector('.language-select').innerHTML = '<option value="">Alle Sprachen</option>' + languages.map(value => `<option value="${escapeHTML(value)}">${escapeHTML(LANGUAGES[value] || value.toUpperCase())}</option>`).join('');
      root.querySelector('.source-select').innerHTML = '<option value="">Alle Quellen</option>' + publishers.map(value => `<option value="${escapeHTML(value)}">${escapeHTML(value)}</option>`).join('');
      this._lastFilterKey = key;
    }
    root.querySelector('.language-select').value = this._language;
    root.querySelector('.source-select').value = this._source;
    const input = root.querySelector('.news-search'); if (input.value !== this._query) input.value = this._query;
    root.querySelector('.filter-summary').textContent = [LANGUAGES[this._language] || this._language.toUpperCase(), this._source].filter(Boolean).join(' · ') || 'Sprache & Quelle';
    root.querySelector('[data-action="reset-news"]').hidden = !this._query.trim() && !this._language && !this._source && this._topic === 'all';
  }
  _renderNews(articles, sources, now) {
    const root = this.shadowRoot;
    const statusById = Object.fromEntries(sources.map(s => [s.id, effectiveSourceStatus(s, now)]));
    const visible = articles.slice(0, this._limit);
    const key = JSON.stringify([visible, statusById, this._region, this._topic, this._hours, this._config.compact_news]);
    const undated = articles.filter(a => a.published == null).length;
    root.querySelector('.news-count').textContent = `${articles.length} ${articles.length === 1 ? 'Meldung' : 'Meldungen'} im Filter${undated ? ` · ${undated} undatiert` : ''}`;
    if (key !== this._lastNewsKey) {
      const opened = new Set([...root.querySelectorAll('.news[open]')].map(n => n.dataset.key));
      root.querySelector('.news-list').innerHTML = visible.map(a => {
        const publisher = [...new Set((a.sources || []).map(s => s.name))].join(' · ');
        const cached = !(a.sources || []).some(s => statusById[s.id] === 'ok');
        const topics = [...new Set((a.topics?.length ? a.topics : [a.category]).map(t => TOPICS[t] || 'Nachrichten'))];
        return `<details class="news ${this._config.compact_news !== false ? 'compact' : ''}" data-key="${escapeHTML(a.id)}" ${opened.has(a.id) ? 'open' : ''}><summary><div class="summary-head"><span class="eyebrow">${escapeHTML(topics.slice(0, 2).join(' · '))}</span>${icon('arrow')}</div><h3>${escapeHTML(a.title)}</h3><div class="meta"><span>${escapeHTML(publisher)}</span><span>·</span><span class="article-age" data-published="${escapeHTML(a.published ?? '')}">${escapeHTML(age(a.published, now))}</span>${a.language ? `<span>· ${escapeHTML(a.language.toUpperCase())}</span>` : ''}</div>${cached ? '<span class="badge cached">Gespeichert · Quelle nicht aktuell</span>' : ''}</summary><div class="news-body">${topics.length > 2 ? `<p class="small muted">Themen: ${escapeHTML(topics.join(' · '))}</p>` : ''}<p>${escapeHTML(a.summary || 'Diese Quelle liefert keinen Kurztext. Öffne den Originalartikel.')}</p>${(a.sources || []).map(s => { const url = safeLink(s.url); return url ? `<a href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(s.name)} öffnen ${icon('external')}</a>` : ''; }).join('')}</div></details>`;
      }).join('') || `<div class="empty"><strong>Keine Meldungen im gewählten Filter</strong>${sources.some(s => s.kind === 'news' && effectiveSourceStatus(s, now) === 'ok') ? 'Suche, Sprache oder Quelle zurücksetzen; alternativ Zeitraum, Region oder Thema ändern.' : 'Die Nachrichtenquellen konnten noch nicht aktuell geladen werden. Prüfe Quellen & Datenalter.'}</div>`;
      this._lastNewsKey = key;
    } else {
      for (const el of root.querySelectorAll('.article-age')) el.textContent = age(el.dataset.published === '' ? null : Number(el.dataset.published), now);
    }
    root.querySelector('.news-more').innerHTML = articles.length > visible.length ? `<button class="more" data-action="more-news">Weitere Meldungen (${articles.length - visible.length})</button>` : '';
  }
  _renderSources(sources, cap, now) {
    const root = this.shadowRoot, outdated = sources.filter(s => effectiveSourceStatus(s, now) !== 'ok').length;
    const sum = root.querySelector('.sources-summary');
    sum.textContent = !sources.length ? 'Noch keine Daten' : outdated ? `${outdated} ${outdated === 1 ? 'Quelle' : 'Quellen'} nicht aktuell` : 'Alle Weltlage-Quellen aktuell';
    sum.classList.toggle('amber', outdated > 0);
    const labels = { ok: 'Aktuell', error: 'Abruf fehlgeschlagen', stale: 'Veraltet', unavailable: 'Nicht verfügbar' };
    root.querySelector('.sources-list').innerHTML = sources.map(s => {
      const status = effectiveSourceStatus(s, now);
      return `<div class="source-row"><div><strong class="source-name">${escapeHTML(s.name)}</strong><span class="source-state ${status === 'ok' ? 'cyan' : 'amber'}">${labels[status]}</span></div><div class="small muted">Erfolgreicher Abruf: ${s.last_success ? escapeHTML(age(s.last_success, now)) : 'noch keiner'}</div><div class="small muted">Neuester Eintrag: ${s.latest_entry ? escapeHTML(age(s.latest_entry, now)) : 'keine Zeitangabe'}</div>${s.error ? `<div class="small amber">${escapeHTML(s.error)}</div>` : ''}</div>`;
    }).join('') + `<div class="source-row"><div><strong>CAP · ${escapeHTML(this._config.alert_label)}</strong><span class="source-state ${cap.status === 'ok' ? 'cyan' : 'amber'}">${cap.status === 'ok' ? 'Aktuell' : cap.status === 'not_configured' ? 'Nicht verbunden' : 'Daten prüfen'}</span></div><div class="small muted">Erfolgreicher Abruf: ${cap.last_success ? escapeHTML(age(cap.last_success, now)) : 'noch keiner'}</div></div><div class="version-info small muted">Karte ${VERSION} · Integration ${escapeHTML(this._state()?.attributes?.version || 'unbekannt')}<br>Globus ${this._config.show_globe === false ? 'ausgeblendet · im Karteneditor aktivierbar' : 'aktiviert'}</div><p class="small muted">Ein älterer Artikel bedeutet keinen fehlgeschlagenen Abruf. Nachrichten bleiben in der Sprache ihrer Quelle.</p>`;
  }
}

export class WeltlageCardEditor extends (globalThis.HTMLElement || class {}) {
  setConfig(config) { this._config = { ...config }; this._render(); }
  set hass(hass) { this._hass = hass; }
  _render() {
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
      this.shadowRoot.addEventListener('change', e => this._change(e));
    }
    const fields = [ ['title', 'Titel', 'Weltlage'], ['entity', 'Lagebild-Entität (leer = automatisch)', ''], ['alert_count_entity', 'CAP-Zähler', 'sensor.cap_alerts_wmo_alert_count'], ['alert_updated_entity', 'CAP: letzter Abruf', 'sensor.cap_alerts_wmo_last_updated'], ['alert_areas', 'CAP-Gebietscodes, durch Komma getrennt', 'RS010'], ['alert_label', 'Name der Warnregion', 'Serbien · Šumadija'], ['intel_url', 'Optional: HTTPS-Adresse deiner God’s-Eye-Installation', ''] ];
    const get = (key, def) => key === 'alert_areas' ? (this._config[key] || [def]).join?.(', ') || this._config[key] : this._config[key] ?? def;
    this.shadowRoot.innerHTML = `<style>:host{display:block}label{display:block;margin:14px 0;font-size:14px}input,select{display:block;width:100%;box-sizing:border-box;min-height:44px;padding:10px;margin-top:6px;color:var(--primary-text-color);background:var(--card-background-color);border:1px solid var(--divider-color);border-radius:8px;font:inherit}input[type=checkbox]{display:inline;width:auto;min-height:0}p{font-size:13px;line-height:1.5;color:var(--secondary-text-color)}</style><p>Die Karte erkennt die Weltlage-Integration automatisch. CAP ist auf deine Warnregion Šumadija voreingestellt.</p>${fields.map(([key, name, def]) => `<label>${name}<input data-key="${key}" value="${escapeHTML(get(key, def))}" ${key === 'intel_url' ? 'type="url"' : ''}></label>`).join('')}<label>Startregion<select data-key="region">${Object.entries(REGIONS).map(([key, name]) => `<option value="${key}" ${key === (this._config.region || 'world') ? 'selected' : ''}>${name}</option>`).join('')}</select></label><label>Meldungen vor «Weitere»<input data-key="max_items" type="number" min="1" max="12" value="${this._config.max_items || 3}"></label><label><input data-key="compact_news" type="checkbox" ${this._config.compact_news !== false ? 'checked' : ''}> Kompakte Meldungen (Titel beim Öffnen vollständig)</label><label><input data-key="show_map" type="checkbox" ${this._config.show_map !== false ? 'checked' : ''}> Weltkarte anzeigen</label><label><input data-key="show_globe" type="checkbox" ${this._config.show_globe !== false ? 'checked' : ''}> 3D-Globus anzeigen</label>`;
  }
  _change(e) {
      const key = e.target.dataset.key; if (!key) return;
      const c = { ...this._config };
      let value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
      if (key === 'max_items') value = Math.max(1, Math.min(12, Number(value) || 3));
      if (key === 'alert_areas') value = String(value).split(',').map(s => s.trim()).filter(Boolean);
      if (value === '') delete c[key]; else c[key] = value;
      this._config = c;
      this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: c }, bubbles: true, composed: true }));
  }
}

if (globalThis.customElements) {
  if (!customElements.get('weltlage-card')) customElements.define('weltlage-card', WeltlageCard);
  if (!customElements.get('weltlage-card-editor')) customElements.define('weltlage-card-editor', WeltlageCardEditor);
  window.customCards = window.customCards || [];
  if (!window.customCards.some(c => c.type === 'weltlage-card')) window.customCards.push({ type: 'weltlage-card', name: 'Weltlage', description: 'Mobile Weltlage mit drehbarem Globus, Flügen, Satelliten und Nachrichten', preview: true });
}
