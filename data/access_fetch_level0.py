import html as h
import json
import os
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
OUT = "/tmp/access_l0"
os.makedirs(OUT, exist_ok=True)

MARKER = re.compile(
    r"(ta kontakt|kontakt oss|du kan kontakte|ring |telefon:|tlf|mob\.? |e-post|epost|drop-?in|framm\u00f8te|timebestilling|bestille time|henvis|s\u00f8knad|slik søker|slik søkjer|inntak|konsultasjon|sentralbord)",
    re.I,
)


def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.getcode(), r.read()
    except Exception as e:
        return 0, str(e).encode()


def to_text(raw):
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    txt = h.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", txt)


targets = json.load(open("data/access-unclear-targets-v1.json"))["targets"]
summary = {}
for t in targets:
    tag, url = t["target_id"], t["existing_source_url"]
    code, body = fetch(url)
    via = "direct"
    if code != 200 or len(body) < 800:
        code2, body2 = fetch("https://r.jina.ai/" + url)
        if code2 == 200 and len(body2) > len(body):
            code, body, via = code2, body2, "r.jina.ai"
    try:
        text = to_text(body.decode("utf-8", "ignore")) if via == "direct" else body.decode("utf-8", "ignore")
    except Exception:
        text = ""
    open(f"{OUT}/{tag}.txt", "w").write(text)
    hits = []
    for m in MARKER.finditer(text):
        s, e = max(0, m.start() - 80), min(len(text), m.end() + 100)
        hits.append("..." + text[s:e] + "...")
    seen, uniq = set(), []
    for x in hits:
        k = x[:70]
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    summary[tag] = {"url": url, "status": code, "via": via, "chars": len(text), "hits": uniq[:8]}
    print(f"== {tag} status={code} via={via} chars={len(text)}")
    for x in uniq[:8]:
        print("   ", x.replace("\n", " "))
    if not uniq:
        print("    (no access-marker hits)")

json.dump(summary, open(f"{OUT}/summary.json", "w"), ensure_ascii=False, indent=2)
