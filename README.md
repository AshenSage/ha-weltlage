# Weltlage für Home Assistant · 1.0.1

Ein eigener Bereich für Weltinformationen: dunkle, taktische Optik, zuerst fürs Handy gebaut. Die Übersicht kombiniert ausgewählte Nachrichten mit separaten Naturereignissen und deinen bestehenden CAP-Wetterwarnungen für **Serbien / Šumadija**. Die grosse Weltkarte öffnet sich bei Bedarf.

**Home Assistant 2026.10.0 oder neuer** · Installation und Updates über HACS · keine neuen API-Schlüssel. Die Integration enthält die Dashboardkarte und stellt sie selbst bereit. Die Veröffentlichung ersetzt keinen Live-Test in Home Assistant; Grenzen stehen in `TESTBERICHT.md`.

`VORSCHAU.html` ist eine eigenständig im Browser bedienbare Vorschau. **Alle Meldungen, Warnungen und Statusangaben darin sind Beispieldaten.** Sie zeigt dieselbe Karte wie die Installation. Nur die separat geöffnete World-Monitor-Karte kontaktiert den externen Dienst.

## Installation mit HACS

1. In **HACS → ⋮ → Benutzerdefinierte Repositories** `https://github.com/AshenSage/ha-weltlage` hinzufügen; Typ **Integration**.
2. **Weltlage** suchen und herunterladen. Falls noch kein Release existiert, die Standardbranch **main** herunterladen.
3. **Home Assistant vollständig neu starten.** Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach **Weltlage** suchen. Quellen wählen; Nachrichtenabruf standardmässig alle 15 Minuten, USGS/GDACS alle 5 Minuten.
4. Unter **Einstellungen → Dashboards → ⋮ → Ressourcen** einmal hinzufügen: URL **`/weltlage/weltlage-card.js`**, Typ **JavaScript-Modul**. Falls Ressourcen nicht sichtbar sind, im Benutzerprofil den erweiterten Modus aktivieren. Danach Browser bzw. Companion App neu laden.
5. Im bestehenden Dashboard eine neue Ansicht **Weltlage** mit Layout **Panel (eine Karte)** anlegen. Eine **Manuelle Karte** hinzufügen und den untenstehenden Code einsetzen. Die eigenen bisherigen Ansichten bleiben bestehen.
6. Unter **Quellen & Datenalter** die Abrufe kontrollieren. CAP darf bei fehlenden oder veralteten Daten keine Entwarnung anzeigen.

HACS verwaltet den gesamten Ordner `custom_components/weltlage`, einschliesslich der Karte. Ein separates Kopieren nach `www` ist nicht erforderlich. Neue Versionen über HACS herunterladen, HA vollständig neu starten und Browser/Companion App neu laden. Die Ressourcen-URL bleibt gleich. Die Integration registriert keine fremden Ressourcen und schreibt nicht in bestehende Dashboard-Konfigurationen.

### Manuelle Installation oder Wechsel vom ZIP 1.0.0

Manuell den enthaltenen Ordner `custom_components/weltlage` nach **`/config/custom_components/weltlage`** kopieren und HA neu starten. Danach Schritte 3–6 oben ausführen. Keine `configuration.yaml` ersetzen.

Bei einer vorhandenen manuellen Installation über HACS herunterladen bzw. erneut herunterladen. HACS übernimmt denselben Integrationsordner. Der bestehende Integrationseintrag und die Karte bleiben verwendbar. Eine alte Ressourcen-URL **`/local/weltlage/weltlage-card.js?v=1.0.0`** durch **`/weltlage/weltlage-card.js`** ersetzen; beide URLs nicht parallel laden. Die bisherige Kopie in `/config/www/weltlage` wird danach nicht mehr gebraucht.

```yaml
type: custom:weltlage-card
title: Weltlage
max_items: 3
alert_count_entity: sensor.cap_alerts_wmo_alert_count
alert_updated_entity: sensor.cap_alerts_wmo_last_updated
alert_areas:
  - RS010
alert_label: Serbien · Šumadija
```

Alternativ enthält `dashboard/weltlage-ansicht.yaml` die vollständige einzelne Ansicht für den Dashboard-Rohkonfigurationseditor. Diesen Block als neuen Eintrag unter `views:` einfügen und die Einrückung anpassen. `dashboard/weltlage-dashboard.yaml` ist eine vollständige Vorlage für ein **neues, separates** Dashboard.

Die Karte findet die Lagebild-Entität und den Aktualisieren-Button automatisch. Falls mehrere ähnliche Entitäten existieren oder eine andere Entität ausdrücklich gewünscht ist, `entity: sensor.weltlage_lagebild` und `refresh_entity: button.weltlage_aktualisieren` ergänzen. Die tatsächlichen IDs stehen unter Geräte & Dienste → Weltlage → Entitäten; manuelles Umbenennen kann sie verändern.

## Was enthalten ist

