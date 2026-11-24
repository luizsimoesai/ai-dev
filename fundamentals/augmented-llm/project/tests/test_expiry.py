from datetime import datetime, timedelta, timezone

from shortlinks.expiry import is_expired
from shortlinks.store import Link

NOW = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


def test_new_link_is_not_expired():
    assert not is_expired(Link("abc", "https://example.com", created_at=NOW - timedelta(days=10)), NOW)


def test_link_expires_on_day_90():
    assert is_expired(Link("abc", "https://example.com", created_at=NOW - timedelta(days=90)), NOW)
