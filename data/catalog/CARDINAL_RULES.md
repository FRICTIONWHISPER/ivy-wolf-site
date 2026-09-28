# Cardinal Rules — site-catalog-map

1. **PRICES HELD** — never render a price while `work.price` is `None` (HELD). The reader returns `None`; the caller checks `is not None` before displaying anything. A rendered HELD string is a bug.

2. **CREDIT IS ALWAYS 'The Wolf Life'** — no photographer name, no PIC name, on any image or work record. The credit field defaults to 'The Wolf Life'; override only if the PIC explicitly states a different credit for a specific work.

3. **product_type is collection-limited-edition** for all works in a collection. Commissions are separate; never mix the two on a collection page. A collection page never says "commission this work."

4. **catalog.json is the source of truth** — collection pages do NOT hardcode images, prices, or edition data. If the page has a hardcoded value that contradicts the catalog, the catalog wins and the page must be updated.

5. **Sizes in both units** — every work record requires both `size_in` (inches) and `size_cm` (centimetres). Never ship a work with only one unit. Use 'HELD' for both if unknown.

6. **Never invent a collection slug** — slugs must exactly match the live routes in `collections/<slug>/index.html`. Adding a new collection requires both a slug entry here AND a route in the site.

7. **The reader is pure core** — no filesystem I/O inside the `parse_*` functions. `load_catalog()` is the only I/O seam. Inject a loader for tests; never mock the filesystem inside pure functions.

8. **Branch discipline** — changes to catalog.json ship on `plan/ivy-catalog-map` or a successor branch. No direct commits to main. The Director merges.
