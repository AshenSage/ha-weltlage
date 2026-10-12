"""Optional private key file in HA's config root, preserved by HACS updates."""
import json
from pathlib import Path
from .layers import KEYS

CREDENTIALS_FILE = "weltlage_credentials.json"
MAX_SIZE = 20_000


def read_local_credentials(path):
    """Read only the fixed private config file; never log its contents."""
    file = Path(path)
    try:
        if not file.exists():
            return {}
        if file.stat().st_size > MAX_SIZE:
            raise ValueError
        data = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError
        result = {}
        for key in KEYS:
            if key not in data:
                continue
            value = data[key]
            if not isinstance(value, str) or len(value) > 4000 or any(ord(c) < 32 for c in value):
                raise ValueError
            result[key] = value.strip()
        return result
    except (OSError, ValueError, UnicodeError):
        raise ValueError("Lokale Weltlage-Schlüsseldatei ungültig oder nicht lesbar") from None


async def async_local_credentials(hass):
    return await hass.async_add_executor_job(read_local_credentials, hass.config.path(CREDENTIALS_FILE))
