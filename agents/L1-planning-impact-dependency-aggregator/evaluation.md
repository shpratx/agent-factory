# Evaluation — L1-planning-impact-dependency-aggregator

This is the aggregator's own basic self-check only. This agent performs no analysis — it is a
verbatim pass-through concatenation. The quality of the source artifacts is the responsibility
of L1-planning-impact-dependency-mapper and its independent evaluators.

## Quality Gates
- [ ] Both source artifacts (L1-impact-assessment.md and L1-dependency-graph.mmd) were
      retrieved in full and are non-empty
- [ ] Product name in the Impact Assessment header is consistent with the nodes referenced in
      the Mermaid diagram
- [ ] The combined document contains the Impact Assessment content first, a horizontal rule
      separator, a "## Dependency Graph" heading, then the Mermaid content in a fenced code block
- [ ] No content was added, removed, reworded, or reordered from either source artifact
- [ ] The Mermaid content is inside a properly fenced ```mermaid code block
- [ ] The blob storage write succeeded and blob_storage_url is recorded in the artifact

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 1.00 | Combined document is byte-for-byte identical to source content (no edits) |
| Hallucination | ≤ 0.00 | No content invented or added beyond the separator and heading |
| Consistency | 1.00 | Source artifacts are reproduced verbatim, in order |
| Completeness | 1.00 | Both source artifacts appear in full, nothing omitted |

## Reflection Checklist
- [ ] Both reader tool calls succeeded
- [ ] Writer tool call succeeded and blob_storage_url recorded
- [ ] No interim output printed — only the final result

## Reflection Process
1. Retrieve both source artifacts → 2. Validate both present and non-empty → 3. Concatenate
verbatim → 4. Self-check (no additions/omissions) → 5. Save → 6. Deliver final output only.
Do NOT print interim output.
