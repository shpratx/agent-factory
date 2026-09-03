# Schreiber Foods Inc. — Jira Epic Best Practices & Standard Operating Procedure (SOP)

**Document Owner:** Agile Program Management Office (PMO) / Enterprise Solutions Architecture
**Applies To:** All Product, Engineering, QA, and IT Delivery Teams
**Status:** Approved — Mandatory Standard
**Version:** 1.1 (adds §2.5 PRD-to-Epic Cardinality Rule)
**Related Source Document:** Standard Product Requirements Document (PRD) Template

---

## 1. Purpose of a Schreiber Foods Epic

An Epic in Jira is a **strategic container**, not a technical execution document. Its sole function is to answer two questions for any reader — plant leadership, product stakeholders, or a new engineer — in under 60 seconds:

- **What** business or manufacturing capability are we delivering?
- **Why** does it matter to Schreiber Foods (cost, compliance, throughput, customer service, food safety)?

An Epic must **never** attempt to answer **"How"**. The "How" belongs downstream — in Stories, Tasks, Sub-tasks, technical design docs, and Confluence engineering pages.

> **Guiding Principle:** If a reader has to scroll more than one screen or parse a technical diagram to understand the business intent of the Epic, the Epic has failed its purpose.

An Epic that is overloaded with implementation detail creates four organizational risks:
1. It becomes stale the moment implementation details change, eroding trust in Jira as a source of truth.
2. It buries the business justification that Plant Ops, Finance, and Compliance stakeholders rely on.
3. It duplicates content that already lives (and should only live) in the PRD or Confluence, creating conflicting versions of the truth.
4. It slows down sprint planning and portfolio reviews because Epics stop being scannable.

---

## 2. Input Filtering Rules — What to Extract From the PRD

When converting an approved PRD into a Jira Epic, the author (or AI-assisted drafting agent) must pull **only** from the four sections below, and only at the level of abstraction described.

### 2.1 Executive Summary → Epic Summary & User Value Statement

- Compress the Executive Summary into a **single-sentence Epic Summary** (used as the Jira title) and a **3–5 sentence User Value Statement** in the Epic description.
- The Value Statement must answer: *Who benefits, what capability changes, and what business/manufacturing outcome improves* (e.g., reduced changeover time, improved lot traceability, faster order-to-cash).
- Strip all narrative color, background history, and stakeholder quotes — retain only the distilled business intent.

### 2.2 Requirements → Macro Feature Pillars Only

- Do not transcribe individual requirements. Instead, **roll requirements up into 3–6 macro feature pillars** (capability groupings) that will each likely become one or more child Stories or a linked sub-Epic.
- Test for correct altitude: a macro pillar should be describable in 5–8 words (e.g., "Automated Lot Genealogy Capture," "SAP Batch Record Sync").
- If a "requirement" cannot be shortened to a capability-level phrase without losing meaning, it is too granular for the Epic — defer it to the Story layer.

### 2.3 Out of Scope → Strict Project Boundaries

- Carry the Out of Scope section forward **verbatim in intent, condensed in language**, as a short bullet list under an **"Out of Scope"** subsection of the Epic.
- This list exists to prevent scope creep during sprint planning and PI Planning — it is a boundary fence, not a discussion.
- Limit to 3–6 bullets. If Out of Scope in the PRD is longer, summarize into categories (e.g., "Excludes integration with legacy Trenton plant MES") rather than listing every excluded item.

### 2.4 Constraints → High-Level Operating Constraints Only

- Extract only constraints that materially bound the solution space at a strategic level, such as:
  - ERP/SAP version limitations or module boundaries (e.g., "Must operate within existing SAP S/4HANA batch management module — no custom Z-table development")
  - Plant infrastructure limitations (e.g., "Limited to plants with existing OT/IT network segmentation")
  - Supply chain or production calendar timelines (e.g., "Cannot deploy during peak cheese production season, June–August")
  - Regulatory or corporate policy boundaries
- Exclude constraints that are technical/implementation-specific (API rate limits, library versions, data schema restrictions) — these belong in Story-level acceptance criteria or technical design docs.

### 2.5 PRD-to-Epic Cardinality Rule — How Many Epics Does One PRD Produce?

*(Addendum — clarifies how a human Product Owner, or an AI-assisted drafting agent, decides Epic count from a single PRD.)*

Determine Epic count in this order, before drafting any Epic content:

