#!/usr/bin/env python3
"""AFK prep V1 core library.

Read-only view of the authoritative Batch 2 packet file, the frozen V2.15
lane as the only validate/derive engine, deterministic packet QC, review
burden metrics, and a fully synthetic E2E pipeline used only on a temp copy.

No semantic assistance: spans are only re-encodied and checked verbatim.
"""
import hashlib, json, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
CORPUS = os.path.join(EVAL, "dev-corpus-v1-1-repair")
BATCH = os.path.join(EVAL, "measurement-v3-human-review-batch-2-repaired")
V15_DIR = os.path.join(EVAL, "measurement-v2-15-semantic-human-review-fallback")
J13_DIR = os.path.join(EVAL, "judge-selection-v2-13-forbidden-route-specialist")
sys.path.insert(0, V15_DIR)
sys.path.insert(0, J13_DIR)
import review_lane_semantic_v2_15 as LANE  # frozen, unmodified

REVIEWER_ID = "OWNER-01"
FORBIDDEN_UI_TERMS = ("final_gold", "model_verdict", "automated_verdict",
                      "CLAIM_PRESENT", "CLAIM_ABSENT_TAKEN", "CRITICAL_ERROR",
                      "AI_SEMANTIC_SUGGESTION", "suggested_verdict")
FORBIDDEN_SPAN_SOURCES = ("provenance", "claims", "reviewer_instructions", "criterion", "case_context")


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def load_packets():
    """Read-only parse of the authoritative packet file."""
    path = os.path.join(BATCH, "human-review-packets.jsonl")
    packets = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                packets.append(json.loads(line))
    return packets


def load_order():
    with open(os.path.join(BATCH, "review-order.json"), encoding="utf-8") as f:
        ro = json.load(f)
    return ro["critical_condition"] + ro["forbidden_claim"]


def parse_answer(raw):
    try:
        obj = json.loads(raw)
    except Exception:
        return None
    if isinstance(obj, dict) and isinstance(obj.get("answer"), str):
        return obj
    return None


ENUMS = {
    "critical_condition": {"critical_evidence_state": LANE.EVIDENCE_STATES},
    "forbidden_claim": {"criterion_semantic_match": LANE.MATCH_STATES,
                        "speaker_commitment": LANE.COMMITMENTS},
}


# ---------------- mechanical validator (human-verbose) ----------------

def validate_review_row(row, packets_by_id, seen_ids, allowed_contract=None, expected_reviewer=REVIEWER_ID):
    """Validate one human-review row; returns list of human-readable errors."""
    errs = []
    if not isinstance(row, dict):
        return ["row is not a JSON object"]
    allowed = {"packet_id", "case_id", "packet_sha256", "reviewer_id", "contract_version", "reviewed_utc", "judgment"}
    unknown = sorted(set(row) - allowed)
    if unknown:
        errs.append("unexpected field(s): " + ", ".join(unknown))
    pid = row.get("packet_id")
    p = packets_by_id.get(pid)
    if p is None:
        errs.append("unknown packet ID: " + str(pid))
        return errs
    if row.get("case_id") != p.get("case_id"):
        errs.append("case_id mismatch for " + str(pid) + ": expected " + str(p.get("case_id")))
    if row.get("packet_sha256") not in (None, p["packet_sha256"]):
        errs.append("packet SHA mismatch for " + str(pid) + ": bound to different packet body")
    if row.get("reviewer_id") != expected_reviewer:
        errs.append("wrong reviewer_id: expected " + expected_reviewer + ", got " + str(row.get("reviewer_id")))
    if row.get("contract_version") != p["contract_version"]:
        errs.append("contract version mismatch for " + str(pid) + ": expected " + p["contract_version"])
    ts = row.get("reviewed_utc")
    if not isinstance(ts, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ts or ""):
        errs.append("reviewed_utc missing or not ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ) for " + str(pid))
    j = row.get("judgment")
    if not isinstance(j, dict):
        errs.append("judgment not an object for " + str(pid))
        return errs
    dims = ENUMS[p["dimension"]]
    unknown_j = sorted(set(j) - set(dims) - {"evidence_spans", "note"})
    if unknown_j:
        errs.append("unexpected judgment field(s) for " + str(pid) + ": " + ", ".join(unknown_j))
    for field, allowed_vals in dims.items():
        v = j.get(field)
        if v is None or v == "":
            errs.append("missing required enum: " + field + " for " + str(pid))
        elif v not in allowed_vals:
            errs.append("invalid " + field + " for " + str(pid) + ": " + str(v) +
                        " (valid: " + " / ".join(allowed_vals) + ")")
    spans = j.get("evidence_spans")
    if not isinstance(spans, list) or any(not isinstance(s, str) for s in spans):
        errs.append("evidence_spans must be a list of strings for " + str(pid))
        spans = []
    for i, s in enumerate(spans):
        if not s:
            errs.append("empty evidence span " + str(i + 1) + " for " + str(pid))
        elif s not in p["sut_output"]:
            errs.append("PKT " + str(pid) + ": evidence span not found verbatim in permitted SUT output: " + str(s[:80] + ("..." if len(s) > 80 else "")))
    note = j.get("note")
    if note is not None and not isinstance(note, str):
        errs.append("note must be a string for " + str(pid))
    if pid in seen_ids:
        errs.append("duplicate review for packet " + str(pid))
    seen_ids.add(pid)
    return errs


