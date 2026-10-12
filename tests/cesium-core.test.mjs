import {test} from 'node:test';
import assert from 'node:assert/strict';
import {globeHeight,HOME,validPoint,regionalBounds,truncateTrail} from '../frontend_src/cesium/core.js';
test('full globe fits narrow and wide viewports including margin',()=>{for(const [w,h] of [[320,420],[390,450],[844,220]]){const R=6378137,H=globeHeight(w,h);const angle=Math.asin(R/(R+H));const narrow=Math.atan(Math.tan(Math.PI/6)*Math.min(w/h,h/w));assert.ok(angle<narrow);assert.ok(H>R);}});
test('home is verified Arandjelovac and points reject invalid coordinates',()=>{assert.deepEqual(HOME,{latitude:44.30694,longitude:20.56});assert.equal(validPoint({latitude:91,longitude:20}),false);assert.equal(validPoint({latitude:NaN,longitude:20}),false);});
test('trail keeps chronological actual snapshots with a bounded history',()=>{let rows=[];for(let i=0;i<80;i++)rows=truncateTrail(rows,{observed:i});assert.equal(rows.length,30);assert.equal(truncateTrail(rows,{observed:79}).length,30);});
test('regional request clamps polar coordinates',()=>assert.deepEqual(regionalBounds([-180,-90,180,90],HOME),[-180,-85,180,85]));

test('flight trail breaks across an unobserved five minute gap',()=>assert.deepEqual(truncateTrail([{observed:1}],{observed:400}),[{observed:400}]));
