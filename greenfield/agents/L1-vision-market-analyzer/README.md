# L1-vision-market-analyzer

## Purpose

No idea should reach a funding decision without knowing who else is already
solving this problem. This agent makes that check mandatory, grounded, and
consistent — instead of an ad hoc "someone should Google this" step that
gets skipped under time pressure.

## What does it do?

Accepts the problem statement and target users from `L1-vision-idea-intake`
and produces:
- A competitor matrix (name, positioning, strengths, weaknesses), every row
  citing a real source
- A SWOT analysis, every item traceable to a specific competitor entry or
  idea-brief fact
- An honest data-sufficiency verdict — if coverage is genuinely thin, it says
  so rather than padding the matrix to look complete

## How does it work?

1. Ingests `problem_statement` and `target_users` from the upstream agent's output
2. Queries `kb-L2-domain-market` for relevant distribution-channel
   and player-category facts
3. Issues `tool-L1-web-search-competitor-scan` queries for anything more
   current than the KB's last review
4. Builds the competitor matrix — every entry cited, no exceptions
5. Derives SWOT items, each pointing back to a specific competitor or fact
6. Assesses data sufficiency honestly; self-checks citation completeness
   before returning (full scoring delegated to
   `L1-vision-market-analyzer-evaluator`, per S6)

## Input

- **Source:** agent_output from `L1-vision-idea-intake`
- **Required:** `problem_statement`, `target_users[]`
- **Optional:** `known_competitor_list` — candidates the requester already has in mind

## Output

- **Type:** `market_analysis`
- **Items:** `competitor_matrix[]`, `swot` (strengths/weaknesses/opportunities/threats),
  `data_sufficiency` — see `output_schema.json`
- **Artifacts:** `market-analysis.md`
- **Metadata:** competitor entries carry `citation` (source + retrieved_date) —
  this is a BLOCKER guardrail (`gr-L1-citation-verifier`), not advisory; SWOT
  items carry `reasoning` pointing to their origin
- **Summary:** competitor/SWOT counts, search queries run, KB content used,
  guardrail results, data-sufficiency verdict

## Composition

```
agents/L1-vision-market-analyzer/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-internal-tool.json
│   ├── output-01-internal-tool.json
│   ├── input-02-thin-coverage.json
│   └── output-02-thin-coverage.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-thin-coverage.json
    └── golden-02-thin-coverage.json

prompts/L1-vision-market-analyzer/
└── instructions.md
```
