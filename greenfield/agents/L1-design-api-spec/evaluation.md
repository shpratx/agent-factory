# Evaluation — L1-design-api-spec

> **No evaluator agent, by design.** Unlike every Phase 1 sibling, this agent
> has no `L1-design-api-spec-evaluator` and the workflow sets
> `quality_gate: null`. The prompt's Reflection block is therefore the only
> gate standing between this artifact and its five downstream consumers
> (`L1-design-hld`, `L1-design-lld`, `L1-testing-script-generator`,
> `L1-construction-api-code-generator`, `L1-construction-ui-code-generator`).
> These gates are the self-check's own checklist, not a downstream scorer's.

## Quality Gates
- [ ] The FR-NNN sets in `requirements.md` and `nfr-spec.md` were compared — same ids, same order — before any endpoint was derived; a mismatch halted with `INSUFFICIENT_CONTEXT` rather than producing a partial contract *(this replaces the zero-drop guarantee `L1-requirements-prd-composer` used to provide)*
- [ ] Every endpoint carries >=1 `FR-NNN` in `fr_trace` — no orphan endpoint, however obviously useful (no unmotivated health check, admin console, or bulk export)
- [ ] Every FR in `requirements.md` has exactly one `fr_coverage` entry, same id and order — none dropped, none merged, none reordered. An FR with no endpoint is `non_api` with a specific rationale drawn from its own statement, never a generic "not applicable"
- [ ] No TBD boundary condition appears anywhere in the contract as a concrete value; every TBD has an `x-open-question` in `openapi.yaml` **and** a matching `open_questions[]` entry whose `spec_location` points at it — a question recorded only in `items` is invisible to the five agents that read the YAML
- [ ] Every non-TBD contract detail that reads as a decision (auth scheme, rate limit, error shape, retention window, availability tier) cites `nfr-spec.md § FR-NNN`, `kb-L1-enterprise-security § ES<n>`, or `kb-L1-enterprise-architecture § EA<n>` in `nfr_trace` — never a plausible default
- [ ] Every external-facing `securityScheme` uses a group-approved external IdP and **never** Azure AD (ES1); every compliance-relevant write is tied to an authenticated, non-shared identity; no limit or gate is client-bypassable
- [ ] Every service is published through the group API Gateway (EA2/EA4); no point-to-point integration, no write-back to SMDS, no SAP ERP surface at all (EA3)
- [ ] API rules stated outright in an FR's own statement are honoured — an "immutable, append-only" FR yields no `PUT`/`DELETE` on that resource; a "never takes possession/title" FR yields no endpoint implying the platform is a transacting party
- [ ] `openapi.yaml` parses as valid OpenAPI 3.1: every `$ref` resolves, every required field present, every `operationId` unique, one shared `Problem` schema `$ref`'d rather than re-declared per operation
- [ ] REST conventions from `instructions.md` applied uniformly — `/v1/` prefix, plural kebab-case resources, camelCase fields and operationIds, cursor pagination on every collection GET, RFC 9457 `problem+json` on every non-2xx, `Idempotency-Key` on every compliance-relevant creating POST

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every endpoint and schema field derives from a real `requirements.md` statement or `nfr-spec.md` boundary condition |
| Hallucination | <= 0.10 | No endpoint, schema, field, enum, limit, or SLA figure present that no cited source supports |
| Consistency | 0.90 | `fr_trace` / `fr_coverage` agree in both directions; no two operations contradict on auth, error shape, or pagination |
| Relevance | 0.85 | Usable as-is by all five downstream consumers without re-deriving the endpoint surface |
| Reasoning quality | 0.80 | Every `reasoning` explains why the resource/method shape follows from the FR's verbatim statement and why each NFR condition landed where it did |
| Citation completeness | 0.95 | Every `nfr_trace` entry carries a specific, checkable source |
| OpenAPI validity | 1.00 | Structurally valid 3.1 — binary, `hard_fail_on: invalid_openapi_syntax` per the workflow |

## Reflection Checklist
- [ ] Endpoint derivation read each FR's **verbatim** `statement`, not its title or a gloss of it
- [ ] No boundary condition was reworded on the way into `nfr_trace` — TBDs carry the literal "TBD — needs stakeholder input" phrasing through
- [ ] `applied_as` is `open_question` for every TBD and for no non-TBD condition (schema-enforced; self-check confirms none slipped through)
- [ ] No boundary condition was recorded in `nfr_trace` that changed nothing in the contract, and no contract detail exists with nothing behind it
- [ ] Where `hld_output` was supplied: every `API-NN` and every path is accounted for in `hld_reconciliation`, and every disagreement carries an `open_question_id` rather than a silent pick
- [ ] The FR-link for any HLD-seeded endpoint came from `requirements.md`, never from the HLD's `F-XX.X` `implements_features` — the two id vocabularies are not interchangeable

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
