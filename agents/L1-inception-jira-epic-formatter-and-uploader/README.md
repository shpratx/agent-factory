# L1-inception-jira-uploader

## Purpose

This agent is the hand-off between inception planning and Jira tooling in the AI-Augmented SDLC. It reads the approved, evaluated Epic set (`L1-epics.json`) and Feature set (`L1-features.json`) from blob storage, flattens both into the shape `tool-L1-jira-upload-epics` requires, invokes that tool exactly once, and returns a uniform status record so the workflow orchestrator and audit logs never need to parse Jira API responses directly.

## What does it do?

- Reads `L1-epics.json` and `L1-features.json` from blob storage via the attached **blob-storage-reader** tool (given `folder_name` + `file_names`) — this is the ONLY accepted ingestion path; no direct input or file upload.
- Validates that **both** upstream documents carry top-level `status: "success"` before doing any further processing — halts immediately with `agent_status: "failed"` if either evaluator did not succeed.
- Validates every extracted epic (non-empty `epic_id`/`title`) and feature (non-empty `feature_id`/`title`, resolvable `epic_id`), dropping and logging anything invalid; deduplicates by ID (first occurrence kept).
- Builds an internal Jira-tool payload — **Epics first, then Features** — with `parentKey` links so every Feature resolves to its owning Epic in a single pass. Descriptions use only strings/arrays of strings (never ADF, HTML, or nested objects — the tool builds ADF internally).
- Runs 6 pre-call payload validation checks (correct top-level keys, non-empty issues, Epic-before-Feature ordering, resolvable parentKeys, string-only description values, correct issue count, no spaces in labels) before ever calling the tool.
- Invokes `tool-L1-jira-upload-epics` **exactly once** — never retries on failure.
- Parses every line of the tool's return text into `created_issues[]` or `failed_issues[]`, or detects a fatal error.
- Reports `agent_status`: `success` (all created), `partial_success` (some created, some failed), or `failed` (validation failed / tool not invoked / fatal error / zero created).
- Never surfaces the internal Jira payload as output — the deliverable is exclusively the status record.

## How does it work?

1. **Ingest** both blob documents via blob-storage-reader.
2. **Validate upstream status** — halt with `agent_status: "failed"` if either is not `"success"`.
3. **Extract** `epics[]`/`features[]` verbatim from each document's `content.items` — never merged or backfilled across sources.
4. **Validate** every epic/feature (required fields, resolvable parent, duplicates) — drop and log violations; halt if zero valid epics remain.
5. **Build** the internal Jira payload (Epics then Features, with parentKey links) — never surfaced as output.
6. **Pre-call validate** the payload against all 6 structural checks; fix any violation before invoking the tool.
7. **Invoke** `tool-L1-jira-upload-epics` exactly once.
8. **Parse** every line of the tool's return into `created_issues[]`/`failed_issues[]`, or detect a fatal error.
9. **Reconcile** counts (`total_created + total_failed == total_expected`) and determine `agent_status`.
10. **Reflect**: self-check against `evaluation.md`'s Reflection Checklist, silently fix bookkeeping issues, and log findings/resolutions.
11. **Emit** the final status AgentOutput plus a plain-text `execution_summary`.

## Input

- **Source:** `blob_storage` ONLY — via the attached blob-storage-reader tool. This agent does NOT accept `direct_input` or `file_upload`.
- **Required:** `folder_name` — blob storage folder containing `L1-epics.json` and `L1-features.json`.
- **Optional:** `projectKey` — Jira project key passed through to the tool payload; omitted entirely from the payload if not supplied.

## Output

- **Type:** `jira_upload_status` — returned directly as this agent's deliverable (this agent does NOT write to blob storage).
- **Envelope note:** This agent's top-level envelope intentionally differs from the other 3 pipeline agents — it carries `input_summary` (source, `source_agent_ids`, `parameters`) instead of a top-level `status` enum, and reports its own outcome via `content.items.agent_status` instead. This is the confirmed real-world shape for this specific agent.
- **Items:** `agent_status` (success/partial_success/failed), `tool_call` (tool_name/invoked/success), `jira_space` (base_url/project_key/project_url), `issue_counts` (epics_expected/features_expected/total_expected/total_created/total_failed), `created_issues[]` (logical_id/jira_key/issue_type/summary/url), `failed_issues[]` (summary/error).
- **Summary:** `execution_summary` — plain-text bullets covering status, counts, project URL, sample created keys, key mapping decisions, reflection findings, guardrails, and any failed-issue detail verbatim.
- **Knowledge Bases:** `kb-epics-best-practices` (v1.1) and `kb-features-best-practices` (v1.1), attached at runtime for context when validating extracted Epic/Feature structure.
- **Tools:** `blob-storage-reader` (fetch L1-epics.json/L1-features.json), `tool-L1-jira-upload-epics` (create Jira issues, invoked exactly once, never retried) — both attached at runtime.

## Composition

```
agents/L1-inception-jira-uploader/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-success.json
│   ├── output-01-success.json
│   ├── input-02-upstream-failed.json
│   └── output-02-upstream-failed.json
└── golden/v1.0.0/
    ├── input-golden-01-partial-success.json
    ├── golden-01-partial-success.json
    ├── input-golden-02-upstream-failed.json
    └── golden-02-upstream-failed.json

prompts/L1-inception-jira-uploader/
└── instructions.md
```
