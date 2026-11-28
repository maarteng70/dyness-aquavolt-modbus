"""Pure helpers for decoding Dyness TOU (economic mode) schedule registers.

Protocol v1.15, registers 27515-27530:

  2 bytes per field:
    StartTime_N / EndTime_N   HHMM  (HH = value / 100, MM = value % 100)
    BatPower_N                signed watts (neg = charge, pos = discharge)
    WorkWeek_N                bitmask

  WorkWeek_N:
    bits 15-8   0xFF = slot enabled, 0x00 = slot disabled
    bit 6       Saturday
    bit 5       Friday
    bit 4       Thursday
    bit 3       Wednesday
    bit 2       Tuesday
    bit 1       Monday
    bit 0       Sunday
    e.g. 0xFF7F = enabled, every day

No Home Assistant imports here so the logic stays unit-testable.
"""

from __future__ import annotations

DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def format_hhmm(value) -> str | None:
    """Render a HHMM register value as HH:MM.

    Returns None when the value is not a usable time, so entities can show
    ``unknown`` instead of nonsense such as ``65:376``.
    """
    if value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if number < 0:
        return None
    hours, minutes = divmod(number, 100)
    if hours > 23 or minutes > 59:
        return None
    return f"{hours:02d}:{minutes:02d}"


def week_enabled(value) -> bool:
    """Return True when the high byte of the WorkWeek register is 0xFF."""
    if value is None:
        return False
    try:
        return ((int(value) >> 8) & 0xFF) == 0xFF
    except (TypeError, ValueError):
        return False


def week_days(value) -> list[str]:
    """Return the selected weekday names (Sunday first) from a WorkWeek mask."""
    if value is None:
        return []
    try:
        mask = int(value) & 0xFF
    except (TypeError, ValueError):
        return []
    return [name for bit, name in enumerate(DAY_NAMES) if mask & (1 << bit)]


def describe_schedule(start, end, percent, week) -> dict:
    """Build a display/attribute payload for one TOU slot."""
    days = week_days(week)
    start_text = format_hhmm(start)
    end_text = format_hhmm(end)
    return {
        "start": start_text,
        "end": end_text,
        "days": days,
        "days_text": ", ".join(days) if days else "none",
        "enabled": week_enabled(week),
        "power_w": percent,
        "raw": {"start": start, "end": end, "power": percent, "week": week},
    }


def schedule_label(start, end, week) -> str | None:
    """Short label used as the entity state, e.g. ``02:00-06:21``."""
    start_text = format_hhmm(start)
    end_text = format_hhmm(end)
    if start_text is None or end_text is None:
        return None
    suffix = "" if week_enabled(week) else " (off)"
    return f"{start_text}-{end_text}{suffix}"
