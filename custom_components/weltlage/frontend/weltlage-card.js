import './weltlage-globe.js?v=1.2.0';
export const VERSION='1.2.0';
const REGIONS={world:'Welt',europa:'Europa',ch:'Schweiz',rs:'Serbien',balkan:'Balkan'};
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
const STYLE=`:host{display:block;color:#dcefee;font:14px/1.5 system-ui,sans-serif}ha-card{display:block;background:#061310;border:1px solid #264a43;border-radius:20px;overflow:hidden}weltlage-globe{display:block}.notice{margin:10px;padding:11px;border:1px solid #9e7537;border-radius:10px;background:#241e12;color:#ffcd7d;font-size:12px}[hidden]{display:none!important}`;
export class WeltlageCard extends (globalThis.HTMLElement||class{}) {
  static getConfigElement(){return document.createElement('weltlage-card-editor');}
  static getStubConfig(){return {type:'custom:weltlage-card',title:"GOD'S EYE"};}
  getCardSize(){return 9;}
  getLayoutOptions(){return {grid_columns:12,grid_rows:9};}
  setConfig(config){
    this._config={title:"GOD'S EYE",region:'world',alert_count_entity:'sensor.cap_alerts_wmo_alert_count',alert_updated_entity:'sensor.cap_alerts_wmo_last_updated',alert_areas:['RS010'],alert_label:'Serbien · Šumadija',alert_max_age:90,...config};
    if(typeof this._config.alert_areas==='string')this._config.alert_areas=this._config.alert_areas.split(',').map(s=>s.trim()).filter(Boolean);
    this._init();this._render();
  }
  set hass(hass){this._hass=hass;if(this._config)this._render();}
  connectedCallback(){if(!this._clock)this._clock=setInterval(()=>this._render(),60000);this._render();}
  disconnectedCallback(){clearInterval(this._clock);this._clock=null;}
  _state(){return this._hass?.states[this._config?.entity]||(!this._config?.entity&&Object.values(this._hass?.states||{}).find(s=>s.attributes?.integration==='weltlage'&&Array.isArray(s.attributes?.hazards)));}
  _init(){if(this.shadowRoot)return;this.attachShadow({mode:'open'});this.shadowRoot.innerHTML=`<style>${STYLE}</style><ha-card><div class="setup" role="status" hidden></div><weltlage-globe></weltlage-globe></ha-card>`;this.shadowRoot.addEventListener('intel-request',e=>this._fetchIntel(e.detail));this.shadowRoot.addEventListener('refresh-request',()=>this._refresh());}
  _render(){
    if(!this.shadowRoot||!this._config)return;
    const state=this._state(),data=state?.attributes||{},cap=capAlerts(this._hass?.states||{},this._config);
    const setup=this.shadowRoot.querySelector('.setup');const message=!state?'Unter Einstellungen → Geräte & Dienste die Integration «Weltlage» hinzufügen.':state.state==='unavailable'?'Integration nicht erreichbar · gespeicherte Positionen können veraltet sein.':data.version&&data.version!==VERSION?`Karte ${VERSION} · Integration ${data.version}. HACS aktualisieren, HA neu starten und App neu laden.`:'';
    setup.textContent=message;setup.hidden=!message;setup.className='setup'+(message?' notice':'');
    const globe=this.shadowRoot.querySelector('weltlage-globe');globe.configure({title:this._config.title,region:this._config.region,storageKey:'weltlage.globe.'+(this._config.entity||'auto')});
    const capPoints=(this._config.alert_areas||[]).includes('RS010')?[...cap.active,...cap.upcoming].map(a=>({id:a.id,name:a.title+(a.onset>Date.now()?' · kommend':''),latitude:44.3,longitude:20.7,source:'CAP · Šumadija',url:a.url,description:(cap.status!=='ok'?'Datenstand prüfen. ':'')+'Gebietsmitte Šumadija, keine exakte Ereignisposition. '+a.description})):[];
    globe.payload={hazards:data.hazards||[],intel:data.intel||{},sources:data.sources||[],stale_sources:(data.sources||[]).filter(s=>effectiveSourceStatus(s)!=='ok').map(s=>s.id),cap:capPoints,version:VERSION,cap_status:cap.status};
  }
  async _fetchIntel(detail){
    const globe=this.shadowRoot.querySelector('weltlage-globe');
    if(!this._hass||!this._state()){globe.setBusy(detail.kind,false,'Zuerst die Weltlage-Integration einrichten.','error');return;}
    globe.setBusy(detail.kind,true);
    try{await this._hass.callService('weltlage','fetch_intel',detail);this._render();globe.setBusy(detail.kind,false,'','ok');}
    catch{globe.setBusy(detail.kind,false,'Abruf fehlgeschlagen · Verbindung und Integration prüfen.','error');}
  }
  async _refresh(){try{await this._hass.callService('homeassistant','update_entity',{entity_id:this._config.entity||Object.keys(this._hass.states).find(k=>this._hass.states[k]===this._state())});}catch{this.shadowRoot.querySelector('weltlage-globe').setBusy('hazards',false,'Ereignisse konnten nicht aktualisiert werden.','error');}}
}
export class WeltlageCardEditor extends (globalThis.HTMLElement||class{}) {
  setConfig(config){this._config={...config};this._render();}
  set hass(hass){this._hass=hass;}
  _render(){if(!this.shadowRoot){this.attachShadow({mode:'open'});this.shadowRoot.addEventListener('change',e=>this._change(e));}
    const fields=[['title','Titel',"GOD'S EYE"],['entity','Lagebild-Entität (leer = automatisch)',''],['alert_count_entity','CAP-Zähler','sensor.cap_alerts_wmo_alert_count'],['alert_updated_entity','CAP: letzter Abruf','sensor.cap_alerts_wmo_last_updated'],['alert_areas','CAP-Gebietscodes','RS010'],['alert_label','Warnregion','Serbien · Šumadija']];
    this.shadowRoot.innerHTML=`<style>:host{display:block}label{display:block;margin:14px 0}input,select{display:block;box-sizing:border-box;width:100%;min-height:44px;font:inherit;padding:10px;margin-top:5px;border:1px solid var(--divider-color);border-radius:8px;color:var(--primary-text-color);background:var(--card-background-color)}p{font-size:13px;line-height:1.5;color:var(--secondary-text-color)}</style><p>Nur Globus. Kameranetze, Ebenen, Flugaktualisierung und Darstellung steuerst du direkt auf der Karte. Position, Zoom und Ebenen werden auf diesem Gerät gemerkt.</p>${fields.map(([key,label,def])=>`<label>${label}<input data-key="${key}" value="${escapeHTML(key==='alert_areas'?(this._config[key]||[def]).join?.(', ')||this._config[key]:this._config[key]??def)}"></label>`).join('')}<label>Startregion<select data-key="region">${Object.entries(REGIONS).map(([k,v])=>`<option value="${k}" ${k===(this._config.region||'world')?'selected':''}>${v}</option>`).join('')}</select></label>`;
  }
  _change(e){const key=e.target.dataset.key;if(!key)return;const config={...this._config};let value=e.target.value;if(key==='alert_areas')value=value.split(',').map(s=>s.trim()).filter(Boolean);if(value==='')delete config[key];else config[key]=value;this._config=config;this.dispatchEvent(new CustomEvent('config-changed',{detail:{config},bubbles:true,composed:true}));}
}
if(globalThis.customElements){if(!customElements.get('weltlage-card'))customElements.define('weltlage-card',WeltlageCard);if(!customElements.get('weltlage-card-editor'))customElements.define('weltlage-card-editor',WeltlageCardEditor);window.customCards=window.customCards||[];if(!window.customCards.some(c=>c.type==='weltlage-card'))window.customCards.push({type:'weltlage-card',name:"Weltlage · God's Eye",description:'Mobiler Intel-Globus mit Verkehrskameras, Flügen und Satelliten',preview:true});}
