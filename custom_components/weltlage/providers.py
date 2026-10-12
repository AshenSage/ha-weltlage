"""Shared bounded, on-demand adapters. No provider URLs are accepted from clients."""
from __future__ import annotations
import asyncio
from collections import OrderedDict
from datetime import datetime, timezone
import json
import math
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

import aiohttp

from .layers import LAYERS, SATELLITE_GROUPS
from . import data_parsers as parse
from .parsers import parse_gdacs, number, stamp
from .intel import parse_satellites
from .cameras import parse_cameras

MAX_BODY = 8_000_000
MAX_CACHE = 100

class SourceError(Exception):
    """Only a safe status and message, never a credential-bearing URL."""
    def __init__(self, status="unreachable", message="Quelle nicht erreichbar"):
        super().__init__(message)
        self.status, self.message = status, message

def bounds(value):
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError("Ausschnitt fehlt")
    b = tuple(float(v) for v in value)
    if not all(math.isfinite(v) for v in b):
        raise ValueError("Ungültiger Ausschnitt")
    w, s, e, n = b
    if not (-180 <= w < e <= 180 and -85 <= s < n <= 85):
        raise ValueError("Ungültiger Ausschnitt")
    return b

def _key(layer, b, group, date):
    if layer in ("satellites", "radar", "clouds", "imagery", "cables", "gdacs", "finland"):
        return (layer, group if layer == "satellites" else "", date if layer == "imagery" else "")
    # Quantise outwards, retaining coverage for the entire requested rectangle.
    step = .02 if layer in ("traffic", "mapillary") else .2
    q = tuple((math.floor(v / step) if i < 2 else math.ceil(v / step)) * step for i, v in enumerate(b))
    return (layer, *q)

