# Evaluation Criteria — L1-inception-jira-uploader

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Both L1-epics.json and L1-features.json read before any processing | 100% | Automated: verify both blob-storage-reader calls happened before payload construction |
| Upstream status validation | 100% | Automated: verify both blob documents' top-level `status == "success"` before building the payload; `agent_status = "failed"` and halt otherwise |
| Every epic has non-empty `epic_id` and `title` | 100% | Automated: schema check; invalid epics dropped and logged |
| Every feature has non-empty `feature_id`, `title`, and a resolvable `epic_id` | 100% | Automated: cross-check against extracted epics[]; invalid features dropped and logged |
| Duplicate `epic_id`/`feature_id` handling | 100% | Automated: first occurrence kept, subsequent dropped and logged |
| Payload top-level keys exactly `projectKey` (optional), `issueType`, `issues` | 100% | Automated: pre-call payload validation step 6a |
| All Epic issues before all Feature issues | 100% | Automated: pre-call payload validation step 6c |
| Every Feature's `parentKey` resolves to an earlier Epic issue | 100% | Automated: pre-call payload validation step 6d |
| Every `description` value is a string or array of strings (never nested objects/ADF) | 100% | Automated: pre-call payload validation step 6e |
| `issues.length == epics_expected + features_expected` | 100% | Automated: pre-call payload validation step 6f |
| No label token contains a space | 100% | Automated: pre-call payload validation step 6g |
| `tool-L1-jira-upload-epics` invoked exactly once, never retried | 100% | Automated: verify single tool call in execution trace |
| `total_created + total_failed == total_expected` | 100% | Automated: arithmetic reconciliation check |
| Jira payload never surfaced in the final AgentOutput | 100% | Automated: scan output for `issueType`/`parentKey`/`label` keys outside `created_issues`/`failed_issues` |
| Output validates against output_schema.json | 100% | Automated: JSON Schema validation |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Grounding | ≥ 0.95 | Every issue traces to a specific epic_id/feature_id in the blob input |
| Hallucination | ≤ 0.05 | No invented Jira keys, project URLs, or issue content |
| Reconciliation accuracy | = 1.00 | issue_counts arithmetic is internally consistent |
| Error transparency | ≥ 0.95 | Every failed_issues entry carries the tool's verbatim error detail, never paraphrased away |
| Reasoning quality | ≥ 0.80 | Key mapping decisions (sprint labels, parent links, drops) explained in execution_summary |

## Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| Upstream validation discipline | Both status fields checked before any processing; correct halt-and-report on failure | Checked but minor logging gap | One upstream check skipped | No upstream status validation performed |
| Payload construction | All 6 pre-call checks pass; Epics strictly before Features; parentKey always resolvable | Minor cosmetic payload issue, self-corrected | One pre-call check failed and was not caught | Payload sent with structural violations (ADF, nested objects, feature-before-epic) |
| Tool invocation discipline | Invoked exactly once; result fully parsed line-by-line | Invoked once, parsing mostly complete | Invoked once but some return lines unparsed | Invoked more than once, or never invoked when it should have been |
| Reconciliation & reporting | Counts reconcile exactly; status accurately reflects success/partial/failed; Jira URLs correctly built | Counts reconcile, minor status nuance | Counts technically correct but status label debatable | Counts don't reconcile, or status contradicts actual outcome |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] Both L1-epics.json and L1-features.json were read via blob-storage-reader before any payload work began
- [ ] Both upstream documents' top-level `status` were checked; if either was not `"success"`, agent halted with `agent_status: "failed"` and did NOT invoke the tool
- [ ] Every epic/feature validation rule (non-empty IDs/titles, resolvable `epic_id`, duplicate handling) was applied and every drop was logged
- [ ] The internal Jira payload was never surfaced in the final output
- [ ] All 6 pre-call payload validation checks (step 6a-6g) were run and passed before tool invocation
- [ ] `tool-L1-jira-upload-epics` was invoked exactly once — never retried on failure
- [ ] Every line of the tool's return text was parsed into either `created_issues` or `failed_issues`, or triggered the fatal-error path
- [ ] `total_created + total_failed == total_expected`
- [ ] `agent_status` correctly reflects success / partial_success / failed per the exact rule in step 9
- [ ] `jira_space.project_url` and every `created_issues[].url`/`failed_issues[]` entry are correctly built from `base_url`
- [ ] `execution_summary` is plain text bullets, not JSON, and includes every required element (status, counts, project URL, sample keys, mapping decisions, reflection findings, guardrails, failed-issue detail)

## Reflection Process (mandatory)

1. **Generate** initial status output following the processing rules
2. **Log** `[REFLECTING] Checking output against evaluation.md criteria`
3. **Check** every item in the Reflection Checklist above
4. **Identify** gaps, errors, inconsistencies, or missed items
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** each issue — amend the output silently (this agent never retries the Jira tool itself, but MAY correct its own status/count bookkeeping before delivering)
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final corrected output

Reflection findings appear in execution_summary but interim output and payload drafts are never shown.
