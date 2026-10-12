"""Single source of truth for the globe's opt-in data products."""
KEYS = ("cesium_ion_token", "windy_webcams_api_key", "tomtom_api_key", "mapillary_client_token", "nasa_firms_map_key", "aisstream_api_key")

def product(name, group, source, ttl, note, key=None, extent=360, color="#57dbeb"):
    return dict(name=name, group=group, source=source, ttl=ttl, note=note, key=key, max_extent=extent, color=color)

LAYERS = {
    "flights": product("Zivile Flüge", "Bewegung", "adsb.lol · ODbL", 60, "Öffentlich empfangene ADS-B-Kontakte; Empfangslücken möglich.", extent=30),
    "military": product("Militärflüge", "Bewegung", "adsb.lol · ODbL", 60, "Nur öffentlich empfangene Kontakte mit militärischem Datenbankkennzeichen; keine vollständige Erfassung.", extent=30, color="#ffbf66"),
    "satellites": product("Satelliten / ISS", "Bewegung", "CelesTrak · SGP4", 21600, "Berechnete Positionen aus Bahnelementen, keine Live-Messung. Elemente älter als 14 Tage werden verworfen.", color="#bbaaff"),
    "ships": product("Schiffe", "Bewegung", "AISStream", 60, "Kurze regionale AIS-Empfangsfenster; unvollständig, besonders auf Binnengewässern.", "aisstream_api_key", 20, "#78cfaa"),
    "cameras": product("Öffentliche Webcams", "Kameras", "Windy.com", 300, "API-Katalog kann vom Windy-Webangebot abweichen. Bilder erst beim Öffnen laden.", "windy_webcams_api_key", 45, "#8bdfae"),
    "finland": product("Fintraffic", "Kameras", "Fintraffic / Digitraffic · CC BY 4.0", 3600, "Ergänzender offizieller Kamerakatalog, nur Finnland.", extent=45, color="#8bdfae"),
    "radar": product("Regenradar", "Wetter", "RainViewer", 600, "Beobachteter Radarkomposit; Framezeit ist nicht die genaue Messzeit jeder Station. Empfangslücken bleiben möglich.", color="#6eafff"),
    "clouds": product("Wolken / Infrarot", "Wetter", "NOAA nowCOAST · globales IR-Mosaik", 1800, "Globales Satellitenmosaik (ca. 60°S–60°N), mit 2–3 Stunden Latenz. Auch Oberflächentemperatur, keine reine Wolkenmaske.", color="#d1e0f0"),
    "wind": product("Wind", "Wetter", "Open-Meteo · CC BY 4.0", 1800, "Modellwerte in 10 m Höhe auf einem begrenzten Raster; animierte Richtungspfeile, keine Partikelmessungen.", extent=45),
    "traffic": product("Verkehrsfluss", "Bewegung", "TomTom", 180, "Stichprobe realer Strassensegmente mit aktueller und freier Geschwindigkeit; keine flächendeckende Verkehrsübersicht.", "tomtom_api_key", 1, "#f3bc69"),
    "incidents": product("Verkehrsstörungen", "Bewegung", "TomTom", 180, "Gemeldete Störungen im Ausschnitt; Abdeckung hängt vom Anbieter ab.", "tomtom_api_key", 5, "#ff916b"),
    "earthquakes": product("Erdbeben", "Ereignisse", "EMSC / Seismic Portal", 300, "Letzte 7 Tage, M ≥ 1; maximal 500 Ereignisse im Ausschnitt. Keine Treffer bedeutet keine gemeldeten Ereignisse im Filter.", color="#ffb174"),
    "fires": product("Hitze / Hotspots", "Ereignisse", "NASA FIRMS", 1800, "VIIRS NOAA-20, letzte 24 Stunden. Thermische Anomalie ist kein bestätigter Waldbrand.", "nasa_firms_map_key", 30, "#ff7768"),
    "mapillary": product("Strassenfotos", "Kameras", "Mapillary", 3600, "Historische Aufnahmen; Aufnahmedatum im Bildbetrachter. Keine Live-Kamera.", "mapillary_client_token", .5, "#a4de72"),
    "imagery": product("Neuere Satellitenbilder", "Wetter", "NASA GIBS / MODIS Terra", 3600, "Tagesmosaik mit Datumsauswahl; keine Echtzeit, Wolken und Lücken möglich, ca. 250 m Auflösung.", color="#9eb7ff"),
    "datacenters": product("Rechenzentren", "Infrastruktur", "OpenStreetMap · ODbL", 86400, "Statische, unvollständige öffentliche Kartierung; keine Betriebs- oder Auslastungsdaten.", extent=8, color="#88bbcf"),
    "dams": product("Staudämme", "Infrastruktur", "OpenStreetMap · ODbL", 86400, "Öffentlich kartierte Anlagen; keine Wasserstandsmessung.", extent=8, color="#88bbcf"),
    "bases": product("Militäranlagen", "Infrastruktur", "OpenStreetMap · ODbL", 86400, "Statische, unvollständige öffentliche Kartierung, keine Einsatzinformationen.", extent=8, color="#c5a883"),
    "cables": product("Unterseekabel", "Infrastruktur", "TeleGeography · CC BY-NC-SA 3.0", 86400, "Schematische Kabelverläufe; nur nichtkommerzielle Nutzung gemäss Quellenlizenz, keine genaue Lage am Meeresboden.", color="#e5a4d9"),
    "gdacs": product("GDACS", "Ereignisse", "GDACS", 300, "Öffentliche Katastrophenmeldungen. Gemeldete Gebietspositionen können angenähert sein.", color="#ff9988"),
    "cap": product("CAP · Šumadija", "Ereignisse", "CAP Alerts / RHMZ", 300, "Warngebiete aus HA; bei fehlender Geometrie nur ausdrücklich gekennzeichnete Gebietsmitte.", color="#ffd16a"),
}

SATELLITE_GROUPS = ("stations", "visual", "gps-ops", "galileo", "glonass", "geo", "starlink")
