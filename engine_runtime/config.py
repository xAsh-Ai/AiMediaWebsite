"""Load engine configuration files from the repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
ENGINE_DIR = REPO_ROOT / "engine"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_registry_config() -> dict[str, Any]:
    return _load_json(ENGINE_DIR / "source-registry.json")


def load_source_item_schema() -> dict[str, Any]:
    return _load_json(ENGINE_DIR / "source-item.schema.json")


def load_workflow_config() -> dict[str, Any]:
    return _load_json(ENGINE_DIR / "workflow-state.json")


def load_review_rule_config() -> dict[str, Any]:
    return _load_json(ENGINE_DIR / "review-rules.json")


def active_sources(registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    config = registry or load_registry_config()
    return [source for source in config["sources"] if source.get("status") == "active"]


def get_source_by_id(source_id: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    config = registry or load_registry_config()
    for source in config["sources"]:
        if source["id"] == source_id:
            return source
    raise KeyError(f"Unknown source id: {source_id}")
