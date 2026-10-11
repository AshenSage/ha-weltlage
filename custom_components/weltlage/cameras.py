"""Official public traffic camera catalogs. Only registered HTTPS frame origins."""
import json
import math
import re
from urllib.parse import urlsplit

from .parsers import number, plain, stamp

CAMERA_PROVIDERS = {
    "london": {"name": "London · TfL", "url": "https://api.tfl.gov.uk/Place/Type/JamCam", "credit": "Powered by TfL Open Data. Contains OS data © Crown copyright and database rights", "page": "https://tfl.gov.uk/traffic/status/", "refresh": 180},
    "finland": {"name": "Finnland · Fintraffic", "url": "https://tie.digitraffic.fi/api/weathercam/v1/stations", "credit": "Fintraffic / digitraffic.fi · CC BY 4.0", "page": "https://www.digitraffic.fi/en/road-traffic/", "refresh": 600},
    "bc": {"name": "Kanada · DriveBC", "url": "https://www.drivebc.ca/api/webcams/", "credit": "DriveBC. Contains information licensed under the Open Government Licence – British Columbia", "page": "https://www.drivebc.ca/", "refresh": 600},
}


def camera_image_url(value, provider):
    """No credentials, arbitrary hosts, private endpoints or alternate ports."""
    try:
        u = urlsplit(str(value))
        if u.scheme != "https" or u.username or u.password or u.port not in (None, 443):
            return None
        host, path = u.hostname, u.path
        if provider == "london" and host == "s3-eu-west-1.amazonaws.com" and re.fullmatch(r"/jamcams\.tfl\.gov\.uk/[\d.]+\.jpg", path):
            return f"https://{host}{path}"
        if provider == "finland" and host == "weathercam.digitraffic.fi" and re.fullmatch(r"/C\d{7}\.jpg", path):
            return f"https://{host}{path}"
        if provider == "bc" and host == "www.drivebc.ca" and re.fullmatch(r"/images/\d+\.jpg", path):
            return f"https://{host}{path}"
    except (TypeError, ValueError):
        pass
    return None


def parse_cameras(body, provider, now):
    obj = json.loads(body)
    source = CAMERA_PROVIDERS[provider]
    rows = obj if provider in ("london", "bc") else obj.get("features") if isinstance(obj, dict) else None
    if not isinstance(rows, list):
        raise ValueError("Ungültiger Kamerakatalog")
    items, seen = [], set()
    for row in rows[:5000]:
        if not isinstance(row, dict):
            continue
        if provider == "london":
            props = {p.get("key"): p.get("value") for p in row.get("additionalProperties", []) if isinstance(p, dict)}
            if props.get("available") != "true":
                continue
            candidates = [(row.get("id"), props.get("imageUrl"))]
            lat, lon, name, desc = row.get("lat"), row.get("lon"), row.get("commonName"), props.get("view", "")
            observed, credit = None, source["credit"]
        elif provider == "bc":
            if not row.get("is_on") or not row.get("should_appear") or row.get("marked_stale"):
                continue
            coords = (row.get("location") or {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            lon, lat = coords[:2]
            ident = str(row.get("id", ""))
            if not ident.isdigit():
                continue
            candidates = [(ident, f"https://www.drivebc.ca/images/{ident}.jpg")]
            name, desc = row.get("name"), row.get("caption")
            observed = stamp(row.get("last_update_modified"))
            credit = source["credit"] + (" · " + plain(row["credit"], 150) if row.get("credit") else "")
        else:
            coords = (row.get("geometry") or {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            lon, lat = coords[:2]
            p = row.get("properties") or {}
            observed, credit = None, source["credit"]
            if provider == "finland":
                if p.get("collectionStatus") != "GATHERING":
                    continue
                candidates = [(a.get("id"), f"https://weathercam.digitraffic.fi/{a.get('id')}.jpg") for a in p.get("presets", []) if isinstance(a, dict) and a.get("inCollection") is True]
                name, desc = p.get("name"), "Strassen- und Wetterkamera · festes Kamerabild"

        lat, lon = number(lat), number(lon)
        if lat is None or lon is None or not -90 <= lat <= 90 or not -180 <= lon <= 180:
            continue
        for ident, image in candidates:
            image = camera_image_url(image, provider)
            ident = plain(ident, 100)
            if not image or not ident or ident in seen:
                continue
            seen.add(ident)
            items.append({"id": f"{provider}:{ident}", "provider": provider, "latitude": lat, "longitude": lon, "name": plain(name, 120) or ident, "description": plain(desc, 250), "image_url": image, "observed": observed if observed and observed <= now + 60 else None, "source": source["name"], "credit": credit, "url": source["page"], "refresh_seconds": source["refresh"]})
    return items


def nearest_cameras(items, latitude, longitude, limit=600):
    """Bound HA's state payload; retain the cameras nearest the requested view."""
    def distance(p):
        a, b = math.radians(latitude), math.radians(p["latitude"])
        return math.sin((b-a)/2)**2 + math.cos(a)*math.cos(b)*math.sin(math.radians(p["longitude"]-longitude)/2)**2
    return sorted(items, key=distance)[:limit]
