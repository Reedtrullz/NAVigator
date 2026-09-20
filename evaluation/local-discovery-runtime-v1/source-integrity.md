# Source Integrity - Local Discovery Runtime Prototype V1

Task: NAV-EXPLORE-LOCAL-DISCOVERY-RUNTIME-PROTOTYPE-V1
Date: 2026-09-09

## Frozen Artifacts - SHA Re-verification

All frozen inputs verified byte-identical at task close (sha256, full file):

| Artifact | SHA-256 (first 16) | Full match |
|---|---|---|
| data/local-service-discovery-protocol-v1.json | `fb533d99d473a338` | vs TASK-LOCK + protocol-predictions recorded SHA: exact |
| data/local-discovery-generalization-sample-v1.json | `295f3a168648bf72` | vs predictions `sample_sha256_verified`: exact |
| data/local-discovery-generalization-v1.json | `b7fb2c6d5c134a77` | vs prior TASK-LOCK recorded SHA: exact |
| data/local-access-verification-v1.json | `f594162c95a6f02f` | recorded in handoff evidence: exact |
| evaluation/local-discovery-generalization-v1/protocol-predictions.json | `ff8b0322552db2c8` | recorded in handoff evidence: exact |

Historical files modified by this task: **0**.

## Runtime Changes (this session)

- `runtime/discovery/engine.py`: generalized markers only (nynorsk "tilvising" variants, "bruk skjema", capacity closure, system-targeted, service-connected email, "ringe" in phone-intake context). No case IDs, no municipality names.
- `runtime/discovery/classification.py`: DIRECT_EMAIL method mapping; capacity/system-targeted -> self_referral NO. Doctrine text unchanged.
- `runtime/discovery/orchestrator.py`: DIRECT_EMAIL counts as strong access evidence.
- `runtime/discovery/schema.py`: NEW stdlib subset validator for the result schema.
- `runtime/discovery/tests.py`: +7 tests (5 marker, 2 schema).
- `data/local-discovery-runtime-result-v1.schema.json`: NEW frozen result contract.

## Provenance Discipline

- Every runtime service row carries source_url, evidence spans, and fetch metadata (method, content hash, retrieved_at).
- Provenance graph records QUERY_SEARCH / KNOWN_URL / NAVIGATION_LINK edges per URL.
- Replay fetches use fixture-captured content hashes; live fetches hash the retrieved body.

## Statement

No frozen protocol, sample, prediction, or historical verification artifact was modified during this task. Runtime-only generalizations were derived from linguistic variants present in historical fixture text, not from case-specific mappings.

