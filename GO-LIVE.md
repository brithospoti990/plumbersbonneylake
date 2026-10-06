# plumbersbonneylake.com — go-live checklist

## 1. Repo + Vercel
- Push this folder to the GitHub repo root. Vercel: Framework = Other, no build command, output = root.
- Add a custom domain (plumbersbonneylake.com + www → redirect to apex). Vercel issues SSL automatically.
- Project → Storage: connect the Upstash KV store (same one as the Beaverton site) so `KV_REST_API_URL` / `KV_REST_API_TOKEN` exist. Optional `LEAD_NOTIFY_WEBHOOK` (Zapier/Make/email) to get a ping per lead.
- Test the form on /contact/ and /#request after deploy; leads land in Upstash under `leads:index`.

## 2. Fill the placeholders (search the repo for `[ADD NUMBER]`)
- Footer in `partials/footer.html` AND every built page: WA Plumbing Contractor Reg. # and L&I Plumber Cert. #. Edit the partial, then re-run the three build scripts so every page picks it up:
  `python3 build/pages_build.py && python3 build/areas_build.py && python3 build/build.py`
- `index.html` head: uncomment and fill the Google / Bing verification meta tags.
- Schema `email` in `index.html` (office@plumbersbonneylake.com) — set to real or remove.
- Geo coordinates (47.1775, -122.1865) — confirm against Google Maps for 15121 198th Ave E.
- Reviews page links: swap the Google/Yelp/Nextdoor search URLs for the real profile URLs once created.

## 3. Photos (placeholder SVG shows until added) — all 1200×800 JPG under 200 KB
- img/home-truck.jpg, img/ashino-thomas.jpg (300×300 is fine), img/reviews-job.jpg, img/og-home.png (replace with a real 1200×630)
- img/services/<slug>-1.jpg and <slug>-2.jpg for all 22 service slugs (44 photos). Alt text in each page describes the intended shot.

## 4. Search engines
- Google Search Console: add property, verify, submit https://plumbersbonneylake.com/sitemap.xml (44 URLs; privacy/terms are noindex).
- Bing Webmaster Tools: same.
- Google Business Profile: this is the #1 lever for the map pack. The "3rd Floor, Ste Executive" address will likely need to be set up as a service-area business (hide address) unless the suite is staffed during posted hours. Match NAP exactly: Plumbers Bonney Lake · 15121 198th Ave E, 3rd Floor, Ste Executive, Bonney Lake, WA 98391 · (253) 465-7734.
- Citations with identical NAP: Yelp, Angi, HomeAdvisor, Nextdoor, BBB, Apple Maps, Bing Places, Yellow Pages, L&I contractor lookup link on the About page.

## 5. After launch
- Link GBP and Yelp profile URLs into the Plumber schema `sameAs` on index.html.
- Once real reviews exist, add `aggregateRating` to the Plumber node (never before).
- Post 1 guide/month; the pages_build.py pipeline makes it a one-file add.
