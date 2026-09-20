"""Semantic boundary comparison for support-proof eligibility.

Implements boundary-contract-v1.md with the RC3.1 bounded bugfix pass:
clause-scoped modality, negation consensus over fuzzy-shared terms,
phase-aware temporal comparison, and qualified numeric comparison.
UNKNOWN on any relevant dimension fails closed.

overall = BOUNDARY_COMPATIBLE : all relevant dims MATCH/LICENSED/NOT_APPLICABLE
          BOUNDARY_BLOCKED     : at least one hard MISMATCH
          BOUNDARY_UNRESOLVED  : no hard MISMATCH but at least one UNKNOWN
"""
import json
import os
import re

from .proposition import clauses, content_tokens, polarity, toks, tok_match

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.abspath(
    os.path.join(HERE, "..", "..", "rc3-1-support-boundary"))

with open(os.path.join(TASK_DIR, "modality-boundary-table.json"),
          encoding="utf-8") as f:
    MODALITY_TABLE = json.load(f)["relations"]

MODALITY_MARKERS = [
    ("PROHIBITED", ("kan ikke", "ikke tillatt", "forbudt",
                    "ikke mulig", "utelukket")),
    ("NOT_REQUIRED", ("ikke nodvendig", "ikke krav", "ikke obligatorisk",
                      "ikke paakrevd", "ingen henvisning", "krever ikke",
                      "ikke kreves", "frivillig", "ikke forpliktet",
                      "hindrer ikke", "ikke begrenset", "utbetales ikke",
                      "gis ikke", "far ikke", "ikke bare", "ingen")),
    ("ENTITLED", ("har rett", "rett til", "rettigheter", "krav pa",
                  "er en rettighet", "rettighet for", "utbetales til",
                  "utbetales", "gratis", "dekker", "gis til",
                  "stopper ved", "fortsetter", "gir")),
    ("REQUIRED", ("skal", "ma", "obligatorisk", "paakrevd", "plikt",
                  "plikter", "kreves", "krever", "ma sendes", "ma gjores",
                  "forpliktet", "mote", "skriver seg", "meldeplikt",
                  "har ansvar", "tilbyr", "ma vurderes")),
    ("PERMITTED", ("kan", "mulig", "adgang", "tilbyds", "far",
                   "finnes", "er mulig")),
    ("POSSIBLE", ("mulig", "kan", "adgang")),
]

DISCRETIONARY_MARKERS = ("skjon", "skjonsbestemt", "vanligvis", "normalt",
                         "regel", "etter vurdering", "individuell vurdering",
                         "varierer", "avhenger", "individuelt",
                         "kan justeres", "fravikes")

CONDITION_MARKERS = ("hvis ", "nar ", "dersom ", "etter behov",
                     "etter individuell vurdering", "ved behov",
                     "kan ha rett", "kan fa rett", "med behov", "naar ",
                     "ved opphold", "som bor")

EXCEPTION_MARKERS = ("unntak", "unntatt", "med mindre", "ikke gjelder",
                     "ikke tilbudt")

PERIOD_PATTERN = re.compile(
    r"([0-9]{1,3}) (maned|maneder|mnd|ar|dager|uke|uker|virkedager)")

ACTORS = ["fastlege", "barnevernet", "bup", "helsestasjon",
          "tannhelsetjeneste", "nav", "larer", "foreldre", "kommunen",
          "skolehelsetjeneste", "familievernkontor", "elever"]

NEG = {"ikke", "ingen"}

STOP_SHARED = {"ma", "pa", "at", "for", "med", "i", "er", "om", "eller",
               "kan", "til", "av", "fra", "har", "og", "a", "skal", "ikke",
               "det", "den", "du", "man"}


