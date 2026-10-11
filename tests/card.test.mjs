import test from 'node:test';
import assert from 'node:assert/strict';
import { safeLink, escapeHTML, age, effectiveSourceStatus, regionMatches, filterArticles, capAlerts } from '../custom_components/weltlage/frontend/weltlage-card.js';

const now = Date.parse('2025-01-01T12:00:00Z');
const config = { alert_count_entity: 'sensor.count', alert_updated_entity: 'sensor.updated', alert_areas: ['RS010'], alert_label: 'Šumadija', alert_max_age: 90 };
const base = () => ({ 'sensor.count': { state: '1' }, 'sensor.updated': { state: '2025-01-01T11:55:00Z' } });
const warning = (override = {}) => ({ state: 'unknown', attributes: { provider: 'meteoalarm', identifier: 'a', status: 'Actual', msg_type: 'Alert', geocodes: { EMMA_ID: ['RS010'] }, severity: 'Minor', severity_normalized: 'unknown', parameters: { awareness_level: '2; yellow; Moderate', awareness_type: '3; thunderstorm' }, onset: '2025-01-01T11:00:00Z', expires: '2025-01-01T18:00:00Z', ...override } });

test('URLs and feed text cannot inject HTML or script links', () => {
  for (const url of ['javascript:alert(1)', 'data:text/html,x', 'https://user:pw@example.org', 'not a url']) assert.equal(safeLink(url), '');
  assert.equal(safeLink('https://example.org/a'), 'https://example.org/a');
  assert.equal(escapeHTML('<img onerror="x">'), '&lt;img onerror=&quot;x&quot;&gt;');
});
test('freshness is recomputed as time passes without HA updates', () => {
  const source = { status: 'ok', interval: 300, last_success: '2025-01-01T11:55:00Z' };
  assert.equal(effectiveSourceStatus(source, now), 'ok');
  assert.equal(effectiveSourceStatus(source, now + 20 * 60000), 'stale');
  assert.equal(effectiveSourceStatus({ ...source, status: 'error' }, now), 'error');
  assert.equal(effectiveSourceStatus({ last_success: null }, now), 'unavailable');
});
test('region, topic and time filters compose', () => {
  const a = { published: now / 1000 - 3600, regions: ['world', 'ch', 'europa'], category: 'energie' };
  assert.equal(regionMatches(a.regions, 'chrs'), true);
  assert.equal(regionMatches(a.regions, 'rs'), false);
  assert.equal(filterArticles([a], 'chrs', 'energie', 24, now).length, 1);
  assert.equal(filterArticles([a], 'world', 'natur', 24, now).length, 0);
  assert.equal(filterArticles([{ ...a, published: now / 1000 - 90000 }], 'world', 'all', 24, now).length, 0);
  assert.equal(filterArticles([{ ...a, published: null, first_seen: now / 1000 - 3600 }], 'world', 'all', 24, now).length, 1);
});
test('missing publication date is displayed honestly', () => {
  assert.equal(age(null, now), 'Datum fehlt');
  assert.equal(age(now / 1000 - 600, now), 'vor 10 Min.');
  assert.equal(age(now / 1000 + 600, now), 'Zeitangabe prüfen');
});
test('green CAP records do not become alarms despite raw counter', () => {
  const states = base();
  states['sensor.count'].state = '28';
  for (let i = 0; i < 28; i++) states[`sensor.cap_alert_${i}`] = warning({ identifier: `a${i}`, parameters: { awareness_level: ['1; green; Minor'] } });
  const cap = capAlerts(states, config, now);
  assert.equal(cap.status, 'ok');
  assert.equal(cap.active.length, 0);
  assert.equal(cap.upcoming.length, 0);
});
test('unknown HA state still permits valid yellow CAP attributes', () => {
  const cap = capAlerts({ ...base(), 'sensor.cap_alert_a': warning() }, config, now);
  assert.equal(cap.status, 'ok');
  assert.equal(cap.active[0].level, 1);
  assert.equal(cap.active[0].title, 'Gewitter');
});
test('future, expired, duplicate, test and other-region CAP entries', () => {
  const states = { ...base(), 'sensor.cap_alert_a': warning(), 'sensor.cap_alert_duplicate': warning(), 'sensor.cap_alert_future': warning({ identifier: 'future', onset: '2025-01-01T14:00:00Z' }), 'sensor.cap_alert_expired': warning({ identifier: 'expired', expires: '2025-01-01T10:00:00Z' }), 'sensor.cap_alert_test': warning({ identifier: 'test', status: 'Test' }), 'sensor.cap_alert_ch': warning({ identifier: 'ch', geocodes: { EMMA_ID: ['CH001'] } }) };
  const cap = capAlerts(states, config, now);
  assert.equal(cap.active.length, 1);
  assert.equal(cap.upcoming.length, 1);
});
test('stale, unavailable or incomplete CAP never implies all clear', () => {
  assert.equal(capAlerts({}, config, now).status, 'not_configured');
  assert.equal(capAlerts({ ...base(), 'sensor.cap_alert_a': warning() }, config, now + 2 * 3600000).status, 'stale');
  assert.equal(capAlerts(base(), config, now).status, 'partial');
  assert.equal(capAlerts({ ...base(), 'sensor.cap_alert_a': warning({ parameters: {}, severity: 'Unknown' }) }, config, now).status, 'partial');
  const unavailable = { ...warning(), state: 'unavailable' };
  assert.equal(capAlerts({ ...base(), 'sensor.cap_alert_a': unavailable }, config, now).status, 'partial');
});
test('fresh empty CAP is different from missing CAP', () => {
  const states = base(); states['sensor.count'].state = '0';
  assert.equal(capAlerts(states, config, now).status, 'ok');
});
test('CAP timestamps without a timezone are incomplete', () => {
  const states = { ...base(), 'sensor.cap_alert_a': warning({ onset: '2025-01-01T11:00:00' }) };
  assert.equal(capAlerts(states, config, now).status, 'partial');
  assert.equal(capAlerts(states, config, now).active.length, 0);
});
