"""Weltlage custom integration."""
from homeassistant.const import Platform
from .coordinator import WeltlageCoordinator
from .frontend import async_register_frontend

PLATFORMS = [Platform.SENSOR, Platform.BUTTON]


async def async_setup(hass, config):
    await async_register_frontend(hass)
    return True


async def async_setup_entry(hass, entry):
    coordinator = WeltlageCoordinator(hass, entry)
    await coordinator.async_load()
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
        await entry.runtime_data.async_save()
    return unloaded
