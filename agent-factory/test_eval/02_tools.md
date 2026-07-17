# Evaluation Framework — Tools

Three tools. Only one makes LLM calls. Two are pure code.

---

## Tool 1 — `similarity_checker`

**Token cost: ZERO — pure code, no LLM call**

### Input
```json
{
  "output": "string",
  "groundTruth": "string"
}
```

### Output
```json
{
  "bleu": {
    "bleu1": 0.0,
    "bleu2": 0.0,
    "bleu3": 0.0,
    "bleu4": 0.0,
    "combined": 0.0
  },
  "rouge1":  { "precision": 0.0, "recall": 0.0, "f1": 0.0 },
  "rouge2":  { "precision": 0.0, "recall": 0.0, "f1": 0.0 },
  "rougeL":  { "lcsLength": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0 },
  "tokenF1": { "precision": 0.0, "recall": 0.0, "f1": 0.0 },
  "cosine":  0.0,
  "exactMatch": false,
  "similarityScore": 0.0
}
```

### Logic (implement in code, no LLM)

**BLEU Score**
- Compute BLEU-1 through BLEU-4 against ground truth
- Use add-1 (Laplace) smoothing
- Apply brevity penalty if output is shorter than ground truth
- Combined BLEU = geometric mean of BLEU-1 to BLEU-4

**ROUGE-1**
- Tokenize both texts: lowercase, remove punctuation, split on whitespace
- Precision = matched unigrams / output unigrams
- Recall = matched unigrams / ground truth unigrams
- F1 = 2 × P × R / (P + R)

**ROUGE-2**
- Same as ROUGE-1 but using bigrams (consecutive word pairs)

**ROUGE-L**
- Find Longest Common Subsequence between output and ground truth tokens
- Recall = LCS length / ground truth length
- Precision = LCS length / output length
- F1 = harmonic mean

**Token F1**
- Tokenize both texts (lowercase, remove punctuation)
- Compute token-level precision, recall, F1

**Cosine Similarity**
- Build TF vectors over shared vocabulary
- Cosine = dot product / (magnitude_output × magnitude_groundTruth)
- No LLM call — pure JavaScript/code

**Overall Similarity Score**
```
similarityScore =
  rougeL.f1    × 0.40 +
  bleu.combined × 0.30 +
  cosine        × 0.20 +
  tokenF1.f1    × 0.10
```

---

## Tool 2 — `faithfulness_checker`

**Token cost: 1 LLM call**

### Input
```json
{
  "output": "string",
  "source": "string"
}
```

> Only this tool receives the full source document.
> No other tool needs it.

### Output
```json
{
  "claims": [
    {
      "claim": "string",
      "supported": true,
      "evidence": "string"
    }
  ],
  "attributions": [
    {
      "outputSentence": "string",
      "sourceSentence": "string",
      "attributed": true
    }
  ],
  "faithfulnessScore": 0.0,
  "hallucinationRate": 0.0,
  "attributionCoverage": 0.0
}
```

### LLM Prompt (single call covering claims + attribution)
```
Extract every factual claim from the OUTPUT as a list.
For each claim, check if it is directly supported by the SOURCE DOCUMENT.

Also, for each sentence in the OUTPUT, identify which sentence
in the SOURCE it was derived from, or mark as unattributed.

Return JSON only, no other text:
{
  "claims": [
    { "claim": "string", "supported": bool, "evidence": "string" }
  ],
  "attributions": [
    { "output_sentence": "string", "source_sentence": "string", "attributed": bool }
  ]
}
```

### Score Computation (in code after LLM response)
```
faithfulnessScore  = supported claims / total claims
hallucinationRate  = 1 - faithfulnessScore
attributionCoverage = attributed sentences / total sentences
```

---

## Tool 3 — `llm_judge`

**Token cost: 1 LLM call**

### Input
```json
{
  "output": "string",
  "groundTruth": "string",
  "taskType": "Summary | QA | RAG | General | Code",
  "failedDimensions": ["string"]
}
```

> `failedDimensions` is optional — only passed on re-evaluation
> iterations to focus the judge on what previously failed.

### Output
```json
{
  "accuracy":      { "score": 0, "justification": "string", "evidence": "string" },
  "relevancy":     { "score": 0, "justification": "string", "evidence": "string" },
  "completeness":  { "score": 0, "justification": "string", "evidence": "string" },
  "clarity":       { "score": 0, "justification": "string", "evidence": "string" },
  "groundedness":  { "score": 0, "justification": "string", "evidence": "string" },
  "overallVerdict": "PASS | FAIL",
  "primaryFailureReason": "string | null",
  "improvementInstructions": "string | null",
  "llmJudgeScore": 0.0
}
```

### LLM Prompt
```
You are an expert evaluator. Evaluate the AGENT OUTPUT
against the GROUND TRUTH using the scoring guide below.

Score each dimension from 1 to 5. Return JSON only, no other text:
{
  "accuracy":     { "score": int, "justification": string, "evidence": string },
  "relevancy":    { "score": int, "justification": string, "evidence": string },
  "completeness": { "score": int, "justification": string, "evidence": string },
  "clarity":      { "score": int, "justification": string, "evidence": string },
  "groundedness": { "score": int, "justification": string, "evidence": string },
  "overall_verdict": "PASS" | "FAIL",
  "primary_failure_reason": string | null,
  "improvement_instructions": string | null
}

SCORING GUIDE:
- Accuracy:      Does the output contain correct information vs ground truth?
- Relevancy:     Does the output address the actual task or question?
- Completeness:  Are all required points from ground truth covered?
- Clarity:       Is the output clear, well-structured, and readable?
- Groundedness:  Is every claim traceable to a source?
```

### Score Normalization (in code)
```
normalized score = (raw score 1–5 - 1) / 4 × 100  →  0–100 scale

llmJudgeScore =
  accuracy.score     × 0.25 +
  relevancy.score    × 0.25 +
  completeness.score × 0.20 +
  clarity.score      × 0.15 +
  groundedness.score × 0.15
```

---

## Tool Input Rules — What Each Tool Receives

| Data | similarity_checker | faithfulness_checker | llm_judge |
|---|---|---|---|
| Source Document | ✗ | ✓ | ✗ |
| Agent Output | ✓ | ✓ | ✓ |
| Ground Truth | ✓ | ✗ | ✓ |
| Task Type | ✗ | ✗ | ✓ |
| LLM Call | ✗ | ✓ | ✓ |
