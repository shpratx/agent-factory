# Evaluation Framework — Guardrails & Workflow

---

## Guardrails

Configure all 5 guardrails on the Evaluator + Improver agent.

---

### Guardrail 1 — JSON Enforcer

**Purpose:** All tool outputs must be valid JSON. Never let a parse failure
block the entire pipeline.

**Rules:**
```
On any LLM tool call that returns unparseable JSON:
  → Retry once with this suffix appended to the prompt:
    "Return valid JSON only. No prose, no markdown, no backticks.
     Start your response with { and end with }"
  → If second attempt also fails:
    → Return { "error": true, "metric": null } for that metric
    → Continue pipeline with remaining metrics
    → Flag that metric as "unavailable" in the final report
    → Never block the whole evaluation for one metric failure
```

---

### Guardrail 2 — Token Cap

**Purpose:** Prevent runaway token usage on any single call.

**Rules:**
```
llm_judge calls:
  max_tokens: 800

faithfulness_checker calls:
  max_tokens: 1000

Improver calls:
  max_tokens: 1200

If platform allows per-call token limits, set them directly on each tool.
If not, enforce via prompt suffix:
  "Be concise. Your response must not exceed 800 tokens."
```

---

### Guardrail 3 — Loop Breaker

**Purpose:** Hard stop on improvement iterations to prevent infinite loops.

**Rules:**
```
Track iteration count in workflow state variable: improvementCount
Initialize: improvementCount = 0
On each improvement attempt: improvementCount += 1

IF improvementCount >= 3:
  → Stop loop immediately
  → Return the best scoring version seen across all iterations
  → Add to report: "Maximum improvement iterations reached.
                    Best version returned (iteration N, score X)"
  → Do not call Improver again regardless of score
```

---

### Guardrail 4 — Score Regression Check

**Purpose:** Stop improving if the output is getting worse.

**Rules:**
```
Before each new improvement iteration:
  Compare currentScore vs previousScore

  IF currentScore < previousScore:
    → Stop loop immediately
    → Return previousIteration.improvedOutput (not current)
    → Add to report: "Improvement stopped: score regressed
                      from {previousScore} to {currentScore}"

  IF currentScore == previousScore for 2 consecutive iterations:
    → Stop loop
    → Return current output
    → Add to report: "Improvement stopped: no score change detected"
```

---

### Guardrail 5 — Input Truncation

**Purpose:** Prevent oversized inputs from burning tokens on long documents.

**Rules:**
```
Source Document > 2000 words:
  → Pass only: first 1000 words + last 500 words
  → Add separator: "--- [middle section truncated] ---"
  → Apply only to faithfulness_checker (only tool that receives source)

Agent Output > 1000 words:
  → Pass only first 500 words to llm_judge
  → Pass full output to similarity_checker (pure code, no token cost)

Ground Truth > 500 words:
  → Pass only first 300 words to llm_judge

Truncation note:
  Always truncate from the middle, never from the end.
  First and last sections carry the most signal.
```

---

## Workflow — `evaluation_pipeline`

Configure this as a workflow in your app with the following steps and gates.

---

### Step 1 — Receive Input
```
Variables to initialize:
  source          ← source document (string)
  output          ← agent output (string)
  groundTruth     ← ground truth (string)
  taskType        ← Summary | QA | RAG | General | Code
  improvementCount ← 0
  bestScore       ← 0
  bestOutput      ← output
  iterationHistory ← []
```

Apply Guardrail 5 truncation to source and output before passing anywhere.

---

### Step 2 — similarity_checker (always runs)
```
Input:  output, groundTruth
Output: similarityResult
Cost:   0 tokens

Store: similarityResult.similarityScore
```

---

### Step 3 — Decision Gate A (similarity-based routing)
```
IF similarityResult.similarityScore > 0.85:
  → Skip Step 4 (faithfulness)
  → Go to Step 5 (llm_judge) with confidence mode flag

ELSE IF similarityResult.similarityScore < 0.40:
  → Skip Step 4 and Step 5
  → Go directly to Step 7 (Improver)
  → Set primaryFailureReason: "Output too dissimilar to ground truth"

ELSE:
  → Go to Step 4
```

---

### Step 4 — faithfulness_checker (conditional)
```
Input:  output, source (truncated per Guardrail 5)
Output: faithfulnessResult
Cost:   1 LLM call (~600 tokens)

Store: faithfulnessResult.hallucinationRate
       faithfulnessResult.faithfulnessScore
       faithfulnessResult.claims
       faithfulnessResult.attributions
```