class GlobeProviders:
    def __init__(self, session, executor, credentials, budget=500):
        self.session, self.executor, self.credentials = session, executor, credentials
        self.cache = OrderedDict()
        self.inflight = {}
        self.semaphore = asyncio.Semaphore(3)
        self.budget = max(20, min(2000, int(budget)))
        self.daily = {}
        self.closed = False

    async def close(self):
        self.closed = True
        tasks = list(self.inflight.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.inflight.clear()
        self.cache.clear()

    def _charge(self, source):
        today = datetime.now(timezone.utc).date().isoformat()
        if self.daily.get("date") != today:
            self.daily = {"date": today}
        if self.daily.get(source, 0) >= self.budget:
            raise SourceError("rate_limited", "Lokales Tageslimit erreicht")
        self.daily[source] = self.daily.get(source, 0) + 1

    async def request(self, url, *, params=None, headers=None, text=False, method="GET", data=None, source="public"):
        self._charge(urlsplit(url).hostname if source == "public" else source)
        async with self.semaphore:
            async with self.session.request(method, url, params=params, data=data, headers={"User-Agent": "HomeAssistant-Weltlage/2.0 (+https://github.com/AshenSage/ha-weltlage)", **(headers or {})}, timeout=aiohttp.ClientTimeout(total=22), allow_redirects=False) as r:
                if r.status in (401, 403):
                    raise SourceError("invalid_key" if source != "public" else "unreachable", "Zugang abgelehnt")
                if r.status == 429:
                    raise SourceError("rate_limited", "Anbieter begrenzt die Abrufe")
                if r.status == 404 and source == "tomtom":
                    raise SourceError("no_coverage", "Kein Strassensegment für diese Position")
                if r.status == 204:
                    return "" if text else {}
                if r.status != 200:
                    raise SourceError()
                chunks, size = [], 0
                async for chunk in r.content.iter_chunked(65536):
                    size += len(chunk)
                    if size > MAX_BODY:
                        raise SourceError("unreachable", "Anbieterantwort zu gross")
                    chunks.append(chunk)
        body = b"".join(chunks).decode("utf-8")
        return body if text else await self.executor(json.loads, body)

    async def layer(self, layer, bbox, group="stations", date=None):
        if self.closed:
            raise SourceError()
        if layer not in LAYERS or layer == "cap":
            raise ValueError("Unbekannte Ebene")
        b = bounds(bbox)
        if group not in SATELLITE_GROUPS:
            raise ValueError("Ungültiger Satellitenkatalog")
        now = time.time()
        spec = LAYERS[layer]
        common = dict(layer=layer, source=spec["source"], note=spec["note"], items=[], fetched=now)
        if spec["key"] and not self.credentials.get(spec["key"]):
            return {**common, "status": "missing_key", "message": "Schlüssel in der Integration hinterlegen"}
        if max(b[2] - b[0], b[3] - b[1]) > spec["max_extent"]:
            return {**common, "status": "zoom_required", "message": "Näher zoomen: Datenabruf ist regional begrenzt"}
        if layer == "clouds" and (b[1] >= 60 or b[3] <= -60):
            return {**common, "status": "no_coverage", "message": "Globales IR-Mosaik nur zwischen 60° Süd und 60° Nord"}
        if layer == "finland" and not (b[0] < 32 and b[2] > 19 and b[1] < 71 and b[3] > 59):
            return {**common, "status": "no_coverage", "message": "Diese Quelle deckt nur Finnland ab"}
        if layer == "imagery":
            try:
                selected = datetime.strptime(date or "", "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError as err:
                raise ValueError("Bilddatum ungültig") from err
            if not 0 <= now - selected.timestamp() <= 366 * 86400:
                raise ValueError("Bilddatum ausserhalb des letzten Jahres")
        k = _key(layer, b, group, date)
        old = self.cache.get(k)
        if old and now < old["next_due"]:
            self.cache.move_to_end(k)
            result = dict(old["result"])
            if result.get("status") in ("current", "no_hits") and now - result["fetched"] > spec["ttl"] * 2:
                result["status"] = "stale"
            return result
        if k not in self.inflight:
            if len(self.inflight) >= 12:
                return {**common, "status": "rate_limited", "message": "Zu viele parallele Ausschnitte"}
            self.inflight[k] = asyncio.create_task(self._load(k, layer, tuple(k[1:5]) if len(k) == 5 else b, group, date, common, old))
        try:
            return await asyncio.shield(self.inflight[k])
        finally:
            if k in self.inflight and self.inflight[k].done():
                self.inflight.pop(k, None)

    async def _load(self, k, layer, b, group, date, common, old):
        now = time.time()
        failures = 0
        try:
            payload = await self._fetch(layer, b, group, date, now)
            result = {**common, **payload, "status": payload.get("status", "current" if payload.get("items") or payload.get("raster") else "no_hits")}
        except (aiohttp.ClientError, TimeoutError, ValueError, TypeError, KeyError, ET.ParseError, SourceError) as err:
            failures = min(6, (old or {}).get("failures", 0) + 1)
            result = {**common, "status": getattr(err, "status", "unreachable"), "message": getattr(err, "message", "Quelle nicht erreichbar oder Antwort ungültig")}
            if old and (old["result"].get("items") or old["result"].get("raster")):
                # Never keep old flight/ship contacts as if currently observed.
                if layer not in ("flights", "military", "ships"):
                    result = {**old["result"], "status": "stale", "message": result["message"]}
        self.cache[k] = dict(result=result, failures=failures, next_due=now + (min(3600, 60 * 2 ** failures) if failures else LAYERS[layer]["ttl"]))
        while len(self.cache) > MAX_CACHE:
            self.cache.popitem(last=False)
        return result

    async def _fetch(self, layer, b, group, date, now):
        w, s, e, n = b
        lat, lon = (s + n) / 2, (w + e) / 2
        cred = self.credentials
        if layer in ("flights", "military"):
            # Both UI layers share one upstream/cache product.
            if layer == "military":
                result = await self.layer("flights", b)
                return {**result, "layer": "military", "source": LAYERS["military"]["source"], "note": LAYERS["military"]["note"], "items": [x for x in result["items"] if x.get("military")], "status": result["status"] if result["status"] not in ("current", "no_hits") else "current" if any(x.get("military") for x in result["items"]) else "no_hits"}
            lat, lon = round(lat), round(lon)
            body = await self.request(f"https://api.adsb.lol/v2/point/{lat}/{lon}/250", text=True)
            rows = await self.executor(parse.flights, body, now)
            return dict(items=rows, query_center=[lon, lat], radius_nm=250)
        if layer == "satellites":
            body = await self.request("https://celestrak.org/NORAD/elements/gp.php", params={"GROUP": group, "FORMAT": "json"}, text=True)
            rows = await self.executor(parse_satellites, body, now)
            for row in rows:
                row["group"] = "dense" if group == "starlink" else group
            return dict(items=rows[:1000], group=group, truncated=len(rows) > 1000, computed=True)
        if layer == "cameras":
            obj = await self.request("https://api.windy.com/webcams/api/v3/webcams", params={"bbox": f"{n},{e},{s},{w}", "include": "location", "limit": 50, "lang": "de"}, headers={"x-windy-api-key": cred["windy_webcams_api_key"]}, source="windy")
            return dict(items=await self.executor(parse.webcams, obj, now), total=obj.get("total"), limited=number(obj.get("total")) is not None and obj["total"] > 50)
        if layer == "finland":
            body = await self.request("https://tie.digitraffic.fi/api/weathercam/v1/stations", headers={"Digitraffic-User": "ha-weltlage/2.0"}, text=True)
            rows = await self.executor(parse_cameras, body, "finland", now)
            return dict(items=[x for x in rows if s <= x["latitude"] <= n and w <= x["longitude"] <= e][:400])
        if layer == "earthquakes":
            start = datetime.fromtimestamp(now - 7 * 86400, timezone.utc).isoformat()
            obj = await self.request("https://www.seismicportal.eu/fdsnws/event/1/query", params=dict(format="json", limit=500, minlat=s, maxlat=n, minlon=w, maxlon=e, minmag=1, starttime=start))
            return dict(items=await self.executor(parse.earthquakes, obj) if obj else [])
        if layer == "fires":
            key = cred["nasa_firms_map_key"]
            text = await self.request(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/VIIRS_NOAA20_NRT/{w},{s},{e},{n}/1", text=True, source="firms")
            return dict(items=await self.executor(parse.hotspots, text))
        if layer in ("datacenters", "dams", "bases"):
            selector = {"datacenters": '["man_made"="data_center"]', "dams": '["waterway"="dam"]', "bases": '["landuse"="military"]'}[layer]
            body = f"[out:json][timeout:18];nwr{selector}({s},{w},{n},{e});out center 1000;"
            obj = await self.request("https://overpass-api.de/api/interpreter", method="POST", data={"data": body})
            return dict(items=await self.executor(parse.osm, obj, layer, now), static=True)
        if layer == "mapillary":
            obj = await self.request("https://graph.mapillary.com/images", headers={"Authorization": "OAuth " + cred["mapillary_client_token"]}, params={"bbox": f"{w},{s},{e},{n}", "limit": 100, "fields": "id,geometry,captured_at,thumb_1024_url"}, source="mapillary")
            return dict(items=await self.executor(parse.mapillary, obj), limited=bool(obj.get("paging", {}).get("next")))
        if layer == "traffic":
            rows = []
            # Five real probes, explicitly a sampled layer, never synthetic cars.
            for dy, dx in ((0, 0), (-.25, -.25), (-.25, .25), (.25, -.25), (.25, .25)):
                try:
                    obj = await self.request("https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/12/json", params={"key": cred["tomtom_api_key"], "point": f"{lat+dy*(n-s)},{lon+dx*(e-w)}", "unit": "kmph"}, source="tomtom")
                    if row := parse.traffic_segment(obj, now):
                        rows.append(row)
                except SourceError as err:
                    if err.status != "no_coverage":
                        raise
            return dict(items=list({r["id"]: r for r in rows}.values()), sampled=True, status="current" if rows else "no_coverage")
        if layer == "incidents":
            obj = await self.request("https://api.tomtom.com/traffic/services/5/incidentDetails", params={"key": cred["tomtom_api_key"], "bbox": f"{w},{s},{e},{n}", "fields": "{incidents{type,geometry{type,coordinates},properties{id,iconCategory,events{description},startTime,endTime,delay}}}", "language": "de-DE", "timeValidityFilter": "present"}, source="tomtom")
            return dict(items=await self.executor(parse.incidents, obj))
        if layer == "radar":
            obj = await self.request("https://api.rainviewer.com/public/weather-maps.json")
            frames = [f for f in obj.get("radar", {}).get("past", []) if isinstance(f.get("time"), int) and str(f.get("path", "")).startswith("/v2/radar/")][-12:]
            if not frames or obj.get("host") != "https://tilecache.rainviewer.com":
                raise ValueError("radar")
            return dict(items=[], raster={"kind": "radar", "frames": frames, "max_zoom": 6}, observed=frames[-1]["time"], status="stale" if now - frames[-1]["time"] > 3600 else "current")
        if layer == "clouds":
            text = await self.request("https://nowcoast.noaa.gov/geoserver/observations/satellite/ows", params={"service": "WMS", "request": "GetCapabilities"}, text=True)
            times = await self.executor(cloud_times, text)
            if not times:
                raise ValueError("clouds")
            return dict(items=[], raster={"kind": "clouds", "times": times[-12:]}, observed=stamp(times[-1]), status="stale" if now - (stamp(times[-1]) or 0) > 6 * 3600 else "current")
        if layer == "imagery":
            # Validate actual GIBS service imagery; a date alone is no coverage proof.
            url = f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/0/0/0.jpeg"
            self._charge("gibs")
            async with self.semaphore:
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15), allow_redirects=False) as r:
                    if r.status != 200 or not r.headers.get("Content-Type", "").startswith("image/"):
                        raise SourceError()
                    await r.read()
            return dict(items=[], raster={"kind": "imagery", "date": date}, date=date, observation_kind="Tagesmosaik, regionale Lücken möglich")
        if layer == "wind":
            points = [(s + (n-s)*y/4, w + (e-w)*x/4) for y in range(5) for x in range(5)]
            obj = await self.request("https://api.open-meteo.com/v1/forecast", params={"latitude": ",".join(str(round(p[0], 3)) for p in points), "longitude": ",".join(str(round(p[1], 3)) for p in points), "current": "wind_speed_10m,wind_direction_10m", "timezone": "UTC"})
            rows = []
            for i, a in enumerate(obj if isinstance(obj, list) else [obj]):
                c = a.get("current", {})
                if (p := parse.position(a.get("latitude"), a.get("longitude"))) and number(c.get("wind_direction_10m")) is not None and number(c.get("wind_speed_10m")) is not None:
                    rows.append(dict(id=str(i), name="Wind · Modell 10 m", latitude=p[0], longitude=p[1], heading=number(c["wind_direction_10m"]), speed_kmh=number(c["wind_speed_10m"]), observed=stamp(str(c.get("time", "")) + "Z"), forecast=True, source="Open-Meteo · CC BY 4.0"))
            return dict(items=rows, forecast=True)
        if layer == "gdacs":
            body = await self.request("https://www.gdacs.org/xml/rss.xml", text=True)
            rows = await self.executor(parse_gdacs, body.encode("utf-8"), now)
            return dict(items=[dict(r, name=r.get("title"), observed=r.get("published"), description="Gemeldete Gebietsposition; kann angenähert sein. " + r.get("summary", "")) for r in rows])
        if layer == "cables":
            obj = await self.request("https://www.submarinecablemap.com/api/v3/cable/cable-geo.json")
            rows = await self.executor(cable_items, obj)
            return dict(items=rows, static=True)
        if layer == "ships":
            return await self._ships(b, now)
        raise ValueError("Ebene nicht implementiert")

    async def camera(self, camera_id):
        if not str(camera_id).isdigit() or len(str(camera_id)) > 16:
            raise ValueError("Kamera-ID ungültig")
        if not self.credentials.get("windy_webcams_api_key"):
            raise SourceError("missing_key", "Windy-Schlüssel fehlt")
        k = ("camera", str(camera_id))
        if k in self.cache and time.time() < self.cache[k]["next_due"]:
            return self.cache[k]["result"]
        obj = await self.request(f"https://api.windy.com/webcams/api/v3/webcams/{camera_id}", params={"include": "images,urls,player,location", "lang": "de"}, headers={"x-windy-api-key": self.credentials["windy_webcams_api_key"]}, source="windy")
        row = parse.webcam_detail(obj, time.time())
        self.cache[k] = dict(result=row, next_due=time.time()+120)
        while len(self.cache) > MAX_CACHE:
            self.cache.popitem(last=False)
        return row

    async def _ships(self, b, now):
        w, s, e, n = b
        rows = {}
        self._charge("aisstream")
        async with self.semaphore:
            async with self.session.ws_connect("wss://stream.aisstream.io/v0/stream", timeout=aiohttp.ClientWSTimeout(ws_close=3), heartbeat=20, max_msg_size=100000) as ws:
                await ws.send_json({"APIKey": self.credentials["aisstream_api_key"], "BoundingBoxes": [[[s,w],[n,e]]], "FilterMessageTypes": ["PositionReport"]})
                deadline = time.monotonic()+8
                while time.monotonic() < deadline and len(rows) < 400:
                    try:
                        msg = await ws.receive(timeout=max(.1, deadline-time.monotonic()))
                    except TimeoutError:
                        break
                    if msg.type != aiohttp.WSMsgType.TEXT:
                        break
                    a = json.loads(msg.data)
                    if "error" in a or "Error" in a:
                        raise SourceError("invalid_key", "AISStream lehnt Zugang ab")
                    meta, pos = a.get("MetaData", {}), a.get("Message", {}).get("PositionReport", {})
                    p = parse.position(pos.get("Latitude"), pos.get("Longitude"))
                    if p and s <= p[0] <= n and w <= p[1] <= e:
                        ident = str(meta.get("MMSI", pos.get("UserID", "")))
                        rows[ident] = dict(id=ident, name=str(meta.get("ShipName", ident)).strip()[:120], latitude=p[0], longitude=p[1], speed_kmh=(number(pos.get("Sog")) or 0)*1.852, heading=number(pos.get("Cog")), observed=now, observation_kind="Empfangszeit im achtsekündigen Fenster", source="AISStream")
        return dict(items=list(rows.values()), receive_window_s=8, message="Keine Kontakte im Empfangsfenster; daraus folgt keine Abdeckungsaussage" if not rows else None)

def cloud_times(text):
    if "<!DOCTYPE" in text or "<!ENTITY" in text:
        raise ValueError("XML")
    root = ET.fromstring(text)
    for layer in root.iter():
        if layer.tag.split("}")[-1] != "Layer":
            continue
        if not any(x.tag.split("}")[-1] == "Name" and x.text == "global_longwave_imagery_mosaic" for x in layer):
            continue
        for x in layer:
            if x.tag.split("}")[-1] in ("Dimension", "Extent") and x.attrib.get("name") == "time":
                return sorted(t.strip() for t in (x.text or "").split(",") if stamp(t.strip()) is not None and "/" not in t)[-24:]
    return []

def cable_items(obj):
    rows = []
    for f in obj.get("features", [])[:1000]:
        g, a = f.get("geometry", {}), f.get("properties", {})
        lines = g.get("coordinates", []) if g.get("type") == "MultiLineString" else [g.get("coordinates", [])]
        for i, line in enumerate(lines[:100]):
            good = [c[:2] for c in line[:2000] if len(c) >= 2 and parse.position(c[1], c[0])]
            if len(good) >= 2:
                rows.append(dict(id=f"{a.get('id', f.get('id'))}:{i}", name=str(a.get("name", "Unterseekabel"))[:160], latitude=good[0][1], longitude=good[0][0], line=good, source="TeleGeography · CC BY-NC-SA 3.0", static=True, url="https://www.submarinecablemap.com", description="Schematischer, statischer Verlauf. Nichtkommerzielle Nutzung."))
    return rows[:1500]
