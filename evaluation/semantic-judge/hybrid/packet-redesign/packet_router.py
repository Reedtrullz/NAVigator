"""Evidence-packet router v2 (task SEMANTIC-JUDGE-EVIDENCE-PACKET-REDESIGN).

Turns the flat v1 packet into a per-atom evidence-group packet:
candidate gathering (existing aligner, wider top_n) -> global dedup ->
role tagging -> condition/exception linking -> diversity pruning ->
per-atom groups with joint_support sets.  S0 full-source span is
mode-controlled (include | no_s0 | fallback).  No new retrieval.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HY = os.path.dirname(HERE)
JUDGE_DIR = os.path.join(os.path.dirname(HY), "quote-aligner", "v0.2")
for p in (JUDGE_DIR, os.path.dirname(JUDGE_DIR), HY, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
from quote_aligner import candidates, content_tokens  # noqa: E402
from polarity_engine import detect_injection  # noqa: E402

SCHEMA_VERSION = "packet-v2.1"
BS = chr(92)  # regex backslash, kept out of source (transport safety)

RE_MODAL = re.compile(BS + "b(kan|kunne|skal|maa|må|bør|bor|alltid|aldri|aldrig)" + BS + "b", re.IGNORECASE)
RE_NEG = re.compile(BS + "b(ikke|aldri|aldrig|uten|mangler|fravaer|fravær)" + BS + "b", re.IGNORECASE)
RE_COND = re.compile(BS + "b(dersom|hvis|naar|når|ved|sa lenge|så lenge|forutsatt)" + BS + "b", re.IGNORECASE)
RE_EXC = re.compile(BS + "b(unntak|bortsett|med mindre|unntatt|annet enn)" + BS + "b", re.IGNORECASE)
RE_NUM = re.compile("(" + BS + "d|" + BS + "bkr" + BS + "b|kroner|prosent)", re.IGNORECASE)
RE_LOC = re.compile(BS + "b(kommune|kommunal|kommunale|lokal|lokalt|lokale)" + BS + "b", re.IGNORECASE)
RE_ACTOR = re.compile(BS + "b(fastlege|legen|lege|BUP|PPT|barnevernet|barnevern|kommunen|kommunepsykolog|helsesykepleier|helsestasjon|HFU|familievernkontoret|familievern|HABU|NAV|skolen|skole|familieteam|familieteamet)" + BS + "b", re.IGNORECASE)
RE_TEMP = re.compile(BS + "b(aar|år|mnd|måned|maaneder|måneder|uke|uker|dager)" + BS + "b", re.IGNORECASE)


def _roles(span_text):
    roles = []
    if RE_COND.search(span_text):
        roles.append("CONDITION")
    if RE_EXC.search(span_text):
        roles.append("EXCEPTION")
    if RE_NEG.search(span_text):
        roles.append("NEGATION")
    if RE_MODAL.search(span_text):
        roles.append("MODALITY")
    if RE_NUM.search(span_text):
        roles.append("NUMERIC")
    if RE_TEMP.search(span_text):
        roles.append("TEMPORAL")
    if RE_LOC.search(span_text):
        roles.append("LOCALITY")
    if RE_ACTOR.search(span_text):
        roles.append("ACTOR")
    if not roles:
        roles = ["MAIN_RULE"]
    return roles


def _canon(text):
    t = re.sub(r"[^a-zæøå0-9 ]", " ", text.lower())
    return " ".join(t.split())


def _jac(a, b):
    sa, sb = set(_canon(a).split()), set(_canon(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _coverage(span_text, atom_text):
    a = set(content_tokens(atom_text))
    if not a:
        return 1.0
    s = set(content_tokens(span_text))
    return round(len(a & s) / len(a), 3)


def _greedy_joint(cands, atom_text, need=0.7, max_spans=3):
    """Smallest span set whose union covers >= need of the atom."""
    a = set(content_tokens(atom_text))
    if not a:
        return [], 1.0
    chosen, cov = [], set()
    pool = sorted(cands, key=lambda c: (-c["_cov"], -c["score"]))
    for c in pool:
        missing = a - cov
        if not missing:
            break
        gain = len(set(content_tokens(c["text"])) & missing)
        if gain <= 0:
            continue
        chosen.append(c)
        cov |= set(content_tokens(c["text"])) & a
        if len(chosen) >= max_spans:
            break
    return [c["span_id"] for c in chosen], round(len(cov) / len(a), 3)


def build_v2_packet(claim_text, source_text, engine_result, gate_reason,
                    s0_mode="no_s0", max_spans=6, atoms_per_cand=6):
    """Schema packet-v2.1: per-atom evidence groups, roles, linking."""
    atoms = [a.get("atom_text") or a.get("text") or ""
             for a in (engine_result.get("atom_results") or [])] or [claim_text]
    registry = {}   # span_id -> {"text":..., "roles":set, "score":max}

    def register(text, score):
        key = _canon(text)
        for sid, s in registry.items():
            if _canon(s["text"]) == key:
                s["score"] = max(s["score"], score)
                return sid
        sid = "S%d" % (len(registry) + 1)
        registry[sid] = {"text": text, "score": score, "roles": set()}
        return sid

    atom_groups = []
    for i, at in enumerate(atoms, 1):
        cands = candidates(at, source_text, top_n=atoms_per_cand)
        entries = []
        for c in cands:
            sid = register(c["text"], c["score"])
            entries.append({"span_id": sid, "text": c["text"],
                            "score": c["score"],
                            "_cov": _coverage(c["text"], at)})
        kept = []   # within-atom diversity: drop near-duplicates
        for c in sorted(entries, key=lambda x: -x["score"]):
            if any(_jac(c["text"], k["text"]) >= 0.8 for k in kept):
                continue
            kept.append(c)
        for c in kept:
            registry[c["span_id"]]["roles"].update(_roles(c["text"]))
        joint_ids, joint_cov = _greedy_joint(kept, at)
        for c in kept:
            c["relation"] = ("single_support" if c["_cov"] >= 0.7
                             else "joint_support" if c["span_id"] in joint_ids
                             else "qualifier")
        g = {"atom_id": "A%d" % i, "claim_atom": at,
             "candidate_evidence": [
                 {"span_id": c["span_id"],
                  "roles": sorted(registry[c["span_id"]]["roles"]),
                  "atom_coverage": c["_cov"], "relation": c["relation"]}
                 for c in kept],
             "evidence_set": joint_ids, "joint_coverage": joint_cov}
        ids = set(g["evidence_set"])
        roles = set()
        for e in g["candidate_evidence"]:
            if e["span_id"] in ids:
                roles |= set(e["roles"])
        if RE_EXC.search(at) or "EXCEPTION" in roles:
            g["group_type"] = "RULE_WITH_EXCEPTION"
        elif RE_COND.search(at) or "CONDITION" in roles:
            g["group_type"] = "RULE_WITH_CONDITION"
        atom_groups.append(g)
    # global packet budget: rank spans by atom-use count, then score
    use_count = {}
    for g in atom_groups:
        for sid in set(e["span_id"] for e in g["candidate_evidence"]):
            use_count[sid] = use_count.get(sid, 0) + 1
    ranked = sorted(registry.items(),
                    key=lambda kv: (-use_count.get(kv[0], 0),
                                    -kv[1]["score"]))
    keep_ids = set(sid for sid, _ in ranked[:max_spans])
    # never orphan an atom: its top evidence and joint set stay
    for g in atom_groups:
        if g["candidate_evidence"]:
            keep_ids.add(g["candidate_evidence"][0]["span_id"])
        keep_ids.update(g["evidence_set"])
    # S0 policy
    weak = any(not g["candidate_evidence"] or g["joint_coverage"] < 0.5
               for g in atom_groups)
    if s0_mode == "include" or (s0_mode == "fallback" and weak):
        if len(source_text) < 1200:
            sid = None
            key = _canon(source_text)
            for s, v in registry.items():
                if _canon(v["text"]) == key:
                    sid = s
                    break
            if sid is None:
                sid = "S%d" % (len(registry) + 1)
                registry[sid] = {"text": source_text, "score": 0.15,
                                 "roles": {"MAIN_RULE"}}
            registry[sid]["roles"].add("FULL_SOURCE")
            keep_ids.add(sid)
    spans_out = []
    for sid in sorted(keep_ids, key=lambda x: int(x[1:])):
        s = registry.get(sid)
        if s:
            spans_out.append({"span_id": sid, "text": s["text"],
                              "roles": sorted(s["roles"])})
    for g in atom_groups:
        g["candidate_evidence"] = [e for e in g["candidate_evidence"]
                                   if e["span_id"] in keep_ids]
    return {
        "schema": SCHEMA_VERSION,
        "s0_mode": s0_mode,
        "claim": claim_text,
        "atoms": atom_groups,
        "candidate_spans": spans_out,
        "deterministic_findings": {
            "engine_verdict": engine_result.get("verdict"),
            "injection_detected": bool(detect_injection(source_text)),
            "atom_results": [
                {"id": a.get("atom_id", "A%d" % (i + 1)),
                 "verdict": a.get("verdict"), "rule": a.get("rule")}
                for i, a in enumerate(engine_result.get("atom_results") or [])],
            "gate_reason": gate_reason}}