def detect_modality(text):
    """Modality of the clause containing the first fuzzy-shared content
    token, falling back to whole text when no clause-local marker exists."""
    tl = toks(text)

    def _probe(txt):
        t2 = toks(txt)
        for label, markers in MODALITY_MARKERS:
            for mk in markers:
                if " " in mk:
                    parts = mk.split()
                    if len(parts) == 2:
                        if any(t2[i] == parts[0]
                               and t2[i + 1] == parts[1]
                               for i in range(len(t2) - 1)):
                            return label
                elif mk in t2:
                    return label
        return None

    hit = None
    for cl in clauses(text):
        if any(tok_match(t, u) for t in cl for u in tl if u not in STOP_SHARED):
            hit = " ".join(cl)
            break
    if hit is None:
        return _probe(text) or "UNKNOWN"
    m = _probe(hit)
    if m is not None:
        return m
    for cl in clauses(text):
        m = _probe(" ".join(cl))
        if m is not None:
            return m
    return "UNKNOWN"


def _clause_of(text, term):
    """Token list of the clause containing a fuzzy match for term."""
    for cl in clauses(text):
        if any(tok_match(term, t) for t in cl):
            return cl
    return []


def _local_context(text, term):
    return _clause_of(text, term)


def _has_marker(text, markers):
    """Word-boundary marker match so "nav" does not hit inside
    "avlastning" and "ikke til" does not hit inside "ikke tilbudt"."""
    low = text.lower()
    for mk in markers:
        if re.search(r"(?<![a-z0-9])" + re.escape(mk.strip()) + r"(?![a-z0-9])",
                     low):
            return True
    return False


def _shared_terms(claim, span_text):
    """Fuzzy shared content terms (compound forms match via prefix rules)."""
    ct = content_tokens(claim)
    st = content_tokens(span_text)
    return [t for t in ct if any(tok_match(t, u) for u in st)]


def _periods(text):
    """(periods, anytime) where periods are (value, unit, phase) triples.

    Phase is START (deadline to initiate), END (entitlement stops) or WHOLE
    (per-period amount). Regex on normalized numeric periods only; symbolic
    deadlines fail closed through the UNKNOWN path.
    """
    low = text.lower()
    out = []
    for m in PERIOD_PATTERN.finditer(low):
        n, u = int(m.group(1)), m.group(2)
        phase_end = False
        if u == "ar":
            # Age ranges ("under 18 ar", "mellom 13 og 20 ar") are
            # population qualifiers, not temporal periods. "X ar" counts
            # as a period only in deadline/stop/amount context.
            pre_ctx = low[max(0, m.start() - 40):m.start()]
            if re.search(r"under |over |mellom ", pre_ctx):
                continue
            phase_end = bool(re.search(r"fyller", pre_ctx))
            if not phase_end and not re.search(
                    r"innen|senest|frist|stopper|etter|per ", pre_ctx):
                continue
        pre = low[max(0, m.start() - 30):m.start()]
        post = low[m.end():m.end() + 12]
        if re.search(r"innen|senest|frist", pre):
            phase = "START"
        elif phase_end:
            phase = "END"
        elif re.search(r"til |for |stopper ved |ved ", pre) or "stopper ved" in post:
            phase = "END"
        else:
            phase = "WHOLE"
        out.append((n, u, phase))
    anytime = bool(re.search(r"nar som helst|naar som helst|uten frist", low))
    return out, anytime


def _unit_class(u):
    if u.startswith("maned") or u == "mnd":
        return "MONTH"
    if u in ("ar", "ars"):
        return "YEAR"
    return "DAY"


def _claim_number_qualified(claim):
    """True when a claim number carries a unit/quantity context that makes
    it an exact commitment (amount per month, deadline, percentage)."""
    low = claim.lower()
    if re.search(r"kroner per maned|kroner i maneden|innen|senest|prosent", low):
        return True
    tl = toks(claim)
    for i, t in enumerate(tl):
        if t.isdigit() and len(t) >= 2:
            nxt = tl[i + 1:i + 3]
            if any(u.startswith("maned") or u in ("ar", "mnd", "dager")
                   for u in nxt):
                return True
    return False


