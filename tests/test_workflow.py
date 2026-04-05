from __future__ import annotations

import unittest

from engine_runtime.config import load_review_rule_config, load_workflow_config
from engine_runtime.drafting import build_article_from_source_item
from engine_runtime.models import NormalizedSourceItem, SourceItem
from engine_runtime.rules import run_review_rules
from engine_runtime.workflow import run_pipeline_for_item


def _source_item(title: str, event_key: str) -> SourceItem:
    return SourceItem(
        id=f"item:{event_key}",
        source_id="openai-api-changelog",
        vendor_code="openai",
        title=title,
        url="https://developers.openai.com/docs/changelog",
        published_at="2026-04-01T00:00:00Z",
        raw_text="The API changed and teams should respond.",
        raw_fetched_at="2026-04-05T00:00:00Z",
        fetch_status="ok",
        normalized=NormalizedSourceItem(
            event_key=event_key,
            vendor_code="openai",
            source_type="changelog",
            title=title,
            url="https://developers.openai.com/docs/changelog",
            published_at="2026-04-01T00:00:00Z",
            topic="api change",
            category="models-api",
            trust_level="official_primary",
            official_source_links=["https://developers.openai.com/docs/changelog"],
            affected_track="engineering",
            impact_tags=["breaking"],
            parser_key="html-docs-changelog",
            parser_version="v1",
            summary_hint="A new API behavior was introduced.",
        ),
    )


class WorkflowTests(unittest.TestCase):
    def test_draft_contains_required_sections(self) -> None:
        article = build_article_from_source_item(_source_item("OpenAI ships a new API", "openai:test"))
        self.assertIn("## Practical impact", article.body_markdown)
        self.assertIn("## What to do now", article.body_markdown)
        self.assertIn("## CTA", article.body_markdown)

    def test_pipeline_approves_clean_item(self) -> None:
        payload = run_pipeline_for_item(
            _source_item("OpenAI ships a new API", "openai:clean"),
            existing_articles=[],
            workflow_config=load_workflow_config(),
            rule_config=load_review_rule_config(),
        )
        self.assertEqual(payload["content_job"]["status"], "approved")
        self.assertEqual(payload["article"]["review_status"], "approved")
        self.assertEqual(len(payload["channel_packages"]), 2)

    def test_pipeline_rejects_exact_duplicate(self) -> None:
        payload = run_pipeline_for_item(
            _source_item("OpenAI ships a new API", "openai:dup"),
            existing_articles=[{"title": "OpenAI ships a new API", "review_status": "published"}],
            workflow_config=load_workflow_config(),
            rule_config=load_review_rule_config(),
        )
        self.assertEqual(payload["content_job"]["status"], "rejected")
        self.assertEqual(payload["article"]["review_status"], "rejected")
        self.assertIn("duplicate_title_exact", payload["blocking_failures"])

    def test_rule_runner_reports_similarity(self) -> None:
        article = build_article_from_source_item(_source_item("Cursor agent mode upgrade", "cursor:test"))
        logs = run_review_rules(
            article,
            _source_item("Cursor agent mode upgrade", "cursor:test"),
            existing_articles=[{"title": "Cursor agent mode upgrades", "review_status": "approved"}],
            rule_config=load_review_rule_config(),
        )
        similarity = next(log for log in logs if log.rule_key == "duplicate_similarity")
        self.assertEqual(similarity.result, "fail")


if __name__ == "__main__":
    unittest.main()
