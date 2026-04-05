from helpers.tool import Tool, Response


class SocialManagerAdapt(Tool):
    """Preview how content will be adapted for each platform (does NOT post)."""

    async def execute(self, **kwargs) -> Response:
        text = self.args.get("text", "")
        platforms_arg = self.args.get("platforms", "all")

        if not text:
            return Response(
                message="Error: 'text' is required.",
                break_loop=False,
            )

        from usr.plugins.social_manager.helpers.social_manager_client import (
            get_social_manager_config,
            resolve_platform_list,
            get_available_platforms,
            PLATFORMS,
        )
        from usr.plugins.social_manager.helpers.sanitize import validate_platform_list
        from usr.plugins.social_manager.helpers.content_adapter import preview_adaptations

        config = get_social_manager_config(self.agent)

        valid, error, _ = validate_platform_list(platforms_arg)
        if not valid:
            return Response(message=f"Error: {error}", break_loop=False)

        # For preview, show all requested platforms even if not ready
        if not platforms_arg or platforms_arg.strip().lower() == "all":
            targets = get_available_platforms(agent=self.agent)
        else:
            names = [p.strip().lower() for p in platforms_arg.split(",")]
            targets = []
            for name in names:
                if name in PLATFORMS:
                    info = PLATFORMS[name]
                    targets.append({
                        "platform": name,
                        "char_limit": info["char_limit"],
                        "supports_images": info["supports_images"],
                        "supports_video": info["supports_video"],
                    })

        if not targets:
            return Response(
                message="No platforms specified.",
                break_loop=False,
            )

        prefs = config.get("content_preferences", {})
        add_hashtags = prefs.get("add_hashtags", False)
        max_hashtags = prefs.get("max_hashtags", 5)

        previews = preview_adaptations(
            text, targets,
            add_hashtags=add_hashtags,
            max_hashtags=max_hashtags,
        )

        # Format output
        lines = ["**Content Adaptation Preview**", ""]
        lines.append(f"Source text ({len(text)} chars): {text[:100]}{'...' if len(text) > 100 else ''}")
        lines.append("")

        for p in previews:
            status = "TRUNCATED" if p["truncated"] else "OK"
            lines.append(
                f"### {p['platform'].title()} "
                f"[{p['adapted_length']}/{p['char_limit']} chars] ({status})"
            )
            lines.append(f"  {p['adapted_text']}")
            if p["warnings"]:
                for w in p["warnings"]:
                    lines.append(f"  Warning: {w}")
            lines.append("")

        return Response(message="\n".join(lines), break_loop=False)
