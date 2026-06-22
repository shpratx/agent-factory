# L1-inception-vision-generator

## Purpose

Converts a product idea into a comprehensive, industry-grade vision document by conducting market research within a functional domain whose knowledge is provided as a knowledge base. The generated document is uploaded as a markdown artifact to Azure Blob Storage.

## What does it do?

- Accepts a product idea (text) and domain knowledge base
- Generates a 5-section vision document following the standard structure:
  1. Executive Summary
  2. Business Context (problem, drivers, users, constraints, metrics)
  3. Full Scope Vision (vision statement, feature areas, integrations, journeys, roadmap)
  4. MVP Scope (objective, criteria, in/out scope, journeys, constraints, DoD)
  5. Risks and Dependencies (risks, dependencies, open questions)
- Grounds all content in the domain KB (users, regulations, terminology, business rules)
- Uploads the markdown file to Azure Blob Storage at `/<execution-id>/vision-doc/`
- Returns standard AgentOutput with artifact location

## How does it work?

1. Ingest the idea and validate it has enough substance to generate a vision
2. Query the domain KB for: target users, business rules, regulations, terminology, integrations
3. Generate the vision document following the template structure
4. Ground every feature area, user type, constraint, and risk in domain context
5. Separate full vision from MVP scope with explicit in/out boundaries
6. Reflect against evaluation.md criteria (specificity, grounding, no vague language)
7. Upload the final markdown to Azure Blob Storage
8. Return AgentOutput with artifact location and document summary

## Input

- **Source:** direct_input or agent_output
- **Required:** `idea` — text description of the product idea
- **Optional:** `product_name` — preferred name (derived if not provided)
- **Optional:** `target_market` — market segment hint
- **Optional:** `constraints` — known business constraints

## Output

- **Type:** `vision_document`
- **Items:** product_name, document_summary (section/feature/risk counts), artifact (location, filename, blob_path)
- **Metadata:** domain_kb_used, confidence, grounding_coverage
- **Artifact:** Markdown file at `/<execution-id>/vision-doc/vision-<product-name>.md`
- **Summary:** Plain text bullet points of what was produced, key decisions, and reflection findings

## Composition

```
agents/L1-inception-vision-generator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── vision-document-template.md
├── README.md
├── examples/
│   ├── input-01-calculator-api.json
│   └── output-01-calculator-api.json
└── golden/v1.0.0/

prompts/L1-inception-vision-generator/
└── instructions.md
```

## Tools Used

- `tool-L1-azure-blob-upload` — uploads the generated markdown to Azure Blob Storage

## Downstream

The vision document feeds into:
- `L1-inception-requirements-extractor` — extracts FRs, NFRs, constraints from the vision doc
- Human review for stakeholder alignment
