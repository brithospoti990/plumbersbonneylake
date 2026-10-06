#!/usr/bin/env python3
"""Build service/area pages from content/<slug>.html fragments.
Fragment = <!--META {json}--> followed by article HTML. Run: python3 build/build.py
Also updates sitemap.xml with every built page."""
import json, re, os, html, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
HDR = (ROOT/'partials/header.html').read_text().split('\n',1)[1]
FTR = (ROOT/'partials/footer.html').read_text().split('\n',1)[1]
BASE = 'https://plumbersbonneylake.com'
PHONE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.6 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .6 3.6 1 1 0 0 1-.25 1z" fill="currentColor"/></svg>'

SERVICES = {  # slug: (name, silo)
 'emergency-plumber':('Emergency plumber','Emergency & water treatment'),
 'water-softener-installation':('Water softener installation','Emergency & water treatment'),
 'water-filtration-systems':('Water filtration systems','Emergency & water treatment'),
 'water-heater-installation':('Water heater installation','Water heaters'),
 'tankless-water-heaters':('Tankless water heaters','Water heaters'),
 'hot-water-recirculation':('Hot water recirculation','Water heaters'),
 'expansion-tanks':('Expansion tanks','Water heaters'),
 'hose-bibs':('Hose bibs','Water heaters'),
 'garbage-disposals':('Garbage disposals','Kitchen & appliances'),
 'dishwasher-installation':('Dishwasher installation','Kitchen & appliances'),
 'ice-maker-water-lines':('Ice maker water lines','Kitchen & appliances'),
 'instant-hot-water-dispensers':('Instant hot water dispensers','Kitchen & appliances'),
 'toilet-repair-replacement':('Toilet repair & replacement','Bathroom & fixtures'),
 'faucet-repair-replacement':('Faucet repair & replacement','Bathroom & fixtures'),
 'fixture-installation':('Fixture installation','Bathroom & fixtures'),
 'tub-shower-installation':('Tub & shower installation','Bathroom & fixtures'),
 'walk-in-bathtubs':('Walk-in bathtubs','Bathroom & fixtures'),
 'drain-cleaning':('Drain cleaning','Pipes, drains & remodels'),
 'water-line-repair':('Water line repair','Pipes, drains & remodels'),
 'drain-line-repair':('Drain & sewer line repair','Pipes, drains & remodels'),
 'backflow-preventers':('Backflow preventers','Pipes, drains & remodels'),
 'repipes-remodels':('Repipes & remodels','Pipes, drains & remodels'),
}
AREAS = ['lake-tapps','sumner','buckley','tehaleh','orting','south-prairie','puyallup','enumclaw','auburn','edgewood','prairie-ridge','wilkeson-carbonado']

def esc(s): return html.escape(s, quote=True)

def sidebar(meta):
    slug = meta['slug']; silo = SERVICES.get(slug,('',''))[1]
    sibs = ''.join(f'<li><a href="/services/{k}/"{" aria-current=\"page\"" if k==slug else ""}>{esc(v[0])}</a></li>' for k,v in SERVICES.items() if v[1]==silo)
    areas = ''.join(f'<li><a href="/service-areas/{a}/">{a.replace("-"," ").title().replace(" And "," & ")}</a></li>' for a in AREAS[:6])
    return f'''<aside class="aside">
  <div class="card"><h3>Talk to a Bonney Lake plumber</h3><p>24/7 — a person answers, not a call center.</p><a class="fphone" href="tel:+12534657734">(253) 465-7734</a><a class="btn btn-call" href="/#request">Request a written estimate</a></div>
  <div class="card"><h3>{esc(silo)}</h3><ul>{sibs}</ul></div>
  <div class="card"><h3>Where we work</h3><ul>{areas}<li><a href="/service-areas/">All service areas</a></li></ul></div>
</aside>'''

def faq_html(faqs):
    return ''.join(f'<details><summary>{esc(q)}</summary><div class="answer"><p>{esc(a)}</p></div></details>' for q,a in faqs)

def schema(meta):
    url = f"{BASE}/services/{meta['slug']}/"
    g = [
     {"@type":"Service","@id":url+"#service","name":meta['service_name'],"serviceType":meta['service_name'],"url":url,
      "description":meta['description'],"provider":{"@id":BASE+"/#business"},
      "areaServed":[{"@type":"City","name":"Bonney Lake, WA"}]+[{"@type":"Place","name":a.replace('-',' ').title()+", WA"} for a in AREAS],
      "offers":{"@type":"Offer","availability":"https://schema.org/InStock","url":url}},
     {"@type":"WebPage","@id":url+"#webpage","url":url,"name":meta['title'],"description":meta['description'],
      "isPartOf":{"@id":BASE+"/#website"},"about":{"@id":url+"#service"},"inLanguage":"en-US",
      "breadcrumb":{"@id":url+"#breadcrumb"}},
     {"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":"Services","item":BASE+"/services/"},
        {"@type":"ListItem","position":3,"name":meta['service_name'],"item":url}]},
     {"@type":"FAQPage","@id":url+"#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in meta['faqs']]}
    ]
    return json.dumps({"@context":"https://schema.org","@graph":g}, ensure_ascii=False, indent=1)

