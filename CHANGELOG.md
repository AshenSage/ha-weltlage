# Änderungen

## 1.1.2 · 11.10.2026

- Kartenressource wird beim HA-Start automatisch angelegt oder auf Version und Dateiprüfsumme aktualisiert; keine manuellen Versionsparameter bei Updates.
- Alte `/local/weltlage/weltlage-card.js`-Einträge werden migriert; doppelte eigene Einträge werden entfernt, andere Ressourcen bleiben erhalten. YAML-Ressourcen nur im Laufzeitspeicher angepasst.
- Ausschliesslich zwei öffentliche JavaScript-Endpunkte mit ausdrücklichem `no-store`; alte Query-Parameter liefern die aktuell installierten Dateien.
- Registrierung idempotent und nach einer teilweise fehlgeschlagenen Registrierung erneut ausführbar.

## 1.1.1 · 11.10.2026

- Kompakte Handy-Meldungen: drei Titelzeilen in der Vorschau, vollständiger Titel beim Öffnen; dauernd wiederholter Medienbericht-Badge entfällt.
- Suche, Sprach- und Quellenfilter mit Rücksetzen und sichtbarer Trefferzahl.
- Mehrere Themen pro Bericht, Konfliktbezug vor Energiebezug; erneute Zuordnung gespeicherter Artikel bei der Zusammenführung.
- Kartenversion direkt sichtbar, Integration und Globuseinstellung im Quellenbereich; unterschiedliche Versionen werden angezeigt.
- Regionaler Warnzähler trägt den konfigurierten Gebietsnamen.
- World-Monitor-Dialog mit flexibler Kartenhöhe und Platz für Bildschirmränder; Hinweis bleibt auch im Querformat sichtbar.

## 1.1.0 · 11.10.2026

- Drehbarer Globus direkt in der Karte mit Touch-/Tastaturbedienung, Zoom, grosser Ansicht, Tag/Nacht und sechs schaltbaren Ebenen.
- USGS-/GDACS-Ereignisse, Ortsmarken und als ungefähr gekennzeichnete regionale CAP-Marker antippbar.
- Öffentliche Flugaufnahme von adsb.lol im gewählten 250-sm-Ausschnitt auf Abruf; alte Positionen verschwinden nach 120 Sekunden.
- CelesTrak-Raumstationen-Bahndaten auf Abruf; lokale SGP4-Positionen und 90-Minuten-Bodenspur bei Auswahl.
- Begrenzter, persistenter Intel-Cache und Service `weltlage.fetch_intel`; grosse Attribute werden nicht im Recorder gespeichert.
- Bibliotheken und Landdaten lokal gebündelt; Drittanbieter-Lizenzen und reproduzierbare Build-/Vorschau-Skripte.

## 1.0.1 · 11.10.2026

- Bereitstellung als HACS Custom Repository (Integration).
- Kartenmodul in die Integration aufgenommen: HACS aktualisiert Backend und Karte zusammen.
- HA stellt ausschliesslich die Karten-Datei unter `/weltlage/weltlage-card.js` bereit; kein separater Kopiervorgang nach `www` nötig.
- Installationsanleitung für HACS und manuelle Installation aktualisiert.

## 1.0.0 · 11.10.2026

- Erste Version mit RSS-Nachrichten, USGS/GDACS, unabhängigen Quellenstatus und persistentem Cache.
- Mobile Dashboardkarte mit Regionen-, Themen- und Zeitfiltern, separaten CAP-Warnungen und optionaler World-Monitor-Karte.
- Eigene Bewertung des God’s-Eye-Repositorys und Bedienvorschau mit markierten Beispieldaten.
