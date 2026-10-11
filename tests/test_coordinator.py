import asyncio
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
