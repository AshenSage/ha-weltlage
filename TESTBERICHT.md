# Prüfung · Weltlage 1.0.1

Stand: 11.10.2026. Gebaut für die Konfiguration im bereitgestellten HA-Export (Home Assistant 2026.10.0). **Das Paket ist nicht in der laufenden HA-Instanz installiert.**

## Erfolgreich geprüft

| Prüfung | Ergebnis |
| --- | --- |
| Python-Verarbeitung und Datensammler | 18 Tests bestanden. RSS/Atom, Datumsangaben, HTML-Bereinigung, Links, Zusammenführung, Aufbewahrung und Naturereignisse. |
| HTTP-Verhalten des tatsächlichen Datensammlers | Lokaler HTTP-Testserver: ein Feed funktioniert, ein Feed fällt aus; bedingter Abruf mit 304; beschädigte/überdimensionierte Antwort; Speicherung; Wiederholungsabstand; manueller Abruf. |
| Mitgelieferte Karte / HTTP-Pfad | 3 Tests bestanden: ausschliesslich die Karten-Datei wird bereitgestellt, kein Langzeit-Cache, keine doppelte Registrierung beim Neuladen; nach Fehler erneut registrierbar. Bestehende Lovelace-Ressourcen bleiben unberührt. |
| Reine Kartenlogik | 10 Node-Tests bestanden: Filter, Datenalter, Links/HTML, CAP-Stufen, Aktiv/Kommend, Ablauf, Doppelte und fehlende/veraltete Warnquellen. |
| DOM-Bedienlogik | 35 Assertions bestanden mit jsdom: tatsächlicher Kartencode, Filter, weitere Meldungen, erneute Konfiguration, offene Details, Aktualisieren-Aufruf, Karten-URL und Entfernen des Frames, wiederholte Editoränderungen, gespeicherte Daten bei Fehlern, leere Einrichtung. |
| CAP-Regressionsprüfung am Export | Alle 28 exportierten CAP-Einträge zum Exportzeitpunkt geprüft. Filter `RS010`: 0 besondere aktive und 0 besondere kommende Warnungen. Grüne Einträge bleiben ausserhalb der Alarmzahl. |
| Syntax und Paket | Python-Kompilierung, JavaScript-Syntax, JSON und YAML geprüft. ZIP enthält keine Exportdaten, Zugangsdaten, Entwicklungsabhängigkeiten oder temporären Dateien. |

Die CAP-Regressionsprüfung beschreibt **den Exportzeitpunkt**, keine heutige Wetterlage. Der Originalexport bzw. private Testdaten daraus werden nicht mitgeliefert.

## Noch nicht geprüft

- **Laufende Home-Assistant-Integration:** Konfigurationsdialog, Entitätsregistrierung, statischer HTTP-Pfad, HACS-Download und Neustart in einer echten HA-2026.10-Instanz. In den lokalen Coordinator-Tests sind nur HA-Scheduling und Storage durch kleine Testadapter ersetzt; HTTP und Parser laufen als tatsächlicher Projektcode.
- **Live-Abruf aller Feeds durch HA:** Quellenadressen wurden anhand öffentlicher Anbieterinformationen ausgewählt/geprüft. Ein kompletter Live-Abruf aus dieser Ausführungsumgebung war nicht möglich. Beim Installieren den Quellenstatus kontrollieren.
- **Visuelles Rendering, tatsächliche Touch-Bedienung und Leistung auf dem Handy:** Der Browser-Download scheiterte; der verfügbare Browser konnte die lokale Vorschau nicht erreichen. Es liegt keine bestandene Browserprüfung bei 360/390/430 Pixeln oder auf einem echten Mobilgerät vor. Die CSS-Auslegung ist einspaltig mit grossen Bedienelementen, aber dies ersetzt keinen Gerätetest.
- **Native Dialogdarstellung und eingebettete World-Monitor-Antwort:** jsdom besitzt keine Layout-Engine. Nur der Dialog-Lebenszyklus wurde im DOM-Test ersetzt; das externe iframe wurde dabei nicht tatsächlich geladen.
- **God’s-Eye-Laufzeit:** Repo-Dokumentation und Datenquellen bewertet, Anwendung nicht auf deinem System installiert und keine API-Schlüssel eingerichtet.

Die separat enthaltene `VORSCHAU.html` zeigt den tatsächlichen Kartencode mit **klar markierten Beispieldaten** und kann auf dem Handy geöffnet werden. Ihre simulierten grünen Quellenstatus sind keine Prüfung der Internetanbieter.

## Tests selbst ausführen

Im entpackten Paket, für die Python-Tests mit Python 3.12+ und `aiohttp`:

```bash
python3 -m unittest discover -s tests -v
```

Für die 10 JavaScript-Tests genügt Node ohne Zusatzpakete:

```bash
npm test
```

Der zusätzliche DOM-Test benötigt Node 24 und die Testabhängigkeit jsdom. Diese ist **keine Abhängigkeit der HA-Karte**:

```bash
npm ci
npm run test:dom
```

## Nach der Installation kontrollieren

1. Weltlage-Lagebild und Quellenstatus sind vorhanden. Mindestens die gewünschten Nachrichtenquellen melden erfolgreiche Abrufe.
2. Welt → CH/RS → Serbien wechseln. Thema und Zeitraum ändern; Details und «Weitere» öffnen.
3. CAP-Zeitstempel ist aktuell. Grüne Meldungen bleiben ohne Alarmzahl; abgelaufene Warnungen verschwinden. Bei veralteter CAP-Quelle steht «Warnstatus prüfen».
4. Handy hochkant: kein horizontaler Bildlauf, lesbare Meldungstitel und erreichbare Schaltflächen. Weltkarte separat öffnen und schliessen.
5. Nach einem HA-Neustart und einem vorübergehenden Quellenfehler prüfen, ob gespeicherte Meldungen sichtbar bleiben und ihr Datenstatus stimmt.
