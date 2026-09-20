#!/usr/bin/env python3
"""Annotation pass 2: model-assisted (GPT-5.6-Luna), independent.

Reads ONLY the public case packet (claim, evidence spans, atom-free).
Must never read pass-1 labels. Writes checkpoint json + final json.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "construction-audit"
PROXY = "http://127.0.0.1:10100/v1/chat/completions"
MODEL = "gpt-5.6-luna"

CONTRACT = (
    "Du er uavhengig annotator for en norsk NAV-kunnskapsbase-evaluering.\n"
    "Du faar en claim og et evidence-packet (eksakte kildesitat).\n"
    "Svar KUN med ett JSON-objekt, ingen annen tekst.\n"
    "Semantisk sannhet (semantic_truth), basert KUN paa evidensen:\n"
    "- SUPPORTED: hele claimet dekkes direkte eller ved aritmetikk/eksplisitt regel\n"
    "- CONTRADICTED: evidensen motsiger kaernen i claimet slik at "
    "claimet som helhet er feil\n"
    "- PARTIALLY_SUPPORTED: en del stemmer, en annen del er feil\n"
    "- INSUFFICIENT_EVIDENCE: packeten gir ikke grunnlag for aa avgjore\n"
    "Proof-safe (proof_safe): SUPPORTED/CONTRADICTED kun om deterministisk proof "
    "kan etableres direkte av sitatene; PARTIALLY_SUPPORTED -> bruk "
    "REVIEW_REQUIRED; tvil om avgrensning/modality -> REVIEW_REQUIRED.\n"
    "Product action (product_action): AUTO_SUPPORTED (valid SUPPORT-proof), "
    "AUTO_CONTRADICTED (valid CONTRADICTION-proof), REVIEW_REQUIRED (relevant "
    "evidence men krever avgrensning/avklares), ABSTAIN_INSUFFICIENT "
    "(evidensen er genuint utilstrekkelig, ingen konkret konflikt).\n"
    "Regler: fravaer av stotte er ikke motsigelse. Modality (kan/skal/maa/"
    "vanligvis/som regel/alltid) maa matche. Beloep/datoer maa vaere eksakte.\n"
    "VIKTIG precedence for sammensatte claims: hvis atomene ikke er helt "
    "uniforme (minst to ulike klasser), er helheten PARTIALLY_SUPPORTED "
    "(aldri CONTRADICTED, aldri INSUFFICIENT_EVIDENCE paa topp-nivaa). Kun "
    "naar alle atomer har samme klasse beholder helheten den klassen.\n"
    "Avklaring av taushet vs motsigelse (gjelder alle claims):\n"
    "- Evidensen som oppgir en ANNEN verdi for samme stoerrelse claimet "
    "nevner, er en motsigelse (CONTRADICTED), ikke INSUFFICIENT_EVIDENCE.\n"
    "- Dersom evidensen stoeetter hoveddelen av claimet, men er taus om en "
    "sekundaer del, er claimet PARTIALLY_SUPPORTED. INSUFFICIENT_EVIDENCE "
    "kun naar ingen kjerne-del i claimet kan avgjoes fra packeten.\n"
    "- En generell regel i evidensen er ikke motsagt av ett enkelt eksempel "
    "med avvikende dato/belop, saa lenge regelen selv staar i evidensen.\n"
    "- Tidsbinding er kjernee i claimet: et claim som binder et beloep/ en "
    "sats til en spesifikk dato eller periode kan bare vaere SUPPORTED "
    "dersom evidensen knytter SAMME verdi til SAMME periode. Oppgir "
    "evidensen verdien uten periodeankerknening, er tidsbindingen "
    "uavklart: claimet er da INSUFFICIENT_EVIDENCE, eller "
    "PARTIALLY_SUPPORTED hvis andre selvstendige deler er avklart.\n"
    "Hvis claimet bestaar av flere selvstendige del-paastander (conjuncts), "
    "dekomponer det i atomer (atom = minste selvstendige proposisjon) og "
    "gi semantic_truth per atom. Top-level semantic_truth for compounds: "
    "uniforme atomer beholder klassen; ellers PARTIALLY_SUPPORTED.\n"
    "Output-schema:\n"
    '{"semantic_truth": "...", "proof_safe": "SUPPORTED|CONTRADICTED|'
    'INSUFFICIENT_EVIDENCE|REVIEW_REQUIRED", "product_action": "...", '
    '"genuine_insufficiency": true|false, '
    '"atoms": [{"text": "...", "semantic_truth": "..."}], '
    '"rationale_short": "..."}\n'
    "genuine_insufficiency er true KUN naar product_action er "
    "ABSTAIN_INSUFFICIENT (evidensen kan ikke resolve noen kjerne-del).\n"
    "atoms skal vaere tom liste for single-claims; kun compound-claims "
    "(flere selvstendige del-paastander knyttet med og/eller liknende) "
    "skal dekomponeres i atomer."
)

SEM = {"SUPPORTED", "CONTRADICTED", "PARTIALLY_SUPPORTED",
       "INSUFFICIENT_EVIDENCE"}
PS = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE",
      "REVIEW_REQUIRED"}
PR = {"AUTO_SUPPORTED", "AUTO_CONTRADICTED", "REVIEW_REQUIRED",
      "ABSTAIN_INSUFFICIENT"}


def packet(case):
    ev = "\n".join("[S%d] %s" % (i + 1, s["text"])
                    for i, s in enumerate(case["sources"]))
    return "Claim: %s\n\nEvidence-packet:\n%s" % (case["claim"], ev)


def valid_label(obj):
    if not isinstance(obj, dict):
        return False
    if obj.get("semantic_truth") not in SEM:
        return False
    if obj.get("proof_safe") not in PS:
        return False
    if obj.get("product_action") not in PR:
        return False
    if not isinstance(obj.get("genuine_insufficiency"), bool):
        return False
    if not isinstance(obj.get("atoms"), list):
        return False
    for a in obj["atoms"]:
        if not isinstance(a, dict) or a.get("semantic_truth") not in SEM:
            return False
        if not isinstance(a.get("text"), str) or not a["text"]:
            return False
    return True


def call_luna(user_text):
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": CONTRACT},
            {"role": "user", "content": user_text}],
        "temperature": 0,
        "max_tokens": 900,
    }).encode()
    req = urllib.request.Request(
        PROXY, data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode())
    return data["choices"][0]["message"]["content"]


def parse_json(text):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return None


def main():
    data = json.loads((AUDIT / "cases-pass1.json").read_text(encoding="utf-8"))
    selection = json.loads((AUDIT / "selection.json").read_text(encoding="utf-8"))
    core_ids = set(selection["core_ids"])
    cases = [c for c in data["cases"] if c["case_id"] in core_ids]
    out_path = AUDIT / "labels-pass2.json"
    done = {}
    if out_path.exists():
        done = json.loads(out_path.read_text(encoding="utf-8"))
    pending = [c for c in cases
               if not (c["case_id"] in done
                       and done[c["case_id"]].get("status") == "OK")]

    def annotate(case):
        rec = {"status": "FAILED", "retries": 0}
        for attempt in range(3):
            try:
                raw = call_luna(packet(case))
                obj = parse_json(raw)
                if obj is not None and valid_label(obj):
                    rec = {"status": "OK", "label": obj, "retries": attempt}
                    break
                rec = {"status": "INVALID_JSON", "raw": raw[:400],
                       "retries": attempt + 1}
            except Exception as e:
                rec = {"status": "ERROR", "error": str(e)[:200],
                       "retries": attempt + 1}
            time.sleep(2)
        return case["case_id"], rec

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(annotate, c): c["case_id"] for c in pending}
        for i, fut in enumerate(as_completed(futures), 1):
            cid, rec = fut.result()
            done[cid] = rec
            out_path.write_text(json.dumps(done, ensure_ascii=False, indent=1),
                                encoding="utf-8")
            print("%d/%d %s %s" % (i, len(pending), cid, rec["status"]),
                  flush=True)
    ok = sum(1 for v in done.values() if v.get("status") == "OK")
    print("PASS2_COMPLETE ok=%d total=%d" % (ok, len(cases)), flush=True)


if __name__ == "__main__":
    main()
