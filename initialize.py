"""One-time setup script for the Social Media Manager plugin.

This is a META-PLUGIN orchestrator — it has no external dependencies of its own.
All API calls are delegated to the individual platform plugins.

Called by the Init button in Agent Zero's Plugin List UI.
Must define main() returning 0 on success, non-zero on failure."""

import logging
import sys
from pathlib import Path

logger = logging.getLogger("social_manager_init")


def main():
    # No external dependencies needed — this plugin orchestrates other plugins.
    # Ensure the data directory exists for schedule storage.
    data_dirs = [
        Path(__file__).parent / "data",
        Path("/a0/usr/plugins/social_manager/data"),
    ]
    for d in data_dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            logger.info(f"Data directory ready: {d}")
        except Exception:
            pass

    logger.info("Social Media Manager plugin initialized (no external deps required).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
