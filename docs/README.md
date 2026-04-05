# Social Media Manager Plugin Documentation

## Overview

The Social Media Manager is a **meta-plugin orchestrator** for Agent Zero. It coordinates across all installed social media platform plugins to provide unified cross-platform social media management.

This plugin does **not** call any external APIs directly. It discovers which platform plugins are installed and configured, adapts content to each platform's constraints, and delegates posting/reading to the individual platform plugin tools.

## Contents

- [Quick Start](QUICKSTART.md) -- Installation and first-use guide
- [Setup](SETUP.md) -- Detailed configuration reference
- [Development](DEVELOPMENT.md) -- Contributing and development setup

## Architecture

```
Social Media Manager (orchestrator)
    |
    +-- Platform Detection (scan installed plugins)
    +-- Content Adapter (trim, format, split for each platform)
    +-- Cross-Post Router (delegate to platform tools)
    +-- Schedule Manager (local JSON storage)
    +-- Analytics Aggregator (collect from platform tools)
    |
    +-- bluesky plugin --> Bluesky AT Protocol
    +-- x plugin ---------> X/Twitter API
    +-- reddit plugin -----> Reddit API
    +-- facebook plugin ---> Facebook Graph API
    +-- threads plugin ----> Threads API
    +-- instagram plugin --> Instagram Graph API
    +-- linkedin plugin ---> LinkedIn API
    +-- youtube plugin ----> YouTube Data API
    +-- pinterest plugin --> Pinterest API
    +-- tiktok plugin -----> TikTok API
```

## Tools

| Tool | Description |
|------|-------------|
| `social_manager_post` | Cross-post to multiple platforms simultaneously |
| `social_manager_status` | Check which platforms are installed, enabled, and configured |
| `social_manager_analytics` | Aggregate analytics from all connected platforms |
| `social_manager_schedule` | Schedule content for future posting (local storage) |
| `social_manager_adapt` | Preview content adaptation for each platform |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plugins/social_manager/social_manager_test` | GET/POST | Check platform availability |
| `/api/plugins/social_manager/social_manager_config_api` | GET/POST | Read/write plugin config |

## Skills

| Skill | Description |
|-------|-------------|
| `social-manager-publish` | Cross-platform publishing workflow |
| `social-manager-monitor` | Platform monitoring and health checks |
| `social-manager-campaign` | Plan and execute cross-platform campaigns |
