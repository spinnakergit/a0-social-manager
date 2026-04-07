"""Plugin lifecycle hooks for the Social Media Manager plugin.

Called by Agent Zero's plugin system during install, uninstall, and update.
See: helpers/plugins.py -> call_plugin_hook()
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def _get_plugin_dir() -> Path:
    """Return the directory this hooks.py lives in."""
    return Path(__file__).parent.resolve()


def _get_a0_root() -> Path:
    """Detect A0 root directory."""
    if Path("/a0/plugins").is_dir():
        return Path("/a0")
    if Path("/git/agent-zero/plugins").is_dir():
        return Path("/git/agent-zero")
    return Path("/a0")


def _find_python() -> str:
    """Find the appropriate Python interpreter."""
    candidates = ["/opt/venv-a0/bin/python3", sys.executable, "python3"]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return "python3"


def install(**kwargs):
    """Post-install hook: set up data dir, deps, skills, toggle."""
    plugin_dir = _get_plugin_dir()
    a0_root = _get_a0_root()
    plugin_name = "social_manager"

    print(f"[{plugin_name}] Running post-install hook...")

    # 1. Enable plugin
    toggle = plugin_dir / ".toggle-1"
    if not toggle.exists():
        toggle.touch()
        print(f"[{plugin_name}] Created {toggle}")

    # 2. Create data directory with restrictive permissions
    data_dir = plugin_dir / "data"
    data_dir.mkdir(exist_ok=True)
    os.chmod(str(data_dir), 0o700)

    # Pre-create config.json with restrictive permissions
    config_file = plugin_dir / "config.json"
    if not config_file.exists():
        fd = os.open(str(config_file), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump({}, f)
        print(f"[{plugin_name}] Created config.json with 0o600 permissions")

    # 3. Install Python dependencies via initialize.py
    init_script = plugin_dir / "initialize.py"
    if init_script.is_file():
        python = _find_python()
        try:
            subprocess.run(
                [python, str(init_script)],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            print(f"[{plugin_name}] Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"[{plugin_name}] Warning: dependency install failed (exit code {e.returncode})")
        except subprocess.TimeoutExpired:
            print(f"[{plugin_name}] Warning: dependency install timed out")

    print(f"[{plugin_name}] Post-install hook complete")


def uninstall(**kwargs):
    """Pre-uninstall hook: clean up skills."""
    a0_root = _get_a0_root()
    plugin_name = "social_manager"

    print(f"[{plugin_name}] Running uninstall hook...")

    print(f"[{plugin_name}] Uninstall hook complete")
