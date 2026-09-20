# RC3 Generalization Holdout (RC3G-HOLDOUT-V1)

Task: NAV-EXPLORE-RC3-GENERALIZATION-HOLDOUT-CONSTRUCTION
Status: GENERALIZATION_HOLDOUT_SEALED_AND_READY (TASK-LOCK.json is authoritative)

What this is: a fresh, non-tuned, double-annotated 159-case CORE
generalization holdout for the frozen RC3 runtime snapshot
(NAV-EXPLORE-RC3-GEN-SNAPSHOT-A), with a cryptographically sealed answer
key. This construction task never executed the snapshot against the
holdout; scoring happens in a separate future phase under the G1/G2
protocol in future-generalization-protocol.md.

Public artifacts (runner-accessible, label-free):
- generalization-cases.json / generalization-cases.schema.json
- runtime-snapshot/ (frozen, hash-verified)
- proof-soundness-contract-v2.{md,json} (authoritative metric definitions)
- burned-v4-metric-reconciliation.{md,json}
- evaluation-metrics.md (preregistered scoring gates)
- future-generalization-protocol.md

Sealed artifacts (AES-256-GCM, AAD bound to the cases file sha256):
- answer-key.sealed (triple labels, atom keys, adjudication, rationale)
- construction-audit.sealed (both annotation passes, agreement stats,
  selection ledger, novelty results, and the label-bearing construction
  scripts, which were removed from plaintext per spec 48)

Key handling: the AES key was generated with secrets.token_bytes(32),
printed once in the construction session final message, and never
persisted. It is not stored in this repository, in reports, or in
TASK-LOCK.json.

Construction notes: case authoring scripts remain for provenance, but
case_list_*.py and adjudicate_resolve.py (which embed per-case label
codes) exist only inside construction-audit.sealed; author_cases_main.py
will not run without restoring them from the sealed bundle. Annotation
pass 2 was model-assisted with GPT-5.6-Luna (spec 33); 0 of 2 subagent
budget used.
