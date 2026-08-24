<!--
EXAMPLE OUTPUT — illustrative content generated to demonstrate Phase 0's document
chain end-to-end. Regulatory framework names (Reg. (EC) 852/2004, Reg. (EC)
178/2002, Natasha's Law, UK GDPR) are real UK/retained-EU frameworks referenced
for realism; the specific classifications and mitigations below are an
illustrative worked example, not verified legal advice. A real assessment
requires actual legal review before any funding or build decision.
-->

# Regulatory Feasibility Assessment: HarvestLink — Compliance-Enabled Producer-to-Foodservice Marketplace

| Field | Value |
|---|---|
| Source idea brief | `idea-brief.json` (idea-brief-2026-08-02-002) |
| Target geography | United Kingdom |
| Generated | 2026-08-02 |
| Viability score | 6.0/10 |

## ✅ Feasibility Summary
**Overall status:** Amber
One constraint below (Food Business Operator status) is individually Red,
but has a standard, structurally-precedented mitigation (facilitation-only
platform design) that other UK marketplace/SaaS platforms routinely use to
avoid taking on a regulated-activity status they aren't built for. No
constraint is left unmitigated, so overall program feasibility is Amber,
not Red.

## ✅ Constraints Assessed

### Food Business Operator (FBO) Status — Red
**Regulation:** Regulation (EC) 852/2004 (retained UK law), Regulation (EC)
178/2002 (General Food Law)
**Rationale:** If HarvestLink takes possession, repackages, or relabels
food — rather than only facilitating data and matching between producers,
distributors, and buyers — it becomes an FBO itself, triggering
registration/approval obligations and inspection exposure far beyond a
software platform's typical remit.
**Mitigation:** Platform must operate strictly as a data/matching and
documentation layer. Producers and distributors remain the FBOs for every
trade; HarvestLink never takes physical possession, title, or custody of
food.

### Traceability Record Integrity — Amber
**Regulation:** Regulation (EC) 178/2002, Article 18 ("one step back, one
step forward")
**Rationale:** Traceability records created on HarvestLink will be relied
upon by foodservice buyers and potentially by enforcement bodies during a
recall — the platform cannot be a passive form-filler; records need
integrity guarantees designed deliberately, not assumed.
**Mitigation:** Require producer *and* distributor dual sign-off on every
traceability record, with an immutable, append-only audit log.

### Allergen Declaration Liability — Amber
**Regulation:** Food Information (Amendment) (England) Regulations 2019
("Natasha's Law"); Food Information Regulations 2014 / EU FIC Regulation
1169/2011
**Rationale:** If HarvestLink auto-generates or edits an allergen
declaration without producer attestation, liability for an incorrect
declaration could shift toward HarvestLink as a technology provider rather
than staying with the FBO who is legally responsible for the food.
**Mitigation:** Allergen declarations must always be producer-attested and
signed off before being finalised on-platform; HarvestLink is documentation
infrastructure, not the legal declarant.

### Data Protection — Green
**Regulation:** UK GDPR / Data Protection Act 2018
**Rationale:** Standard obligation for any platform handling producer and
buyer business data; not a feasibility blocker on its own.
**Mitigation:** Not required for feasibility; carried forward as an ongoing
design and monitoring requirement rather than a launch blocker.

## ✅ Categories Assessed and Not Applicable
- **Financial crime (AML/KYC) and payments authorisation** — contract value
  settles directly between producer and buyer; the platform never holds or
  moves funds.
- **International data transfer and residency** — UK-only producers, buyers
  and hosting at this scope; no transfer arises.
- **Automated decision-making and AI obligations** — matching surfaces
  candidates for human selection; no decision is made about an individual.
- **Consumer protection and unfair trading** — both sides are businesses; no
  consumer contracts are formed on the platform.
- **Sector-specific safety regimes beyond food** — no workplace, medicines,
  telecoms, energy or nuclear activity is carried on.
- **Employment and worker classification** — the platform coordinates
  contracts between businesses, not people's work.
- **Accessibility** — assessed; standard WCAG-aligned design discharges the
  duty for a B2B interface, so no separate constraint is raised.
- **Sanctions and export control** — domestic UK trade only at this scope;
  reassess if export is added.
- **Age-restricted or conditional supply** — no age-restricted category is in
  scope; would need reassessment if alcohol were added.

## ✅ Viability Score
**Score:** 6.0/10 — `human_review_required` against the
`qg-L1-viability-score` threshold of 7

| Component | Weight | Score | Traced to |
|---|---|---|---|
| Regulatory posture | 0.60 | 6.0 | CON-01, CON-02, CON-03, CON-04 |
| Idea clarity | 0.40 | 9.0 | `idea-brief.json`: problem_statement, target_geography, product_category |

**Weighted before caps:** 7.2
**Caps applied:** `red_constraint` → 6.0, triggered by CON-01 (Food Business
Operator status). A Red constraint caps the score below the gate even when it
carries a precedented mitigation — the mitigation is a plan, not a resolution.
**What would raise the score:** confirming the facilitation-only boundary with
qualified counsel so CON-01 can be reclassified below Red. That single change
releases the cap and lifts both the component and the final score.

<!--
Note the shape of this result: an idea can be well-formed and commercially
sensible (idea clarity 9.0) and still route to human review, because the
binding term is regulatory and a cap is a ceiling, never an average. This is
the outcome the scoring model exists to produce — not an edge case.
-->

## Open Items
- None currently flagged "requires legal review" — every Amber/Red item
  above has a concrete, precedented mitigation. This assessment should
  still be confirmed by qualified legal counsel before the facilitation-only
  structure is finalised, since the FBO-status boundary is a matter of fact
  and degree, not a bright line.

---
*Generated by `L1-vision-regulatory-feasibility-checker` · execution_id: `exec-f08c4b3a` · workflow_execution_id: `wf-a17c5e92`*
