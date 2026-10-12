# Weltlage 2.0.0 · Cesium-Globus für Home Assistant

Dieses normale Release macht den Cesium-Umbau über HACS installierbar, ohne einen Beta-Schalter zu benötigen. Es ersetzt die frühere Vorabversion als neuestes Release. Das Paket enthält keine persönlichen Schlüssel.

- Vollständiger Globus mit Atmosphäre, Aranđelovac im Zentrum und Home-/Schnellzielen.
- Mobile Werkzeugleiste, Kartenbasis und schaltbare Daten-Layer, Details, Kamerafavoriten und Objektverfolgung.
- Lokal gebündelte Cesium-Assets; kein zusätzlicher Node-Dienst.
- Authentifizierte, begrenzte HA-Datenadapter mit gemeinsamem Cache, Datenstatus und Abruflimits.
- Bestehender Kartentyp, CAP-Entitäten und automatische Ressourcenregistrierung bleiben erhalten.

## Installation über HACS

HACS → Weltlage → ⋮ → Erneut herunterladen → `v2.0.0` auswählen und herunterladen. Falls HACS noch eine Commit-Version wie `7571422` anzeigt, zuerst die Repository-Informationen aktualisieren. Danach Home Assistant vollständig neu starten und die Seite neu laden.

Einstellungen → Geräte & Dienste → Weltlage → Konfigurieren: die sechs optionalen Schlüssel eintragen. Für Mapillary den **Access/Client Token**, nicht den Client Secret verwenden. Die bestehende Dashboard-YAML funktioniert weiter. Keine manuelle Ressourcen-Version nötig.

Der bisherige 1.2.0-Konfigurationsdialog enthält nur eine Beschreibung. Mit dem aktualisierten Integrationscode und nach dem Neustart erscheinen sechs Passwortfelder sowie das Abruflimit; die bestehende Einrichtung muss dazu nicht gelöscht werden.

## Prüfungen und Grenzen

63 Python-, fünf JS- und 20 Browserprüfungen bestehen. Ein isolierter HA-2026.10.1-Lauf bestätigt Einrichtung, Optionen, Reload, HTTP/WS und Unload mit einer nur im Testharness erforderlichen Netzwerkanpassung. Echte Daten-/Assetabrufe bestätigen unter anderem World Terrain, Google-Root-Tileset, TomTom, FIRMS, Mapillary bei Aranđelovac/Oberbipp und AIS bei Rotterdam.

**Offen:** breite Windy-Kameraabdeckung, regional gerenderte Google-3D-Gebäude, vollständige HACS-Migration auf einem bestehenden Gerät und reale Smartphone-/Raspberry-Pi-Performance. Overpass ist in der Arbeitsumgebung nicht erreichbar. Die Veröffentlichung im normalen Release-Kanal ist kein zusätzlicher Nachweis für diese noch offenen Prüfungen. Ausführliche Quellenmatrix: `docs/TEST_REPORT.md`.