| Bereich | Verhalten |
| --- | --- |
| Nachrichten | SRF International, Wirtschaft und Schweiz; BBC World und Europe; RTS Serbien. Quellen sind in den Integrationsoptionen auswählbar. |
| Regionen | Welt, CH/RS, Europa, Balkan, Schweiz, Serbien. Ein Artikel kann zu mehreren Regionen gehören. |
| Themen | Politik, Konflikte, Energie/Handel, Wirtschaft, Natur, Technik. Einfache Stichwortzuordnung; keine KI-Wahrheitsbewertung. |
| Zeiträume | 24, 48 oder 72 Stunden; höchstens 120 zusammengeführte Meldungen. Standardmässig drei sichtbar, danach «Weitere». |
| Warnungen | Vorhandene CAP-Alerts-Entitäten für `RS010`. Gelb/Orange/Rot getrennt aktiv und kommend. Grüne Einträge zählen nicht als besondere Warnung. |
| Naturereignisse | USGS-Erdbeben M ≥ 4.5 der letzten 24 Stunden; GDACS Orange/Rot. GDACS-Erdbeben werden ausgelassen, damit dieselbe Ereignisart nicht doppelt gezählt wird. |
| Weltkarte | Externe kostenlose World-Monitor-Einbettung für Konflikte, Erdbeben und Wetter; öffnet im Vollbilddialog. Welt/Europa/Balkan wählbar. |
| Datenqualität | Eigener Status je Quelle; gespeicherte Artikel werden bei Abruffehlern markiert. Warnstatus bei fehlenden CAP-Daten unbekannt. |
| Speicherung | Letzte erfolgreiche Quelldaten in HA `.storage`; bleiben über Neustarts erhalten. RSS-Historie höchstens 72 Stunden und 50 Einträge je Quelle. |

Meldungen bleiben in der Sprache ihrer Quelle: Deutsch, Englisch bzw. Serbisch. Kurztexte stammen aus dem RSS-Feed; vollständige Artikel öffnen beim Anbieter. Offensichtlich gleiche URLs bzw. längere identische Überschriften in engem Zeitabstand werden zusammengeführt. Ähnliche Berichte können trotzdem mehrfach erscheinen.

Die Meldungszahl zählt Einträge mit einem gültigen Veröffentlichungsdatum im gewählten Filter. Undatierte Einträge tragen «Datum fehlt» und bleiben ab ihrer ersten Erfassung höchstens 72 Stunden sichtbar. «Erfolgreicher Abruf» bedeutet, dass die Quelle erreichbar und verarbeitet wurde; der neueste Artikel kann trotzdem älter sein.

## Was sinnvoll ist

Für den Alltag sind **kurz lesbare Meldungen, nachvollziehbare Quellen, regionale Wetterwarnungen und sichtbar veraltete Daten** am nützlichsten. Weltlage bietet einen Einstieg in relevante Entwicklungen; Details lassen sich bei Bedarf öffnen. Nachrichten aus Serbien und der Schweiz sind schnell erreichbar, ohne die globale Sicht aufzugeben.

Die Karte ist im schmalen Fenster einspaltig. Ab 760 Pixel Kartenbreite stehen Nachrichten und Zusatzbereiche nebeneinander. Die Weltkarte und eine mögliche spätere 3D-Ansicht laden erst auf ausdrücklichen Aufruf. Das reduziert Last und Ablenkung beim Lesen auf dem Handy.

## Was nicht sinnvoll ist und hier bewusst fehlt

- **Eine globale «Gefahrenampel» aus Schlagzeilen:** dafür gibt es weder eine definierte Skala noch ausreichend vollständige Daten. Medienberichte lösen hier keine Warnung aus.
- **Automatische Alarmmeldungen für jede Weltmeldung:** zu viel Rauschen. Dieses Paket verschickt keine Push-Nachrichten und steuert keine Geräte.
- **KI-Texte als angeblich bestätigte Lage:** es gibt keine erfundenen Zusammenfassungen, automatischen Übersetzungen oder Behauptungen einer unabhängigen Bestätigung.
- **Eine dauerhaft laufende 3D-Erde auf der Handy-Startseite:** für diesen schnellen Informationsblick wenig hilfreich. God’s Eye ist als optional separat zu öffnende Ansicht vorgesehen.
- **Vollständige weltweite Abdeckung:** RSS-Auswahl, Stichwortfilter und öffentliche Daten haben Lücken. Ein leerer Filter ist keine Aussage, dass weltweit nichts passiert.

## World Monitor und God’s Eye

Die eingebaute kostenlose World-Monitor-Karte benötigt laut Anbieter keinen Schlüssel und aktualisiert stündlich. Sie erlaubt die drei genannten Ebenen. Flugzeuge, Schiffe und Satelliten sind nicht Teil dieser Einbettung. Die Karte meldet ihre eigene Datenlage; der Weltlage-Quellenstatus bewertet ausschliesslich unsere eigenen Feeds und CAP. Eine eingebettete Karte kann nach einem Ausfall einen älteren Zustand zeigen.

