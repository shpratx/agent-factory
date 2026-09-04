"""tool-L1-system-current-date: returns the date this run executes, read from the host clock.

No credentials and no network call — the value is computed locally.

Why this tool exists: an LLM has no clock. Asked to stamp a document with
"today's date" it will fill the slot with a plausible-looking date drawn from
its training distribution or from dates elsewhere in its context, and the result
is indistinguishable from a correct one to whoever reads the document. This tool
replaces that guess with an actual reading, so an agent can cite a date instead
of inventing one.
"""

import json
import logging
from datetime import datetime, timezone as _utc_timezone

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None


DEFAULT_TIMEZONE = "UTC"


# Define the args schema for your tool
class CurrentDateSchema(BaseModel):
    timezone: str = Field(
        default=DEFAULT_TIMEZONE,
        description=(
            "IANA timezone name to read the date in (e.g. 'Asia/Kolkata', "
            "'Europe/London', 'UTC'). Defaults to UTC. An unrecognised or "
            "unavailable name falls back to UTC and is reported in the "
            "'warning' field — never silently substituted."
        ),
    )


# Set up secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='system_tool_operations.log'
)
logger = logging.getLogger('CurrentDateTool')


class CurrentDateTool(BaseTool):
    name: str = "Current Date Tool"
    description: str = (
        "Returns the current date from the host clock as JSON, with current_date "
        "in yyyy-mm-dd, optionally read in a given IANA timezone. Call this "
        "whenever a document must carry the date it was produced — never state "
        "a date from memory."
    )
    args_schema: type[BaseModel] = CurrentDateSchema

    def __init__(self):
        super().__init__(
            name="Current Date Tool",
            description=(
                "Returns the current date from the host clock as JSON, with "
                "current_date in yyyy-mm-dd, optionally read in a given IANA "
                "timezone."
            )
        )

    def _resolve_timezone(self, requested):
        """
        Resolve an IANA timezone name to a tzinfo.

        Returns (tzinfo, resolved_name, warning). Falls back to UTC rather than
        raising — a missing date is a worse outcome for the caller than a date
        read in the wrong timezone, provided the substitution is reported.
        """
        # UTC is handled without zoneinfo so the tool still works on hosts with
        # no IANA tz database installed (Windows without the tzdata package).
        if requested.upper() == "UTC":
            return _utc_timezone.utc, "UTC", None

        if ZoneInfo is None:
            return (
                _utc_timezone.utc,
                "UTC",
                f"zoneinfo unavailable on this host; '{requested}' could not be "
                f"applied and the date was read in UTC.",
            )

        try:
            return ZoneInfo(requested), requested, None
        except Exception as e:
            logger.warning(f"Timezone '{requested}' could not be resolved: {str(e)}")
            return (
                _utc_timezone.utc,
                "UTC",
                f"Timezone '{requested}' is not a recognised IANA name or its "
                f"data is not installed; the date was read in UTC instead.",
            )

    def get_current_date(self, timezone=DEFAULT_TIMEZONE):
        """
        Read today's date from the host clock.

        :param timezone: string, IANA timezone name. Defaults to UTC.
        Returns:
            str: JSON object with success, current_date (yyyy-mm-dd), timezone,
                 requested_timezone, iso_timestamp, day_of_week, warning.
                 On failure: success false, current_date null, and an error string.
        """
        requested = (timezone or DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE

        try:
            tzinfo, resolved, warning = self._resolve_timezone(requested)
            now = datetime.now(tzinfo)

            result = {
                "success": True,
                "current_date": now.strftime("%Y-%m-%d"),
                "timezone": resolved,
                "requested_timezone": requested,
                "iso_timestamp": now.isoformat(timespec="seconds"),
                "day_of_week": now.strftime("%A"),
                "warning": warning,
                "error": None,
            }

            logger.info(
                f"Current date served: {result['current_date']} ({resolved})"
                + (f" — warning: {warning}" if warning else "")
            )
            return json.dumps(result)

        except Exception as e:
            # Log the full error details but return a generic message.
            logger.error(f"An error occurred reading the clock: {str(e)}", exc_info=True)
            return json.dumps({
                "success": False,
                "current_date": None,
                "timezone": None,
                "requested_timezone": requested,
                "iso_timestamp": None,
                "day_of_week": None,
                "warning": None,
                "error": "Could not read the current date from the host clock",
            })

    def _run(self, timezone=DEFAULT_TIMEZONE):
        """
        Run method required by CrewAI BaseTool.

        Args:
            timezone (str): IANA timezone name to read the date in. Defaults to UTC.

        Returns:
            str: JSON string carrying current_date in yyyy-mm-dd.
        """
        return self.get_current_date(timezone)
