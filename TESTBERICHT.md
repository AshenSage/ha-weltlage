# Prüfung · Weltlage 1.1.2

Stand: 11.10.2026. Für Home Assistant 2026.10.0 oder neuer. **Version 1.1.2 wurde lokal geprüft; ihr Betrieb in einer laufenden Home-Assistant-Instanz wurde nicht verifiziert.**

## Erfolgreich geprüft

| Prüfung | Ergebnis |
| --- | --- |
| Python-Verarbeitung und Datensammler | 28 Tests bestanden. RSS/Atom, Datumsangaben, HTML-Bereinigung, Links, Zusammenführung, Aufbewahrung, Naturereignisse sowie mehrere Themen und erneute Themenzuordnung gespeicherter Meldungen. |
| HTTP-Verhalten des tatsächlichen Datensammlers | Lokaler HTTP-Testserver: ein Feed funktioniert, ein Feed fällt aus; bedingter Abruf mit 304; beschädigte/überdimensionierte Antwort; Speicherung; Wiederholungsabstand; manueller Abruf. |
| Karte, HTTP-Pfade und Ressourcenaktualisierung | 8 Tests bestanden: genau zwei öffentliche JavaScript-Endpunkte; tatsächliche aiohttp-Antworten mit `no-store`, auch bei altem Query und bedingtem Abruf. Automatisches Anlegen, Migration alter URLs mit gleicher ID, Entfernen doppelter eigener Einträge, unveränderte fremde/externe Ressourcen, keine zusätzlichen Schreibvorgänge beim Wiederholen, neuer Ressourcenparameter bei verändertem Dateistand, YAML nur im Laufzeitspeicher und Wiederholung nach Teilfehler. HA-View- und Collection-Schnittstellen durch Testadapter ersetzt. |
| Intel-Abrufe | Feste API-Hosts, 2-MB-Grenze, gültige Koordinaten und Bahndaten, Aufnahmealter, 60-s-/2-h-Abstände, Fehlerstatus und Cache-Speicherung geprüft. Kein Abruf ohne ausdrückliche Anfrage. |
| Chromium-Bedienung | 32 Prüfungen bestanden. Handybreiten 320/360/390/430 und Desktop 1060 Pixel: keine seitlichen Überstände; Ziehen, Tastatur, Touch-Pinch, Punkt-/Listenauswahl, Ebenen, Intel-Anfrage, Bodenspur, native grosse Dialogansicht, Escape, Ausblenden und tatsächliche ESM-Dateien über lokale HTTP-Pfade geprüft. Zusätzlich: kompakte lange kyrillische Titel und vollständiges Aufklappen, kombinierte Sprach-/Quellenfilter, Suche ohne Fokusverlust und Versionshinweis. World-Monitor-Dialog bei 320×640, 390×844 und 844×390: Kopf und Hinweis innerhalb des Bildschirms, positive Kartenhöhe. Externe Karte dabei durch synthetischen iframe-Inhalt ersetzt; geprüft wird das Dialoglayout, nicht die Anbieterantwort. |
| Direkte öffentliche APIs | adsb.lol-Punktabfrage und CelesTrak-Raumstationen-OMM-JSON haben am 11.10.2026 aus der Entwicklungsumgebung geantwortet. Das ist keine Erreichbarkeitsprüfung aus deiner HA-Installation. |
| Reine Kartenlogik | 14 Node-Tests bestanden: Mehrfachthemen, Suchwörter, Sprache/Quelle, Region/Zeit, Datenalter, Links/HTML, CAP-Stufen, Aktiv/Kommend, Ablauf, Doppelte und fehlende/veraltete Warnquellen. |
| DOM-Bedienlogik | 45 Assertions bestanden mit jsdom: tatsächlicher Kartencode, Filter, weitere Meldungen, erneute Konfiguration, offene Details, Aktualisieren-Aufruf, Karten-URL und Entfernen des Frames, wiederholte Editoränderungen, gespeicherte Daten bei Fehlern, leere Einrichtung; Suche, kombinierte Filter, Trefferzahl, kompakter Editor und Versionsunterschiede. |
| CAP-Regressionsprüfung am Export | Alle 28 exportierten CAP-Einträge zum Exportzeitpunkt geprüft. Filter `RS010`: 0 besondere aktive und 0 besondere kommende Warnungen. Grüne Einträge bleiben ausserhalb der Alarmzahl. |
| Syntax und Paket | Python-Kompilierung, JavaScript-Syntax, JSON und YAML geprüft. Veröffentlichte Dateien enthalten keine Exportdaten, Zugangsdaten, node_modules oder temporären Dateien. |

