"""Serve the bundled card so HACS updates integration and frontend together."""
from pathlib import Path

from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN

CARD_URL = "/weltlage/weltlage-card.js"


async def async_register_frontend(hass):
    state = hass.data.setdefault(DOMAIN, {})
    if state.get("frontend_registered"):
        return
    # Expose only the card file, not the integration's Python files or cache.
    card = Path(__file__).parent / "frontend" / "weltlage-card.js"
    await hass.http.async_register_static_paths([
        StaticPathConfig(CARD_URL, str(card), False)
    ])
    state["frontend_registered"] = True
