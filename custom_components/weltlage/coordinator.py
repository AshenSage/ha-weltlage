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

_LOGGER = logging.getLogger(__name__)


class WeltlageCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=5), config_entry=entry)
        self.entry = entry
        self.session = async_get_clientsession(hass)
        self.store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}")
        self.cache = {}
        self._semaphore = asyncio.Semaphore(3)
        self._last_manual = 0
        self._force = False
        selected = entry.options.get("feeds", entry.data.get("feeds", DEFAULT_FEEDS))
        news_interval = max(300, min(3600, int(entry.options.get("interval", entry.data.get("interval", 15))) * 60))
        self.sources = {key: {**FEEDS[key], "kind": "news", "interval": news_interval} for key in selected if key in FEEDS}
        self.sources.update(HAZARD_SOURCES)

    async def async_load(self):
        saved = await self.store.async_load()
        if saved and isinstance(saved.get("cache"), dict):
            self.cache = {k: v for k, v in saved["cache"].items() if k in self.sources and isinstance(v, dict)}

    async def async_manual_refresh(self):
        # The refresh button cannot turn a shared free API into a rapid poll loop.
        if time.time() - self._last_manual < 60:
            return
        self._last_manual = time.time()
        self._force = True
        await self.async_request_refresh()

    async def async_save(self):
        await self.store.async_save({"cache": self.cache})

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
        self.store.async_delay_save(lambda: {"cache": self.cache}, 10)
        return {"integration": DOMAIN, "version": VERSION, "articles": articles, "hazards": sorted(hazards, key=lambda h: h.get("published") or 0, reverse=True), "sources": source_rows, "status": "ok" if good == len(source_rows) else "partial" if good else "unavailable", "current_sources": good, "total_sources": len(source_rows), "news_last_success": max(news_times, default=None), "generated_at": iso(now), "news_24h": sum(a.get("published") is not None and now - a["published"] <= 86400 for a in articles)}
