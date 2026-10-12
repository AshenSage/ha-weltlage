# Weltlage 2.0.0-beta.1 · Cesium-Globus für Home Assistant

Diese **Vorabversion** macht den Cesium-Umbau über HACS installierbar. Das Release enthält keine persönlichen Schlüssel.

- Vollständiger Globus mit Atmosphäre, Aranđelovac im Zentrum und Home-/Schnellzielen.
- Mobile Werkzeugleiste, Kartenbasis und schaltbare Daten-Layer, Details, Kamerafavoriten und Objektverfolgung.
- Lokal gebündelte Cesium-Assets; kein zusätzlicher Node-Dienst.
- Authentifizierte, begrenzte HA-Datenadapter mit gemeinsamem Cache, Datenstatus und Abruflimits.
- Bestehender Kartentyp, CAP-Entitäten und automatische Ressourcenregistrierung bleiben erhalten.

## Installation über HACS

HACS → Weltlage → ⋮ → Erneut herunterladen → gegebenenfalls «Andere Version»/Vorabversionen anzeigen → `v2.0.0-beta.1` auswählen und herunterladen. Danach Home Assistant neu starten.

Einstellungen → Geräte & Dienste → Weltlage → Konfigurieren: die sechs optionalen Schlüssel eintragen. Für Mapillary den **Access/Client Token**, nicht den Client Secret verwenden. Die bestehende Dashboard-YAML funktioniert weiter. Keine manuelle Ressourcen-Version nötig.

## Prüfungen und Grenzen

63 Python-, fünf JS- und 20 Browserprüfungen bestehen. Ein isolierter HA-2026.10.1-Lauf bestätigt Einrichtung, Optionen, Reload, HTTP/WS und Unload mit einer nur im Testharness erforderlichen Netzwerkanpassung. Echte Daten-/Assetabrufe bestätigen unter anderem World Terrain, Google-Root-Tileset, TomTom, FIRMS, Mapillary bei Aranđelovac/Oberbipp und AIS bei Rotterdam.

**Offen:** breite Windy-Kameraabdeckung, regional gerenderte Google-3D-Gebäude, vollständige HACS-Migration auf einem bestehenden Gerät und reale Smartphone-/Raspberry-Pi-Performance. Overpass ist in der Arbeitsumgebung nicht erreichbar. Die Beta ist deshalb noch keine stabile Freigabe. Ausführliche Quellenmatrix: `docs/TEST_REPORT.md`.
