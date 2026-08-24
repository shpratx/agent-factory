# L1-design-api-spec

> **Status: design doc only.** No `spec.yaml`, `output_schema.json`,
> `prompts/instructions.md`, `examples/`, or `golden/` fixtures exist yet.
> This file records the design so a future session (or another contributor)
> can build the scaffold without re-deriving these decisions.

## Purpose

Phase 4 (Design) needs one authoritative API contract before HLD, LLD, test
scripts, and both code generators can run — five downstream agents key off
this artifact (`L1-design-hld`, `L1-design-lld`,
`L1-testing-script-generator`, `L1-construction-api-code-generator`,
`L1-construction-ui-code-generator`), more than any other single artifact in
the pipeline. Getting the endpoint surface and NFR-driven contract details
(auth, rate limits, error envelopes) right here means they don't have to be
re-derived or guessed downstream.

## Why input changed from the original wiring

`greenfield/workflows/L1-WF-greenfield-idea-to-pr.yaml` wires this agent's
input as `stories.json` (from `L1-inception-story-generator`) +
`nfr-spec.md`. Phase 3 (Inception: epic-creator → feature-decomposer →
story-generator → task-generator) is not built and is owned by others, so
`stories.json` has no real producer yet — and task-generator isn't a
substitute, since task-generator's own input *is* `stories.json` (it sits
downstream of story-generator, not beside it). Feeding tasks in would also
invert the dependency: the API contract belongs *above* work breakdown, not
below it — tasks like "implement `POST /listings`" have already assumed the
endpoint shape this agent exists to derive.

**Decision: `requirements.md` + `nfr-spec.md`.** `L1-requirements-prd-composer`
is not part of this pipeline, so `prd.md` is unavailable. The substitute is
the two documents the PRD was composing *from*, taken directly — both built,
both carrying everything this agent needs:

- `requirements.md` (`L1-requirements-elicitor`) —
  `functional_requirements[]` with `FR-NNN` id, **full verbatim** `statement`
  (its own output schema guarantees the exact wording is preserved for
  downstream derivation, not a gloss), and `traces_to`
- `nfr-spec.md` (`L1-requirements-nfr-classifier`) — per-FR boundary
  conditions across six categories, same FR ids and same order, each cited
  to a real source or marked `TBD`

**What dropping the PRD costs.** Two things, both small:

1. *The zero-drop composition guarantee.* The PRD composer's own gate
   verified no FR or boundary condition was lost between elicitation and
   downstream. That check now has to live here: this agent must confirm the
   `FR-NNN` sets in `requirements.md` and `nfr-spec.md` align before
   deriving anything. `nfr-spec.md`'s schema already mandates same-ids-
   same-order, so it's a cheap assertion, not new analysis.
2. *Assumptions / Constraints / Risks condensed from `vision.md`.* Mostly
   redundant here — the regulatory constraints that actually shape an API
   contract arrive anyway through `nfr-spec.md`'s Compliance boundary
   conditions, which cite `regulatory-feasibility.md § <constraint>`
   directly. Add `vision.md` as a read-only third input only if a concrete
   gap shows up in practice.

When story-generator exists, re-open this decision — story-level acceptance
criteria would sharpen endpoint derivation, but requirements remain the
authoritative capability source either way.

## What does it do?

Accepts `requirements.md` (from `L1-requirements-elicitor`) and
`nfr-spec.md` (from `L1-requirements-nfr-classifier`) and produces
`openapi.yaml`:
- One or more resources/endpoints per FR-NNN, traceable back to the FR that
  motivated them
- Request/response schemas derived from each FR's described data
- Auth, rate-limit, and error-handling shape driven by the FR's NFR
  boundary conditions (e.g. a Security boundary condition becomes a
  `securitySchemes` entry; a Performance boundary condition becomes a
  documented SLA note, not a runtime enforcement)
