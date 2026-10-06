#!/usr/bin/env python3
"""Build /service-areas/<slug>/ pages and the /service-areas/ hub from build/areas_data.py."""
import json, html, pathlib, datetime, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from areas_data import AREAS
ROOT = pathlib.Path(__file__).resolve().parent.parent
HDR = (ROOT/'partials/header.html').read_text().split('\n',1)[1]
FTR = (ROOT/'partials/footer.html').read_text().split('\n',1)[1]
BASE = 'https://plumbersbonneylake.com'
PHONE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.6 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .6 3.6 1 1 0 0 1-.25 1z" fill="currentColor"/></svg>'
SVC = {'emergency-plumber':'Emergency plumber','water-softener-installation':'Water softener installation','water-filtration-systems':'Water filtration systems','water-heater-installation':'Water heater installation','tankless-water-heaters':'Tankless water heaters','hot-water-recirculation':'Hot water recirculation','expansion-tanks':'Expansion tanks','hose-bibs':'Hose bibs','garbage-disposals':'Garbage disposals','dishwasher-installation':'Dishwasher installation','ice-maker-water-lines':'Ice maker water lines','instant-hot-water-dispensers':'Instant hot water dispensers','toilet-repair-replacement':'Toilet repair & replacement','faucet-repair-replacement':'Faucet repair & replacement','fixture-installation':'Fixture installation','tub-shower-installation':'Tub & shower installation','walk-in-bathtubs':'Walk-in bathtubs','drain-cleaning':'Drain cleaning','water-line-repair':'Water line repair','drain-line-repair':'Drain & sewer line repair','backflow-preventers':'Backflow preventers','repipes-remodels':'Repipes & remodels'}
E = lambda s: html.escape(s, quote=True)

def head(title, desc, url, ld, og=None):
    og = og or f'{BASE}/img/og-home.png'
    return f'''<!DOCTYPE html>
<html lang="en-US">
<head>
<!--
  {url}
  SEO title: {title}
  Meta description: {desc}
  Canonical: {url}
-->
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large"><meta name="geo.region" content="US-WA"><meta name="theme-color" content="#0F2E4A">
<meta property="og:type" content="website"><meta property="og:site_name" content="Plumbers Bonney Lake"><meta property="og:locale" content="en_US">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{og}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/img/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/styles.css">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{HDR}
<main id="main">
'''

def tail(cta_noun):
    return f'''</main>
{FTR}
</body>
</html>
'''

def wrap(txt, n=46, maxlines=2):
    words=txt.split(); lines=[]; cur=''
    for w in words:
        if len(cur)+len(w)+1>n and cur: lines.append(cur); cur=w
        else: cur=(cur+' '+w).strip()
    if cur: lines.append(cur)
    return lines[:maxlines]

def profile_svg(a):
    """SVG infographic: water source, housing era, soil and top risks."""
    def lines(txt,x,y,fs=12.5,n=44):
        return ''.join(f'<text x="{x}" y="{y+i*17}" font-family="Source Sans 3, Arial, sans-serif" font-size="{fs}" fill="#0F2E4A">{E(l)}</text>' for i,l in enumerate(wrap(txt,n)))
    risks=''.join(f'<text x="400" y="{104+i*24}" font-family="Source Sans 3, Arial, sans-serif" font-size="12.5" fill="#0F2E4A">• {E(r[0])}</text>' for i,r in enumerate(a['risks'][:4]))
    bars=''
    for i,(lab,s_,e_) in enumerate(a['era_bar']):
        if s_==e_: s_=1900
        x=30+(s_-1900)*1.6; w=max((e_-s_)*1.6,30)
        bars+=f'<rect x="{x:.0f}" y="{216+i*22}" width="{w:.0f}" height="17" rx="3" fill="{["#1B7F8E","#B8742A","#0F2E4A"][i%3]}" opacity=".88"/><text x="{x+w+6:.0f}" y="{229+i*22}" font-family="Source Sans 3, Arial, sans-serif" font-size="11" fill="#0F2E4A">{E(lab)}</text>'
    return f'''<figure class="diagram">
  <svg viewBox="0 0 720 300" role="img" aria-labelledby="pf{a['slug']}">
    <title id="pf{a['slug']}">Plumbing profile of {E(a['name'])}: water source, typical home eras, soil and the most common plumbing issues</title>
    <rect width="720" height="300" rx="8" fill="#E3F1F3"/>
    <text x="30" y="38" font-family="Barlow Semi Condensed, Arial Narrow, sans-serif" font-size="20" fill="#0F2E4A">{E(a['name'])} plumbing profile</text>
    <line x1="385" y1="60" x2="385" y2="200" stroke="#B9C8D4"/>
    <g font-family="Source Sans 3, Arial, sans-serif" font-size="12.5" fill="#0F2E4A">
      <text x="30" y="76" font-weight="700">Water</text>{lines(a['water_short'],30,94)}
      <text x="30" y="146" font-weight="700">Soil &amp; site</text>{lines(a['soil_short'],30,164)}
      <text x="30" y="206" font-weight="700" font-size="12">Typical home eras (1900 → today)</text>
      {bars}
      <text x="400" y="76" font-weight="700">Most common calls here</text>
      {risks}
      <text x="400" y="226" font-weight="700">From our office</text>{lines(a['drive'],400,244,12,40)}
    </g>
  </svg>
  <figcaption>{E(a['profile_caption'])}</figcaption>
</figure>'''

