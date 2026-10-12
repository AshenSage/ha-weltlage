# Cesium-Rework: Prüfbericht / Fortsetzung

Stand: 12.10.2026. Branch `rework/cesium-2`; Ausgangsbasis `7ec0a4f` (1.2.0), Original God's Eye View `591f299`. **Entwurf: kein stabiles 2.0.0-Release veröffentlicht.**

## Reproduzierbare Prüfungen

- `npm run build`: Cesium-Karte, Satellite-Worker und lokale Runtime-Assets gebaut.
- `npm test`: 5 Prüfungen bestanden (Globusrahmen, Ortskoordinaten, valide Positionen, begrenzte Spur und Unterbrechung bei Beobachtungslücken).
- `npm run test:python`: 57 Prüfungen bestanden. Vorhandene Parser-/Coordinator-/Ressourcenprüfungen plus Cache-Sharing, Backoff, Datenalter, Schlüssel-/Extentzustände, Budget, Abbruch, XML-Sicherheit und neue Datenparser. Die HA-Schnittstellen sind dabei nachgebildet; das ist kein HA-Installationstest.
- Chromium 141 / SwiftShader: 20 Browserprüfungen bestanden, keine `pageerror`-Ereignisse. Breiten 320, 360, 390, 430 und 844 px; Hoch-/Querformat; kein horizontaler Seitenüberlauf; globales Zentrum; Schnellziel und Home; tatsächlicher Klick auf ein ausdrücklich synthetisches Flug-Testobjekt, Tracking und Schliessen; Zwei-Finger-Zoom; Layer ohne Schlüssel; Vollbild-Dock; Entfernen, Viewer-/Worker-Freigabe und Wiederöffnung.
- Globaler Zielpunkt nach Wiederöffnung: 44.30694025 N, 20.56000035 E. Der vollständige Globus passt mit Rand und Atmosphäre in den verfügbaren Bildbereich; geometrische Frustumprüfung plus Sichtprüfung.
- `npm run package`: vollständig gebündeltes `weltlage.zip` erstellt; Versionsgleichheit von Manifest und Build sowie erforderliche Worker-/CSS-Dateien geprüft.
- `git diff --check`: keine Whitespacefehler.

Die Browserprüfung verwendet die tatsächliche gebündelte Cesium-Karte. HA-WebSocket und Schlüssel-/Testobjektzustände sind nachgebildet. Esri-Metadaten und Kacheln werden **live** abgerufen; der Testadapter über `curl` behebt ausschliesslich die Netzwerkroute des Prüfbrowsers. Kein Testadapter ist Teil der produktiven HA-Integration. Die ersten Screenshots enthalten keine synthetischen Flugkontakte, sondern nur den echten Globus und seine Oberfläche. Die Testansicht ist oben eindeutig bezeichnet.

## Live-Datenmatrix

Diese Abrufe erfolgten in der Arbeitsumgebung, nicht auf dem Raspberry Pi und nicht im Hausnetz.

| Ebene / Quelle | Geprüfter Ausschnitt | Tatsächliches Ergebnis | Offener Nachweis / Grenze |
|---|---|---|---|
| ADS-B / adsb.lol | Serbien, Mittelpunkt nahe Aranđelovac, 250 NM | 245 bzw. beim Folgeabruf 251 valide Kontakte | Nicht das ganze sichtbare Rechteck garantiert; militärische Kennzeichnung aus `dbFlags`, keine Vollerfassung |
| CelesTrak Stationen | Globaler Katalog | 22 valide, ausreichend aktuelle Bahnelemente | Weitere Kategorien / dichter Starlink-Katalog noch nicht live geprüft |
| EMSC | Europa −25,34 bis 45,72 | 500 Ereignisse, 7 Tage, M≥1 | Ergebnislimit erreicht; nicht sämtliche Ereignisse |
| RainViewer | Europäische Sicht / globaler Framekatalog | Aktuelle beobachtete Radarframes | Regionale Stationen-/Pixelabdeckung nicht vollständig geprüft |
| NOAA globales IR | Europa 10,40 bis 30,55 | Zeitdimension gültig; echte PNG-Karte HTTP 200 | Nicht nördlich 60°; Aufnahmezeit ist nicht Abrufzeit |
| Open-Meteo Wind | Serbien | 25 valide Modellpunkte | Modell in 10 m Höhe, keine Windmessung |
| GDACS | Globaler Feed | Feed HTTP 200; 0 gültige orange/rote Meldungen im bestehenden Filter | Kein Fehler und kein Nachweis fehlender Ereignisse ausserhalb des Filters |
| TeleGeography | Globaler Kabelkatalog | 1500 geparste Linienabschnitte | Darstellung auf 1000 Objekte begrenzt, schematisch / statisch / nichtkommerziell |
| Fintraffic | Südfinnland 24,59 bis 26,61 | 238 Kamerapresets | Ergänzung für Finnland; kein Nachweis eines Schweizer/serbischen Kameranetzes |
| Esri World Imagery | Globaler Startglobe | Metadaten und echte Kacheln im Browser sichtbar | Nahansicht, Hybrid und regionale Auflösung nicht umfassend geprüft |
| OSM Kartenbasis | Weltkachel 0/0/0 | HTTP 200, PNG | Keine vollständige regionale Kachelprüfung |
| OpenTopoMap | Weltkachel 0/0/0 | HTTP 200, PNG | 3D-Terrain ist eine unabhängige ion-Quelle |
| NASA GIBS | MODIS Terra, 11.10.2026 | HTTP 200, JPEG | Tagesmosaik; keine regionale Wolkenfreiheit oder Aktualität jedes Pixels zugesagt |
| OSM Infrastruktur / Overpass | Serbien | Quelle in dieser Arbeitsumgebung nicht erreichbar; separater GET HTTP 406 | Staudämme, Rechenzentren und Militäranlagen nicht als funktionierend bestätigt |
| Windy Webcams | Geplante Tests Aranđelovac, Serbien/Balkan, Oberbipp/Schweiz, Österreich | **Nicht bestätigt** | Automatische Prüfung hat Verwendung des zuvor genannten Schlüssels blockiert; keine Trefferzahlen/Bilder als erfolgreich ausgewiesen |
| Cesium ion Terrain / Google 3D | Aranđelovac, Balkan, Schweiz | **Nicht geprüft** | Aktueller Token fehlt; Assetzugang und regionale 3D-Abdeckung müssen live geprüft werden |
| TomTom | Regionale Segmente / Störungen | **Nicht geprüft** | Schlüssel fehlt |
| Mapillary | Regionale historische Bilder | **Nicht geprüft** | Schlüssel fehlt |
| NASA FIRMS | VIIRS NOAA-20, 24 h | **Nicht geprüft** | Schlüssel fehlt |
| AISStream | Europäische Küsten / Häfen | **Nicht geprüft** | Schlüssel fehlt; Binnengewässer insbesondere Donau ohne Abdeckungsgarantie |
| CAP Alerts / RHMZ | RS010 in bestehender Karte | Parser und Darstellung vorbereitet | Aktuelle HA-Entitäten / Warnpolygone nicht aus dem Haus abgerufen |

