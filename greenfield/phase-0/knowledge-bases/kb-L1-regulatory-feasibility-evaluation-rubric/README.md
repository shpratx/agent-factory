# kb-L1-regulatory-feasibility-evaluation-rubric

**Domain covered:** None specific — this is not a regulatory-domain KB. It's
the evaluation rubric for `L1-vision-regulatory-feasibility-checker`,
exposed as a knowledge base rather than being read directly off disk.

**Why it exists:** `L1-vision-regulatory-feasibility-checker-evaluator`
scores the checker's output against this rubric every run. Previously the
rubric (`evaluation.md`) was wired in via a direct file `ref:` in the
evaluator's spec.yaml; this KB carries the same content instead, so it's
retrieved the same way as the evaluator's other runtime context (a KB
query) rather than a bespoke file reference.

**Source of truth:** `L1-vision-regulatory-feasibility-checker/evaluation.md`.
This KB is a runtime copy of that file's content, not an independent fork —
whenever evaluation.md changes (a Quality Gate, a score threshold, the
Reflection Checklist), update `content/evaluation-rubric.md` here to match
in the same change.

**Update frequency:** Whenever evaluation.md changes; reviewed quarterly
otherwise, in step with the checker/evaluator pair's own review cadence.

**Quality bar:** Content here must be an exact match for evaluation.md —
no summarizing, no rephrasing the thresholds. Drift between the two is a
defect, not a style choice.

**Owner:** Agentic-AI CoE

**Consumers:** `L1-vision-regulatory-feasibility-checker-evaluator`
