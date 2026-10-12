"""Weltlage custom integration."""
from homeassistant.const import Platform
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
from .coordinator import WeltlageCoordinator
from .frontend import async_register_frontend
from .const import DOMAIN
from .layers import KEYS
from .providers import GlobeProviders
from .websocket import register as register_websocket

PLATFORMS = [Platform.SENSOR, Platform.BUTTON]


async def async_setup(hass, config):
    await async_register_frontend(hass)
    register_websocket(hass)
    async def fetch_intel(call):
        entries = hass.config_entries.async_entries(DOMAIN)
        coordinator = next((getattr(entry, "runtime_data", None) for entry in entries if getattr(entry, "runtime_data", None)), None)
        if coordinator is None:
            raise HomeAssistantError("Weltlage ist noch nicht eingerichtet")
        # Keep the legacy service callable, but never populate Recorder catalogs.
        lat, lon = call.data.get("latitude", 45), call.data.get("longitude", 15)
        kind = {"cameras": "finland"}.get(call.data["kind"], call.data["kind"])
        if call.data["kind"] == "cameras" and call.data.get("provider") != "finland":
            raise HomeAssistantError("Öffentliche Kameras jetzt direkt in der Globuskarte laden")
        await coordinator.globe.layer(kind, [max(-180, lon-1), max(-85, lat-1), min(180, lon+1), min(85, lat+1)])
    hass.services.async_register(DOMAIN, "fetch_intel", fetch_intel, schema=vol.Schema({vol.Optional("provider", default="london"): vol.In(["london", "finland", "bc"]), vol.Required("kind"): vol.In(["flights", "satellites", "cameras"]), vol.Optional("latitude", default=45): vol.All(vol.Coerce(float), vol.Range(min=-90, max=90)), vol.Optional("longitude", default=15): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180))}))
    return True


async def async_setup_entry(hass, entry):
    coordinator = WeltlageCoordinator(hass, entry)
    # Retain sensor IDs, but stop old polls and catalogs in sensor attributes.
    coordinator.sources = {}
    coordinator.update_interval = None
    values = {**entry.data, **entry.options}
    coordinator.globe = GlobeProviders(coordinator.session, hass.async_add_executor_job, {k: values.get(k, "") for k in KEYS}, values.get("request_budget", 500))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.globe.close()
    return unloaded
