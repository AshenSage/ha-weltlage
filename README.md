# Weltlage · Cesium für Home Assistant

**2.0.1 ist das normale HACS-Release.** Der Rework ersetzt den Canvas-Globus durch lokal gebündeltes Cesium 1.146.0. Bestehende Karten behalten `custom:weltlage-card`, CAP-Entitäten und `alert_areas`; `max_items` und `show_globe` werden weiterhin akzeptiert. Künftige Veröffentlichungen verwenden normale Versionsnummern ohne Beta-Kanal.

Beim Öffnen erscheint die ganze Erde mit Atmosphäre und Aranđelovac im Bildzentrum. Die Kameradistanz richtet sich nach dem verfügbaren Bildbereich. Home stellt diese Ansicht wieder her. Schnellziele führen nach Aranđelovac, Balkan, Europa und Schweiz. Koordinaten: 44.30694 N, 20.56 E ([verifizierte Ortskoordinaten](https://www.geodatos.net/en/coordinates/serbia/arandelovac)). Die letzte Kameraposition wird bewusst nicht wiederhergestellt.

## Oberfläche

Globus, kompakte Werkzeugleiste und Layer darunter, ohne Nachrichten- oder Kennzahlenkarten. Ein Finger dreht, zwei Finger zoomen. Details, Verfolgung und Kamerafavoriten erscheinen unten. Kartenbasis: Karte (Esri World Street Map), Satellit, Hybrid, Topografie und Google Photorealistic 3D Tiles via ion. Das echte Höhenmodell ist separat schaltbar. Welt Terrain ist Asset 1; Google 3D ist Asset 2275207. Es gibt keine zweite Gebäudeschicht und deshalb keine überlagerten OSM-Gebäude.

Kartenstil, Layer, Satellitenkategorie, Effekte und Favoriten werden gerätebezogen im Browser gespeichert. Nachtsicht, FLIR und CRT sind ausdrücklich **visuelle Effekte**, keine Wärmebild- oder Erkennungsdaten. Suche umfasst geladene Objekte, Schnellziele und Eingaben `Breite,Länge`; eine weltweite Ortssuche ist noch nicht implementiert.

## Einrichtung und Update

1. Weltlage über HACS aktualisieren und Home Assistant neu starten.
2. Einstellungen → Geräte & Dienste → Weltlage → Konfigurieren. Die sechs optionalen Schlüssel lokal eingeben.
3. Dashboard neu laden. Bei einem alten Browsercache einmal vollständig neu laden. Die Lovelace-Ressource bekommt automatisch die installierte Version plus Build-Hash; keine manuelle Versionsnummer nötig.

Das normale GitHub-Release `v2.0.1` enthält `weltlage.zip`. In HACS → Weltlage → ⋮ → Erneut herunterladen die Version `v2.0.1` auswählen. Ein Beta-Schalter ist nicht erforderlich. Falls noch eine kurze Commit-Version wie `7571422` angeboten wird, zuerst die Repository-Informationen in HACS aktualisieren. Das ZIP enthält alle Cesium-Worker, Widgets, Bilder und JavaScript-Dateien. Ein zusätzlicher Node-Dienst ist nicht notwendig. Zugangsdaten werden nach dem Neustart lokal unter Geräte & Dienste → Weltlage → Konfigurieren eingegeben; die Veröffentlichung enthält keine persönlichen Schlüssel.

Zeigt «Konfigurieren» noch ausschliesslich die Beschreibung «Globus mit öffentlichen Verkehrskameras … USGS und GDACS werden alle fünf Minuten geprüft», läuft noch der Dialog aus 1.2.0. Nach dem HACS-Update Home Assistant vollständig neu starten und die Seite neu laden. Der neue Dialog zeigt sechs Passwortfelder sowie das Abruflimit. Die bestehende Weltlage-Einrichtung kann erhalten bleiben.

```yaml
type: custom:weltlage-card
title: Weltlage
show_globe: true
map_style: satellite
default_layers:
  - cap
storage_key: arandjelovac
alert_count_entity: sensor.cap_alerts_wmo_alert_count
alert_updated_entity: sensor.cap_alerts_wmo_last_updated
alert_areas:
  - RS010
alert_label: Serbien · Šumadija
```

`default_layers` gilt bei einem frischen Browserprofil. Bereits gespeicherte Einstellungen haben Vorrang. `map_style` kann `map`, `satellite`, `hybrid`, `topo` oder `photo` sein.

## Persönliche Schlüsseldatei

Optional können die sechs Felder aus `/config/weltlage_credentials.json` gelesen werden. Die Datei liegt **ausserhalb** von `custom_components/weltlage` und bleibt bei HACS-Updates erhalten. Vorhandene Einstellungen in HA haben Vorrang; ausdrücklich leere Felder deaktivieren eine Quelle. Beim Optionsdialog werden lokale Werte vorgeschlagen. Die Datei enthält ausschliesslich Zugangsdaten, keine Client-Secrets, und wird nicht über HTTP ausgeliefert oder in öffentliche Release-ZIPs gepackt. Ungültige Dateien verursachen eine verständliche Einrichtungsfehlermeldung.

Persönliche Werte werden nie im öffentlichen Repository hinterlegt. Wer eine eigene Datei verwendet, legt sie einmal in den HA-Konfigurationsordner und startet HA neu. Die veröffentlichten Pakete enthalten keine vorgegebenen Schlüssel.

## Schlüssel und Kontingente

| Lokales Feld | Verwendung |
|---|---|
| Cesium ion | Browser-Token für World Terrain und optional Google 3D; Zugriff auf Assets und erlaubte Origins beschränken |
| Windy Webcams API v3 | Backend-Katalog und Kameraeinzelabruf |
| TomTom | Backend-Verkehrsfluss und Störungen |
| Mapillary | Backend-Bildkatalog; die bereitgestellten Bilder werden im Browser geladen |
| NASA FIRMS | Backend-VIIRS-Hotspots |
| AISStream | Backend-AIS-WebSocket mit kurzen regionalen Empfangsfenstern |

Kein Schlüssel steht im Repository. Backend-Schlüssel werden nicht über die Globus-API an den Browser geschickt; notwendiger ion-Token, Bildlinks und externe Medien sind im Browser sichtbar. Diagnoseexporte enthalten nur boolesche Angaben über konfigurierte Schlüssel. Leere Felder deaktivieren die entsprechende Quelle. Die Eingabe validiert Form und Länge; die tatsächliche Gültigkeit wird beim ersten Abruf geprüft und separat gemeldet. Anbieterlimits gelten zusätzlich zum konfigurierbaren lokalen Tageslimit von standardmässig 500 Aufrufen je Quelle.

Keine bezahlten Upgrades werden vorgenommen. Kartenkacheln, ion-Assets und Bilder gehen direkt vom Browser zum Anbieter und werden nicht vom Backend-Tageslimit erfasst. Free-Tarife sind keine Zusage unbegrenzter Nutzung oder vollständiger Abdeckung.

## Daten und Grenzen

[Prüfbericht und Quellenmatrix](docs/TEST_REPORT.md) enthält die Live-Nachweise und offenen Punkte. Mapillary liefert maximal 20 Positionspunkte je Anfrage; der Ausschnitt darf höchstens 0,01 Quadratgrad umfassen. Einzelbilder werden erst beim Öffnen über den Backend-Token abgefragt.

Hauptlayer sind ADS-B, Satelliten, Windy, Fintraffic, Radar, globales IR, Windmodell, TomTom, AISStream, EMSC, FIRMS, Mapillary, NASA-Tagesmosaik, OSM-Infrastruktur, Kabel, GDACS und CAP.

Globale Kameradistanz löst keine unbegrenzten regionalen Abrufe aus. Kleine Layer melden «Näher zoomen». Ohne Treffer wird nicht automatisch «keine Abdeckung» behauptet. Satellitenpositionen werden aus maximal 14 Tage alten Bahnelementen in einem Worker berechnet. Windpfeile zeigen Modellrichtung. Flugspuren verbinden tatsächlich empfangene Positionssnapshots; sie sind keine Rekonstruktion des vollständigen Flugwegs. Radar läuft durch beobachtete Frames, deren Zeitpunkt an der Schaltfläche steht. Rasterzeiten sind Quellen-/Framezeiten, keine Garantie, dass jeder Pixel zur gleichen Zeit aufgenommen wurde.

Windy liefert maximal 50 Kameras pro Ausschnitt; eine mögliche Kürzung wird in der API-Antwort angegeben. Bilder werden erst beim Antippen geladen. API-Bildlinks werden unverändert benutzt, nicht hochskaliert und nicht in 3D projiziert. Anbieterzeit wird von Ladezeit unterschieden. Favoriten enthalten keine kurzlebigen Bildlinks. Quelle und Windy-Verlinkung sind sichtbar. [Dokumentation](https://api.windy.com/webcams/docs), [Bedingungen](https://api.windy.com/webcams/terms).

CAP verwendet verfügbare Warnpolygone. Ohne Geometrie ist nur eine ausdrücklich angenäherte Gebietsmitte Šumadija sichtbar. Mehrere Polygone einer Warnung werden derzeit auf das erste gültige Polygon begrenzt. GDACS zeigt orange/rote Meldungen ohne EQ-Duplikate.

## Architektur / Entwicklung

Authentifizierte Home-Assistant-WebSocket-Kommandos `weltlage/config`, `weltlage/layer` und `weltlage/camera` und `weltlage/streetphoto`. Validierte Layernamen, Grenzen, Filter und Datumsangaben; keine vom Client wählbaren Proxy-URLs. Gemeinsamer Backend-Cache, maximal drei parallele HTTP-Abrufe, begrenzte Antwortgrössen, Backoff und lokale Tageslimits. Grössere Kataloge gehen nicht in Recorder-Sensorattribute. Die bisherigen Sensor-/Button-IDs bleiben erhalten, die alten Hintergrundpolls werden gestoppt. Der Legacy-Service ist nur als begrenzter Aufruf erhalten.

```sh
npm ci
python -m pip install aiohttp
npm run build
npm test
npm run test:python
npx playwright install --with-deps chromium
npm run test:browser
npm run package
```

`npm run preview` startet eine lokale **UI-Vorschau mit simuliertem HA**. Sie liefert keine produktiven oder vorgetäuschten Live-Objekte. Die generierten Frontend-Dateien sind Build-Ausgabe und werden im HACS-ZIP statt als grosse, handgepflegte Git-Dateien verteilt. GitHub Actions baut und prüft das Review-Paket; der Release-Workflow verlangt eine zum Manifest passende Versionsmarke.

Zur Veröffentlichung Manifest, Package, Lockdatei und `VERSION` gemeinsam auf eine normale `x.y.z`-Version setzen, Release-Notizen aktualisieren und die geprüften Änderungen integrieren. Ein neuer Branch `release/vx.y.z` auf diesem Commit startet den Release-Workflow. Er prüft und baut das Paket, hängt das ZIP an einen Entwurf und veröffentlicht anschliessend ein normales, als «Latest» markiertes Release. Vorabversionsnummern werden vom Workflow abgewiesen.

## Original und Lizenzen

God's Eye View wurde auf Commit `591f299` untersucht. Übernommen: `satelliteClass.js` und `worldFocus.js` (MIT). Die vollständige Original-Lizenz liegt unter `frontend_src/vendor/GODS-EYE-LICENSE`. Dessen Node-Server, Sprachsteuerung, SDR, Nepal-Szene, synthetische Verkehrsdarstellung, USA-spezifische ÖV-/Radar-/Blitzlayer und lokale Fremddatensammlungen werden nicht übernommen. Fintraffic bleibt eine regionale Ergänzung; Windy ist als Hauptkatalog vorbereitet, aber regional noch nicht bestätigt. AMSS und Schweizer Spezialnetze sind ohne geprüfte Bildnutzung noch nicht integriert. Ein globaler CMR-Suchkatalog, Cockpitansicht und optionale Kamerapersistenz fehlen noch.

[Quellen- und Lizenzangaben](THIRD_PARTY.md).
