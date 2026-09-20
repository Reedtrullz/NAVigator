#!/usr/bin/env python3
"""Build the unique semantic-reviewer reference corpus for cost qualification.

One row per unique canonical semantic review input. Observations come from
frozen Measurement V3 lineages only. No model calls are made here.
"""
import hashlib
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SOURCES = [
    {
        "lineage_id": "W3",
        "label": "evaluation/measurement-v3-remeasure-repair-wave-3",
        "packets": "semantic-review-packets.jsonl",
        "primary": "primary-consensus.json",
        "residual": "residual-consensus.json",
        "freeze": "semantic-review-freeze-manifest.json",
        "preferred_order": 1,
    },
    {
        "lineage_id": "W2",
        "label": "evaluation/measurement-v3-remeasure-repair-wave-2",
        "packets": "semantic-review-packets.jsonl",
        "primary": "primary-consensus.json",
        "residual": "residual-consensus.json",
        "freeze": "semantic-review-freeze-manifest.json",
        "preferred_order": 2,
    },
    {
        "lineage_id": "B1",
        "label": "evaluation/measurement-v3-human-review-batch-2-repaired",
        "packets": "human-review-packets.jsonl",
        "primary": None,
        "consolidated": "../measurement-v3-astra-review-batch-1/consensus-results.json",
        "freeze": None,
        "preferred_order": 3,
    },
    {
        "lineage_id": "W4",
        "label": "evaluation/measurement-v3-remeasure-repair-wave-4-quota-safe-v1",
        "packets": "semantic-review-packets.jsonl",
        "primary": None,
        "derived": "../measurement-v3-remeasure-wave-4-quota-resume-v1/derived-measurement-results.json",
        "freeze": None,
        "resume_hashes": "../measurement-v3-remeasure-wave-4-quota-resume-v1/hashes.txt",
        "preferred_order": 4,
    },
    {
        "lineage_id": "W1",
        "label": "evaluation/measurement-v3-remeasure-repair-wave-1",
        "packets": "semantic-review-packets.jsonl",
        "primary": "primary-consensus.json",
        "residual": "residual-consensus.json",
        "freeze": "semantic-review-freeze-manifest.json",
        "preferred_order": 5,
    },
]

