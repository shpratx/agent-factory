# tool-L1-system-current-date

## What does it do?

Returns the current date from the host clock as a JSON string, with `current_date` in `yyyy-mm-dd`, optionally read in a given IANA timezone. It makes no network call and needs no credentials — the value is computed locally.

It exists because an LLM has no clock. Given a template slot like `| Generated | {current_date} |` and no date anywhere in its context, a model does not report that it cannot know the date; it fills the slot with a plausible-looking date sampled from its training distribution, or anchored on some other date in the prompt. The output is correctly formatted and confidently wrong, which is the worst combination — a reader cannot tell it apart from a real date. A prompt instruction ("never guess the date") does not fix this on its own, because it competes with the stronger instruction to fill the template completely and offers the model nothing to write instead. This tool gives it something real to write.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timezone | string | — | IANA timezone name (e.g. `Asia/Kolkata`, `Europe/London`, `UTC`). Defaults to `UTC`. An unrecognised or unavailable name falls back to UTC and is reported in `warning` — never silently substituted. |

Pass the timezone of the jurisdiction the document is being produced for where that matters: near midnight, UTC and a local timezone disagree about what day it is, and a document dated a day off can sit on the wrong side of a commencement or deadline date.

## Returns

A JSON string, always parseable.

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether the clock was read |
| data.current_date | string | Today's date as `yyyy-mm-dd` (null on failure) |
| data.timezone | string | The timezone actually used |
| data.requested_timezone | string | The timezone as passed in, for comparison against `timezone` |
| data.iso_timestamp | string | Full ISO-8601 instant with UTC offset |
| data.day_of_week | string | Day name, e.g. `Wednesday` |
| data.warning | string | Set when the requested timezone could not be applied (null otherwise) |
| error | string | Error message (null on success) |

## Example

```python
tool = CurrentDateTool()

tool.execute(timezone="Asia/Kolkata")
# '{"success": true, "current_date": "2026-09-03", "timezone": "Asia/Kolkata",
#   "requested_timezone": "Asia/Kolkata", "iso_timestamp": "2026-09-03T03:00:00+05:30",
#   "day_of_week": "Thursday", "warning": null, "error": null}'

tool.execute()
# '{"success": true, "current_date": "2026-09-02", "timezone": "UTC", ...}'
```

## How an agent should use it

1. Call the tool once, at the start of the run, before filling any dated field.
2. Read `current_date` by key from the returned JSON — do not regex the string.
3. Write that value, and only that value, into the document's date field.
4. If `success` is false, write `"not available"` in the field and note it in the execution summary. **Never** fall back to a remembered or inferred date: an honest gap is recoverable, an invented date is not, because nothing downstream can detect it.
5. If `warning` is non-null, the date is real but was read in UTC rather than the timezone asked for — carry that into the execution summary.

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Unrecognised timezone | Name is not in the IANA database | Falls back to UTC, `success` stays true, `warning` names the rejected input |
| tz database missing | Windows host without the `tzdata` package | Falls back to UTC with a warning; UTC itself always works |
| Clock read fails | Host-level failure | `success` false, `current_date` null, generic error string; details go to `system_tool_operations.log` |

There is no retry and no circuit breaker: a local clock read has no transient failure mode worth retrying, and there is no downstream service to protect.

## Dependencies

Standard library (`json`, `logging`, `datetime`, `zoneinfo`) plus `crewai` and `pydantic` for the tool wrapper. On Windows, non-UTC timezones need `tzdata` installed (`pip install tzdata`); without it the tool still works and returns UTC with a warning.

## Tests

```
pytest tool-L1-system-current-date-test.py -v
```

The host clock is patched to a fixed instant chosen late in the UTC day, so the timezone tests pin down the case that actually matters — a timezone shift moving the date across midnight.
