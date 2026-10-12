"""Authenticated, bounded HA WebSocket API; no data in Recorder attributes."""
import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import callback
from .const import DOMAIN, VERSION
from .layers import LAYERS, SATELLITE_GROUPS
from .providers import SourceError

def provider(hass):
    entries = hass.config_entries.async_entries(DOMAIN)
    for entry in entries:
        runtime = getattr(entry, "runtime_data", None)
        if runtime and getattr(runtime, "globe", None):
            return runtime.globe
    raise SourceError("unavailable", "Weltlage zuerst unter Geräte & Dienste einrichten")

@websocket_api.websocket_command({vol.Required("type"): "weltlage/config"})
@websocket_api.async_response
async def config(hass, connection, msg):
    try:
        p = provider(hass)
        connection.send_result(msg["id"], {"version": VERSION, "layers": LAYERS, "configured": {k: bool(v) for k,v in p.credentials.items()}, "cesium_ion_token": p.credentials.get("cesium_ion_token", "")})
    except SourceError as err:
        connection.send_error(msg["id"], err.status, err.message)

@websocket_api.websocket_command({vol.Required("type"): "weltlage/layer", vol.Required("layer"): vol.In(list(LAYERS)), vol.Required("bbox"): vol.All([vol.Coerce(float)], vol.Length(min=4,max=4)), vol.Optional("group", default="stations"): vol.In(SATELLITE_GROUPS), vol.Optional("date"): vol.All(str, vol.Length(max=10))})
@websocket_api.async_response
async def layer(hass, connection, msg):
    try:
        result = await provider(hass).layer(msg["layer"], msg["bbox"], msg["group"], msg.get("date"))
        connection.send_result(msg["id"], result)
    except ValueError:
        connection.send_error(msg["id"], "invalid_parameters", "Ungültiger Ausschnitt oder Filter")
    except SourceError as err:
        connection.send_error(msg["id"], err.status, err.message)

@websocket_api.websocket_command({vol.Required("type"): "weltlage/camera", vol.Required("camera_id"): vol.All(str, vol.Match(r"^\d{1,16}$"))})
@websocket_api.async_response
async def camera(hass, connection, msg):
    try:
        connection.send_result(msg["id"], await provider(hass).camera(msg["camera_id"]))
    except (SourceError, ValueError) as err:
        connection.send_error(msg["id"], getattr(err,"status","invalid_parameters"), getattr(err,"message","Ungültige Kamera-ID"))

@websocket_api.websocket_command({vol.Required("type"): "weltlage/streetphoto", vol.Required("image_id"): vol.All(str, vol.Match(r"^\d{1,32}$"))})
@websocket_api.async_response
async def streetphoto(hass, connection, msg):
    try:
        connection.send_result(msg["id"], await provider(hass).streetphoto(msg["image_id"]))
    except (SourceError, ValueError) as err:
        connection.send_error(msg["id"], getattr(err, "status", "invalid_parameters"), getattr(err, "message", "Ungültige Bild-ID"))

@callback
def register(hass):
    state = hass.data.setdefault(DOMAIN, {})
    if state.get("websocket_registered"):
        return
    for handler in (config, layer, camera, streetphoto):
        websocket_api.async_register_command(hass, handler)
    state["websocket_registered"] = True
