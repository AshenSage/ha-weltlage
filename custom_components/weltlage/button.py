"""Manual refresh, with a 60-second minimum interval."""
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([WeltlageRefresh(entry.runtime_data, entry)])


class WeltlageRefresh(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Aktualisieren"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_refresh"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}}
        self._attr_extra_state_attributes = {"integration": DOMAIN, "role": "refresh"}

    async def async_press(self):
        await self.coordinator.async_manual_refresh()
