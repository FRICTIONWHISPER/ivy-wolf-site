# AV1-07 SITREP — Ivy Wolf Art whole-site SEO pass (all 16 routes)

**Date:** 2026-09-26
**Branch:** `ivy-seo-whole-site` · commit `f36037d` (SEO edits) + this file
**PIC:** Justin Smith · **SIC:** AV-1 (Claude Sonnet 4.6)

---

## What's done

**SEO was sitting inside the blog chain. It now runs on every route.**

Before this run: **94 gaps across 16 pages** (audit confirmed).
After this run: **0 gaps across 16 pages** (audit confirmed).

Every page on ivy-wolf.com now has:

- A `<link rel="canonical">` pointing to its own URL
- Open-graph tags: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `og:site_name`
- Twitter card: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`
- JSON-LD schema markup appropriate to the page type
- A title at least 30 characters long
- A meta description at least 50 characters long

**The 11 titles I lengthened (old → new):**

| Route | Old title | New title |
|---|---|---|
| /about | About — Ivy Wolf Art (20 ch) | About the Artist — Ivy Wolf Art \| Expressionist Painter (55 ch) |
| /contact | Contact — Ivy Wolf Art (22 ch) | Contact Ivy Wolf Art — Begin a Vision Session (45 ch) |
| /legal | Legal — Ivy Wolf Art (20 ch) | Legal Information — Ivy Wolf Art \| Wolf Co. (43 ch) |
| /shop | Shop — Ivy Wolf Art (19 ch) | Shop Original Paintings — Ivy Wolf Art \| Opening Soon (53 ch) |
| /shop/a-work | Shop — Ivy Wolf Art (19 ch, same as /shop!) | A-Work — Original Paintings by Ivy Wolf Art \| Opening Soon (57 ch) |
| /journal | The Ivy Wolf Life — Journal (27 ch) | The Ivy Wolf Life — Art Journal by Ivy Wolf (43 ch) |
| /thank-you | Thank you — Ivy Wolf Art (24 ch) | Thank You — Your Message Was Received \| Ivy Wolf Art (52 ch) |
| /collections | Collections — Ivy Wolf Art (26 ch) | Collections — Ivy Wolf Art Original Expressionist Paintings (58 ch) |
| /collections/austin-texas | Austin, Texas — Ivy Wolf Art (28 ch) | Austin, Texas — Ivy Wolf Art \| Expressionist Paintings (54 ch) |
| /collections/the-bahamas | The Bahamas — Ivy Wolf Art (26 ch) | The Bahamas — Ivy Wolf Art \| Expressionist Paintings (52 ch) |
| /collections/panama | Panama — Ivy Wolf Art (21 ch) | Panama — Ivy Wolf Art \| Expressionist Paintings (47 ch) |

**The 2 descriptions I fixed (old → new):**

| Route | Old description | New description |
|---|---|---|
| /shop | "Ivy Wolf Art shop — opening soon." (33 ch — too short) | "Ivy Wolf Art original expressionist paintings — shop opening soon. Browse the collections while you wait." (105 ch) |
| /shop/a-work | "Ivy Wolf Art shop — opening soon." (33 ch — same as /shop, too short) | "Browse A-Work original expressionist paintings by Ivy Wolf Art. Shop opening soon. See the collections in the meantime." (118 ch) |

**Tools built:**

- `seo_inject.py` — bounded-region-editor style injector. Every find/replace asserts exactly one match or halts. Idempotent: safe to re-run.
- `seo_audit.py` — gap reporter across all 16 routes. Exits 0 when clean, exits 1 when gaps remain.

**Proof:**

- `seo_audit.py`: 16/16 CLEAN, 0 gaps — confirmed after all edits
- 16/16 routes return HTTP 200 — confirmed via local server curl loop
- Secret scan: CLEAN — `secret_scan.py --path .` returned no findings
- Push verified: local and remote hash match `f36037de69e1ed705ee34ce0cf4f1c3c668c4622`

---

## What's not done

1. **Not deployed** — by design. Card said hand the branch back. AV-0 publishes.
2. **No sitemap.xml** — the repo has none. Not in scope for this card.
3. **No robots.txt** — the repo has none. Not in scope for this card.
4. **Tools not moved to seo-whisper** — by AV-0 direction: separate card needed.
5. **OG image dimensions unconfirmed** — the images are 1200w JPEGs. Google wants 1200×630 (1.91:1). The photos are landscape but exact pixel height is untested. Social previews may crop.

---

## Open questions

**1. Should the `/thank-you` page be noindex?**
It currently has `<meta name="robots" content="noindex, nofollow">` (I added it).
Rec: Keep it. Thank-you pages are form-redirect landings, not content. Indexing them wastes crawl budget and can confuse users who find them through search.

**2. Should sitemap.xml be added to this branch or a follow-up?**
Rec: Follow-up. It is a 20-line XML file with no risk. It deserves its own card so it gets its own gate and its own SITREP.

**3. Are the OG images the right size for social cards?**
The photos served are 1200px wide JPEGs. Exact height is not confirmed. Facebook and LinkedIn want 1200×630; Twitter wants 800×418 minimum.
Rec: After deploy, check one link in a social card tester (e.g. opengraph.xyz). If the crop is wrong, resize the images and update the og:image paths. This is one file change per page that needs fixing, not a full re-run.

**4. Should collection pages have Article or CollectionPage schema?**
They currently use `CollectionPage`. That is correct for a visual art collection. `Article` is for written content.
Rec: No change needed.

---

## Open decisions

**1. The $1,000 price in the /services meta tags — what happens at the next price change?**
Right now `$1,000` appears in the meta description, og:description, and twitter:description on `/services`. It also appears in body text on multiple pages (see "Price finding" section below).
The meta description is the source that feeds the OG and Twitter tags. A future price change on `/services` must touch:

- The `<meta name="description">` on `/services/index.html` (1 change)
- The `<meta property="og:description">` on `/services/index.html` (1 change — my run added this)
- The `<meta name="twitter:description">` on `/services/index.html` (1 change — my run added this)
- The body text on `/services/index.html` (multiple occurrences)
- The body text on `/index.html` and the five collection pages (each carries the price in their copy)

**The finding is: a single price change now touches 3 places in head markup (was 1 before this run) plus multiple body-text occurrences across 7 pages.**

Options (for PIC to decide, not AV-1):
- A. Keep as-is. The price is frozen, so this is low-urgency.
- B. Remove the price from the meta description only (replace with generic copy). This drops the head-markup count from 3 back to 0. Body text is unchanged.
- C. Build a single-source price constant (a JSON token) that all pages read at build time. Future changes touch one file. This is the clean engineering solution but is a build-system change.

PIC holds this. No change was made.

**2. Which OG image for /about, /contact, /legal, /thank-you?**
These four pages all use the main painting hero (`img-7235-1200w.jpg`). If the PIC wants page-specific OG images for any of them, each is a one-line change in `seo_inject.py` and a re-run.
Rec: Keep the hero image. General pages sharing one hero is standard practice.

---

## Expert recommendations

**1. AV-0 merges and deploys this branch as-is.** Everything is clean. Holding it longer adds no value.

**2. PIC decides: drop the price from the /services meta description.** Option B above. The copy already on the page shows pricing — the meta description does not need to repeat it. A generic "Commission an original expressionist painting. Begin with a free Vision Session." costs nothing and survives any price change.

**3. Next SEO card: sitemap.xml + robots.txt.** Two small files. Sitemap accelerates Google's crawl. Robots.txt is hygiene. Together they close the last technical SEO gap.

**4. Move seo_audit.py and seo_inject.py to seo-whisper — but in a separate card with a proper gate.** See the tool analysis below.

**5. After deploy, run a social card test on /services, /, and one collection page.** Check the OG image crop. If wrong, fix the images before the first social post.

---

## Learning corner

**Two things learned on this run:**

**1. Apostrophes inside double-quoted HTML attributes break naive audit regexes.**
The journal page meta description contains an apostrophe: `Ivy Wolf's journal…`.
A regex that matches on *any* quote character (`[^"\']*`) stopped at the apostrophe
and read a 89-char description as 28 chars. The bounded editor caught the downstream
problem (the OG description was also set to the truncated value) before the push.
Fix: write the regex to respect the *opening* quote type. If the attribute opens with `"`,
only stop at `"`.

