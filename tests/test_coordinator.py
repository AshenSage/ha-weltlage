import asyncio
import json
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

import aiohttp
from aiohttp import web
from bootstrap import coordinator_module

c = coordinator_module()
RSS = b'<rss><channel><item><title>Undated article</title><link>https://example.org/story</link></item></channel></rss>'


class FakeHass:
    def __init__(self, session):
        self.session, self.saved, self.pending_save = session, {}, None
    async def async_add_executor_job(self, fn, *args):
        return await asyncio.to_thread(fn, *args)


class CoordinatorTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.responses = {"good": (200, RSS), "bad": (503, b"down")}
        self.requests = []
        async def handler(request):
            name = request.match_info["name"]
            self.requests.append((name, dict(request.headers)))
            status, body = self.responses[name]
            return web.Response(status=status, body=body, headers={"ETag": '"test"'})
        app = web.Application()
        app.router.add_get("/{name}", handler)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await self.site.start()
        port = self.site._server.sockets[0].getsockname()[1]
        self.session = aiohttp.ClientSession()
        self.hass = FakeHass(self.session)
        self.entry = SimpleNamespace(entry_id="test", data={"feeds": ["bbc_world"], "interval": 15}, options={})
        self.coordinator = c.WeltlageCoordinator(self.hass, self.entry)
        self.coordinator.sources = {name: {"name": name, "publisher": name, "url": f"http://127.0.0.1:{port}/{name}", "kind": "news", "interval": 900} for name in self.responses}

    async def asyncTearDown(self):
        await self.session.close()
        await self.runner.cleanup()

    async def test_one_failure_does_not_hide_good_source(self):
        data = await self.coordinator._async_update_data()
        self.assertEqual(data["status"], "partial")
        self.assertEqual(len(data["articles"]), 1)
        self.assertEqual(data["current_sources"], 1)
        self.assertEqual(self.coordinator.cache["bad"]["error"], "Netzwerkfehler")
        self.assertIsNotNone(self.hass.pending_save)

    async def test_304_keeps_items_and_conditional_headers(self):
        await self.coordinator._fetch("good", self.coordinator.sources["good"], 10000, True)
        self.responses["good"] = (304, b"")
        await self.coordinator._fetch("good", self.coordinator.sources["good"], 11000, True)
        state = self.coordinator.cache["good"]
        self.assertEqual(state["last_success"], 11000)
        self.assertEqual(state["items"][0]["first_seen"], 10000)
        self.assertEqual(self.requests[-1][1]["If-None-Match"], '"test"')

    async def test_failed_or_oversized_refresh_retains_last_good_data(self):
        await self.coordinator._fetch("good", self.coordinator.sources["good"], 10000, True)
        for body in (b"<html>Not a feed</html>", b"x" * (c.MAX_BYTES + 1)):
            self.responses["good"] = (200, body)
            await self.coordinator._fetch("good", self.coordinator.sources["good"], 11000, True)
            self.assertEqual(self.coordinator.cache["good"]["last_success"], 10000)
            self.assertEqual(len(self.coordinator.cache["good"]["items"]), 1)
            self.assertEqual(self.coordinator.cache["good"]["error"], "Feed konnte nicht verarbeitet werden")

    async def test_undated_articles_do_not_become_new_each_refresh(self):
        for now in (10000, 11000):
            await self.coordinator._fetch("good", self.coordinator.sources["good"], now, True)
        self.assertEqual(self.coordinator.cache["good"]["items"][0]["first_seen"], 10000)
        self.assertIsNone(self.coordinator.cache["good"]["items"][0]["published"])

    async def test_due_time_and_backoff_limit_requests(self):
        await self.coordinator._fetch("bad", self.coordinator.sources["bad"], 10000, False)
        await self.coordinator._fetch("bad", self.coordinator.sources["bad"], 10001, False)
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.coordinator.cache["bad"]["next_due"], 10900)
        await self.coordinator._fetch("bad", self.coordinator.sources["bad"], 10900, False)
        self.assertEqual(self.coordinator.cache["bad"]["next_due"], 12700)

    async def test_persistence_and_selected_sources(self):
        await self.coordinator._fetch("good", self.coordinator.sources["good"], 10000, True)
        await self.coordinator.async_save()
        self.hass.saved["weltlage.test"]["cache"]["not_selected"] = {"items": []}
        self.coordinator.cache = {}
        await self.coordinator.async_load()
        self.assertIn("good", self.coordinator.cache)
        self.assertNotIn("not_selected", self.coordinator.cache)

    async def test_manual_refresh_is_throttled(self):
        with patch.object(c.time, "time", return_value=10000):
            await self.coordinator.async_manual_refresh()
        count = len(self.requests)
        with patch.object(c.time, "time", return_value=10030):
            await self.coordinator.async_manual_refresh()
        self.assertEqual(len(self.requests), count)
        with patch.object(c.time, "time", return_value=10061):
            await self.coordinator.async_manual_refresh()
        self.assertGreater(len(self.requests), count)

    async def test_all_sources_failed_returns_explicit_unavailable(self):
        self.responses["good"] = (503, b"down")
        data = await self.coordinator._async_update_data()
        self.assertEqual(data["status"], "unavailable")
        self.assertEqual(data["current_sources"], 0)
        self.assertEqual(data["articles"], [])

    async def test_intel_only_loads_on_request_and_is_throttled(self):
        self.coordinator.data = {"articles": [{"id":"unchanged"}]}
        self.responses["good"] = (200, json.dumps({"now":10000,"ac":[{"hex":"abc123","lat":44,"lon":20,"seen_pos":1}]}).encode())
        url = self.coordinator.sources["good"]["url"]
        with patch.object(c, "flight_url", return_value=(url,45,20)), patch.object(c.time, "time", return_value=10000):
            await self.coordinator.async_fetch_intel("flights",44,20)
            await self.coordinator.async_fetch_intel("flights",44,20)
        self.assertEqual(len(self.requests),1)
        self.assertEqual(len(self.coordinator.data["intel"]["flights"]["items"]),1)
        self.assertEqual(self.coordinator.data["articles"],[{"id":"unchanged"}])
        self.assertEqual(self.coordinator.cache,{})

    async def test_intel_failure_keeps_last_good_snapshot_and_persists(self):
        self.coordinator.data = {}
        self.responses["good"] = (200,b'{"now":10000,"ac":[]}')
        url = self.coordinator.sources["good"]["url"]
        with patch.object(c, "flight_url", return_value=(url,45,20)), patch.object(c.time, "time", return_value=10000):
            await self.coordinator.async_fetch_intel("flights")
        self.responses["good"] = (503,b'down')
        with patch.object(c, "flight_url", return_value=(url,45,20)), patch.object(c.time, "time", return_value=10100):
            await self.coordinator.async_fetch_intel("flights")
        self.assertEqual(self.coordinator.intel["flights"]["last_success"],10000)
        self.assertIsNotNone(self.coordinator.intel["flights"]["error"])
        self.coordinator.intel = {}
        await self.coordinator.async_load()
        self.assertEqual(self.coordinator.intel["flights"]["last_success"],10000)

    async def test_satellite_requests_have_two_hour_cooldown(self):
        self.coordinator.data = {}
        self.responses["good"] = (200,b'[]')
        with patch.object(c,"SATELLITE_URL",self.coordinator.sources["good"]["url"]):
            for now in (10000,10100,17199):
                with patch.object(c.time,"time",return_value=now):
                    await self.coordinator.async_fetch_intel("satellites")
            self.assertEqual(len(self.requests),1)
            with patch.object(c.time,"time",return_value=17200):
                await self.coordinator.async_fetch_intel("satellites")
        self.assertEqual(len(self.requests),2)

    async def test_oversized_intel_and_unknown_kind_are_rejected(self):
        self.coordinator.data = {}
        self.responses["good"] = (200,b'x'*(c.MAX_BYTES+1))
        with patch.object(c,"SATELLITE_URL",self.coordinator.sources["good"]["url"]),patch.object(c.time,"time",return_value=10000):
            await self.coordinator.async_fetch_intel("satellites")
        self.assertIsNotNone(self.coordinator.intel["satellites"]["error"])
        with self.assertRaises(ValueError):
            await self.coordinator.async_fetch_intel("unknown")

    async def test_default_sources_drop_news_even_with_legacy_options(self):
        coordinator=c.WeltlageCoordinator(self.hass,self.entry)
        self.assertEqual(set(coordinator.sources),{'usgs','gdacs'})
        self.assertTrue(all(s['kind']!='news' for s in coordinator.sources.values()))

    async def test_camera_catalogs_are_opt_in_cached_independently_and_survive_failure(self):
        self.coordinator.data={}
        row={'id':'one','lat':51.5,'lon':0,'commonName':'Road','additionalProperties':[{'key':'available','value':'true'},{'key':'imageUrl','value':'https://s3-eu-west-1.amazonaws.com/jamcams.tfl.gov.uk/00001.02151.jpg'}]}
        self.responses['good']=(200,json.dumps([row]).encode())
        provider={**c.CAMERA_PROVIDERS['london'],'url':self.coordinator.sources['good']['url']}
        with patch.dict(c.CAMERA_PROVIDERS,{'london':provider}):
            for now in (10000,10060,13599):
                with patch.object(c.time,'time',return_value=now):await self.coordinator.async_fetch_intel('cameras',51,0,'london')
            self.assertEqual(len(self.requests),1)
            state=self.coordinator.intel['cameras']['providers']['london'];self.assertEqual(len(state['items']),1)
            self.assertEqual(self.requests[0][1]['Digitraffic-User'],'ha-weltlage/'+c.VERSION)
            self.responses['good']=(503,b'down')
            with patch.object(c.time,'time',return_value=13600):await self.coordinator.async_fetch_intel('cameras',51,0,'london')
            state=self.coordinator.intel['cameras']['providers']['london'];self.assertEqual(state['last_success'],10000);self.assertEqual(len(state['items']),1);self.assertIsNotNone(state['error'])
            self.coordinator.intel={};await self.coordinator.async_load();self.assertEqual(self.coordinator.intel['cameras']['providers']['london']['last_success'],10000)
            with self.assertRaises(ValueError):await self.coordinator.async_fetch_intel('cameras',51,0,'evil')
