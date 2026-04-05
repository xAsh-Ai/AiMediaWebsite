"""Dataclasses for engine runtime records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def _strip_none(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


@dataclass(slots=True)
class SourceConfig:
    id: str
    domain_id: str
    vendor_code: str
    vendor_name: str
    name: str
    source_type: str
    url: str
    is_official: bool
    fetch_cadence: str
    parser_key: str
    status: str
    notes: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SourceConfig":
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class NormalizedSourceItem:
    event_key: str
    vendor_code: str
    source_type: str
    title: str
    url: str
    published_at: str
    topic: str
    category: str
    trust_level: str
    official_source_links: list[str]
    first_seen_via: str | None = None
    affected_track: str = "undetermined"
    impact_tags: list[str] = field(default_factory=list)
    parser_key: str | None = None
    parser_version: str | None = None
    summary_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class SourceItem:
    id: str
    source_id: str
    vendor_code: str
    raw_fetched_at: str
    fetch_status: str
    external_id: str | None = None
    title: str | None = None
    url: str | None = None
    published_at: str | None = None
    raw_text: str | None = None
    normalized: NormalizedSourceItem | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = _strip_none(asdict(self))
        if self.normalized is not None:
            payload["normalized"] = self.normalized.to_dict()
        return payload


@dataclass(slots=True)
class ContentJob:
    id: str
    source_item_id: str
    status: str
    created_at: str
    updated_at: str
    article_id: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class Article:
    id: str
    content_job_id: str
    slug: str
    title: str
    review_status: str
    body_markdown: str
    created_at: str
    updated_at: str
    published_at: str | None = None
    source_item_id: str | None = None
    category: str | None = None
    affected_track: str | None = None
    official_source_links: list[str] = field(default_factory=list)
    impact_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class ReviewLog:
    id: str
    rule_key: str
    result: str
    message: str
    created_at: str
    article_id: str | None = None
    content_job_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class ChannelPackage:
    id: str
    article_id: str
    package_type: str
    created_at: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = _strip_none(asdict(self))
        data["payload"] = self.payload
        return data


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
