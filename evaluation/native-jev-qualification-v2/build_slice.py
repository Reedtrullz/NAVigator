#!/usr/bin/env python3
"""Deterministic diagnostic slice for native Jev qualification V2.

Selects from the frozen reference corpus (frozen before this experiment):
  critical_condition: CLEAR_TRIGGER_SUPPORT x5, CLEAR_NON_TRIGGER_SUPPORT x10,
    AMBIGUOUS_OR_CONFLICTING x8, INSUFFICIENT_TO_DECIDE x12, UNRESOLVED x3
  forbidden_claim: MATCH/ASSERTED x6, MATCH/NEGATED x6, NO_MATCH/UNRESOLVED x10,
    resolved-PARTIAL x8 (if present), explicit UNRESOLVED-match x3
Excludes the 12 unlabeled tier-B rows. Deterministic: sorted by canonical_hash,
take first k per frozen label cell.
"""
import json, pathlib

BASE = pathlib.Path(__file__).resolve().parent
CORPUS = BASE.parent / "semantic-reviewer-cost-qualification-v1" / "reference-corpus.jsonl"

rows = [json.loads(l) for l in CORPUS.read_text().splitlines() if l.strip()]
labeled = [r for r in rows if "observation" in r]
excluded = [r["case_id"] for r in rows if "observation" not in r]

def af(r):
    return r["observation"]["authoritative_fields"]

cc = sorted((r for r in labeled if r["lane"] == "critical_condition"), key=lambda r: r["canonical_hash"])
fc = sorted((r for r in labeled if r["lane"] == "forbidden_claim"), key=lambda r: r["canonical_hash"])

cc_by_state = {}
for r in cc:
    cc_by_state.setdefault(af(r)["critical_evidence_state"], []).append(r)

fc_cells = {}
for r in fc:
    fc_cells.setdefault((af(r)["criterion_semantic_match"], af(r)["speaker_commitment"]), []).append(r)

selected = []
selected += cc_by_state.get("CLEAR_TRIGGER_SUPPORT", [])[:5]
selected += cc_by_state.get("CLEAR_NON_TRIGGER_SUPPORT", [])[:10]
selected += cc_by_state.get("AMBIGUOUS_OR_CONFLICTING", [])[:8]
selected += cc_by_state.get("INSUFFICIENT_TO_DECIDE", [])[:12]
selected += cc_by_state.get("UNRESOLVED", [])[:3]
selected += fc_cells.get(("MATCH", "ASSERTED"), [])[:6]
selected += fc_cells.get(("MATCH", "NEGATED"), [])[:6]
selected += fc_cells.get(("NO_MATCH", "UNRESOLVED"), [])[:10]
resolved_partials = sorted(
    (r for cell, v in fc_cells.items() if cell[0] == "PARTIAL" for r in v),
    key=lambda r: r["canonical_hash"])
selected += resolved_partials[:8]
selected += sorted(
    (r for cell, v in fc_cells.items() if cell[0] == "UNRESOLVED" for r in v),
    key=lambda r: r["canonical_hash"])[:3]

seen, deduped = set(), []
for r in selected:
    if r["canonical_hash"] not in seen:
        seen.add(r["canonical_hash"])
        deduped.append(r)
deduped.sort(key=lambda r: r["canonical_hash"])

TRUNCATION_NOTE = "...[MIDDLE_OF_OUTPUT_TRUNCATED_FOR_STATE_SIZE]..."

def redact(sut):
    if len(sut) > 12000:
        return sut[:6000] + TRUNCATION_NOTE + sut[-3000:]
    return sut

slice_rows = []
for r in deduped:
    af_ = af(r)
    if r["lane"] == "critical_condition":
        expected = {"lane": "critical_condition", "critical_evidence_state": af_["critical_evidence_state"]}
    else:
        expected = {"lane": "forbidden_claim",
                    "criterion_semantic_match": af_["criterion_semantic_match"],
                    "speaker_commitment": af_["speaker_commitment"]}
    sut = r["packet"]["sut_output"]
    slice_rows.append({
        "packet_id": r["packet_id"],
        "case_id": r["case_id"],
        "lane": r["lane"],
        "criterion": r["packet"]["criterion"],
        "expected": expected,
        "packet_sha256": r["packet_sha256"],
        "canonical_hash": r["canonical_hash"],
        "sut_len": len(sut),
        "state_sut_for_jev": redact(sut),
        "state_was_truncated": len(sut) > 12000,
    })

chars = sorted(len(r["state_sut_for_jev"]) for r in slice_rows)
raw = sorted(r["sut_len"] for r in slice_rows)
manifest = {
    "experiment": "NAV-EXPLORE-NATIVE-JEV-QUALIFICATION-V2",
    "slice_id": "jev-v2-diagnostic-slice-v1",
    "source_corpus": "evaluation/semantic-reviewer-cost-qualification-v1/reference-corpus.jsonl",
    "source_corpus_sha256": None,
    "selection_rule": "deterministic first-k per frozen label cell by canonical_hash order; documented in build_slice.py docstring",
    "selected_n": len(slice_rows),
    "excluded_unlabeled_n": len(excluded),
    "excluded_unlabeled_case_ids": excluded,
    "state_reduction": {
        "raw_sut_chars_median": raw[len(raw)//2],
        "state_chars_median": chars[len(chars)//2],
        "state_chars_p95": chars[int(len(chars)*0.95)],
        "state_chars_max": chars[-1],
    },
    "cases": slice_rows,
}

import hashlib
manifest["source_corpus_sha256"] = hashlib.sha256(CORPUS.read_bytes()).hexdigest()

(BASE / "selected-case-manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
print(f"selected={len(slice_rows)} excluded_unlabeled={len(excluded)}")
print("state chars median/p95/max:", manifest["state_reduction"]["state_chars_median"],
      manifest["state_reduction"]["state_chars_p95"], manifest["state_reduction"]["state_chars_max"])
