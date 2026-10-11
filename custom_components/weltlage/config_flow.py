"""Configure source selection and refresh interval through HA's UI."""
try:
    import probatio as vol
except ImportError:
    import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN, FEEDS, DEFAULT_FEEDS


def schema(values):
    return vol.Schema({
        vol.Required("feeds", default=values.get("feeds", DEFAULT_FEEDS)): selector.SelectSelector(selector.SelectSelectorConfig(options=[{"value": k, "label": v["name"]} for k, v in FEEDS.items()], multiple=True, mode=selector.SelectSelectorMode.DROPDOWN)),
        vol.Required("interval", default=values.get("interval", 15)): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
    })


class WeltlageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        errors = {}
        if user_input is not None:
            if not user_input.get("feeds") or any(k not in FEEDS for k in user_input["feeds"]):
                errors["feeds"] = "select_feeds"
            else:
                return self.async_create_entry(title="Weltlage", data=user_input)
        return self.async_show_form(step_id="user", data_schema=schema(user_input or {}), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WeltlageOptionsFlow()


class WeltlageOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input.get("feeds") or any(k not in FEEDS for k in user_input["feeds"]):
                errors["feeds"] = "select_feeds"
            else:
                return self.async_create_entry(title="", data=user_input)
        values = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=schema(user_input or values), errors=errors)
