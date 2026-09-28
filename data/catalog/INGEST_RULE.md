# IWA IMAGE INGEST RULE (committed-folder discipline)

Source of truth for image classification: the PIC labels. Nothing is inferred.

## When new images arrive
1. They land in a DATED COMMITTED folder, never a flat drop:
   `uploads/COMMITTED/YYYY-MM-DD/<NN | COLLECTION>/`
   using the PIC pipe convention, e.g. `03 | MIND, BODY, SPIRIT`, `IWA | NEW | 01`.
2. Each image is numbered + labeled (collection, category, location, status).
3. The image is APPENDED to `media-map.json`.
4. An image is NEVER published until it appears in `media-map.json`.
   A raw drop with no date folder is NOT committed and does not ship.

## Status values
- SELECT-KEEP        — PIC-approved keep for a live collection
- LIVE-ELIGIBLE      — labeled, in a live collection
- HELD-v2-PIC-PICK   — v2 collection (MBS / Laguna), best frame chosen by PIC
- HELD               — labeled but parked (not in the five)
- PAINTING           — a work by Ivy; renders on its own surface, never in a place grid
- FNK-PINNED         — Fly Naked product shot; FNK lane, not Ivy Wolf

## Ties to pricing
`media-map.json` is the image half; `catalog.json` is the product/price half.
They join on the image `id`. A price is HELD until the PIC sets it, then it drops
into `catalog.json` against the same id — never hardcoded into a page.