1. **Read the Executive Summary first.** If it describes **one cohesive business capability and one business outcome**, default to **1 Epic**.
2. **Roll Requirements into 3–6 macro feature pillars** under that one capability (per §2.2). If they fit comfortably, confirm **1 Epic**.
3. **If pillars would exceed 6** even after honest consolidation:
   - If the pillars still serve the **same business "Why"** (one outcome, one stakeholder group), keep **1 Epic** — flag it as large during backlog grooming rather than splitting artificially.
   - If the pillars clearly serve **genuinely distinct business outcomes or stakeholder groups** (e.g., Quality/Compliance vs. Plant Engineering/Maintenance), split into **multiple Epics** — one per distinct outcome/stakeholder group.
4. **If the Executive Summary itself bundles multiple unrelated initiatives** (e.g., "automate lot genealogy AND overhaul the plant maintenance scheduling system"), this is a **PRD-scoping problem**, not a normal Epic-splitting case:
   - A human Product Owner should first push back and request the PRD be re-scoped into separate PRDs.
   - If forced to proceed from the single PRD as-is, produce **one Epic per distinct initiative**. Each resulting Epic must independently satisfy every Input Filtering (§2), Exclusion (§3), and Risk (§4) rule in this SOP, and each must remain traceable back to the same source PRD.
   - Note the scoping concern directly in the Epic's User Value Statement or Summary context (not as a separate structured field) and recommend the PRD be re-scoped for future changes.
5. **Never create one Epic per individual requirement.** Epics are always capability-level rollups (§2.2). Epic count tracks the number of **distinct business initiatives/outcomes** in the PRD — not the number of requirements, and not the number of macro pillars.

> **Cardinality Filtering Test:** Ask, *"Could this cluster of requirements ship independently and deliver value to a distinct stakeholder group, even if the rest of the PRD were never built?"* If the answer is yes for two different clusters, they are separate Epics. If no, they belong in the same Epic.

---

## 3. Exclusion Rules — What Is Strictly Forbidden in the Epic

The following PRD sections must **never** be copied, summarized, or referenced in detail within the Epic description. Their content is either too granular, too volatile, or intended for a different audience.

| PRD Section | Why It's Forbidden in the Epic | Correct Destination |
|---|---|---|
| **Traceability Matrix** | Requirement-to-test-case mapping is execution-level detail that changes constantly and has no strategic value at the Epic altitude. | Linked Confluence page or test management tool (Zephyr/Xray); referenced from Stories only. |
| **Compound Requirement Split** | This is a decomposition artifact for engineering/QA — it exists specifically to produce Stories, not to live in an Epic. | Directly converted into individual Jira Stories/Tasks. |
| **Open Questions** | Unresolved items signal an incomplete Epic and create false blockers or confusion for stakeholders scanning Jira. | Confluence "Open Items" log or Story-level comments, tracked until resolved. |
| **Assumptions** | Assumptions are working hypotheses for the delivery team, not durable business context. They date quickly and clutter the Epic. | Confluence PRD page or Story description context. |
| **Glossary** | Definitions are reference material, not narrative content, and do not aid scanability. | Linked Confluence Glossary page (org-wide or project-specific), referenced by hyperlink only. |

> **Rule of Thumb:** If a section exists in the PRD to help an engineer **build** or a QA analyst **test**, it does not belong in the Epic. If it exists to help a stakeholder **understand intent and value**, it may belong in the Epic (in condensed form).

---

## 4. Food Safety & Regulatory Risks — The Special Exception

The **Risks** section of the PRD is the one exception where the Epic author must actively filter for a specific risk *category*, not simply summarize everything.

### 4.1 What MUST Be Included

Only risks that meet the **Critical Compliance Threshold** are elevated into the Epic's Risks section:

- FDA regulatory requirements or compliance deadlines (e.g., FSMA 204 traceability rule impacts)
- SQF (Safe Quality Food) audit blockers or certification-impacting risks
- Major food safety system changes (HACCP plan impacts, allergen control, recall/traceability capability gaps)
- USDA or state dairy/food regulatory exposure
- Any risk that could halt production, trigger a recall, or jeopardize a plant's certification status

Each qualifying risk should be written as a single, scannable bullet with severity noted, e.g.:
> ⚠️ **Regulatory:** Delayed lot genealogy capture may impact FSMA 204 traceability compliance readiness (target: Jan 2027).

### 4.2 What MUST Be Excluded

The following must **never** appear in the Epic's Risks section, even if they appear in the PRD's Risks list:

- General technical/engineering bugs or defects
- Developer or end-user training gaps
- Third-party vendor SLA concerns unrelated to compliance
- Resourcing, staffing, or timeline risks not tied to a regulatory outcome
- Any risk that is a normal delivery risk rather than a compliance/food-safety risk

