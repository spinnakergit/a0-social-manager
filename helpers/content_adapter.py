"""Content adaptation for different social media platforms.

Handles character limits, hashtag formatting, mention translation,
and thread splitting for cross-platform posting.
"""

import logging
import re

logger = logging.getLogger("social_manager")


def adapt_for_platform(text: str, platform: str, max_length: int,
                       add_hashtags: bool = False,
                       max_hashtags: int = 5) -> str:
    """
    Adapt text content for a specific platform's constraints.

    - Trims to max_length with ellipsis if needed
    - Optionally extracts/adds hashtags
    - Cleans whitespace

    Returns the adapted text string.
    """
    if not text:
        return ""

    # Normalize whitespace
    adapted = re.sub(r"\n{3,}", "\n\n", text.strip())

    # Platform-specific mention format adjustments
    adapted = _adapt_mentions(adapted, platform)

    # Handle hashtags
    if add_hashtags:
        adapted = _normalize_hashtags(adapted, max_hashtags)

    # Enforce character limit
    if len(adapted) > max_length:
        # Leave room for ellipsis
        adapted = adapted[: max_length - 1].rstrip() + "\u2026"

    return adapted


def _adapt_mentions(text: str, platform: str) -> str:
    """Adjust mention format for the target platform."""
    # Most platforms use @username; Bluesky uses @handle.bsky.social
    # We leave mentions as-is since the source format is unknown
    return text


def _normalize_hashtags(text: str, max_hashtags: int) -> str:
    """Ensure hashtags are properly formatted and capped."""
    existing = re.findall(r"#\w+", text)
    if len(existing) > max_hashtags:
        # Remove excess hashtags from end
        to_remove = existing[max_hashtags:]
        for tag in to_remove:
            text = text.replace(tag, "").strip()
    return text


def split_for_threads(text: str, max_length: int) -> list:
    """
    Split long content into thread-sized chunks for a platform.

    Splits on paragraph boundaries first, then sentence boundaries,
    then hard-wraps as a last resort. Adds thread numbering.
    """
    if not text or len(text) <= max_length:
        return [text]

    # Reserve space for thread numbering like " (1/N)"
    reserve = 8
    effective_limit = max_length - reserve

    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        candidate = (current + "\n\n" + para).strip() if current else para.strip()

        if len(candidate) <= effective_limit:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # If single paragraph exceeds limit, split by sentences
            if len(para) > effective_limit:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                current = ""
                for sentence in sentences:
                    candidate = (current + " " + sentence).strip() if current else sentence
                    if len(candidate) <= effective_limit:
                        current = candidate
                    else:
                        if current:
                            chunks.append(current)
                        # Hard split if single sentence exceeds limit
                        if len(sentence) > effective_limit:
                            for i in range(0, len(sentence), effective_limit):
                                chunks.append(sentence[i: i + effective_limit])
                            current = ""
                        else:
                            current = sentence
            else:
                current = para.strip()

    if current:
        chunks.append(current)

    # Add thread numbering
    total = len(chunks)
    if total > 1:
        chunks = [f"{chunk} ({i + 1}/{total})" for i, chunk in enumerate(chunks)]

    return chunks


def generate_platform_variants(text: str, platforms: list,
                               add_hashtags: bool = False,
                               max_hashtags: int = 5) -> dict:
    """
    Generate adapted versions of text for each platform.

    Args:
        text: The source text.
        platforms: List of platform dicts (from get_available_platforms).
        add_hashtags: Whether to normalize hashtags.
        max_hashtags: Maximum hashtags to keep.

    Returns:
        Dict of platform_name -> adapted_text.
    """
    variants = {}
    for platform in platforms:
        name = platform["platform"]
        limit = platform["char_limit"]
        adapted = adapt_for_platform(
            text, name, limit,
            add_hashtags=add_hashtags,
            max_hashtags=max_hashtags,
        )
        variants[name] = adapted
    return variants


def preview_adaptations(text: str, platforms: list,
                        add_hashtags: bool = False,
                        max_hashtags: int = 5) -> list:
    """
    Generate a preview showing how text will appear on each platform.
    Returns a list of dicts with platform info, adapted text, and warnings.
    """
    results = []
    for platform in platforms:
        name = platform["platform"]
        limit = platform["char_limit"]
        adapted = adapt_for_platform(
            text, name, limit,
            add_hashtags=add_hashtags,
            max_hashtags=max_hashtags,
        )

        warnings = []
        original_len = len(text)
        adapted_len = len(adapted)

        if original_len > limit:
            warnings.append(
                f"Content truncated: {original_len} -> {adapted_len} chars "
                f"(limit: {limit})"
            )

        # Check media constraints
        if not platform.get("supports_images"):
            warnings.append("Platform does not support image attachments")
        if not platform.get("supports_video"):
            warnings.append("Platform does not support video attachments")

        results.append({
            "platform": name,
            "char_limit": limit,
            "original_length": original_len,
            "adapted_length": adapted_len,
            "adapted_text": adapted,
            "truncated": original_len > limit,
            "warnings": warnings,
        })

    return results
