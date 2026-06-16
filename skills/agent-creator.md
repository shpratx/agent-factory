---
name: agent-creator
description: Standard structure, patterns, and conventions for creating agents in the Agent Factory. Use this whenever asked to create a new agent — apply this exact structure, naming, prompt format, and quality patterns.
trigger: When the user asks to create a new agent, build an agent, implement an agent, or asks about agent structure and standards.
---

# Agent Creator Skill

## Naming Convention

```
L{layer}-{phase}-{function}-agent
```

- `L1` = Enterprise (generic, works for any domain)
- `L2` = Domain/LOB (domain-specific, extends L1)
- `L3` = Project/Initiative (project-specific, extends L2)
- `L4` = Squad/Local (team-specific, extends L3)
- `{phase}` = SDLC phase: inception | design | construction | testing | deployment
- `{function}` = kebab-case description of what the agent does

Examples:
- `L1-inception-requirements-extractor-agent`
- `L1-inception-epics-generator-agent`
- `L2-payments-inception-story-generator-agent`

## File Structure (mandatory for every agent)

```
agents/{agent-name}/
├── spec.yaml                 # Agent specification (purpose, contract, guardrails, quality)
├── evaluation.md             # Quality rubric, scoring thresholds, reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── README.md                 # Purpose, what it does, how it works, composition, I/O summary
├── examples/                 # Input/output pairs (minimum 2: happy path + edge case)
│   ├── input-01-{name}.json
│   ├── output-01-{name}.json
│   ├── input-02-{name}.json
│   └── output-02-{name}.json
└── golden/v{version}/        # Production-grade benchmark responses
    ├── input-golden-01-{name}.json    # Detailed realistic input
    ├── golden-01-{name}.json          # Full expected output + evaluation criteria
    ├── input-golden-02-{name}.json    # Edge case / failure input
    └── golden-02-{name}.json          # Correct failure handling output

prompts/{agent-name}/
└── instructions.md           # Agent prompt (Role/Goal/BackStory/Instructions/Output)
```

## spec.yaml Template

```yaml
# Agent Specification Document
spec_version: "1.0"
artifact_type: agent
metadata:
  name: {agent-name}
  version: "1.0.0"
  layer: L{n}
  phase: {phase}
  owner: agentic-ai-coe
  created: {date}

purpose:
  description: "{what this agent does in one sentence}"
  input: "{what it accepts}"
  output: "{what it produces}"
  business_value: "{why it exists — what problem it solves}"

prompt:
  ref: "prompts/{agent-name}/instructions.md"
  version: "1.0.0"
  description: "{brief description of what the prompt does}"

contract:
  input_schema: "$ref: schemas/agent-input-contract-schema.json"
  output_schema: "$ref: schemas/agent-output-schema.json"

  input:
    accepts_from_agents: [{upstream-agent} | any]
    accepts_direct_input: true
    accepts_file_upload:
      enabled: true|false
      formats: [".md", ".txt", ".json", ".pdf"]
    required_parameters:
      {param}: {type: string, description: "{description}"}
    optional_parameters:
      {param}: {type: string, default: "{value}", description: "{description}"}

  output:
    $ref: "output_schema.json"

context:
  knowledge_bases:
    - kb-L1-enterprise-architecture
  guardrails:
    - gr-L1-output-schema-validator
    - gr-L1-pii-detection
    - gr-L3-hallucination-detector
    - gr-L3-citation-validator
    - gr-L3-consistency-checker

quality:
  evaluation_ref: "evaluation.md"
  min_score: 7.0
  hallucination_check: true
  consistency_check: true

versioning:
  input_version: "1.0"
  output_version: "1.0"
  instruction_hash: "sha256:pending"
```

## Prompt Template (instructions.md)

The prompt MUST follow this exact structure:

