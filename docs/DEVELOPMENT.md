# Social Media Manager Plugin -- Development Guide

## Project Structure

```
a0-social-manager/
├── plugin.yaml              # Plugin manifest
├── default_config.yaml      # Default settings
├── initialize.py            # Dependency installer (none needed)
├── install.sh               # Deployment script
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT license
├── README.md                # Plugin overview
├── helpers/
│   ├── __init__.py
│   ├── social_manager_client.py  # Platform registry & detection
│   ├── content_adapter.py        # Content adaptation logic
│   └── sanitize.py               # Validation & formatting
├── tools/
│   ├── social_manager_post.py       # Cross-post tool
│   ├── social_manager_status.py     # Platform status tool
│   ├── social_manager_analytics.py  # Analytics aggregation tool
│   ├── social_manager_schedule.py   # Scheduling tool
│   └── social_manager_adapt.py      # Content preview tool
├── prompts/
│   ├── agent.system.tool_group.md
│   ├── agent.system.tool.social_manager_post.md
│   ├── agent.system.tool.social_manager_status.md
│   ├── agent.system.tool.social_manager_analytics.md
│   ├── agent.system.tool.social_manager_schedule.md
│   └── agent.system.tool.social_manager_adapt.md
├── api/
│   ├── social_manager_test.py       # Platform availability endpoint
│   └── social_manager_config_api.py # Configuration endpoint
├── webui/
│   ├── main.html            # Platform status dashboard
│   └── config.html          # Settings panel
├── skills/
│   ├── social-manager-publish/SKILL.md   # Publishing workflow
│   ├── social-manager-monitor/SKILL.md   # Monitoring workflow
│   └── social-manager-campaign/SKILL.md  # Campaign workflow
├── tests/
│   ├── regression_test.sh   # Automated regression suite
│   └── HUMAN_TEST_PLAN.md   # Manual verification checklist
└── docs/
    ├── README.md            # Documentation index
    ├── QUICKSTART.md        # Installation guide
    ├── SETUP.md             # Configuration reference
    └── DEVELOPMENT.md       # This file
```

## Development Setup

1. Start the dev container:
   ```bash
   docker start agent-zero-dev
   ```

2. Install the plugin:
   ```bash
   docker cp a0-social-manager/. agent-zero-dev:/a0/usr/plugins/social_manager/
   docker exec agent-zero-dev ln -sf /a0/usr/plugins/social_manager /a0/plugins/social_manager
   docker exec agent-zero-dev touch /a0/usr/plugins/social_manager/.toggle-1
   docker exec agent-zero-dev supervisorctl restart run_ui
   ```

3. Run tests:
   ```bash
   bash tests/regression_test.sh agent-zero-dev 50083
   ```

## Key Patterns

- **Tool base class:** `from helpers.tool import Tool, Response`
- **Config access:** `plugins.get_plugin_config("social_manager", agent=self.agent)`
- **CSRF:** All API handlers return `requires_csrf() -> True`
- **WebUI JS:** `globalThis.fetchApi || fetch` for CSRF-aware requests
- **WebUI HTML:** `data-sm=` attribute prefix (never bare IDs)
- **Logging:** Use `logging.getLogger("social_manager")`, never `print()`

## Adding a New Platform

1. Add entry to `PLATFORMS` dict in `helpers/social_manager_client.py`
2. Ensure the platform plugin follows standard A0 tool naming conventions
3. Update the regression test platform count assertion
4. Update README and docs

## Adding a New Tool

1. Create `tools/social_manager_<action>.py` with a Tool subclass
2. Create `prompts/agent.system.tool.social_manager_<action>.md`
3. Add import test to `tests/regression_test.sh`
4. Update `prompts/agent.system.tool_group.md`
5. Update documentation

## Code Style

- Follow existing patterns from the codebase
- Use `async/await` for all tool execute methods
- Return `Response(message=..., break_loop=False)` from tools
- Validate inputs before delegating to platform tools
- Handle platform tool failures gracefully (report per-platform, don't crash)
