"""The link store: keeps links in memory and counts visits."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from shortlinks.slugs import is_valid_slug, new_slug


@dataclass
class Link:
    slug: str
    url: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    visits: int = 0


class LinkStore:
    def __init__(self):
        self.links: dict[str, Link] = {}

    def add(self, url: str, slug: str | None = None) -> Link:
        """Store a link under a custom slug, or a random one if none is given."""
        slug = slug or new_slug()
        if not is_valid_slug(slug):
            raise ValueError(f"invalid slug: {slug!r}")
        if slug in self.links:
            raise ValueError(f"slug already taken: {slug!r}")
        self.links[slug] = Link(slug, url)
        return self.links[slug]

    def resolve(self, slug: str) -> str:
        """The long URL for a slug; counts one visit."""
        link = self.links[slug]
        link.visits += 1
        return link.url
