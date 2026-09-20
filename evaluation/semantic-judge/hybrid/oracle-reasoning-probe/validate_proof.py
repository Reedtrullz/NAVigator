"""Deterministic proof validator for the structured-proof reviewer.

Validates model proofs against the packet: span ids exist, operator is
allowed, operator preconditions hold, derived fact uses only evidence.
Failed validation -> REVIEW_REQUIRED (spec 17). ASCII-only source;
Norwegian regex tokens use unicode escapes.
"""
import json
import re
import sys

VERDICTS = {"SUPPORTED", "CONTRADICTED", "PARTIAL", "INSUFFICIENT",
            "REVIEW_REQUIRED"}

NEG_RE = re.compile(r"\b(ikke|ingen|aldri|uten|frav\u00e6r|fravaer|nekt)\b", re.IGNORECASE)
MOD_RE = re.compile(r"\b(kan|skal|m\u00e5|maa|rett|plikt|forutsetter|krever)\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b(\d{1,2}[./]\d{1,2}([./]\d{2,4})?|\d{4}|\d+\s*(\u00e5r|mnd|m\u00e5ned|m\u00e5neder|maaneder))\b", re.IGNORECASE)
COND_RE = re.compile(r"\b(hvis|n\u00e5r|nar|dersom|ved|etter|f\u00f8lger|folger|men|gjelder)\b", re.IGNORECASE)
EXH_RE = re.compile(r"\b(kun|bare|eneste|alle|ingen andre|ikke andre|eksklusiv|utgj\u00f8r)\b", re.IGNORECASE)
EXC_RE = re.compile(r"\b(unntak|men|bortsett fra|unntatt)\b", re.IGNORECASE)
ARITH_RE = re.compile(r"(\d|\+|\-|>|<|=|mnd|m\u00e5ned|\u00e5r)", re.IGNORECASE)

STOP = set("""og eller at det en et ei som for fra til med av om i paa p\u00e5
den det dette disse er var blir har hadde kan skal maa m\u00e5 ikke
the a an of to in on for and or is are""".split())

OPERATORS = {
    "DIRECT_ASSERTION": {"safety": "high",
        "preconditions": ["paraphrase-level overlap between claim and premises"]},
    "EXPLICIT_NEGATION": {"safety": "high",
        "preconditions": ["premise contains explicit negation token"]},
    "NUMERIC_CONFLICT": {"safety": "high",
        "preconditions": ["premise contains a number on the claim axis", "values differ"]},
    "TEMPORAL_CONFLICT": {"safety": "high",
        "preconditions": ["premise contains a date/duration anchor", "anchors conflict"]},
    "MODALITY_CONFLICT": {"safety": "medium",
        "preconditions": ["modality tokens present on both sides"]},
    "SAME_PREDICATE_OPPOSITE_POLARITY": {"safety": "medium",
        "preconditions": ["shared predicate", "opposite polarity"]},
    "RULE_PLUS_CONDITION": {"safety": "medium",
        "preconditions": ["rule and condition co-present (two premises or condition-marked span)"]},
    "RULE_PLUS_EXCEPTION": {"safety": "medium",
        "preconditions": ["rule span plus explicit exception marker"]},
    "DEFINITION_PLUS_INSTANCE": {"safety": "medium",
        "preconditions": ["class term shared between claim and premise"]},
    "EXHAUSTIVE_SET_EXCLUSION": {"safety": "high-if-marked",
        "preconditions": ["premise marks the list exhaustive (kun/bare/eneste/alle/...)"]},
    "ACTOR_MEMBERSHIP": {"safety": "medium",
        "preconditions": ["actor term shared between claim and premise"]},
    "LOCAL_RULE_OVERRIDES_GENERAL": {"safety": "medium",
        "preconditions": ["locality term present in the premise span"]},
    "MULTI_SPAN_CONJUNCTION": {"safety": "medium",
        "preconditions": ["at least two distinct premise spans"]},
    "SIMPLE_ARITHMETIC": {"safety": "high",
        "preconditions": ["numbers in premises", "arithmetic relation in derived_fact"]},
    "TRANSITIVE_EQUIVALENCE": {"safety": "medium",
        "preconditions": ["each equivalence step is a small paraphrase"]},
}


def _tokens(text):
    return set(re.findall(r"[a-z\u00e6\u00f8\u00e50-9]+", (text or "").lower()))


def _nums(text):
    return {re.sub(r"[\s,]", "", n) for n in re.findall(r"\d[\d ,]*\d|\d", text or "")}


def _hallucinated_terms(derived_fact, evidence_texts):
    """Terms in derived_fact absent from claim+premises (prefix-4 fallback
    for Norwegian inflection). Conservative: flags invented content only."""
    ev = _tokens(" ".join(evidence_texts))
    bad = []
    for tok in _tokens(derived_fact):
        if tok in ev or tok in STOP or tok.isdigit():
            continue
        if any(tok[:4] == e[:4] for e in ev):
            continue
        if len(tok) >= 5 and any(len(e) >= 5 and (tok in e or e in tok) for e in ev):
            continue
        bad.append(tok)
    return bad


