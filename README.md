# plumbersbonneylake.com — build step 2 (brand, nav, footer, homepage)

Static site for Vercel + GitHub. Push this folder to the repo root; Vercel auto-detects it (no build step).

## What's here
- `index.html` — homepage (1,900+ words, schema, FAQ, lead form)
- `css/styles.css`, `js/main.js` — shared across every page
- `img/` — logo.svg, logo-white.svg, mark.svg, favicon.svg, favicon.ico, apple-touch-icon.png, icon-192/512.png, og-home.png
- `partials/header.html`, `partials/footer.html` — paste into every future page
- `api/lead.js` — serverless lead handler → Upstash (KV_REST_API_URL / KV_REST_API_TOKEN). Optional LEAD_NOTIFY_WEBHOOK.
- `vercel.json` (clean URLs, trailing slash, caching/security headers), `robots.txt`, `sitemap.xml`, `site.webmanifest`

## Before go-live
1. Footer: replace the two `[ADD NUMBER]` licence placeholders (WA Plumbing Contractor Reg. #, WA L&I Plumber Cert. #) with real numbers.
2. `img/og-home.png` can be swapped for a real truck/founder photo (1200×630).
3. Verify the geo coordinates in the schema/meta (47.1775, -122.1865 — approximate for 15121 198th Ave E) against Google Maps.
4. Set `email` in the schema to the real office address or remove the line.
5. Connect the Upstash store to the Vercel project (same as the Beaverton site) and add env vars.
6. Regenerate `sitemap.xml` once service/area pages are published — only live URLs belong in it.

## Step 3 (this drop) — services hub + 8 service pages
Built from `content/<slug>.html` by `python3 build/build.py` (regenerates `sitemap.xml` too). Edit content fragments, not the generated `services/*/index.html`.

Pages: /services/ · emergency-plumber · water-softener-installation · water-filtration-systems · water-heater-installation · tankless-water-heaters · hot-water-recirculation · expansion-tanks · hose-bibs

### Photo slots (drop real JPGs here; placeholder SVG shows until you do)
All 1200×800 (3:2), JPG, <200 KB:
- img/home-truck.jpg — service truck at a home near Lake Tapps (homepage)
- img/ashino-thomas.jpg — 300×300 founder portrait (homepage; About page later)
- img/services/<slug>-1.jpg and <slug>-2.jpg for each of the 8 slugs above (16 photos). The alt text in each page describes the intended shot.
- Each page's og:image points at <slug>-1.jpg — add that one first.

## Steps 4–5 — remaining 14 service pages
All 22 service pages now exist under /services/<slug>/. Photo slots: img/services/<slug>-1.jpg and -2.jpg for every slug (44 photos total); alt text in each page describes the shot.

## Step 6 — service areas
`python3 build/areas_build.py` builds /service-areas/ (hub with ZIP finder + schematic map) and 12 area pages from build/areas_data_*.py. Run it before build/build.py so the sitemap picks the pages up. Area pages use Google Maps embeds + generated SVG infographics (no photo slots required; add `img/areas/<slug>.jpg` later if you want a hero photo).
