"""Exercise the real asset views and automatic resource migration."""
import asyncio
from copy import deepcopy
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace, ModuleType
import sys
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from aiohttp import web, ClientSession
import bootstrap


class ResourceStorageCollection:
    """Match HA's collection interface; retain IDs and foreign resource fields."""
    def __init__(self, items=()):
        self.data = deepcopy(list(items))
        self.loaded = False
        self.changes = []

    async def async_get_info(self):
        self.loaded = True
        return {"resources": len(self.data)}

    def async_items(self):
        assert self.loaded
        return self.data

    async def async_create_item(self, data):
        item = {"id": "created", "url": data["url"], "type": data["res_type"]}
        self.data.append(item)
        self.changes.append(("create", item["id"]))
        return item

    async def async_update_item(self, item_id, data):
        item = next(item for item in self.data if item["id"] == item_id)
        item.update(url=data["url"], type=data["res_type"])
        self.changes.append(("update", item_id))
        return item

    async def async_delete_item(self, item_id):
        self.data = [item for item in self.data if item["id"] != item_id]
        self.changes.append(("delete", item_id))


class ResourceYAMLCollection:
    def __init__(self, items):
        self.data = items

    async def async_get_info(self):
        return {"resources": len(self.data)}

    def async_items(self):
        return self.data


for name in ("homeassistant", "homeassistant.components", "homeassistant.components.lovelace", "homeassistant.helpers"):
    sys.modules.setdefault(name, ModuleType(name))
ll_const = ModuleType("homeassistant.components.lovelace.const")
ll_const.LOVELACE_DATA = "lovelace"
sys.modules.setdefault(ll_const.__name__, ll_const)
ll_resources = ModuleType("homeassistant.components.lovelace.resources")
ll_resources.ResourceStorageCollection = ResourceStorageCollection
sys.modules.setdefault(ll_resources.__name__, ll_resources)
http = ModuleType("homeassistant.helpers.http")
http.HomeAssistantView = type("HomeAssistantView", (), {})
sys.modules.setdefault(http.__name__, http)
frontend = import_module("weltlage_backend.frontend")

FOREIGN = {"id": "foreign", "url": "/hacsfiles/another-card.js?v=7", "type": "module", "custom_field": "retained"}


