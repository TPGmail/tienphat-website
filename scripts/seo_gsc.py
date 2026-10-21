#!/usr/bin/env python3
"""SEO audit and (after Google Cloud authorization) Search Console sync."""
import os, sys, re, json, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET
from pathlib import Path
DOMAIN="https://www.tienphat.org"
PROPERTY="sc-domain:tienphat.org"
SLUGS=["index.html","da-pu-pho-thong.html","da-pu-nubuck.html","da-that.html"]
LANGS=["en","vi","zh"]
def path_for(slug, lang):
    return Path(slug if lang=="en" else lang+"/"+slug)
def url_for(slug, lang):
    return DOMAIN+("" if lang=="en" else "/"+lang)+("/" if slug=="index.html" else "/"+slug)
def audit():
    root=ET.parse("sitemap.xml").getroot()
    ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9","x":"http://www.w3.org/1999/xhtml"}
    entries=root.findall("s:url", ns)
    urls=[e.findtext("s:loc",namespaces=ns) for e in entries]
    expected=[url_for(s,l) for s in SLUGS for l in LANGS]
    problems=[]
    if len(urls)!=12 or set(urls)!=set(expected): problems.append("Sitemap does not contain exactly 12 distinct expected URLs")
    for slug in SLUGS:
        for lang in LANGS:
            path=path_for(slug,lang)
            if not path.is_file():
                problems.append(f"Missing {path}"); continue
            html=path.read_text(encoding="utf-8")
            url=url_for(slug,lang)
            required=[f'<html lang="{lang}"',f'rel="canonical" href="{url}"',f'property="og:url" content="{url}"']
            for loc in LANGS+["x-default"]:
                target=url_for(slug,"en" if loc=="x-default" else loc)
                required.append(f'hreflang="{loc}" href="{target}"')
            for token in required:
                if token not in html: problems.append(f"{path}: missing {token[:55]}")
            if len(re.findall(r"<h1\b",html))!=1: problems.append(f"{path}: not exactly one H1")
            if not re.search(r"<title>[^<]+</title>",html): problems.append(f"{path}: missing SEO title")
            if 'name="description"' not in html: problems.append(f"{path}: missing SEO description")
            if re.search(r'(?:href|src)="assets/',html): problems.append(f"{path}: broken relative asset path")
    for e in entries:
        loc=e.findtext("s:loc",namespaces=ns)
        matches=[s for s in SLUGS if loc in [url_for(s,l) for l in LANGS]]
        if not matches: continue
        alt={x.attrib.get("hreflang"):x.attrib.get("href") for x in e.findall("x:link",ns)}
        for lang in LANGS+["x-default"]:
            target=url_for(matches[0],"en" if lang=="x-default" else lang)
            if alt.get(lang)!=target: problems.append(f"Sitemap hreflang mismatch: {loc} {lang}")
    for p in problems: print("ERROR:",p,file=sys.stderr)
    print(f"SEO audit: {len(expected)} expected URLs; {len(problems)} problems")
    if problems: sys.exit(1)
def request(method,url,token,body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=data,method=method,headers={"Authorization":"Bearer "+token,**({"Content-Type":"application/json"} if body is not None else {})})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            raw=r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Google API HTTP {e.code}: {e.read().decode(errors='replace')[:400]}") from None
def sync(submit):
    token=os.getenv("GSC_ACCESS_TOKEN")
    if not token: sys.exit("Missing authorized GSC_ACCESS_TOKEN. Configure Workload Identity Federation.")
    if submit:
        endpoint="https://www.googleapis.com/webmasters/v3/sites/"+urllib.parse.quote(PROPERTY,safe="")+"/sitemaps/"+urllib.parse.quote(DOMAIN+"/sitemap.xml",safe="")
        request("PUT",endpoint,token)
        print("Sitemap submitted")
    rows=[]
    for slug in SLUGS:
        for lang in LANGS:
            url=url_for(slug,lang)
            response=request("POST","https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",token,{"inspectionUrl":url,"siteUrl":PROPERTY})
            info=response.get("inspectionResult",{}).get("indexStatusResult",{})
            rows.append((url,info.get("verdict","UNKNOWN"),info.get("coverageState","UNKNOWN")))
            print(json.dumps({"url":url,"verdict":rows[-1][1],"coverage":rows[-1][2]},ensure_ascii=False))
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("## Search Console — 12 URLs\n\n| URL | Verdict | Coverage |\n|---|---|---|\n")
            for url,verdict,coverage in rows: f.write(f"| {url} | {verdict} | {coverage} |\n")
if __name__=="__main__":
    if sys.argv[1:2]==["audit"]: audit()
    elif sys.argv[1:2]==["sync"]: sync("--submit" in sys.argv[2:])
    else: sys.exit("Usage: python scripts/seo_gsc.py audit|sync [--submit]")