def tool_html(a):
    """Per-area 'home profile' interactive: water + era + concern → top services with local reasoning."""
    data = json.dumps({'name':a['name'],'water':a['tool_water'],'eras':a['tool_eras'],'risks':[[r[0],r[1],r[2]] for r in a['risks']]}, ensure_ascii=False)
    opts_w = ''.join(f'<option value="{E(k)}">{E(v[0])}</option>' for k,v in a['tool_water'].items())
    opts_e = ''.join(f'<option value="{E(k)}">{E(v[0])}</option>' for k,v in a['tool_eras'].items())
    return f'''<div class="tool" id="ap">
  <h3>What should a {E(a['name'])} homeowner check first?</h3>
  <div class="row three">
    <div><label for="ap-w">Your water comes from</label><select id="ap-w">{opts_w}</select></div>
    <div><label for="ap-e">Home built</label><select id="ap-e">{opts_e}</select></div>
    <div><label for="ap-c">Main concern</label><select id="ap-c"><option value="none">Nothing specific — just curious</option><option value="hot">Hot water problems</option><option value="drain">Slow drains or backups</option><option value="water">Taste, scale, stains</option><option value="leak">Leaks or pressure</option><option value="remodel">Planning a remodel</option></select></div>
  </div>
  <button class="btn btn-outline" type="button" id="ap-go">Show my checklist</button>
  <div class="result" id="ap-out" hidden></div>
</div>
<script>
(function(){{var D={data};var S={json.dumps(SVC)};document.getElementById('ap-go').addEventListener('click',function(){{var w=document.getElementById('ap-w').value,e=document.getElementById('ap-e').value,c=document.getElementById('ap-c').value;var items=[];D.water[w][1].forEach(function(s){{items.push([s,D.water[w][2]])}});D.eras[e][1].forEach(function(s){{items.push([s,D.eras[e][2]])}});var cmap={{hot:['water-heater-installation','tankless-water-heaters','hot-water-recirculation'],drain:['drain-cleaning','drain-line-repair'],water:['water-softener-installation','water-filtration-systems'],leak:['water-line-repair','expansion-tanks','emergency-plumber'],remodel:['repipes-remodels','tub-shower-installation','fixture-installation']}};if(cmap[c]){{cmap[c].forEach(function(s){{items.unshift([s,'Your stated concern.'])}})}}var seen={{}},out=[];items.forEach(function(it){{if(seen[it[0]])return;seen[it[0]]=1;out.push(it)}});out=out.slice(0,5);var o=document.getElementById('ap-out');o.hidden=false;o.innerHTML='<strong>Top checks for your '+D.name+' home</strong><ol style="margin:6px 0 0;padding-left:20px">'+out.map(function(it){{return '<li><a href="/services/'+it[0]+'/">'+S[it[0]]+'</a> — '+it[1]+'</li>'}}).join('')+'</ol>'}})}})();
</script>'''


