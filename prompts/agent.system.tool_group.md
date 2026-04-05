## Social Media Manager — Cross-Platform Orchestrator

You have access to **Social Media Manager** tools for cross-platform social media orchestration. This is a **meta-plugin**: it does not call external APIs directly. Instead, it detects which platform plugins are installed and configured on this Agent Zero instance and delegates to each platform's own tools.

### Supported Platforms

The Social Media Manager can coordinate across these platform plugins when they are installed, enabled, and configured:

| Platform | Plugin | Char Limit | Image | Video |
|----------|--------|------------|-------|-------|
| Bluesky | `bluesky` | 300 | Yes | No |
| X (Twitter) | `x` | 280 | Yes | Yes |
| Reddit | `reddit` | 40,000 | Yes | Yes |
| Facebook | `facebook` | 63,206 | Yes | No |
| Threads | `threads` | 500 | Yes | Yes |
| Instagram | `instagram` | 2,200 | Yes | Yes |
| LinkedIn | `linkedin` | 3,000 | Yes | Yes |
| YouTube | `youtube` | 5,000 | No | Yes |
| Pinterest | `pinterest` | 500 | Yes | Yes |
| TikTok | `tiktok` | 2,200 | No | Yes |

### Available Tools

- `social_manager_status` — Check which platforms are installed, enabled, configured, and ready
- `social_manager_post` — Cross-post content (text, images, or video) to multiple platforms simultaneously with auto-adaptation and native video uploads
- `social_manager_adapt` — Preview how content will look on each platform before posting
- `social_manager_schedule` — Schedule content for future posting across platforms
- `social_manager_analytics` — Aggregate analytics from all connected platforms

### Best Practices

- **Always check status first**: Use `social_manager_status` to see which platforms are available before posting.
- **Preview before posting**: Use `social_manager_adapt` to see how content will be truncated or formatted for each platform's character limits.
- **Content adaptation is automatic**: When cross-posting, text is trimmed to each platform's limit with an ellipsis. Short-limit platforms (X: 280, Bluesky: 300) will truncate long posts while long-limit platforms (Reddit: 40,000, Facebook: 63,206) keep the full text.
- **Platform plugins must be set up separately**: Each platform plugin has its own credentials and configuration. The Social Media Manager only orchestrates — it does not handle authentication.
- **Scheduling is local**: Scheduled posts are stored locally. Actual timed posting requires an external trigger (cron, scheduler agent, etc.).
