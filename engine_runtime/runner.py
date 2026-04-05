"""End-to-end orchestration for the AiMedia engine runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import get_source_by_id, load_registry_config, load_review_rule_config, load_workflow_config
from .models import SourceConfig
from .storage import ArtifactStore


def run_pipeline_from_html(
    source_id: str,
    html: str,
    *,
    fetched_at: str | None = None,
    existing_articles: list[dict[str, Any]] | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    from .normalize import normalize_source_item
    from .parsing import extract_source_items
    from .workflow import run_pipeline_for_item

    registry = load_registry_config()
    workflow_config = load_workflow_config()
    rule_config = load_review_rule_config()
    source_config = SourceConfig.from_dict(get_source_by_id(source_id, registry))

    raw_items = extract_source_items(source_config, html, fetched_at=fetched_at)
    if not raw_items:
        raise ValueError(f"No source items extracted for source_id={source_id}")

    normalized_items = [normalize_source_item(item, source_config) for item in raw_items]
    run_results = [
        run_pipeline_for_item(
            item,
            existing_articles=existing_articles or [],
            workflow_config=workflow_config,
            rule_config=rule_config,
        )
        for item in normalized_items
    ]

    payload = {
      "source": source_config.to_dict(),
      "source_items": [item.to_dict() for item in normalized_items],
      "runs": run_results,
    }

    if output_dir is not None:
        store = ArtifactStore(output_dir)
        store.write_json("pipeline-output.json", payload)

    return payload
