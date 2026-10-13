# Weltlage 2.1.1 · Gültige Aktionsbeschreibung

Behebt den YAML-Parserfehler in `services.yaml`, durch den Home Assistant die Beschreibung von `weltlage.fetch_intel` nicht laden konnte. Die Auswahlfelder und Vorgabewerte entsprechen dem vorhandenen Backend. Kameras über die alte Aktion unterstützen nur `provider: finland`; öffentliche Webcams werden weiter direkt im Globus geladen.

Zusätzliche Regressionstests prüfen alle Komponenten-YAML-Dateien und die unterstützten Aktionsfelder vor der Veröffentlichung. Die Browser-Testdaten lesen die Backend-Version jetzt aus dem Manifest.

Normales stabiles HACS-Release. HACS → Weltlage → Informationen aktualisieren → `v2.1.1` installieren. Danach Home Assistant neu starten und das Dashboard vollständig neu laden.

Der Patch behält den Globus von 2.1.0, die vorhandenen Schlüssel und die Konfiguration bei. Die Veröffentlichung baut und prüft Backend, Frontend, Browser und das vollständige `weltlage.zip`. Lokal bestanden 65 Python-Tests, fünf JavaScript-Tests und 32 Browserprüfungen. Für kalte regionale Vektorkacheln erhält der Browser-Test ein längeres Wartebudget; seine Bedingungen bleiben unverändert.
