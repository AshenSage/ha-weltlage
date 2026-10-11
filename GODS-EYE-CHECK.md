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

## Was jetzt direkt in HA enthalten ist

**Weltlage 1.2.0 konzentriert sich ausschliesslich auf den Globus.** Neben ADS-B, SGP4, USGS, GDACS und CAP enthält die eigene HA-Karte nun öffentliche TfL-, Fintraffic- und DriveBC-Kameras mit Bildansicht, Kameracluster, ISS-Folgen, optionaler Flugaktualisierung und einen wählbaren Esri-Satellitenhintergrund. Das grüne taktische Erscheinungsbild ist ein Darstellungsstil. Aufnahmen, Beobachtungen und berechnete Positionen sind getrennt gekennzeichnet.

Nachrichtenbereich und World-Monitor-Iframe wurden entfernt. Die Datenquellen-Ideen stammen aus dem ursprünglichen Repo; dessen Code, 3D-Modelle und Kameraprojektionen wurden nicht kopiert. Eine separate Installation ist für den eigenen HA-Globus nicht erforderlich.

Nicht enthalten: Google-/Cesium-Fotorealismus mit 3D-Gebäuden, AIS-Schiffe, NASA-FIRMS-Schlüsselquellen oder eine freie weltweite Kameraabdeckung. Die ursprüngliche God’s-Eye-App wurde nicht auf dem Gerät des Nutzers installiert. Die folgenden Startangaben dienen nur als Referenz zum fremden Projekt.

## Technischer Einstieg

Das Projekt nennt Node 24.x ab 24.14 bzw. 26.x und diesen lokalen Startweg:

```bash
git clone https://github.com/bilawalsidhu/gods-eye-view.git
cd gods-eye-view
npm ci
npm run doctor
npm run dev
```

Standardadresse ist `http://localhost:4173`. Für Handy-Zugriff braucht es eine erreichbare eigene Adresse; dafür die [LAN-/Server-Hinweise des Projekts](https://github.com/bilawalsidhu/gods-eye-view/blob/main/SECURITY.md) befolgen. Eine separate Installation ist unabhängig von der neuen HA-Globuskarte.

Quellen: [README](https://github.com/bilawalsidhu/gods-eye-view), [DATA_SOURCES.md](https://github.com/bilawalsidhu/gods-eye-view/blob/main/DATA_SOURCES.md). Anbieterbedingungen und Quoten können sich ändern.
