import pytest

from shortlinks.store import LinkStore


def test_resolve_counts_visits():
    store = LinkStore()
    store.add("https://example.com/spring-sale", slug="spring-sale")
    assert store.resolve("spring-sale") == "https://example.com/spring-sale"
    assert store.links["spring-sale"].visits == 1


def test_slug_already_taken():
    store = LinkStore()
    store.add("https://example.com/a", slug="promo")
    with pytest.raises(ValueError):
        store.add("https://example.com/b", slug="promo")
