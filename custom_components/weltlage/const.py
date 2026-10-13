"""Bounded, keyless data sources for Weltlage."""
DOMAIN = "weltlage"
VERSION = "2.1.1"
MAX_BYTES = 2_000_000
MAX_ARTICLES = 120
RETENTION_HOURS = 72
DEFAULT_FEEDS = ["srf_world", "srf_business", "srf_ch", "bbc_world", "bbc_europe", "rts"]
FEEDS = {
    "srf_world": {"name": "SRF International", "publisher": "SRF", "url": "https://www.srf.ch/news/bnf/rss/1922", "language": "de", "region": "world", "category": "politik"},
    "srf_business": {"name": "SRF Wirtschaft", "publisher": "SRF", "url": "https://www.srf.ch/news/bnf/rss/1926", "language": "de", "region": "world", "category": "wirtschaft"},
    "srf_ch": {"name": "SRF Schweiz", "publisher": "SRF", "url": "https://www.srf.ch/news/bnf/rss/1890", "language": "de", "region": "ch", "category": "politik"},
    "bbc_world": {"name": "BBC World", "publisher": "BBC", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "language": "en", "region": "world", "category": "politik"},
    "bbc_europe": {"name": "BBC Europe", "publisher": "BBC", "url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml", "language": "en", "region": "europa", "category": "politik"},
    "rts": {"name": "RTS Serbien", "publisher": "RTS", "url": "https://www.rts.rs/vesti/rss.html", "language": "sr", "region": "world", "category": "politik"},
}
HAZARD_SOURCES = {
    "usgs": {"name": "USGS · Erdbeben M ≥ 4.5", "publisher": "USGS", "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson", "kind": "usgs", "interval": 300},
    "gdacs": {"name": "GDACS · Orange / Rot", "publisher": "GDACS", "url": "https://www.gdacs.org/xml/rss.xml", "kind": "gdacs", "interval": 300},
}