def build_service(path):
    raw = path.read_text()
    m = re.match(r'\s*<!--META\s*(\{.*?\})\s*-->', raw, re.S)
    meta = json.loads(m.group(1)); body = raw[m.end():]
    slug = meta['slug']; meta['service_name']=SERVICES[slug][0]
    url = f"{BASE}/services/{slug}/"
    hdr = HDR.replace('<li><a href="/">Home</a></li>','<li><a href="/">Home</a></li>')
    page = f'''<!DOCTYPE html>
<html lang="en-US">
<head>
<!--
  {url}
  SEO title: {meta['title']}
  Meta description: {meta['description']}
  Canonical: {url}
  H1: {meta['h1']}
-->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(meta['title'])}</title>
<meta name="description" content="{esc(meta['description'])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="geo.region" content="US-WA"><meta name="geo.placename" content="Bonney Lake">
<meta name="theme-color" content="#0F2E4A">
<meta property="og:type" content="website"><meta property="og:site_name" content="Plumbers Bonney Lake"><meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(meta['title'])}">
<meta property="og:description" content="{esc(meta['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/img/services/{slug}-1.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(meta['title'])}">
<meta name="twitter:description" content="{esc(meta['description'])}">
<meta name="twitter:image" content="{BASE}/img/services/{slug}-1.jpg">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/img/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/styles.css">
<script type="application/ld+json">
{schema(meta)}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{hdr}
<main id="main">
<section class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb" style="color:#C9D6E0"><ol><li><a href="/" style="color:#C9D6E0">Home</a></li><li><a href="/services/" style="color:#C9D6E0">Services</a></li><li aria-current="page">{esc(meta['service_name'])}</li></ol></nav>
    <h1>{esc(meta['h1'])}</h1>
    <p class="lede">{esc(meta['lede'])}</p>
    <div class="cta-row"><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a><a class="btn btn-outline on-dark" href="/#request">Get a written estimate</a></div>
  </div>
</section>
<div class="wrap layout">
  <article class="article">
{body}
    <h2>Questions Bonney Lake homeowners ask about {esc(meta['service_name'].lower())}</h2>
    <div class="faq faq-page">{faq_html(meta['faqs'])}</div>
  </article>
  {sidebar(meta)}
</div>
<section class="cta-strip"><div class="wrap"><div><h2>Need {esc(meta['cta_noun'])} in Bonney Lake?</h2><p style="color:#C9D6E0;margin:0">Same-day appointments across the Plateau. Written estimate before any work starts.</p></div><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a></div></section>
</main>
{FTR}
</body>
</html>
'''
    out = ROOT/'services'/slug/'index.html'; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(page)
    return url, meta

def sitemap(urls):
    today = datetime.date.today().isoformat()
    items = ''.join(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>{"weekly" if u.endswith(".com/") else "monthly"}</changefreq><priority>{p}</priority></url>\n' for u,p in urls)
    (ROOT/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}</urlset>\n')

if __name__ == '__main__':
    urls=[(BASE+'/','1.0')]
    report=[]
    for p in sorted((ROOT/'content').glob('*.html')):
        u,m = build_service(p); urls.append((u,'0.9')); report.append(m)
    if (ROOT/'services/index.html').exists(): urls.insert(1,(BASE+'/services/','0.9'))
    if (ROOT/'service-areas/index.html').exists():
        urls.append((BASE+'/service-areas/','0.8'))
        for d in sorted((ROOT/'service-areas').iterdir()):
            if d.is_dir() and (d/'index.html').exists(): urls.append((BASE+'/service-areas/'+d.name+'/','0.8'))
    for extra in ['about','reviews','guides','faq','contact','privacy','terms']:
        if (ROOT/extra/'index.html').exists(): urls.append((BASE+'/'+extra+'/','0.5' if extra in ('privacy','terms') else '0.7'))
    sitemap(urls)
    for m in report:
        print(f"{m['slug']}: title {len(m['title'])} | desc {len(m['description'])} | h1 {len(m['h1'])}")
