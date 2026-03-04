from datetime import datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_utc().isoformat()


def dt_to_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


def get_shift_name(hour: int) -> str:
    """Return shift name based on hour (0-23). Matches frontend dateUtils.ts."""
    if 7 <= hour < 15:
        return "Day"
    elif 15 <= hour < 23:
        return "Evening"
    else:
        return "Night"


def seconds_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds())
