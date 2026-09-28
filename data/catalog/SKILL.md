---
name: site-catalog-map
description: Machine-readable catalog layer for IWA-family sites (Ivy Wolf Art, Fly Naked, How2FlyPrivate). Defines the collection/works/image-stems/price schema and a pure Python reader. Prices are HELD until the PIC sets them — the reader suppresses display. Reuse: point CATALOG_PATH at any site's data/catalog/catalog.json.
---

# site-catalog-map

Single source of truth for every collection, work, image stem, edition size, and price on an IWA-family site. Collection pages READ this map — they do not hardcode.

## Files

| File | Purpose |
|---|---|
| `catalog.json` | Site-specific data (collections, works, images). Lives in the site repo. |
| `schema.json` | JSON Schema defining the allowed shape. |
| `reader.py` | Pure Python reader with injected I/O seam. Import and call `load_catalog()`. |
| `tests/test_reader.py` | 17-test suite (unit + rules enforcement). |

## Usage

```python
from data.catalog.reader import load_catalog

catalog = load_catalog()
coll = catalog.collection("austin-texas")
for work in coll.works:
    if work.price is not None:   # None = HELD — never render
        print(work.title, work.price)
```

## Price rule
`work.price` is `None` when the PIC has not set it. **Never render a None price.** The reader handles this — callers just check `is not None`.

## Cardinal rules
See `CARDINAL_RULES`.
