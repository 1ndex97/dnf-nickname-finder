from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import keyring

APP_NAME = "DNF Nickname Finder"
SERVICE_NAME = "dnf-nickname-finder"


@dataclass(slots=True)
class AppConfig:
    selected_server: str = "all"
    result_limit: int = 100
    rate_limit_per_second: float = 3.0
    theme: str = "dark"


class ConfigManager:
    def __init__(self, path: Path | None = None) -> None:
        base = Path(os.getenv("APPDATA", Path.home() / ".config")) / SERVICE_NAME
        self.path = path or base / "config.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            allowed = {
                field: data[field]
                for field in AppConfig.__dataclass_fields__
                if field in data
            }
            return AppConfig(**allowed)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        self.path.write_text(
            json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get_api_key(self) -> str:
        return keyring.get_password(SERVICE_NAME, "neople_api_key") or ""

    def set_api_key(self, api_key: str) -> None:
        if api_key.strip():
            keyring.set_password(SERVICE_NAME, "neople_api_key", api_key.strip())
        else:
            try:
                keyring.delete_password(SERVICE_NAME, "neople_api_key")
            except keyring.errors.PasswordDeleteError:
                pass
