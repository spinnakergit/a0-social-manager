# Cross-Platform Publishing Workflow

Publish content across multiple social media platforms with automatic adaptation.

## Steps

1. **Check platform status** using `social_manager_status` to see which platforms are connected and ready.
2. **Preview adaptations** using `social_manager_adapt` with the user's content and target platforms. Review character limits and truncation warnings.
3. If content is too long for some platforms, suggest edits or confirm the user wants automatic truncation.
4. **Cross-post** using `social_manager_post` with the final text, target platforms, and any image attachment.
5. Report the per-platform results (success/failure) back to the user.

## Tips
- Always preview before posting to avoid surprises.
- If the user says "post everywhere" or "all platforms", use `platforms: "all"`.
- Mention which platforms were skipped (not installed/configured) so the user knows.
