# Social Media Manager Plugin -- Setup Guide

## Overview

The Social Media Manager is a **meta-plugin** -- it does not connect to any external API on its own. Instead, it orchestrates content across whichever platform plugins you have installed and configured in Agent Zero. There are no separate API credentials or tokens needed for this plugin.

## Prerequisites

Install at least one platform plugin before using the Social Media Manager. Without platform plugins, the Social Media Manager has nothing to orchestrate.

## Supported Platforms

| Platform | Plugin Name | Char Limit | Images | Video |
|----------|-------------|------------|--------|-------|
| Bluesky | `bluesky` | 300 | Yes | No |
| X (Twitter) | `x` | 280 | Yes | Yes |
| Reddit | `reddit` | 40,000 | Yes | Yes |
| Facebook | `facebook` | 63,206 | Yes | Yes |
| Threads | `threads` | 500 | Yes | Yes |
| Instagram | `instagram` | 2,200 | Yes | Yes |
| LinkedIn | `linkedin` | 3,000 | Yes | Yes |
| YouTube | `youtube` | 5,000 | No | Yes |
| Pinterest | `pinterest` | 500 | Yes | Yes |
| TikTok | `tiktok` | 2,200 | No | Yes |

## Installation

### Step 1: Install platform plugins

Install and configure the platform plugins you want to use. Each has its own setup process with API credentials. For example:

```bash
# Inside the Agent Zero container
cp -r a0-bluesky/ /a0/usr/plugins/bluesky/
ln -sf /a0/usr/plugins/bluesky /a0/plugins/bluesky
touch /a0/usr/plugins/bluesky/.toggle-1
```

Then configure each platform plugin through its own WebUI settings page.

### Step 2: Install the Social Media Manager

```bash
# From inside the Agent Zero container
cp -r a0-social-manager/ /a0/usr/plugins/social_manager/
ln -sf /a0/usr/plugins/social_manager /a0/plugins/social_manager
touch /a0/usr/plugins/social_manager/.toggle-1
```

Or use the install script:

```bash
cd /tmp/a0-social-manager && ./install.sh
```

### Step 3: Restart the UI

```bash
supervisorctl restart run_ui
```

### Step 4: Verify

Open Agent Zero WebUI > Settings > External Services > Social Media Manager. The dashboard should show all 10 supported platforms with their current status.

## Configuration

The Social Media Manager's configuration is optional and controls default behavior:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default_platforms` | list | `[]` (all) | Platforms to target by default |
| `adapt_content` | bool | `true` | Auto-trim content per platform limits |
| `content_preferences.add_hashtags` | bool | `true` | Normalize hashtag formatting |
| `content_preferences.max_hashtags` | int | `5` | Maximum hashtags to keep |
| `content_preferences.include_platform_handles` | bool | `false` | Include platform-specific @handles |
| `schedule.timezone` | string | `"UTC"` | Display timezone for scheduled posts |

### Setting via WebUI

1. Navigate to Settings > External Services > Social Media Manager
2. Click the config tab
3. Adjust settings and click "Save Settings"

### Setting via API

```bash
curl -X POST http://localhost/api/plugins/social_manager/social_manager_config_api \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: <token>" \
  -d '{"action":"set","config":{"default_platforms":["bluesky","x"],"adapt_content":true}}'
```

## How Platform Detection Works

The Social Media Manager checks three conditions for each platform:

1. **Installed**: Does `/a0/plugins/<name>/plugin.yaml` or `/a0/usr/plugins/<name>/plugin.yaml` exist?
2. **Enabled**: Does the `.toggle-1` file exist in the plugin directory?
3. **Configured**: Does the plugin have at least one non-empty config value?

A platform is "ready" only when all three are true. Use the `social_manager_status` tool or the WebUI dashboard to check.

## Content Adaptation Rules

When cross-posting, content is adapted per platform:

- **Short-limit platforms** (X: 280, Bluesky: 300, Threads: 500, Pinterest: 500): Long text is trimmed with an ellipsis at the character boundary.
- **Medium-limit platforms** (Instagram: 2,200, TikTok: 2,200, LinkedIn: 3,000): Most posts fit without trimming.
- **Long-limit platforms** (YouTube: 5,000, Reddit: 40,000, Facebook: 63,206): Full text is always preserved.
- **Image support**: Images are only attached to platforms that support them. YouTube and TikTok are video-only.
- **Hashtag normalization**: Optionally caps the number of hashtags to the configured maximum.

Use `social_manager_adapt` to preview how content will look on each platform before posting.

## Enabling / Disabling Platforms

- **Enable a platform**: Install its plugin, create `.toggle-1`, and configure its credentials.
- **Disable a platform**: Remove `.toggle-1` from the platform plugin directory, or uninstall the plugin entirely.
- **Selective posting**: Use the `platforms` argument in `social_manager_post` to target specific platforms per post (e.g., `platforms="bluesky,linkedin"`).

## Scheduling

Scheduled posts are stored in `data/schedule.json`. The Social Media Manager stores scheduling **intent** only. Actual timed posting requires an external mechanism (cron job, scheduler agent, manual trigger) that reads the schedule file and invokes the `social_manager_post` tool.

## Data Storage

| File | Purpose |
|------|---------|
| `config.json` | Plugin settings (auto-created on first save) |
| `default_config.yaml` | Default values when no config.json exists |
| `data/schedule.json` | Scheduled post entries |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Platform shows "Not Installed" | Install the platform plugin first |
| Platform shows "Disabled" | Create `.toggle-1` in the platform plugin directory |
| Platform shows "Not Configured" | Set up API credentials in the platform plugin's settings |
| Cross-post fails for one platform | Check that platform's individual plugin -- credentials may have expired |
| Scheduled posts don't fire | Scheduling is local storage only; an external scheduler is needed |
| Dashboard shows 0 platforms ready | Install, enable, and configure at least one platform plugin |
