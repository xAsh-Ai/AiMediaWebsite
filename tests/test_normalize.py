from __future__ import annotations

import unittest

from engine_runtime.models import SourceConfig
from engine_runtime.normalize import normalize_source_item
from engine_runtime.parsing import extract_source_items


class NormalizeTests(unittest.TestCase):
    def test_extract_article_and_normalize(self) -> None:
        source = SourceConfig(
            id="openai-api-deprecations",
            domain_id="ai-saas",
            vendor_code="openai",
            vendor_name="OpenAI",
            name="OpenAI API deprecations",
            source_type="deprecations",
            url="https://developers.openai.com/api/docs/deprecations",
            is_official=True,
            fetch_cadence="daily",
            parser_key="html-docs-article",
            status="active",
        )
        html = """
        <html>
          <head><title>Deprecating the old Responses API</title></head>
          <body>
            <time datetime="2026-04-01T00:00:00Z">2026-04-01</time>
            <p>The old endpoint is deprecated and teams should migrate.</p>
            <p>This affects API integrations and deployment planning.</p>
          </body>
        </html>
        """

        items = extract_source_items(source, html, fetched_at="2026-04-05T00:00:00Z")
        self.assertEqual(len(items), 1)

        item = normalize_source_item(items[0], source)
        self.assertEqual(item.published_at, "2026-04-01T00:00:00Z")
        self.assertEqual(item.normalized.category, "models-api")
        self.assertIn("breaking", item.normalized.impact_tags)
        self.assertEqual(item.normalized.affected_track, "engineering")
        self.assertEqual(item.normalized.trust_level, "official_primary")

    def test_extract_changelog_entries(self) -> None:
        source = SourceConfig(
            id="cursor-changelog",
            domain_id="ai-saas",
            vendor_code="cursor",
            vendor_name="Cursor",
            name="Cursor changelog",
            source_type="changelog",
            url="https://cursor.com/changelog",
            is_official=True,
            fetch_cadence="daily",
            parser_key="html-site-changelog",
            status="active",
        )
        html = """
        <html>
          <head><title>Cursor changelog</title></head>
          <body>
            <h2>Agent mode now supports longer tasks</h2>
            <time datetime="2026-04-03T00:00:00Z">2026-04-03</time>
            <p>Developers can run multi-step coding tasks in agent mode.</p>
            <h2>Workspace admin controls</h2>
            <time datetime="2026-04-02T00:00:00Z">2026-04-02</time>
            <p>Admins can manage policy and security defaults.</p>
          </body>
        </html>
        """

        items = extract_source_items(source, html, fetched_at="2026-04-05T00:00:00Z")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].published_at, "2026-04-03T00:00:00Z")
        self.assertEqual(items[1].published_at, "2026-04-02T00:00:00Z")
        normalized = [normalize_source_item(item, source) for item in items]
        self.assertEqual(normalized[0].normalized.category, "coding-tools")
        self.assertEqual(normalized[1].normalized.affected_track, "operations")


if __name__ == "__main__":
    unittest.main()