def _actor_tokens(text):
    low = text.lower()
    found = [a for a in ACTORS if re.search(
        r"(?<![a-z0-9])" + re.escape(a)
        + r"(?:e[nr]|en|et|a|ene|ane|n|ne)?(?![a-z0-9])", low)]
    if "voksen" in low:
        found.append("voksne")
    if re.search(r"barn under|under 18", low):
        found.append("barn_u18")
    elif "barn" in low:
        found.append("barn")
    if re.search(r"(?<![a-z0-9])barn(?![a-z0-9])", low):
        found.append("barn")
    if re.search(r"(?<![a-z0-9])elever(?![a-z0-9])", low):
        found.append("skolehelsetjeneste")
    if "voksne" in low:
        found.append("voksne")
    return found


def _population_tokens(text):
    """Population-qualifier tokens, kept separate from role actors so a
    shared role name cannot mask a population mismatch."""
    low = text.lower()
    pop = []
    if re.search(r"(?<![a-z0-9])voksne(?![a-z0-9])", low):
        pop.append("voksne")
    if re.search(r"barn under|under 18", low):
        pop.append("barn_u18")
    elif re.search(r"(?<![a-z0-9])barn(?![a-z0-9])", low):
        pop.append("barn")
    return pop


def _definite_stem(text):
    """Bare stem of a definite-form first-word subject (fastlegen ->
    fastleg), or None when the text does not open with one."""
    w = text.split()[0].strip(".,:;!").lower() if text.split() else ""
    m2 = re.fullmatch(r"([a-z]+)(?:en|et|a|ene|ane)", w)
    return m2.group(1) if m2 and len(m2.group(1)) >= 4 else None


def _agent_mismatch(claim, span_text):
    """Definite-form subjects naming different agents: a locative-only
    mention of the evidence subject inside the claim ("pa helsestasjonen")
    does not make the claim's agent compatible with the evidence agent."""
    c_stem = _definite_stem(claim)
    s_stem = _definite_stem(span_text)
    if not c_stem or not s_stem or c_stem == s_stem:
        return False
    if c_stem in span_text.lower():
        return False
    low = claim.lower()
    hits = [m.start() for m in re.finditer(re.escape(s_stem), low)]
    if not hits:
        return False
    for i in hits:
        if not low[max(0, i - 4):i].endswith(("pa ", "i ", "ved ", "hos ")):
            return False
    return True


def _cl_neg(cl_toks):
    """Clause-level propositional negation. 'uten' is a preposition
    (exception/comitative) and must not flip clause polarity."""
    return any(x in ("ikke", "ingen") for x in cl_toks)
    return False


