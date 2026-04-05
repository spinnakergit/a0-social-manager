"""Shared validation and formatting for the Social Media Manager plugin."""

import logging

from usr.plugins.social_manager.helpers.social_manager_client import PLATFORMS

logger = logging.getLogger("social_manager")


def validate_platform_list(platforms_str: str) -> tuple:
    """
    Validate a comma-separated platform list.
    Returns (valid: bool, error_message: str, parsed_list: list).
    """
    if not platforms_str or platforms_str.strip().lower() == "all":
        return (True, "", ["all"])

    names = [p.strip().lower() for p in platforms_str.split(",")]
    invalid = [n for n in names if n and n not in PLATFORMS]

    if invalid:
        valid_names = ", ".join(sorted(PLATFORMS.keys()))
        return (
            False,
            f"Unknown platform(s): {', '.join(invalid)}. "
            f"Valid platforms: {valid_names}",
            [],
        )

    return (True, "", names)


def format_cross_post_result(results: list) -> str:
    """
    Format results from a multi-platform posting operation.

    Args:
        results: list of dicts with keys: platform, success, message

    Returns:
        Formatted string with per-platform results.
    """
    if not results:
        return "No platforms were targeted."

    lines = ["**Cross-Post Results:**", ""]
    success_count = 0
    fail_count = 0

    for r in results:
        platform = r.get("platform", "unknown")
        success = r.get("success", False)
        message = r.get("message", "")

        if success:
            success_count += 1
            lines.append(f"  [OK] {platform}: {message}")
        else:
            fail_count += 1
            lines.append(f"  [FAIL] {platform}: {message}")

    lines.append("")
    lines.append(f"**Summary:** {success_count} succeeded, {fail_count} failed")
    return "\n".join(lines)


def format_platform_status(platforms: list) -> str:
    """
    Format connection status for all platforms into a readable table.

    Args:
        platforms: list of dicts from get_available_platforms()

    Returns:
        Formatted string showing each platform's status.
    """
    if not platforms:
        return "No platforms registered."

    lines = ["**Platform Status:**", ""]
    lines.append("| Platform   | Installed | Enabled | Configured | Ready |")
    lines.append("|------------|-----------|---------|------------|-------|")

    for p in platforms:
        name = p["platform"].ljust(10)
        installed = "Yes" if p["installed"] else "No "
        enabled = "Yes" if p["enabled"] else "No "
        configured = "Yes" if p["configured"] else "No "
        ready = "Yes" if p["ready"] else "No "
        lines.append(f"| {name} | {installed}       | {enabled}     | {configured}        | {ready}   |")

    ready_count = sum(1 for p in platforms if p["ready"])
    total = len(platforms)
    lines.append("")
    lines.append(f"**{ready_count}/{total}** platforms ready.")

    return "\n".join(lines)


def format_schedule_entry(entry: dict) -> str:
    """Format a single schedule entry for display."""
    entry_id = entry.get("id", "?")
    text_preview = entry.get("text", "")[:60]
    if len(entry.get("text", "")) > 60:
        text_preview += "..."
    platforms = entry.get("platforms", "all")
    scheduled_time = entry.get("scheduled_time", "unset")
    status = entry.get("status", "pending")

    return (
        f"  [{entry_id}] {scheduled_time} | {platforms} | "
        f"{status} | {text_preview}"
    )
