"""Build NAV-EXPLORE-RC3-GEN-SNAPSHOT-A (frozen, pre-authoring).

Copies every runtime component the RC3 engine can load into
runtime-snapshot/components/ with SHA-256 hashes and a manifest.
Idempotent: re-running re-copies and re-hashes the same sources.
"""
import datetime
import hashlib
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SEM = os.path.abspath(os.path.join(HERE, ".."))
RC3_DEV = os.path.join(SEM, "rc3-development")
SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "runtime-snapshot")
COMP = os.path.join(SNAP, "components")

COMPONENTS = [
    ("rc3-dev", "rc3_engine/engine_rc3.py", "PROOF_ENGINE_RC3",
     "engine wrapper + clause-context guard"),
    ("rc3-dev", "rc3_engine/decomposition.py", "DECOMPOSITION_V1",
     "canonical decomposition"),
    ("rc3-dev", "rc3_engine/routing.py", "PRODUCT_ROUTING_V2",
     "routing table + sufficiency classifier + aggregation"),
    ("rc3-dev", "rc3_engine/arbitration.py", "ARBITRATION_V2",
     "proof arbitration"),
    ("rc3-dev", "rc3_engine/reviewer_v2.py", "REVIEWER_V2",
     "reviewer schema/validator (embedded prompt)"),
    ("rc3-dev", "rc3_engine/reviewer_bridge.py",
     "REVIEWER_V2_BRIDGE", "reviewer transport bridge"),
    ("sem", "rc2-development/engine/polarity_engine.py",
     "FROZEN_RC2_BASE_V0_1", "frozen base engine"),
    ("sem", "rc2-development/engine/polarity_engine_v02.py",
     "FROZEN_RC2_BASE_V0_2", "frozen v0.2 wrapper"),
    ("sem", "rc2-development/engine/quote_aligner.py",
     "QUOTE_ALIGNER_FROZEN", "quote aligner"),
    ("sem", "rc2-development/engine/modality.py",
     "MODALITY_FROZEN", "deontic modality helpers"),
    ("sem", "rc2-development/engine/domain-lexicon.json",
     "DOMAIN_LEXICON", "lexicon data"),
    ("sem", "rc2-development/engine/predicate-map.json",
     "PREDICATE_MAP", "predicate data"),
    ("rc3-dev", "routing-calibration.json",
     "ROUTING_CALIBRATION", "frozen routing calibration config"),
    ("rc3-dev", "review_cache.py", "REVIEWER_TRANSPORT",
     "frozen reviewer transport harness"),
]


def main():
    os.makedirs(COMP, exist_ok=True)
    entries = []
    for base, rel, version, role in COMPONENTS:
        root = RC3_DEV if base == "rc3-dev" else SEM
        src = os.path.join(root, rel)
        dst = os.path.join(COMP, rel.replace("/", "__"))
        shutil.copy2(src, dst)
        data = open(dst, 'rb').read()
        entries.append({
            "component": rel,
            "version": version,
            "role": role,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
    manifest = {
        "snapshot_name": "NAV-EXPLORE-RC3-GEN-SNAPSHOT-A",
        "status": "FROZEN_FOR_GENERALIZATION_HOLDOUT_ONLY",
        "not_release_candidate": True,
        "frozen_at": datetime.datetime.now().astimezone()
                       .isoformat(timespec="seconds"),
        "frozen_before": "holdout case authoring",
        "source_state": "RC3_NOT_READY "
                        "(NAV-EXPLORE-RC3-ARCHITECTURE-REPAIR outcome)",
        "runtime_changes_after_freeze":
            "forbidden; if runtime changes later, this holdout must "
            "not evaluate that change in the same cycle",
        "execution_on_holdout":
            "forbidden in this construction task (G1/G2 separate phase)",
        "architecture_versions": {
            "decomposition": "DECOMPOSITION_V1",
            "proof_engine": "PROOF_ENGINE_RC3",
            "reviewer": "REVIEWER_V2",
            "arbitration": "ARBITRATION_V2",
            "routing": "PRODUCT_ROUTING_V2",
            "rc2_base": "polarity_engine v0.1 + v0.2 wrapper "
                        "(RC2 freeze, unmodified)",
        },
        "prompt_hash_note":
            "REVIEWER_V2 prompt and output schema are embedded in "
            "reviewer_v2.py; the file hash covers them",
        "frozen_routing_table": {
            "ENGINE_PROOF_ACCEPTED+SUPPORTED": "AUTO_SUPPORTED",
            "ENGINE_PROOF_ACCEPTED+CONTRADICTED": "AUTO_CONTRADICTED",
            "ENGINE_UNSAFE": "REVIEW_REQUIRED",
            "ENGINE_CONFLICT": "REVIEW_REQUIRED",
            "ENGINE_NO_PROOF":
                "sufficiency classifier -> ABSTAIN_INSUFFICIENT "
                "or REVIEW_REQUIRED",
        },
        "thresholds_note":
            "no confidence thresholds in routing (proof-bounded); "
            "routing-calibration.json hashed as frozen config",
        "components": entries,
    }
    with open(os.path.join(SNAP, "manifest.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    mh = hashlib.sha256(open(os.path.join(SNAP, "manifest.json"),
                             "rb").read()).hexdigest()
    with open(os.path.join(SNAP, "hashes.txt"), "w") as f:
        for e in entries:
            flat = e['component'].replace('/', '__')
            f.write(e['sha256'] + '  components/' + flat + '\n')
    with open(os.path.join(SNAP, "manifest.sha256"), "w") as f:
        f.write(mh + "  manifest.json\n")
    print("MANIFEST_SHA", mh)
    print("COMPONENTS", len(entries))


if __name__ == "__main__":
    main()