def compare(claim, span_text):
    """Return the boundary dict for claim vs one aligned span."""
    c_low = claim.lower()
    s_low = span_text.lower()
    c_cond = _has_marker(claim, CONDITION_MARKERS)
    s_cond = _has_marker(span_text, CONDITION_MARKERS)
    c_exc = _has_marker(claim, EXCEPTION_MARKERS)
    s_exc = _has_marker(span_text, EXCEPTION_MARKERS)
    shared = _shared_terms(claim, span_text)

    # ---- modality (clause-local detection, then contextual upgrades)
    c_mod = detect_modality(claim)
    s_mod = detect_modality(span_text)
    if s_mod in ("PERMITTED", "POSSIBLE") and s_cond:
        s_mod = "CONDITIONAL_ENTITLEMENT"
    if c_mod in ("PERMITTED", "POSSIBLE") and (c_cond or c_exc):
        c_mod = "CONDITIONAL_ENTITLEMENT"
    if (s_mod in ("REQUIRED", "PERMITTED", "ENTITLED")
            and _has_marker(span_text, DISCRETIONARY_MARKERS)
            and not _has_marker(claim, DISCRETIONARY_MARKERS)):
        s_mod = "DISCRETIONARY"
    key = s_mod + "->" + c_mod
    if s_mod == "UNKNOWN" or c_mod == "UNKNOWN":
        modality_dim = "UNKNOWN"
    else:
        modality_dim = MODALITY_TABLE.get(key, "UNKNOWN")

    # ---- polarity: consensus over shared content terms. Negation is
    # clause-propositional: a shared term flips polarity only when its
    # aligned clause carries ikke/ingen on one side and not the other.
    # Terms that are clause-initial subjects on both sides are topic
    # mentions, not predication, and are skipped.
    polarity_dim = "MATCH"
    checked = 0
    mism = False
    for t in shared:
        c_cl = _clause_of(claim, t)
        s_cl = _clause_of(span_text, t)
        if not c_cl or not s_cl:
            continue
        if c_cl[0] == t and s_cl[0] == t:
            continue
        checked += 1
        if _cl_neg(c_cl) != _cl_neg(s_cl):
            mism = True
    if mism:
        polarity_dim = "MISMATCH"
    elif checked == 0:
        polarity_dim = "UNKNOWN"

    # ---- actor (role + population)
    actor_dim = "MATCH"
    cset = set(_actor_tokens(claim))
    sset = set(_actor_tokens(span_text))
    cpop = set(_population_tokens(claim))
    spop = set(_population_tokens(span_text))
    if cpop and spop and not (cpop & spop):
        # Specific vs specific population mismatch ("voksne" vs
        # "barn under 18") blocks. A generic "barn" claim against a
        # narrower "barn under 18" population is covered: the evidence
        # grounds at least the claim's population.
        if (cpop == {"barn"} and spop == {"barn_u18"}):
            actor_dim = "MATCH"
        elif (spop == {"barn"} and cpop == {"barn_u18"}):
            actor_dim = "UNKNOWN"
        else:
            actor_dim = "MISMATCH"
    elif cset and sset and not (cset & sset):
        actor_dim = "MISMATCH"
    elif cset and not sset:
        actor_dim = "UNKNOWN"
    if actor_dim == "MATCH" and _agent_mismatch(claim, span_text):
        actor_dim = "MISMATCH"

    # ---- scope
    scope_dim = "MATCH"
    if re.search("alle kommuner", c_low) and not re.search(
            "alle kommuner|nasjonal", s_low):
        scope_dim = "UNKNOWN"
    if re.search("kun i |bare i ", s_low) and re.search("alle kommuner", c_low):
        scope_dim = "MISMATCH"
    loc = re.search(r"(hjemme|institusjon)", c_low)
    if loc and loc.group(1) in s_low and " eller " in s_low:
        scope_dim = "UNKNOWN"

    # ---- temporal (phase-aware)
    temporal_dim = "NOT_APPLICABLE"
    cp, c_any = _periods(claim)
    sp, _ = _periods(span_text)
    if cp or sp:
        if c_any and sp:
            temporal_dim = "MISMATCH"
        elif not cp or not sp:
            temporal_dim = "UNKNOWN"
        else:
            ok = False
            hard = False
            for n1, u1, p1 in cp:
                for n2, u2, p2 in sp:
                    if _unit_class(u1) != _unit_class(u2):
                        continue
                    if p1 == p2 and n1 == n2:
                        ok = True
                    elif p1 == p2 and n1 != n2:
                        hard = True
                    elif p1 != p2 and _unit_class(u1) == "YEAR":
                        hard = True
            if ok:
                temporal_dim = "MATCH"
            elif hard:
                temporal_dim = "MISMATCH"
            else:
                temporal_dim = "UNKNOWN"

    # ---- numeric (qualified claim numbers are exact commitments)
    numeric_dim = "NOT_APPLICABLE"
    cnums = {t for t in toks(claim) if t.isdigit() and len(t) >= 2}
    snums = {t for t in toks(span_text) if t.isdigit() and len(t) >= 2}
    if cnums and snums:
        if cnums <= snums:
            numeric_dim = "MATCH"
        elif _claim_number_qualified(claim):
            numeric_dim = "MISMATCH"
        else:
            numeric_dim = "UNKNOWN"
    elif cnums and not snums:
        numeric_dim = "UNKNOWN"

    # ---- numeric-factive modality: a matched concrete quantity grounds an
    # otherwise-unmodalized claim against a REQUIRED/evidence rule
    if (modality_dim == "UNKNOWN" and c_mod == "UNKNOWN"
            and (temporal_dim == "MATCH" or numeric_dim == "MATCH")
            and s_mod in ("REQUIRED", "UNKNOWN")):
        modality_dim = "MATCH"

    # Numeric-factive stop rule: an end-phase period match grounds a
    # NOT_REQUIRED-style stop claim against an entitlement-with-stop
    # evidence clause; the mismatch is lexical, not deontic.
    if (modality_dim == "MISMATCH" and temporal_dim == "UNKNOWN"
            and numeric_dim == "MATCH" and c_mod == "NOT_REQUIRED"
            and s_mod == "ENTITLED"):
        modality_dim = "UNKNOWN"

    # Alternative-location evidence ("hjemme eller pa institusjon") leaves
    # the claim's location scope unresolved; a stronger deontic reading of
    # the same general offer is then unknown, not a mismatch.
    if (scope_dim == "UNKNOWN" and modality_dim == "MISMATCH"
            and s_mod in ("PERMITTED", "POSSIBLE",
                          "CONDITIONAL_ENTITLEMENT")
            and c_mod in ("REQUIRED", "ENTITLED")):
        modality_dim = "UNKNOWN"

    # ---- condition / exception
    condition_dim = "NOT_APPLICABLE"
    if s_cond and not c_cond:
        # An unstated claim condition only fails closed to a hard block
        # when the claim asserts a strong right/obligation, or the
        # evidence condition is explicitly restrictive (bare/kun). A mere
        # possibility claim gains no falsifiable commitment from an
        # unstated condition: the difference is unresolved, not a
        # contradiction.
        if (c_mod in ("REQUIRED", "ENTITLED")
                or re.search(r"(?<![a-z0-9])(bare|kun)(?![a-z0-9])",
                             s_low)):
            condition_dim = "MISMATCH"
        else:
            condition_dim = "UNKNOWN"
    elif s_cond and c_cond:
        condition_dim = "MATCH"

    exception_dim = "NOT_APPLICABLE"
    if s_exc and not c_exc:
        exception_dim = "MISMATCH"
    elif s_exc and c_exc:
        exception_dim = "MATCH"

    # ---- clause_coverage: negation after the aligned span, or a
    # prohibition inside the aligned clause, forbids support
    clause_dim = "MATCH"
    if shared:
        sctx = _local_context(span_text, shared[0])
        if sctx:
            late_neg = bool(NEG & set(sctx))
            cneg_any = any(
                any(x in NEG for x in _clause_of(claim, t)[:8])
                for t in shared)
            if late_neg and not cneg_any:
                clause_dim = "MISMATCH"
            sctx_mod = detect_modality(" ".join(sctx))
            if (sctx_mod in ("PROHIBITED", "NOT_REQUIRED")
                    and c_mod not in ("PROHIBITED", "NOT_REQUIRED")):
                clause_dim = "MISMATCH"

    dims = {
        "polarity": polarity_dim,
        "modality": modality_dim,
        "actor": actor_dim,
        "temporal": temporal_dim,
        "scope": scope_dim,
        "condition": condition_dim,
        "exception": exception_dim,
        "numeric_quantity": numeric_dim,
        "clause_coverage": clause_dim,
    }
    hard = [k for k, v in dims.items() if v == "MISMATCH"]
    soft_unknown = [k for k, v in dims.items() if v == "UNKNOWN"]
    if hard:
        overall = "BOUNDARY_BLOCKED"
    elif soft_unknown:
        overall = "BOUNDARY_UNRESOLVED"
    else:
        overall = "BOUNDARY_COMPATIBLE"
    dims["overall"] = overall
    dims["blocking_dimensions"] = hard + soft_unknown
    dims["dimension_evidence"] = _dimension_evidence(
        claim, span_text, dims, c_mod, s_mod, c_cond, s_cond, c_exc, s_exc,
        c_low, s_low, shared)
    return dims


