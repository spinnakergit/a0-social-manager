## social_manager_schedule
Schedule content for future posting across social media platforms. Manages a local schedule file where posts can be added, listed, and removed. Actual timed posting requires an external scheduler or cron trigger.

**How it works:**
1. **add**: Stores a new schedule entry with text, target platforms, and an ISO 8601 datetime.
2. **list**: Shows all pending scheduled entries with their IDs, times, platforms, and text previews.
3. **remove**: Deletes a scheduled entry by its ID.
4. Schedule data is persisted in the plugin's `data/schedule.json` file.

**Arguments:**
- **action** (string, optional): "add" (default), "list", or "remove"
- **text** (string, required for add): The content to schedule
- **platforms** (string, optional): Comma-separated platforms or "all" (default: "all")
- **scheduled_time** (string, required for add): ISO 8601 datetime, e.g. "2026-03-20T14:00:00Z"
- **image_path** (string, optional): Path to an image to attach when the post is eventually published
- **id** (string, required for remove): ID of the schedule entry to remove

~~~json
{"action": "add", "text": "Weekly update!", "platforms": "bluesky,x", "scheduled_time": "2026-03-20T14:00:00Z"}
~~~
~~~json
{"action": "list"}
~~~
~~~json
{"action": "remove", "id": "3"}
~~~

**Notes:**
- This tool stores scheduling intent locally. It does not automatically fire posts at the scheduled time. An external mechanism (agent cron, webhook, manual trigger) is needed to execute scheduled posts.
- Schedule entries are assigned auto-incrementing integer IDs.
- The timezone in the plugin config affects display formatting only; `scheduled_time` should always be in ISO 8601 format (preferably UTC).
