"""Slugs: the short code at the end of a link, as in sho.rt/k3x9q2a."""

import secrets
import string

ALPHABET = string.ascii_lowercase + string.digits
DEFAULT_LENGTH = 7
MIN_SLUG_LENGTH = 3
MAX_SLUG_LENGTH = 24  # custom slugs chosen by users can be up to this long


def new_slug(length: int = DEFAULT_LENGTH) -> str:
    """A random slug of lowercase letters and digits."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def is_valid_slug(slug: str) -> bool:
    """Custom slugs: lowercase letters, digits and hyphens, within the length limits."""
    allowed = set(ALPHABET + "-")
    return MIN_SLUG_LENGTH <= len(slug) <= MAX_SLUG_LENGTH and set(slug) <= allowed
