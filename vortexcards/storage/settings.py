from __future__ import annotations
import json
from pathlib import Path
from platformdirs import user_config_dir

DEFAULTS = {
    "width": 1280,
    "height": 720,
    "fullscreen": False,
    "master_volume": 0.8,
    "music_volume": 0.5,
    "sfx_volume": 0.8,
    "animation_speed": 1.0,
    "reduce_motion": False,
    "network_port": 27845,
    "reconnect_timeout": 45,
}

CONFIG_DIR = Path(user_config_dir("VortexCards", "VortexCards"))
CONFIG_FILE = CONFIG_DIR / "settings.json"


def load_settings() -> dict:
    data = DEFAULTS.copy()
    try:
        if CONFIG_FILE.exists():
            loaded = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update({k: v for k, v in loaded.items() if k in DEFAULTS})
    except (OSError, ValueError, TypeError):
        pass
    return data


def save_settings(settings: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    clean = DEFAULTS.copy()
    clean.update({k: v for k, v in settings.items() if k in DEFAULTS})
    CONFIG_FILE.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
