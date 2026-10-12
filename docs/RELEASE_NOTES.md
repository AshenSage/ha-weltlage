# Weltlage 2.1.0 · Scharfe Vektorkarte und erkennbare Objekte

Dieses normale HACS-Release ersetzt die unscharfe Strassenkarte und generischen Punktmarker.

- Retina-Darstellung bis 2× Pixeldichte, Kantenglättung und feinere Globusdetails. Die bisherige doppelte Reduzierung der Renderauflösung auf hochauflösenden Handys entfällt.
- «Karte» verwendet OpenFreeMap-/OpenMapTiles-Vektordaten. Linien und Flächen werden im Browser pro Zoomstufe neu gezeichnet; die alten Esri-Strassenbildkacheln entfallen. Kein zusätzlicher API-Key erforderlich.
- Ortsnamen sind eigenständige Texteinblendungen, bleiben unabhängig von Kachelgrenzen lesbar und verdecken weder andere Ortsnamen noch Objektsymbole. Serbische Namen verwenden die gelieferten lateinischen Namen mit Sonderzeichen.
- Unterschiedliche SVG-Symbole für Flugzeuge, Militärjets, Schiffe, Satelliten, Kameras, Verkehr, Störungen, Hotspots und Infrastruktur. Gelieferte Flug-/Schiffsrichtungen werden berücksichtigt. Keine erfundenen Einzelautos: das Autosymbol gehört zu einem TomTom-Verkehrssegment.
- Dichte Gruppen erhalten ein Symbol mit Anzahl; Antippen zoomt zur Gruppe. Satellitenfarben und CAP-Warngebiete bleiben erhalten. Auch Werkzeugknöpfe verwenden klare SVG-Grafiken.

## Update

HACS → Weltlage → Informationen aktualisieren → `v2.1.0` installieren. Danach Home Assistant vollständig neu starten und das Dashboard vollständig neu laden. Schlüssel, Favoriten und bestehende YAML bleiben erhalten.

## Nachweise und Grenzen

Die Browserprüfung verwendet reale Vektordaten und Smartphone-Pixeldichte 3× bei auf 2× begrenztem Renderbuffer. Aranđelovac-Nahansicht, globale Zentrierung, Objektsymbole, Gruppen, Auswahl, Tracking, fehlende Schlüssel und Freigabe beim Entfernen werden geprüft. HA und die markierten Testobjekte sind simuliert; keine privaten Schlüssel werden verwendet. Release-Prüfung und Quellenmatrix: `docs/TEST_REPORT.md`.

Die Vektorgeometrie wird als hochauflösende Textur auf den Cesium-Globus gelegt; Ortsnamen sind separate native Labels. Daten können unvollständig sein. Satellitenbilder, Topografie und Fotorealistisch 3D behalten ihre jeweiligen Bild-/3D-Datenanbieter. Reale Smartphone-/Raspberry-Pi-Leistungsmessungen und die zuvor offenen regionalen Quellenprüfungen bleiben offen. Die neue Vektorkarte wird im Browser gerendert; die GPU-Auflösung ist zur Begrenzung der Last auf 2× gedeckelt.
