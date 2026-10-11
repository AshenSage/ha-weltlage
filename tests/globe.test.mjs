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
