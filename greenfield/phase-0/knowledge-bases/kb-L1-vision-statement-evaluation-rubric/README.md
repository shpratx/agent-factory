# kb-L1-vision-statement-evaluation-rubric

**Domain covered:** None specific — this is not a domain KB. It's the
evaluation rubric for `L1-vision-statement-generator`, exposed as a
knowledge base rather than being read directly off disk.

**Why it exists:** `L1-vision-statement-generator-evaluator` scores the
generator's output against this rubric every run. Carrying the rubric as a
KB means it's retrieved the same way as the evaluator's other runtime
context (a KB query) rather than via a bespoke file `ref:` in the
evaluator's spec.yaml.

**Source of truth:** `L1-vision-statement-generator/evaluation.md`. This KB
is a runtime copy of that file's content, not an independent fork —
whenever evaluation.md changes (a Quality Gate, a score threshold, the
Reflection Checklist), update `content/evaluation-rubric.md` here to match
in the same change.

**Update frequency:** Whenever evaluation.md changes; reviewed quarterly
otherwise, in step with the generator/evaluator pair's own review cadence.

**Quality bar:** Content here must be an exact match for evaluation.md —
no summarizing, no rephrasing the thresholds. Drift between the two is a
defect, not a style choice. The Reconciliation BLOCKER and the 0.95
consistency threshold in particular must be carried verbatim; they are the
strictest gates in Phase 0.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-vision-statement-generator-evaluator`
