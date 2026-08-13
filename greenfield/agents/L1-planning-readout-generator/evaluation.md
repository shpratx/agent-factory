# Evaluation — L1-planning-readout-generator

Basic self-check only. Full completeness/consistency re-derivation is delegated to the
sibling evaluator, `L1-planning-readout-generator-evaluator` (built separately), which
retrieves readout.md from `agent_output.storage.readout_md_url` for deep scoring.

## Quality Gates
- [ ] readout.md contains all required sections (Exec Summary, Requirements, Impact,
      Dependencies & Sequencing, Assumptions/Constraints/Risks/Open Questions,
      External Dependencies, Flags & Data Quality)
- [ ] `dependency_graph_status` is set, and if `cyclic` or `unresolved` the ⚠️ warning
      callout is present in Section 4
- [ ] No FR, CI row, component row, assumption, constraint, risk, open question,
      external dependency, or flag was dropped during carry-forward
- [ ] No new risk, assumption, constraint, finding, or dependency edge/node appears
      that isn't traceable to one of the three source documents

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Every carried-forward item matches its source document's content and framing |
| Hallucination | ≤ 0.05 | No invented risk, assumption, CI touch, or dependency edge |
| Consistency | 0.95 | Readout contradicts none of prd.md / impact-assessment.md / dependency-graph.mmd |
| Completeness (basic) | 0.90 | Every FR / row / bullet from the sources appears somewhere in the readout |
| Executive Summary grounding | 1.00 | Every claim in the Exec Summary traces to a line in a section below it |

## Reflection Checklist
- [ ] Every FR-NNN in prd.md appears in Section 2 with its full NFR table intact
- [ ] Every row of impact-assessment.md's Components Identified table appears in Section 3
- [ ] The embedded `.mmd` block and the derived sequencing table agree with each other and
      introduce no edge/node absent from dependency-graph.mmd
- [ ] Every item in prd.md's Assumptions/Constraints/Risks/Open Questions appears in
      Section 5 with the same FR tagging
- [ ] Every external dependency and every flag from impact-assessment.md appears in
      Sections 6–7 (Section 7 explicitly states "None" if impact-assessment.md flagged none)
- [ ] Executive Summary introduces no claim absent from the sections below it, and was
      written last
- [ ] Any source unavailable across all three input channels is stated explicitly in its
      section(s) ("Not available — {{document}} not yet generated") and reflected in
      `sources_available` — the run still completed, not hard-failed
- [ ] `agent_output` fields (`requirement_ids`, `blast_radius_rollup`,
      `dependency_graph_status`, `open_question_count`, `flags_present`) match what's
      actually in readout.md — no drift between the document and its own index
- [ ] No field in `agent_output` contains narrative/prose text — it is a pure structural
      index, never a copy of readout.md content
- [ ] `agent_output` itself was not written to blob storage — only readout.md is a blob artifact

## Reflection Process
1. Generate readout.md → 2. Walk every item in the Reflection Checklist against it →
3. Fix silently (re-derive `agent_output` fields from the corrected document, never the
reverse) → 4. Deliver final readout.md + agent_output + execution_summary only — no
interim output.
