# Platform Monitoring Workflow

Monitor the status and health of all connected social media platforms.

## Steps

1. **Check all platforms** using `social_manager_status` with no arguments to get a full status table.
2. For any platforms showing as not ready, explain what is missing:
   - Not installed: the platform plugin needs to be installed
   - Not enabled: the plugin needs to be toggled on in A0 settings
   - Not configured: credentials/tokens need to be set up in the platform plugin's config
3. If the user wants analytics, use `social_manager_analytics` with the requested period (day, week, month).
4. Summarize findings: which platforms are healthy, which need attention, and key metrics.

## Tips
- Run status checks periodically to catch configuration issues early.
- If a platform was previously working but now shows "not configured", credentials may have expired.
