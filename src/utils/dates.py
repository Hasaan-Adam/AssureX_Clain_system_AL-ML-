"""
AssureX Claim Engine - Date & Time Utilities
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Tuple, Union


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


def today_utc() -> date:
    """Return current UTC date."""
    return utc_now().date()


def parse_date(date_val: Union[str, date, datetime]) -> date:
    """
    Parse a date input from string or datetime into a standard date object.
    Supports ISO formats (YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY, etc.)
    """
    if isinstance(date_val, datetime):
        return date_val.date()
    if isinstance(date_val, date):
        return date_val
    if isinstance(date_val, str):
        clean_val = date_val.strip()
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(clean_val, fmt).date()
            except ValueError:
                continue
        try:
            return date.fromisoformat(clean_val.split("T")[0])
        except ValueError as exc:
            raise ValueError(f"Unable to parse date string: {date_val}") from exc

    raise TypeError(f"Unsupported type for date conversion: {type(date_val)}")


def parse_datetime(dt_val: Union[str, datetime]) -> datetime:
    """
    Parse a datetime string or object into a UTC timezone-aware datetime.
    """
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo is None:
            return dt_val.replace(tzinfo=timezone.utc)
        return dt_val.astimezone(timezone.utc)
    if isinstance(dt_val, str):
        clean_val = dt_val.strip()
        try:
            parsed = datetime.fromisoformat(clean_val)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            pass
        d = parse_date(clean_val)
        return datetime.combine(d, time.min, tzinfo=timezone.utc)

    raise TypeError(f"Unsupported type for datetime conversion: {type(dt_val)}")


def format_iso(dt_or_d: Union[date, datetime]) -> str:
    """Format a date or datetime to standard ISO string."""
    return dt_or_d.isoformat()


def days_between(start_date: Union[str, date, datetime], end_date: Union[str, date, datetime]) -> int:
    """Calculate signed number of days between two dates (end_date - start_date)."""
    d1 = parse_date(start_date)
    d2 = parse_date(end_date)
    return (d2 - d1).days


def calculate_warranty_expiry(purchase_date: Union[str, date, datetime], duration_months: int) -> date:
    """
    Calculate warranty expiration date given a purchase date and duration in months.
    Accounts for month boundaries and leap years.
    """
    p_date = parse_date(purchase_date)
    year = p_date.year + (p_date.month + duration_months - 1) // 12
    month = (p_date.month + duration_months - 1) % 12 + 1
    day = min(p_date.day, 28)
    for try_day in range(p_date.day, 27, -1):
        try:
            return date(year, month, try_day)
        except ValueError:
            continue
    return date(year, month, day)


def is_warranty_active(
    start_date: Union[str, date, datetime],
    end_date: Union[str, date, datetime],
    current_date: Optional[Union[str, date, datetime]] = None,
    grace_period_days: int = 0,
) -> Tuple[bool, int]:
    """
    Check if a warranty is active at the given date (or current date).
    Returns (is_active, days_remaining_or_overdue).
    - If active: returns (True, days_remaining)
    - If expired within grace period: returns (True, -days_overdue)
    - If expired past grace period: returns (False, -days_overdue)
    """
    ref_date = parse_date(current_date) if current_date else today_utc()
    s_date = parse_date(start_date)
    e_date = parse_date(end_date)

    if ref_date < s_date:
        return False, days_between(ref_date, s_date)

    days_until_expiry = days_between(ref_date, e_date)
    if days_until_expiry >= 0:
        return True, days_until_expiry

    overdue_days = abs(days_until_expiry)
    if overdue_days <= grace_period_days:
        return True, days_until_expiry

    return False, days_until_expiry