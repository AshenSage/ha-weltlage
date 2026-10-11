import importlib
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace, ModuleType
import sys
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

import bootstrap


@dataclass
class StaticPathConfig:
    url_path: str
    path: str
    cache_headers: bool


sys.modules.setdefault("homeassistant", ModuleType("homeassistant"))
sys.modules.setdefault("homeassistant.components", ModuleType("homeassistant.components"))
http = ModuleType("homeassistant.components.http")
http.StaticPathConfig = StaticPathConfig
sys.modules.setdefault("homeassistant.components.http", http)
frontend = importlib.import_module("weltlage_backend.frontend")


class FrontendTests(IsolatedAsyncioTestCase):
    def make_hass(self):
        return SimpleNamespace(data={"lovelace": {"untouched": True}}, http=SimpleNamespace(async_register_static_paths=AsyncMock()))

    async def test_only_bundled_javascript_is_exposed(self):
        hass = self.make_hass()
        await frontend.async_register_frontend(hass)
        paths = hass.http.async_register_static_paths.call_args.args[0]
        self.assertEqual(len(paths), 2)
        self.assertEqual({Path(p.path).name for p in paths}, {"weltlage-card.js", "weltlage-globe.js"})
        for p in paths:
            self.assertTrue(Path(p.path).is_file())
            self.assertFalse(p.cache_headers)
        self.assertEqual(paths[0].url_path, "/weltlage/weltlage-card.js")
        self.assertEqual(Path(paths[0].path).name, "weltlage-card.js")
        self.assertTrue(Path(paths[0].path).is_file())
        self.assertFalse(paths[0].cache_headers)
        self.assertEqual(hass.data["lovelace"], {"untouched": True})

    async def test_duplicate_registration_on_reload_is_avoided(self):
        hass = self.make_hass()
        await frontend.async_register_frontend(hass)
        await frontend.async_register_frontend(hass)
        hass.http.async_register_static_paths.assert_awaited_once()

    async def test_failed_registration_can_be_retried(self):
        hass = self.make_hass()
        hass.http.async_register_static_paths.side_effect = RuntimeError("test")
        with self.assertRaises(RuntimeError):
            await frontend.async_register_frontend(hass)
        self.assertFalse(hass.data["weltlage"].get("frontend_registered"))
        hass.http.async_register_static_paths.side_effect = None
        await frontend.async_register_frontend(hass)
        self.assertTrue(hass.data["weltlage"]["frontend_registered"])
