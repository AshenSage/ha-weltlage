"""Fetch independently; persist last-good data and expose source health honestly."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import time

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, VERSION, FEEDS, DEFAULT_FEEDS, HAZARD_SOURCES, MAX_BYTES, RETENTION_HOURS
from .parsers import parse_news, merge_news, parse_gdacs, parse_usgs, iso
from .intel import SATELLITE_URL, flight_url, parse_flights, parse_satellites
from .cameras import CAMERA_PROVIDERS, parse_cameras, nearest_cameras

_LOGGER = logging.getLogger(__name__)


class WeltlageCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=5), config_entry=entry)
        self.entry = entry
        self.session = async_get_clientsession(hass)
        self.store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}")
        self.cache = {}
        self.intel = {}
        self._intel_lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(3)
        self._last_manual = 0
        self._force = False
        self.sources = {key: dict(value) for key, value in HAZARD_SOURCES.items()}

    async def async_load(self):
        saved = await self.store.async_load()
        if saved and isinstance(saved.get("cache"), dict):
            self.cache = {k: v for k, v in saved["cache"].items() if k in self.sources and isinstance(v, dict)}
        if saved and isinstance(saved.get("intel"), dict):
            self.intel = {k: v for k, v in saved["intel"].items() if k in ("flights", "satellites", "cameras") and isinstance(v, dict)}

    async def async_manual_refresh(self):
        # The refresh button cannot turn a shared free API into a rapid poll loop.
        if time.time() - self._last_manual < 60:
            return
        self._last_manual = time.time()
        self._force = True
        await self.async_request_refresh()

    async def async_save(self):
        await self.store.async_save({"cache": self.cache, "intel": self.intel})

    async def async_fetch_intel(self, kind, latitude=45, longitude=15, provider="london"):
        if kind == "cameras":
            return await self.async_fetch_cameras(provider, latitude, longitude)
        if kind not in ("flights", "satellites"):
            raise ValueError("Unbekannte Ebene")
        url, lat, lon = flight_url(latitude, longitude) if kind == "flights" else (SATELLITE_URL, None, None)
        async with self._intel_lock:
            now = time.time()
            old = self.intel.get(kind, {})
            cooldown = 60 if kind == "flights" else 7200
            if now - old.get("last_attempt", 0) < cooldown:
                return
            state = {**old, "last_attempt": now}
            try:
                async with self.session.get(url, headers={"User-Agent": f"HomeAssistant-Weltlage/{VERSION}", "Accept": "application/json"}, timeout=aiohttp.ClientTimeout(total=20)) as response:
                    response.raise_for_status()
                    chunks, size = [], 0
                    async for chunk in response.content.iter_chunked(65536):
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise ValueError("Intel-Antwort zu gross")
                        chunks.append(chunk)
                parser = parse_flights if kind == "flights" else parse_satellites
                items = await self.hass.async_add_executor_job(parser, b"".join(chunks), now)
                state.update(items=items, last_success=now, error=None, latitude=lat, longitude=lon, radius_nm=250 if kind == "flights" else None)
            except (aiohttp.ClientError, TimeoutError, ValueError, KeyError, TypeError) as err:
                state["error"] = "Zeitüberschreitung" if isinstance(err, TimeoutError) else "Intel-Quelle nicht erreichbar" if isinstance(err, aiohttp.ClientError) else "Intel-Daten konnten nicht verarbeitet werden"
            self.intel[kind] = state
            if self.data is not None:
                self.async_set_updated_data({**self.data, "intel": dict(self.intel)})
            await self.async_save()

    async def async_fetch_cameras(self, provider, latitude, longitude):
        if provider not in CAMERA_PROVIDERS:
            raise ValueError("Unbekannte Kameraquelle")
        # Validate coordinates using the same bounded globe-centre validator.
        _, lat, lon = flight_url(latitude, longitude)
        async with self._intel_lock:
            now = time.time()
            providers = dict(self.intel.get("cameras", {}).get("providers", {}))
            old = providers.get(provider, {})
            cooldown = 60 if old.get("error") else 3600
            if now - old.get("last_attempt", 0) < cooldown:
                return
            state = {**old, "last_attempt": now}
            try:
                headers = {"User-Agent": f"HomeAssistant-Weltlage/{VERSION}", "Digitraffic-User": f"ha-weltlage/{VERSION}", "Accept": "application/json", "Accept-Encoding": "gzip"}
                async with self.session.get(CAMERA_PROVIDERS[provider]["url"], headers=headers, timeout=aiohttp.ClientTimeout(total=25), allow_redirects=False) as response:
                    response.raise_for_status()
                    if response.status != 200:
                        raise ValueError("Kamerakatalog nicht verfügbar")
                    chunks, size = [], 0
                    async for chunk in response.content.iter_chunked(65536):
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise ValueError("Kamerakatalog zu gross")
                        chunks.append(chunk)
                all_items = await self.hass.async_add_executor_job(parse_cameras, b"".join(chunks), provider, now)
                items = nearest_cameras(all_items, lat, lon, 600)
                state.update(items=items, total=len(all_items), last_success=now, error=None)
            except (aiohttp.ClientError, TimeoutError, ValueError, KeyError, TypeError) as err:
                state["error"] = "Zeitüberschreitung" if isinstance(err, TimeoutError) else "Kameraquelle nicht erreichbar" if isinstance(err, aiohttp.ClientError) else "Kameradaten konnten nicht verarbeitet werden"
            providers[provider] = state
            self.intel["cameras"] = {"providers": providers}
            if self.data is not None:
                self.async_set_updated_data({**self.data, "intel": dict(self.intel)})
            await self.async_save()

    async def _fetch(self, key, source, now, force):
        old = self.cache.get(key, {})
        if not force and now < min(old.get("next_due", 0), now + 3600):
            return
        headers = {"User-Agent": "HomeAssistant-Weltlage/1.0", "Accept": "application/rss+xml, application/atom+xml, application/json, application/xml, text/xml;q=0.9"}
        if old.get("etag"):
            headers["If-None-Match"] = old["etag"]
        if old.get("modified"):
            headers["If-Modified-Since"] = old["modified"]
        state = {**old, "last_attempt": now}
        try:
            async with self._semaphore:
                async with self.session.get(source["url"], headers=headers, timeout=aiohttp.ClientTimeout(total=18)) as response:
                    state["http_status"] = response.status
                    if response.status == 304:
                        if "items" not in old:
                            raise ValueError("304 ohne gespeicherte Daten")
                        items = old["items"]
                    else:
                        response.raise_for_status()
                        chunks, size = [], 0
                        async for chunk in response.content.iter_chunked(65536):
                            size += len(chunk)
                            if size > MAX_BYTES:
                                raise ValueError("Antwort überschreitet 2 MB")
                            chunks.append(chunk)
                        body = b"".join(chunks)
                        parser = parse_usgs if source["kind"] == "usgs" else parse_gdacs if source["kind"] == "gdacs" else None
                        items = await self.hass.async_add_executor_job(parser, body, now) if parser else await self.hass.async_add_executor_job(parse_news, body, key, source, now)
                        if source["kind"] == "news":
                            previous = {a["id"]: a for a in old.get("items", [])}
                            for item in items:
                                if item["id"] in previous:
                                    item["first_seen"] = previous[item["id"]].get("first_seen", now)
                            # Keep dated history across short upstream feed windows.
                            ids = {a["id"] for a in items}
                            items.extend(a for a in old.get("items", []) if a["id"] not in ids and now - (a.get("published") or a.get("first_seen", 0)) < RETENTION_HOURS * 3600)
                            items = sorted(items, key=lambda a: a.get("published") or a["first_seen"], reverse=True)[:50]
                        state["etag"] = response.headers.get("ETag", "")[:500]
                        state["modified"] = response.headers.get("Last-Modified", "")[:200]
            state.update(items=items, last_success=now, failures=0, error=None, next_due=now + source["interval"])
        except (aiohttp.ClientError, TimeoutError, ValueError, KeyError, TypeError) as err:
            failures = min(8, old.get("failures", 0) + 1)
            state.update(failures=failures, error="Zeitüberschreitung" if isinstance(err, TimeoutError) else "Netzwerkfehler" if isinstance(err, aiohttp.ClientError) else "Feed konnte nicht verarbeitet werden", next_due=now + min(3600, source["interval"] * 2 ** (failures - 1)))
            _LOGGER.debug("Weltlage source %s failed: %s", key, type(err).__name__)
        self.cache[key] = state

    async def _async_update_data(self):
        now = time.time()
        force, self._force = self._force, False
        await asyncio.gather(*(self._fetch(k, s, now, force) for k, s in self.sources.items()))
        source_rows, news, hazards = [], [], []
        for key, source in self.sources.items():
            state = self.cache.get(key, {})
            last = state.get("last_success")
            stale = last is None or now - last > max(source["interval"] * 2, 900)
            status = "unavailable" if last is None else "error" if state.get("error") else "stale" if stale else "ok"
            items = state.get("items", [])
            source_rows.append({"id": key, "name": source["name"], "url": source["url"], "kind": source["kind"], "status": status, "last_success": iso(last), "last_attempt": iso(state.get("last_attempt")), "latest_entry": iso(max((a.get("published") or 0 for a in items), default=0)) if any(a.get("published") for a in items) else None, "interval": source["interval"], "error": state.get("error"), "count": len(items)})
            if source["kind"] == "news":
                news.extend(items)
            else:
                hazards.extend(h for h in items if (h.get("expires") is None and now - (h.get("published") or 0) < 30 * 86400) or (h.get("expires") is not None and h["expires"] > now))
        articles = merge_news(news, now)
        good = sum(s["status"] == "ok" for s in source_rows)
        news_times = [s["last_success"] for s in source_rows if s["kind"] == "news" and s["last_success"]]
        self.store.async_delay_save(lambda: {"cache": self.cache, "intel": self.intel}, 10)
        return {"integration": DOMAIN, "version": VERSION, "articles": articles, "intel": dict(self.intel), "hazards": sorted(hazards, key=lambda h: h.get("published") or 0, reverse=True), "sources": source_rows, "status": "ok" if good == len(source_rows) else "partial" if good else "unavailable", "current_sources": good, "total_sources": len(source_rows), "news_last_success": max(news_times, default=None), "generated_at": iso(now), "news_24h": sum(a.get("published") is not None and now - a["published"] <= 86400 for a in articles)}
