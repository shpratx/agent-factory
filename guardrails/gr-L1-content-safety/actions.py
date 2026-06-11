"""gr-L1-content-safety: Deterministic content safety checks."""
import re
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("gr-L1-content-safety")

HARMFUL_PATTERNS = [
    r'(?i)\b(kill\s+(yourself|themselves|himself|herself)|commit\s+suicide)\b',
    r'(?i)\b(how\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive))\b',
    r'(?i)\b(instructions\s+for\s+(making|creating)\s+(drugs|weapons|poison))\b',
]

TOXICITY_KEYWORDS = [
    r'(?i)\b(n[i1]gg[ae]r|f[a@]gg?[o0]t|k[i1]ke|sp[i1]c|ch[i1]nk)\b',
]

PROFANITY_THRESHOLD = 3
PROFANITY_PATTERN = r'(?i)\b(fuck|shit|damn|ass|bitch|bastard)\b'


@action()
async def check_content_safety(text: str) -> bool:
    """Return True if UNSAFE content found, False if safe."""
    if not text:
        return False

    content = text if isinstance(text, str) else str(text)

    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, content):
            logger.warning("CONTENT_SAFETY: harmful content pattern detected")
            return True

    for pattern in TOXICITY_KEYWORDS:
        if re.search(pattern, content):
            logger.warning("CONTENT_SAFETY: toxic/hate speech detected")
            return True

    profanity_count = len(re.findall(PROFANITY_PATTERN, content))
    if profanity_count >= PROFANITY_THRESHOLD:
        logger.warning(f"CONTENT_SAFETY: excessive profanity ({profanity_count} instances)")
        return True

    return False
