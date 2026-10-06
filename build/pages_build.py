#!/usr/bin/env python3
"""Build company pages (/about/, /reviews/, /faq/, /contact/, /privacy/, /terms/, /guides/) and guide
articles (/guides/<slug>/) from content-pages/<path>.html fragments with a leading <!--META {json}--> block.
META keys: path, title, description, h1, lede, kind (company|guide|hub), faqs (optional), date (guides),
related (list of service slugs), image (optional og image path)."""
import json, re, html, pathlib, datetime, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
ROOT = pathlib.Path(__file__).resolve().parent.parent
HDR = (ROOT/'partials/header.html').read_text().split('\n',1)[1]
FTR = (ROOT/'partials/footer.html').read_text().split('\n',1)[1]
BASE = 'https://plumbersbonneylake.com'
PHONE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.6 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .6 3.6 1 1 0 0 1-.25 1z" fill="currentColor"/></svg>'
SVC = {'emergency-plumber':'Emergency plumber','water-softener-installation':'Water softener installation','water-filtration-systems':'Water filtration systems','water-heater-installation':'Water heater installation','tankless-water-heaters':'Tankless water heaters','hot-water-recirculation':'Hot water recirculation','expansion-tanks':'Expansion tanks','hose-bibs':'Hose bibs','garbage-disposals':'Garbage disposals','dishwasher-installation':'Dishwasher installation','ice-maker-water-lines':'Ice maker water lines','instant-hot-water-dispensers':'Instant hot water dispensers','toilet-repair-replacement':'Toilet repair & replacement','faucet-repair-replacement':'Faucet repair & replacement','fixture-installation':'Fixture installation','tub-shower-installation':'Tub & shower installation','walk-in-bathtubs':'Walk-in bathtubs','drain-cleaning':'Drain cleaning','water-line-repair':'Water line repair','drain-line-repair':'Drain & sewer line repair','backflow-preventers':'Backflow preventers','repipes-remodels':'Repipes & remodels'}
E = lambda s: html.escape(s, quote=True)

def load():
    pages=[]
    for p in sorted((ROOT/'content-pages').glob('*.html')):
        raw=p.read_text(); m=re.match(r'\s*<!--META\s*(\{.*?\})\s*-->',raw,re.S)
        meta=json.loads(m.group(1)); meta['body']=raw[m.end():]; pages.append(meta)
    return pages

def crumbs(meta):
    parts=[('Home','/')]
    if meta['kind']=='guide': parts.append(('Guides','/guides/'))
    items=''.join(f'<li><a href="{h}" style="color:#C9D6E0">{E(n)}</a></li>' for n,h in parts)
    return f'<nav class="crumbs" aria-label="Breadcrumb" style="color:#C9D6E0"><ol>{items}<li aria-current="page">{E(meta["crumb"] if "crumb" in meta else meta["h1"])}</li></ol></nav>'

