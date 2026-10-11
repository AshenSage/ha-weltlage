import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(import.meta.url);
const dep=process.env.WELTLAGE_NODE_MODULES;
const esbuild=dep?createRequire(resolve(dep,'../package.json'))('esbuild'):require('esbuild');
await esbuild.build({entryPoints:[resolve(root,'frontend_src/weltlage-globe.js')],outfile:resolve(root,'custom_components/weltlage/frontend/weltlage-globe.js'),bundle:true,format:'esm',minify:true,target:'es2020',legalComments:'eof',nodePaths:dep?[dep]:[],banner:{js:'/* Weltlage Globe 1.1.0. Bundled d3-geo (ISC), satellite.js (MIT), Natural Earth (Public Domain). See THIRD_PARTY.md. */'}});
