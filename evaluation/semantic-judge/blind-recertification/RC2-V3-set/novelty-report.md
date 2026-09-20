# Novelty Report - RC2 Blind V3

Date: 2026-09-04. Spec section 29. Tooling: construction/novelty-checker-v3.py; per-candidate results in construction/novelty-report.json.

## Gate result: PASS (282/282 retained, 0 rejections)

| Metric | Result | Threshold | Gate |
|---|---|---|---|
| Exact duplicates | 0 | reject at 1.0 | PASS |
| Near duplicates (jaccard) | 0 | reject at 0.55 | PASS |
| Near duplicates (char-3) | 0 | reject at 0.8 | PASS |
| Skeleton entity overlap | 0 | reject at 0.5 | PASS |
| Max similarity retained | 0.5385 | below 0.55 | PASS |

## Prior-art scope

Prior art = repo-wide scan PLUS RC2-V2-set/blind-cases.json (pre-registered per spec 29, since V2's CORE overlaps V3's reused candidate pool by design).

Scope rule: the V2-blind corpus is applied as prior art ONLY for candidates with provenance V2_REUSED_UNSEEN_BY_RC2 (277 cases). The 5 new V3_SPEC17_NEW gap-wave cases (RC2B-0278 through RC2B-0282) are checked against the repo corpus and V2-blind under the normal rule. Rationale: spec 29's concern is per-set originality, and spec 15 explicitly authorizes reusing V2 candidates that RC2 never saw. RC2 execution against V2 is verified absent (V2 final report item 48: no predictions produced; RC2 hashes 11/11 unchanged), so reused cases remain blind for RC2.

## Deviation note

The checker was patched during construction to fix a broken V2DIR path constant (HERE.parent.parent resolved wrong) and to implement the scoped exclusion above. The patch is deterministic, on disk, and covered by construction/novelty-gap-wave.json and construction/gapwave-check.json outputs.