KNOWN_SENSITIVITY_CASE = "ESC-DIS-118"


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sha_obj(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def canonical_hash(packet):
    body = {
        "contract_version": packet["contract_version"],
        "dimension": packet["dimension"],
        "case_context": packet["case_context"],
        "criterion": packet["criterion"],
        "sut_output": packet["sut_output"],
    }
    return sha_obj(body)


def packet_body_sha(packet):
    body = dict(packet)
    body.pop("packet_sha256", None)
    return sha_obj(body)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def verify_pins(rel_root, hashes_file, results, resolve_root=None):
    path = os.path.join(ROOT, rel_root, hashes_file)
    base = os.path.join(ROOT, resolve_root) if resolve_root else os.path.join(ROOT, rel_root)
    verified, failed = 0, []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            sha, name = line.split(maxsplit=1)
            target = os.path.join(base, name.strip())
            if not os.path.exists(target):
                failed.append({"file": name.strip(), "reason": "MISSING"})
                continue
            actual = sha_file(target)
            if actual == sha:
                verified += 1
            elif name.strip() == "TASK-LOCK.json" and os.path.exists(target):
                failed.append({
                    "file": name.strip(),
                    "reason": "EXPECTED_TASK_LOCK_STATUS_FLIP",
                    "current_sha256": actual,
                    "detail": "frozen hash predates terminal status flip; "
                              "review artifacts unaffected",
                })
            else:
                failed.append({"file": name.strip(), "reason": "HASH_MISMATCH"})
    results.append({
        "lineage": rel_root,
        "hashes_file": hashes_file,
        "pins_total": verified + len(failed),
        "pins_verified": verified,
        "pin_failures": failed,
    })


def pass_fields(rec):
    fields = rec.get("authoritative_fields") or rec.get("observation_fields") or {}
    return fields


def extract_observations(source, packets_by_id):
    """Return {packet_id: obs_record} with only frozen consensus/adjudication."""
    obs = {}
    diag = {}

    def add(packet_id, kind, status, passes, authority, subtype, model):
        rec = {
            "packet_id": packet_id,
            "kind": kind,
            "consensus_status": status,
            "passes": passes,
            "authority_class": authority,
            "authority_subtype": subtype,
            "observation_model": model,
        }
        if status in ("LLM_CONSENSUS", "LLM_ADJUDICATION_CONSENSUS") and all(
            p.get("validity") == "OK" for p in passes
        ):
            obs[packet_id] = rec
        else:
            diag[packet_id] = rec

    primary_path = source.get("primary")
    if primary_path:
        data = json.load(open(os.path.join(ROOT, source["label"], primary_path),
                              encoding="utf-8"))
        for entry in data["packets"]:
            passes = [entry.get("astra_a"), entry.get("astra_b")]
            add(entry["packet_id"], "PRIMARY", entry["consensus_status"],
                passes, entry.get("authority_class"), None, "gpt-6-astra")
    if source.get("consolidated"):
        data = json.load(open(os.path.join(ROOT, source["label"],
                                           source["consolidated"]),
                              encoding="utf-8"))
        for entry in data["packets"]:
            passes = [entry.get("astra_a"), entry.get("astra_b")]
            add(entry["packet_id"], "PRIMARY", entry["consensus_status"],
                passes, entry.get("authority_class"), None, "gpt-6-astra")
    if source.get("residual"):
        data = json.load(open(os.path.join(ROOT, source["label"],
                                           source["residual"]),
                              encoding="utf-8"))
        for entry in data["packets"]:
            passes = [entry.get("sol_a") or entry.get("adj_a"),
                      entry.get("sol_b") or entry.get("adj_b")]
            status = entry["consensus_status"]
            model = ("gpt-5.6-sol" if entry.get("sol_a")
                     else "gpt-6-astra-adjudicator")
            add(entry["packet_id"], "RESIDUAL", status, passes,
                entry.get("authority_class"), entry.get("authority_subtype"),
                model)
    if source.get("derived"):
        data = json.load(open(os.path.join(ROOT, source["label"],
                                           source["derived"]),
                              encoding="utf-8"))
        for row in data["derived_rows"]:
            rec = {
                "packet_id": row["packet_id"],
                "kind": "RESUME",
                "consensus_status": "LLM_CONSENSUS",
                "passes": [{"validity": "OK",
                            "authoritative_fields": row["observation_fields"]},
                           {"validity": "OK",
                            "authoritative_fields": row["observation_fields"]}],
                "authority_class": row["authority_class"],
                "authority_subtype": row.get("observation_source"),
                "observation_model": row.get("observation_model"),
                "evidence_spans": row.get("evidence_spans", []),
                "observation_record_shas": row.get("observation_record_shas"),
            }
            if row["authority_class"] in ("LLM_REVIEWED", "LLM_ADJUDICATED"):
                obs[row["packet_id"]] = rec
            else:
                diag[row["packet_id"]] = rec
    return obs, diag


def main():
    integrity = []
    rows = []
    exclusions = []
    conflicts = []
    conflict_details = defaultdict(list)

    # 1. Verify frozen pins for all source lineages.
    for source in SOURCES:
        hashes_file = source.get("resume_hashes") or "hashes.txt"
        hashes_path = os.path.join(ROOT, source["label"], hashes_file)
        if source.get("resume_hashes"):
            verify_pins(source["label"], hashes_file, integrity,
                        resolve_root="evaluation/measurement-v3-remeasure-wave-4-quota-resume-v1")
        elif os.path.exists(hashes_path):
            verify_pins(source["label"], hashes_file, integrity)
        elif source["lineage_id"] == "B1":
            verify_pins("evaluation/measurement-v3-astra-review-batch-1", "hashes.txt",
                        integrity, resolve_root="evaluation/measurement-v3-astra-review-batch-1")
        else:
            integrity.append({"lineage": source["label"], "hashes_file":
                              hashes_file, "pins_total": 0,
                              "pins_verified": 0,
                              "pin_failures": [{"file": hashes_file,
                                                "reason": "NO_HASHES_FILE"}]})

    # 2. Load packets, verify body hashes, compute canonical hashes.
    # Authoritative repaired-criterion case list from the batch-2 manifest.
    batch_manifest = json.load(open(
        os.path.join(ROOT, "evaluation/measurement-v3-human-review-batch-2-repaired",
                     "human-review-batch-manifest.json"), encoding="utf-8"))
    repaired_case_ids = set()
    for source in SOURCES:
        if source["lineage_id"] != "B1":
            continue
        packets = load_jsonl(os.path.join(ROOT, source["label"],
                                          source["packets"]))
        for p in packets:
            if p["packet_id"] in batch_manifest.get("criterion_repaired_packets", []):
                repaired_case_ids.add(p["case_id"])

    hash_index = defaultdict(list)  # canonical_hash -> [(source, packet, obs)]
    for source in SOURCES:
        packets = load_jsonl(os.path.join(ROOT, source["label"],
                                          source["packets"]))
        bad = [p["packet_id"] for p in packets
               if packet_body_sha(p) != p["packet_sha256"]]
        if bad:
            raise SystemExit("PACKET_BODY_HASH_FAILURE %s %s"
                             % (source["label"], bad[:5]))
        if source["lineage_id"] == "B1":
            manifest_hashes = {h["packet_id"]: h["sha256"]
                               for h in batch_manifest["packet_hashes"]}
            manifest_bad = [p["packet_id"] for p in packets
                            if manifest_hashes.get(p["packet_id"]) != p["packet_sha256"]]
            if manifest_bad:
                raise SystemExit("B1_MANIFEST_BINDING_FAILURE %s" % manifest_bad[:5])
        obs, diag = extract_observations(source, packets)
        for p in packets:
            pid = p["packet_id"]
            chash = canonical_hash(p)
            record = {
                "source": source,
                "packet": p,
                "obs": obs.get(pid),
                "diag": diag.get(pid),
            }
            hash_index[chash].append(record)

    # 3. Reference conflict audit + tier assignment.
    tier_a, tier_b = 0, 0
    for chash, records in hash_index.items():
        eligible = [r for r in records if r["obs"]]
        fields_list = []
        for r in eligible:
            fields_list.append((r, pass_fields(r["obs"])))
        conflict = False
        if len(fields_list) >= 2:
            base = fields_list[0][1]
            for _, fields in fields_list[1:]:
                if fields != base:
                    conflict = True
        if conflict:
            conflicts.append({
                "canonical_hash": chash,
                "resolution": "EXCLUDED_FROM_TIER_A",
                "observations": [
                    {"source": r["source"]["lineage_id"],
                     "packet_id": r["packet"]["packet_id"],
                     "fields": fields}
                    for r, fields in fields_list
                ],
            })
        # Preferred observation source for the row.
        chosen = None
        for r in sorted(records, key=lambda x: x["source"]["preferred_order"]):
            if r["obs"]:
                chosen = r
                break
        case_id = records[0]["packet"]["case_id"]
        lane = records[0]["packet"]["dimension"]
        if case_id in repaired_case_ids:
            exclusions.append({
                "canonical_hash": chash,
                "case_id": case_id,
                "lane": lane,
                "reason": "CRITERION_DEFECT_REPAIRED",
                "detail": "criterion repaired via "
                          "NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1 "
                          "(R061-A/R070-A/R073-A); historical observation "
                          "not usable for qualification",
            })
            continue
        has_diag = any(r["diag"] for r in records)
        if case_id == KNOWN_SENSITIVITY_CASE:
            exclusions.append({
                "canonical_hash": chash,
                "case_id": case_id,
                "lane": lane,
                "reason": "KNOWN_MEASUREMENT_SENSITIVITY",
                "detail": "case tied to unresolved Measurement sensitivity; "
                          "excluded from Tier A regardless of observation "
                          "source",
            })
            continue
        if conflict:
            continue  # already recorded as conflict
        if not eligible:
            if has_diag:
                tier_b += 1
                rows.append(make_row(chash, records, chosen=None, tier="B"))
            else:
                exclusions.append({
                    "canonical_hash": chash,
                    "case_id": case_id,
                    "lane": lane,
                    "reason": "NO_FROZEN_OBSERVATION",
                    "detail": "no eligible consensus/adjudication and no "
                              "diagnostic record in any source lineage",
                })
            continue
        r = chosen or eligible[0]
        tier_a += 1
        rows.append(make_row(chash, records, chosen=r, tier="A"))

    # 4. Write artifacts.
    with open(os.path.join(HERE, "reference-corpus.jsonl"), "w",
              encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    lane_counts = Counter(r["lane"] for r in rows)
    tier_lane = Counter((r["tier"], r["lane"]) for r in rows)
    provenance = {
        "artifact": "reference-provenance",
        "task_id": "NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V1",
        "canonical_hash_contract": "WAVE4-QUOTA-SAFE-V1 "
            "(sha256 of {contract_version, dimension, case_context, "
            "criterion, sut_output}, sort_keys, ensure_ascii=False)",
        "semantic_contract_version": "semantic-judge-contract-v1-4",
        "source_lineages": [
            {"lineage_id": s["lineage_id"], "label": s["label"],
             "packets_file": s["packets"],
             "preferred_order": s["preferred_order"]}
            for s in SOURCES
        ],
        "summary": {
            "unique_canonical_inputs": len(rows),
            "tier_a": tier_a,
            "tier_b": tier_b,
            "excluded_total": len(exclusions),
            "excluded_by_reason": dict(Counter(e["reason"] for e in exclusions)),
            "reference_conflicts": len(conflicts),
            "lanes": dict(lane_counts),
            "tier_by_lane": {("%s_%s" % k): v for k, v in tier_lane.items()},
        },
        "reference_target_semantics":
            "AGREEMENT_WITH_FROZEN_AUTHORITATIVE_SEMANTIC_REFERENCE",
        "not_human_ground_truth": True,
    }
    json.dump(provenance, open(os.path.join(HERE, "reference-provenance.json"),
                               "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    json.dump({"artifact": "reference-exclusions", "exclusions": exclusions},
              open(os.path.join(HERE, "reference-exclusions.json"), "w",
                   encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump({"artifact": "reference-conflicts", "conflicts": conflicts,
               "policy": "same canonical hash with disagreeing historical "
                         "authoritative observations is excluded from Tier A; "
                         "no newest/strongest/majority resolution"},
              open(os.path.join(HERE, "reference-conflicts.json"), "w",
                   encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump({"artifact": "input-integrity",
               "pin_verification": integrity,
               "all_pins_verified": all(not i["pin_failures"] for i in integrity)},
              open(os.path.join(HERE, "input-integrity.json"), "w",
                   encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(provenance["summary"], indent=1))
    print("pin failures:", sum(len(i["pin_failures"]) for i in integrity))


def make_row(chash, records, chosen, tier):
    packet = (chosen or records[0])["packet"]
    obs = chosen["obs"] if chosen else None
    diag = next((r["diag"] for r in records if r["diag"]), None)
    source = (chosen or records[0])["source"]
    freeze_sha = None
    if source.get("freeze"):
        fp = os.path.join(ROOT, source["label"], source["freeze"])
        if os.path.exists(fp):
            freeze_sha = sha_file(fp)
    row = {
        "canonical_hash": chash,
        "tier": tier,
        "lane": packet["dimension"],
        "case_id": packet["case_id"],
        "packet_id": packet["packet_id"],
        "packet_sha256": packet["packet_sha256"],
        "contract_version": packet["contract_version"],
        "packet": packet,
        "source_lineage": source["label"],
        "source_review_freeze_sha256": freeze_sha,
    }
    if obs:
        row["observation"] = {
            "authoritative_fields": pass_fields(obs["passes"][0])
                if obs.get("passes") else pass_fields(obs),
            "authority_class": obs["authority_class"],
            "authority_subtype": obs.get("authority_subtype"),
            "observation_model": obs.get("observation_model"),
            "consensus_status": obs["consensus_status"],
            "evidence_spans": obs.get("evidence_spans")
                or obs["passes"][0].get("evidence_spans", []),
        }
    else:
        row["diagnostic_observation"] = {
            "consensus_status": diag["consensus_status"] if diag else None,
            "note": "no eligible frozen consensus/adjudication for this input",
        }
    return row


if __name__ == "__main__":
    main()
