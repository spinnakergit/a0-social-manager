# Cross-Platform Campaign Workflow

Plan and execute a coordinated content campaign across multiple social media platforms.

## Steps

1. **Gather requirements** from the user: campaign theme, target platforms, number of posts, timeframe.
2. **Check platform status** using `social_manager_status` to confirm which platforms are available.
3. **Draft content** for each post in the campaign. Use `social_manager_adapt` to preview how each piece adapts across platforms.
4. **Schedule posts** using `social_manager_schedule` with specific times for each post. Space them appropriately (avoid posting everything at once).
5. **Review the schedule** using `social_manager_schedule` with `action: "list"` so the user can approve.
6. Adjust or remove entries with `social_manager_schedule` `action: "remove"` if the user wants changes.
7. **Execute immediate posts** if the user wants some content published now using `social_manager_post`.
8. Report the full campaign plan and any scheduled items.

## Tips
- Vary content slightly across platforms rather than posting identical text everywhere.
- Consider platform-specific best practices (hashtags on Instagram/X, longer form on LinkedIn/Reddit).
- Note that scheduled posts require an external cron/scheduler to actually fire at the planned time.
