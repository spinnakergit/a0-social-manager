# Human Test Plan: Social Media Manager

> **Plugin:** `social_manager`
> **Version:** 1.0.0
> **Type:** Meta-plugin orchestrator (cross-platform social media management)
> **Prerequisite:** `regression_test.sh` passed 100%
> **Estimated Time:** 30-45 minutes

---

## How to Use This Plan

1. Work through each phase in order — phases are gated (Phase 2 requires Phase 1 pass, etc.)
2. For each test, perform the **Action**, check against **Expected**, tell Claude "Pass" or "Fail"
3. Claude will record results in `HUMAN_TEST_RESULTS.md` as you go
4. If any test fails: stop, troubleshoot with Claude, fix, then continue

**Start by telling Claude:** "Start human verification for social_manager"

---

## Phase 0: Prerequisites & Environment

Before starting, confirm each item:

- [ ] **Container running:** `docker ps | grep <container-name>`
- [ ] **WebUI accessible:** Open `http://localhost:<port>` in browser
- [ ] **Plugin deployed:** `docker exec <container> ls /a0/usr/plugins/social_manager/plugin.yaml`
- [ ] **Plugin enabled:** `docker exec <container> ls /a0/usr/plugins/social_manager/.toggle-1`
- [ ] **Symlink exists:** `docker exec <container> ls -la /a0/plugins/social_manager`
- [ ] **Platform plugin installed:** At least one platform plugin installed and configured (e.g., Bluesky)
- [ ] **Platform plugin ready:** The platform plugin passes its own "Test Connection" check
- [ ] **Regression passed:** `bash regression_test.sh <container> <port>` shows 100% pass

**Record your environment:**
```
Container:          _______________
Port:               _______________
Platform Plugins:   _______________  (e.g., bluesky, x, telegram)
Ready Platforms:    _______________  (which ones pass status check)
```

---

## Phase 1: WebUI Verification (6 tests)

Open the Agent Zero WebUI in your browser.

