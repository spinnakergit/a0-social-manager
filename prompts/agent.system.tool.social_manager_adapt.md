## social_manager_adapt
Preview how content will be adapted for each platform's constraints without posting. Shows character counts, truncation warnings, and platform-specific formatting so you can refine content before committing to a cross-post.

**How it works:**
1. Takes the input text and the list of target platforms.
2. For each platform, applies the character limit (trimming with ellipsis if needed).
3. Reports original length, adapted length, whether truncation occurred, and any warnings.
4. Warnings include: content truncated, platform does not support images, platform does not support video.

**Arguments:**
- **text** (string, required): The content to preview
- **platforms** (string, optional): Comma-separated platforms or "all" (default: "all")

**Platform character limits:**
- X: 280 | Bluesky: 300 | Threads: 500 | Pinterest: 500
- Instagram: 2,200 | TikTok: 2,200 | LinkedIn: 3,000
- YouTube: 5,000 | Reddit: 40,000 | Facebook: 63,206

~~~json
{"text": "This is a long announcement with details about our product launch and roadmap for the coming quarter.", "platforms": "all"}
~~~
~~~json
{"text": "Short update", "platforms": "bluesky,x,threads"}
~~~

**Notes:**
- Use this before `social_manager_post` to catch truncation issues early.
- If a 300+ character post will be truncated on X (280 limit) and Bluesky (300 limit), consider shortening it or writing platform-specific versions.
- Truncation adds an ellipsis character, so the effective content space is `limit - 1` characters.