Das geprüfte God’s-Eye-Repository und meine Einschätzung stehen separat in **`GODS-EYE-CHECK.md`**. Es wird mit diesem Paket nicht installiert. Sobald du eine eigene erreichbare Installation hast, kannst du in der Karte ergänzen:

```yaml
intel_url: https://deine-intel-adresse.example
```

Dann erscheint «3D Intel öffnen». Das Beispiel ist ein Platzhalter, keine bereitgestellte Adresse. Ein auf einem anderen Rechner laufendes `localhost:4173` ist vom Handy aus nicht erreichbar.

## Anpassungen

Alle üblichen Einstellungen stehen auch im grafischen Karteneditor. Zusätzlich per YAML:

| Schlüssel | Standard | Zweck |
| --- | --- | --- |
| `region` | `world` | Startfilter: `world`, `chrs`, `europa`, `balkan`, `ch`, `rs` |
| `max_items` | `3` | Sichtbare Meldungen vor «Weitere», 1–12 |
| `show_map` | `true` | Karten-Schaltfläche anzeigen |
| `entity` | automatische Erkennung | Lagebild-Entität explizit wählen |
| `refresh_entity` | automatische Erkennung | Aktualisieren-Button explizit wählen |
| `alert_areas` | `[RS010]` | CAP-Gebietscodes; leere Liste zeigt alle vorhandenen CAP-Gebiete |
| `alert_entities` | automatische Suche | Optional Liste bestimmter CAP-Warnentitäten |
| `alert_label` | `Serbien · Šumadija` | Name der Warnregion |
| `alert_max_age` | `90` | Minuten bis CAP als veraltet gilt |
| `intel_url` | leer | Adresse deiner optionalen God’s-Eye-Installation |

CAP-Sensoren mit HA-Zustand `unknown` sind nutzbar, wenn ihre CAP-Attribute gültig sind. Unbekannte Warnstufen, fehlende Zeitangaben oder nicht verfügbare Sensoren ergeben einen unvollständigen Warnstatus. Die Zeitzone der Anzeige kommt aus Home Assistant.

## Betrieb und Fehlerbehebung

- Integration nicht gefunden: Ordnerpfad kontrollieren; `manifest.json` muss direkt unter `/config/custom_components/weltlage/` liegen. HA nach dem Kopieren neu starten.
- «Custom element doesn't exist»: Modulressource kontrollieren, Browser/Companion App neu laden. Bei Updates den Versionsparameter der Ressource erhöhen.
- Einzelne Quelle ausgefallen: Quellenbereich öffnen. Andere Quellen laufen weiter; letzte erfolgreiche Daten bleiben sichtbar. DNS/Internet des HA-Systems und HA-Protokolle prüfen.
- CAP «Daten prüfen»: Zähler, Letzter-Abruf-Entität und Gebietscode kontrollieren. Der rohe CAP-Zähler kann auch grüne Einträge zählen und ist daher keine Alarmzahl.
- Weltkarte leer: World Monitor muss vom Handy aus erreichbar sein. Bei eigener Content Security Policy muss die Domain für Frames erlaubt sein.
- Manueller Abruf: der Aktualisieren-Button hat mindestens 60 Sekunden Abstand. Automatische Abrufe bleiben massvoll; bei Fehlern verlängert sich das Wiederholungsintervall bis auf eine Stunde.

Die Integration erfordert für Nachrichtendaten Internetzugriff vom HA-Server. Die Weltkarte und externe Artikel benötigen Internet vom Gerät, auf dem die Karte geöffnet wird. Es werden keine Schlüssel verlangt, keine eigenen privaten Kameras eingebunden und keine Koordinaten deines Zuhauses an die Nachrichtenquellen geschickt.

Zum Entfernen Integration und Lovelace-Karte löschen, Modulressource entfernen, Weltlage in HACS entfernen bzw. ausschliesslich den Integrationsordner entfernen und HA neu starten. Der Integrationscache kann bei Bedarf über den HA-Speicher administriert werden; andere `.storage`-Dateien nicht verändern.

## Quellen und Prüfung

- [HA Custom Cards](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/) und [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data/)
- [SRF RSS](https://www.srf.ch/really-simple-syndication-rss-feeds-von-srf), [BBC RSS](https://feeds.bbci.co.uk/news/world/rss.xml), [RTS RSS](https://www.rts.rs/vesti/rss.html)
- [USGS GeoJSON Feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php), [GDACS Feed](https://www.gdacs.org/xml/rss.xml)
- [World Monitor: offizielle Embed-Dokumentation](https://www.worldmonitor.app/docs/embed-live-map)

Die genaue Prüfung und ihre Grenzen stehen in `TESTBERICHT.md`. Dieses Repository enthält ausschliesslich Quellcode, synthetische Tests, Vorlagen und Dokumentation; keine Zugangsdaten oder HA-Exportarchive. Änderungen stehen in `CHANGELOG.md`. Lizenz: MIT.
