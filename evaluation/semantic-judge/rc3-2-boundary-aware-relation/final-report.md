# RC3.2 Final Report

Task: NAV-EXPLORE-RC3_2-BOUNDARY-AWARE-RELATION-RECOVERY
Status: COMPLETED (implementation budget exhausted per spec sections 28/31)
Readiness: BOUNDARY_AWARE_RELATION_NOT_READY
Subagents: 0 (policy: GPT-5.6-Luna default, GPT-5.5 forbidden; none used)

## 1. Task ID

NAV-EXPLORE-RC3_2-BOUNDARY-AWARE-RELATION-RECOVERY

## 2. Prior status

RELATION_REPAIR_NOT_READY (RC3.1 relation-class repair ended with
atom relation accuracy 0.6596 on its 157-case suite and did not meet
proof-readiness gates; the sealed 60-case validation remained closed).

## 3. Authoritative engine SHAs

- Engine entering this task: 4bd2845fac3535fb... (RESTORED_PRE_PASS,
  per TASK-LOCK / source-integrity-report.md lineage).
- Engine after task: 16d4fdbf34afe1ca460c6ea2c43b2937dc1cc4c7ace21c4da6324520a28b2f20
- boundary.py after task: 9200aa9033bb25eaa63dcb23552f814b0e079accff86b97c48c3ef026343fc1e

## 4-5. Prior failed pass / historical artifacts

The failed prior pass was excluded (restored pre-pass engine verified
before implementation). Historical artifacts unchanged, with one
documented exception: rc3-1-support-boundary/baseline-results.json was
accidentally overwritten during verification (default output path) and
was restored as an explicit HEADLINE_ONLY reconstruction; see
regression-report.md. No manifest-listed artifact was affected.

## 6-7. Validation seal

Sealed validation SHA unchanged before/after:
15b13bb7006eff02bc50ef914a2b00593912829c6740d44548248cb0c1e50159.
The sealed file was NEVER opened or executed.

## 8-10. Compile / import / control-char gates

py_compile OK (engine.py, boundary.py); import smoke test OK;
control-char scan clean on both edited modules.

## 11-13. Frozen contract SHAs

- dimension-evidence-contract-v1.md: e7955e3da88fc6c83907903bd20514cd3e6022473716a602df73dee490dc44b5
- dimension-evidence-schema-v1.json: 574e01c95a85073cb81f3e9f17b43951e114e6bde875857d55746439786db920
- relation-recovery-metrics-v1.json: 5c95164301a82583468956f9a66870e74f9c3eae62ac383d5e80151e22724e63
- modality-lattice-v2.json (corrected to contract section 6 before implementation): ad981488d722b0c99933088560fdd121cbf65f4012a39d9a5dada620ea8bf01c
- fresh-architecture-cases.json (152 cases): 81b25913c74e8ee8079cf0f109b8f516b538e7b5b9c63873a0252580b37fc129

## 14. Core architectural hypothesis

The relation layer was classifying from the collapsed 3-state gate,
losing direction and boundedness information. A rich per-dimension
evidence layer (frozen contract) consumed BEFORE the gate projection
lets the relation layer distinguish positive propositional conflict
from exception-bounded, condition-gapped, scope-capped, and
direction-unknown situations, without weakening the frozen gate.

## 15. Baseline information-collapse rate

0.0978 (92 relation errors, 9 collapsed groups; 152-case frozen suite).

## 16. Fresh architecture N

152 cases, 179 atom decisions. Group distribution: modality 30,
condition 22, exception 15, actor 20, negation 20, temporal/numeric 17,
compound 27, critical 30. Relation distribution: ENTAILS 73, RBI 44,
CONTRADICTS 23, PARTIAL 11, AMBIGUOUS 1.

## 17. Relation class distribution

See fresh-architecture-cases.json and architecture-results.json.

## 18-20. Annotation agreement

Single-author annotation; sampled self-consistency proxy 100% relation,
95% dimension (20-case sample), marked DEVELOPMENT_SANITY_ONLY. Formal
independent double-annotation was not available and is not claimed.

## QA gates

py_compile, import smoke, control-char scan, schema enum validation,
gate-equivalence differential (0/677, 0 projection), fresh suite,
confusion matrices, boundary regression, unsound-proof audit,
decomposition 44/44, legacy battery (RC2 37/37, tier1 gate clean,
operators 43/43, operator 23/23, RC3 dev 24/24, evaluator 1.00, KB
48/48, engine probes pass), id_guard 0, determinism byte-identical,
seal SHA unchanged. Full detail: regression-report.md,
proof-safety-audit.json.

## Results (152-case frozen suite, post-implementation)

- Baseline: accuracy 0.486, macro-F1 0.4846, critical false-ENTAILS 3,
  critical false-CONTRADICTS 5.
- After implementation pass: accuracy 0.514, macro-F1 0.5002, critE 5,
  critC 0.
- After the one bounded bugfix pass: accuracy 0.514, macro-F1 0.4693,
  ENTAILS precision 0.8033, CONTRADICTS precision 0.5833, critE 5,
  critC 0, collapse rate 0.1034. Burned-train atom relation accuracy
  0.3494 -> 0.3313.

## Honest interpretation

The pass delivered the designed structural separation and real fixes
(exception-bounded conflicts no longer auto-contradict; direction-
unknown modality no longer reads as deontic opposition; gold-ENTAILS
rows under licensing modality now classify correctly, e.g. BA-008),
and all safety gates held (false auto 0, unsound 0, critC 0). But the
primary relation gate moved only 0.486 -> 0.514 against a 0.95 target,
and the bugfix pass traded CONTRADICTS precision gains for macro-F1
loss. The residual error mass is concentrated in 3-state gate collapse
cases (rich evidence honest, gate UNKNOWN) and R23/R25 numeric-
coverage soundness gaps (BA-077/087/095), which require gate-level or
soundness-rule work that this task does not authorize.

## Readiness (spec sections 43-44)

- Relation >= 0.95: FAIL (0.514).
- ENTAILS precision >= 0.99: FAIL (0.8033).
- CONTRADICTS precision >= 0.99: FAIL (0.5833).
- Dimension gates: pass (annotation proxy DEVELOPMENT_SANITY_ONLY).
- Boundary safety gates: PASS (0 false auto, precision 1.0, recall
  0.973, unsound 0).
- Proof safety (unsound eligible = 0): PASS.
- Decomposition: PASS. Determinism: PASS. Legacy: no safety regressions.

Status: BOUNDARY_AWARE_RELATION_NOT_READY (main relation gates fail).
No candidate freeze (section 45 applies only to PROOF_READY). The
sealed 60-case validation remains sealed for a later task.

## Next-step recommendation

The dominant residual class is 3-state gate collapse: the rich layer
now classifies honestly but the frozen gate cannot consume it. The next
task should be a bounded gate-consumption design (RC3.3) that defines,
before implementation, which rich states may resolve UNKNOWN gate
dimensions for eligibility without weakening the false-auto history,
plus a numeric-coverage soundness repair (R23/R25) for BA-077/087/095
classes. No tuning against the sealed validation.
