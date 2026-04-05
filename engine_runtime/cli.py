"""CLI entrypoints for the AiMedia engine runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import active_sources, load_registry_config
from .runner import run_pipeline_from_html


def _load_existing_articles(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return []
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("existing articles file must contain a JSON list")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aimedia-engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-sources", help="Print active source registry entries.")

    run_html = subparsers.add_parser("run-html", help="Run the engine pipeline from a local HTML file.")
    run_html.add_argument("--source-id", required=True)
    run_html.add_argument("--html-file", required=True)
    run_html.add_argument("--existing-articles")
    run_html.add_argument("--fetched-at")
    run_html.add_argument("--output-dir")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list-sources":
        payload = active_sources(load_registry_config())
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return 0

    if args.command == "run-html":
        html = Path(args.html_file).read_text(encoding="utf-8")
        payload = run_pipeline_from_html(
            args.source_id,
            html,
            fetched_at=args.fetched_at,
            existing_articles=_load_existing_articles(args.existing_articles),
            output_dir=args.output_dir,
        )
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
