"""Bounded provider parsing without Home Assistant or network side effects."""
import csv
import io
import json
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .parsers import plain, number, stamp
from .intel import parse_flights, parse_satellites

def position(lat, lon):
    lat, lon = number(lat), number(lon)
    return (lat, lon) if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180 else None

def link(value):
    try:
        u = urlsplit(str(value or ""))
        return str(value) if u.scheme == "https" and u.hostname and not u.username and not u.password else None
    except ValueError:
        return None

def webcams(obj, now):
    rows = obj.get("webcams", []) if isinstance(obj, dict) else obj
    if not isinstance(rows, list):
        raise ValueError("webcams")
    items = []
    for row in rows[:100]:
        loc = row.get("location") or {}
        p = position(loc.get("latitude"), loc.get("longitude"))
        if p and row.get("status") == "active" and str(row.get("webcamId", "")).isdigit():
            items.append(dict(id=str(row["webcamId"]), name=plain(row.get("title"), 180), latitude=p[0], longitude=p[1], source="Windy.com", observed=stamp(row.get("lastUpdatedOn")), cluster_size=min(10000, max(1, int(number(row.get("clusterSize")) or 1)))))
    return items

def webcam_detail(row, now):
    image = (row.get("images") or {}).get("current") or {}
    urls, players = row.get("urls") or {}, row.get("player") or {}
    # API image URLs are used as delivered, never proxied, transformed or upscaled.
    return dict(id=str(row.get("webcamId", "")), name=plain(row.get("title"), 180), image_url=link(image.get("preview") or image.get("thumbnail")), page_url=link(urls.get("detail")), livestream=link(players.get("live")), timelapse=link(players.get("day")), observed=stamp(row.get("lastUpdatedOn")), loaded=now, expires=now + 540, source="Windy.com", media_kind="updated_still")

def flights(body, now):
    rows = parse_flights(body, now)
    raw = json.loads(body)
    flags = {str(a.get("hex", "")).lower(): int(number(a.get("dbFlags")) or 0) for a in raw.get("ac", raw.get("aircraft", [])) if isinstance(a, dict)}
    for row in rows:
        row["military"] = bool(flags.get(row["id"], 0) & 1)
    return rows

def earthquakes(obj):
    if not isinstance(obj.get("features"), list):
        raise ValueError("earthquakes")
    items = []
    for f in obj["features"][:500]:
        c, a = (f.get("geometry") or {}).get("coordinates", []), f.get("properties") or {}
        if len(c) < 2 or not (p := position(c[1], c[0])):
            continue
        items.append(dict(id=str(f.get("id")), name=f"M {a.get('mag', '?')} · {plain(a.get('flynn_region'), 140)}", latitude=p[0], longitude=p[1], magnitude=number(a.get("mag")), depth_km=number(a.get("depth", c[2] if len(c) > 2 else None)), observed=stamp(a.get("time")), source="EMSC / Seismic Portal", url=link(a.get("source_catalog"))))
    return items

def hotspots(text):
    items = []
    for i, r in enumerate(csv.DictReader(io.StringIO(text))):
        if i >= 1500:
            break
        if not (p := position(r.get("latitude"), r.get("longitude"))):
            continue
        ts = str(r.get("acq_time", "")).zfill(4)
        observed = stamp(f"{r.get('acq_date')}T{ts[:2]}:{ts[2:]}:00Z")
        items.append(dict(id=f"{p[0]}:{p[1]}:{observed}", name="Thermische Anomalie", latitude=p[0], longitude=p[1], observed=observed, confidence=plain(r.get("confidence"), 30), sensor=plain(r.get("instrument"), 40), satellite=plain(r.get("satellite"), 40), brightness_k=number(r.get("bright_ti4")), frp_mw=number(r.get("frp")), source="NASA FIRMS · VIIRS NOAA-20", description="Hotspot ist kein bestätigter Waldbrand."))
    return items

def osm(obj, kind, now):
    items = []
    for r in obj.get("elements", [])[:1000]:
        c, tags = r.get("center", r), r.get("tags", {})
        if not (p := position(c.get("lat"), c.get("lon"))):
            continue
        items.append(dict(id=f"{r.get('type')}/{r.get('id')}", name=plain(tags.get("name") or tags.get("operator") or kind, 160), latitude=p[0], longitude=p[1], source="OpenStreetMap · ODbL", static=True, loaded=now, url=f"https://www.openstreetmap.org/{r.get('type')}/{r.get('id')}", description="Statische öffentliche Kartierung, unvollständig."))
    return items

def mapillary(obj):
    items = []
    for r in obj.get("data", [])[:100]:
        c = (r.get("geometry") or {}).get("coordinates", [])
        if len(c) < 2 or not (p := position(c[1], c[0])):
            continue
        items.append(dict(id=str(r.get("id")), name="Mapillary · Strassenaufnahme", latitude=p[0], longitude=p[1], observed=(number(r.get("captured_at")) or 0) / 1000 or None, source="Mapillary", image_url=link(r.get("thumb_1024_url")), url=f"https://www.mapillary.com/app/?pKey={r.get('id')}&focus=photo", description="Historische Aufnahme, keine Live-Kamera."))
    return items

def traffic_segment(obj, now):
    a = obj.get("flowSegmentData") or {}
    coords = [position(c.get("latitude"), c.get("longitude")) for c in a.get("coordinates", {}).get("coordinate", [])[:1000]]
    coords = [p for p in coords if p]
    if len(coords) < 2:
        return None
    return dict(id=":".join(map(str, coords[0])), name="Verkehrsfluss · Strassensegment", latitude=coords[0][0], longitude=coords[0][1], line=[[p[1], p[0], 5] for p in coords], speed_kmh=number(a.get("currentSpeed")), free_speed_kmh=number(a.get("freeFlowSpeed")), confidence=number(a.get("confidence")), road_closure=bool(a.get("roadClosure")), loaded=now, source="TomTom", description="Aktuelle Anbieterantwort; exakte Messzeit nicht geliefert.")

def incidents(obj):
    items = []
    for f in obj.get("incidents", [])[:300]:
        a, g = f.get("properties") or {}, f.get("geometry") or {}
        c = g.get("coordinates", [])
        line = c if g.get("type") == "LineString" else []
        loc = line[0] if line else c
        if len(loc) < 2 or not (p := position(loc[1], loc[0])):
            continue
        items.append(dict(id=str(a.get("id")), name=plain((a.get("events") or [{}])[0].get("description") or "Verkehrsstörung", 180), latitude=p[0], longitude=p[1], line=[[x[0], x[1], 5] for x in line[:1000] if len(x) >= 2 and position(x[1], x[0])], observed=stamp(a.get("startTime")), expires=stamp(a.get("endTime")), delay_s=number(a.get("delay")), source="TomTom"))
    return items