PERMIT = {
 'lake-tapps':'Lake Tapps is mostly unincorporated Pierce County, with the Bonney Lake and Auburn city limits touching its shores, so permits go through Pierce County Planning and Public Works or the relevant city depending on your address.',
 'sumner':'Permits in Sumner go through the City of Sumner\'s Community Development department; county addresses on the edges go through Pierce County.',
 'buckley':'In-town permits go through the City of Buckley; rural addresses go through Pierce County Planning and Public Works, and septic work involves the Tacoma-Pierce County Health Department.',
 'tehaleh':'Tehaleh is unincorporated Pierce County, so plumbing permits go through Pierce County Planning and Public Works, with Tacoma Water handling cross-connection requirements.',
 'orting':'Permits inside the city go through the City of Orting; river-road and county addresses go through Pierce County, with the Health Department involved for septic.',
 'south-prairie':'The Town of South Prairie handles permits in town; everything around it goes through Pierce County Planning and Public Works and, for septic, the Tacoma-Pierce County Health Department.',
 'puyallup':'Permits in Puyallup go through the City of Puyallup Development Services; South Hill addresses outside the city limits go through Pierce County.',
 'enumclaw':'Enumclaw is in King County, so in-town permits go through the City of Enumclaw and rural addresses through King County Permitting; septic involves Public Health – Seattle & King County.',
 'auburn':'Lakeland Hills straddles the county line: King County addresses permit through the City of Auburn, Pierce County addresses through Pierce County or the City, depending on annexation.',
 'edgewood':'Permits in Edgewood go through the City of Edgewood; Milton through the City of Milton; septic through the Tacoma-Pierce County Health Department.',
 'prairie-ridge':'Prairie Ridge is unincorporated Pierce County, so permits go through Pierce County Planning and Public Works, with the City of Bonney Lake handling water-system cross-connection requirements.',
 'wilkeson-carbonado':'Each town issues its own permits for in-town work; valley addresses go through Pierce County, and septic through the Tacoma-Pierce County Health Department.',
}
def extra_sections(a):
    r=a['risks']
    return f'''<h2>A year of plumbing in {E(a['name'])}</h2>
<p><strong>Late fall.</strong> The first hard freeze is when we get the calls that could have been avoided: disconnect hoses, drain outbuilding lines, and make sure exposed supply runs are insulated. {E(a['name'])} homes with {E(a['soil_short'].lower())} should treat this as a yearly appointment, not a one-time fix.</p>
<p><strong>Winter.</strong> Burst pipes, frozen hose bibs and water heaters that quit on the coldest morning. We dispatch emergencies from Bonney Lake — {E(a['drive'].lower())} — ahead of all scheduled work, and we walk you through the shut-off on the phone while the truck is moving.</p>
<p><strong>Spring.</strong> The leaks winter caused show up when outdoor faucets are first used: a split frost-free stem leaking inside the wall, a crawl-space line weeping at a fitting. It is also sewer season — saturated ground and active roots mean the laterals that are going to back up this year usually do it between March and May. {E(r[0][0])} and {E(r[3][0].lower())} are the two calls we schedule most in {E(a['name'])} at this time of year.</p>
<p><strong>Summer.</strong> Irrigation goes on, which means backflow assembly tests are due and the water heater finally gets the flush it needed. It is the best season for planned work — repipes, remodel rough-ins, water heater replacements before the fall rush — because walls dry fast and the crawl space is at its driest.</p>
<h2>Permits, inspections and who owns what</h2>
<p>{E(PERMIT[a['slug']])} We pull the permit in our name, meet the inspector, and hand you the final — the paperwork matters when you sell. On the utility side, the water purveyor owns the main and the meter; everything from the meter into the house is yours, and that is what we repair. The same split applies to sewer: the lateral from the house to the main is the homeowner\'s, and we confirm the exact connection point with the utility before quoting a line repair.</p>
<h2>What a service call in {E(a['name'])} looks like</h2>
<p>You call <a href="tel:+12534657734">(253) 465-7734</a> and a person answers — 24 hours a day. We ask what is happening, where you are, and whether you have been able to shut anything off, then give you an honest arrival window. On site, your plumber diagnoses the cause rather than the symptom, checks the things {E(a['name'])} homes are prone to ({E(r[0][0].lower())}, {E(r[1][0].lower())}, {E(r[2][0].lower())}), and writes an estimate with options. Nothing beyond the diagnosis is billed until you approve it. Most repairs finish on the first visit because the truck carries the parts {E(a['name'])} houses need; when something has to be ordered, we leave the system safe and usable. Every job comes with a written invoice that notes anything else we saw, so you can plan the next one on your own schedule.</p>'''