**Decision Gate B (hallucination-based routing)**
```
IF faithfulnessResult.hallucinationRate > 0.5:
  → Skip Step 5 (llm_judge)
  → Go to Step 6 (score aggregation) then Step 7 (Improver)
  → Log: "Skipped llm_judge — hallucination rate too high"
```

---

### Step 5 — llm_judge (conditional)
```
Input:  output, groundTruth, taskType
        failedDimensions (only on re-evaluation iterations)
Output: judgeResult
Cost:   1 LLM call (~800 tokens)

Store: judgeResult (all dimensions + verdict + instructions)
```

---

### Step 6 — Score Aggregation (pure code, no LLM)
```
Compute using KB weights:
  llmJudgeScore     (from judgeResult, 0 if skipped)
  faithfulnessScore (from faithfulnessResult, 0 if skipped)
  similarityScore   (from similarityResult, always present)
  overallScore      (weighted combination per KB)

Determine verdict:
  PASS if overallScore >= 70 AND hallucinationRate == 0
  FAIL otherwise

Update bestScore and bestOutput if overallScore > bestScore
```

---

### Step 7 — Verdict Gate
```
IF verdict == PASS:
  → Go to Step 9 (Final Report)

IF verdict == FAIL:
  → IF improvementCount >= 3:
      → Apply Guardrail 3 (return best version, stop)
      → Go to Step 9 with best version
  → ELSE:
      → Go to Step 8 (Improver)
```

---

### Step 8 — Improver (non-happy path only)
```
improvementCount += 1

Build failure report:
  primaryFailureReason  ← from judgeResult or similarity gate
  failedDimensions      ← dimensions scoring < 60
  hallucinatedClaims    ← from faithfulnessResult.claims where supported=false
  missingContent        ← derived from groundTruth vs output comparison
  improvementInstructions ← from judgeResult

Call platform LLM with Improver prompt (from agent instructions doc)
  max_tokens: 1200

Store improved output as: improvedOutput

Re-run ONLY failed tools:
  IF similarityScore was the cause → re-run similarity_checker
  IF faithfulness was the cause    → re-run faithfulness_checker
  IF judge dimensions failed       → re-run llm_judge with failedDimensions

Apply Guardrail 4 (regression check) before accepting new score

Append to iterationHistory:
  { iterationNumber, failureReport, improvedOutput, scoreAfter, verdictAfter }

→ Go back to Step 6
```

---

### Step 9 — Final Report
```
Return:
  verdict:          PASS | FAIL
  happyPath:        bool
  overallScore:     float
  llmJudgeScore:    float
  faithfulnessScore: float
  similarityScore:  float
  judgeDetails:     all 5 dimensions with scores + justifications
  faithfulnessDetails: claims table + attribution map
  similarityDetails: BLEU, ROUGE, Cosine, Token F1, Exact Match
  hallucinatedClaims: list (empty if none)
  improvementTriggered: bool
  iterationHistory: array (empty if happy path)
  finalOutput:      best version of the output
  improvementInstructions: string (shown even on PASS as suggestions)
```

---

## Workflow Variable State Shape

```json
{
  "source": "string",
  "output": "string",
  "groundTruth": "string",
  "taskType": "string",
  "improvementCount": 0,
  "bestScore": 0.0,
  "bestOutput": "string",
  "iterationHistory": [],
  "similarityResult": {},
  "faithfulnessResult": {},
  "judgeResult": {},
  "overallScore": 0.0,
  "verdict": "PASS | FAIL",
  "happyPath": false
}
```

---

## Token Budget Summary

| Step | Tool | LLM Call | Est. Tokens |
|---|---|---|---|
| Step 2 | similarity_checker | No | 0 |
| Step 4 | faithfulness_checker | Yes | ~600 |
| Step 5 | llm_judge | Yes | ~800 |
| Step 8 | Improver (per iteration) | Yes | ~600 |
| Step 8 | Re-evaluation (per iteration) | Yes | ~400 |

| Scenario | Total Tokens |
|---|---|
| Happy path — easy (similarity only + judge) | ~800 |
| Happy path — normal (all tools) | ~1,400 |
| Non-happy — 1 iteration | ~2,400 |
| Non-happy — 3 iterations (worst case) | ~4,600 |
