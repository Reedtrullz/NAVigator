#!/usr/bin/env python3
"""Independent deterministic proof validation (spec 14).

Re-derives every check from raw claim + source text. Invalid or missing
precondition -> (False, reason) and the gate falls back to REVIEW_REQUIRED.
Never trusts the operator result field.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
QA = os.path.join(os.path.dirname(HERE), "quote-aligner")
V02 = os.path.join(QA, "v0.2")
sys.path.insert(0, QA)
sys.path.insert(0, V02)

import polarity_engine as pe  # frozen
import polarity_engine_v02 as v02  # frozen
import tier1_operators as ops

VALID_OPERATORS = {"DIRECT_ASSERTION", "EXPLICIT_NEGATION", "NUMERIC_CONFLICT",
                   "TEMPORAL_CONFLICT", "SIMPLE_ARITHMETIC"}
_NEG_RE = re.compile(r"\b(ikke|ingen|aldri|uten|verken|umulig)\b")
_ARITH_RE = re.compile(r"\b(til sammen|tilsammen|totalt|samlet|i alt|sum)\b")


def validate(proof, claim, source_text):
    """Returns (ok: bool, reason: str)."""
    if not isinstance(proof, dict):
        return False, "not-a-dict"
    for k in ("operator", "premises", "derived_fact", "claim_atom", "result"):
        if k not in proof:
            return False, "missing-key:" + k
    op = proof["operator"]
    if op not in VALID_OPERATORS:
        return False, "unknown-operator"
    result = proof["result"]
    if result not in ("SUPPORTED", "CONTRADICTED"):
        return False, "invalid-result"
    premises = proof.get("premises") or []
    if not premises or not all(isinstance(p, str) for p in premises):
        return False, "bad-premises"
    sents = ops._sentences(source_text)
    for p in premises:
        m = re.match(r"^S(\d+)$", p)
        if not m or not (1 <= int(m.group(1)) <= len(sents)):
            return False, "span-missing:" + str(p)
    if op == "SIMPLE_ARITHMETIC" and len(premises) < 2:
        return False, "arithmetic-needs-2-premises"
    if op == "SIMPLE_ARITHMETIC":
        pass
    elif op == "DIRECT_ASSERTION":
        if not 1 <= len(premises) <= 2:
            return False, "bad-premise-count"
    elif len(premises) != 1:
        return False, "bad-premise-count"
    ci = int(premises[0][1:]) - 1
    sent = sents[ci]
    # no external facts: derived_fact must quote the premise span
    if op != "SIMPLE_ARITHMETIC":
        df = v02._fold(proof.get("derived_fact", ""))
        sp = v02._fold(sent)
        first_word = next((w for w in df.split() if len(w) >= 4), "")
        if not first_word or first_word[:5] not in sp:
            return False, "external-fact-or-truncated-span"
    # re-run the operator independently
    fn = dict(zip([f.__name__ for f in ops.OPERATORS], ops.OPERATORS)).get(
        op.lower())
    if fn is None:
        return False, "no-operator-fn"
    try:
        fresh = fn(claim, source_text)
    except Exception as e:
        return False, "operator-crash:" + type(e).__name__
    if fresh is None:
        return False, "operator-no-longer-fires"
    if fresh["result"] != result:
        return False, "result-mismatch"
    # operator-specific re-derivation
    if op == "DIRECT_ASSERTION":
        concepts = (proof.get("detail") or {}).get("concepts") or []
        if not concepts:
            return False, "no-concepts-in-detail"
        for c in concepts:
            concept = c.get("concept")
            cp, _ = v02._concept_polarity(claim, concept)
            found = any(
                v02._concept_polarity(s, concept)[0] == cp
                for s in sents if v02._concept_polarity(s, concept)[0] != 0)
            if cp == 0 or not found:
                return False, "equal-polarity-not-established"
        # Every premise must carry the shared subject directly or be a
        # no-actor fragment chained to any preceding bound sentence.
        prev_ok = False
        first = min(int(p[1:]) for p in premises)
        for idx in range(1, first):
            if ops._same_subject(claim, sents[idx - 1], contra=False):
                prev_ok = True
        for idx in sorted(int(p[1:]) for p in premises):
            sent = sents[idx - 1]
            if ops._same_subject(claim, sent, contra=False):
                prev_ok = True
            elif not (prev_ok and not ops._sentence_has_own_actor(sent)):
                return False, "fragment-not-chained"
    elif op == "EXPLICIT_NEGATION":
        if not (v02._has_neg_wb(sent) or v02._has_neg_wb(claim)):
            return False, "no-explicit-negation"
        concepts = (proof.get("detail") or {}).get("concepts") or []
        if not concepts:
            return False, "no-concepts-in-detail"
        for c in concepts:
            concept = c.get("concept")
            cp, _ = v02._concept_polarity(claim, concept)
            if cp == 0:
                return False, "opposite-polarity-not-established"
            sp2 = None
            for s in sents:
                pol = v02._concept_polarity(s, concept)[0]
                if pol != 0:
                    sp2 = pol
                    break
            if sp2 is None or sp2 == cp:
                return False, "opposite-polarity-not-established"
        if ops._scope_conflict(claim, sent) or                 not ops._time_compatible(claim, sent):
            return False, "scope-or-time-conflict"
        subj = ops._same_subject(claim, sent, contra=True)
        if not subj:
            return False, "actor-axis-not-established"
    elif op == "NUMERIC_CONFLICT":
        if not v02._FRAMING_RE.search(v02._fold(claim)):
            return False, "no-binding-framing"
        conflict = ops._conflicting_pair(
            v02._num_bounds(claim), v02._num_bounds(sent),
            ops._exclusion_flag(claim), ops._exclusion_flag(sent))
        if not conflict:
            return False, "no-numeric-conflict"
    elif op == "TEMPORAL_CONFLICT":
        cd, sd = pe.extract_dates(claim), pe.extract_dates(sent)
        if not cd or not sd:
            return False, "no-dates"
        c0, s0 = cd[0], sd[0]
        if (c0["y"], c0["m"], c0["d"]) == (s0["y"], s0["m"], s0["d"]):
            return False, "no-date-conflict"
        if not ops._shared_content(claim, sent):
            return False, "no-shared-topic"
    elif op == "SIMPLE_ARITHMETIC":
        if not _ARITH_RE.search(v02._fold(claim)):
            return False, "no-arithmetic-framing"
        rel = (proof.get("detail") or {}).get("relation")
        if rel not in ("sum", "difference"):
            return False, "bad-relation"
        vals = (proof.get("detail") or {}).get("values") or []
        if len(vals) != 2:
            return False, "need-2-values"
        a, b = vals
        got = a + b if rel == "sum" else abs(a - b)
        cb = v02._num_bounds(claim)
        if not cb or got != cb[0]["value"]:
            return False, "recompute-mismatch"
    return True, "ok"


if __name__ == "__main__":
    print("validator module ok")
