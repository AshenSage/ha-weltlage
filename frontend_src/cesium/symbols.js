const shapes={
 flights:'<path d="M32 5 37 24 56 35v6l-19-6v14l7 5v4l-12-3-12 3v-4l7-5V35L8 41v-6l19-11z"/>',
 military:'<path d="m32 4 5 23 15 16-2 5-13-5v9l6 7-11-3-11 3 6-7v-9l-13 5-2-5 15-16z"/>',
 ships:'<path d="m32 6 15 11 5 28-20 13-20-13 5-28z"/><path d="M25 22h14v21H25z" fill="#07131d" stroke="none"/>',
 satellites:'<rect x="24" y="22" width="16" height="20" rx="3"/><path d="M5 19h14v26H5zm40 0h14v26H45zM19 32h5m16 0h5M32 22V11m-5 0h10"/>',
 cameras:'<rect x="8" y="19" width="36" height="28" rx="6"/><path d="m44 26 13-6v26l-13-6z"/><circle cx="26" cy="33" r="7" fill="#07131d" stroke="none"/>',
 traffic:'<path d="m16 27 6-13h20l6 13v22H16z"/><path d="M22 26h20l-3-7H25z" fill="#07131d" stroke="none"/><path d="M19 49v5m26-5v5M21 36h4m14 0h4"/>',
 incidents:'<path d="M32 8 59 55H5z"/><path d="M32 24v14" fill="none" stroke="#07131d" stroke-width="5"/><circle cx="32" cy="46" r="3" fill="#07131d" stroke="none"/>',
 earthquakes:'<path d="M5 32h12l6-15 9 32 9-25 5 8h13" fill="none" stroke-width="6"/>',
 fires:'<path d="M33 5c5 14 19 18 17 34-1 12-10 19-20 19S13 50 14 39c0-11 8-14 9-23 6 5 5 10 5 10 6-7 8-13 5-21z"/>',
 mapillary:'<rect x="9" y="12" width="46" height="40" rx="5"/><circle cx="23" cy="25" r="5" fill="#07131d" stroke="none"/><path d="m15 44 12-12 8 7 9-13 6 18z" fill="#07131d" stroke="none"/>',
 datacenters:'<rect x="13" y="9" width="38" height="46" rx="4"/><path d="M19 22h26M19 33h26M19 44h26" fill="none" stroke="#07131d" stroke-width="3"/>',
 dams:'<path d="M13 12h38l-5 38H18z"/><path d="M5 54q7-7 14 0t14 0 14 0 12 0" fill="none"/>',
 bases:'<path d="M32 8 53 17v17c0 12-21 23-21 23S11 46 11 34V17z"/><path d="m32 20 4 8 9 1-7 6 2 9-8-4-8 4 2-9-7-6 9-1z" fill="#07131d" stroke="none"/>',
 cap:'<path d="M32 8 59 55H5z"/><path d="M32 24v14" fill="none" stroke="#07131d" stroke-width="5"/><circle cx="32" cy="46" r="3" fill="#07131d" stroke="none"/>',
 default:'<path d="M32 5 54 18v28L32 59 10 46V18z"/><circle cx="32" cy="32" r="8" fill="#07131d" stroke="none"/>'
};
shapes.finland=shapes.cameras;shapes.gdacs=shapes.cap;
const images=new Map();
export function markerImage(id){const kind=shapes[id]?id:'default';if(!images.has(kind)){const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 64 64"><g fill="#ffffff" stroke="#07131d" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">${shapes[kind]}</g></svg>`;images.set(kind,'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg))}return images.get(kind)}
export function symbolHeading(layer,heading,cameraHeading=0){return ['flights','military','ships'].includes(layer)&&Number.isFinite(heading)?cameraHeading-heading*Math.PI/180:0}
