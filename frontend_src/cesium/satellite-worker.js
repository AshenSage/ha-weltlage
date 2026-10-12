import {json2satrec,propagate,gstime,eciToGeodetic,degreesLat,degreesLong} from 'satellite.js';
let records=[];
function position(rec,date){const pv=propagate(rec,date);if(!pv.position)return null;const p=eciToGeodetic(pv.position,gstime(date));if(!Number.isFinite(p.height))return null;return [degreesLong(p.longitude),degreesLat(p.latitude),p.height*1000];}
self.onmessage=({data})=>{
 if(data.type==='catalog'){
  records=(data.items||[]).filter(a=>Date.now()/1000-a.epoch_timestamp<14*86400).slice(0,1000).map(a=>{try{return {a,rec:json2satrec(a)}}catch{return null}}).filter(Boolean);
 }
 if(data.type==='tick'||data.type==='catalog'){
  const date=new Date(data.now||Date.now()),rows=[];
  for(const {a,rec} of records){if(date.getTime()/1000-a.epoch_timestamp>14*86400)continue;const p=position(rec,date);if(p)rows.push({id:String(a.NORAD_CAT_ID),name:a.OBJECT_NAME,longitude:p[0],latitude:p[1],altitude_m:p[2],group:a.group,epoch:a.epoch_timestamp,computed:true,source:'CelesTrak · SGP4'});}
  self.postMessage({type:'positions',items:rows});
 }
 if(data.type==='orbit'){
  const r=records.find(r=>String(r.a.NORAD_CAT_ID)===data.id);if(!r)return;
  const start=Number(data.now)||Date.now(),period=86400000/r.a.MEAN_MOTION,line=[];
  for(let i=0;i<=120;i++){const p=position(r.rec,new Date(start+period*i/120));if(p)line.push(p);}
  self.postMessage({type:'orbit',id:data.id,line});
 }
};
