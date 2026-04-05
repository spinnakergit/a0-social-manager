## social_manager_post
Cross-post content to multiple social media platforms simultaneously. Content is automatically adapted to each platform's character limits and format constraints. Only posts to platforms that are installed, enabled, and configured.

**How it works:**
1. Validates the requested platforms against the known registry.
2. Filters to only platforms that are ready (installed + enabled + configured).
3. If `adapt_content` is true (default), trims text to each platform's character limit with an ellipsis.
4. Delegates to each platform's own post tool (e.g., `bluesky_post`, `x_post`, `youtube_upload`).
5. For video posts, handles platform-specific upload workflows (e.g., Instagram Reels, X two-step media upload, YouTube native upload).
6. Dedup guard: skips platforms where identical content was already posted within 5 minutes (prevents retry duplicates).
7. Returns per-platform success/failure results.

**Arguments:**
- **text** (string, required): The content/caption to post
- **platforms** (string, optional): Comma-separated list of target platforms, or "all" (default: "all")
- **video_path** (string, optional): Path to a video file for native upload. Automatically routes to each platform's video workflow (YouTube upload, Instagram Reel, X media upload). Platforms without video support receive text-only posts.
- **image_path** (string, optional): Path to an image file to attach. If a video file is passed here, it is auto-detected and treated as video_path.
- **title** (string, optional): Title for the video (used by YouTube). Defaults to first 100 characters of text.
- **adapt_content** (bool, optional): Whether to auto-adapt content per platform (default: true)

**Video support by platform:**
| Platform | Video | How |
|----------|-------|-----|
| YouTube | Yes | Native upload via `youtube_upload` |
| Instagram | Yes | Reel via `instagram_post` (auto-hosts local files) |
| X | Yes | Two-step: upload via `x_media`, then `x_post` with media_ids |
| Facebook | No | Text-only post (video upload not yet supported) |
| Bluesky | No | Text-only post |

**Supported platforms:** bluesky, x, reddit, facebook, threads, instagram, linkedin, youtube, pinterest, tiktok

~~~json
{"text": "Exciting news! Our project just launched.", "platforms": "bluesky,x,linkedin"}
~~~
~~~json
{"text": "Texas bluebonnets in golden hour", "video_path": "/a0/files/reel.mp4", "title": "Texas Bluebonnets — Golden Hour", "platforms": "youtube,instagram,x"}
~~~
~~~json
{"text": "New blog post with photo", "platforms": "bluesky,threads,instagram", "image_path": "/tmp/photo.jpg"}
~~~

**Notes:**
- If no platforms are ready, returns an error prompting the user to install and configure platform plugins first.
- Platforms that fail (auth expired, network error) are reported individually without stopping other platforms.
- Duplicate posts are automatically prevented: if the same content was posted to a platform within the last 5 minutes, it is skipped.
- Use `social_manager_adapt` first to preview how content will look on each platform.
