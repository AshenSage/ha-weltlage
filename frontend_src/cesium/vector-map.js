import {VectorTile} from '@mapbox/vector-tile';
import {PbfReader} from 'pbf';
import {Credit,Event,WebMercatorTilingScheme} from 'cesium';

const SIZE=256,RETINA=2;
const CREDIT='<a href="https://openfreemap.org/">OpenFreeMap</a> · <a href="https://openmaptiles.org/">© OpenMapTiles</a> · <a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>';
const roadRank={motorway:0,trunk:1,primary:2,secondary:3,tertiary:4,minor:5,street:5,residential:5,service:6,track:7,path:8,rail:9};
const roadMin={motorway:4,trunk:5,primary:6,secondary:8,tertiary:9,minor:11,street:11,residential:11,service:13,track:13,path:14,rail:8};
const name=p=>String(p['name:sr-Latn']||p['name:latin']||p.name||p['name:en']||'').slice(0,100);

// MVT geometry is drawn afresh at every requested zoom, including overzoom.
// Text is native browser text, never enlarged from a lower-resolution map image.
export function paintVectorTile(ctx,tile,x,y,level,dataX,dataY,dataLevel){
 const scale=2**(level-dataLevel),ox=x-dataX*scale,oy=y-dataY*scale;
 const point=(p,extent)=>({x:(p.x/extent*scale-ox)*SIZE,y:(p.y/extent*scale-oy)*SIZE});
 const features=[],labels=[];
 let drawn=0;
 const read=(layer,fn)=>{const l=tile.layers[layer];if(!l)return;for(let i=0;i<Math.min(l.length,20000);i++){const f=l.feature(i);fn(f,f.properties,f.loadGeometry().map(r=>r.map(p=>point(p,f.extent))))}};
 const path=(rings,closed)=>{ctx.beginPath();for(const ring of rings){if(!ring.length)continue;ctx.moveTo(ring[0].x,ring[0].y);for(const p of ring.slice(1))ctx.lineTo(p.x,p.y);if(closed)ctx.closePath()}};
 const fill=(rings,color,outline)=>{path(rings,true);ctx.fillStyle=color;ctx.fill('evenodd');if(outline){ctx.strokeStyle=outline;ctx.lineWidth=.45;ctx.stroke()}drawn++};
 const line=(rings,color,width,dash=[])=>{path(rings,false);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);drawn++};
 ctx.save();ctx.scale(RETINA,RETINA);ctx.fillStyle='#eff3ed';ctx.fillRect(0,0,SIZE,SIZE);ctx.lineJoin='round';ctx.lineCap='round';
 read('landcover',(f,p,g)=>{if(f.type===3)fill(g,/wood|forest/.test(p.class)?'#d6e5d3':/grass|scrub/.test(p.class)?'#e2ecd9':'#e9eee3')});
 if(level>=7){read('landuse',(f,p,g)=>{if(f.type===3)fill(g,/park|cemetery|forest/.test(p.class)?'#d4e5d2':/industrial/.test(p.class)?'#e3e5e8':'#e9ece5')});read('park',(f,p,g)=>{if(f.type===3)fill(g,'#d9e9d6')})}
 read('water',(f,p,g)=>{if(f.type===3)fill(g,'#b8d9e8')});
 if(level>=6)read('waterway',(f,p,g)=>line(g,'#a9cddb',p.class==='river'?1.5:.75));
 read('boundary',(f,p,g)=>{if(p.admin_level<=2||level>=7&&p.admin_level<=4)line(g,'#a8b5bc',p.admin_level<=2?.85:.5,[3,3])});
 if(level>=13)read('building',(f,p,g)=>{if(f.type===3)fill(g,'#d8dee0','#c0cacd')});
 read('transportation',(f,p,g)=>{if(f.type!==2||level<(roadMin[p.class]??12)||p.brunnel==='tunnel')return;features.push({p,g})});
 features.sort((a,b)=>(roadRank[b.p.class]??6)-(roadRank[a.p.class]??6));
 for(const {p,g} of features){const major=(roadRank[p.class]??6)<4,w=major?Math.max(.7,Math.min(4.8,(level-4)*.38+(4-(roadRank[p.class]??4))*.4)):p.class==='rail'?.8:level<13?.8:1.5;if(p.class==='rail'){line(g,'#9ba9ac',w,[3,2]);continue}line(g,major?'#d9bc94':'#cbd3d5',w+1);line(g,major?'#ffe4ba':'#ffffff',w)}
 if(level>=13)read('transportation_name',(f,p,g)=>{const text=name(p);if(!text)return;const ring=g.reduce((best,r)=>r.length>best.length?r:best,[]);let length=0;for(let i=1;i<ring.length;i++)length+=Math.hypot(ring[i].x-ring[i-1].x,ring[i].y-ring[i-1].y);if(length<text.length*6+25)return;let left=length/2;for(let i=1;i<ring.length;i++){const a=ring[i-1],b=ring[i],d=Math.hypot(b.x-a.x,b.y-a.y);if(left<=d&&d>0){let angle=Math.atan2(b.y-a.y,b.x-a.x);if(angle>Math.PI/2)angle-=Math.PI;if(angle< -Math.PI/2)angle+=Math.PI;labels.push({text,x:a.x+(b.x-a.x)*left/d,y:a.y+(b.y-a.y)*left/d,size:10,weight:500,priority:2000+(roadRank[p.class]??9),angle});break}left-=d}})
 const boxes=[];let count=0;labels.sort((a,b)=>a.priority-b.priority);
 for(const l of labels){ctx.font=`${l.weight} ${l.size}px system-ui, sans-serif`;const width=ctx.measureText(l.text).width+8,height=l.size+7,box={x:l.x-width/2,y:l.y-height/2,w:width,h:height};if(box.x< -64||box.y< -64||box.x+box.w>SIZE+64||box.y+box.h>SIZE+64||boxes.some(b=>box.x<b.x+b.w&&box.x+box.w>b.x&&box.y<b.y+b.h&&box.y+box.h>b.y)||count>=80)continue;boxes.push(box);ctx.save();ctx.translate(l.x,l.y);ctx.rotate(l.angle||0);ctx.textAlign='center';ctx.textBaseline='middle';ctx.strokeStyle='#f7faf3';ctx.lineWidth=3;ctx.strokeText(l.text,0,0);ctx.fillStyle=l.city?'#243b49':'#435b67';ctx.fillText(l.text,0,0);ctx.restore();count++}
 ctx.restore();return {features:drawn,labels:count};
}