# ---------------- packet mechanical QC (non-semantic) ----------------

def qc_all():
    packets = load_packets()
    order = load_order()
    by_id = {p["packet_id"]: p for p in packets}
    findings = []
    seen_answers = {}
    for i, pid in enumerate(order, 1):
        p = by_id.get(pid)
        if p is None:
            findings.append({"packet_id": pid, "finding": "packet/order mismatch: packet missing"})
            continue
        if p["dimension"] == "critical_condition" and pid not in order[:10]:
            findings.append({"packet_id": pid, "finding": "order corruption: critical outside first block"})
        if not str(p.get("criterion", "")).strip():
            findings.append({"packet_id": pid, "finding": "criterion empty"})
        if not str(p.get("case_context", "")).strip():
            findings.append({"packet_id": pid, "finding": "case_context empty"})
        sut = p.get("sut_output") or ""
        if not sut.strip():
            findings.append({"packet_id": pid, "finding": "SUT output empty"})
        if not p.get("reviewer_instructions"):
            findings.append({"packet_id": pid, "finding": "reviewer_instructions missing"})
        if p["dimension"] not in ENUMS:
            findings.append({"packet_id": pid, "finding": "lane not in frozen enum map"})
        ans = parse_answer(sut)
        if ans is None:
            findings.append({"packet_id": pid, "finding": "SUT output is not JSON with answer field (raw shown in appendix only)"})
        else:
            a = ans["answer"]
            sig = sha_text(a)
            if sig in seen_answers:
                findings.append({"packet_id": pid, "finding": "duplicate rendered answer with " + seen_answers[sig]})
            else:
                seen_answers[sig] = pid
            for term in FORBIDDEN_UI_TERMS:
                if term in a:
                    findings.append({"packet_id": pid, "finding": "escaped JSON leakage term in answer: " + term})
            claims = ans.get("claims") or []
            if not claims or not any(str(c).strip() for c in claims):
                findings.append({"packet_id": pid, "finding": "structured claims empty"})
            maxline = max((len(x) for x in a.splitlines()), default=0)
            if maxline > 2000:
                findings.append({"packet_id": pid, "finding": "extreme line length: " + str(maxline) + " chars"})
            if re.search(r"\uFFFD", a):
                findings.append({"packet_id": pid, "finding": "malformed unicode (replacement char) in answer"})
            if re.search(r"[aeiouyAEIOUY]aa|\bsokr\b|\boga\b", a) and "\u00e5" not in a:
                findings.append({"packet_id": pid, "finding": "transliteration artifacts throughout answer (ascii-fallback)"})
    if len(by_id) != 74 or len(order) != 74:
        findings.append({"packet_id": None, "finding": "packet/order count mismatch"})
    return {"artifact": "packet-mechanical-qc", "task_id": "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-2-AFK-PREP-V1",
            "findings": findings, "findings_count": len(findings),
            "note": "non-semantic presentation/tooling audit only; no criterion judged"}


# ---------------- review burden metrics (mechanical only) ----------------

