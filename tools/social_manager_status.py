from helpers.tool import Tool, Response


class SocialManagerStatus(Tool):
    """Check connection status across all social media platforms."""

    async def execute(self, **kwargs) -> Response:
        platform_filter = self.args.get("platform", "")

        from usr.plugins.social_manager.helpers.social_manager_client import (
            get_available_platforms,
            PLATFORMS,
        )
        from usr.plugins.social_manager.helpers.sanitize import format_platform_status

        self.set_progress("Checking platform status...")

        all_platforms = get_available_platforms(agent=self.agent)

        # Optionally filter to a single platform
        if platform_filter:
            name = platform_filter.strip().lower()
            if name not in PLATFORMS:
                valid = ", ".join(sorted(PLATFORMS.keys()))
                return Response(
                    message=f"Error: Unknown platform '{name}'. Valid: {valid}",
                    break_loop=False,
                )
            all_platforms = [p for p in all_platforms if p["platform"] == name]

        return Response(
            message=format_platform_status(all_platforms),
            break_loop=False,
        )
