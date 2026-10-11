"""Import the actual backend without requiring a full HA installation."""
import importlib
from pathlib import Path
import sys
import types

BACKEND = Path(__file__).resolve().parents[1] / "custom_components" / "weltlage"
package = types.ModuleType("weltlage_backend")
package.__path__ = [str(BACKEND)]
sys.modules.setdefault("weltlage_backend", package)
parsers = importlib.import_module("weltlage_backend.parsers")


def coordinator_module():
    """Stub only HA's scheduling/storage interfaces; HTTP/parser code is real."""
    modules = ["homeassistant", "homeassistant.helpers", "homeassistant.helpers.aiohttp_client", "homeassistant.helpers.storage", "homeassistant.helpers.update_coordinator"]
    for name in modules:
        sys.modules.setdefault(name, types.ModuleType(name))

    class Store:
        def __init__(self, hass, version, key):
            self.hass, self.key = hass, key
        async def async_load(self):
            return self.hass.saved.get(self.key)
        async def async_save(self, value):
            self.hass.saved[self.key] = value
        def async_delay_save(self, factory, delay):
            self.hass.pending_save = factory

    class Coordinator:
        def __init__(self, hass, logger, **kwargs):
            self.hass, self.data = hass, None
        async def async_request_refresh(self):
            self.data = await self._async_update_data()
        def async_set_updated_data(self, data):
            self.data = data

    sys.modules[modules[2]].async_get_clientsession = lambda hass: hass.session
    sys.modules[modules[3]].Store = Store
    sys.modules[modules[4]].DataUpdateCoordinator = Coordinator
    return importlib.import_module("weltlage_backend.coordinator")
