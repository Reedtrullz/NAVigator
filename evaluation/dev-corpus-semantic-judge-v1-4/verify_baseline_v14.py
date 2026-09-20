#!/usr/bin/env python3
"""V1.4 baseline integrity: re-verify the 29 historical artifacts and the
V1.3M migration artifacts, read-only."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # evaluation/

EXPECTED_29 = {
    "evaluation/dev-corpus-v1/manifest.json": "9c265731e6e17ea54844b6db646dac4abe1901e49ee1c5ce56c3ec081db177ef",
    "evaluation/dev-corpus-scorer-v1/scorer-manifest.json": "cca4a57732cb9ba53c504c69c2abd4248e11281d535499e3ad055b13ec74e71c",
    "evaluation/dev-corpus-semantic-judge-v1/semantic-judge-contract-v1.json": "c61b9ad853327c03685726535420f14978028230bc84976122d22ccaaecb52fd",
    "evaluation/dev-corpus-semantic-judge-v1/judge-validation-gold.json": "e1925e6063d44d28fadd84d74b91bd6379f8939d21cf6b33cecdcb334b2b53e3",
    "evaluation/dev-corpus-semantic-judge-v1/official-validation-results.json": "31a3e0123b72af5059416f0c086aa7696f530ab77497ebd31e74a4ffe21dfb46",
    "evaluation/dev-corpus-semantic-judge-v1/stability-results.json": "73ecdee1ddb59aa0d24ac8c48759daee620196569841e1578f5b72a615b99f67",
    "evaluation/dev-corpus-semantic-judge-v1/semantic-judge-manifest.json": "44a8ed005e35c7ce4522e1b87d78b5b452da019c0ff3fa32f6cf5dc470f20557",
    "evaluation/dev-corpus-semantic-judge-v1/scorer-v1-semantic-manifest.json": "9fb6fc67dc041f8bb220d7f3c2c4b36cc18d0281170e5a9bd2a1eaa3d90b2049",
    "evaluation/dev-corpus-scorer-v1-semantic/semantic_adapter.py": "385a7b5edef37e42584f648ee165fe8a2b04f01ee4104946bf74419f82f24f9a",
    "evaluation/dev-corpus-scorer-v1-semantic/integration_test.py": "d875b42fb750781fb029bd03daee97ddc0bea38a62fa9520cfdc441c1b38b002",
    "evaluation/dev-corpus-semantic-judge-v1-1/TASK-LOCK.json": "fc7211ad4cdf45ef20b8debdff25b4a5f0043c58e2217ba9d1fc099e8ce939d3",
    "evaluation/dev-corpus-semantic-judge-v1-1/semantic-judge-contract-v1-1.json": "fc47022f24038507e6c95f0559ea6cbd4c4e1ed03805013a2b8ba1bf52047f70",
    "evaluation/dev-corpus-semantic-judge-v1-1/semantic-judge-manifest-v1-1.json": "b4b128b71be183430cfa05785d0b2fc4dda3604da4bf9c14db47bcae44f0b3e4",
    "evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-fixtures-v1-1.json": "442f34fd8fc64335f31c3dd6b1e8ee026515bdbde6e59e551d6929eb7e088f47",
    "evaluation/dev-corpus-semantic-judge-v1-1/judge-validation-gold-v1-1.UNFROZEN.json": "9bc2c4c55ffe691b9b90b69b04543bd099dd0a02ece636c11bd7b57cbd224ee0",
    "evaluation/dev-corpus-semantic-judge-v1-1/annotation-agreement.json": "e4c5cb3dec10303a797882ae646ebb0fcef02b7899829b76ee0f73b5e64a5a7b",
    "evaluation/dev-corpus-semantic-judge-v1-1/final-report.md": "40cc03c30a483f0f69aa6628c1405fcc231255a26f4078b8bcd0995db3a1e9c4",
    "evaluation/dev-corpus-semantic-judge-v1-2/TASK-LOCK.json": "708c1fffd0d0f3c5adaf9d92ed8cd8c7216b2fc1d64d9f6a6fb1992a7bc15b40",
    "evaluation/dev-corpus-semantic-judge-v1-2/semantic-judge-contract-v1-2.json": "5747d8d1b70b1f5879235dadf1b746efc86dac9029dbb541534718da07bd815b",
    "evaluation/dev-corpus-semantic-judge-v1-2/semantic-judge-result-v1-2.schema.json": "bf172ecd1154c565831fa3eed3948b514c75e299cdc4a11ed7d187123b74bd86",
    "evaluation/dev-corpus-semantic-judge-v1-2/prompt-freeze-v1-2.json": "bf7cc31bc8e0e164156832e84608474a80ee040e2485282ff10247881db9b610",
    "evaluation/dev-corpus-semantic-judge-v1-2/model-calibration.json": "36efb12ed31384a4aa5582433937e90765fe58d6e4d6d05f97b15452186de3a0",
    "evaluation/dev-corpus-semantic-judge-v1-2/model-calibration-run.json": "86e3729ef3c9213fa7cb63640162f452110f8039de866a6c79eaf291e26051b7",
    "evaluation/dev-corpus-semantic-judge-v1-2/judge-validation-fixtures-v1-2.json": "51bcc8e21138f840d5a451bc4fcfd9328f025aabb40b9c897add91b1ac777918",
    "evaluation/dev-corpus-semantic-judge-v1-2/human-label-pass1-v1-2.json": "fdaf9f0a8dc520944e02e1cdd42e6e2b2306e720a3e52bf0b5032450f874fa20",
    "evaluation/dev-corpus-semantic-judge-v1-2/human-label-pass2-v1-2.json": "e408fa2d429567d2ed011482c6701e7c0f13534102c11abc3ef19afccd542669",
    "evaluation/dev-corpus-semantic-judge-v1-2/annotation-agreement-v1-2.json": "86c5341e1450ae178f9fe6f3cf8bc3bbc390c3c1655e5b3dd03e66f4a034fab5",
    "evaluation/dev-corpus-semantic-judge-v1-2/judge-validation-gold-v1-2.UNFROZEN.json": "07dc7c783b195cb11963af476d1a5535b3e8971270d11a302e068a22c703d6da",
    "evaluation/dev-corpus-semantic-judge-v1-2/final-report.md": "a498f5aac7b37e42ab50f1de6308707461fad25927d96d4f7275be7bac91e6cb",
}

V13M_ARTIFACTS = [
    "TASK-LOCK.json",
    "migration-rationale.md",
    "source-artifact-pins.json",
    "model-identity.json",
    "transport-smoke.json",
    "boundary-calibration-a.json",
    "boundary-calibration-a-label1.json",
    "boundary-calibration-a-label2.json",
    "boundary-calibration-a-agreement.json",
    "set-a-run.json",
    "set-a-agreement.json",
    "calibration-a-run.log",
    "final-report.md",
    "semantic-judge-manifest-v1-3m.json",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    results = {"historical_29": {}, "v1_3m_artifacts": {}}
    all_match = True
    for rel, expected in EXPECTED_29.items():
        actual = sha256(os.path.join(ROOT, rel))
        ok = actual == expected
        all_match &= ok
        results["historical_29"][rel] = {
            "expected": expected, "actual": actual, "match": ok}
    for name in V13M_ARTIFACTS:
        p = os.path.join(HERE, "..", "dev-corpus-semantic-judge-v1-3m", name)
        results["v1_3m_artifacts"][name] = sha256(os.path.abspath(p))
    out = {
        "artifact": "V1.4 baseline integrity (29 historical + 14 V1.3M artifacts)",
        "historical_count_expected": 29,
        "historical_count_verified": len(results["historical_29"]),
        "v1_3m_count": len(results["v1_3m_artifacts"]),
        "all_match": all_match,
        "historical_writes": 0,
        "verification_mode": "read-only SHA256; no writes into historical lineages",
        **results,
    }
    with open(os.path.join(HERE, "baseline-integrity.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("BASELINE_INTEGRITY", "PASS" if all_match else "FAIL",
          f"29/29 historical + {len(results['v1_3m_artifacts'])} V1.3M artifacts")
    sys.exit(0 if all_match else 1)


if __name__ == "__main__":
    main()