**2. Every time a description becomes an OG tag, the number of places a fact lives doubles.**
This run was correct — copying the existing description into OG and Twitter tags is exactly
what the SEO chain asks for. But it means a frozen "fact" in a description (like a price)
now lives in three places instead of one. The finding is not a bug in this run. It is a
flag for the next decision: is that fact source-of-truth content, or is it a detail that
belongs only in the page body?

---

## Price finding (full report for AV-0)

**Prices in `<head>` markup (meta description, OG, Twitter, JSON-LD):**

| File | Tag | Price | Added this run? |
|---|---|---|---|
| services/index.html | `<meta name="description">` | $1,000 | No — was already there |
| services/index.html | `<meta property="og:description">` | $1,000 | **Yes** |
| services/index.html | `<meta name="twitter:description">` | $1,000 | **Yes** |

**Total price locations in head markup: 3** (was 1 before this run — this run added 2).
**JSON-LD on /services has no price.** The schema uses a text description without the price figure.

**Prices in body text (page content — unchanged by this run):**

| Page | Prices found in body |
|---|---|
| / | $1,000, $3,000 |
| /services | $1,000 (×many), $1,500, $2,000, $3,000 |
| /collections/austin-texas | $1,000, $1,500, $2,000, $3,000 |
| /collections/the-bahamas | $1,000, $1,500, $2,000, $3,000 |
| /collections/telluride-colorado | $1,000, $1,500, $2,000, $3,000 |
| /collections/sedona-arizona | $1,000, $1,500, $2,000, $3,000 |
| /collections/panama | $1,000, $1,500, $2,000, $3,000 |

