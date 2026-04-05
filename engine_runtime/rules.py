"""Deterministic rule execution for engine drafts."""

from __future__ import annotations

import difflib
import re
from typing import Any

from .models import Article, ReviewLog, SourceItem, utc_now


_HEADING_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)
_WORD_RE = re.compile(r"[a-z0-9]+")
_ACTIVE_ARTICLE_STATES = {"approved", "scheduled", "published"}


def _normalize_title(value: str) -> str:
    return " ".join(_WORD_RE.findall(value.casefold()))


def _existing_article_values(existing_articles: list[Any]) -> list[dict[str, str]]:
    values: list[dict[str, str]] = []
    for article in existing_articles:
        if isinstance(article, Article):
            values.append({"title": article.title, "review_status": article.review_status})
            continue
        if isinstance(article, dict):
            values.append(
                {
                    "title": str(article.get("title", "")),
                    "review_status": str(article.get("review_status", "")),
                }
            )
    return values


def _make_log(article: Article, rule_key: str, result: str, message: str) -> ReviewLog:
    created_at = utc_now()
    return ReviewLog(
        id=f"log:{article.id}:{rule_key}:{created_at}",
        article_id=article.id,
        rule_key=rule_key,
        result=result,
        message=message,
        created_at=created_at,
    )


def _section_map(body_markdown: str) -> set[str]:
    return {match.group(1).strip().casefold() for match in _HEADING_RE.finditer(body_markdown)}


def run_review_rules(
    article: Article,
    source_item: SourceItem,
    existing_articles: list[Any] | None = None,
    rule_config: dict[str, Any] | None = None,
) -> list[ReviewLog]:
    if source_item.normalized is None:
        raise ValueError("source_item.normalized must exist before review")

    existing_articles = existing_articles or []
    existing = _existing_article_values(existing_articles)
    normalized = source_item.normalized
    sections = _section_map(article.body_markdown)
    logs: list[ReviewLog] = []
    threshold = 0.8

    if rule_config:
        for rule in rule_config.get("rules", []):
            if rule.get("rule_key") == "duplicate_similarity":
                threshold = float(rule.get("similarity_threshold", threshold))
                break

    if normalized.official_source_links and all(link in article.body_markdown for link in normalized.official_source_links):
        logs.append(_make_log(article, "official_source_first", "pass", "Official source links are present in the article."))
    else:
        logs.append(_make_log(article, "official_source_first", "fail", "Article is missing one or more official source links."))

    if "practical impact" in sections:
        logs.append(_make_log(article, "practical_impact_present", "pass", "Practical impact section exists."))
    else:
        logs.append(_make_log(article, "practical_impact_present", "fail", "Practical impact section is missing."))

    if "what to do now" in sections:
        logs.append(_make_log(article, "what_to_do_now_present", "pass", "What-to-do-now section exists."))
    else:
        logs.append(_make_log(article, "what_to_do_now_present", "fail", "What-to-do-now section is missing."))

    if "cta" in sections:
        logs.append(_make_log(article, "cta_present", "pass", "CTA section exists."))
    else:
        logs.append(_make_log(article, "cta_present", "fail", "CTA section is missing."))

    normalized_title = _normalize_title(article.title)
    exact_duplicate = any(
        _normalize_title(item["title"]) == normalized_title and item["review_status"] in _ACTIVE_ARTICLE_STATES
        for item in existing
    )
    if exact_duplicate:
        logs.append(_make_log(article, "duplicate_title_exact", "fail", "An active article already uses this normalized title."))
    else:
        logs.append(_make_log(article, "duplicate_title_exact", "pass", "No exact duplicate title detected."))

    highest_ratio = 0.0
    closest_title = None
    for item in existing:
        if item["review_status"] not in _ACTIVE_ARTICLE_STATES:
            continue
        ratio = difflib.SequenceMatcher(None, normalized_title, _normalize_title(item["title"])).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            closest_title = item["title"]

    if highest_ratio >= threshold:
        logs.append(
            _make_log(
                article,
                "duplicate_similarity",
                "fail",
                f"Similar article detected ({highest_ratio:.2f} vs threshold {threshold:.2f}) against '{closest_title}'.",
            )
        )
    else:
        logs.append(
            _make_log(
                article,
                "duplicate_similarity",
                "pass",
                f"No near-duplicate exceeded the threshold ({highest_ratio:.2f} < {threshold:.2f}).",
            )
        )

    return logs
