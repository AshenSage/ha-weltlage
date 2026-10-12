export const HOME={latitude:44.30694,longitude:20.56};
export const PRESETS={home:{name:'Welt',...HOME,global:true},arandjelovac:{name:'Aranđelovac',...HOME,height:18000},balkan:{name:'Balkan',latitude:44,longitude:20,height:2000000},europe:{name:'Europa',latitude:49,longitude:15,height:6200000},switzerland:{name:'Schweiz',latitude:46.8,longitude:8.2,height:650000}};
export const STATUS={off:'Aus',loading:'Lädt',current:'Aktuell',stale:'Veraltet',no_hits:'Keine Treffer',no_coverage:'Keine Abdeckung',missing_key:'Schlüssel fehlt',invalid_key:'Zugang abgelehnt',unreachable:'Quelle nicht erreichbar',zoom_required:'Näher zoomen',rate_limited:'Abruflimit',unavailable:'Nicht eingerichtet'};
export function globeHeight(width,height,fov=Math.PI/3,radius=6378137){
 const aspect=Math.max(.1,width/Math.max(1,height));
 // Cesium PerspectiveFrustum.fov is horizontal when aspect > 1, vertical otherwise.
 const halfWide=fov/2;
 const halfNarrow=Math.atan(Math.tan(halfWide)*Math.min(aspect,1/aspect));
 return radius/Math.sin(halfNarrow*.86)-radius;
}
export function validPoint(p){return Number.isFinite(p?.latitude)&&Number.isFinite(p?.longitude)&&Math.abs(p.latitude)<=90&&Math.abs(p.longitude)<=180;}
export function regionalBounds(rect,center){
 if(rect&&rect.every(Number.isFinite)&&rect[2]>rect[0]&&rect[3]>rect[1])return [Math.max(-180,rect[0]),Math.max(-85,rect[1]),Math.min(180,rect[2]),Math.min(85,rect[3])];
 return [Math.max(-180,center.longitude-4),Math.max(-85,center.latitude-3),Math.min(180,center.longitude+4),Math.min(85,center.latitude+3)];
}
export function dateUTC(days=1){return new Date(Date.now()-days*86400000).toISOString().slice(0,10);}
export function readPrefs(key){try{const o=JSON.parse(localStorage.getItem(key)||'{}');return o&&typeof o==='object'?o:{}}catch{return {}}}
export function savePrefs(key,data){try{localStorage.setItem(key,JSON.stringify(data))}catch{}}
export function truncateTrail(rows,point){if(rows.length&&point.observed-rows.at(-1).observed>300)rows=[];if(!rows.length||point.observed>rows.at(-1).observed)rows.push({...point});return rows.slice(-30);}