**Body text prices were not touched by this run — all were there before.**

---

## Tool analysis — what it would take to fold into seo-whisper

### seo_audit.py

**What it does:** Opens each HTML file in a site and checks it against a fixed list of SEO requirements (title length, meta description length, canonical tag, og:title/og:description/og:image, H1 count, JSON-LD presence, image alt text). Prints a pass/fail table. Exits 0 when clean.

**What is ivy-wolf-specific:** Only the `ROUTES` list at the top — the 16 file paths and URL slugs.

**What would it take to fold into seo-whisper:**
- Move the file to `seo-whisper/03_ATOMIC/00_CODE/seo_audit.py`
- Replace the hardcoded `ROUTES` list with a CLI argument: `--routes <routes.json>` (a JSON file each site provides listing its pages)
- The rest of the logic is fully generic. No other ivy-wolf-specific code exists.
- Estimated effort: under an hour, including tests.

### seo_inject.py

**What it does:** Reads a per-page data map (title, description, OG image, JSON-LD schema type, route) and injects the full SEO head block into each HTML file before `</head>`. Enforces a bounded-region contract: every find/replace must match exactly once or the script halts. Idempotent.

**What is ivy-wolf-specific:**
- The `PAGES` list — 16 entries, each with the file path, route, title edits, description edits, OG image choice, and JSON-LD schema
- The `BASE_URL = "https://ivy-wolf.com"`
- The `DEFAULT_OG_IMAGE` path

**What would it take to fold into seo-whisper:**
- Move the core injector functions (`bounded_replace`, `build_seo_block`, `process_page`, `main`) to `seo-whisper/03_ATOMIC/00_CODE/seo_inject.py`
- The `PAGES` list and `BASE_URL` move to a per-site config file: `seo-whisper/04_HANDOFF/ivy-wolf-site.seo.json` (or wherever the calling site keeps its config)
- The injector accepts `--config <path>` and reads from that file
- The schema builders (`schema_webpage`, `schema_collection`, `ORG_SCHEMA`) are fully generic and move with the tool unchanged
- Estimated effort: 2–3 hours, including config schema design, one test suite, and a gate pass under coding-whisper

**What the config file would look like (sketch):**
```json
{
  "base_url": "https://ivy-wolf.com",
  "default_og_image": "assets/photo-library/img-7235-1200w.jpg",
  "pages": [
    {
      "file": "index.html",
      "route": "/",
      "og_type": "website",
      "schema_type": "Organization+WebSite"
    },
    ...
  ]
}
```

**Nothing in the core logic is so ivy-wolf-specific that it cannot be parameterised.**
The bounded-region contract, the idempotency check, and the head injection pattern
all belong in the fleet. They are generic tools wearing a site-specific data coat.

---

TAIL: AV-1 · | 2026-09-26 | PIC Justin Smith · SIC Director Whisper
