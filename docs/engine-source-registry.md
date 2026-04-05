# Engine v0 Source Registry

`Issue #12` defines the first engine slice: represent official vendor sources as config, then normalize raw source items into a stable shape that downstream briefing logic can trust.

## Goals

- keep the first engine asset config-first instead of hardcoding vendor logic in the fetcher
- document the minimum `sources` and `source_items` contract before crawler work starts
- encode the first vendor inventory for OpenAI, Anthropic, Cursor, Vercel, and Supabase
- make the config/code boundary explicit so new vendors can be added without rewriting the engine

## Design posture

- Official sources are the final authority.
- Community links can be a discovery signal, but not the final truth.
- The registry should prefer reusable parser families over vendor-specific fetch code.
- New vendors should be addable by config when they fit an existing parser family.

## Source types

| source_type | What it represents | Pollable in v0 | Typical trust level |
| --- | --- | --- | --- |
| `changelog` | dedicated vendor change log | yes | `official_primary` |
| `release_notes` | product or app release notes | yes | `official_primary` |
| `deprecations` | retirement or migration notices | yes | `official_primary` |
| `docs` | official docs page used to confirm rollout behavior | yes | `official_secondary` |
| `github_release` | official GitHub release page | yes | `official_github` |
| `github_issue` | official GitHub issue or discussion used as a rollout notice | yes | `official_github` |
| `email` | account-scoped vendor email notice | no, manual intake only | `official_account_email` |

`email` is part of the model because the manual workflow already treats official email as a valid authority, but the first registry file only includes pollable web sources.

## `sources` config contract

The machine-readable definition lives in [`engine/source-registry.schema.json`](../engine/source-registry.schema.json) and the initial inventory lives in [`engine/source-registry.json`](../engine/source-registry.json).

Each source record must carry:

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | stable config key used by the engine |
| `domain_id` | yes | owning domain, currently `ai-saas` |
| `vendor_code` | yes | short vendor identifier such as `openai` |
| `vendor_name` | yes | human-readable vendor label |
| `name` | yes | source label shown in logs and admin views |
| `source_type` | yes | one of the source types above |
| `url` | yes | canonical official URL |
| `is_official` | yes | final authority flag, must be `true` for the initial inventory |
| `fetch_cadence` | yes | scheduler hint such as `hourly`, `daily`, or `manual` |
| `parser_key` | yes | parser family key selected by config |
| `status` | yes | `active`, `paused`, or `draft` |
| `notes` | no | editorial or ingestion notes |

## `source_items` capture and normalize contract

The machine-readable contract lives in [`engine/source-item.schema.json`](../engine/source-item.schema.json).

The raw capture layer keeps the minimal audit fields:

| Field | Meaning |
| --- | --- |
| `id` | internal item identifier |
| `source_id` | source registry link |
| `external_id` | vendor-provided item key when available |
| `vendor_code` | normalized vendor label |
| `title` | raw source title |
| `url` | raw item URL |
| `published_at` | item publish timestamp |
| `raw_text` | extracted text body before interpretation |
| `raw_fetched_at` | when the engine captured the item |
| `fetch_status` | `ok`, `partial`, `error`, or `skipped` |

The normalized object is the downstream contract used by briefing logic:

| Field | Meaning |
| --- | --- |
| `event_key` | stable dedupe key for one vendor event |
| `vendor_code` | vendor identifier repeated after normalization |
| `source_type` | normalized source family |
| `title` | normalized title |
| `url` | canonical item URL |
| `published_at` | normalized publish timestamp |
| `topic` | narrow subject, for example `model retirement` or `edge runtime` |
| `category` | site-facing category such as `models-api` or `deploy-infra` |
| `trust_level` | authority grade such as `official_primary` |
| `first_seen_via` | how the team first encountered the change |
| `affected_track` | `operations`, `engineering`, `both`, or `undetermined` |
| `impact_tags` | urgency or impact markers such as `breaking`, `cost`, `security` |
| `official_source_links` | one or more authority links used for audit and publication |
| `parser_key` | parser used to produce the item |
| `parser_version` | parser revision string for traceability |
| `summary_hint` | short neutral note for later content generation |

This keeps the normalize layer focused on fact extraction and routing hints. Review decisions, approval state, and publishing state belong to `Issue #13`.

## Initial vendor inventory

The initial registry covers the first tracked vendor set from the product brief:

| Vendor | Included sources | Why they are in v0 |
| --- | --- | --- |
| OpenAI | API changelog, API deprecations, ChatGPT release notes | highest editorial priority and already used in seed briefs |
| Anthropic | release notes overview, Claude Help Center release notes, model deprecations | strong comparator vendor for API and workspace changes |
| Cursor | changelog | primary coding-tool desk and interview-backed follow-up seed |
| Vercel | changelog | deploy, runtime, and pricing changes often overlap with API work |
| Supabase | changelog | infra, security, and dashboard changes fit the same audience |

## Config ends here, code begins here

Config owns:

- domain definitions
- vendor and source inventory
- fetch cadence hints
- parser selection by `parser_key`
- stable category and trust labels used by normalization

Code owns:

- HTTP fetching and retry logic
- parser implementations keyed by `parser_key`
- text extraction, checksuming, and dedupe
- normalized item validation against schema
- storage adapters, review pipeline, and publishing pipeline

The handoff rule is simple:

- if a new vendor fits an existing `source_type` and `parser_key`, add config only
- if a new source shape does not fit an existing parser family, add one parser in code and then reference it from config

That keeps vendor expansion mostly data-driven while still allowing parser code to stay generic and reusable.

## Files added in this slice

- [`engine/source-registry.schema.json`](../engine/source-registry.schema.json)
- [`engine/source-registry.json`](../engine/source-registry.json)
- [`engine/source-item.schema.json`](../engine/source-item.schema.json)

These files are intentionally engine-facing assets, not crawler code. They are the contract that the first ingestion prototype should consume.
