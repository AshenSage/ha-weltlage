# God’s Eye: Einschätzung für deine HA-Weltlage

Geprüft am 11.10.2026: **[bilawalsidhu/gods-eye-view](https://github.com/bilawalsidhu/gods-eye-view)**, das ursprüngliche God’s Eye View / WorldView. Da du keinen Link genannt hast, ist dies die gewählte Zuordnung. Ähnlich benannte Repositories können etwas anderes enthalten. Geprüft wurden die aktuelle Projektbeschreibung, Datenquellendokumentation und Einrichtungsangaben; kein vollständiges Code- oder Sicherheitsaudit.

Es bringt viele öffentliche Signale auf eine 3D-Erde. Der praktische Mehrwert liegt im räumlichen Erkunden. Die taktische Darstellung allein sagt nichts über Verlässlichkeit oder Vollständigkeit aus.

## Welche Informationen es tatsächlich liefert

| Ebene | Einordnung |
| --- | --- |
| Flugzeuge / militärisch markierte Kontakte | Öffentliche ADS-B-Daten über OpenSky/adsb.lol; keine vollständige Luftlage. Ohne Schlüssel startbar. |
| Schiffe | AISStream; Registrierung und Schlüssel erforderlich. |
| Satelliten | CelesTrak-Bahnelemente mit berechneten Positionen; keine Live-Spionagesatellitenbilder. |
| Erdbeben | USGS-Ereignisdaten; sinnvoll auch direkt als kompakter HA-Bereich. |
| Aktive Brände | NASA FIRMS; kostenloser Schlüssel erforderlich, Beobachtungsdaten mit Verzögerung. |
| Wetter | Radar/Clouds und Modellvorhersagen; Beobachtung und Prognose auseinanderhalten. |
| Öffentliche Kameras | Ausgewählte regionale Kamerafeeds; die Kameraperspektiven sind geschätzt. Keine beliebige Kameraabdeckung deines Wohnorts. |
| Strassenverkehr | Simulierte Fahrzeuge. Optional beeinflussen TomTom-Verkehrsgeschwindigkeiten die Simulation; Einzelpositionen sind keine Live-Beobachtungen. |
| FLIR / Nachtsicht | Shader-Stile über der Szene; keine echten Wärmebilder. |

Grundfunktionen starten ohne Schlüssel. Für fotorealistische 3D-Daten gibt es Cesium-ion-Zugang für berechtigte private, nicht kommerzielle Nutzung innerhalb der Bedingungen/Quoten; die direkte Google-Variante ist verbrauchsabhängig abgerechnet. OpenAI-Sprachfunktionen sind optional und über den regulären API-Zugang zusätzlich kostenpflichtig.

## Was ich für uns übernehmen würde

**Seit Weltlage 1.1.0 direkt in HA:** drehbarer Globus, öffentliche ADS-B-Flugaufnahme im gewählten Ausschnitt, ISS-/Raumstationen-Bahndaten mit lokaler SGP4-Berechnung und antippbare USGS-/GDACS-Ereignisse. CAP und statische Ortsmarken ergänzen den räumlichen Blick. Quelle, Aufnahmealter und berechnete Satellitenpositionen sind gekennzeichnet. Die Datenquellen-Ideen stammen aus dem Repo; dessen Code oder 3D-Modelle wurden nicht kopiert.

**Danach:** God’s Eye separat auf einem Rechner oder eigenen Server betreiben und über «3D Intel öffnen» aufrufen. Für deine Anwendung wären Balkan/Europa, Flughäfen, Wetter und grössere Naturereignisse gute Einstiege. Satelliten sind eine interessante Zusatzansicht; aus ihrer blossen Nähe sollte kein Gefahrenalarm entstehen.

Die separate Ansicht bleibt die Option für den vollständigen God’s-Eye-Umfang, insbesondere fotorealistische 3D-Daten, AIS-Schiffe oder weitere Kameras. Unser eigener Globus wurde in Chromium bei Handybreiten geprüft; die ursprüngliche God’s-Eye-App wurde nicht auf deinem Handy gemessen. Ich habe das Repo nicht auf deinem Gerät gestartet. Ein eigener Rechner/Server ist ebenfalls noch nicht eingerichtet.

**Später bei Bedarf:** einzelne zusätzliche Datenquellen direkt in die HA-Integration übernehmen, etwa FIRMS-Brände. Dabei bleiben Quelle, Alter, Schwelle und räumlicher Bezug sichtbar. Eine God’s-Eye-Oberfläche ist keine vorausgesetzte HA-Daten-API.

## Technischer Einstieg

Das Projekt nennt Node 24.x ab 24.14 bzw. 26.x und diesen lokalen Startweg:

```bash
git clone https://github.com/bilawalsidhu/gods-eye-view.git
cd gods-eye-view
npm ci
npm run doctor
npm run dev
```

Standardadresse ist `http://localhost:4173`. Für Handy-Zugriff braucht es eine erreichbare eigene Adresse; dafür die [LAN-/Server-Hinweise des Projekts](https://github.com/bilawalsidhu/gods-eye-view/blob/main/SECURITY.md) befolgen. In Weltlage lässt sich diese später per `intel_url` hinterlegen.

Quellen: [README](https://github.com/bilawalsidhu/gods-eye-view), [DATA_SOURCES.md](https://github.com/bilawalsidhu/gods-eye-view/blob/main/DATA_SOURCES.md). Anbieterbedingungen und Quoten können sich ändern.
