import json
import logging
import os
import time
from pathlib import Path

from helpers.tool import Tool, Response

logger = logging.getLogger("social_manager")


class SocialManagerSchedule(Tool):
    """Schedule content for future posting across platforms."""

    async def execute(self, **kwargs) -> Response:
        action = self.args.get("action", "add")
        text = self.args.get("text", "")
        platforms_arg = self.args.get("platforms", "all")
        scheduled_time = self.args.get("scheduled_time", "")
        image_path = self.args.get("image_path", "")
        entry_id = self.args.get("id", "")

        from usr.plugins.social_manager.helpers.social_manager_client import (
            get_schedule_path,
        )
        from usr.plugins.social_manager.helpers.sanitize import (
            validate_platform_list,
            format_schedule_entry,
        )

        schedule_path = get_schedule_path()

        if action == "list":
            return self._list_schedule(schedule_path, format_schedule_entry)

        if action == "remove":
            if not entry_id:
                return Response(
                    message="Error: 'id' is required for remove action.",
                    break_loop=False,
                )
            return self._remove_entry(schedule_path, entry_id)

        # Default: add
        if not text:
            return Response(
                message="Error: 'text' is required to schedule a post.",
                break_loop=False,
            )

        if not scheduled_time:
            return Response(
                message=(
                    "Error: 'scheduled_time' is required. "
                    "Use ISO 8601 format, e.g. '2026-03-20T14:00:00Z'."
                ),
                break_loop=False,
            )

        valid, error, _ = validate_platform_list(platforms_arg)
        if not valid:
            return Response(message=f"Error: {error}", break_loop=False)

        # Load existing schedule
        schedule = self._load_schedule(schedule_path)

        # Generate a simple incremental ID
        max_id = max((e.get("id", 0) for e in schedule), default=0)
        new_id = max_id + 1

        entry = {
            "id": new_id,
            "text": text,
            "platforms": platforms_arg,
            "scheduled_time": scheduled_time,
            "image_path": image_path,
            "status": "pending",
            "created_at": int(time.time()),
        }

        schedule.append(entry)
        self._save_schedule(schedule_path, schedule)

        return Response(
            message=(
                f"Scheduled post #{new_id} for {scheduled_time} "
                f"on platforms: {platforms_arg}.\n"
                f"Note: Actual posting requires a scheduler/cron job. "
                f"This stores the intent for future execution."
            ),
            break_loop=False,
        )

    def _load_schedule(self, path: Path) -> list:
        """Load the schedule from JSON file."""
        try:
            with open(path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_schedule(self, path: Path, schedule: list):
        """Atomic write schedule to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(schedule, f, indent=2)
        except Exception:
            os.unlink(str(tmp))
            raise
        os.replace(str(tmp), str(path))

    def _list_schedule(self, path: Path, formatter) -> Response:
        """List all scheduled entries."""
        schedule = self._load_schedule(path)
        if not schedule:
            return Response(
                message="No scheduled posts.",
                break_loop=False,
            )

        lines = [f"**Scheduled Posts ({len(schedule)}):**", ""]
        for entry in schedule:
            lines.append(formatter(entry))

        return Response(message="\n".join(lines), break_loop=False)

    def _remove_entry(self, path: Path, entry_id: str) -> Response:
        """Remove a schedule entry by ID."""
        schedule = self._load_schedule(path)
        try:
            target_id = int(entry_id)
        except (ValueError, TypeError):
            return Response(
                message=f"Error: Invalid ID '{entry_id}'.",
                break_loop=False,
            )

        original_len = len(schedule)
        schedule = [e for e in schedule if e.get("id") != target_id]

        if len(schedule) == original_len:
            return Response(
                message=f"Error: No entry with ID {target_id} found.",
                break_loop=False,
            )

        self._save_schedule(path, schedule)
        return Response(
            message=f"Removed scheduled post #{target_id}.",
            break_loop=False,
        )
