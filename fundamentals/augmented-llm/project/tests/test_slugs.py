from shortlinks.slugs import DEFAULT_LENGTH, is_valid_slug, new_slug


def test_new_slug_is_valid():
    slug = new_slug()
    assert len(slug) == DEFAULT_LENGTH and is_valid_slug(slug)


def test_custom_slug_limits():
    assert is_valid_slug("abc")
    assert is_valid_slug("a" * 24)
    assert not is_valid_slug("ab")
    assert not is_valid_slug("a" * 25)
    assert not is_valid_slug("Spring-Sale")
