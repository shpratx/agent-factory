# L2-schreiber-foods-inception-epic-creator

## Purpose

Creates a strategic, Jira-ready Epic for Schreiber Foods from approved business requirements. It keeps Jira focused on the business capability, value, boundaries, and critical governance concerns.

## What does it do?

- Accepts a requirements document or upstream extracted requirements.
- Uses only the five permitted sections: Executive Summary, Requirements, Out of Scope, Constraints, and Risks.
- Produces a pipeline filename, a 3–5 word Jira Epic Name, and the specified Markdown body.
- Returns `INSUFFICIENT_CONTEXT` when the permitted sections cannot support an Epic.

## How does it work?

1. Validates that meaningful permitted source content exists.
2. Excludes prohibited sections before synthesis.
3. Converts macro capabilities into a strategic Epic container.
4. Carries forward out-of-scope content exactly and distils only critical constraints and risks.
5. Reflects against the Jira governance rubric and emits final structured output.

## Input

- **Source:** direct input, upstream agent output, or file upload.
- **Required:** `requirements_document` — labelled source requirements.
- **Optional:** `domain_component` — approved domain name for the Epic Name.

## Output

- **Type:** `jira_epic`
- **Items:** one or more Jira-ready Epic packages.
- **Metadata:** confidence, reasoning, citations, and source trajectory.
- **Summary:** produced count, filtering decisions, and reflection corrections.

## Composition

```text
agents/L2-schreiber-foods-inception-epic-creator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
└── golden/v1.0.0/
prompts/L2-schreiber-foods-inception-epic-creator/
└── instructions.md
```
