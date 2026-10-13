# Prüfung · Weltlage 1.2.0

> Historischer Prüfbericht vom 11.10.2026 für Version 1.2.0. Die damalige Canvas-Oberfläche, Testbefehle und Funktionsgrenzen beschreiben diese frühere Ausgabe. Aktuell ist das normale Release **2.1.1** mit Cesium. Aktuelle Installation und Testbefehle stehen in der [README](README.md), die aktuelle Patchprüfung und datierte Quellen-Nachprüfungen im [Prüfbericht](docs/TEST_REPORT.md).

Stand: 11.10.2026. Ziel: Home Assistant 2026.10 oder neuer. Die neue Ausgabe wurde lokal geprüft. Die vorherige Globusversion 1.1.2 wurde vom Nutzer in seiner HA-Ansicht bestätigt; 1.2.0 wurde noch nicht auf seinem Gerät installiert.

| Prüfung | Ergebnis |
| --- | --- |
| Backend | 43 Python-Tests bestanden. Quellenbegrenzung ohne RSS-Abfragen, echte HTTP-Abrufe am lokalen Testserver, Datenverarbeitung, Fehler, Grössenlimit, 304, Speicherung, manuelle Abrufgrenzen und alte Parserregressionen. |
| Kameraquellen | Drei offizielle Kataloge tatsächlich geladen und verarbeitet: TfL, Fintraffic, DriveBC. Je ein echtes JPEG erfolgreich geladen. Die zum Prüfzeitpunkt vorhandenen Katalogmengen sind keine Garantie künftiger Verfügbarkeit. NSW-Katalog erreichbar, alle fünf geprüften Beispielbilder lieferten einen HTML-Ausfallhinweis; deshalb nicht aktiviert. |
| Kamera-Parser | Nur gültige Koordinaten und veröffentlichte, aktive Ansichten; HTTPS, feste Bildhosts und Pfade. Inaktive Fintraffic-Presets und veraltete DriveBC-Kameras entfallen. Doppelte Kameras, Herkunft, Partner-Credits und Maximalmenge geprüft. |
| Kamerakataloge im Datensammler | Abruf nur auf Anforderung, getrennter Zustand pro Netz, Stundenlimit, Fehler behalten die letzten Daten, Persistenz, Identifikations- und Kompressionsheader; unbekannte Netze werden abgelehnt. |
| Frontend-Ressourcen | Die vorhandenen acht Tests für echte HTTP-Antworten, `no-store`, Migration alter Ressourcen, fremde Ressourcen, YAML-Laufzeitliste und Teilfehler bleiben erfolgreich. |
| Browserunabhängige Logik | 16 Node-Tests bestanden: CAP, Datenalter, HTML/Links, Koordinaten, Flugfrische, Satellitenfehler, Flugregion, Kamera-Hosts und Cluster; zusätzlich Mercator, feste Bildkachelquelle, Datumsgrenzen und Dreiecksprojektion. |
| DOM | 18 jsdom-Prüfungen bestanden: nur Globus, alte YAML-Optionen, Titel, Ebenen, Serviceaufrufe und Abstände, Kameradaten, Vollbild-Lifecycle, neuer Editor und fehlende Einrichtung. |
| Echter Chromium-Browser | 45 Prüfungen bestanden: 320/360/390/430/1060 px ohne horizontalen Überlauf; Drehen, Tastatur, echter Touch-Pinch, Auswahl, Ebenen und Abrufe; ISS-Folgen und Abbruch beim Drehen, Kameracluster, Suche, Bildladen erst bei Auswahl, Originalbildformat und Attribution, fehlgeschlagenes Bild behält letzten erfolgreichen Stand. |
| Vollbild | 320×640, 390×844 und 844×390; mehr als 70 Prozent des Dialogs für den Globus, keine abgeschnittene Dialoghöhe, Escape und Schliessen. |
| Speicherung / Sichtbarkeit | Blickrichtung, Zoom und Ebenen über Reload erhalten; 60-Sekunden-Modus startet ausgeschaltet. Verborgene Karte erzeugt keine Flugabrufe, sichtbare Karte kann wieder abrufen; veraltete Flugpositionen entfallen. |
| Satellitenhintergrund | Esri-Dienstbeschreibung und echte JPEG-Kacheln erfolgreich geladen; CORS vorhanden. Chromium zeichnet den echten Hintergrund. Kontrollierter Browsertest mit markierten DEMO-Kacheln: kein Abruf vor Aktivierung, begrenzte Anfragen, sichtbare dynamische Attribution, Pause bei verborgener Ansicht und Wechsel zurück zur Vektordarstellung. |
| Module statt nur Demo-Bundle | Beide tatsächlich ausgelieferten JavaScript-Dateien über lokalen HTTP-Server importiert und Karte initialisiert; keine JavaScript-Fehler. |
| Paket | Syntax, JSON, YAML und Prüfsummen geprüft. Keine Exportdaten, Zugangsdaten, Bilder der Kameraprovider, node_modules oder temporären Arbeitsdateien im Paket. |

## Praktische Grenzen

Die Browserprüfung ersetzt keine Messung in der Android-/iOS-Companion-App oder auf dem HA-Rechner. Die Integration verwendet für Scheduling und Storage kleine Testadapter; HACS-Download, HA-Neustart und die neue Service-Registrierung werden nicht durch eine laufende HA-Installation getestet.

Provider können Bilder unterbrechen oder Platzhalter liefern. Ein erfolgreicher Bilddownload ist keine Garantie für eine neue Aufnahme. Kamerabildstatus nennt den Zeitpunkt des Ladens, nicht eine erfundene Aufnahmezeit. Die drei Kameranetze decken nur ihre Regionen ab; CH/RS haben in dieser Ausgabe kein Kameranetz.

Esri ist ein externer, wählbarer Hintergrunddienst. Bilder sind keine Live-Satellitenaufnahmen und die Karte enthält keine fotorealistischen 3D-Gebäude. Bei fehlenden Kacheln bleibt die Vektorbasis erhalten. Die Prüfungsumgebung benötigt für externe Chromium-Anfragen ihre Netzwerk-Proxy-/Zertifikatskonfiguration; solche Anpassungen sind kein Bestandteil der ausgelieferten Karte.

Die veröffentlichten Bildschirmbilder zeigen klar markierte Demo-Ereignisse und Demo-Kamerabilder. Testadapter führen keine echten HA-Serviceaufrufe aus. Die echte Kamera wird erst auf dem Gerät des Nutzers vom Anbieter geladen.

## Selbst ausführen

```bash
npm ci
npm run build
npm run preview
python3 -m unittest discover -s tests -v
npm test
npm run test:dom
npm run test:browser
```

Für Python werden Python 3.12+ und aiohttp benötigt. Die Browserprüfung benötigt Chromium (`npx playwright install chromium --only-shell`). JS-Testabhängigkeiten laufen nur in der Entwicklung und werden nicht in Home Assistant installiert.