def burden():
    packets = load_packets()
    order = load_order()
    by_id = {p["packet_id"]: p for p in packets}
    rows = []
    for i, pid in enumerate(order, 1):
        p = by_id[pid]
        sut = p["sut_output"]
        ans = parse_answer(sut)
        answer = ans["answer"] if ans else ""
        claims = (ans.get("claims") if ans else []) or []
        prov = (ans.get("provenance") if ans else []) or []
        rows.append({
            "pos": i, "packet_id": pid, "lane": p["dimension"],
            "answer_chars": len(answer), "answer_words": len(answer.split()),
            "answer_lines": len(answer.splitlines()),
            "raw_appendix_chars": len(sut),
            "structured_claim_count": len(claims),
            "provenance_count": len(prov),
            "fields_to_fill": 3 if p["dimension"] == "critical_condition" else 4,
            "approx_800col_screens": round(len(answer) / 4800, 1),
        })
    totals = {
        "answer_chars_total": sum(r["answer_chars"] for r in rows),
        "answer_words_total": sum(r["answer_words"] for r in rows),
        "raw_appendix_chars_total": sum(r["raw_appendix_chars"] for r in rows),
        "critical_condition_rows": sum(1 for r in rows if r["lane"] == "critical_condition"),
        "forbidden_claim_rows": sum(1 for r in rows if r["lane"] == "forbidden_claim"),
    }
    return {"artifact": "review-burden-report", "task_id": "NAV-EXPLORE-MEASUREMENT-V3-HUMAN-REVIEW-BATCH-2-AFK-PREP-V1",
            "totals": totals, "rows": rows,
            "note": "mechanical ergonomics only; no semantic difficulty, label, failure or confidence estimates"}


# ---------------- synthetic E2E on an isolated temp copy ----------------

SYNTH_PREFIX = "SYN-"

def make_synthetic_packets(n_critical=2, n_forbidden=3):
    """Clearly-marked synthetic packets with the same schema; never real IDs."""
    out = []
    for i in range(n_critical):
        raw = json.dumps({"answer": "SYNTHETIC TEST DATA answer " + str(i + 1) + ": kommunen oppgir kontaktvei.",
                          "claims": ["SYNTHETIC TEST DATA claim"], "routes": []}, ensure_ascii=False)
        out.append({"packet_id": "PKT-SYN-CRIT-" + str(i + 1), "case_id": "SYN-CRIT-" + str(i + 1),
                    "dimension": "critical_condition", "criterion": "synthetic trigger",
                    "case_context": "synthetic", "sut_output": raw,
                    "reviewer_instructions": list(LANE.INSTRUCTIONS["critical_condition"]),
                    "contract_version": "semantic-judge-contract-v1-4", "created_utc": "2026-09-14T00:00:00Z"})
    for i in range(n_forbidden):
        raw = json.dumps({"answer": "SYNTHETIC TEST DATA forbudt paastand " + str(i + 1) + ".",
                          "claims": ["SYNTHETIC TEST DATA forbudt paastand"], "routes": []}, ensure_ascii=False)
        out.append({"packet_id": "PKT-SYN-FORB-" + str(i + 1), "case_id": "SYN-FORB-" + str(i + 1),
                    "dimension": "forbidden_claim", "criterion": "synthetic forbidden criterion",
                    "case_context": "synthetic", "sut_output": raw,
                    "reviewer_instructions": list(LANE.INSTRUCTIONS["forbidden_claim"]),
                    "contract_version": "semantic-judge-contract-v1-4", "created_utc": "2026-09-14T00:00:00Z"})
    for p in out:
        body = {k: v for k, v in p.items() if k != "packet_sha256"}
        p["packet_sha256"] = sha_text(json.dumps(body, sort_keys=True, ensure_ascii=False))
    return out


