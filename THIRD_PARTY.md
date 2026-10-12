# Drittanbieter und Datenquellen

Der eigene Weltlage-Code steht unter MIT. Die folgenden Bibliotheken und Daten behalten ihre jeweiligen Lizenzen.

- Natural Earth Land 1:110m, Public Domain. [Original](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson), Koordinaten auf drei Nachkommastellen gerundet, Attribute entfernt.
- Laufzeit-Flugdaten: adsb.lol, ODbL 1.0. Keine Flug-Datenbank im Repository.
- Laufzeit-Bahndaten: CelesTrak, Dr. T.S. Kelso; OMM/SGP4 berechnete Positionen. Keine Bahndaten im Repository ausser ausdrücklich synthetischen Test-/Vorschaudaten.
- USGS / GDACS: Quellen bleiben bei den Ereignissen sichtbar.

Alle Skripte und Bibliotheken werden lokal von HA geliefert. Optional geladene Kamera-Standbilder und Esri-Hintergrundkacheln kommen direkt vom jeweiligen öffentlichen Anbieter.

- Natural Earth Land und Ländergrenzen 1:50m, Public Domain: [Land](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_land.geojson), [Grenzen](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_admin_0_boundary_lines_land.geojson). Attribute entfernt, Koordinaten gerundet, Linien mit Ramer-Douglas-Peucker (0.025°) vereinfacht. Grenzen sind Orientierungsdaten; kein politischer Anspruch.
- TfL JamCams: [Open Data und Bedingungen](https://tfl.gov.uk/info-for/open-data-users/our-open-data). Attribution: “Powered by TfL Open Data. Contains OS data © Crown copyright and database rights”. Bilder werden weder beschnitten noch umgefärbt.
- Fintraffic / Digitraffic: [CC BY 4.0 und Bedingungen](https://www.digitraffic.fi/en/terms-of-service/), [API](https://www.digitraffic.fi/en/road-traffic/). Attribution: “Fintraffic / digitraffic.fi · CC BY 4.0”. Katalogabrufe senden Digitraffic-User und Accept-Encoding: gzip.
- DriveBC: [Open Government Licence – British Columbia](https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc). Attribution: “DriveBC. Contains information licensed under the Open Government Licence – British Columbia”. Vorhandene Partner-Credits bleiben erhalten.
- Esri World Street Map: [Dienst](https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer), [Nutzungsbedingungen](https://www.esri.com/en-us/legal/terms/web-site-service). Attribution wird aus `copyrightText` der Dienstbeschreibung übernommen und über die sichtbaren Cesium-Datencredits angezeigt. Keine Kacheln im Repository, kein Offlinepaket. Älterer Rasterdienst: seit 2021 keine laufenden Updates; [geplante Einstellung Dezember 2029](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/announcements/sunsetting-legacy-basemaps).
- Esri World Imagery: [Dienst](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer), [Nutzungsbedingungen](https://www.esri.com/en-us/legal/terms/web-site-service). Aktuelle Attribution wird aus der Dienstbeschreibung gelesen und auf der sichtbaren Karte angezeigt; Rückfalltext entsprechend der beim Aufbau geprüften Dienstbeschreibung: “Esri, Vantor, Earthstar Geographics, and the GIS User Community”. Die Kacheln werden nur für den aktuellen Ausschnitt geladen und vorübergehend im Arbeitsspeicher des Browsers gehalten. Kein Offlinepaket und keine Bildkacheln im Repository.
- Der öffentliche TfL-Beispielkatalog in der Vorschau behält seine Attribution. Die veröffentlichten Test-Screenshots verwenden ausdrücklich synthetische DEMO-Kamerabilder.

## d3-geo

```text
Copyright 2010-2024 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

This license applies to GeographicLib, versions 1.12 and later.

Copyright 2008-2012 Charles Karney

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

```

## d3-array

```text
Copyright 2010-2023 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

```

## internmap

```text
Copyright 2021 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

```

## satellite.js

```text
MIT License

Copyright (C) 2013 Shashwat Kandadai, UCSC Jack Baskin School of Engineering

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```


## Cesium-Rework (2.0)

- CesiumJS 1.146.0: Apache-2.0, vollständige Lizenz und Fremdlizenzen im gebündelten `frontend/cesium/LICENSE.md` und Legal-Dateien. [CesiumJS](https://github.com/CesiumGS/cesium), [ion-Nutzungsbedingungen](https://cesium.com/legal/terms-of-service/). Die Browserdarstellung lässt die Cesium-/Datencredits sichtbar.
- God's Eye View, Commit 591f299, Bilawal Sidhu (2026): MIT **nur für Quellcode**. Unveränderte Module `satelliteClass.js` und `worldFocus.js`; vollständiger Hinweis in `frontend_src/vendor/GODS-EYE-LICENSE`. Keine extern lizenzierten Originalmodelle oder Nepal-Datensätze kopiert.
- Google Photorealistic 3D Tiles via Cesium ion: Anbieterbedingungen und Attribution bleiben verbindlich; verfügbare Regionen und Kontingente hängen vom Konto ab. Kein Offlinepaket und keine Zusage flächendeckender Abdeckung.
- OpenStreetMap / Overpass: ODbL, © OpenStreetMap contributors. [Kachelnutzungsregeln](https://operations.osmfoundation.org/policies/tiles/); kein Prefetch oder Offlinepaket.
- OpenTopoMap: © OpenStreetMap contributors, SRTM; Darstellung CC BY-SA. [Quelle und Hinweise](https://opentopomap.org/about).
- Windy API v3: Bilder und Webcam-Inhalte behalten ihre Anbieterrechte; [API-Bedingungen](https://api.windy.com/webcams/terms). Unveränderte API-URLs, keine Vergrösserung, Pflichtverlinkung und Courtesy-Hinweis. Free-Bildlinks verfallen gemäss Dokumentation nach zehn Minuten.
- TomTom: [Traffic API](https://developer.tomtom.com/traffic-api/documentation/traffic-flow/flow-segment-data), Anbieterbedingungen und Kontingente. Segmentdaten und Störungen werden getrennt und als unvollständige Anbieterinformationen bezeichnet.
- Mapillary: [Dokumentation](https://www.mapillary.com/developer/api-documentation/), Anbieterbedingungen und jeweilige Bildrechte. Foto-/Quelllink und Aufnahmedatum bleiben sichtbar; kein Live-Anspruch.
- AISStream: [Dokumentation](https://aisstream.io/documentation). Live empfangene, unvollständige öffentliche AIS-Positionsmeldungen; kein Archiv oder Abdeckungsgarantie.
- EMSC / Seismic Portal: [FDSN-Service](https://www.seismicportal.eu/fdsn-wsevent.html); Quelle, Magnitude, Tiefe und Datum werden angegeben.
- NASA FIRMS: [API](https://firms.modaps.eosdis.nasa.gov/api/), öffentlich verfügbare VIIRS-Daten, NASA-FIRMS-Attribution. Thermische Anomalien sind keine bestätigten Brände.
- NASA GIBS / MODIS Terra: [GIBS-Dokumentation](https://nasa-gibs.github.io/gibs-api-docs/). Datierte Tagesmosaike, keine Echtzeitaufnahme.
- RainViewer: [API](https://www.rainviewer.com/api.html). Beobachtete Radarframes; Quelle, Zeit und räumliche Lücken beachten.
- NOAA nowCOAST: [Dienst](https://nowcoast.noaa.gov/), globales Longwave-IR-Mosaik, sichtbare Zeitangabe; keine reine Wolkenmaske.
- Open-Meteo: [Lizenz und Bedingungen](https://open-meteo.com/en/terms), CC BY 4.0, Nutzung ohne Schlüssel nur gemäss Anbieterbedingungen; Wind ist eine Modellschätzung.
- TeleGeography: schematische Kabelgeometrien, CC BY-NC-SA 3.0 gemäss Original-Quellenkatalog; **keine kommerzielle Nutzung** ohne gesonderte Rechte. [Kabelkarte](https://www.submarinecablemap.com/).

Die oben erhaltenen älteren Natural-Earth/d3/TfL/DriveBC-Hinweise betreffen Vorgängercode. Der neue Cesium-Produktionsbuild enthält keine d3-/Natural-Earth-Basis und keinen TfL-/DriveBC-Layer.
