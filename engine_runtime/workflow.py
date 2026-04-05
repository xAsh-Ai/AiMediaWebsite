"""Workflow orchestration using the engine state model."""

from __future__ import annotations

from typing import Any

from .drafting import build_article_from_source_item
from .models import ChannelPackage, ContentJob, ReviewLog, SourceItem, utc_now
from .rules import run_review_rules


def _entity_config(workflow_config: dict[str, Any], entity_key: str) -> dict[str, Any]:
    if not workflow_config:
        raise ValueError("workflow_config is required")
    return workflow_config[entity_key]


def _can_transition(workflow_config: dict[str, Any], entity_key: str, from_state: str, to_state: str) -> bool:
    entity = _entity_config(workflow_config, entity_key)
    return any(
        transition["from"] == from_state and transition["to"] == to_state
        for transition in entity["transitions"]
    )


def _transition(workflow_config: dict[str, Any], entity_key: str, current_state: str, next_state: str) -> str:
    if current_state == next_state:
        return current_state
    if not _can_transition(workflow_config, entity_key, current_state, next_state):
        raise ValueError(f"Invalid {entity_key} transition: {current_state} -> {next_state}")
    return next_state


def _blocking_failures(review_logs: list[ReviewLog], rule_config: dict[str, Any]) -> list[str]:
    blocking = {
        rule["rule_key"]
        for rule in rule_config.get("rules", [])
        if rule.get("blocking")
    }
    return [log.rule_key for log in review_logs if log.rule_key in blocking and log.result == "fail"]


def _make_channel_packages(article_id: str) -> list[ChannelPackage]:
    created_at = utc_now()
    return [
        ChannelPackage(
            id=f"package:{article_id}:web",
            article_id=article_id,
            package_type="web_publish",
            created_at=created_at,
            payload={"surface": "web", "status": "ready"},
        ),
        ChannelPackage(
            id=f"package:{article_id}:newsletter",
            article_id=article_id,
            package_type="newsletter_batch",
            created_at=created_at,
            payload={"surface": "newsletter", "status": "ready"},
        ),
    ]


def run_pipeline_for_item(
    source_item: SourceItem,
    *,
    existing_articles: list[Any] | None = None,
    workflow_config: dict[str, Any] | None = None,
    rule_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_item.normalized is None:
        raise ValueError("source_item.normalized must exist before the workflow can run")
    if workflow_config is None:
        raise ValueError("workflow_config is required")
    if rule_config is None:
        raise ValueError("rule_config is required")

    timestamp = utc_now()
    job = ContentJob(
        id=f"job:{source_item.normalized.event_key}",
        source_item_id=source_item.id,
        status="queued",
        created_at=timestamp,
        updated_at=timestamp,
    )
    job.status = _transition(workflow_config, "content_job", job.status, "processing")

    article = build_article_from_source_item(source_item)
    job.article_id = article.id
    article.review_status = _transition(workflow_config, "article", article.review_status, "needs_review")
    job.status = _transition(workflow_config, "content_job", job.status, "needs_review")

    review_logs = run_review_rules(
        article,
        source_item,
        existing_articles=existing_articles or [],
        rule_config=rule_config,
    )
    failures = _blocking_failures(review_logs, rule_config)

    if not failures:
        article.review_status = _transition(workflow_config, "article", article.review_status, "approved")
        job.status = _transition(workflow_config, "content_job", job.status, "approved")
        channel_packages = _make_channel_packages(article.id)
        reason = "all blocking rules passed"
    elif "duplicate_title_exact" in failures:
        article.review_status = _transition(workflow_config, "article", article.review_status, "rejected")
        job.status = _transition(workflow_config, "content_job", job.status, "rejected")
        channel_packages = []
        reason = "exact duplicate detected"
    else:
        channel_packages = []
        reason = "manual revision required before approval"

    job.updated_at = utc_now()
    article.updated_at = utc_now()
    job.reason = reason

    return {
        "source_item": source_item.to_dict(),
        "content_job": job.to_dict(),
        "article": article.to_dict(),
        "review_logs": [log.to_dict() for log in review_logs],
        "channel_packages": [package.to_dict() for package in channel_packages],
        "blocking_failures": failures,
    }
