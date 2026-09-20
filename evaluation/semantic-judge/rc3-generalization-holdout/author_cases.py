#!/usr/bin/env python3
"""RC3 generalization holdout: case authoring with pass-1 annotations.

Pass 1 = this author (contract-driven, independent of snapshot output).
Labels live ONLY here and in construction-audit/; never in public files.
This script never imports anything from runtime-snapshot/.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from construction_tools import check_novelty, validate_case  # noqa: E402

ROOT = Path("/Users/reidar/Projectos/NAV Explore")
AUDIT = HERE / "construction-audit"
AUDIT.mkdir(exist_ok=True)

# --- facts: id -> (kb_file, anchor-substring, extra-lines-below) ------
FACTS = {
    "BB_INTRO": ("48-barnebidrag-i-dybden.md", "til barnet selv etter fylte 18", 0),
    "BB_REGELVERK": ("48-barnebidrag-i-dybden.md", "Barnelova LOV-1981-04-08-7", 0),
    "BB_FORSKRIFT": ("48-barnebidrag-i-dybden.md", "Detaljerte beregningsregler", 0),
    "SAM_OVER": ("49-samvaersfradrag-og-reisekostnader.md", "MER enn 2 dager", 0),
    "SAM_FAKTISK": ("49-samvaersfradrag-og-reisekostnader.md", "Avtalt men ikke", 0),
    "SAM_SATS": ("49-samvaersfradrag-og-reisekostnader.md", "1277", 1),
    "BT_TAB": ("54-delt-barnetrygd-ordinar-og-utvidet.md", "1 006 kr/mnd", 0),
    "BT_UTV": ("54-delt-barnetrygd-ordinar-og-utvidet.md", "1 286 kroner", 0),
    "BT_SUM": ("54-delt-barnetrygd-ordinar-og-utvidet.md", "2 292", 0),
    "BT_SATS": ("16-livssituasjoner/02-aleneforsorger.md", "2 012 kr/mnd per barn", 0),
    "BT_UTV2": ("16-livssituasjoner/02-aleneforsorger.md", "2 572 kr/mnd", 0),
    "BT_FINN": ("16-livssituasjoner/02-aleneforsorger.md", "+512 kr/mnd", 0),
    "BT_ETTER": ("16-livssituasjoner/02-aleneforsorger.md", "Etterbetaling", 0),
    "BS_ALDER": ("55-bostotte-i-dybden.md", "eller under 18 år med barn", 0),
    "BS_KVAL": ("55-bostotte-i-dybden.md", "egen inngang, eget bad", 0),
    "BS_FRIST": ("55-bostotte-i-dybden.md", "den 25. i måneden", 0),
    "BS_UTB": ("55-bostotte-i-dybden.md", "den 20. i måneden etter", 0),
    "BS_MINST": ("55-bostotte-i-dybden.md", "Minsteutbetaling er 61", 0),
    "BS_BT_IKKE": ("55-bostotte-i-dybden.md", "barnetrygd", 0),
    "BS_AAP": ("55-bostotte-i-dybden.md", "2/3", 1),
    "BS_FORST": ("55-bostotte-i-dybden.md", "kreve at du søker bostøtte først", 0),
    "BS_OS_TELLER": ("55-bostotte-i-dybden.md", "tell", 0),
    "BS_KOLL": ("55-bostotte-i-dybden.md", "kollektiv", 0),
    "SH_17": ("56-okonomisk-sosialhjelp-i-dybden.md", "Kommunen skal gi slik hjelp", 0),
    "SH_18": ("56-okonomisk-sosialhjelp-i-dybden.md", "har krav", 0),
    "SH_19": ("56-okonomisk-sosialhjelp-i-dybden.md", "Kommunen KAN yte", 0),
    "SH_20": ("56-okonomisk-sosialhjelp-i-dybden.md", "naer sammenheng med vedtaket", 0),
    "SH_BT": ("56-okonomisk-sosialhjelp-i-dybden.md", "barnetrygd", 0),
    "OS_14": ("63-overgangsstonad-endringsloven-og-kapittel-15.md", "barnet fyller 14 måneder", 0),
    "OS_SATS": ("63-overgangsstonad-endringsloven-og-kapittel-15.md", "25 603", 0),
    "OS_GAMMEL": ("63-overgangsstonad-endringsloven-og-kapittel-15.md", "beholder de tidligere reglene", 0),
    "OS_225": ("63-overgangsstonad-endringsloven-og-kapittel-15.md", "2,25 ganger grunnbeløpet", 0),
    "OS_AVKORT": ("63-overgangsstonad-endringsloven-og-kapittel-15.md", "0,5", 0),
    "OS_OPPHEV": ("63-overgangsstonad-endringsloven-og-kapittel-15.md", "opphevet for nye saker", 0),
    "OS_2MND": ("64-overgangsstonad-nye-regler-i-dybden.md", "inntil 2 måneder før fødselen", 0),
    "OS_AL": ("64-overgangsstonad-nye-regler-i-dybden.md", "etter at du blir alene om omsorgen", 0),
    "OS_14B": ("64-overgangsstonad-nye-regler-i-dybden.md", "må være under 14 måneder", 0),
    "OS_TERM": ("64-overgangsstonad-nye-regler-i-dybden.md", "for terminen", 0),
    "DEP_MAX": ("58-boligtrygghet-depositum-utkastelse.md", "inntil seks maneders leie", 0),
    "DEP_KOMM": ("58-boligtrygghet-depositum-utkastelse.md", "enkelte kommuner tilbyr", 0),
    "DEP_NAV": ("58-boligtrygghet-depositum-utkastelse.md", "vanligvis en garanti for depositum", 0),
    "DEP_SPERRET": ("58-boligtrygghet-depositum-utkastelse.md", "sperret konto", 0),
    "DEP_ANDRE": ("58-boligtrygghet-depositum-utkastelse.md", "avtalemonstre", 0),
    "PPT_DIAG": ("28-ppt-i-dybden.md", "diagnos", 0),
    "PPT_SAK": ("28-ppt-i-dybden.md", "sakkyndig instans", 0),
    "PPT_LOV": ("28-ppt-i-dybden.md", "pedagogisk-psykologisk tjeneste", 0),
    "PPT_ERSTATTE": ("28-ppt-i-dybden.md", "ikke erstattes", 0),
    "SK_DAG1": ("30-skolefravar-og-skolevegring.md", "fra første dag eleven er borte", 0),
    "SK_PLAN": ("30-skolefravar-og-skolevegring.md", "skriftlig plan for oppfølging", 0),
    "SK_LOV": ("30-skolefravar-og-skolevegring.md", "aktivt med i oppl", 0),
    "RPH_16": ("25-kommunale-psykiske-tjenester-barn-unge.md", "over 16", 0),
    "STATPED": ("17-statped-og-barnehus.md", "varig og omfattende tilretteleggingsbehov", 0),
    "STATPED_PPT": ("17-statped-og-barnehus.md", "PPT søker på vegne", 0),
    "STATPED_DEP": ("17-statped-og-barnehus.md", "Kunnskapsdepartementet", 0),
    "PEN_62": ("07-pensjon/README.md", "fra 62 år", 0),
    "PEN_40": ("07-pensjon/README.md", "fullt minimum etter 40", 0),
    "PEN_KOMB": ("07-pensjon/README.md", "arbeidsinntekt uten reduksjon", 0),
    "PEN_SOK": ("07-pensjon/README.md", "4 måneder før", 0),
    "AMS_REG": ("03-arbeidsmarkedstjenester/README.md", "Alle kan registrere seg", 0),
    "AMS_14A": ("03-arbeidsmarkedstjenester/README.md", "14a", 0),
    "KLAGE_TLF": ("14-kontakt-og-klage/README.md", "55 55 33 33", 0),
    "KLAGE_AAPEN": ("14-kontakt-og-klage/README.md", "Hverdager 09", 0),
    "KLAGE_KANALER": ("14-kontakt-og-klage/README.md", "Telefon, chat", 0),
    "GB_HOVED": ("15-referansedata/README.md", "NOK 136 549", 0),
    "GB_AARSVERDI": ("15-referansedata/README.md", "134 419", 0),
    "GB_FAKTOR": ("15-referansedata/README.md", "1,049085", 0),
    "HM_VARIG": ("09-hjelpemidler/README.md", "varig nedsatt funksjonsevne", 0),
    "VOLD_112": ("42-vold-trusler-og-sikkerhet.md", "Krisesenterlinjen: 116 006", 0),
    "KK_KONTROLL": ("19-kontrollkommisjon-og-klage.md", "Kontroll av vedtak etter 3", 0),
    "KK_SAMTYKKE": ("19-kontrollkommisjon-og-klage.md", "Samtykke til videre tvang", 0),
    "KK_MEDLEMMER": ("19-kontrollkommisjon-og-klage.md", "4 medlemmer", 0),
}

SEM_MAP = {"S": "SUPPORTED", "C": "CONTRADICTED", "P": "PARTIALLY_SUPPORTED", "I": "INSUFFICIENT_EVIDENCE"}
PS_MAP = {"S": "SUPPORTED", "C": "CONTRADICTED", "P": "REVIEW_REQUIRED", "I": "INSUFFICIENT_EVIDENCE"}
PR_MAP = {"S": "AUTO_SUPPORTED", "C": "AUTO_CONTRADICTED", "P": "REVIEW_REQUIRED", "I": "ABSTAIN_INSUFFICIENT"}

_FACT_CACHE = {}


def fact_block(fid):
    """Resolve a fact to (block_text, kb_ref, line_start). Cached."""
    if fid in _FACT_CACHE:
        return _FACT_CACHE[fid]
    kb_file, anchor, extra = FACTS[fid]
    path = ROOT / kb_file
    if not path.exists():
        _FACT_CACHE[fid] = None
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    hit = None
    for i, ln in enumerate(lines):
        if anchor in ln:
            hit = i
            break
    if hit is None:
        _FACT_CACHE[fid] = None
        return None
    block = "\n".join(lines[hit:hit + 1 + extra]).strip()
    out = (block, kb_file, hit + 1)
    _FACT_CACHE[fid] = out
    return out


def build_case(entry):
    """entry = (cid, track, claim, sem, fact_ids, flags, atoms, critical, rationale)"""
    cid, track, claim, sem, fact_ids, flags, atoms, critical, rationale = entry
    sources, missing = [], []
    for fid in fact_ids:
        fb = fact_block(fid)
        if fb is None:
            missing.append(fid)
            continue
        block, kb_file, ln = fb
        sources.append({"kb_ref": "kb/" + kb_file, "lines": [ln, ln], "text": block})
    if missing:
        return None, missing
    flags = list(flags) if flags else []
    if not atoms:
        flags = [f for f in flags if f != "compound"]
    if len(set(fact_ids)) >= 2:
        flags.append("multi-span")
    lower = claim.lower()
    if any(m in lower for m in ("dersom", "hvis", "unntak", "hovedregel",
                                "bare ", "kun ", "krever", "må ")):
        flags.append("condition")
    if "unntak" in lower:
        flags.append("exception")
    case = {
        "case_id": cid,
        "claim": claim,
        "track": track,
        "sources": sources,
        "evidence": [
            {"span_id": "S%d" % (i + 1), "text": s["text"]} for i, s in enumerate(sources)
        ],
        "compound": bool(atoms),
        "public_flags": sorted(set(flags)),
        "critical": critical,
    }
    if atoms:
        case["atoms"] = [
            {
                "atom_id": "A%d" % (i + 1),
                "text": a[0],
                "relation_to_parent": "CONJUNCT",
                "semantic_truth": SEM_MAP[a[1]],
                "evidence_span_ids": (
                    ["S%d" % (fact_ids.index(a[2]) + 1)] if len(a) > 2 and a[2] in fact_ids else []
                ),
                "required_inference": a[3] if len(a) > 3 else "EXPLICIT_MATCH",
            }
            for i, a in enumerate(atoms)
        ]
        # top-level aggregation: frozen RC3 routing convention --
        # uniform atoms keep their class; any mix -> PARTIALLY_SUPPORTED.
        sems = {a[1] for a in atoms}
        top = sems.pop() if len(sems) == 1 else "P"
        sem = top
    errs = validate_case(case)
    if errs:
        return ("INVALID", errs), []
    # pass-1 labels (sealed material)
    labels = {
        "semantic_truth": SEM_MAP[sem],
        "proof_safe": PS_MAP[sem],
        "product_action": PR_MAP[sem],
        "genuine_insufficiency": sem == "I",
        "groundedness_target": True,
        "structural_validity_target": True,
        "semantic_soundness_target": sem in ("S", "C"),
        "proof_safe_auto_correctness_target": True,
        "adjudication_status": "PASS1_ONLY",
        "rationale": rationale,
    }
    return case, labels
