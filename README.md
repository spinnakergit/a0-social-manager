# Social Media Manager Plugin for Agent Zero

A **meta-plugin orchestrator** that coordinates across all social media platform plugins. It does not call any external APIs directly -- instead it discovers which platform plugins are installed and configured, then delegates to their tools.

## Supported Platforms

| Platform   | Plugin Name | Post Tool        | Char Limit | Images | Video |
|------------|-------------|------------------|------------|--------|-------|
| Bluesky    | `bluesky`   | `bluesky_post`   | 300        | Yes    | No    |
| X          | `x`         | `x_post`         | 280        | Yes    | Yes   |
| Reddit     | `reddit`    | `reddit_post`    | 40,000     | Yes    | Yes   |
| Facebook   | `facebook`  | `facebook_post`  | 63,206     | Yes    | Yes   |
| Threads    | `threads`   | `threads_post`   | 500        | Yes    | Yes   |
| Instagram  | `instagram` | `instagram_post` | 2,200      | Yes    | Yes   |
| LinkedIn   | `linkedin`  | `linkedin_post`  | 3,000      | Yes    | Yes   |
| YouTube    | `youtube`   | `youtube_upload` | 5,000      | No     | Yes   |
| Pinterest  | `pinterest` | `pinterest_pin`  | 500        | Yes    | Yes   |
| TikTok     | `tiktok`    | `tiktok_upload`  | 2,200      | No     | Yes   |

## How It Works

1. **Platform Detection** -- Scans for installed, enabled, and configured platform plugins
2. **Content Adaptation** -- Automatically trims and formats content for each platform's constraints
3. **Cross-Posting** -- Delegates to each platform's native posting tool
4. **Scheduling** -- Stores posting intent for future execution
5. **Analytics Aggregation** -- Collects metrics from all connected platforms

## Tools

| Tool | Description |
|------|-------------|
| `social_manager_post` | Cross-post to multiple platforms simultaneously |
| `social_manager_status` | Check connection status across all platforms |
| `social_manager_analytics` | Aggregate analytics from all platforms |
| `social_manager_schedule` | Schedule content for future posting |
| `social_manager_adapt` | Preview content adaptation per platform |

## Quick Start

1. Install the Social Media Manager plugin
2. Install and configure one or more platform plugins (e.g., `a0-bluesky`, `a0-x`)
3. Check status: ask the agent "Check my social media platform status"
4. Post everywhere: ask "Post to all my social media: Hello world!"

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for detailed installation instructions.

## Requirements

- Agent Zero instance (Docker or local)
- One or more platform plugins installed and configured
- No additional Python dependencies (this plugin orchestrates existing plugins)

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Setup Guide](docs/SETUP.md)
- [Development Guide](docs/DEVELOPMENT.md)

## License

MIT -- see [LICENSE](LICENSE) for details.
