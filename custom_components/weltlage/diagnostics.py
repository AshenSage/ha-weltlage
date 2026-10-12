"""No credentials, signed image URLs, positions or provider bodies in diagnostics."""
from .const import VERSION
from .layers import KEYS

async def async_get_config_entry_diagnostics(hass, entry):
    p = getattr(getattr(entry, "runtime_data", None), "globe", None)
    values = {**entry.data, **entry.options}
    return {"version": VERSION, "credentials": {k: bool(values.get(k)) for k in KEYS}, "request_budget": values.get("request_budget", 500), "cached_products": len(p.cache) if p else 0, "inflight": len(p.inflight) if p else 0, "daily_counts": dict(p.daily) if p else {}}
