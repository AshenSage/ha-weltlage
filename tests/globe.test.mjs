import test from 'node:test';
import assert from 'node:assert/strict';
import {validCoordinates,flightIsFresh,satellitePosition,subsolarPoint} from '../custom_components/weltlage/frontend/weltlage-globe.js';

test('Globe excludes invalid coordinates and expired flight positions',()=>{
 assert.equal(validCoordinates({latitude:0,longitude:180}),true);
 for(const p of [{latitude:91,longitude:0},{latitude:0,longitude:NaN},{latitude:'44',longitude:20}])assert.equal(validCoordinates(p),false);
 assert.equal(flightIsFresh({latitude:44,longitude:20,observed:9999},10000),true);
 assert.equal(flightIsFresh({latitude:44,longitude:20,observed:9879},10000),false);
 assert.equal(flightIsFresh({latitude:44,longitude:20,observed:10061},10000),false);
});
test('Failed satellite propagation does not invent a position',()=>{
 assert.equal(satellitePosition(null),null);
 assert.equal(satellitePosition({}),null);
});
test('Approximate daylight hemisphere follows UTC longitude',()=>{
 assert.equal(subsolarPoint(new Date('2026-03-21T12:00:00Z'))[0],0);
 assert.equal(subsolarPoint(new Date('2026-03-21T00:00:00Z'))[0],-180);
 assert.ok(subsolarPoint(new Date('2026-06-21T12:00:00Z'))[1]>23);
});

test('Flight snapshot matches only its rounded query region',async()=>{
 const {snapshotMatchesView}=await import('../custom_components/weltlage/frontend/weltlage-globe.js');
 assert.equal(snapshotMatchesView({latitude:50,longitude:15},49,15),true);
 assert.equal(snapshotMatchesView({latitude:20,longitude:5},49,15),false);
});
test('Public camera frames require a known HTTPS origin and path',async()=>{
 const {allowedCameraImage}=await import('../custom_components/weltlage/frontend/weltlage-globe.js');
 assert.ok(allowedCameraImage('https://weathercam.digitraffic.fi/C0150301.jpg','finland'));
 for(const u of ['https://evil.example/C0150301.jpg','http://weathercam.digitraffic.fi/C0150301.jpg','https://user:pw@weathercam.digitraffic.fi/C0150301.jpg','https://weathercam.digitraffic.fi:8000/C0150301.jpg'])assert.equal(allowedCameraImage(u,'finland'),'');
});
test('Camera cluster retains every source point and leaves isolated points selectable',async()=>{
 const {clusterCameras}=await import('../custom_components/weltlage/frontend/weltlage-globe.js');
 const result=clusterCameras([{key:'a',x:20,y:20},{key:'b',x:22,y:24},{key:'c',x:100,y:100}]);
 assert.equal(result.length,2);assert.equal(result[0].cluster.length,2);assert.equal(result[1].key,'c');
});


test('Satellite background tiles wrap the antimeridian and use the pinned source',async()=>{
 const {tileUrl,mercatorLatitude,triangleMatrix}=await import('../custom_components/weltlage/frontend/weltlage-globe.js');
 assert.ok(tileUrl(2,-1,1).endsWith('/tile/2/1/3'));
 assert.throws(()=>tileUrl(2,0,5));
 assert.equal(mercatorLatitude(2,4),0);
 assert.ok(Math.abs(mercatorLatitude(0,4)-85.05112878)<.000001);
 assert.deepEqual(triangleMatrix([[0,0],[1,0],[0,1]],[[5,6],[7,6],[5,9]]),[2,0,0,3,5,6]);
 assert.equal(triangleMatrix([[0,0],[0,0],[0,0]],[[0,0],[1,1],[2,2]]),null);
});