def nearby(a):
    return ''.join(f'<li><a href="/service-areas/{s}/">{E(AREAS[s]["name"])}</a></li>' for s in a['nearby'])

def build_area(a):
    url=f"{BASE}/service-areas/{a['slug']}/"
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"Service","@id":url+"#service","name":f"Plumber in {a['name']}, WA","serviceType":"Plumbing","url":url,"description":a['description'],"provider":{"@id":BASE+"/#business"},"areaServed":{"@type":"Place","name":f"{a['name']}, WA","geo":{"@type":"GeoCoordinates","latitude":a['lat'],"longitude":a['lng']}}},
      {"@type":"WebPage","@id":url+"#webpage","url":url,"name":a['title'],"description":a['description'],"isPartOf":{"@id":BASE+"/#website"},"about":{"@id":url+"#service"},"inLanguage":"en-US","breadcrumb":{"@id":url+"#breadcrumb"}},
      {"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Service areas","item":BASE+"/service-areas/"},{"@type":"ListItem","position":3,"name":a['name'],"item":url}]},
      {"@type":"FAQPage","@id":url+"#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}} for q,ans in a['faqs']]}]}
    faqs=''.join(f'<details><summary>{E(q)}</summary><div class="answer"><p>{E(ans)}</p></div></details>' for q,ans in a['faqs'])
    top=''.join(f'<li><a href="/services/{r[1]}/">{E(SVC[r[1]])}</a></li>' for r in a['risks'])
    body=f'''<section class="page-hero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb" style="color:#C9D6E0"><ol><li><a href="/" style="color:#C9D6E0">Home</a></li><li><a href="/service-areas/" style="color:#C9D6E0">Service areas</a></li><li aria-current="page">{E(a['name'])}</li></ol></nav>
<h1>{E(a['h1'])}</h1>
<p class="lede">{E(a['lede'])}</p>
<div class="cta-row"><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a><a class="btn btn-outline on-dark" href="/#request">Get a written estimate</a></div>
</div></section>
<div class="wrap layout">
  <article class="article">
{a['intro']}
{tool_html(a)}
<iframe class="map" style="height:320px;margin:28px 0" title="Map of {E(a['name'])}, Washington" src="https://www.google.com/maps?q={E(a['map_q'])}&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
{a['water_section']}
{profile_svg(a)}
{a['homes_section']}
{a['services_section']}
<div class="callout"><strong>Getting to {E(a['name'])}</strong><br>{E(a['drive_long'])}</div>
{extra_sections(a)}
{a['closing']}
    <h2>Questions from {E(a['name'])} homeowners</h2>
    <div class="faq faq-page">{faqs}</div>
  </article>
  <aside class="aside">
    <div class="card"><h3>Plumber serving {E(a['name'])}</h3><p>24/7 — a person answers, not a call center.</p><a class="fphone" href="tel:+12534657734">(253) 465-7734</a><a class="btn btn-call" href="/#request">Request a written estimate</a></div>
    <div class="card"><h3>Most requested in {E(a['name'])}</h3><ul>{top}<li><a href="/services/">All 22 services</a></li></ul></div>
    <div class="card"><h3>Nearby areas</h3><ul>{nearby(a)}<li><a href="/service-areas/">All service areas</a></li></ul></div>
  </aside>
</div>
<section class="cta-strip"><div class="wrap"><div><h2>Need a plumber in {E(a['name'])}?</h2><p style="color:#C9D6E0;margin:0">Same-day service from Bonney Lake. Written estimate before any work starts.</p></div><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a></div></section>
'''
    out=ROOT/'service-areas'/a['slug']/'index.html'; out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(head(a['title'],a['description'],url,ld)+body+tail(''))
    return url

def build_hub():
    url=BASE+'/service-areas/'
    title="Plumber Service Areas | Bonney Lake & the Plateau"
    desc="Plumbers Bonney Lake serves Lake Tapps, Sumner, Buckley, Tehaleh, Orting, Puyallup, Enumclaw, Auburn and the Plateau from Bonney Lake. Call (253) 465-7734."
    ld={"@context":"https://schema.org","@graph":[
      {"@type":"CollectionPage","@id":url+"#webpage","url":url,"name":title,"description":desc,"isPartOf":{"@id":BASE+"/#website"},"about":{"@id":BASE+"/#business"},"inLanguage":"en-US","breadcrumb":{"@id":url+"#breadcrumb"}},
      {"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Service areas","item":url}]},
      {"@type":"ItemList","@id":url+"#list","itemListElement":[{"@type":"ListItem","position":i+1,"name":a['name'],"url":f"{BASE}/service-areas/{s}/"} for i,(s,a) in enumerate(AREAS.items())]}]}
    # SVG map: positions relative to Bonney Lake (approx lat/lng projected)
    def proj(lat,lng):
        x=360+(lng+122.1865)*1700; y=170-(lat-47.1775)*1500; return x,y
    pins=''
    for s,a in AREAS.items():
        x,y=proj(a['lat'],a['lng']); pins+=f'<a href="/service-areas/{s}/"><circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="#1B7F8E" stroke="#fff" stroke-width="2"/><text x="{x+10:.0f}" y="{y+4:.0f}" font-family="Source Sans 3, Arial, sans-serif" font-size="12" fill="#0F2E4A">{E(a["name"])}</text></a>'
    bx,by=proj(47.1775,-122.1865)
    cards=''.join(f'<a href="/service-areas/{s}/">{E(a["name"])}<small>{E(a["tag"])}</small></a>' for s,a in AREAS.items())
    opts=''.join(f'<option value="{s}">{E(a["name"])}</option>' for s,a in AREAS.items())
    zips={}
    for s,a in AREAS.items():
        for z in a['zips']: zips[z]=s
    body=f'''<section class="page-hero"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb" style="color:#C9D6E0"><ol><li><a href="/" style="color:#C9D6E0">Home</a></li><li aria-current="page">Service areas</li></ol></nav>
<h1>Where We Work: Bonney Lake and the Plateau</h1>
<p class="lede">Our office is on 198th Ave E in Bonney Lake, and our regular routes cover the Plateau, the Puyallup and White River valleys and the foothill towns toward Mount Rainier. Every area below has its own page with the water source, housing stock and the plumbing problems we see most there.</p>
<div class="cta-row"><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a><a class="btn btn-outline on-dark" href="/#request">Get a written estimate</a></div>
</div></section>
<section class="section"><div class="wrap">
<div class="tool" style="margin-top:0" id="zipfind">
  <h3>Are we in your area? Enter your ZIP</h3>
  <div class="row"><div><label for="zf-zip">ZIP code</label><input id="zf-zip" type="text" inputmode="numeric" maxlength="5" placeholder="98391"></div><div><label for="zf-town">…or pick your town</label><select id="zf-town"><option value="">Choose…</option><option value="home">Bonney Lake</option>{opts}</select></div></div>
  <button class="btn btn-outline" type="button" id="zf-go">Check</button>
  <div class="result" id="zf-out" hidden></div>
</div>
<script>(function(){{var Z={json.dumps(zips)};var N={json.dumps({s:a['name'] for s,a in AREAS.items()})};var D={json.dumps({s:a['drive'] for s,a in AREAS.items()})};document.getElementById('zf-go').addEventListener('click',function(){{var z=document.getElementById('zf-zip').value.trim(),t=document.getElementById('zf-town').value,o=document.getElementById('zf-out');o.hidden=false;var s=t||Z[z];if(t==='home'||z==='98391'&&!t){{o.innerHTML='<strong>Bonney Lake — that\\'s home</strong>Our office is here; most addresses are minutes away. <a href="/">Back to the homepage</a> or call now.';return}}if(s&&N[s]){{o.innerHTML='<strong>Yes — we serve '+N[s]+'</strong>'+D[s]+'. <a href="/service-areas/'+s+'/">See the '+N[s]+' page</a> for local water and plumbing notes.';return}}o.innerHTML='<strong>Not on our regular route list</strong>That doesn\\'t mean no — we take calls across Pierce and south King County. Call (253) 465-7734 and we\\'ll tell you honestly whether we can get there quickly.'}})}})();</script>
<figure class="diagram">
  <svg viewBox="0 0 720 340" role="img" aria-labelledby="areaMap">
    <title id="areaMap">Schematic map of Plumbers Bonney Lake's service area with Bonney Lake at the center and the twelve surrounding communities positioned by direction and distance</title>
    <rect width="720" height="340" rx="8" fill="#E3F1F3"/>
    <circle cx="{bx:.0f}" cy="{by:.0f}" r="95" fill="none" stroke="#B8742A" stroke-width="1.5" stroke-dasharray="6 5"/><circle cx="{bx:.0f}" cy="{by:.0f}" r="190" fill="none" stroke="#B8742A" stroke-width="1" stroke-dasharray="4 6" opacity=".6"/>
    <text x="{bx+70:.0f}" y="{by-80:.0f}" font-family="Source Sans 3, Arial, sans-serif" font-size="11" fill="#8F5A1F">~10 min</text><text x="{bx+150:.0f}" y="{by-150:.0f}" font-family="Source Sans 3, Arial, sans-serif" font-size="11" fill="#8F5A1F">~25 min</text>
    {pins}
    <rect x="{bx-10:.0f}" y="{by-10:.0f}" width="20" height="20" rx="4" fill="#B8742A" stroke="#0F2E4A" stroke-width="2"/><text x="{bx+14:.0f}" y="{by-12:.0f}" font-family="Barlow Semi Condensed, Arial Narrow, sans-serif" font-size="14" font-weight="700" fill="#0F2E4A">Bonney Lake (office)</text>
    <text x="20" y="325" font-family="Source Sans 3, Arial, sans-serif" font-size="11" fill="#4A5862">Schematic, not to scale. Click a town for its page.</text>
  </svg>
  <figcaption>Everything inside the inner ring is a same-day call on a normal day; the outer ring is a short drive up SR 410, SR 162 or SR 167.</figcaption>
</figure>
<div class="areas">{cards}</div>
<h2 style="margin-top:48px">Why we publish a page for each town</h2>
<p>Plumbing on the Plateau isn't uniform. Bonney Lake proper is on the City's spring and well water; Tehaleh is on Tacoma Water; Sumner and Orting have their own spring-fed systems; Buckley, South Prairie and the Carbon River towns mix small municipal systems with private wells. Housing runs from 1900s valley farmhouses to 2020s master-planned subdivisions. A plumber who knows which you've got brings the right parts and asks the right questions. Each area page tells you what we know about your town's water, your neighborhood's housing era, and the three or four plumbing problems we're called about most there.</p>
<h2>How far will we go?</h2>
<p>Our regular routes are the twelve communities above plus Bonney Lake itself. We also take calls in neighboring areas — Pacific, Algona, Milton, Graham, Black Diamond, Greenwater — when the schedule allows. If you're outside the list, call: we'll give you an honest answer about timing rather than a drive charge you didn't expect. Emergency calls are prioritized by severity and distance; a burst pipe in Enumclaw gets a truck before a dripping faucet in Sumner.</p>
<iframe class="map" style="height:360px;margin:28px 0" title="Map of Plumbers Bonney Lake service area" src="https://www.google.com/maps?q=Bonney+Lake,+WA&amp;z=10&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</div></section>
<section class="cta-strip"><div class="wrap"><div><h2>Talk to a Bonney Lake plumber</h2><p style="color:#C9D6E0;margin:0">24/7 — a person answers, not a call center.</p></div><a class="btn btn-call" href="tel:+12534657734">{PHONE_SVG}Call (253) 465-7734</a></div></section>
'''
    (ROOT/'service-areas').mkdir(exist_ok=True)
    (ROOT/'service-areas/index.html').write_text(head(title,desc,url,ld)+body+tail(''))
    return url,title,desc

if __name__=='__main__':
    urls=[]
    for s,a in AREAS.items():
        urls.append(build_area(a)); print(f"{s}: title {len(a['title'])} | desc {len(a['description'])} | h1 {len(a['h1'])}")
    u,t,d=build_hub(); print('hub',len(t),len(d))
