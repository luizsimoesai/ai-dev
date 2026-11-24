"""Expiry: links stop working after a number of days."""

from datetime import datetime, timedelta

from shortlinks.store import Link

TTL_DAYS = 90


def is_expired(link: Link, now: datetime, ttl_days: int = TTL_DAYS) -> bool:
    """A link expires once it is ttl_days old."""
    return now - link.created_at > timedelta(days=ttl_days)
