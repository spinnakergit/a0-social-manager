"""API endpoint: Get/set Social Media Manager plugin configuration.
URL: POST /api/plugins/social_manager/social_manager_config_api

Manages: default_platforms, adapt_content, content_preferences, schedule settings.
"""
import json
import os
import yaml
from pathlib import Path
from helpers.api import ApiHandler, Request, Response


def _get_config_path() -> Path:
    """Find the writable config path."""
    candidates = [
        Path(__file__).parent.parent / "config.json",
        Path("/a0/usr/plugins/social_manager/config.json"),
        Path("/a0/plugins/social_manager/config.json"),
    ]
    for p in candidates:
        if p.parent.exists():
            return p
    return candidates[-1]


def _load_defaults() -> dict:
    """Load default_config.yaml as baseline."""
    default_path = Path(__file__).parent.parent / "default_config.yaml"
    if default_path.exists():
        with open(default_path) as f:
            return yaml.safe_load(f) or {}
    return {}


class SocialManagerConfigApi(ApiHandler):

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["GET", "POST"]

    @classmethod
    def requires_csrf(cls) -> bool:
        return True

    async def process(self, input: dict, request: Request) -> dict | Response:
        action = input.get("action", "get")
        if request.method == "GET" or action == "get":
            return self._get_config()
        else:
            return self._set_config(input)

    def _get_config(self) -> dict:
        try:
            config_path = _get_config_path()
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
            else:
                config = _load_defaults()

            return config
        except Exception:
            return {"error": "Failed to read configuration."}

    def _set_config(self, input: dict) -> dict:
        try:
            config = input.get("config", input)
            if not config or config == {"action": "set"}:
                return {"error": "No config provided"}
            config.pop("action", None)

            config_path = _get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Merge with existing config
            existing = {}
            if config_path.exists():
                with open(config_path, "r") as f:
                    existing = json.load(f)

            # Deep merge content_preferences and schedule sub-dicts
            for key in ("content_preferences", "schedule"):
                if key in config and isinstance(config[key], dict):
                    existing_sub = existing.get(key, {})
                    existing_sub.update(config[key])
                    config[key] = existing_sub

            existing.update(config)

            # Atomic write with restrictive permissions
            tmp = config_path.with_suffix(".tmp")
            fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(existing, f, indent=2)
            os.replace(str(tmp), str(config_path))

            return {"ok": True}
        except Exception:
            return {"error": "Failed to save configuration."}
