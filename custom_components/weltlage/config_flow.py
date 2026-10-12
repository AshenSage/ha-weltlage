"""Local HA options for six optional credentials and a conservative request budget."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN
from .layers import KEYS
from .credentials import async_local_credentials


def schema(values):
    fields = {vol.Optional(k, description={"suggested_value": values.get(k, "")}): selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)) for k in KEYS}
    fields[vol.Optional("request_budget", default=values.get("request_budget", 500))] = vol.All(vol.Coerce(int), vol.Range(min=20, max=2000))
    return vol.Schema(fields)


def clean(values):
    result = {k: str(values.get(k, "")).strip() for k in KEYS}
    if any(len(v) > 4000 or any(ord(c) < 32 for c in v) for v in result.values()):
        raise ValueError("invalid_key")
    result["request_budget"] = values.get("request_budget", 500)
    return result


class WeltlageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        errors = {}
        if user_input is not None:
            try:
                return self.async_create_entry(title="Weltlage", data=clean(user_input))
            except ValueError:
                errors["base"] = "invalid_key"
        try:
            local = await async_local_credentials(self.hass)
        except ValueError:
            local = {}
            errors["base"] = "invalid_local_file"
        return self.async_show_form(step_id="user", data_schema=schema(user_input or local), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WeltlageOptionsFlow()


class WeltlageOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        try:
            local = await async_local_credentials(self.hass)
        except ValueError:
            local = {}
            errors["base"] = "invalid_local_file"
        values = {**local, **self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            try:
                return self.async_create_entry(title="", data=clean(user_input))
            except ValueError:
                errors["base"] = "invalid_key"
        return self.async_show_form(step_id="init", data_schema=schema(user_input or values), errors=errors)