def schema(meta, guides):
    url=BASE+meta['path']
    bl=[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"}]
    if meta['kind']=='guide': bl.append({"@type":"ListItem","position":2,"name":"Guides","item":BASE+"/guides/"})
    bl.append({"@type":"ListItem","position":len(bl)+1,"name":meta.get('crumb',meta['h1']),"item":url})
    g=[{"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":bl}]
    if meta['kind']=='guide':
        g.append({"@type":"Article","@id":url+"#article","headline":meta['h1'],"description":meta['description'],"url":url,"mainEntityOfPage":url,
                  "datePublished":meta['date'],"dateModified":meta['date'],"inLanguage":"en-US",
                  "author":{"@id":BASE+"/#ashino-thomas"},"publisher":{"@id":BASE+"/#business"},
                  "image":BASE+meta.get('image','/img/og-home.png'),"about":[{"@type":"Thing","name":SVC[s]} for s in meta.get('related',[])]})
    elif meta['path']=='/about/':
        g.append({"@type":"AboutPage","@id":url+"#webpage","url":url,"name":meta['title'],"description":meta['description'],"isPartOf":{"@id":BASE+"/#website"},"about":{"@id":BASE+"/#business"},"mainEntity":{"@id":BASE+"/#ashino-thomas"},"breadcrumb":{"@id":url+"#breadcrumb"}})
    elif meta['path']=='/contact/':
        g.append({"@type":"ContactPage","@id":url+"#webpage","url":url,"name":meta['title'],"description":meta['description'],"isPartOf":{"@id":BASE+"/#website"},"about":{"@id":BASE+"/#business"},"breadcrumb":{"@id":url+"#breadcrumb"}})
    elif meta['kind']=='hub':
        g.append({"@type":"CollectionPage","@id":url+"#webpage","url":url,"name":meta['title'],"description":meta['description'],"isPartOf":{"@id":BASE+"/#website"},"breadcrumb":{"@id":url+"#breadcrumb"}})
        g.append({"@type":"ItemList","@id":url+"#list","itemListElement":[{"@type":"ListItem","position":i+1,"name":x['h1'],"url":BASE+x['path']} for i,x in enumerate(guides)]})
    else:
        g.append({"@type":"WebPage","@id":url+"#webpage","url":url,"name":meta['title'],"description":meta['description'],"isPartOf":{"@id":BASE+"/#website"},"about":{"@id":BASE+"/#business"},"breadcrumb":{"@id":url+"#breadcrumb"}})
    if meta.get('faqs'):
        g.append({"@type":"FAQPage","@id":url+"#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in meta['faqs']]})
    return json.dumps({"@context":"https://schema.org","@graph":g},ensure_ascii=False,indent=1)

def aside(meta, guides):
    rel=''.join(f'<li><a href="/services/{s}/">{E(SVC[s])}</a></li>' for s in meta.get('related',[]))
    others=''.join(f'<li><a href="{x["path"]}">{E(x["h1"])}</a></li>' for x in guides if x['path']!=meta['path'])[:2000]
    blocks=f'<div class="card"><h3>Talk to a Bonney Lake plumber</h3><p>24/7 — a person answers, not a call center.</p><a class="fphone" href="tel:+12534657734">(253) 465-7734</a><a class="btn btn-call" href="/#request">Request a written estimate</a></div>'
    if rel: blocks+=f'<div class="card"><h3>Related services</h3><ul>{rel}</ul></div>'
    if meta['kind']=='guide': blocks+=f'<div class="card"><h3>More guides</h3><ul>{others}<li><a href="/guides/">All guides</a></li></ul></div>'
    return f'<aside class="aside">{blocks}</aside>'

def build(meta, guides):
    url=BASE+meta['path']; og=BASE+meta.get('image','/img/og-home.png')
    faqs=''
    if meta.get('faqs'):
        faqs='<h2>'+E(meta.get('faq_title','Frequently asked questions'))+'</h2><div class="faq faq-page">'+''.join(f'<details><summary>{E(q)}</summary><div class="answer"><p>{E(a)}</p></div></details>' for q,a in meta['faqs'])+'</div>'
    byline=''
    if meta['kind']=='guide':
        d=datetime.date.fromisoformat(meta['date']).strftime('%B %-d, %Y')
        byline=f'<p style="color:#C9D6E0;margin:-6px 0 14px;font-size:.95rem">By <a href="/about/" style="color:#fff">Ashino Thomas</a>, founder · {d}</p>'
    wide = meta.get('wide', False)
    if wide:
        main=f'<section class="section"><div class="wrap">{meta["body"]}{faqs}</div></section>'
    else:
        main=f'<div class="wrap layout"><article class="article">{meta["body"]}{faqs}</article>{aside(meta,guides)}</div>'
    page=f'''<!DOCTYPE html>
<html lang="en-US">
<head>
<!--
  {url}
  SEO title: {meta['title']}
  Meta description: {meta['description']}
  Canonical: {url}
  H1: {meta['h1']}
-->
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(meta['title'])}</title>
<meta name="description" content="{E(meta['description'])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{meta.get('robots','index, follow, max-image-preview:large')}"><meta name="geo.region" content="US-WA"><meta name="theme-color" content="#0F2E4A">
<meta property="og:type" content="{'article' if meta['kind']=='guide' else 'website'}"><meta property="og:site_name" content="Plumbers Bonney Lake"><meta property="og:locale" content="en_US">
<meta property="og:title" content="{E(meta['title'])}"><meta property="og:description" content="{E(meta['description'])}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(meta['title'])}"><meta name="twitter:description" content="{E(meta['description'])}"><meta name="twitter:image" content="{og}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/img/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/styles.css">
<script type="application/ld+json">
{schema(meta,guides)}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{HDR}
<main id="main">
<section class="page-hero"><div class="wrap">
{crumbs(meta)}
<h1>{E(meta['h1'])}</h1>
{byline}
<p class="lede">{E(meta['lede'])}</p>
<div class="cta-row"><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a><a class="btn btn-outline on-dark" href="/#request">Get a written estimate</a></div>
</div></section>
{main}
<section class="cta-strip"><div class="wrap"><div><h2>Talk to a Bonney Lake plumber</h2><p style="color:#C9D6E0;margin:0">Same-day service across the Plateau. Written estimate before any work starts.</p></div><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a></div></section>
</main>
{FTR}
</body>
</html>
'''
    out=ROOT/meta['path'].strip('/')/'index.html'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(page)

if __name__=='__main__':
    pages=load(); guides=[p for p in pages if p['kind']=='guide']
    # guide hub gets its list injected
    for p in pages:
        if p['kind']=='hub':
            cards=''.join(f'<div class="silo"><h3><a href="{x["path"]}" style="text-decoration:none;color:inherit">{E(x["h1"])}</a></h3><p style="color:var(--ink-soft);font-size:.98rem">{E(x["description"].split(" Call")[0])}</p><a class="more" href="{x["path"]}">Read the guide →</a></div>' for x in guides)
            p['body']=p['body'].replace('<!--GUIDE_CARDS-->',f'<div class="hub-grid">{cards}</div>')
        build(p,guides); print(f"{p['path']:50} title {len(p['title'])} | desc {len(p['description'])}")