| ID | Test | Action | Expected | Result |
|----|------|--------|----------|--------|
| HV-01 | Plugin in list | Navigate to Settings > External Services | "Social Media Manager" appears in the plugin list | |
| HV-02 | Toggle | Toggle the Social Media Manager plugin off, then back on | Plugin disables/enables without error or page crash | |
| HV-03 | Dashboard loads | Click the Social Media Manager plugin dashboard tab | `main.html` renders with title in indigo (#6366F1), platform grid displays cards for all 10 supported platforms | |
| HV-04 | Platform status badges | Inspect the platform grid cards | Each card shows platform name and status badge (Ready / Not Configured / Disabled / Not Installed), summary line shows "X installed, Y ready of 10 supported platforms" | |
| HV-05 | Config loads | Click the Social Media Manager plugin settings tab | `config.html` renders with all sections: Default Platforms, Auto-adapt content, Content Preferences (max_hashtags etc.), Schedule timezone | |
| HV-06 | No console errors | Open browser DevTools (F12) > Console tab, reload the config page | Zero JavaScript errors in console | |

---

## Phase 2: Configuration & Platform Detection (6 tests)

| ID | Test | Action | Expected | Result |
|----|------|--------|----------|--------|
| HV-07 | Save config | Set default_platforms to "bluesky,x", uncheck auto-adapt, set max_hashtags to 3, set timezone to "US/Eastern", click Save | Success message appears (green "Saved!" or similar) | |
| HV-08 | Config persists | Reload the config page (F5) | All values persist as entered (default_platforms, auto-adapt off, max_hashtags=3, timezone=US/Eastern) | |
| HV-09 | Refresh status | Go to Dashboard, click "Refresh Status" button | Platform grid re-checks and updates badges; ready count matches installed platform state | |
| HV-10 | Detect installed platform | Ensure at least one platform plugin (e.g., Bluesky) is installed and enabled | Dashboard shows that platform as "Ready" or "Not Configured" (not "Not Installed") | |
| HV-11 | Detect missing platform | Confirm a platform plugin that is NOT installed (e.g., Mastodon) | Dashboard shows that platform as "Not Installed" | |
| HV-12 | Restart persistence | Run `docker exec <container> supervisorctl restart run_ui`, wait 10s, reload WebUI | Plugin still configured, dashboard loads, platform statuses unchanged | |

---

## Phase 3: Core Tools — Status & Adapt (5 tests)

Test via the Agent Zero chat interface. Type each prompt into the agent chat.

| ID | Test | Agent Prompt | Expected | Result |
|----|------|-------------|----------|--------|
| HV-13 | Status all platforms | "Check my social media platform status" | Agent uses `social_manager_status`, returns table with all 10 platforms showing installed/enabled/configured/ready columns; ready count matches dashboard | |
| HV-14 | Status single platform | "Check the status of my Bluesky connection" | Agent uses `social_manager_status` with platform="bluesky", returns status for just Bluesky | |
| HV-15 | Adapt all platforms | "Preview how this text would look on all platforms: [paste 300+ character text]" | Agent uses `social_manager_adapt`, shows per-platform preview with character counts; short-limit platforms (X 280, Bluesky 300) show truncation warnings; long-limit platforms (Reddit, Facebook) show no truncation | |
| HV-16 | Adapt specific platforms | "Preview this for X and LinkedIn: 'Product launch announcement with details'" | Agent uses `social_manager_adapt` with platforms="x,linkedin", only X and LinkedIn previews appear | |
| HV-17 | Adapt empty platforms | "Preview this for all platforms: 'Short test'" | Agent uses `social_manager_adapt`, no truncation warnings for any platform (text is well under all limits) | |

---

## Phase 4: Core Tools — Post (3 tests)

| ID | Test | Agent Prompt | Expected | Result |
|----|------|-------------|----------|--------|
| HV-18 | Cross-post multiple | "Post to all my social media: 'Hello from Social Media Manager!'" (at least 1 platform ready) | Agent uses `social_manager_post`, reports per-platform success/failure; content appears on ready platform(s); unreachable platforms show failure messages, no crashes | |
| HV-19 | Post with adaptation | "Post this everywhere: [paste 400+ character text]" | Agent uses `social_manager_post` with adapt_content=true; content trimmed for short-limit platforms (X, Bluesky); full text goes to long-limit platforms (Reddit, LinkedIn) | |
| HV-20 | Post to specific platform | "Post to Bluesky: 'Targeted platform post'" | Agent uses `social_manager_post` with platforms="bluesky", only posts to Bluesky | |

---

## Phase 5: Core Tools — Schedule (4 tests)

| ID | Test | Agent Prompt | Expected | Result |
|----|------|-------------|----------|--------|
| HV-21 | Schedule a post | "Schedule a post for tomorrow at 2pm UTC: 'Scheduled test'" | Agent uses `social_manager_schedule` with action="add", reports entry ID and scheduled time, mentions that actual posting requires a scheduler | |
| HV-22 | List scheduled posts | "Show my scheduled social media posts" | Agent uses `social_manager_schedule` with action="list", shows the entry from HV-21 | |
| HV-23 | Remove scheduled post | "Remove scheduled post #1" | Agent uses `social_manager_schedule` with action="remove", confirms removal | |
| HV-24 | List after removal | "Show my scheduled social media posts" | Returns empty list or confirms no scheduled posts | |

---

## Phase 6: Core Tools — Analytics (1 test)

| ID | Test | Agent Prompt | Expected | Result |
|----|------|-------------|----------|--------|
| HV-25 | Aggregate analytics | "Show my social media analytics for the past week" | Agent uses `social_manager_analytics` with period="week", collects from available platforms; unavailable platforms show "Analytics unavailable" (not crash) | |

---

## Phase 7: Skill Workflows (3 tests)

| ID | Test | Agent Prompt | Expected | Result |
|----|------|-------------|----------|--------|
| HV-26 | Publishing workflow | "Help me publish a post across all my social media" | Agent follows the social-manager-publish skill workflow: checks status, previews adaptation, then posts | |
| HV-27 | Monitoring skill | "Monitor my social media platform connections" | Agent follows the social-manager-monitor skill, shows comprehensive status report | |
| HV-28 | Campaign planning | "Help me plan a social media campaign" | Agent follows the social-manager-campaign skill, asks about campaign details, creates schedule entries | |

---

## Phase 8: Edge Cases & Error Handling (6 tests)

| ID | Test | Action | Expected | Result |
|----|------|--------|----------|--------|
| HV-29 | Post with no platforms ready | Disable all platform plugins, then ask: "Post everywhere: test" | Returns helpful error about no platforms being ready, no crash | |
| HV-30 | Post to unknown platform | Ask: "Post to myspace: test" | Returns error listing valid platform names | |
| HV-31 | Schedule missing time | Ask: "Schedule a post: test" (no time specified) | Returns error about scheduled_time being required | |
| HV-32 | Remove non-existent entry | Ask: "Remove scheduled post #999" | Returns error about entry not found | |
| HV-33 | CSRF enforcement | Run: `curl -X POST http://localhost:<port>/api/plugins/social_manager/social_manager_status -H "Content-Type: application/json" -d '{}'` | 403 Forbidden (no CSRF token) | |
| HV-34 | Re-enable platforms | Re-enable platform plugins disabled in HV-29, refresh dashboard | Platforms return to Ready state, posting works again | |

---

## Phase 9: Sign-Off

```
Plugin:           Social Media Manager
Version:          1.0.0
Container:        _______________
Port:             _______________
Date:             _______________
Tester:           _______________

Regression Tests: ___/___ PASS
Human Tests:      ___/34  PASS  ___/34 FAIL  ___/34 SKIP
Security Assessment: Pending / Complete (see SECURITY_ASSESSMENT_RESULTS.md)

Overall:          [ ] APPROVED  [ ] NEEDS WORK  [ ] BLOCKED

Notes:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

---

## Quick Troubleshooting

| Problem | Check |
|---------|-------|
| Dashboard shows all "Not Installed" | Are platform plugins actually deployed? Check symlinks in `/a0/plugins/` |
| Agent doesn't use social_manager tools | Is plugin enabled (.toggle-1)? Restart run_ui after deploy |
| Post fails on ready platform | Check the platform plugin's own connection — social_manager delegates to it |
| Schedule doesn't auto-post | Scheduling stores entries; actual posting requires an external scheduler or cron |
| Config not saving | Check browser console for JS errors; verify CSRF is working |
| Status mismatch dashboard vs tool | Click "Refresh Status" on dashboard; platform state may have changed |
