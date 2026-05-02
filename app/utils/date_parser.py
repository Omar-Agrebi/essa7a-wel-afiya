"""
Utility functions for deadline parsing and recency scoring.
Standalone module — no framework imports.
"""
from datetime import date
import dateparser


def parse_deadline(raw: str | None) -> date | None:
    """
    Parse a raw deadline string into a Python date object.

    Args:
        raw: Raw deadline string (e.g. "Dec 31 2025", "2025-12-31", "in 3 months").

    Returns:
        date | None: Parsed date, or None if parsing fails or input is None.
    """
    if not raw:
        return None
    try:
        parsed = dateparser.parse(
            raw,
            settings={
                "RETURN_AS_TIMEZONE_AWARE": False,
                "PREFER_FUTURE_DATES": True,
            },
        )
        return parsed.date() if parsed else None
    except Exception:
        return None


def days_until(deadline: date) -> int:
    """
    Compute how many days remain until the deadline from today.

    Args:
        deadline: Target date.

    Returns:
        int: Positive = days remaining, negative = days past deadline.
    """
    return (deadline - date.today()).days


def is_expired(deadline: date) -> bool:
    """
    Check whether a deadline has already passed.

    Args:
        deadline: Target date.

    Returns:
        bool: True if deadline is before today.
    """
    return deadline < date.today()


def recency_score(deadline: date | None) -> float:
    """
    Compute a recency score based on how far in the future the deadline is.

    Args:
        deadline: Target date or None.

    Returns:
        float:
            0.3  — unknown/None (neutral, not penalized)
            1.0  — more than 30 days away
            0.5  — 10 to 30 days away
            0.2  — 0 to 10 days away
            0.0  — already expired
    """
    if deadline is None:
        return 0.3
    remaining = days_until(deadline)
    if remaining > 30:
        return 1.0
    if remaining >= 10:
        return 0.5
    if remaining >= 0:
        return 0.2
    return 0.0