```
ROLE:
  You are a {role title} specialising in {expertise}.

GOAL:
  {Clear objective statement}
  
  Success criteria:
  - {criterion 1}
  - {criterion 2}
  - {criterion 3}

BACK STORY:
  {Context about why this agent exists, where it sits in the pipeline}
  
  Domain context:
  - {relevant domain knowledge}
  
  Upstream: {what feeds into this agent}
  Downstream: {what consumes this agent's output}

INSTRUCTIONS:

  Input Ingestion:
  - Source: {direct_input | agent_output | file_upload}
  - Extract: {what to extract from the input}
  - Validate: {validation rules — reject if invalid}

  Processing Rules:
  1. {step 1}
  2. {step 2}
  3. {step 3}
  ...

  Rules:
  - {rule 1}
  - {rule 2}

  Don'ts:
  - Do NOT {prohibition 1}
  - Do NOT {prohibition 2}
  - Do NOT print interim reflection output — only deliver final result

  Examples:
  Refer to examples/ folder for input/output pairs.
  Golden responses in golden/v1.0.0/ for benchmark quality.

  Example 1 (typical):
    Input: {example input}
    Output: {example output with reasoning}

  Example 2 (edge case):
    Input: {edge case input}
    Output: {correct handling}

  Evaluation Instructions:
  Refer to evaluation.md for the full quality rubric, scoring thresholds, 
  and reflection checklist. Key rules:
  - Grounding: Every output item must trace to specific input content.
  - Citations: Every item must cite the exact source phrase or ID.
  - Reasoning: Every item must explain the decision logic.
  - Validation: Self-check IDs, required fields, enums, and counts.
  - Reflection: After generating initial output, you MUST:
    1. Log internally: "[REFLECTING] Checking output against evaluation.md criteria"
    2. Review against every item in the Reflection Checklist
    3. Identify gaps, inconsistencies, or missed items
    4. Log findings: "[REFLECTING] Found: <issue>"
    5. Fix each issue silently — amend the output
    6. Log resolution: "[REFLECTING] Resolved: <what was fixed>"
    7. Only deliver the final, corrected output
    Do NOT print interim output, reflection logs, or draft versions.

  Summary:
  - Append a plain-text execution_summary after the structured output:
    • What was produced (item counts, types)
    • Key decisions made
    • What reflection found and changed
    • Gaps or issues flagged
  - Do NOT print interim reasoning or corrections.
  - Summary is plain text bullet points, NOT JSON.

EXPECTED OUTPUT:
  Format: JSON (AgentOutput standard)
  output.type: "{type}"

  Schema:
  {full schema showing structure with placeholders}
```

## evaluation.md Template

```markdown
# Evaluation Criteria — {agent-name}

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| {rule 1} | {threshold} | Automated: {how} |
| {rule 2} | {threshold} | Automated: {how} |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every item traces to input |
| Hallucination | ≤ 0.10 | No invented content |
| Consistency | ≥ 0.90 | No contradictions |
| Relevance | ≥ 0.85 | Output is actionable |
| Reasoning quality | ≥ 0.80 | Decisions explained |
| Citation completeness | ≥ 0.95 | Every item cites source |

## Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| {dimension 1} | {excellent} | {good} | {fair} | {poor} |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] {check 1}
- [ ] {check 2}
- [ ] {check 3}

## Reflection Process (mandatory)

1. **Generate** initial output following processing rules
2. **Log** `[REFLECTING] Checking output against evaluation criteria`
3. **Check** every item in the Reflection Checklist above
4. **Identify** gaps, errors, inconsistencies, or missed items
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** each issue — amend the output silently
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final corrected output

Reflection findings appear in execution_summary but interim output is never shown.
```

## README.md Template

```markdown
# {agent-name}

## Purpose

{Why this agent exists — one paragraph}

## What does it do?

{Detailed explanation of what it accepts and produces, with bullet lists}

## How does it work?

{Numbered steps showing the processing pipeline}

## Input

- **Source:** {source types}
- **Required:** {parameter} — {description}
- **Optional:** {parameter} — {description}

## Output

- **Type:** {output type}
- **Items:** {what the items contain}
- **Metadata:** {what metadata is included}
- **Summary:** {what the execution summary covers}

## Composition

{File tree showing actual folder structure}
```

## Golden Response Requirements

Golden responses MUST be:
- **Production-grade** — full, detailed, realistic outputs (not stubs or summaries)
- **Paired with inputs** — each golden has a corresponding `input-golden-XX.json`
- **Include evaluation criteria** — what scores/checks this golden should pass
- **Cover happy path AND failure** — at least one valid + one insufficient/empty input
- **Demonstrate reflection** — execution_summary mentions what reflection found and fixed

## output_schema.json Requirements

- Must be valid JSON Schema (draft 2020-12)
- Must validate against the golden output without errors
- Must use `$defs` for reusable types (ItemMetadata, Citation)
- Must enforce ID patterns via regex
- Must require `execution_summary` as string (not JSON)
- Must match the metadata structure used in the prompt (consistent `metadata` wrapper)

## Key Patterns to Always Follow

1. **Every item has metadata** — confidence, reasoning, citation, trajectory in a `metadata` wrapper
2. **execution_summary is plain text** — bullet points, NOT JSON object
3. **Reflection is mandatory** — agent must reflect, find issues, fix silently, deliver final
4. **IDs are sequential** — FR-01, FR-02... / EP-01, EP-02... / US-001, US-002...
5. **Citations trace to input** — exact phrase or ID from the source
6. **Confidence is self-assessed** — 0.9+ explicit, 0.7-0.8 inferred, <0.7 uncertain
7. **Don'ts section is mandatory** — explicit prohibitions prevent common failures
8. **Input validation first** — reject empty/gibberish before processing
9. **evaluation.md referenced from spec AND prompt** — single source of truth
10. **Golden inputs are detailed and realistic** — not one-liners
11. **Enterprise architecture adherence** — agents must verify output against EA KB during reflection
12. **Prompts should be concise** — delegate detail to evaluation.md, avoid duplicating rules in prompt and evaluation
13. **output_schema.json must match actual output** — validate golden against schema, fix mismatches immediately
14. **Feature IDs use F-{epic}.{seq}** format (e.g., F-01.1, F-02.3) — not FEAT-XX-XX
15. **Story IDs use US-XXX** format (e.g., US-001) — not STORY-XX-XX
16. **Epic IDs use EP-XX** format (e.g., EP-01) — not EPIC-XX