def run_synthetic_e2e():
    """Full downstream dry run on synthetic data in a temp dir. Returns evidence dict."""
    steps = []
    packets = make_synthetic_packets()
    by_id = {p["packet_id"]: p for p in packets}
    order = [p["packet_id"] for p in packets]
    reviews = []
    syn_inputs = [
        ("PKT-SYN-CRIT-1", {"critical_evidence_state": "CLEAR_TRIGGER_SUPPORT", "evidence_spans": [], "note": "synthetic"}),
        ("PKT-SYN-CRIT-2", {"critical_evidence_state": "INSUFFICIENT_TO_DECIDE", "evidence_spans": [], "note": "synthetic"}),
        ("PKT-SYN-FORB-1", {"criterion_semantic_match": "NO_MATCH", "speaker_commitment": "ASSERTED",
                            "evidence_spans": ["SYNTHETIC TEST DATA forbudt paastand 1."], "note": ""}),
        ("PKT-SYN-FORB-2", {"criterion_semantic_match": "MATCH", "speaker_commitment": "HEDGED_ASSERTION", "evidence_spans": [], "note": ""}),
        ("PKT-SYN-FORB-3", {"criterion_semantic_match": "UNRESOLVED", "speaker_commitment": "NONCOMMITTAL", "evidence_spans": [], "note": ""}),
    ]
    for pid, j in syn_inputs:
        p = by_id[pid]
        reviews.append({"packet_id": pid, "case_id": p["case_id"], "reviewer_id": "SYNTHETIC-REVIEWER",
                        "contract_version": p["contract_version"], "reviewed_utc": "2026-09-15T00:00:00Z",
                        "judgment": j})
    valid_rows, invalid_rows = [], []
    seen = set()
    for r in reviews:
        errs = validate_review_row(r, by_id, seen, expected_reviewer="SYNTHETIC-REVIEWER")
        if errs:
            invalid_rows.append({"packet_id": r["packet_id"], "errors": errs})
        else:
            valid_rows.append(r)
    steps.append({"step": "schema+evidence validation", "valid": len(valid_rows), "invalid": len(invalid_rows)})
    if invalid_rows or len(valid_rows) != len(reviews):
        return {"verdict": "FAIL", "failed_step": "synthetic reviews must all validate", "detail": invalid_rows}
    derived = []
    for r in valid_rows:
        p = by_id[r["packet_id"]]
        probe = dict(r)
        j = dict(r["judgment"]); j.pop("_synthetic", None)
        probe["judgment"] = j
        ok, why = LANE.validate_review(p, probe)
        if not ok:
            return {"verdict": "FAIL", "failed_step": "lane validation " + r["packet_id"], "detail": why}
        final = LANE.derive_final(p["dimension"], j)
        derived.append({"packet_id": r["packet_id"], "dimension": p["dimension"], "final_verdict": final[0], "synthetic": True})
    steps.append({"step": "frozen lane derive_final", "derived": len(derived)})
    with tempfile.TemporaryDirectory(prefix="afk-prep-e2e-") as td:
        syn = {"artifact": "synthetic-completed-measurement-results", "synthetic": True,
               "deterministic_criteria": 526, "human_reviewed_criteria": len(derived),
               "total_authoritative_criteria": 526 + len(derived), "target": 531,
               "derived": derived}
        path = os.path.join(td, "completed-measurement-results.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(syn, f, indent=2, ensure_ascii=False)
        agg = {"artifact": "synthetic-aggregate-metrics", "synthetic": True,
               "criteria_total": syn["total_authoritative_criteria"],
               "by_dimension": {d: sum(1 for x in derived if x["dimension"] == d) for d in ("critical_condition", "forbidden_claim")}}
        apath = os.path.join(td, "aggregate-metrics.json")
        with open(apath, "w", encoding="utf-8") as f:
            json.dump(agg, f, indent=2, ensure_ascii=False)
        pins = {fn: sha_file(os.path.join(td, fn)) for fn in sorted(os.listdir(td))}
        mpath = os.path.join(td, "synthetic-freeze-manifest.json")
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump({"artifact": "synthetic-freeze-manifest", "synthetic": True, "pins": pins}, f, indent=2)
        reverify = all(sha_file(os.path.join(td, fn)) == h for fn, h in pins.items())
        steps.append({"step": "assemble+aggregate+freeze+hash-verify", "pins": len(pins), "hash_reverify": reverify})
        if not reverify:
            return {"verdict": "FAIL", "failed_step": "hash verification"}
    if len(derived) != len(reviews):
        return {"verdict": "FAIL", "failed_step": "derive count mismatch", "derived": len(derived)}
    return {"verdict": "PASS", "synthetic_packets": len(packets), "synthetic_reviews": len(valid_rows),
            "derived": len(derived), "steps": steps,
            "note": "ran only on SYN-* packets and temp dir; zero authoritative writes"}
