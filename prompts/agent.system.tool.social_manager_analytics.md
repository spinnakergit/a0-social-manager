## social_manager_analytics
Aggregate analytics from all connected social media platforms. Collects available metrics from each platform's analytics capabilities and presents a unified summary.

**How it works:**
1. Identifies which platforms are ready.
2. Queries each platform's analytics tool (if available).
3. Aggregates results into a combined report.
4. Platforms without analytics support or that are unreachable show "Analytics unavailable" rather than causing errors.

**Arguments:**
- **period** (string, optional): Time period for analytics — "day", "week", or "month" (default: "week")

~~~json
{"period": "week"}
~~~
~~~json
{"period": "month"}
~~~
~~~json
{"period": "day"}
~~~

**Notes:**
- Analytics availability depends on each platform plugin's capabilities. Not all platform plugins support analytics retrieval.
- This provides a cross-platform overview. For detailed per-platform analytics, use the individual platform plugin's tools.
- The period parameter maps to each platform's native time-range concept; exact ranges may vary slightly by platform.