def _op_ok(op, claim, premise_texts, derived):
    joined = " ".join(premise_texts)
    claim_t, span_t = _tokens(claim), _tokens(joined)
    overlap = len(claim_t & span_t) / max(1, len(claim_t | span_t))
    if op == "DIRECT_ASSERTION":
        return overlap >= 0.4, "overlap %.2f < 0.4" % overlap
    if op == "EXPLICIT_NEGATION":
        if not NEG_RE.search(joined):
            return False, "no negation token in premises"
        return overlap >= 0.15, "negated predicate not in claim"
    if op == "NUMERIC_CONFLICT":
        sn, cn = _nums(joined), _nums(claim)
        if not sn:
            return False, "no number in premises"
        if cn and not (sn - cn):
            return False, "premise numbers all match claim"
        return True, ""
    if op == "TEMPORAL_CONFLICT":
        if not DATE_RE.search(joined):
            return False, "no date/duration anchor in premises"
        return True, ""
    if op == "MODALITY_CONFLICT":
        if not (MOD_RE.search(claim) and MOD_RE.search(joined)):
            return False, "modality token missing on one side"
        return True, ""
    if op == "SAME_PREDICATE_OPPOSITE_POLARITY":
        if overlap < 0.1:
            return False, "no shared predicate"
        if NEG_RE.search(claim) == NEG_RE.search(joined):
            return False, "no polarity opposition (negation on one side required)"
        return True, ""
    if op == "RULE_PLUS_CONDITION":
        if len(premise_texts) >= 2:
            return True, ""
        return bool(COND_RE.search(joined)), "single premise lacks condition marker"
    if op == "RULE_PLUS_EXCEPTION":
        return bool(EXC_RE.search(joined)), "no exception marker"
    if op == "DEFINITION_PLUS_INSTANCE":
        return overlap >= 0.2, "class/instance term not shared"
    if op == "EXHAUSTIVE_SET_EXCLUSION":
        if not EXH_RE.search(joined):
            return False, "exhaustiveness_not_marked"
        return True, ""
    if op == "ACTOR_MEMBERSHIP":
        return overlap >= 0.15, "actor term not shared"
    if op == "LOCAL_RULE_OVERRIDES_GENERAL":
        # locality term must appear in the premise span, not only the claim
        locals_ = _tokens(claim) - _tokens(claim)  # placeholder, see below
        claim_words = re.findall(r"[A-Z\u00c6\u00d8\u00c5][a-z\u00e6\u00f8\u00e5]+", claim or "")
        for w in claim_words:
            if w.lower() in span_t:
                return True, ""
        return False, "locality term absent from premises"
    if op == "MULTI_SPAN_CONJUNCTION":
        return len(premise_texts) >= 2, "fewer than two premises"
    if op == "SIMPLE_ARITHMETIC":
        if not _nums(joined):
            return False, "no numbers in premises"
        return bool(ARITH_RE.search(derived)), "no arithmetic relation in derived_fact"
    if op == "TRANSITIVE_EQUIVALENCE":
        return overlap >= 0.15, "equivalence chain has no anchor"
    return False, "unknown operator"


def validate_proof(output, packet, claim_text=None):
    """Return {"valid": bool, "reasons": [...], "hallucinated_terms": [...]}."""
    reasons = []
    if not isinstance(output, dict):
        return {"valid": False, "reasons": ["not_json_object"], "hallucinated_terms": []}
    verdict = output.get("verdict")
    if verdict not in VERDICTS:
        reasons.append("bad_verdict:%s" % verdict)
    op = output.get("inference_operator")
    premises = output.get("premises_used") or []
    derived = output.get("derived_fact") or ""
    if not isinstance(premises, list):
        reasons.append("premises_not_list")
        premises = []
    spans = {s["span_id"]: s["text"] for s in packet.get("candidate_spans", [])}
    claim = claim_text if claim_text is not None else packet.get("claim", "")
    missing = [sid for sid in premises if sid not in spans]
    if missing:
        reasons.append("span_not_found:%s" % ",".join(missing))
    if verdict == "INSUFFICIENT":
        if op not in (None, "NO_OPERATOR"):
            reasons.append("insufficient_requires_no_operator")
    else:
        if op == "NO_OPERATOR":
            reasons.append("verdict_requires_operator")
        elif op not in OPERATORS:
            reasons.append("operator_not_allowed:%s" % op)
    if verdict in ("SUPPORTED", "CONTRADICTED", "PARTIAL", "REVIEW_REQUIRED") \
            and op != "NO_OPERATOR" and op in OPERATORS and not missing:
        texts = [spans[sid] for sid in premises if sid in spans]
        ok, why = _op_ok(op, claim, texts, derived)
        if not ok:
            reasons.append("precondition_failed:%s:%s" % (op, why))
    if len(_tokens(derived)) < 3 and verdict not in ("INSUFFICIENT",):
        reasons.append("derived_fact_too_short")
    halluc = _hallucinated_terms(derived, [claim] + [spans[s] for s in premises if s in spans])
    if halluc:
        reasons.append("hallucinated_premise_terms")
    return {"valid": not reasons, "reasons": reasons,
            "hallucinated_terms": halluc}


def export_operators(path):
    doc = {"schema": "inference-operators-v1",
           "note": "Generated from validate_proof.py. Exhaustiveness requires an "
                   "explicit marker; absence of evidence never yields "
                   "contradiction (probe spec 7-8).",
           "operators": [{"id": k, **v} for k, v in OPERATORS.items()],
           "no_operator": {"id": "NO_OPERATOR",
                           "meaning": "no valid derivation; verdict must be INSUFFICIENT"}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--export-operators":
        import os
        export_operators(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "inference-operators.json"))
    else:
        out = json.load(open(sys.argv[1], encoding="utf-8"))
        pkt = json.load(open(sys.argv[2], encoding="utf-8"))
        print(json.dumps(validate_proof(out, pkt), ensure_ascii=False, indent=1))
