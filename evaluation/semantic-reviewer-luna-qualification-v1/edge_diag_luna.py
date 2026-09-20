import json, sys, os

V1 = os.path.join(os.path.dirname(os.getcwd()), "semantic-reviewer-cost-qualification-v1")
sys.path.insert(0, V1)
from run_transport_calibration import load_frozen

contract, split, rows = load_frozen()
dp = json.load(open("dual-pass-results.json"))

AUTH = {"forbidden_claim": ["criterion_semantic_match", "speaker_commitment"],
        "critical_condition": ["critical_evidence_state"]}

out = {}
for lane, data in dp["configs"]["LUNA-HIGH"].items():
    edge_hashes = set(split["partitions"][lane]["EDGE"])
    a = {r["canonical_hash"]: r for r in data["A"]}
    b = {r["canonical_hash"]: r for r in data["B"]}
    valid = errs = 0
    for h in edge_hashes:
        ref = tuple(rows[h]["observation"]["authoritative_fields"][f] for f in AUTH[lane])
        for r in (a[h], b[h]):
            if r["status"] == "OK":
                valid += 1
                if tuple((r.get("parsed") or {}).get(f) for f in AUTH[lane]) != ref:
                    errs += 1
    out[lane] = {"edge_rows": len(edge_hashes), "valid_passes": valid, "ref_errors": errs,
                 "pass_level_agreement": round((valid - errs) / max(1, valid), 4)}

json.dump(out, open("edge-agreement-diagnostic.json", "w"), indent=2)
print(json.dumps(out, indent=1))
