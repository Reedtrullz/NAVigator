#!/usr/bin/env python3
"""One-pass, keyless RC3G prediction driver."""
import json
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOLDOUT = HERE.parent
SNAPSHOT = HOLDOUT / "runtime-snapshot"
COMPONENTS = SNAPSHOT / "components"

FROZEN_FILES = {
    "rc3_engine__engine_rc3.py": Path("rc3_engine/engine_rc3.py"),
    "rc3_engine__decomposition.py": Path("rc3_engine/decomposition.py"),
    "rc3_engine__routing.py": Path("rc3_engine/routing.py"),
    "rc3_engine__arbitration.py": Path("rc3_engine/arbitration.py"),
    "rc3_engine__reviewer_v2.py": Path("rc3_engine/reviewer_v2.py"),
    "rc3_engine__reviewer_bridge.py": Path("rc3_engine/reviewer_bridge.py"),
    "rc2-development__engine__polarity_engine.py":
        Path("rc2-development/engine/polarity_engine.py"),
    "rc2-development__engine__polarity_engine_v02.py":
        Path("rc2-development/engine/polarity_engine_v02.py"),
    "rc2-development__engine__quote_aligner.py":
        Path("rc2-development/engine/quote_aligner.py"),
    "rc2-development__engine__modality.py":
        Path("rc2-development/engine/modality.py"),
    "rc2-development__engine__domain-lexicon.json":
        Path("rc2-development/engine/domain-lexicon.json"),
    "rc2-development__engine__predicate-map.json":
        Path("rc2-development/engine/predicate-map.json"),
}

