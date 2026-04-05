"""API endpoint: Check which social media platforms are available.
URL: POST /api/plugins/social_manager/social_manager_test
"""
from helpers.api import ApiHandler, Request, Response


class SocialManagerTest(ApiHandler):

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["GET", "POST"]

    @classmethod
    def requires_csrf(cls) -> bool:
        return True

    async def process(self, input: dict, request: Request) -> dict | Response:
        try:
            from usr.plugins.social_manager.helpers.social_manager_client import (
                get_available_platforms,
            )

            platforms = get_available_platforms()
            ready = [p for p in platforms if p["ready"]]
            installed = [p for p in platforms if p["installed"]]

            platform_status = []
            for p in platforms:
                platform_status.append({
                    "platform": p["platform"],
                    "installed": p["installed"],
                    "enabled": p["enabled"],
                    "configured": p["configured"],
                    "ready": p["ready"],
                })

            return {
                "ok": True,
                "total_platforms": len(platforms),
                "installed_count": len(installed),
                "ready_count": len(ready),
                "platforms": platform_status,
            }
        except Exception as e:
            return {"ok": False, "error": f"Platform detection failed: {type(e).__name__}"}
