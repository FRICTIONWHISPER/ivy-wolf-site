"""site-catalog-map reader — pure core, injected I/O.

Loads data/catalog/catalog.json and returns typed structures.
PRICE RULE: any work whose price field is 'HELD' is returned with
price=None so callers never accidentally render a placeholder string.

TrueCore: no filesystem calls inside the pure functions; the load_catalog
entry point is the only I/O seam — inject a loader for tests.

Reusable by Fly Naked (FNK) and How2FlyPrivate (H2P): point CATALOG_PATH
at a different repo's data/catalog/catalog.json, or inject your own loader.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

CATALOG_PATH = Path(__file__).parent / "catalog.json"
HELD = "HELD"


# ---------------------------------------------------------------------------
# Pure data types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Work:
    id: str
    title: str
    size_in: str
    size_cm: str
    image_stems: tuple
    edition_size: Optional[int]
    price: Optional[str]           # None when HELD — never render while None
    credit: str
    product_type: str
    status: str = "available"


@dataclass(frozen=True)
class Collection:
    slug: str
    title: str
    status: str
    product_type: str
    credit: str
    hero_stem: str
    place_image_stems: tuple
    works: tuple                   # tuple[Work, ...]


@dataclass(frozen=True)
class Catalog:
    schema_version: str
    site: str
    generated: str
    collections: tuple             # tuple[Collection, ...]

    def collection(self, slug: str) -> Optional[Collection]:
        """Return the Collection with this slug, or None."""
        for c in self.collections:
            if c.slug == slug:
                return c
        return None


# ---------------------------------------------------------------------------
# Pure parsing helpers
# ---------------------------------------------------------------------------

def _parse_price(raw: str) -> Optional[str]:
    """Return None for HELD prices; pass through actual price strings."""
    return None if raw == HELD else raw


def _parse_work(raw: dict) -> Work:
    return Work(
        id=raw["id"],
        title=raw["title"],
        size_in=raw["size_in"],
        size_cm=raw["size_cm"],
        image_stems=tuple(raw.get("image_stems", [])),
        edition_size=raw.get("edition_size"),
        price=_parse_price(raw.get("price", HELD)),
        credit=raw.get("credit", "The Wolf Life"),
        product_type=raw["product_type"],
        status=raw.get("status", "available"),
    )


def _parse_collection(raw: dict) -> Collection:
    return Collection(
        slug=raw["slug"],
        title=raw["title"],
        status=raw["status"],
        product_type=raw["product_type"],
        credit=raw.get("credit", "The Wolf Life"),
        hero_stem=raw.get("hero_stem", ""),
        place_image_stems=tuple(raw.get("place_image_stems", [])),
        works=tuple(_parse_work(w) for w in raw.get("works", [])),
    )


def parse_catalog(data: dict) -> Catalog:
    """Pure: parse a raw dict (already loaded from JSON) into a Catalog."""
    return Catalog(
        schema_version=data.get("schema_version", ""),
        site=data.get("site", ""),
        generated=data.get("generated", ""),
        collections=tuple(_parse_collection(c) for c in data.get("collections", [])),
    )


# ---------------------------------------------------------------------------
# I/O seam — only entry point that touches the filesystem
# ---------------------------------------------------------------------------

def load_catalog(
    loader: Optional[Callable[[], dict]] = None,
    catalog_path: Optional[Path] = None,
) -> Catalog:
    """Load and parse the catalog.

    Args:
        loader: inject a callable returning a dict (for tests / other sites).
        catalog_path: override the default path (for tests / other sites).
    """
    if loader is not None:
        return parse_catalog(loader())
    path = catalog_path or CATALOG_PATH
    with open(path, encoding="utf-8") as fh:
        return parse_catalog(json.load(fh))


# ---------------------------------------------------------------------------
# CLI convenience — print a collection's data
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    cat = load_catalog()
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    if slug:
        coll = cat.collection(slug)
        if coll is None:
            print(f"ERROR: collection '{slug}' not found", file=sys.stderr)
            sys.exit(1)
        print(f"Collection : {coll.title} ({coll.status})")
        print(f"Product    : {coll.product_type}")
        print(f"Credit     : {coll.credit}")
        print(f"Hero stem  : {coll.hero_stem}")
        print(f"Place imgs : {', '.join(coll.place_image_stems)}")
        print(f"Works      : {len(coll.works)}")
        for w in coll.works:
            price_disp = w.price if w.price is not None else "(HELD — not shown)"
            print(f"  {w.id} | {w.title} | {w.size_in} / {w.size_cm} | price: {price_disp}")
    else:
        print(f"Catalog v{cat.schema_version} | site {cat.site} | {len(cat.collections)} collections")
        for c in cat.collections:
            print(f"  {c.slug}: {len(c.works)} works, {len(c.place_image_stems)} place images")
