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
    const item = { eid, id: a.identifier, title: types[type] || a.event_alt || a.event || a.headline || 'Wetterwarnung', original: a.headline || a.event || '', area: a.area_desc || cfg.alert_label, level, onset, expires, url: safeLink(a.web), polygons: a.polygons || a.polygon || [], description: String(a.description_alt || a.description || '').slice(0, 600) };
    (onset > now ? upcoming : active).push(item);
  }
  active.sort((a, b) => b.level - a.level || a.expires - b.expires);
  upcoming.sort((a, b) => a.onset - b.onset);
  const configured = Boolean(counter || updated || found.length);
  const stale = !Number.isFinite(last) || now - last > (cfg.alert_max_age || 90) * 60000 || last > now + 300000;
  const partial = incomplete || (rawValid && raw > 0 && !found.length) || (!rawValid && !found.length);
  return { active, upcoming, status: !configured ? 'not_configured' : stale ? 'stale' : partial ? 'partial' : 'ok', last_success: Number.isFinite(last) ? new Date(last).toISOString() : null };
}
