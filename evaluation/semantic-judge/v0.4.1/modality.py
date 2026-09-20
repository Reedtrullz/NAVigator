#!/usr/bin/env python3
"""Deterministic modality normalizer and modality matrix (spec v0.4.1
sections 10-12).

The LLM only identifies verbatim modal trigger phrases. This module maps
them to canonical modality values and computes the modality relation.
No model calls, no I/O, no claim-id lookups.

Canonical values: MAY, SHOULD, ENTITLED, MAY_BE_ENTITLED, USUALLY,
ALWAYS, NEVER, REQUIRED, NOT_REQUIRED, RECOMMENDED, MUST, UNKNOWN.
"""
import re

_NEVER = [
    r"\baldri\b", r"\bm[åa] ikke\b", r"\bskal ikke\b", r"\bf[åa]r ikke\b",
    r"\bikke tillatt\b", r"\bforbudt\b", r"\bikke gis\b", r"\bikke ytes\b",
    r"\bhar ikke rett\b", r"\bhar ikke krav\b", r"\bikke rett til\b",
    r"\bikke krav p[åa]\b", r"\bikke ha rett\b",
]
_NOT_REQUIRED = [
    r"\bikke n[øo]dvendig\b", r"\btrenger ikke\b", r"\bkreves ikke\b",
    r"\bkrever ikke\b", r"\bikke p[åa]krevd\b", r"\bikke obligatorisk\b",
    r"\bikke pliktig\b", r"\bikke forpliktet\b", r"\bfrivillig\b",
    r"\buten\b",
]
_ALWAYS = [r"\balltid\b", r"\bskal alltid\b", r"\bma[å] alltid\b"]
_ENTITLED = [
    r"\bhar rett\b", r"\bhar krav\b", r"\brett til\b", r"\bkrav p[åa]\b",
    r"\ber berettiget\b",
]
_MAY_BE_ENTITLED = [
    r"\bkan ha rett\b", r"\bkan ha krav\b", r"\bkan f[åa] rett\b",
    r"\bkan v[æae]re berettiget\b", r"\bkan f[åa]\b",
]
_MUST = [
    r"\bm[åa]\b", r"\bskal\b", r"\ber pliktig\b", r"\bplikt til\b",
    r"\bpliktet til\b", r"\bforpliktet til\b", r"\bkreves\b",
    r"\bkrever\b", r"\bobligatorisk\b",
]
_MAY_OMIT = [
    r"\bkan (velge [åa] |velge )?(droppe|frav[æae]lge|avvikle|utelate|unnlate|legge ned)\b",
]
_MAY = [
    r"\bkan\b", r"\bmulighet\b", r"\bmulig\b", r"\bkan velge\b",
    r"\bkan gis\b", r"\bkan innvilges\b", r"\bkan innvilge\b",
]
_USUALLY = [
    r"\bnormalt\b", r"\bvanligvis\b", r"\bsom hovedregel\b",
    r"\bvanlig(e?)\b", r"\boftest\b", r"\bsom regel\b",
    r"\bi utgangspunktet\b",
]
_SHOULD = [r"\bb[øo]r\b", r"\bburde\b"]
_RECOMMENDED = [r"\banbefales\b", r"\banbefalt\b"]

_ORDER = [
    ("NEVER", _NEVER),
    ("NOT_REQUIRED", _NOT_REQUIRED),
    ("ALWAYS", _ALWAYS),
    ("MAY_BE_ENTITLED", _MAY_BE_ENTITLED),
    ("ENTITLED", _ENTITLED),
    ("MUST", _MUST),
    ("MAY_OMIT", _MAY_OMIT),
    ("MAY", _MAY),
    ("USUALLY", _USUALLY),
    ("SHOULD", _SHOULD),
    ("RECOMMENDED", _RECOMMENDED),
]
_COMPILED = [(name, [re.compile(p, re.IGNORECASE) for p in pats])
             for name, pats in _ORDER]

_STRONG = {"MUST", "REQUIRED", "ALWAYS", "ENTITLED"}
_WEAK = {"MAY", "MAY_OMIT", "MAY_BE_ENTITLED", "USUALLY", "SHOULD",
         "RECOMMENDED"}
