"""Bounded, opt-in public flight snapshots and satellite orbital elements."""
import json
import re

from .parsers import number, plain, stamp

SATELLITE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=json"


def flight_url(latitude, longitude):
    lat, lon = number(latitude), number(longitude)
    if lat is None or lon is None or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError("Ungültiger Kartenausschnitt")
    # Coarse map centre, never HA's configured home coordinates.
    lat, lon = round(lat / 5) * 5, round(lon / 5) * 5
    return f"https://api.adsb.lol/v2/point/{lat}/{lon}/250", lat, lon


def parse_flights(body, now):
    obj = json.loads(body)
    if not isinstance(obj, dict) or not isinstance(obj.get("ac", obj.get("aircraft")), list):
        raise ValueError("Ungültige Flugantwort")
    reported = number(obj.get("now"))
    if reported is None:
        raise ValueError("Zeitangabe fehlt")
    if reported > 1e11:
        reported /= 1000
    if reported > now + 60 or now - reported > 120:
        raise ValueError("Flugantwort veraltet")
    items = []
    for a in obj.get("ac", obj.get("aircraft", []))[:2000]:
        if not isinstance(a, dict):
            continue
        lat, lon, seen = number(a.get("lat")), number(a.get("lon")), number(a.get("seen_pos"))
        hex_id = str(a.get("hex", "")).lower()
        if lat is None or lon is None or seen is None or seen < 0 or now - reported + seen > 120 or not -90 <= lat <= 90 or not -180 <= lon <= 180 or not re.fullmatch(r"[a-f0-9]{6}", hex_id):
            continue
        altitude = number(a.get("alt_baro"))
        items.append({"id": hex_id, "latitude": lat, "longitude": lon, "name": plain(a.get("flight"), 30) or plain(a.get("r"), 30) or hex_id.upper(), "registration": plain(a.get("r"), 30), "aircraft_type": plain(a.get("t"), 20), "altitude_m": round(altitude * .3048) if altitude is not None else None, "speed_kmh": round(speed * 1.852) if (speed := number(a.get("gs"))) is not None else None, "heading": number(a.get("track")), "observed": reported - seen, "source": "adsb.lol", "url": f"https://globe.adsb.lol/?icao={hex_id}"})
    return items[:500]


def parse_satellites(body, now):
    obj = json.loads(body)
    if not isinstance(obj, list):
        raise ValueError("Ungültige Bahndaten")
    fields = ["MEAN_MOTION", "ECCENTRICITY", "INCLINATION", "RA_OF_ASC_NODE", "ARG_OF_PERICENTER", "MEAN_ANOMALY", "BSTAR", "MEAN_MOTION_DOT", "MEAN_MOTION_DDOT"]
    items = []
    for a in obj[:2000]:
        if not isinstance(a, dict):
            continue
        epoch = stamp(str(a.get("EPOCH", "")) + ("Z" if not re.search(r"(?:Z|[+-]\d{2}:\d{2})$", str(a.get("EPOCH", ""))) else ""))
        values = {f: number(a.get(f)) for f in fields}
        cat = number(a.get("NORAD_CAT_ID"))
        if epoch is None or now - epoch > 14 * 86400 or epoch > now + 86400 or cat is None or cat <= 0 or cat != int(cat) or any(v is None for v in values.values()):
            continue
        if not 0 < values["MEAN_MOTION"] <= 20 or not 0 <= values["ECCENTRICITY"] < 1 or not 0 <= values["INCLINATION"] <= 180:
            continue
        items.append({**values, "OBJECT_NAME": plain(a.get("OBJECT_NAME"), 80), "NORAD_CAT_ID": int(cat), "EPOCH": str(a["EPOCH"]), "epoch_timestamp": epoch, "OBJECT_ID": plain(a.get("OBJECT_ID"), 30)})
    if obj and not items:
        raise ValueError("Keine gültigen aktuellen Bahndaten")
    return items[:1000]
