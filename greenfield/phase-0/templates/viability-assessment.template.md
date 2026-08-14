<!--
TEMPLATE: viability-assessment.md — PHASE 0'S THREE ANALYSES, WHOLE, WITH THE SCORE
Produced by: L1-vision-viability-scorer — artifact only, does NOT publish itself
Owns: qg-L1-viability-score (min_score 7, blocking)
Consumes: idea-brief.md + market-analysis.md + regulatory-feasibility.md (full documents)
Consumed by: L1-vision-statement-generator (receives viability_score as an input parameter
             and must never compute it), and the Product Lead at gate-vision-approval

Required sections marked ✅. Sections 1-4 are authored by the scorer. Sections 5-7 are the
three source documents carried through IN FULL and VERBATIM — no summarising, no trimming,
no correcting. The only permitted change is demoting each document's headings one level so
they nest under their container heading.

The point of carrying them whole: the human at the approval gate reads exactly the text the
score was derived from, in its own words, rather than a condensation written by the agent
that scored it.
-->

# Viability Assessment: {{product_name}}

| Field | Value |
|-------|-------|
| Viability score | **{{viability_score}} / 10** |
| Threshold (qg-L1-viability-score) | 7 |
| Recommendation | {{auto_publish_eligible \| human_review_required}} |
| Weighted score before caps | {{weighted_score}} |
| Capped | {{yes — see Caps Applied \| no}} |
| Workflow execution | {{workflow_execution_id}} |
| Assessed | {{date}} |

## ✅ 1. Verdict

{{One paragraph: what the score means for this idea, in plain language. If a cap fired,
say which unresolved item caused it and what would have to change. Never soften a
below-threshold score — the workflow routes it to a human, which is the correct outcome,
not a failure to explain away.}}

## ✅ 2. Component Scores

| # | Component | Weight | Score | Confidence | Traced to |
|---|-----------|--------|-------|------------|-----------|
| VC-01 | Regulatory posture | 0.40 | {{score}} | {{confidence}} | {{CON ids}} |
| VC-02 | Market opportunity | 0.35 | {{score}} | {{confidence}} | {{SWOT / competitor ids}} |
| VC-03 | Idea clarity | 0.25 | {{score}} | {{confidence}} | {{sections}} |

{{One short paragraph per component explaining the score against its band. Cite the ids in
the embedded documents below, so a reader can scroll down and check the claim. A thin
source document lowers confidence, never the score.}}

## ✅ 3. Caps Applied

{{A table of every cap that fired, or "None — the weighted score stands."}}

| Rule | Cap | Triggered by | Reason |
|------|-----|--------------|--------|
| {{red_constraint}} | 6.0 | {{CON-NN}} | {{≤20 words}} |

{{A cap is a ceiling, not an average. An unresolved regulatory blocker holds the score
below the threshold however strong the market case is — that is the rule working, not a
scoring artefact.}}

## ✅ 4. What Would Raise This Score

{{Concrete, ordered by leverage: the specific constraint that needs a recorded mitigation
or a legal determination, the market claim that needs a source, the user segment that
needs defining. Each item names what changes and which component it lifts. Omit anything
that would require softening a finding rather than resolving it.}}

---

# Source Documents

*The three analyses below are reproduced in full and unaltered, exactly as read from
{{upload \| blob storage}}. They are the evidence for sections 1-4.*

## ✅ 5. idea-brief.md

*Source: {{upload \| blob storage}} · Produced by L1-vision-idea-intake*

{{THE ENTIRE idea-brief.md, VERBATIM. Headings demoted one level; nothing else changed.}}

---

## ✅ 6. market-analysis.md

*Source: {{upload \| blob storage}} · Produced by L1-vision-market-analyzer*

{{THE ENTIRE market-analysis.md, VERBATIM. Headings demoted one level; nothing else
changed. If this document was absent, state "Not available — missing-input cap applied"
here and leave the section otherwise empty.}}

---

## ✅ 7. regulatory-feasibility.md

*Source: {{upload \| blob storage}} · Produced by L1-vision-regulatory-feasibility-checker*

{{THE ENTIRE regulatory-feasibility.md, VERBATIM. Headings demoted one level; nothing else
changed. A constraint you scored low is carried through in its own words, uncorrected.}}

---
*Produced by L1-vision-viability-scorer. This document is an artifact only — it does not
publish itself, and the score is reported, not enforced. Auto-publish is the workflow's
decision at qg-L1-viability-score.*