Die CAP-Regressionsprüfung beschreibt **den Exportzeitpunkt**, keine heutige Wetterlage. Der Originalexport bzw. private Testdaten daraus werden nicht mitgeliefert.

## Noch nicht geprüft

- **Laufende Home-Assistant-Integration:** Konfigurationsdialog, Entitätsregistrierung, Registrierung der HTTP-Views und automatische Ressourcenverwaltung, HACS-Download und Neustart in einer echten HA-2026.10-Instanz. In den lokalen Coordinator-Tests sind nur HA-Scheduling und Storage durch kleine Testadapter ersetzt; HTTP und Parser laufen als tatsächlicher Projektcode.
- **Live-Abruf aller Feeds durch HA:** Quellenadressen wurden anhand öffentlicher Anbieterinformationen ausgewählt/geprüft. Ein kompletter Live-Abruf aus dieser Ausführungsumgebung war nicht möglich. Beim Installieren den Quellenstatus kontrollieren.
- **Echtes Android-/iOS-Gerät, Companion App und Geräte-Leistung:** Rendering und Touch-Ereignisse sind in Chromium geprüft. Das ersetzt keine Messung auf deinem Handy. Lange Nutzung, Akkuverbrauch und HA-WebView wurden nicht geprüft.
- **Eingebettete World-Monitor-Antwort:** Das externe iframe wurde nicht auf heutige Vollständigkeit oder Erreichbarkeit geprüft. Die native grosse Globusansicht wurde hingegen in Chromium geöffnet und geschlossen.
- **God’s-Eye-Laufzeit:** Repo-Dokumentation und Datenquellen bewertet, Anwendung nicht auf deinem System installiert und keine API-Schlüssel eingerichtet.

Die separat enthaltene `VORSCHAU.html` zeigt den tatsächlichen Kartencode mit **klar markierten Beispieldaten** und kann auf dem Handy geöffnet werden. Ihre simulierten grünen Quellenstatus sind keine Prüfung der Internetanbieter.

## Tests selbst ausführen

Im entpackten Paket, für die Python-Tests mit Python 3.12+ und `aiohttp`:

```bash
python3 -m unittest discover -s tests -v
```

Für die 14 JavaScript-Tests genügt Node ohne Zusatzpakete:

```bash
npm test
```

Der zusätzliche DOM-Test benötigt Node 24 und die Testabhängigkeit jsdom. Diese ist **keine Abhängigkeit der HA-Karte**:

```bash
npm ci
npm run test:dom
```

## Nach der Installation kontrollieren

1. Nach HA-Neustart ist genau eine Weltlage-Modulressource automatisch auf dem installierten Stand. Nach App-Neuladen steht «Karte 1.1.2» da; ein manuelles Ändern der URL ist nicht nötig. Weltlage-Lagebild und Quellenstatus sind vorhanden. Mindestens die gewünschten Nachrichtenquellen melden erfolgreiche Abrufe.
2. Oben «Karte 1.1.2» und unter Quellen die Integrationsversion prüfen. Welt → CH/RS → Serbien wechseln. Thema, Zeitraum, Sprache und Quelle ändern; suchen und Filter zurücksetzen. Langen Titel vollständig aufklappen; «Weitere» öffnen.
3. CAP-Zeitstempel ist aktuell. Grüne Meldungen bleiben ohne Alarmzahl; abgelaufene Warnungen verschwinden. Bei veralteter CAP-Quelle steht «Warnstatus prüfen».
4. Handy hochkant: Globus drehen und mit zwei Fingern zoomen; «Gross» öffnen/schliessen. Erdbeben antippen. «Flüge laden» und «Satelliten laden» prüfen; bei Ausfall muss ein Datenhinweis erscheinen. World-Monitor-Karte zusätzlich öffnen/schliessen.
5. Nach einem HA-Neustart und einem vorübergehenden Quellenfehler prüfen, ob gespeicherte Meldungen sichtbar bleiben und ihr Datenstatus stimmt.
