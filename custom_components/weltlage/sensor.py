"""One compact overview payload; large feed attributes are not recorded."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, VERSION


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([WeltlageSensor(entry.runtime_data, entry, role) for role in ("lagebild", "quellenstatus")])


class WeltlageSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _unrecorded_attributes = frozenset({"articles", "hazards", "sources"})

    def __init__(self, coordinator, entry, role):
        super().__init__(coordinator)
        self.role = role
        self._attr_unique_id = f"{entry.entry_id}_{role}"
        self._attr_name = "Lagebild" if role == "lagebild" else "Quellenstatus"
        self._attr_icon = "mdi:earth" if role == "lagebild" else "mdi:database-clock"
        if role == "quellenstatus":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}, "name": "Weltlage", "manufacturer": "Weltlage", "model": "Weltinformation", "sw_version": VERSION}

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        if self.role == "quellenstatus":
            return data.get("status", "unavailable")
        if not any(s.get("kind") == "news" and s.get("last_success") for s in data.get("sources", [])):
            return None
        return data.get("news_24h", 0)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return data if self.role == "lagebild" else {"integration": DOMAIN, "sources": data.get("sources", []), "current_sources": data.get("current_sources", 0), "total_sources": data.get("total_sources", 0)}
