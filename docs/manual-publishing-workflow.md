# Manual Publishing Workflow

## Goal
Validate the MVP with manual, interview-backed briefs before building any ingestion or automation engine.

## Non-goals
- No crawler
- No auto-publishing
- No “rewrite the changelog” workflow

## Allowed source policy
Use official sources as the final authority:
- vendor changelog
- release notes
- developer docs
- official email
- official GitHub release or issue thread

Signals like X, Slack, or community posts can be the **first discovery channel**, but they cannot be the final source of truth.

## Required evidence fields
Every published brief must capture these fields explicitly:

| Field | Why it exists | Example |
|------|------|------|
| official source links | preserve authority and audit trail | OpenAI deprecations, Vercel changelog |
| first discovery channel | show how the team first encountered the change | official email, X link, security Slack |
| who confirms | identify the owner who validates the impact | AI governance lead, backend owner |
| who shares | identify the person who broadcasts it internally | education lead, on-call handoff |
| who acts | identify the team that executes the change | team lead, DevOps, backend |
| action types taken | capture the real operational work | wiki update, staging smoke, fallback memo |
| preferred share format | match the brief to the internal audience | leader 5-line, Slack-ready note |
| priority tags | explain urgency and impact type at a glance | Breaking, Cost, Security |
| what to do this week | force the brief into an action block | impact scan, rollout note, checklist |

## Manual publishing sequence
1. Select one official update candidate.
   Skip it if it is only a minor UI tweak, a marketing announcement, or has no clear operational impact.
2. Decide the primary track.
   Choose `Operations` when the work is policy, education, governance, account scope, audit, or internal guide updates.
   Choose `Engineering` when the work is SDK, endpoint, deploy, fallback, runbook, or on-call handling.
3. Capture the evidence fields before writing prose.
   If any of `official source`, `who confirms`, or `what to do this week` is missing, do not publish yet.
4. Write the brief in the fixed order.
   One-line conclusion → what changed → who is affected → what is different → practical impact → what to do now → FAQ → official sources.
5. Add only the share blocks that fit the track.
   Operations defaults: `Leader 5-line`, `Wiki summary`, `This-week checklist`.
   Engineering defaults: `Slack-ready note`, `Runbook memo`, `This-week checklist`.
6. Update site surfaces.
   Add or update the detail brief page, then update [`briefs/index.html`](../briefs/index.html) seed cards, then update [`index.html`](../index.html) if the item belongs in the latest queue.
7. Perform manual QA.
   Confirm all official links resolve, tags match the impact, the evidence block is complete, and the “what to do this week” section is specific.

## Publish checklist
- The title explains a decision or impact, not just a feature.
- The brief links to at least one official source.
- The brief names who is affected.
- The brief contains a fixed “what to do this week” action block.
- The evidence block includes action types and preferred share format.
- The brief includes only the share blocks that make sense for its track.
- The homepage or briefs hub is updated if this is part of the current seed set.

## Current seed set
| Seed | Track | Page | Official authority | First seen via | Preferred share |
|------|------|------|------|------|------|
| Seed 01 | Operations | [`briefs/ops-governance-brief.html`](../briefs/ops-governance-brief.html) | OpenAI deprecations + changelog | official email + docs | leader 5-line / wiki / checklist |
| Seed 02 | Engineering | [`briefs/eng-runbook-brief.html`](../briefs/eng-runbook-brief.html) | OpenAI changelog + Vercel changelog | X link, then official changelog | Slack / runbook / checklist |

## Next seed candidate
- Cursor agent behavior update
  Action types to test: rules file sync, extension version alignment, Slack rollout note.