- Every new HarvestLink service published through the group API Gateway
  (Kong), per `kb-L1-enterprise-architecture` EA2/EA4/EA10 — no
  point-to-point integration, no direct write-back to legacy systems
  (SMDS, SAP ERP) per EA3

It does not invent endpoints with no FR trace, and does not resolve a TBD
NFR boundary condition into a concrete number — a TBD stays a documented gap
in the spec (e.g. an `x-open-question` extension field), not a guessed value.

## How does it work? (proposed)

1. Validate `requirements_output` and `nfr_spec_output` are present with
   `status: success` — fail fast (`INSUFFICIENT_CONTEXT`) otherwise
2. Assert the two inputs agree: the `FR-NNN` set in
   `nfr_spec_output.nfr_classifications[]` must match
   `requirements_output.functional_requirements[]`, same ids and same order
   (the classifier's schema already mandates this). A mismatch means one
   upstream agent drifted — halt rather than derive from a partial set.
   *This check replaces the zero-drop guarantee the PRD composer used to
   provide.*
3. Walk `functional_requirements[]`; for each FR-NNN, read its **verbatim**
   `statement` and identify the resource(s)/action(s) it implies
4. Attach each FR's NFR boundary conditions from `nfr-spec.md` to the
   relevant part of the contract (security scheme, rate limit doc note,
   error response shape) — TBD conditions become flagged open questions,
   never a fabricated default
5. Apply `kb-L1-enterprise-architecture` constraints: Gateway-published,
   independently deployable, no legacy point-to-point calls
6. Self-check: every FR-NNN maps to at least one endpoint (or is explicitly
   noted as non-API, e.g. a UI-only FR); every endpoint traces back to a
   real FR-NNN — no orphans either direction
7. Emit `openapi.yaml` (valid OpenAPI 3.x) plus structured `items` mirroring
   the same facts in queryable form

## Input (proposed)

- **Source:** agent_output
- **Required:** `requirements_output` (from `L1-requirements-elicitor`,
  `status: success`), `nfr_spec_output` (from
  `L1-requirements-nfr-classifier`, `status: success`)
- **Optional / later:** `vision_output` (read-only) — only if
  Assumptions/Constraints/Risks turn out to shape the contract in a way
  `nfr-spec.md`'s Compliance conditions don't already cover
- **Future:** re-add `stories_output` from `L1-inception-story-generator`
  once it exists; requirements stay the authoritative capability source
  either way

## Output (proposed)

- **Type:** `api_spec`
- **Artifact:** `openapi.yaml` — valid OpenAPI 3.x
- **Items:** per-endpoint entries carrying `fr_trace` (which FR-NNN(s)
  motivated it), `nfr_trace` (which boundary conditions shaped auth/rate
  limit/error handling), `confidence`, `reasoning` — same
  citation-discipline pattern as `L1-requirements-elicitor` and
  `L1-requirements-nfr-classifier`
- **Summary:** endpoint count, FR coverage (any FR with zero endpoints and
  why), open questions carried from TBD NFR boundary conditions, guardrail
  results

## Knowledge bases

Two, both already built.

| Source | Status | Role |
|---|---|---|
| `kb-L1-enterprise-security` | **Exists** | Most of the contract's security surface, already written: external users need a separate IdP and must never use Azure AD (ES1); every action ties to a non-shared identity, no limit client-bypassable (ES1); what counts as Confidential (ES2); 6-year compliance retention held distinct from GDPR erasure (ES3); availability tier per endpoint group (ES4); vetting logged even when approved (ES7) |
| `kb-L1-enterprise-architecture` | **Exists** | Gateway-first integration rule (EA2/EA4), no legacy point-to-point or write-back to SMDS/SAP ERP (EA3), service domain boundaries (EA5), EA review triggers (EA10) |
| REST conventions | **Prompt embed, not a KB** | Versioning strategy, casing/pluralisation, pagination, error envelope, idempotency headers. Domain-agnostic and purely structural, so S4 says embed in `instructions.md` — same call already made for `requirements.template.md`. It also can't be written yet: without the org's own API style guide and Kong plugin config, any content would be invented rather than documented |

### Why there is no food-domain KB

`kb-L2-food-domain-api-patterns` was planned, then dropped. A food
vocabulary KB — GTIN product identity, batch/lot code formats, the EU FIC
14-allergen enum, temperature-chain units, catch-weight — is exercised by
**zero** HarvestLink requirements. HarvestLink is a compliance and
facilitation platform: FR-006 states it never takes possession, title or
custody, so there is no custody chain to model and no cold-chain telemetry
to represent.

FR-004 is the trap — it says "allergen," but it governs the *declaration
workflow* (producer attestation, sign-off), not the allergen *content*.
The contract needs `declarationId`, `attestedBy`, `signedOffAt`, `status`.
It never needs to know what an allergen is.

What the contract genuinely needs comes from the requirements themselves,
not a KB:

- What a compliance-documentation completeness score is and how it's
  bounded (FR-002/FR-005/FR-009) — from `requirements.md`, or an open
  question if genuinely undefined
- FR-003's "immutable, append-only" forbids `PUT` and `DELETE` on
  traceability records — an API rule read straight off the FR
- FR-006 forbids any endpoint implying HarvestLink is a transacting party
  — a constraint on the whole surface

Shipping with only the two L1 KBs matches the call
`L1-requirements-prd-composer` made when it shipped with an empty KB list.
If HarvestLink later grows a real product catalogue with SKUs and
cold-chain tracking, the vocabulary need appears then — building for it now
would be speculative.

**Rule for any KB added later:** every bullet must change the emitted
`openapi.yaml` — a field type, an enum, a constraint, a required property.
If it doesn't, it doesn't belong. Same quality bar
`kb-L1-enterprise-architecture` sets for itself.

## Guardrails

- Default chain: `gr-L1-output-schema-validator`, `gr-L1-hallucination-check`
  (no endpoint/schema invented beyond `requirements.md`/`nfr-spec.md`),
  `gr-L1-consistency-check` (no FR silently dropped from the endpoint
  surface)
- **Naming mismatch to resolve first:** the workflow file's always-on chain
  names `gr-L1-hallucination-check` and `gr-L1-consistency-check`, but the
  repo has `gr-L3-hallucination-detector` and `gr-L3-consistency-checker` —
  different layer, different name. Build L1 versions or re-point the
  workflow, otherwise two thirds of the chain silently never runs.
- Additional (per workflow.yaml): `gr-L1-schema-validator-openapi` —
  **does not exist yet**. Would check the emitted YAML is structurally
  valid OpenAPI (all `$ref`s resolve, required fields present) with
  `hard_fail_on: invalid_openapi_syntax`, two-file AAVA shape (`config.yml`
  + `.co`), self-check input+output rails, `yes` = block
- No evaluator agent, no quality-gate-on-evaluator pattern — confirmed as
  intentional, matching the workflow file (`quality_gate: null`), unlike
  every Phase 1 sibling agent

## Composition (once built)

```
agents/L1-design-api-spec/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md                    ← this file
├── examples/
│   ├── input-01-typical.json
│   └── output-01-typical.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    └── golden-01-harvestlink.json

prompts/L1-design-api-spec/
└── instructions.md

guardrails/gr-L1-schema-validator-openapi/   ← separate build, not yet started
├── config.yml
└── gr-L1-schema-validator-openapi.co
```

## Open items before this can move past design doc status

1. Build `spec.yaml` + `output_schema.json` + `prompts/instructions.md`
   against the `requirements.md` + `nfr-spec.md` input contract above,
   with the REST conventions embedded per S4
2. Build `gr-L1-schema-validator-openapi` guardrail
3. Source the organisation's API style guide and Kong plugin configuration
   — without them the REST conventions embed would be invented, not
   documented
4. Golden fixtures on the HarvestLink scenario, matching the convention the
   Phase 0 and Phase 1 agents use
5. When `L1-inception-story-generator` lands, re-open the input-contract
   decision above