## Freigabeblocker

1. Aktuelle sechs Zugangsdaten fehlen in dieser Sitzung; die Übernahme eines früher genannten Windy-Schlüssels wurde durch automatische Freigabeprüfung abgelehnt. Erst nach ausdrücklicher Freigabe bzw. Bereitstellung aktuelle Schlüsseltests ausführen. Schlüssel nie im Repository hinterlegen.
2. Broad-Camera-Abdeckung/Bilder für die vier verlangten Regionen sind noch nicht nachgewiesen. Es wird bewusst keine Europaabdeckung als erfolgreich behauptet.
3. World Terrain und Google Photorealistic 3D müssen mit dem tatsächlichen ion-Konto funktionieren; Token allein reicht nicht.
4. Upgrade in HA Core 2026.10.1, Config-/Optionsflow, authentifizierte WebSocket-Endpunkte und tatsächliche StaticPath-/Lovelace-Integration sind nicht in einer echten HA-Instanz getestet. Python-/Browser-Stubs ersetzen diesen Nachweis nicht.
5. Reales Android/iOS-Gerät, native Vollbild-Sonderfälle, Raspberry-Pi-Last, mehrere parallele echte Clients und länger laufende Ressourcenmessungen fehlen.
6. OSM-Infrastruktur scheitert aktuell am Quellzugang in dieser Umgebung; Ursache / geeigneter Endpunkt prüfen.

## Bewusste Grenzen des Entwurfs

- Weltweite Ortssuche fehlt; vorhanden sind geladene Objekte, Schnellziele und Koordinaten.
- Windy-Katalog maximal 50 Kameras pro Anfrage, räumliches Clustering im Browser. Eine begrenzte Liste ist keine flächendeckende Bestandsaussage.
- Verkehr ist eine reale Stichprobe von bis zu fünf TomTom-Segmenten, keine kontinuierliche komplette Strassenkarte. Die Anzeige nennt dies ausdrücklich.
- CAP zeigt das erste gültige Polygon je Warnung, sonst eine markierte Gebietsmitte.
- GIBS-Tagesdatum statt vollständiger CMR-Suche. AMSS-/Schweizer-Spezialquellen sind nicht ungeprüft ergänzt.
- Kein OSM-Buildings-Fallback, keine Cockpitansicht, keine gespeicherte letzte Kameraposition. Satelliten-/Schiffsverfolgung und vorhandene Flugspuren sind implementiert, aber nur der Flug-Testfall ist im Browser geprüft.
- Browser-Kachel-/ion-Aufrufe fallen ausserhalb des Backend-Tageslimits an. Das lokale Backend-Limit wird bei HA-Neustart zurückgesetzt und ersetzt keine Anbieterquota.
- Keine Produktionsinstallation, Freigabe oder belastbare Performancezusage aus der Desktop-SwiftShader-Prüfung ableiten.

## Nächste Schritte

1. GitHub-PR / Actions prüfen; Review-ZIP und Browserbilder aus dem Workflow verfügbar machen.
2. Schlüsseltests lokal unter ausdrücklicher Autorisierung durchführen, Resultate nur als redigierte Metadaten dokumentieren.
3. Windy-Verfügbarkeit, kurzlebige Bilder und ion-Abdeckung früh nachweisen. Bei fehlender Kameraabdeckung passende offizielle ergänzende Netze recherchieren und rechtlich/technisch prüfen.
4. HACS-Upgrade in einer echten HA-2026.10.1-Testinstanz sowie mobiles Gerät und Parallelclients prüfen.
5. Kritische Lücken schliessen; Manifest, Package und `VERSION` gemeinsam auf 2.0.0 ändern; erneut bauen/testen. Erst dann PR integrieren und einen passenden Release-Tag veröffentlichen. Release-Workflow hängt das vollständig gebündelte `weltlage.zip` an.

## Screenshots

Cesium-Prüfoberfläche mit echten Esri-Kacheln; HA simuliert, kein ion-Token. Bild-/Kartendaten © Esri und jeweilige Datenanbieter, siehe sichtbare Cesium-Datenattribution und THIRD_PARTY.md. Bildschirmaufnahmen dienen der UI-Prüfung und sind kein Nachweis einer Installation im Haus.

![Mobile Hochformatansicht](screenshots/cesium-mobile.png)

![Mobile Querformatansicht](screenshots/cesium-landscape.png)
