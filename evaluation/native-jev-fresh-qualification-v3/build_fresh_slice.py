#!/usr/bin/env python3
"""Deterministic fresh-pool builder for native Jev qualification V3.

Frozen before any fresh label inspection:
  - corpus SHA asserted
  - exclude every row of the V2 57-row slice (case_id OR packet_id level)
  - exclude the 12 unlabeled tier-B rows
  - dedup by canonical_hash (first by canonical_hash order kept)
  - no sampling: every remaining labeled row is included, sorted by canonical_hash
Redaction identical to V2. Expected fields carried mechanically from frozen gold.
"""
import hashlib, json, pathlib

BASE = pathlib.Path(__file__).resolve().parent
V2 = BASE.parent / "native-jev-qualification-v2"
CORPUS = BASE.parent / "semantic-reviewer-cost-qualification-v1" / "reference-corpus.jsonl"

EXPECTED_CORPUS_SHA = "b85caaaa64f3393f27f8177f0b4979e6139c0ff8d18ee3c80efb45eab9e11c2b"
EXPECTED_CASE_ID_LIST_SHA = "517cd72128e80e6de67963df156d8ba3be9179d2e7339939642cc34bf74540af"
EXPECTED_PACKET_ID_LIST_SHA = "4fb55b026360e8cb03587f817084dffe2c31c3d80f62c865a1d30c5757112ff3"

rows = [json.loads(l) for l in CORPUS.read_text().splitlines() if l.strip()]
corpus_sha = hashlib.sha256(CORPUS.read_bytes()).hexdigest()
assert corpus_sha == EXPECTED_CORPUS_SHA, "source corpus SHA mismatch"

def id_list_sha(ids):
    return hashlib.sha256(json.dumps(sorted(ids), separators=(",", ":")).encode()).hexdigest()

v2_manifest = json.loads((V2 / "selected-case-manifest.json").read_text())
v2_case_ids = set(c["case_id"] for c in v2_manifest["cases"])
v2_packet_ids = set(c["packet_id"] for c in v2_manifest["cases"])
assert id_list_sha(v2_case_ids) == EXPECTED_CASE_ID_LIST_SHA, "V2 case_id exclusion hash mismatch"
assert id_list_sha(v2_packet_ids) == EXPECTED_PACKET_ID_LIST_SHA, "V2 packet_id exclusion hash mismatch"

labeled = [r for r in rows if "observation" in r]
excluded_unlabeled = [r["case_id"] for r in rows if "observation" not in r]

pool = [r for r in labeled
        if r["case_id"] not in v2_case_ids and r["packet_id"] not in v2_packet_ids]

seen, deduped = set(), []
for r in sorted(pool, key=lambda x: x["canonical_hash"]):
    if r["canonical_hash"] not in seen:
        seen.add(r["canonical_hash"])
        deduped.append(r)

TRUNCATION_NOTE = "...[MIDDLE_OF_OUTPUT_TRUNCATED_FOR_STATE_SIZE]..."

def redact(sut):
    if len(sut) > 12000:
        return sut[:6000] + TRUNCATION_NOTE + sut[-3000:]
    return sut

def af(r):
    return r["observation"]["authoritative_fields"]

slice_rows = []
for r in deduped:
    af_ = af(r)
    if r["lane"] == "critical_condition":
        expected = {"lane": "critical_condition",
                    "critical_evidence_state": af_["critical_evidence_state"]}
    else:
        expected = {"lane": "forbidden_claim",
                    "criterion_semantic_match": af_["criterion_semantic_match"],
                    "speaker_commitment": af_["speaker_commitment"]}
    slice_rows.append({
        "packet_id": r["packet_id"],
        "case_id": r["case_id"],
        "lane": r["lane"],
        "criterion": r["packet"]["criterion"],
        "expected": expected,
        "packet_sha256": r["packet_sha256"],
        "canonical_hash": r["canonical_hash"],
        "sut_len": len(r["packet"]["sut_output"]),
        "state_sut_for_jev": redact(r["packet"]["sut_output"]),
        "state_was_truncated": len(r["packet"]["sut_output"]) > 12000,
    })

case_id_list = sorted(set(s["case_id"] for s in slice_rows))
nl = chr(10)
manifest = {
    "experiment": "NAV-EXPLORE-NATIVE-JEV-FRESH-FROZEN-QUALIFICATION-V3",
    "dataset_id": "cost-qual-v1-reference-corpus-fresh-remainder-v3",
    "source_corpus": "evaluation/semantic-reviewer-cost-qualification-v1/reference-corpus.jsonl",
    "source_corpus_sha256": corpus_sha,
    "exclusion": {
        "v2_slice_rows_excluded_by_case_id_or_packet_id": len(v2_case_ids),
        "v2_case_id_list_sha256": id_list_sha(v2_case_ids),
        "v2_packet_id_list_sha256": id_list_sha(v2_packet_ids),
        "excluded_unlabeled_n": len(excluded_unlabeled),
        "excluded_unlabeled_case_ids": sorted(excluded_unlabeled),
        "canonical_hash_duplicates_removed": len(pool) - len(deduped),
    },
    "selection_rule": "no sampling; all remaining labeled rows after V2-slice/unlabeled/dedup exclusion, sorted by canonical_hash",
    "selected_n": len(slice_rows),
    "fresh_case_id_list_sha256": id_list_sha(case_id_list),
    "cases": slice_rows,
}

(BASE / "fresh-case-manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + nl)
fm_sha = hashlib.sha256((BASE / "fresh-case-manifest.json").read_bytes()).hexdigest()
(BASE / "fresh-case-manifest.sha256").write_text(fm_sha + "  fresh-case-manifest.json" + nl)

from collections import Counter
strata = Counter()
for s in slice_rows:
    e = s["expected"]
    if e["lane"] == "critical_condition":
        strata["critical/" + e["critical_evidence_state"]] += 1
    else:
        strata["forbidden/" + e["criterion_semantic_match"] + "/" + e["speaker_commitment"]] += 1
print(json.dumps(strata, indent=1, sort_keys=True))
print(f"selected_n={len(slice_rows)} distinct_case_ids={len(case_id_list)} dedup_removed={len(pool)-len(deduped)}")
print("fresh_case_manifest_sha256=" + fm_sha)