def _dimension_evidence(claim, span_text, dims, c_mod, s_mod, c_cond,
                        s_cond, c_exc, s_exc, c_low, s_low, shared):
    """Rich per-dimension states (contract-v1 section 3) with provenance.
    Computed from the same internal values as the 3-state gate; the gate
    projection in section 5 MUST reproduce dims exactly (differential
    test verifies this before relation consumption is enabled)."""
    ev = {}
    span_id = None

    # --- polarity
    p = dims["polarity"]
    if (p == "MISMATCH" and s_exc and c_low is not None
            and re.search(r"(?<![a-z0-9])unntak(?![a-z0-9])", s_low)
            and not re.search(r"(?<![a-z0-9])unntak(?![a-z0-9])", c_low)):
        # Evidence states the rule with an exception the claim omits:
        # the gate still blocks, but the conflict is exception-bounded,
        # which the relation layer must not treat as a propositional
        # polarity conflict (rule-id provenance, contract section 4).
        state, rule = "EXPLICIT_CONFLICT", "DE-polarity-exception-bounded"
    elif p == "MISMATCH":
        state, rule = "EXPLICIT_CONFLICT", "DE-polarity-clause-negation-consensus"
    elif p == "UNKNOWN":
        state, rule = "RELEVANT_BUT_UNRESOLVED", "DE-polarity-no-shared-predicate"
    else:
        state, rule = "EXACT_MATCH", "DE-polarity-consensus"
    ev["polarity"] = {"state": state, "rule": rule,
                      "evidence_span_id": span_id, "note": None}

    # --- modality: direction from the frozen boundary lattice key
    m = dims["modality"]
    key = s_mod + "->" + c_mod
    if key in MODALITY_TABLE:
        eff = MODALITY_TABLE[key]
    else:
        eff = "UNKNOWN"
    if m == "MISMATCH":
        if (eff == "MISMATCH" and s_mod in ("NOT_REQUIRED", "PROHIBITED")
                and c_mod in ("REQUIRED", "ENTITLED", "PERMITTED")):
            state, rule = ("DEONTIC_OPPOSITION",
                           "DE-modality-deontic-opposition")
        elif (eff == "MISMATCH"
                and s_mod in ("REQUIRED", "ENTITLED",
                              "CONDITIONAL_ENTITLEMENT")
                and c_mod in ("PERMITTED", "POSSIBLE")):
            state, rule = ("SOURCE_STRONGER_THAN_CLAIM",
                           "DE-modality-source-stronger")
        else:
            # Direction-unknown mismatch: the state stays conflict-class
            # (frozen projection), but the rule id marks that deontic
            # opposition is NOT established (weaker-source conflicts land
            # here); the relation layer treats only the named rule as
            # positive opposition.
            state, rule = "DEONTIC_OPPOSITION", "DE-modality-unresolved-direction"
    elif m == "LICENSED_ENTAILMENT":
        if (s_mod in ("REQUIRED", "ENTITLED", "CONDITIONAL_ENTITLEMENT")
                and c_mod in ("PERMITTED", "POSSIBLE", "ENTITLED")):
            state, rule = ("SOURCE_STRONGER_THAN_CLAIM",
                           "DE-modality-source-stronger")
        elif (s_mod == "CONDITIONAL_ENTITLEMENT"
                and c_mod in ("PERMITTED", "ENTITLED")):
            state, rule = ("CONDITIONALLY_COMPATIBLE",
                           "DE-modality-conditional")
        else:
            state, rule = "EXACT_MATCH", "DE-modality-exact"
    elif m == "MATCH":
        state, rule = "EXACT_MATCH", "DE-modality-exact"
    else:
        state, rule = "RELEVANT_BUT_UNRESOLVED", "DE-modality-unknown-direction"
    ev["modality"] = {"state": state, "rule": rule,
                      "evidence_span_id": span_id, "note": key if state not in
                      ("RELEVANT_BUT_UNRESOLVED",) else None}

    # --- condition
    cond = dims["condition"]
    if cond == "MISMATCH":
        state, rule = "CONDITION_MISSING", "DE-condition-missing-in-claim"
    elif cond == "MATCH":
        state, rule = "EXACT_MATCH", "DE-condition-stated-both-sides"
    elif cond == "UNKNOWN":
        state = "RELEVANT_BUT_UNRESOLVED"
        rule = ("DE-condition-weak-claim-unstated" if c_cond
                else "DE-condition-unknown")
    else:
        state, rule = "NOT_APPLICABLE", "DE-condition-not-present"
    ev["condition"] = {"state": state, "rule": rule,
                       "evidence_span_id": span_id, "note": None}

    # --- exception
    exc = dims["exception"]
    if exc == "MISMATCH":
        state, rule = "EXCEPTION_CONFLICT", "DE-exception-unstated-in-claim"
    elif exc == "MATCH":
        state, rule = "EXACT_MATCH", "DE-exception-stated-both-sides"
    else:
        state, rule = "NOT_APPLICABLE", "DE-exception-not-present"
    ev["exception"] = {"state": state, "rule": rule,
                       "evidence_span_id": span_id, "note": None}

    # --- actor
    a = dims["actor"]
    if a == "MISMATCH":
        state, rule = "DIFFERENT_ACTOR", "DE-actor-disjoint-tokens"
    elif a == "UNKNOWN":
        state, rule = "ACTOR_UNRESOLVED", "DE-actor-unstated-in-evidence"
    else:
        state, rule = "SAME_ACTOR", "DE-actor-shared-tokens"
    ev["actor"] = {"state": state, "rule": rule,
                   "evidence_span_id": span_id, "note": None}

    # --- scope
    sc = dims["scope"]
    if sc == "MISMATCH":
        state, rule = "SCOPE_CONFLICT", "DE-scope-restriction-vs-universal"
    elif sc == "UNKNOWN":
        state, rule = "RELEVANT_BUT_UNRESOLVED", "DE-scope-universal-unchecked"
    else:
        state, rule = "SCOPE_COMPATIBLE", "DE-scope-compatible"
    ev["scope"] = {"state": state, "rule": rule,
                   "evidence_span_id": span_id, "note": None}

    # --- temporal
    t = dims["temporal"]
    if t == "MISMATCH":
        state, rule = "TEMPORAL_CONFLICT", "DE-temporal-phase-conflict"
    elif t == "UNKNOWN":
        state, rule = "RELEVANT_BUT_UNRESOLVED", "DE-temporal-partial"
    elif t == "NOT_APPLICABLE":
        state, rule = "NOT_APPLICABLE", "DE-temporal-not-present"
    else:
        state, rule = "TEMPORAL_COMPATIBLE", "DE-temporal-compatible"
    ev["temporal"] = {"state": state, "rule": rule,
                      "evidence_span_id": span_id, "note": None}

    # --- numeric
    n = dims["numeric_quantity"]
    if n == "MISMATCH":
        state, rule = "NUMERIC_CONFLICT", "DE-numeric-qualified-claim-mismatch"
    elif n == "UNKNOWN":
        state, rule = "RELEVANT_BUT_UNRESOLVED", "DE-numeric-unverified"
    elif n == "NOT_APPLICABLE":
        state, rule = "NOT_APPLICABLE", "DE-numeric-not-present"
    else:
        state, rule = "NUMERIC_COMPATIBLE", "DE-numeric-compatible"
    ev["numeric_quantity"] = {"state": state, "rule": rule,
                              "evidence_span_id": span_id, "note": None}

    # --- clause coverage
    cc = dims["clause_coverage"]
    if cc == "MISMATCH":
        state, rule = "PARTIAL_OVERLAP", "DE-clause-late-negation-or-prohibition"
    elif cc == "UNKNOWN":
        state, rule = "RELEVANT_BUT_UNRESOLVED", "DE-clause-no-aligned-context"
    else:
        state, rule = "EXACT_MATCH", "DE-clause-aligned"
    ev["clause_coverage"] = {"state": state, "rule": rule,
                             "evidence_span_id": span_id, "note": None}
    return ev
