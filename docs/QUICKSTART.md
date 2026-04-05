# Social Media Manager Plugin -- Quick Start

## Prerequisites

- Agent Zero instance (Docker or local)
- One or more social media platform plugins installed and configured

Supported platform plugins: `a0-bluesky`, `a0-x`, `a0-reddit`, `a0-facebook`, `a0-threads`, `a0-instagram`, `a0-linkedin`, `a0-youtube`, `a0-pinterest`, `a0-tiktok`

## Installation

```bash
# From inside the Agent Zero container:
cd /tmp
# Copy plugin files, then:
./install.sh

# Or manually:
cp -r a0-social-manager/ /a0/usr/plugins/social_manager/
ln -sf /a0/usr/plugins/social_manager /a0/plugins/social_manager
touch /a0/usr/plugins/social_manager/.toggle-1
```

## Configuration

1. Open Agent Zero WebUI
2. Go to Settings > External Services > Social Media Manager
3. Optionally set default platforms (leave empty for all available)
4. Configure content adaptation preferences
5. Click "Save Settings"

## First Use

Check which platforms are connected:
> "Check my social media platform status"

Preview how content adapts to different platforms:
> "Preview how this text would look on all platforms: 'Hello from Agent Zero!'"

Post to all connected platforms:
> "Post to all my social media: 'Hello from Agent Zero Social Media Manager!'"

Schedule a future post:
> "Schedule a post for 2026-03-20 at 2pm UTC on Bluesky and X: 'Coming soon!'"

## No External Dependencies

This plugin has no external Python dependencies. It orchestrates the individual platform plugins which each manage their own API connections and authentication.
