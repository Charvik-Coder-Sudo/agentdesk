"""Time helpers. AgentDesk stores times as ISO 8601 UTC with milliseconds."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(moment: datetime) -> str:
    """Format a datetime as YYYY-MM-DDTHH:MM:SS.fffZ (converted to UTC)."""
    moment = moment.astimezone(timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def utc_now_iso() -> str:
    """The current time as YYYY-MM-DDTHH:MM:SS.fffZ."""
    return to_iso(utc_now())
