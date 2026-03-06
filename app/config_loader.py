from __future__ import annotations

import json
from pathlib import Path

from app.models import AppConfig


def load_config(config_path: str | Path) -> AppConfig:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as file_handle:
        payload = json.load(file_handle)
    return AppConfig.from_dict(payload)
