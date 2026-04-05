"""Social Media Manager — Platform detection and routing.

This is a META-PLUGIN orchestrator. It does not call external APIs directly;
instead it discovers which platform plugins are installed and configured,
then delegates to their tools.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("social_manager")

# ---------------------------------------------------------------------------
# Platform Registry
# Maps platform name -> plugin name, tool name, char limit, media support
# ---------------------------------------------------------------------------

PLATFORMS = {
    "bluesky": {
        "plugin": "bluesky",
        "post_tool": "bluesky_post",
        "char_limit": 300,
        "supports_images": True,
        "supports_video": False,
    },
    "x": {
        "plugin": "x",
        "post_tool": "x_post",
        "char_limit": 280,
        "supports_images": True,
        "supports_video": True,
    },
    "reddit": {
        "plugin": "reddit",
        "post_tool": "reddit_post",
        "char_limit": 40000,
        "supports_images": True,
        "supports_video": True,
    },
    "facebook": {
        "plugin": "facebook",
        "post_tool": "facebook_post",
        "char_limit": 63206,
        "supports_images": True,
        "supports_video": False,
    },
    "threads": {
        "plugin": "threads",
        "post_tool": "threads_post",
        "char_limit": 500,
        "supports_images": True,
        "supports_video": True,
    },
    "instagram": {
        "plugin": "instagram",
        "post_tool": "instagram_post",
        "char_limit": 2200,
        "supports_images": True,
        "supports_video": True,
    },
    "linkedin": {
        "plugin": "linkedin",
        "post_tool": "linkedin_post",
        "char_limit": 3000,
        "supports_images": True,
        "supports_video": True,
    },
    "youtube": {
        "plugin": "youtube",
        "post_tool": "youtube_upload",
        "char_limit": 5000,
        "supports_images": False,
        "supports_video": True,
    },
    "pinterest": {
        "plugin": "pinterest",
        "post_tool": "pinterest_pin",
        "char_limit": 500,
        "supports_images": True,
        "supports_video": True,
    },
    "tiktok": {
        "plugin": "tiktok",
        "post_tool": "tiktok_upload",
        "char_limit": 2200,
        "supports_images": False,
        "supports_video": True,
    },
}


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def get_social_manager_config(agent=None):
    """Load plugin configuration through A0's plugin config system."""
    try:
        from helpers import plugins
        return plugins.get_plugin_config("social_manager", agent=agent) or {}
    except Exception:
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}


def _data_dir() -> Path:
    """Get the data directory for storing schedule and state files."""
    try:
        from helpers import plugins
        plugin_dir = plugins.get_plugin_dir("social_manager")
        data_dir = Path(plugin_dir) / "data"
    except Exception:
        data_dir = Path("/a0/usr/plugins/social_manager/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_schedule_path() -> Path:
    """Path to the schedule JSON file."""
    return _data_dir() / "schedule.json"


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def _is_plugin_installed(plugin_name: str) -> bool:
    """Check if a platform plugin directory exists and has plugin.yaml."""
    search_paths = [
        Path(f"/a0/plugins/{plugin_name}/plugin.yaml"),
        Path(f"/a0/usr/plugins/{plugin_name}/plugin.yaml"),
    ]
    return any(p.exists() for p in search_paths)


def _is_plugin_enabled(plugin_name: str) -> bool:
    """Check if a platform plugin has the .toggle-1 file (enabled)."""
    search_paths = [
        Path(f"/a0/plugins/{plugin_name}/.toggle-1"),
        Path(f"/a0/usr/plugins/{plugin_name}/.toggle-1"),
    ]
    return any(p.exists() for p in search_paths)


def _has_plugin_config(plugin_name: str, agent=None) -> bool:
    """Check if a platform plugin has non-empty configuration."""
    try:
        from helpers import plugins
        config = plugins.get_plugin_config(plugin_name, agent=agent) or {}
        # A plugin is "configured" if it has at least one non-empty value
        return any(
            v for k, v in config.items()
            if k not in ("defaults", "memory", "security") and v
        )
    except Exception:
        return False


def get_available_platforms(agent=None):
    """
    Detect which platform plugins are installed, enabled, and configured.
    Returns a list of dicts with platform info and status.
    """
    results = []
    for platform_name, info in PLATFORMS.items():
        plugin_name = info["plugin"]
        installed = _is_plugin_installed(plugin_name)
        enabled = _is_plugin_enabled(plugin_name) if installed else False
        configured = _has_plugin_config(plugin_name, agent=agent) if enabled else False

        results.append({
            "platform": platform_name,
            "plugin": plugin_name,
            "post_tool": info["post_tool"],
            "char_limit": info["char_limit"],
            "supports_images": info["supports_images"],
            "supports_video": info["supports_video"],
            "installed": installed,
            "enabled": enabled,
            "configured": configured,
            "ready": installed and enabled and configured,
        })
    return results


def get_ready_platforms(agent=None):
    """Return only platforms that are fully ready (installed + enabled + configured)."""
    return [p for p in get_available_platforms(agent) if p["ready"]]


def get_platform_config(platform_name: str, agent=None) -> dict:
    """Get a specific platform plugin's config."""
    if platform_name not in PLATFORMS:
        return {}
    plugin_name = PLATFORMS[platform_name]["plugin"]
    try:
        from helpers import plugins
        return plugins.get_plugin_config(plugin_name, agent=agent) or {}
    except Exception:
        return {}


def get_platform_info(platform_name: str) -> dict:
    """Get static registry info for a platform."""
    return PLATFORMS.get(platform_name, {})


def resolve_platform_list(platforms_arg: str, agent=None) -> list:
    """
    Resolve a platforms argument into a list of ready platform dicts.
    Accepts: "all", "bluesky,x,reddit", or a single platform name.
    Returns only platforms that are ready.
    """
    ready = get_ready_platforms(agent)
    ready_names = {p["platform"] for p in ready}

    if not platforms_arg or platforms_arg.strip().lower() == "all":
        return ready

    requested = [p.strip().lower() for p in platforms_arg.split(",")]
    result = []
    for name in requested:
        if name in ready_names:
            result.append(next(p for p in ready if p["platform"] == name))
        else:
            logger.warning(
                "Platform '%s' requested but not ready (installed+enabled+configured)", name
            )
    return result