export class VectorMapProvider{
 static async create(){
  const response=await fetch('https://tiles.openfreemap.org/planet/latest',{signal:AbortSignal.timeout(15000),referrerPolicy:'strict-origin-when-cross-origin'});
  if(!response.ok)throw Error('Vector metadata unavailable');const info=await response.json(),url=info.tiles?.[0];
  if(typeof url!=='string'||!/^https:\/\/tiles\.openfreemap\.org\/planet\/[a-zA-Z0-9_]+\/\{z\}\/\{x\}\/\{y\}\.pbf$/.test(url))throw Error('Invalid vector source');
  return new VectorMapProvider(url,Math.min(14,info.maxzoom||14));
 }
 constructor(url,maxDataZoom){this.url=url;this.sourceType='vector';this.tileWidth=SIZE*RETINA;this.tileHeight=SIZE*RETINA;this.minimumLevel=0;this.maximumLevel=18;this.tilingScheme=new WebMercatorTilingScheme();this.rectangle=this.tilingScheme.rectangle;this.errorEvent=new Event();this.credit=new Credit(CREDIT,true);this.hasAlphaChannel=false;this._maxDataZoom=maxDataZoom;this._tiles=new Map();this._cachedBytes=0;this._pending=new Map();this._controllers=new Set();this._active=0;this._destroyed=false;this.stats={tiles:0,features:0,labels:0}}
 getTileCredits(){return undefined}
 pickFeatures(){return undefined}
 requestImage(x,y,level){if(this._destroyed||this._active>=4)return undefined;this._active++;return this._image(x,y,level).finally(()=>this._active--)}
 async _tile(x,y,z){const key=`${z}/${x}/${y}`;if(this._tiles.has(key)){const value=this._tiles.get(key);this._tiles.delete(key);this._tiles.set(key,value);return value}if(this._pending.has(key))return this._pending.get(key);const controller=new AbortController();this._controllers.add(controller);const timer=setTimeout(()=>controller.abort(),15000),promise=(async()=>{const response=await fetch(this.url.replace('{z}',z).replace('{x}',x).replace('{y}',y),{signal:controller.signal,referrerPolicy:'strict-origin-when-cross-origin'});if(!response.ok)throw Object.assign(Error('Vector tile unavailable'),{statusCode:response.status});const bytes=await response.arrayBuffer();if(bytes.byteLength>4000000||this._destroyed)throw Error('Vector tile unavailable');const tile=new VectorTile(new PbfReader(new Uint8Array(bytes)));tile.byteLength=bytes.byteLength;this._tiles.set(key,tile);this._cachedBytes+=bytes.byteLength;while(this._tiles.size>48||this._cachedBytes>12000000){const oldest=this._tiles.keys().next().value;this._cachedBytes-=this._tiles.get(oldest).byteLength;this._tiles.delete(oldest)}return tile})();this._pending.set(key,promise);try{return await promise}finally{clearTimeout(timer);this._pending.delete(key);this._controllers.delete(controller)}}
 async _image(x,y,level){const z=Math.min(level,this._maxDataZoom),factor=2**(level-z),dx=Math.floor(x/factor),dy=Math.floor(y/factor),tile=await this._tile(dx,dy,z);if(this._destroyed)throw Error('Vector provider disposed');if(this.onPlaces){const places=[],l=tile.layers.place;if(l)for(let i=0;i<Math.min(l.length,2000);i++){const f=l.feature(i),p=f.properties,geo=f.toGeoJSON(dx,dy,z);if(geo.geometry.type==='Point'&&name(p))places.push({id:f.id,dataLevel:z,name:name(p),kind:p.class,rank:Number(p.rank||0),longitude:geo.geometry.coordinates[0],latitude:geo.geometry.coordinates[1]})}this.onPlaces(places)}const canvas=document.createElement('canvas');canvas.width=this.tileWidth;canvas.height=this.tileHeight;const stats=paintVectorTile(canvas.getContext('2d'),tile,x,y,level,dx,dy,z);this.stats.tiles++;this.stats.features+=stats.features;this.stats.labels+=stats.labels;return canvas}

 destroy(){this._destroyed=true;for(const c of this._controllers)c.abort();this._controllers.clear();this._tiles.clear();this._cachedBytes=0;this._pending.clear()}
}
