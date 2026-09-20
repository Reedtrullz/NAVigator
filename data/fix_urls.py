#!/usr/bin/env python3
import json

MAPPING = {
    "https://bykle.kommune.no/_f/p1/if30cd7d-c60d-4f36-a1c0-375d72f20a32/bykle-organisasjonskart-2026.pdf":
        "https://www.bykle.kommune.no/tenester/helse-og-omsorg/helsetenesta-i-bykle-og-valle/",
    "https://www.alta.kommune.no/nyhetsarkiv/nyheter/2026-06-24-nytt-gruppetilbud-for-foreldre---parenthood-rus":
        "https://www.alta.kommune.no/tjenester/helse-og-omsorg/helsetjenester/helsestasjon--og-skolehelsetjenesten/helsestasjon-for-ungdom/",
    "https://www.alta.kommune.no/tjenester/helse-og-omsorg/helsetjenester/helsestasjon--og-skolehelsetjenesten/helsestasjon-for-ungdom/hva-er-helsestasjon-for-ungdom":
        "https://www.alta.kommune.no/tjenester/helse-og-omsorg/helsetjenester/helsestasjon--og-skolehelsetjenesten/helsestasjon-for-ungdom/",
    "https://www.lorenskog.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-avhengighet/":
        "https://www.lorenskog.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-avhengighet/helsetjenester-til-voksne-psykisk-helse-og-avhengighet/",
    "https://www.osen.kommune.no/om-osen/ledige-stillinger/ledende-helsesykepleier-i-vakre-osen-kommune.22832.aspx":
        "https://www.osen.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/",
}
NOTE = ("QA 2026-09-08: original source URL 404; erstattet med naermeste levende "
        "offisiell side som fortsatt støtter påstanden.")

def fix(path):
    d = json.load(open(path))
    hits = 0
    def walk(obj):
        nonlocal hits
        if isinstance(obj, dict):
            u = obj.get("source_url")
            if u in MAPPING:
                obj["source_url"] = MAPPING[u]
                obj["notes"] = ((obj.get("notes") or "") + (" " if obj.get("notes") else "")) + NOTE
                hits += 1
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
    walk(d)
    json.dump(d, open(path, "w"), ensure_ascii=False, indent=1)
    return hits

for p in ("data/sample-split-a.json", "data/sample-split-b.json",
          "data/municipal-mental-health-sample-v1.json"):
    print(p, "->", fix(p), "URLs fixed")
