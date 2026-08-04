"""gr-L1-market-analysis-quality-gate: validates the RESULTANT
L1-vision-market-analyzer output (its own items, with the evaluator's
fixes_applied resolved in) against L1-vision-market-analyzer/output_schema.json
and L1-vision-market-analyzer/evaluation.md. Fires at
L1-vision-market-analyzer-evaluator's post_execution.
"""
import json
import logging
import re
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-market-analysis-quality-gate")

SWOT_QUADRANTS = {"strengths": "ST", "weaknesses": "WK", "opportunities": "OP", "threats": "TH"}


def _parse(x):
    if isinstance(x, dict):
        return x
    try:
        return json.loads(x)
    except (TypeError, ValueError):
        return None


def _apply_fixes(items, fixes_applied):
    resultant = json.loads(json.dumps(items))

    def _walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str):
                    for fx in fixes_applied:
                        before, after = fx.get("before"), fx.get("after")
                        if before and after and before in v:
                            node[k] = v.replace(before, after)
                else:
                    _walk(v)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(resultant)
    return resultant


def _ids_sequential(entries, prefix):
    ids = [e.get("id", "") for e in entries if re.match(rf"^{prefix}-\d{{2}}$", e.get("id", ""))]
    nums = sorted(int(i.split("-")[1]) for i in ids)
    return nums == list(range(1, len(nums) + 1))


@action()
async def check_market_analysis_quality_gate(output: str, generator_output: str = None) -> bool:
    """Return True if a quality-gate violation is found in the RESULTANT market-analysis output."""
    evaluator_doc = _parse(output)
    gen_doc = _parse(generator_output)
    if gen_doc is None:
        logger.warning("QUALITY-GATE: generator_output not available or not valid JSON")
        return True

    gen_content = gen_doc.get("content", {})

    if gen_doc.get("status") == "failed":
        return False  # legitimate failure — nothing to validate

    fixes_applied = []
    if evaluator_doc:
        fixes_applied = evaluator_doc.get("content", {}).get("items", {}).get("fixes_applied", [])

    items = _apply_fixes(gen_content.get("items", {}), fixes_applied)

    # schema-compliance
    for field in ["competitor_matrix", "swot", "data_sufficiency"]:
        if field not in items:
            logger.warning(f"QUALITY-GATE: resultant output missing required field '{field}'")
            return True

    competitors = items["competitor_matrix"]
    for c in competitors:
        if not re.match(r"^CM-\d{2}$", c.get("id", "")):
            logger.warning(f"QUALITY-GATE: competitor id '{c.get('id')}' malformed")
            return True
        for f in ["positioning_summary", "strengths_summary", "weaknesses_summary"]:
            v = c.get(f, "")
            if not v or len(v) > 100:
                logger.warning(f"QUALITY-GATE: competitor {c.get('id')}.{f} missing or over length")
                return True
        if not c.get("confidence") or not c.get("reasoning"):
            logger.warning(f"QUALITY-GATE: competitor {c.get('id')} missing confidence/reasoning")
            return True

        # citation-completeness-100pct — the primary rubric check for this agent
        citation = c.get("citation", {})
        if not citation.get("source_reference") or not citation.get("retrieved_date"):
            logger.warning(f"QUALITY-GATE: competitor {c.get('id')} missing source_reference or retrieved_date — citation incomplete")
            return True

    swot = items["swot"]
    for quadrant, prefix in SWOT_QUADRANTS.items():
        entries = swot.get(quadrant, [])
        for e in entries:
            if not re.match(rf"^{prefix}-\d{{2}}$", e.get("id", "")):
                logger.warning(f"QUALITY-GATE: {quadrant} id '{e.get('id')}' malformed")
                return True
            summary = e.get("summary", "")
            if not summary or len(summary) > 100 or not e.get("confidence") or not e.get("reasoning"):
                logger.warning(f"QUALITY-GATE: {quadrant} entry {e.get('id')} fails schema")
                return True
        if entries and not _ids_sequential(entries, prefix):
            logger.warning(f"QUALITY-GATE: {quadrant} ids not sequential / have gaps or duplicates")
            return True

    if competitors and not _ids_sequential(competitors, "CM"):
        logger.warning("QUALITY-GATE: competitor_matrix ids not sequential / have gaps or duplicates")
        return True

    data_suff = items["data_sufficiency"]
    if data_suff.get("status") not in ("sufficient", "insufficient") or not data_suff.get("rationale_summary"):
        logger.warning("QUALITY-GATE: data_sufficiency fails schema")
        return True

    return False