COMPARATOR_RULES = {
    "numeric_conflict",
    "incompatible_dates",
    "neg_object_conflict",
    "exhaustive_list_exclusion",
    "exhaustive_eller_exclusion",
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_runtime(tmp):
    for source_name, target in FROZEN_FILES.items():
        dst = tmp / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(COMPONENTS / source_name, dst)


def load_runtime(tmp):
    sys.path[:0] = [
        str(tmp / "rc3_engine"),
        str(tmp / "rc2-development" / "engine"),
        str(tmp / "rc2-development"),
    ]
    import engine_rc3 as engine
    import routing
    return engine, routing


def proof_is_structurally_valid(atom, source):
    if atom.get("proof_state") != "ENGINE_PROOF_ACCEPTED":
        return None
    proof = atom.get("proof")
    if not isinstance(proof, dict):
        return False
    span = proof.get("source_span")
    if span:
        return span in source
    return (atom.get("frozen_verdict") == "CONTRADICTED"
            and atom.get("frozen_rule") in COMPARATOR_RULES)


def route_atoms(atoms, claim, source, routing):
    routes = []
    details = []
    for atom in atoms:
        route = routing.route_atom(atom, claim, source)
        routes.append(route)
        details.append({
            "atom_id": atom.get("atom_id"),
            "route": route,
            "proof_state": atom.get("proof_state"),
            "frozen_verdict": atom.get("frozen_verdict"),
        })
    product = routing.aggregate_atoms(
        [{"route": route} for route in routes])
    return routes, details, product["product_action"]


def semantic_from_product(product):
    return {
        "AUTO_SUPPORTED": "SUPPORTED",
        "AUTO_CONTRADICTED": "CONTRADICTED",
        "ABSTAIN_INSUFFICIENT": "INSUFFICIENT_EVIDENCE",
    }.get(product, "REVIEW_REQUIRED")


def main():
    cases_doc = json.loads((HOLDOUT / "generalization-cases.json")
                           .read_text(encoding="utf-8"))
    cases = cases_doc["cases"]
    assert cases_doc["set_id"] == "RC3G-HOLDOUT-V1"
    assert len(cases) == 159
    assert Counter(case.get("track") for case in cases) == {
        "A": 75, "B": 84}
    expected_ids = [case["case_id"] for case in cases]
    assert len(set(expected_ids)) == 159

    started = now()
    rows = []
    runtime_failures = 0
    emitted_atoms = 0
    proof_valid = 0
    proof_checked = 0
    decomposition_failures = 0
    product_counts = Counter()
    route_counts = Counter()

    with tempfile.TemporaryDirectory(prefix="rc3g-runtime-") as td:
        tmp = Path(td)
        stage_runtime(tmp)
        engine, routing = load_runtime(tmp)

        for case in cases:
            claim = case["claim"]
            source = "\n\n".join(s["text"] for s in case["sources"])
            row = {"case_id": case["case_id"], "runtime_status": "OK"}
            try:
                engine_output = engine.judge_claim(claim, source)
                atoms = engine_output["atoms"]
                routes, atom_routes, product = route_atoms(
                    atoms, claim, source, routing)
                checks = [proof_is_structurally_valid(a, source)
                          for a in atoms]
                proof_checked += sum(v is not None for v in checks)
                proof_valid += sum(v is True for v in checks)
                emitted_atoms += len(atoms)
                product_counts[product] += 1
                route_counts.update(routes)
                row.update({
                    "semantic_verdict": semantic_from_product(product),
                    "proof_safe_verdict": (
                        semantic_from_product(product)
                        if product in ("AUTO_SUPPORTED",
                                       "AUTO_CONTRADICTED")
                        else "INSUFFICIENT_EVIDENCE"),
                    "product_action": product,
                    "route": product,
                    "proof_object": {
                        "atom_proofs": [a.get("proof") for a in atoms]
                    },
                    "structural_proof_valid": (
                        all(v is True for v in checks)
                        if any(v is not None for v in checks) else None),
                    "reviewer_used": False,
                    "reviewer_output": None,
                    "atom_results": atoms,
                    "atom_routes": atom_routes,
                    "engine_output": engine_output,
                })
            except Exception as exc:
                runtime_failures += 1
                if "decompos" in type(exc).__name__.lower():
                    decomposition_failures += 1
                row.update({
                    "runtime_status": "RUNTIME_FAILURE",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)[:300],
                })
            rows.append(row)

    completed = now()
    assert len(rows) == 159
    assert len({row["case_id"] for row in rows}) == 159
    assert [row["case_id"] for row in rows] == expected_ids
    assert not any(row["runtime_status"] == "OK" and
                   "product_action" not in row for row in rows)

    artifact = {
        "runtime_snapshot": "NAV-EXPLORE-RC3-GEN-SNAPSHOT-A",
        "holdout": "RC3G-HOLDOUT-V1",
        "core_expected": 159,
        "snapshot_manifest_sha256": sha256(SNAPSHOT / "manifest.json"),
        "generalization_cases_sha256": sha256(
            HOLDOUT / "generalization-cases.json"),
        "started_at": started,
        "completed_at": completed,
        "runtime_config": {
            "engine": "PROOF_ENGINE_RC3",
            "decomposition": "DECOMPOSITION_V1",
            "proof_engine": "PROOF_ENGINE_RC3",
            "reviewer": "REVIEWER_V2 (not invoked)",
            "arbitration": "ARBITRATION_V2",
            "routing": "PRODUCT_ROUTING_V2",
            "reviewer_model": None,
            "temperature": None,
            "reviewer_calls": 0,
        },
        "runtime_metrics": {
            "outcomes_recorded": len(rows),
            "runtime_successes": len(rows) - runtime_failures,
            "runtime_failures": runtime_failures,
            "deterministic_only": len(rows),
            "reviewer_calls": 0,
            "retry_count": 0,
            "auto_supported": product_counts["AUTO_SUPPORTED"],
            "auto_contradicted": product_counts["AUTO_CONTRADICTED"],
            "review_required": product_counts["REVIEW_REQUIRED"],
            "abstain_insufficient": product_counts["ABSTAIN_INSUFFICIENT"],
            "total_auto_coverage": (product_counts["AUTO_SUPPORTED"] +
                                     product_counts["AUTO_CONTRADICTED"]),
            "review_coverage": product_counts["REVIEW_REQUIRED"],
            "abstain_coverage": product_counts["ABSTAIN_INSUFFICIENT"],
            "counter_proof_proposals": 0,
            "counter_proofs_accepted": 0,
            "proof_structurally_valid": proof_valid,
            "proofs_checked": proof_checked,
            "atom_count_emitted": emitted_atoms,
            "decomposition_failures": decomposition_failures,
            "route_distribution": dict(route_counts),
            "product_distribution": dict(product_counts),
            "reserve_executed": 0,
        },
        "predictions": rows,
    }
    out = HERE / "RC3G-predictions.json"
    out.write_text(json.dumps(artifact, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(json.dumps({k: v for k, v in artifact["runtime_metrics"].items()},
                     ensure_ascii=False, sort_keys=True))
    print("WROTE", out, "rows=", len(rows))


if __name__ == "__main__":
    main()
