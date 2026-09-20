import html as h
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}


def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.getcode(), r.read().decode("utf-8", "ignore")
    except Exception as e:
        return 0, str(e)


def links(raw):
    out = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S | re.I):
        href = m.group(1)
        label = re.sub(r"\s+", " ", h.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        out.append((href, label))
    return out


# T1: Alta - find Tjenestekontoret contact link (level 2 edge)
code, raw = fetch("https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus")
print("T1 page", code)
for href, label in links(raw):
    if re.search(r"tjenestekontor|kontakt", href + " " + label, re.I):
        print("  EDGE:", label[:60], "->", href[:120])

# T4: Ulstein - find application form link (level 2 edge)
code, raw = fetch("https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/teneste-for-psykisk-helse-og-rus/")
print("T4 page", code)
for href, label in links(raw):
    if re.search(r"skjema|soknad|søknad", href + " " + label, re.I):
        print("  EDGE:", label[:60], "->", href[:120])

# T8: Askvoll - look for intake/how-to-apply subpages (level 2)
code, raw = fetch("https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/psykisk-helse-og-rusteneste-for-vaksne/")
print("T8 page", code)
seen = set()
for href, label in links(raw):
    if re.search(r"psykisk|rus|soknad|søknad|skjema|søk", href + " " + label, re.I) and href not in seen:
        seen.add(href)
        print("  LINK:", label[:60], "->", href[:120])

# T9: Hasvik - sitemap grep (level 3)
code, raw = fetch("https://hasvik.kommune.no/sitemap.xml")
print("T9 sitemap", code, len(raw))
for m in re.finditer(r"<loc>([^<]+)</loc>", raw):
    u = m.group(1)
    if re.search(r"helse|skole|psykisk|rus", u, re.I):
        print("  LOC:", u)