class FrontendTests(IsolatedAsyncioTestCase):
    def make_hass(self, items=()):
        collection = ResourceStorageCollection(items)
        async def executor(fn):
            return await asyncio.to_thread(fn)
        return SimpleNamespace(data={"lovelace": SimpleNamespace(resources=collection)}, http=SimpleNamespace(register_view=Mock()), async_add_executor_job=executor)

    async def test_first_install_creates_resource_and_exposes_only_two_files(self):
        hass = self.make_hass([FOREIGN])
        await frontend.async_register_frontend(hass)
        views = [call.args[0] for call in hass.http.register_view.call_args_list]
        self.assertEqual({v.url for v in views}, {"/weltlage/weltlage-card.js", "/weltlage/weltlage-globe.js"})
        self.assertTrue(all(not v.requires_auth for v in views))
        collection = hass.data["lovelace"].resources
        self.assertEqual(collection.data[0], FOREIGN)
        current = collection.data[1]
        self.assertEqual(current["type"], "module")
        self.assertTrue(current["url"].startswith(frontend.CARD_URL + "?v=" + frontend.VERSION + "-"))

    async def test_existing_legacy_resource_migrates_with_its_id(self):
        hass = self.make_hass([FOREIGN, {"id": "old", "url": "/local/weltlage/weltlage-card.js?v=1.0.0", "type": "js"}])
        await frontend.async_register_frontend(hass)
        items = hass.data["lovelace"].resources.data
        self.assertEqual(items[0], FOREIGN)
        self.assertEqual(items[1]["id"], "old")
        self.assertEqual(items[1]["type"], "module")
        self.assertTrue(items[1]["url"].startswith(frontend.CARD_URL + "?v=" + frontend.VERSION))

    async def test_duplicate_own_urls_removed_foreign_and_external_urls_retained(self):
        external = {"id": "external", "url": "https://another.example/weltlage/weltlage-card.js", "type": "module"}
        hass = self.make_hass([FOREIGN, external, {"id": "old", "url": "/local/weltlage/weltlage-card.js", "type": "module"}, {"id": "current", "url": frontend.CARD_URL + "?v=1.1.0", "type": "module"}])
        await frontend.async_register_frontend(hass)
        items = hass.data["lovelace"].resources.data
        self.assertEqual(items[:2], [FOREIGN, external])
        self.assertEqual([item["id"] for item in items], ["foreign", "external", "current"])

    async def test_unchanged_registration_performs_no_extra_writes_or_routes(self):
        hass = self.make_hass()
        await frontend.async_register_frontend(hass)
        changes = list(hass.data["lovelace"].resources.changes)
        await frontend.async_register_frontend(hass)
        self.assertEqual(hass.http.register_view.call_count, 2)
        self.assertEqual(hass.data["lovelace"].resources.changes, changes)

    async def test_asset_change_on_next_start_updates_url_without_user_action(self):
        hass = self.make_hass()
        await frontend.async_register_frontend(hass)
        old = deepcopy(hass.data["lovelace"].resources.data)
        next_hass = self.make_hass(old)
        next_hass.data["weltlage"] = {"frontend_assets": {"weltlage-card.js": b"new", "weltlage-globe.js": b"new globe"}, "frontend_revision": "newrevision"}
        await frontend.async_register_frontend(next_hass)
        current = next_hass.data["lovelace"].resources.data[0]
        self.assertNotEqual(current["url"], old[0]["url"])
        self.assertEqual(current["id"], old[0]["id"])

    async def test_yaml_runtime_updated_without_editing_original_configuration(self):
        original = [FOREIGN, {"url": "/local/weltlage/weltlage-card.js?v=old", "type": "module"}]
        before = deepcopy(original)
        hass = self.make_hass()
        hass.data["lovelace"].resources = ResourceYAMLCollection(original)
        await frontend.async_register_frontend(hass)
        self.assertEqual(original, before)
        self.assertEqual(hass.data["lovelace"].resources.data[0], FOREIGN)
        self.assertTrue(hass.data["lovelace"].resources.data[1]["url"].startswith(frontend.CARD_URL))

    async def test_partial_route_registration_failure_can_retry(self):
        hass = self.make_hass()
        hass.http.register_view.side_effect = [None, RuntimeError("test"), None]
        with self.assertRaises(RuntimeError):
            await frontend.async_register_frontend(hass)
        self.assertFalse(hass.data["weltlage"].get("frontend_registered"))
        await frontend.async_register_frontend(hass)
        self.assertEqual(hass.http.register_view.call_count, 3)
        self.assertTrue(hass.data["weltlage"]["frontend_registered"])

    async def test_http_always_returns_current_script_with_no_store_even_for_old_query(self):
        hass = self.make_hass()
        await frontend.async_register_frontend(hass)
        app = web.Application()
        for call in hass.http.register_view.call_args_list:
            view = call.args[0]
            app.router.add_get(view.url, view.get)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        try:
            async with ClientSession() as client:
                for name in ("weltlage-card.js", "weltlage-globe.js"):
                    async with client.get(f"http://127.0.0.1:{port}/weltlage/{name}?v=1.0.0", headers={"If-None-Match": '"old"', "If-Modified-Since": "Wed, 01 Jan 2031 00:00:00 GMT"}) as response:
                        self.assertEqual(response.status, 200)
                        self.assertEqual(response.headers["Cache-Control"], "no-store, max-age=0")
                        self.assertEqual(response.content_type, "application/javascript")
                        self.assertEqual(await response.read(), (Path(frontend.__file__).parent / "frontend" / name).read_bytes())
                async with client.get(f"http://127.0.0.1:{port}/weltlage/const.py") as response:
                    self.assertEqual(response.status, 404)
        finally:
            await runner.cleanup()
