# Epic Creation Self-Check — L1-inception-epic-creator

## Grounding Rules (must follow while drafting)

| Rule | Requirement | Check |
|------|-------------|-------|
| Cite every field | Every field written into an epic (title, description, business_value, priority, requirements_used) must trace to a PRD requirement ID, an impact-assessment finding ID, a dependency-graph node ID, or a kb-L1-sdlc-templates convention | Self-check: can I name the exact source for this field? |
| No background-knowledge fill | Never complete a gap using general knowledge not present in prd.md/impact-assessment.md/dependency-graph.json | Self-check: is this claim traceable, or am I inferring it? |
| Unmappable requirement | If a PRD requirement cannot be grounded in an epic, do not force it into one — record it in open_questions with an explanation | Self-check: did I write an epic just to avoid an open question? |

## Epic Definition Rules

| Rule | Requirement | Check |
|------|-------------|-------|
| Business capability, not technical layer | "Split-tender payments at checkout" is an epic; "Payments backend" is not | Self-check: could this title describe a service/component instead of a capability? |
| Title format | <=10 words, verb-first, domain language from the PRD — not generic tech jargon | Self-check: word count and phrasing |
| One delivery phase | Each epic should fit within one delivery phase implied by dependency-graph/PRD | Self-check: does this epic's scope cross a phase boundary? |
| Too large → split candidate | If scope spans more than one delivery phase, or dependency graph implies it can't land in one phase, flag as a split candidate — never silently split or merge | Self-check: is this epic actually two epics wearing one title? |
| Too small → consider merge | If an epic is too small to stand alone, consider merging with a related epic rather than leaving it thin | Self-check: does this epic have enough distinct scope to justify its own entry? |

## Coverage Rules

| Rule | Requirement | Check |
|------|-------------|-------|
| Full PRD coverage | Every FR-NNN/NFR in prd.md MUST appear in at least one epic's requirements_used | Self-check: set comparison — did I walk the full requirement list? |
| No orphan requirement | Any requirement not mapped goes to open_questions with an explanation — never left silently unassigned | Self-check: did every requirement get either an epic or an open question? |
| Dependency-graph node coverage | Every relevant node in dependency-graph.json should resolve to an epic, or be explicitly noted in open_questions if it doesn't map cleanly | Self-check: did I account for every node in scope? |

## Sequencing Rules

| Rule | Requirement | Check |
|------|-------------|-------|
| Dependency-ordered | Epics are ordered using dependency-graph.json edges — foundational (upstream) capabilities first, then dependent (downstream) capabilities | Self-check: does my ordering match a traversal of the graph, or did I order by instinct? |
| No invented ordering | Never sequence epics on assumed priority alone if the dependency graph implies a different order | Self-check: does sequencing conflict with any edge in dependency-graph.json? |

## Priority Rules

| Rule | Requirement | Check |
|------|-------------|-------|
| Trace priority to PRD | Priority is assigned from the PRD's own requirement ordering/priority markers | Self-check: can I point to the exact PRD marker this priority came from? |
| No invented priority | Never assign a priority not traceable to PRD input | Self-check: is this priority a guess or a citation? |

## Quality and Safety Rules

| Rule | Requirement | Check |
|------|-------------|-------|
| Unique, non-overlapping epics | No duplicate or overlapping epics internally | Self-check: title/description similarity scan across my own draft set |
| Sequential, unique IDs | epic_id values follow EPIC-01, EPIC-02... with no duplicates | Self-check: pattern and uniqueness scan |
| No fabricated requirements_used | Every requirements_used entry resolves to real prd.md/impact-assessment.md/dependency-graph.json content | Self-check: does each cited ID actually exist in the input? |
| business_value specificity | Cites a specific PRD requirement or carried-forward vision theme — not a generic statement like "improves the business" | Self-check: would this sentence still make sense if I deleted the requirement it's citing? |
| No PII/sensitive content | Zero PII, credentials, or customer-identifying content in title/description/business_value | Self-check: pattern scan before finalizing |
| Payment-flow classification | Any epic touching payment flows is classified for downstream gr-L2-payments-compliance review | Self-check: does this epic's scope touch payment handling? |
| Impact-assessment folded in | Impact-assessment findings that materially change scope/risk (e.g. high blast-radius flags) are folded into the affected epic's business_value/description, citing the finding ID | Self-check: did I check every relevant finding for material impact? |

## Self-Check Checklist

The agent must self-verify before delivering:

- [ ] Every FR-NNN/NFR from prd.md appears in at least one epic's requirements_used
- [ ] Every epic maps to at least one PRD requirement (no orphan epics)
- [ ] No duplicate or overlapping epics internally
- [ ] Epic sequencing is consistent with dependency-graph.json edges (foundational before dependent)
- [ ] No epic spans more than one delivery phase without an explicit split flag
- [ ] business_value cites a specific PRD requirement or carried-forward vision theme, not a generic statement
- [ ] No PII, credentials, or customer-identifying content in any field
- [ ] Priorities trace to PRD ordering/markers, not invented
- [ ] Every epic touching payment flows is classified for gr-L2-payments-compliance review
- [ ] Every relevant dependency-graph node resolves to an epic or is noted in open_questions
- [ ] Execution summary includes coverage count, sequencing rationale, and open questions

## Reflection Process (mandatory)

The agent MUST perform reflection before delivering output:

1. **Generate** initial epic set following processing rules
2. **Log** `[REFLECTING] Checking output against self-check criteria`
3. **Check** every item in the Self-Check Checklist above
4. **Identify** gaps, ungrounded fields, ordering errors, or missed requirements
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** each issue — amend the output silently
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final corrected output

The reflection findings and resolutions should appear in the execution_summary (what reflection found and changed) but the interim output must never be shown.