These lower-tier risks belong in the **Risk Register (Confluence)** or as **Story-level blockers/impediments** in Jira, not in the Epic.

> **Filtering Test:** Ask, *"If this risk materializes, does it expose Schreiber Foods to a regulatory finding, audit failure, recall, or plant shutdown?"* If the answer is no, it does not belong in the Epic.

---

## 5. The "Link, Don't Copy" Rule

Jira Epics must remain lightweight and scannable. Any content that is inherently large, visual, or matrix-based must be **hosted externally and linked**, never pasted inline.

### 5.1 Content That Must Always Be Externalized

- Detailed impact assessments
- Plant dependency graphs / network diagrams
- Full compliance or traceability matrices
- Multi-tab requirement decomposition spreadsheets
- Architecture diagrams or data flow maps

### 5.2 Required Linking Format

All external references must use a clean, labeled placeholder — never a raw or unlabeled URL:

```
📎 Impact Assessment: [Confluence — Plant Dependency Analysis](URL)
📎 Compliance Matrix: [Confluence — SQF/FDA Traceability Matrix](URL)
📎 Detailed Requirements: [Confluence — Full PRD](URL)
```

- Every Epic must include a **"Reference Links"** subsection at the bottom of the description containing these placeholders.
- Broken or missing links are treated as an Epic quality defect and should block Epic approval in backlog grooming.

---

## 6. Writing & Formatting Standards

### 6.1 Naming Convention

- Epic titles must be **3–5 words**, Title Case, capability-focused, and free of jargon or ticket-number-style prefixes.
- Format: **`[Capability] + [Object] + [Optional Qualifier]`**
- ✅ Good examples:
  - "Automated Lot Genealogy Capture"
  - "SAP Batch Record Sync"
  - "Plant-Wide Allergen Control Upgrade"
- ❌ Avoid:
  - "Epic for the new traceability thing we discussed in the Q3 planning meeting with plant ops"
  - "Update stuff in SAP"

### 6.2 Description Layout (Mandatory Structure)

Every Epic description must follow this exact scannable structure, using bullets — not paragraphs — wherever possible:

```markdown
## Summary
[1 sentence – business capability]

## User Value Statement
[3–5 sentences – who benefits, what changes, why it matters]

## Macro Feature Pillars
- Pillar 1
- Pillar 2
- Pillar 3

## Out of Scope
- Item 1
- Item 2

## Key Constraints
- Constraint 1
- Constraint 2

## Regulatory & Food Safety Risks
- ⚠️ Risk 1 (severity/deadline if applicable)

## Reference Links
📎 [Label](URL)
📎 [Label](URL)
```

### 6.3 General Formatting Rules

- Use **bold** sparingly — only for risk severity flags and section sub-labels.
- No paragraphs longer than 2 sentences anywhere in the Epic.
- No nested bullets deeper than one level.
- No embedded images, tables, or diagrams — these are matrix/visual content and fall under the Link, Don't Copy rule.
- Epics must be reviewed against this SOP during backlog grooming before being marked "Ready for Refinement."

---

## 7. Quick-Reference Compliance Checklist

Before publishing any Epic, confirm:

- [ ] Title is 3–5 words, capability-focused
- [ ] Summary and User Value Statement are present and concise
- [ ] Requirements are rolled up into macro feature pillars (not individual requirements)
- [ ] Epic count matches the number of distinct business initiatives/outcomes in the PRD (§2.5) — not the number of requirements, and not artificially split or merged
- [ ] Out of Scope boundaries are stated
- [ ] Only high-level (ERP/plant/supply-chain) constraints are listed
- [ ] Risks section contains **only** FDA/SQF/food-safety-critical items
- [ ] No content from Traceability Matrix, Compound Requirement Split, Open Questions, Assumptions, or Glossary appears in the Epic
- [ ] All detailed matrices, dependency graphs, and impact assessments are linked, not pasted
- [ ] Reference Links subsection is present and functional
- [ ] Description follows the mandatory bullet-point layout

---

*This SOP is maintained by the Schreiber Foods Agile PMO. Deviations require sign-off from the Enterprise Solutions Architecture team.*

## Revision History

| Version | Change | Note |
|---|---|---|
| 1.0 | Original SOP | Sections 1–7 as approved |
| 1.1 | Added §2.5 "PRD-to-Epic Cardinality Rule" and a matching checklist item in §7 | Clarifies how many Epics one PRD should produce, including the bundled-unrelated-initiatives edge case |