## Agent Pipeline Chain Pattern

When creating agents that form a pipeline, ensure:
- `accepts_from_agents` in spec points to the upstream agent
- Input parameters match what the upstream agent produces
- Output type flows logically (requirements → epics → stories)
- Each agent's prompt documents Upstream/Downstream in Back Story
- ID formats are consistent across the chain (F-XX.X in epics, referenced in stories)

## Output Schema Alignment Rules

- Schema `$defs` must describe every nested type with descriptions on all fields
- Schema must accommodate all fields found in the actual output (validate golden against schema)
- If output uses `items` as an object (not array), schema must reflect that
- Required fields in schema must match what the prompt's EXPECTED OUTPUT shows
- Run golden through schema validation before finalising

## Prompt Optimisation Rules

- Keep prompts concise — under 150 lines where possible
- Delegate evaluation detail to evaluation.md (don't duplicate rubrics in prompt)
- Evaluation section in prompt should reference evaluation.md and list only key principles
- Examples should be brief (1-3 lines showing pattern, not full JSON)
- EXPECTED OUTPUT schema shows structure with placeholders, not full examples

## Knowledge Base References

- Spec must list all KBs the agent needs under `context.knowledge_bases`
- Include enterprise architecture KB for agents that generate code or architecture
- Include domain KB (L2) for domain-specific agents
- Include best practices KB relevant to the output type (story-best-practices, epics-best-practices)
- Prompt should mention KBs are "attached at runtime" — agent doesn't fetch them

## Sprint/Delivery Structure (for Epics Generator)

When decomposing into epics:
- Structure for 4 x 2-week sprints (production-deployable at each sprint end)
- Sprint 1: Foundation (auth, design system, data models)
- Sprint 2: Core flows (primary capabilities)
- Sprint 3: Value-add (secondary capabilities)
- Sprint 4: Polish & cross-cutting (error handling, resilience)
- Include `sprint_allocation`, `nfr_mapping`, `traceability_matrix`, `coverage_matrix` in output
- Epics must be business capabilities (not technical layers)

## INSUFFICIENT_CONTEXT Pattern

When input is empty, gibberish, or too vague to process:
- Return the standard AgentOutput structure with empty items arrays
- Add a single gap explaining what's missing and what question to ask
- execution_summary must state "INSUFFICIENT_CONTEXT" with reason
- Never hallucinate output from vague input — fail gracefully

```json
{
  "output": {
    "type": "{type}",
    "schema_version": "1.0",
    "items": { "category_1": [], "category_2": [] },
    "execution_summary": "• Produced 0 items — INSUFFICIENT_CONTEXT.\n• Input too vague to extract actionable content.\n• Suggested: ask stakeholder for more detail."
  }
}
```

## Guardrails Selection Guide

| Agent Type | Mandatory Guardrails |
|-----------|---------------------|
| All agents (L1+) | gr-L1-output-schema-validator, gr-L1-pii-detection |
| Content generators | + gr-L3-hallucination-detector, gr-L3-citation-validator, gr-L3-consistency-checker |
| Code generators | + gr-L1-secrets-protection, gr-L3-hallucination-detector |
| Agents with tool access | + gr-L2-tool-permissions, gr-L3-agent-rate-limit |
| Agents with memory | + gr-L2-memory-safety |
| Domain-specific (L2+) | + gr-L2-policy-enforcement |
| Payments domain | + gr-L2-payments-compliance |

## Examples Requirements

Minimum 2 input/output pairs:
1. **Happy path** — realistic, detailed input producing full output
2. **Edge case** — empty, vague, or boundary input showing graceful handling

Each example must:
- Be valid JSON matching the contract schema
- Show complete AgentOutput structure (not partial)
- Include metadata (confidence, reasoning, citation, trajectory) on all items
- Include execution_summary as plain text

## Shared Schemas

Agents reference shared schemas at the repository level:
- `schemas/agent-input-contract-schema.json` — standard input contract
- `schemas/agent-output-schema.json` — standard AgentOutput envelope

The agent-specific `output_schema.json` defines the items structure unique to that agent, nested within the standard AgentOutput envelope.

## Versioning Rules

| Change | Version Bump | Action |
|--------|-------------|--------|
| Prompt wording tweak (same behaviour) | Patch (1.0.0 → 1.0.1) | Update instruction_hash |
| New output field added (backward compatible) | Minor (1.0.0 → 1.1.0) | New golden set in golden/v1.1.0/ |
| Output structure change (breaking) | Major (1.0.0 → 2.0.0) | New golden set, update output_schema.json |
| New guardrail added | No version bump | Update spec.yaml guardrails list |
| KB added/removed | No version bump | Update spec.yaml context |
