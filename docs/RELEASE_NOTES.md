# Weltlage 2.0.1 · Kartenbasis und Cesium-Authentifizierung

Dieses normale HACS-Release korrigiert zwei Fehler aus 2.0.0. Es enthält keine persönlichen Schlüssel.

- «Karte» verwendet Esri World Street Map. Die Karte benötigt keinen zusätzlichen Schlüssel und hängt nicht mehr von den Standard-OSM-Kacheln ab, die bei fehlendem Referrer HTTP 403 liefern können. Die erforderliche Attribution bleibt im Globus sichtbar.
- Höhenmodell (ion-Asset 1) und Google Photorealistic 3D (ion-Asset 2275207) verwenden nun explizit authentifizierte `IonResource`-Objekte. Die vorher verwendeten Cesium-Hilfsfunktionen ignorierten den `accessToken` in ihren Darstellungsoptionen und nutzten den SDK-Demo-Token. Dadurch konnte trotz eingetragenem Schlüssel die grosse Demo-Token-Meldung erscheinen.
- Der SDK-Demo-Token wird deaktiviert. Ohne eigenen ion-Token erfolgen keine ion-Anfragen; die normale Kartenbasis funktioniert weiterhin.
- Scheitert der Aufbau einer Kartenbasis, bleibt die vorherige Basis erhalten. Verweigerter Terrain-/3D-Assetzugang wird verständlich angezeigt. Abgebrochene 3D-Auswahl fügt keinen veralteten Tileset hinzu.

## Update

HACS → Weltlage → ⋮ → Informationen aktualisieren → Erneut herunterladen → `v2.0.1`. Danach Home Assistant vollständig neu starten und die Dashboard-Seite neu laden. Vorhandene Schlüssel und die Dashboard-YAML bleiben erhalten. Falls noch kein Cesium-ion-Token eingetragen wurde: Einstellungen → Geräte & Dienste → Weltlage → Konfigurieren.

## Prüfungen und Grenzen

63 Python-, fünf JavaScript- und 26 Browserprüfungen bestehen lokal. Der Veröffentlichungsvorgang wiederholt diese Prüfungen. Die Browserprüfung lädt echte Esri-Kacheln und prüft die Token-Übergabe mit ausschliesslich synthetischen Zugangsdaten und absichtlich verweigerten ion-Assets; sie verwendet keine privaten Schlüssel. Metadatenausfall einer Kartenbasis, fehlende Tokens, beide Asset-IDs, mobile Bedienung, Home, Tracking und Freigabe beim Entfernen sind geprüft.

World Street Map ist ein älterer Rasterdienst ohne laufende Aktualisierung; Esri plant seine Einstellung für Dezember 2029. Die Strassenkarte ist keine Zusage aktueller Strassenzustände. Quellenhinweise: `THIRD_PARTY.md`. Die verbleibenden regionalen Live-/Gerätenachweise aus 2.0.0 bleiben offen; ausführliche Matrix in `docs/TEST_REPORT.md`.
