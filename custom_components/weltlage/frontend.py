"""Serve current assets and maintain only Weltlage's Lovelace resource."""
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit

from aiohttp import web
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.helpers.http import HomeAssistantView

from .const import DOMAIN, VERSION

CARD_URL = "/weltlage/weltlage-card.js"
_ASSETS = ("weltlage-card.js", "weltlage-globe.js")
_OWN_PATHS = {CARD_URL, "/local/weltlage/weltlage-card.js"}
_HEADERS = {
    "Cache-Control": "no-store, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "X-Content-Type-Options": "nosniff",
}


def _read_assets():
    """Read exactly two public files outside HA's event loop."""
    folder = Path(__file__).parent / "frontend"
    assets = {name: (folder / name).read_bytes() for name in _ASSETS}
    revision = sha256(b"\0".join(assets.values())).hexdigest()[:12]
    return assets, revision


def _is_own_resource(url):
    try:
        parts = urlsplit(str(url))
        return not parts.scheme and not parts.netloc and parts.path in _OWN_PATHS
    except ValueError:
        return False


class WeltlageAssetView(HomeAssistantView):
    """The query string never selects an old asset version."""

    requires_auth = False  # Public JavaScript only, no user or integration data.

    def __init__(self, name, content):
        self.url = f"/weltlage/{name}"
        self.name = f"weltlage:{name}"
        self._content = content

    async def get(self, request):
        return web.Response(body=self._content, content_type="application/javascript", headers=_HEADERS)

    async def head(self, request):
        return await self.get(request)


async def _async_update_resource(hass, revision):
    collection = hass.data[LOVELACE_DATA].resources
    # This public method also loads the storage collection before listing it.
    await collection.async_get_info()
    items = list(collection.async_items())
    own = [item for item in items if _is_own_resource(item.get("url", ""))]
    url = f"{CARD_URL}?v={VERSION}-{revision}"
    if isinstance(collection, ResourceStorageCollection):
        # Prefer the current path; retain its ID, remove only duplicate own URLs.
        current = next((item for item in own if urlsplit(item["url"]).path == CARD_URL), own[0] if own else None)
        if current is None:
            await collection.async_create_item({"url": url, "res_type": "module"})
        elif current.get("url") != url or current.get("type") != "module":
            await collection.async_update_item(current["id"], {"url": url, "res_type": "module"})
        for item in own:
            if current is not None and item["id"] != current["id"]:
                await collection.async_delete_item(item["id"])
    else:
        # YAML resources are a runtime collection; never edit configuration files.
        collection.data = [item for item in items if not _is_own_resource(item.get("url", ""))] + [{"url": url, "type": "module"}]


async def async_register_frontend(hass):
    state = hass.data.setdefault(DOMAIN, {})
    if "frontend_revision" not in state:
        assets, revision = await hass.async_add_executor_job(_read_assets)
        state["frontend_assets"] = assets
        state["frontend_revision"] = revision
    registered = state.setdefault("frontend_views", set())
    for name, content in state["frontend_assets"].items():
        if name not in registered:
            hass.http.register_view(WeltlageAssetView(name, content))
            registered.add(name)
    await _async_update_resource(hass, state["frontend_revision"])
    state["frontend_registered"] = True
