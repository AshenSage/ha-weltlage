const VERSION = WeltlagePreview.VERSION;

const ts = Date.now() / 1000;
const success = new Date(Date.now() - 180000).toISOString();
const definitions = [
 ['konflikte', ['world','rs','balkan','europa'], 'Разговори о безбједности енергетске инфраструктуре и заштити снабдијевања у југоисточној Европи — синтетички примјер за приказ дугог наслова', 'RTS', 'sr', 'rts'],
 ['politik', ['world','europa'], 'Diplomatie und internationale Entwicklungen', 'BBC', 'en', 'bbc_world'],
 ['wirtschaft', ['world','ch','europa'], 'Wirtschaft und Handel in der Schweiz', 'SRF', 'de', 'srf_ch'],
 ['natur', ['world'], 'Naturereignisse und aktuelle Lageberichte', 'BBC', 'en', 'bbc_world'],
 ['technik', ['world'], 'Neue Entwicklungen in Technik und Infrastruktur', 'SRF', 'de', 'srf_world'],
 ['politik', ['world','ch','europa'], 'Schweizer Politik und internationale Beziehungen', 'SRF', 'de', 'srf_ch']
];
const articles = definitions.map(([category, regions, title, name, language, sid], i) => ({id:`demo_${i}`, title:`Beispiel: ${title}`, summary:'Beispieldaten zur Vorschau. In Home Assistant steht hier der kurze RSS-Text der Quelle. Der Originalartikel öffnet sich über den Quellenlink.', url:'https://example.org', category, topics:i===0?['konflikte','energie']:[category], regions, language, published:ts-(i+1)*2100, first_seen:ts-10000, sources:[{id:sid,name,url:'https://example.org'}]}));
const sourceNames = [['srf_world','SRF International','news'],['srf_business','SRF Wirtschaft','news'],['srf_ch','SRF Schweiz','news'],['bbc_world','BBC World','news'],['bbc_europe','BBC Europe','news'],['rts','RTS Serbien','news'],['usgs','USGS · Erdbeben M ≥ 4.5','usgs'],['gdacs','GDACS · Orange / Rot','gdacs']];
const sources = sourceNames.map(([id,name,kind])=>({id,name,kind,status:'ok',interval:kind==='news'?900:300,last_success:success,latest_entry:new Date(Date.now()-2100000).toISOString()}));
const states = {
 'sensor.weltlage_lagebild':{state:'6',attributes:{integration:'weltlage',version:VERSION,articles,sources,hazards:[{id:'demo_eq',title:'Beispiel: Erdbeben M 4.8 · Welt',source:'USGS',source_id:'usgs',kind:'Erdbeben',latitude:40.8,longitude:14.3,magnitude:4.8,regions:['world'],severity:'information',published:ts-2000,expires:ts+86400,url:'https://example.org'}]}},
 'button.weltlage_aktualisieren':{state:'unknown',attributes:{integration:'weltlage',role:'refresh'}},
 'sensor.cap_alerts_wmo_alert_count':{state:'1',attributes:{}},
 'sensor.cap_alerts_wmo_last_updated':{state:success,attributes:{}},
 'sensor.cap_alerts_demo':{state:'unknown',attributes:{identifier:'demo_cap',provider:'meteoalarm',geocodes:{EMMA_ID:['RS010']},severity:'Moderate',parameters:{awareness_level:'2; yellow; Moderate',awareness_type:'3; thunderstorm'},status:'Actual',msg_type:'Alert',onset:new Date(Date.now()-3600000).toISOString(),expires:new Date(Date.now()+10800000).toISOString(),headline:'Beispiel-Warnung',description:'Beispieldaten, keine echte Wetterwarnung.',web:'https://example.org'}}
};
window.demoIntel = {
 flights:{last_success:ts,last_attempt:ts,latitude:45,longitude:20,items:[{id:'abc123',name:'DEMO 101',latitude:44.8,longitude:20.2,heading:45,altitude_m:10000,speed_kmh:750,observed:ts,source:'adsb.lol · Demo',url:'https://example.org'},{id:'abc124',name:'DEMO 102',latitude:46.2,longitude:15.5,heading:120,altitude_m:9000,speed_kmh:700,observed:ts,source:'adsb.lol · Demo',url:'https://example.org'}]},
 satellites:{last_success:ts,last_attempt:ts,items:[{OBJECT_NAME:'Demo-Orbit · synthetisch',NORAD_CAT_ID:99999,OBJECT_ID:'DEMO',EPOCH:new Date().toISOString().replace('Z',''),epoch_timestamp:ts,MEAN_MOTION:15.488,ECCENTRICITY:.00067,INCLINATION:51.63,RA_OF_ASC_NODE:86.09,ARG_OF_PERICENTER:248.13,MEAN_ANOMALY:111.89,BSTAR:.00018,MEAN_MOTION_DOT:.000094,MEAN_MOTION_DDOT:0}]}
};
window.demoHass = {states,config:{time_zone:'Europe/Belgrade'},callService:async(domain,service,request)=>{window.lastService=domain+'.'+service;if(domain==='weltlage'){const old=window.demoHass.states['sensor.weltlage_lagebild'];window.demoHass={...window.demoHass,states:{...window.demoHass.states,'sensor.weltlage_lagebild':{...old,attributes:{...old.attributes,intel:{...old.attributes.intel,[request.kind]:window.demoIntel[request.kind]}}}}};window.card.hass=window.demoHass;}}};
const card = document.querySelector('weltlage-card');
card.setConfig({type:'custom:weltlage-card',title:'Weltlage'});
card.hass = window.demoHass;
window.card = card;
