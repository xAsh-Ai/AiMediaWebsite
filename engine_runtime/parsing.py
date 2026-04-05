"""HTML parsing utilities for engine source ingestion."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Iterable

from .models import SourceConfig, SourceItem, utc_now


PARSER_VERSION = "v1"
_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_TEXT_TAGS = _HEADING_TAGS | {"title", "p", "li", "time"}
_WHITESPACE_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


@dataclass(slots=True)
class TextBlock:
    tag: str
    text: str
    attrs: dict[str, str]


class _BlockHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[TextBlock] = []
        self._stack: list[tuple[str, dict[str, str], list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _TEXT_TAGS:
            normalized_attrs = {key: value or "" for key, value in attrs}
            self._stack.append((tag, normalized_attrs, []))

    def handle_data(self, data: str) -> None:
        if self._stack:
            self._stack[-1][2].append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return
        current_tag, attrs, parts = self._stack[-1]
        if current_tag != tag:
            return
        self._stack.pop()
        text = _clean_text("".join(parts))
        if text:
            self.blocks.append(TextBlock(tag=current_tag, text=text, attrs=attrs))


def _clean_text(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value).strip()


def _slugify(value: str) -> str:
    slug = _NON_ALNUM_RE.sub("-", value.lower()).strip("-")
    return slug or "item"


def _looks_like_metadata(text: str, source: SourceConfig) -> bool:
    lowered = text.casefold()
    vendor_bits = {
        source.vendor_name.casefold(),
        source.name.casefold(),
        f"{source.vendor_name.casefold()} changelog",
        "changelog",
        "release notes",
        "overview",
    }
    return lowered in vendor_bits


def _normalize_datetime(text: str, fallback: str) -> str:
    candidate = text.strip()
    if not candidate:
        return fallback

    iso_candidate = candidate.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(iso_candidate)
        if parsed.tzinfo is None:
            return parsed.replace(microsecond=0).isoformat() + "Z"
        return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(candidate, fmt)
            return parsed.replace(microsecond=0).isoformat() + "Z"
        except ValueError:
            continue

    return fallback


def _document_blocks(html: str) -> list[TextBlock]:
    parser = _BlockHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.blocks


def _page_title(blocks: Iterable[TextBlock]) -> str | None:
    for block in blocks:
        if block.tag == "title":
            return block.text
    for block in blocks:
        if block.tag in _HEADING_TAGS:
            return block.text
    return None


def _entry_item(
    *,
    source: SourceConfig,
    title: str,
    raw_text: str,
    fetched_at: str,
    published_at: str | None,
    index: int,
    url: str | None = None,
) -> SourceItem:
    slug = _slugify(title)
    return SourceItem(
        id=f"{source.id}:{index}:{slug}",
        source_id=source.id,
        vendor_code=source.vendor_code,
        external_id=slug,
        title=title,
        url=url or f"{source.url}#{slug}",
        published_at=published_at or fetched_at,
        raw_text=raw_text,
        raw_fetched_at=fetched_at,
        fetch_status="ok" if raw_text else "partial",
    )


def _parse_article(source: SourceConfig, blocks: list[TextBlock], fetched_at: str) -> list[SourceItem]:
    title = _page_title(blocks) or source.name
    body_parts = [block.text for block in blocks if block.tag in {"p", "li"}]
    raw_text = "\n".join(body_parts).strip() or title
    published_at = None
    for block in blocks:
        if block.tag == "time":
            published_at = _normalize_datetime(block.attrs.get("datetime") or block.text, fetched_at)
            break
    return [
        _entry_item(
            source=source,
            title=title,
            raw_text=raw_text,
            fetched_at=fetched_at,
            published_at=published_at,
            index=0,
            url=source.url,
        )
    ]


def _parse_changelog(source: SourceConfig, blocks: list[TextBlock], fetched_at: str) -> list[SourceItem]:
    page_title = _page_title(blocks)
    entries: list[dict[str, str | list[str] | None]] = []
    current: dict[str, str | list[str] | None] | None = None
    pending_time: str | None = None

    for block in blocks:
        if block.tag == "time":
            pending_time = _normalize_datetime(block.attrs.get("datetime") or block.text, fetched_at)
            if current and not current["published_at"]:
                current["published_at"] = pending_time
                pending_time = None
            continue

        if block.tag in {"h2", "h3", "h4"} and not _looks_like_metadata(block.text, source):
            if page_title and block.text == page_title:
                continue
            if current and current["parts"]:
                entries.append(current)
            current = {
                "title": block.text,
                "published_at": pending_time,
                "parts": [],
            }
            pending_time = None
            continue

        if block.tag in {"p", "li"}:
            if current is None:
                continue
            parts = current["parts"]
            assert isinstance(parts, list)
            parts.append(block.text)

    if current and current["parts"]:
        entries.append(current)

    if not entries:
        return _parse_article(source, blocks, fetched_at)

    items: list[SourceItem] = []
    for index, entry in enumerate(entries):
        parts = entry["parts"]
        assert isinstance(parts, list)
        items.append(
            _entry_item(
                source=source,
                title=str(entry["title"]),
                raw_text="\n".join(parts).strip(),
                fetched_at=fetched_at,
                published_at=str(entry["published_at"]) if entry["published_at"] else None,
                index=index,
            )
        )
    return items


def extract_source_items(
    source_config: SourceConfig,
    html: str,
    fetched_at: str | None = None,
) -> list[SourceItem]:
    """Extract raw source items from HTML using the registry parser key."""

    fetched_at = fetched_at or utc_now()
    blocks = _document_blocks(html)

    if source_config.parser_key == "html-docs-article":
        return _parse_article(source_config, blocks, fetched_at)

    if source_config.parser_key in {
        "html-docs-changelog",
        "html-site-changelog",
        "help-center-release-notes",
    }:
        return _parse_changelog(source_config, blocks, fetched_at)

    raise ValueError(f"Unsupported parser_key: {source_config.parser_key}")
