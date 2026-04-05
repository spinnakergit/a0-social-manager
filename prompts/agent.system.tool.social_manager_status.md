## social_manager_status
Check connection status across all social media platforms. Shows which platform plugins are installed, enabled, configured, and ready for posting. Use this tool before cross-posting to understand which platforms are available.

**How it works:**
1. Scans the Agent Zero plugin directories for each supported platform plugin.
2. Checks whether each plugin has a `plugin.yaml` (installed), a `.toggle-1` file (enabled), and non-empty configuration (configured).
3. A platform is "ready" only if all three conditions are met.
4. Returns a formatted table with the status of all 10 supported platforms.

**Arguments:**
- **platform** (string, optional): Filter to a specific platform name. Omit to check all platforms.

~~~json
{}
~~~
~~~json
{"platform": "bluesky"}
~~~
~~~json
{"platform": "x"}
~~~

**Notes:**
- Use this before `social_manager_post` to confirm which platforms will receive your content.
- If a platform shows "Not Configured," the user needs to set up that platform's individual plugin (API keys, tokens, etc.).
- If a platform shows "Not Installed," the corresponding platform plugin needs to be installed in Agent Zero first.
