# Evaluation Framework — Knowledge Base (KB)

Attach this document to the Evaluator + Improver agent in your app.
This keeps agent instructions short — the agent references this KB
instead of repeating all criteria in every prompt.

---

## 1. Scoring Weights

### LLM Judge Score
```
llmJudgeScore =
  accuracy.score     × 0.25 +
  relevancy.score    × 0.25 +
  completeness.score × 0.20 +
  clarity.score      × 0.15 +
  groundedness.score × 0.15
```

### Faithfulness Score
```
faithfulnessScore =
  faithfulness       × 0.40 +
  attributionCoverage × 0.35 +
  contextRecall      × 0.25   ← use 0 if not applicable
```

### Similarity Score
```
similarityScore =
  rougeL.f1     × 0.40 +
  bleu.combined × 0.30 +
  cosine        × 0.20 +
  tokenF1.f1    × 0.10
```

### Overall Score
```
overallScore =
  llmJudgeScore     × 0.45 +
  faithfulnessScore × 0.35 +
  similarityScore   × 0.20
```

---

## 2. Pass / Fail Thresholds

| Threshold | Value |
|---|---|
| PASS | Overall Score ≥ 70 |
| HAPPY PATH | Overall Score ≥ 70 AND hallucinated claims = 0 |
| NON-HAPPY PATH | Overall Score < 70 OR hallucinated claims > 0 |
| Max improvement iterations | 3 |
| Stop improving if | Score stops increasing between iterations |

---

## 3. Dimension Scoring Rubric (1–5)

### Accuracy
| Score | Meaning |
|---|---|
| 5 | All facts correct, matches ground truth exactly |
| 4 | Minor factual differences, core content correct |
| 3 | Some correct, some incorrect or missing facts |
| 2 | Mostly incorrect or contradicts ground truth |
| 1 | Completely wrong or off-topic |

### Relevancy
| Score | Meaning |
|---|---|
| 5 | Directly addresses the task/question, no drift |
| 4 | Mostly relevant, minor tangents |
| 3 | Partially relevant, significant off-topic content |
| 2 | Mostly off-topic |
| 1 | Does not address the task at all |

### Completeness
| Score | Meaning |
|---|---|
| 5 | All key points from ground truth covered |
| 4 | Most points covered, 1–2 minor omissions |
| 3 | About half the key points covered |
| 2 | Only 1–2 points covered |
| 1 | Missing almost everything |

### Clarity
| Score | Meaning |
|---|---|
| 5 | Clear, well-structured, easy to read |
| 4 | Mostly clear, minor structural issues |
| 3 | Readable but disorganized or verbose |
| 2 | Hard to follow, poor structure |
| 1 | Incomprehensible |

### Groundedness
| Score | Meaning |
|---|---|
| 5 | Every claim traceable to source |
| 4 | Most claims grounded, 1–2 unsupported |
| 3 | About half grounded |
| 2 | Mostly unsupported claims |
| 1 | No grounding in source at all |

---

## 4. Color Coding

| Score Range | Color | Label |
|---|---|---|
| ≥ 80 | Green | Excellent |
| 65–79 | Amber | Good |
| 50–64 | Orange | Needs Work |
| < 50 | Red | Poor |

---

## 5. Short-Circuit Rules

```
IF similarityScore > 0.85
  → skip faithfulness_checker
  → call llm_judge with confidence mode
  → reason: output is very close to ground truth, hallucination risk low

IF hallucinationRate > 0.5
  → skip llm_judge
  → go straight to Improver
  → reason: too many hallucinations to be worth full judging

IF improvedScore < previousScore
  → stop improvement loop immediately
  → return previous iteration's output
  → reason: improvement is making things worse
```

---

## 6. Truncation Rules (Token Protection)

```
Source document > 2000 words
  → pass only first 1000 + last 500 words to faithfulness_checker

Agent output > 1000 words
  → pass first 500 words to llm_judge

Ground truth > 500 words
  → pass first 300 words to llm_judge

Full text always goes to similarity_checker (pure code, free)
```

---

## 7. Improvement Rules for Improver Agent

When fixing a non-happy path output, follow these rules strictly:

1. Keep everything that was correct in the original output
2. Remove all hallucinated claims listed in the failure report
3. Add missing content identified from the ground truth
4. Fix only the specific dimensions that scored below 60:
   - **Accuracy failed** → correct the specific factual errors cited
   - **Relevancy failed** → refocus on the actual question/task
   - **Completeness failed** → add the missing points from ground truth
   - **Clarity failed** → restructure and simplify
   - **Groundedness failed** → add source attribution for each claim
5. Do not add any new information not present in the source document
6. Match the same format and approximate length as the original output
7. Do not explain what you changed — return the improved output only

---

## 8. Task-Type Specific Metrics

| Task Type | Extra Metrics Active |
|---|---|
| Summary | Compression Ratio, Coverage Score, Density Score |
| QA | Exact Match, Answer Relevance, Context Recall |
| RAG | Context Recall, Faithfulness (weighted higher) |
| Code | Syntax Valid, Imports Resolvable, Bracket Balance |
| General | All standard metrics only |

---

## 9. Critical Checks (Double Weight)

These checks count double in the programmatic pass rate:

- Required fields present (JSON outputs)
- Hallucination detection
- PII detection
- Required keywords present

A failure in any of these automatically triggers non-happy path
regardless of the overall score.