_SPECIAL_CASE = re.compile(
    r"s(æ|ae)rlige tilfelle(r|ne)?|spesielle tilfelle(r|ne)?|"
    r"enkelte tilfelle(r|ne)?|s(æ|ae)rlige situasjoner|"
    r"spesielle situasjoner", re.IGNORECASE)
_UNIVERSAL_CASE = re.compile(
    r"alle saker|alle tilfelle(r|ne)?|alle kommuner|alle mottakere|"
    r"alle s[øo]kere|hver sak|uansett", re.IGNORECASE)


def normalize_modality(text):
    """Map a verbatim modal trigger phrase to a canonical value."""
    if not text or not str(text).strip():
        return "UNKNOWN"
    t = str(text)
    for name, patterns in _COMPILED:
        for pat in patterns:
            if pat.search(t):
                return name
    return "UNKNOWN"


def modality_relation(source_modality, claim_modality,
                      discretion_explicit=False,
                      source_trigger_text="", claim_text=""):
    """Compute claim-vs-source modality relation deterministically.

    Returns one of: SAME, CLAIM_WEAKER (claim weaker than the source's
    established rule -> compatible), CLAIM_STRONGER (claim hardens
    beyond the source -> insufficient unless discretion conflict),
    CONFLICT (positive incompatibility -> contradiction), UNKNOWN.
    """
    s = source_modality if source_modality in _ALL else "UNKNOWN"
    c = claim_modality if claim_modality in _ALL else "UNKNOWN"
    if (s == "MAY"
            and _UNIVERSAL_CASE.search(str(claim_text or ""))
            and _SPECIAL_CASE.search(str(source_trigger_text or ""))):
        # A universal claim ("i alle saker") asserted against a
        # discretionary special-case option ("i saerlige tilfeller")
        # contradicts the source's limiting scope.
        return "CONFLICT"
    if s == "UNKNOWN" or c == "UNKNOWN":
        return "UNKNOWN"
    if s == c:
        return "SAME"
    if s == "NEVER":
        return "CONFLICT" if c != "NOT_REQUIRED" else "SAME"
    if s == "NOT_REQUIRED":
        if c in _STRONG or c == "NEVER":
            return "CONFLICT"
        return "CLAIM_WEAKER"
    if s in ("ALWAYS", "MUST", "REQUIRED"):
        if c == "MAY_OMIT":
            # An explicit option to omit a duty contradicts the duty.
            return "CONFLICT"
        if c in ("NEVER", "NOT_REQUIRED"):
            return "CONFLICT"
        if c in _STRONG:
            return "SAME"
        return "CLAIM_WEAKER"
    if s == "ENTITLED":
        if c in ("NEVER", "NOT_REQUIRED"):
            return "CONFLICT"
        if c in ("ENTITLED", "ALWAYS", "MUST", "REQUIRED"):
            return "SAME"
        return "CLAIM_WEAKER"
    if s == "MAY":
        if c in ("NEVER", "NOT_REQUIRED"):
            return "CONFLICT"
        if c in _STRONG:
            return "CONFLICT" if discretion_explicit else "CLAIM_STRONGER"
        return "SAME"
    if s == "MAY_BE_ENTITLED":
        if c in ("NEVER", "NOT_REQUIRED"):
            return "CONFLICT"
        if c in _STRONG:
            return "CLAIM_STRONGER"
        return "SAME"
    if s == "USUALLY":
        if c == "NEVER":
            return "CONFLICT"
        if c in _STRONG:
            return "CLAIM_STRONGER"
        return "SAME"
    # source SHOULD / RECOMMENDED
    if c in ("NEVER", "NOT_REQUIRED"):
        return "CONFLICT"
    if c in _STRONG:
        return "CLAIM_STRONGER"
    return "SAME"


_ALL = {"MAY", "MAY_OMIT", "SHOULD", "MUST", "ENTITLED", "MAY_BE_ENTITLED",
        "USUALLY", "ALWAYS", "NEVER", "REQUIRED", "NOT_REQUIRED",
        "RECOMMENDED", "UNKNOWN"}
