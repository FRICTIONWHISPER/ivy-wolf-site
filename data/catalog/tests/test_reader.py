"""Tests for data/catalog/reader.py — pure-core catalog reader.

These tests use injected loaders (no filesystem I/O) for pure functions,
and ONE integration test that reads the real catalog.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

# allow running from any cwd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from reader import (
    HELD,
    Catalog,
    Collection,
    Work,
    _parse_price,
    load_catalog,
    parse_catalog,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_CATALOG = {
    "schema_version": "1.0.0",
    "site": "IWA",
    "generated": "2026-09-28",
    "collections": [
        {
            "slug": "austin-texas",
            "title": "Austin, Texas",
            "status": "live",
            "product_type": "collection-limited-edition",
            "credit": "The Wolf Life",
            "hero_stem": "img-0001",
            "place_image_stems": ["img-0001", "img-0002"],
            "works": [],
        }
    ],
}

WORK_HELD = {
    "id": "IWA-AT-001",
    "title": "Test Work",
    "size_in": "20 × 28 in",
    "size_cm": "50 × 70 cm",
    "image_stems": [],
    "edition_size": None,
    "price": "HELD",
    "credit": "The Wolf Life",
    "product_type": "collection-limited-edition",
    "status": "available",
}

WORK_PRICED = {**WORK_HELD, "price": "$1,500"}


# ---------------------------------------------------------------------------
# Unit tests — pure functions
# ---------------------------------------------------------------------------

def test_parse_price_held():
    assert _parse_price(HELD) is None


def test_parse_price_real():
    assert _parse_price("$1,500") == "$1,500"


def test_parse_catalog_returns_catalog():
    cat = parse_catalog(MINIMAL_CATALOG)
    assert isinstance(cat, Catalog)
    assert cat.schema_version == "1.0.0"
    assert cat.site == "IWA"


def test_parse_catalog_collections():
    cat = parse_catalog(MINIMAL_CATALOG)
    assert len(cat.collections) == 1
    coll = cat.collections[0]
    assert isinstance(coll, Collection)
    assert coll.slug == "austin-texas"
    assert coll.title == "Austin, Texas"
    assert coll.status == "live"
    assert coll.product_type == "collection-limited-edition"
    assert coll.credit == "The Wolf Life"
    assert coll.hero_stem == "img-0001"
    assert coll.place_image_stems == ("img-0001", "img-0002")
    assert coll.works == ()


def test_catalog_lookup_hit():
    cat = parse_catalog(MINIMAL_CATALOG)
    coll = cat.collection("austin-texas")
    assert coll is not None
    assert coll.title == "Austin, Texas"


def test_catalog_lookup_miss():
    cat = parse_catalog(MINIMAL_CATALOG)
    assert cat.collection("nonexistent") is None


def test_work_held_price_is_none():
    cat_data = {
        **MINIMAL_CATALOG,
        "collections": [{
            **MINIMAL_CATALOG["collections"][0],
            "works": [WORK_HELD],
        }],
    }
    cat = parse_catalog(cat_data)
    work = cat.collections[0].works[0]
    assert isinstance(work, Work)
    assert work.price is None, "HELD price must parse to None so callers never render it"


def test_work_real_price_passes_through():
    cat_data = {
        **MINIMAL_CATALOG,
        "collections": [{
            **MINIMAL_CATALOG["collections"][0],
            "works": [WORK_PRICED],
        }],
    }
    cat = parse_catalog(cat_data)
    work = cat.collections[0].works[0]
    assert work.price == "$1,500"


def test_work_credit_defaults_to_wolf_life():
    data = {k: v for k, v in WORK_HELD.items() if k != "credit"}
    cat_data = {
        **MINIMAL_CATALOG,
        "collections": [{
            **MINIMAL_CATALOG["collections"][0],
            "works": [data],
        }],
    }
    cat = parse_catalog(cat_data)
    assert cat.collections[0].works[0].credit == "The Wolf Life"


def test_load_catalog_injected_loader():
    cat = load_catalog(loader=lambda: MINIMAL_CATALOG)
    assert isinstance(cat, Catalog)
    assert len(cat.collections) == 1


# ---------------------------------------------------------------------------
# Rules enforcement
# ---------------------------------------------------------------------------

FIVE_LIVE_SLUGS = {"austin-texas", "the-bahamas", "telluride-colorado", "sedona-arizona", "panama"}


def test_all_five_collections_present():
    """Integration: real catalog.json must have all 5 live collections."""
    cat = load_catalog()
    slugs = {c.slug for c in cat.collections}
    assert FIVE_LIVE_SLUGS == slugs, f"Missing or extra: {FIVE_LIVE_SLUGS.symmetric_difference(slugs)}"


def test_every_collection_is_live():
    cat = load_catalog()
    for c in cat.collections:
        assert c.status == "live", f"{c.slug} status is {c.status!r}, expected 'live'"


def test_credit_always_wolf_life():
    cat = load_catalog()
    for c in cat.collections:
        assert c.credit == "The Wolf Life", f"{c.slug} collection credit is wrong: {c.credit!r}"
        for w in c.works:
            assert w.credit == "The Wolf Life", f"work {w.id} credit is wrong"


def test_no_price_rendered_while_held():
    cat = load_catalog()
    for c in cat.collections:
        for w in c.works:
            if w.price is not None:
                assert w.price != HELD, f"work {w.id} price was not suppressed"


def test_product_type_is_collection_limited_edition():
    cat = load_catalog()
    for c in cat.collections:
        assert c.product_type == "collection-limited-edition", (
            f"{c.slug}: product_type must be collection-limited-edition, got {c.product_type!r}"
        )


def test_every_collection_has_hero_stem():
    cat = load_catalog()
    for c in cat.collections:
        assert c.hero_stem, f"{c.slug}: hero_stem is empty"


def test_hero_stem_is_in_place_image_stems():
    cat = load_catalog()
    for c in cat.collections:
        if c.place_image_stems:
            assert c.hero_stem in c.place_image_stems, (
                f"{c.slug}: hero_stem {c.hero_stem!r} not in place_image_stems"
            )
