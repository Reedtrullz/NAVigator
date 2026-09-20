import html as h
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}


def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.getcode(), r.read()
    except Exception as e:
        return 0, str(e).encode()


def page_text(raw, direct=True):
    if direct:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "ignore")
        raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
        return re.sub(r"\s+", " ", h.unescape(re.sub(r"<[^>]+>", " ", raw)))
    return raw.decode("utf-8", "ignore")


def show(tag, url, direct=True, pats=None):
    code, body = fetch(url)
    via = "direct" if direct else "jina"
    if (code != 200 or len(body) < 500) and direct:
        code2, body2 = fetch("https://r.jina.ai/" + url)
        if code2 == 200:
            code, body, via = code2, body2, "jina"
            return show(tag, url, direct=False)
    txt = page_text(body, direct and via == "direct")
    print(f"== {tag} status={code} via={via} chars={len(txt)}")
    if pats:
        for m in re.finditer(pats, txt, re.I):
            s, e = max(0, m.start() - 100), min(len(txt), m.end() + 130)
            print("   ..." + txt[s:e] + "...")
    return txt

# T1 edge target: Alta Tjenestekontor contact details
show("T1-tjenestekontor", "https://www.alta.kommune.no/tjenester/helse-og-omsorg/tjenestekontor",
     pats=r"(tlf|telefon|e-post|epost|\d{2} \d{2} \d{2} \d{2}|\d{8})")

# T5 full text (review, no new fetch semantics)
code, body = fetch("https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/kommunepsykolog/")
txt = page_text(body)
body_txt = txt[txt.find("Du er her"):][:2600] if "Du er her" in txt else txt[:2600]
print("== T5 main text ==")
print(body_txt)

# T9: Hasvik - FFR page + health catalog listing (bounded)
show("T9-FFR", "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsetjenester/rus-og-psykiatri/psykisk-helse",
     pats=r"(lavterskel|ta kontakt|ring|telefon|\d{2} \d{2} \d{2} \d{2}|helsesykepleier|drop-?in|time)")
show("T9-katalog", "https://hasvik.kommune.no/tjenester/helse-og-omsorg",
     pats=r"(helsesykepleier|skolehelse|psykisk|helsestasjon)")
