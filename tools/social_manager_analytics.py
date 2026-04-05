from helpers.tool import Tool, Response


class SocialManagerAnalytics(Tool):
    """Aggregate analytics from all connected social media platforms."""

    async def execute(self, **kwargs) -> Response:
        period = self.args.get("period", "week")

        if period not in ("day", "week", "month"):
            return Response(
                message="Error: 'period' must be 'day', 'week', or 'month'.",
                break_loop=False,
            )

        from usr.plugins.social_manager.helpers.social_manager_client import (
            get_ready_platforms,
        )

        self.set_progress(f"Collecting analytics for the past {period}...")

        platforms = get_ready_platforms(agent=self.agent)
        if not platforms:
            return Response(
                message=(
                    "No platforms are currently ready. Install and configure "
                    "platform plugins to collect analytics."
                ),
                break_loop=False,
            )

        results = []
        for platform in platforms:
            name = platform["platform"]
            analytics_tool = f"{platform['plugin']}_analytics"

            try:
                tool_args = {"period": period}
                tool = self.agent.get_tool(
                    name=analytics_tool,
                    method=None,
                    args=tool_args,
                    message="",
                    loop_data=self.agent.loop_data,
                )
                tool_result = await tool.execute(**tool_args)
                message = getattr(tool_result, "message", str(tool_result))
                results.append({
                    "platform": name,
                    "success": True,
                    "data": message,
                })
            except Exception as e:
                results.append({
                    "platform": name,
                    "success": False,
                    "data": str(e),
                })

        # Format output
        lines = [f"**Cross-Platform Analytics ({period})**", ""]
        collected = 0
        for r in results:
            name = r["platform"]
            if r["success"]:
                collected += 1
                lines.append(f"### {name.title()}")
                lines.append(r["data"])
                lines.append("")
            else:
                lines.append(f"### {name.title()}")
                lines.append(f"  Analytics unavailable: {r['data']}")
                lines.append("")

        lines.append(
            f"**Collected from {collected}/{len(platforms)} platforms.**"
        )

        return Response(message="\n".join(lines), break_loop=False)
