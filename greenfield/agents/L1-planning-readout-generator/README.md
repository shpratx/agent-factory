# L1-planning-readout-generator

## Purpose

`L1-planning-readout-generator` is the terminal agent of Phase 1
(Requirements → Impact Assessment → Dependency Graph). It exists so a PM or
stakeholder never has to open `prd.md`, `impact-assessment.md`, and
`dependency-graph.mmd` separately to understand a program: it composes all
three into one standalone document — `readout.md` — that a human can read
top to bottom and fully understand what's being built, what it touches, how
it sequences, and what's still open. It is a **synthesis agent**, not an
extraction or analysis agent (same class as `L1-requirements-prd-composer`):
it carries content forward, it never re-scores, re-classifies, or invents.

## What does it do?

- Resolves its three inputs (`prd.md`, `impact-assessment.md`,
  `dependency-graph.mmd`) via whichever channel actually supplies them —
  direct input, file upload, or a blob storage tool call — never combining
  or borrowing content across channels.
- Carries forward, verbatim:
  - every `FR-NNN` and its full NFR boundary-condition table (from `prd.md`)
  - the existing-system touch table and Components Identified table (from
    `impact-assessment.md`), rolling up blast radius counts
  - the dependency graph itself (embedded as a mermaid block) plus a derived
    plain-language sequencing table — never inventing an edge or node
  - Assumptions, Constraints, Risks, and Open Questions (from `prd.md`)
  - External Dependencies and Flags & Data Quality (from
    `impact-assessment.md`)
- Writes the Executive Summary **last**, once every other section is final,
  so it can never introduce a claim the rest of the document doesn't support.
- Degrades gracefully, never hard-fails: if a source document is genuinely
  unavailable, the corresponding section says so explicitly instead of being
  silently dropped or fabricated.
- Never suppresses a cyclic or unresolved dependency graph — it still
  renders the graph, with a prominent warning callout attached.
- Saves the finished document to blob storage as `readout.md`, then returns
  a compact, purely structural `agent_output` JSON index (never the document
  itself) so Phase 2 agents can route/gate — e.g. halt on
  `dependency_graph_status: "cyclic"` — without re-parsing markdown.

## How does it work?

1. Resolve all three source documents via the Input Protocol; mark any that
   are genuinely unavailable.
2. Build Section 2 (Requirements) as a full, uncondensed carry-forward from
   `prd.md`.
3. Build Section 3 (Impact) as a full carry-forward from
   `impact-assessment.md`; compute `blast_radius_rollup` from the
   Components Identified table.
4. Build Section 4 (Dependencies & Sequencing) by embedding
   `dependency-graph.mmd` verbatim, then deriving the sequencing table from
   that same graph; set `dependency_graph_status` and add the warning
   callout if the graph was flagged cyclic/unresolved upstream (or is
   unavailable).
5. Build Section 5 (Assumptions/Constraints/Risks/Open Questions) as a
   verbatim, fragmented carry-forward from `prd.md`; count Open Questions.
6. Build Sections 6–7 (External Dependencies, Flags & Data Quality) as
   verbatim carry-forwards from `impact-assessment.md`.
7. Write the Executive Summary last, as a synthesis of the sections above.
8. Save `readout.md` to blob storage.
9. Run the basic self-check (see `evaluation.md`), then print `agent_output`
   followed by a plain-text `execution_summary`.

## Input

- **Source:** direct input, file upload, or tool call (blob storage reader)
  — see the Input Protocol in `prompts/L1-planning-readout-generator/instructions.md`.
- **Required:** none unconditionally — each of the three source documents
  is resolved independently, and a genuinely missing one degrades to a
  "Not available" section rather than failing the run.
- **Optional:** `prd`, `impact_assessment`, `dependency_graph_mmd` (direct-input
  text) and `folder_name` (blob storage folder for the tool-call channel).

## Output

- **Type:** `readout.md` (blob storage artifact, the authoritative document)
  plus `agent_output` (JSON, printed directly — never written to blob).
- **agent_output:** a purely structural meta-point index — ids, an enum
  (`dependency_graph_status`), counts, and booleans — never a copy of
  `readout.md`'s prose. See `output_schema.json`.
- **Summary:** a plain-text `execution_summary` (bullet points, not JSON)
  appended after `agent_output`, covering what was produced, which sources
  were available, self-check results, tools invoked, guardrails evaluated,
  the blob storage location, and any gaps flagged.

## Composition

```
agents/L1-planning-readout-generator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-password-reset.json
│   ├── output-01-password-reset.json
│   ├── input-02-missing-dependency-graph.json
│   └── output-02-missing-dependency-graph.json
└── golden/v1.0.0/
    ├── input-golden-01-loyalty-points-redemption.json
    ├── golden-01-loyalty-points-redemption.json
    ├── input-golden-02-cyclic-pricing-engine.json
    └── golden-02-cyclic-pricing-engine.json

prompts/L1-planning-readout-generator/
└── instructions.md
```
