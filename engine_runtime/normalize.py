"""Normalize raw source items into the stable downstream contract."""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urlparse

from .models import NormalizedSourceItem, SourceConfig, SourceItem


PARSER_VERSION = "v1"
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")

_CATEGORY_RULES = [
    ("models-api", ("model", "api", "endpoint", "sdk", "responses api", "embedding")),
    ("coding-tools", ("cursor", "editor", "ide", "agent", "autocomplete", "coding")),
    ("deploy-infra", ("deploy", "runtime", "edge", "infrastructure", "vercel", "database", "auth")),
    ("billing-plan", ("price", "pricing", "billing", "invoice", "quota", "plan", "credit")),
    ("automation-agents", ("agent", "automation", "workflow", "tool call", "mcp")),
    ("governance-policy", ("policy", "terms", "retention", "privacy", "governance")),
    ("security-compliance", ("security", "vulnerability", "compliance", "permission", "soc 2")),
    ("docs-education", ("docs", "documentation", "tutorial", "guide", "education")),
    ("workspace-apps", ("workspace", "chatgpt", "claude app", "dashboard", "admin")),
]

_TAG_RULES = [
    ("breaking", ("breaking", "deprecated", "deprecation", "sunset", "remove", "retire")),
    ("cost", ("price", "pricing", "billing", "cost", "quota", "credit")),
    ("security", ("security", "auth", "permission", "compliance", "vulnerability")),
    ("education", ("docs", "guide", "tutorial", "education", "learn")),
    ("deployment", ("deploy", "runtime", "infrastructure", "rollout", "migration")),
    ("policy", ("policy", "privacy", "terms", "retention")),
    ("reliability", ("outage", "latency", "stability", "reliability")),
    ("migration", ("migrate", "migration", "replacement", "upgrade")),
]

_ENGINEERING_KEYWORDS = ("api", "sdk", "deploy", "runtime", "code", "model", "database", "auth")
_OPERATIONS_KEYWORDS = ("admin", "workspace", "plan", "billing", "pricing", "policy", "team")
_ENGINEERING_CATEGORIES = {"models-api", "coding-tools", "deploy-infra", "automation-agents", "security-compliance"}
_OPERATIONS_CATEGORIES = {"billing-plan", "governance-policy", "workspace-apps", "docs-education"}


def _slugify(value: str) -> str:
    slug = _NON_ALNUM_RE.sub("-", value.lower()).strip("-")
    return slug or "item"


def _text_haystack(item: SourceItem, source: SourceConfig) -> str:
    return " ".join(
        filter(
            None,
            [
                item.title,
                item.raw_text,
                source.name,
                source.vendor_name,
                source.notes,
                source.source_type,
            ],
        )
    ).casefold()


def _category_for(item: SourceItem, source: SourceConfig) -> str:
    haystack = _text_haystack(item, source)
    for category, keywords in _CATEGORY_RULES:
        if any(keyword in haystack for keyword in keywords):
            return category
    if source.vendor_code == "cursor":
        return "coding-tools"
    if source.vendor_code in {"vercel", "supabase"}:
        return "deploy-infra"
    return "other"


def _impact_tags_for(item: SourceItem, source: SourceConfig) -> list[str]:
    haystack = _text_haystack(item, source)
    tags = [tag for tag, keywords in _TAG_RULES if any(keyword in haystack for keyword in keywords)]
    return sorted(dict.fromkeys(tags))


def _track_for(item: SourceItem, source: SourceConfig, category: str) -> str:
    haystack = _text_haystack(item, source)
    engineering = any(keyword in haystack for keyword in _ENGINEERING_KEYWORDS)
    operations = any(keyword in haystack for keyword in _OPERATIONS_KEYWORDS)
    if category in _ENGINEERING_CATEGORIES and engineering:
        return "engineering"
    if category in _OPERATIONS_CATEGORIES and operations:
        return "operations"
    if engineering and operations:
        return "both"
    if engineering:
        return "engineering"
    if operations:
        return "operations"
    return "undetermined"


def _trust_level_for(source: SourceConfig) -> str:
    if not source.is_official:
        return "community_signal"
    if source.source_type in {"changelog", "release_notes", "deprecations"}:
        return "official_primary"
    if source.source_type in {"github_release", "github_issue"}:
        return "official_github"
    if source.source_type == "email":
        return "official_account_email"
    return "official_secondary"


def _topic_for(item: SourceItem, source: SourceConfig, category: str) -> str:
    title = (item.title or source.name).casefold()
    if "deprecat" in title or "retire" in title:
        return "model retirement" if category == "models-api" else "deprecation notice"
    if "price" in title or "billing" in title:
        return "pricing change"
    if "security" in title:
        return "security change"
    if "deploy" in title or "runtime" in title:
        return "runtime update"
    if category == "coding-tools":
        return "coding workflow update"
    if category == "models-api":
        return "api change"
    return f"{source.source_type} update"


def _summary_hint(item: SourceItem) -> str | None:
    if not item.raw_text:
        return None
    sentence = item.raw_text.split(".")[0].strip()
    return sentence[:220] if sentence else None


def _event_key(item: SourceItem, source: SourceConfig) -> str:
    published_at = item.published_at or item.raw_fetched_at
    date_part = published_at[:10]
    slug = _slugify(item.title or source.name)
    digest = hashlib.sha1(f"{source.id}:{item.url}:{item.title}".encode("utf-8")).hexdigest()[:8]
    return f"{source.vendor_code}:{date_part}:{slug}:{digest}"


def _canonical_url(item: SourceItem, source: SourceConfig) -> str:
    return item.url or source.url


def _official_links(item: SourceItem, source: SourceConfig) -> list[str]:
    links = [_canonical_url(item, source)]
    parsed = urlparse(source.url)
    if parsed.scheme and parsed.netloc and source.url not in links:
        links.append(source.url)
    return links[:1]


def normalize_source_item(item: SourceItem, source_config: SourceConfig) -> SourceItem:
    category = _category_for(item, source_config)
    normalized = NormalizedSourceItem(
        event_key=_event_key(item, source_config),
        vendor_code=source_config.vendor_code,
        source_type=source_config.source_type,
        title=item.title or source_config.name,
        url=_canonical_url(item, source_config),
        published_at=item.published_at or item.raw_fetched_at,
        topic=_topic_for(item, source_config, category),
        category=category,
        trust_level=_trust_level_for(source_config),
        first_seen_via=source_config.id,
        affected_track=_track_for(item, source_config, category),
        impact_tags=_impact_tags_for(item, source_config),
        official_source_links=_official_links(item, source_config),
        parser_key=source_config.parser_key,
        parser_version=PARSER_VERSION,
        summary_hint=_summary_hint(item),
    )
    item.normalized = normalized
    return item
