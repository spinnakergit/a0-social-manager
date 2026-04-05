import hashlib
import json
import os
import time
from pathlib import Path

from helpers.tool import Tool, Response


def _dedup_path() -> Path:
    """Path to the dedup tracking file."""
    candidates = [
        Path(__file__).parent.parent / "data" / "recent_posts.json",
        Path("/a0/usr/plugins/social_manager/data/recent_posts.json"),
    ]
    for p in candidates:
        if p.parent.exists():
            return p
    candidates[0].parent.mkdir(parents=True, exist_ok=True)
    return candidates[0]


def _content_hash(text: str, platform: str, video_path: str = "", image_path: str = "") -> str:
    """Generate a hash for dedup based on content + platform."""
    key = f"{platform}:{text}:{video_path}:{image_path}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _check_dedup(text: str, platform: str, video_path: str = "", image_path: str = "", window_seconds: int = 300) -> bool:
    """Return True if this content was already posted to this platform recently."""
    h = _content_hash(text, platform, video_path, image_path)
    path = _dedup_path()
    try:
        with open(path) as f:
            recent = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        recent = {}
    cutoff = time.time() - window_seconds
    if h in recent and recent[h] > cutoff:
        return True
    return False


def _record_post(text: str, platform: str, video_path: str = "", image_path: str = ""):
    """Record a successful post for dedup tracking."""
    h = _content_hash(text, platform, video_path, image_path)
    path = _dedup_path()
    try:
        with open(path) as f:
            recent = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        recent = {}
    # Prune entries older than 1 hour
    cutoff = time.time() - 3600
    recent = {k: v for k, v in recent.items() if v > cutoff}
    recent[h] = time.time()
    tmp = path.with_suffix(".tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(recent, f)
    os.replace(str(tmp), str(path))


def _is_video_file(file_path: str) -> bool:
    """Check if a file path looks like a video."""
    if not file_path:
        return False
    ext = Path(file_path).suffix.lower()
    return ext in (".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v")


class SocialManagerPost(Tool):
    """Cross-post content to multiple social media platforms simultaneously."""

    async def execute(self, **kwargs) -> Response:
        text = self.args.get("text", "")
        platforms_arg = self.args.get("platforms", "all")
        image_path = self.args.get("image_path", "")
        video_path = self.args.get("video_path", "")
        title = self.args.get("title", "")
        adapt = self.args.get("adapt_content", True)

        # Auto-detect: if image_path is actually a video, treat as video_path
        if image_path and not video_path and _is_video_file(image_path):
            video_path = image_path
            image_path = ""

        if not text:
            return Response(
                message="Error: 'text' is required.",
                break_loop=False,
            )

        from usr.plugins.social_manager.helpers.social_manager_client import (
            get_social_manager_config,
            resolve_platform_list,
        )
        from usr.plugins.social_manager.helpers.sanitize import (
            validate_platform_list,
            format_cross_post_result,
        )
        from usr.plugins.social_manager.helpers.content_adapter import (
            adapt_for_platform,
        )

        config = get_social_manager_config(self.agent)

        # Validate platform names
        valid, error, _ = validate_platform_list(platforms_arg)
        if not valid:
            return Response(message=f"Error: {error}", break_loop=False)

        # Resolve to ready platforms
        targets = resolve_platform_list(platforms_arg, agent=self.agent)
        if not targets:
            return Response(
                message=(
                    "Error: No ready platforms found. Install and configure "
                    "platform plugins first, then try again."
                ),
                break_loop=False,
            )

        # Determine content adaptation settings
        should_adapt = adapt if isinstance(adapt, bool) else config.get("adapt_content", True)
        prefs = config.get("content_preferences", {})
        add_hashtags = prefs.get("add_hashtags", False)
        max_hashtags = prefs.get("max_hashtags", 5)

        self.set_progress(
            f"Cross-posting to {len(targets)} platform(s)..."
        )

        results = []
        for platform in targets:
            name = platform["platform"]
            tool_name = platform["post_tool"]
            char_limit = platform["char_limit"]

            # Adapt content if requested
            post_text = text
            if should_adapt:
                post_text = adapt_for_platform(
                    text, name, char_limit,
                    add_hashtags=add_hashtags,
                    max_hashtags=max_hashtags,
                )

            # Dedup check — skip if already posted recently
            if _check_dedup(post_text, name, video_path, image_path):
                results.append({
                    "platform": name,
                    "success": False,
                    "message": "Skipped: duplicate (already posted within 5 minutes)",
                })
                continue

            try:
                tool_args = self._build_platform_args(
                    name, tool_name, post_text, image_path, video_path, title, platform
                )

                # X video requires two-step: upload media first, then post
                if name == "x" and video_path and platform.get("supports_video"):
                    tool_result = await self._post_x_with_video(
                        post_text, video_path, tool_args
                    )
                else:
                    tool = self.agent.get_tool(
                        name=tool_name,
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
                    "message": message,
                })
                # Record for dedup
                _record_post(post_text, name, video_path, image_path)

            except Exception as e:
                results.append({
                    "platform": name,
                    "success": False,
                    "message": str(e),
                })

        return Response(
            message=format_cross_post_result(results),
            break_loop=False,
        )

    def _build_platform_args(
        self, name, tool_name, post_text, image_path, video_path, title, platform
    ) -> dict:
        """Build platform-specific tool arguments."""

        # --- VIDEO ---
        if video_path and platform.get("supports_video"):
            if name == "youtube":
                return {
                    "file_path": video_path,
                    "title": title or post_text[:100],
                    "description": post_text,
                    "privacy_status": "public",
                }
            elif name == "instagram":
                return {
                    "action": "reel",
                    "video_url": video_path,
                    "caption": post_text,
                }
            elif name == "x":
                # Handled separately in _post_x_with_video
                return {"text": post_text}
            else:
                # Generic: try video_path arg
                return {"text": post_text, "video_path": video_path}

        # --- IMAGE ---
        if image_path and platform.get("supports_images"):
            if name == "instagram":
                return {
                    "action": "photo",
                    "image_url": image_path,
                    "caption": post_text,
                }
            else:
                return {"text": post_text, "image_path": image_path}

        # --- TEXT ONLY ---
        if name == "facebook":
            return {"action": "create", "message": post_text}
        return {"text": post_text}

    async def _post_x_with_video(self, text, video_path, base_args) -> Response:
        """Two-step X post: upload media via x_media, then post with media_ids."""
        # Step 1: Upload video
        media_args = {"action": "upload", "file_path": video_path}
        media_tool = self.agent.get_tool(
            name="x_media",
            method=None,
            args=media_args,
            message="",
            loop_data=self.agent.loop_data,
        )
        media_result = await media_tool.execute(**media_args)
        media_msg = getattr(media_result, "message", str(media_result))

        # Extract media_id from result
        media_id = ""
        for line in media_msg.split("\n"):
            if "media_id" in line.lower() or "id:" in line.lower():
                # Try to extract numeric ID
                import re
                ids = re.findall(r'\d{10,}', line)
                if ids:
                    media_id = ids[0]
                    break

        if not media_id:
            return Response(
                message=f"X media upload succeeded but could not extract media_id: {media_msg}",
                break_loop=False,
            )

        # Step 2: Post with media_ids
        post_args = {"text": text, "media_ids": media_id}
        post_tool = self.agent.get_tool(
            name="x_post",
            method=None,
            args=post_args,
            message="",
            loop_data=self.agent.loop_data,
        )
        return await post_tool.execute(**post_args)
