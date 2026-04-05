"""Deterministic draft generation from normalized source items."""

from __future__ import annotations

import re

from .models import Article, SourceItem, utc_now


_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    slug = _NON_ALNUM_RE.sub("-", value.lower()).strip("-")
    return slug or "brief"


def build_article_from_source_item(source_item: SourceItem) -> Article:
    if source_item.normalized is None:
        raise ValueError("source_item.normalized must exist before article generation")

    normalized = source_item.normalized
    timestamp = utc_now()
    title = normalized.title
    slug = _slugify(normalized.event_key.replace(":", "-"))
    impact_tags = ", ".join(normalized.impact_tags) if normalized.impact_tags else "monitor"
    official_links = "\n".join(f"- {link}" for link in normalized.official_source_links)
    summary = normalized.summary_hint or "Official source update captured by the engine."

    body_markdown = f"""# {title}

## One-line conclusion
{normalized.vendor_code.title()} shipped a {normalized.topic} update that maps to `{normalized.category}` for `{normalized.affected_track}` teams.

## What changed
{summary}

## Who is affected
- Track: `{normalized.affected_track}`
- Tags: `{impact_tags}`

## Practical impact
This change matters because it can alter existing workflows, implementation details, or operating assumptions for teams following `{normalized.vendor_code}` updates.

## What to do now
- Confirm whether the current workflow depends on the changed capability.
- Review the official source before shipping downstream communication.
- Decide whether this should become a fast brief, weekly item, or no-publish record.

## Official sources
{official_links}

## CTA
Track this update in the weekly summary and escalate it for editorial review if it is breaking, costly, or security-relevant.
"""

    return Article(
        id=f"article:{normalized.event_key}",
        content_job_id=f"job:{normalized.event_key}",
        slug=slug,
        title=title,
        review_status="draft",
        body_markdown=body_markdown,
        created_at=timestamp,
        updated_at=timestamp,
        source_item_id=source_item.id,
        category=normalized.category,
        affected_track=normalized.affected_track,
        official_source_links=list(normalized.official_source_links),
        impact_tags=list(normalized.impact_tags),
    )
