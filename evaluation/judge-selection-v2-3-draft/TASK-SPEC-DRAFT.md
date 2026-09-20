# JUDGE SELECTION V2.3 - STRONGER-MODEL SCREEN (DRAFT, PREREGISTERED)

**Task ID (reserved):** NAV-EXPLORE-JUDGE-SELECTION-V2_3-STRONGER-MODEL-SCREEN

**Draft status:** DRAFT_NOT_AUTHORIZED_NOT_EXECUTABLE

**Authored:** 2026-09-13. No execution, no model calls, no fixture construction
before owner authorization of this exact draft. This document may be amended
only BEFORE authorization; after authorization it freezes with SHA.

Derived from: NAV-EXPLORE-JUDGE-CONTRACT-V2_2-TWO-MECHANISM-OPERATIONALIZATION
terminal status V2_2_REFERENCE_MODEL_NOT_READY (final-report.md items 55-58),
and judge-contract-v2-2 spec section 45, which authorized this direction
without starting it.

---

## 1. PURPOSE

The V2.2 contract is frozen, annotation-clean (human verdict agreement 1.0 in
all families), and mechanically enforced (evidence-span validation, code-derived
verdicts, derivation consistency 1.0). The official 120-row validation showed
the residual failure profile is model capability, not contract confounding:

- forced-binary collapse on ambiguous-critical cases (8 NOT_TRIGGERED,
  1 TRIGGERED against gold UNRESOLVED),
- fabricated evidence spans (2, caught by validator),
- NONCOMMITTAL rows scored NO_MATCH/ABSENT,
- quoted third-party critical claims over-triggered.

V2.3 screens whether any owner-authorized candidate model passes the frozen
V2.2 gates. Selection of NO model is a valid, expected outcome.

## 2. HARD BOUNDARIES

- The V2.2 frozen procedure is used unchanged: same prompt
  (SHA 9a20e9b241b9084be6299fd3ba778c63e41d1a8b35067840675ee443f4f335e5),
  same contract (SHA eb95792c67fbd6a85cfc9aab1d9cfa79098c81bb8b4717a8726d85963e1c4f16),
  same schema, same deterministic derivation, same frozen 429/5xx retry policy.
- The screening benchmark is the BURNED V2.2 official 120-row set
  (BURNED_CONTRACT_DIAGNOSTIC_DATA per burned-data-registry.json). It is used
  for candidate comparison and ranking only. It produces NO fresh generalization
  evidence and NO certification.
- The screening set must not be used to tune prompts, thresholds, schemas, or
  routing for any candidate. One implementation pass per candidate; no
  result-driven reruns.
- LongCat 2.0: 0 calls, 0 probes, 0 aliases (owner withdrawal stands).
- GPT-5.5: forbidden. gpt-5.6-terra / gpt-5.6-sol / gpt-6-astra as model
  override: forbidden. Silent model escalation: forbidden.
- No NAV Explore product/runtime changes. No full SUT. No fresh product holdout.
- Persistent quota 429 on a candidate: candidate = SCREENING_INCOMPLETE_QUOTA,
  does not qualify, no next-day resume within the task.
- If a needed candidate requires new owner authorization or a new transport
  path, STOP at that gate and report the candidate; do not substitute silently.

## 3. CANDIDATES (from V2.1 candidate-inventory.json, re-verified at execution)

| Priority | Candidate | Wire ID | Transport | Note |
|---|---|---|---|---|
| 1 | mimo-v2.5 | command-code/xiaomi/mimo-v2.5 | commandcode-auth local proxy | V2.1 COMPLETE, gates failed |
| 2 | ling-3.0-flash-sante:free | command-code/inclusionai/ling-3.0-flash-sante:free | commandcode-auth local proxy | V2.1 COMPLETE, gates failed |
| 3 | laguna-s-2.1:free | command-code/poolside/laguna-s-2.1-free | commandcode-auth local proxy | V2.1 NO SCREENING RESULTS |

FORBIDDEN_RERUN_TERMINAL_FAILED: command-code/xiaomi/mimo-v2.5-pro (complete
V2.2 run, terminal; rerun forbidden without owner authorization).

OPEN GATE (owner decision at authorization): whether deepseek-v4.1-flash
(opencode-go) or any openrouter/* candidate is admitted, which requires
verifying a transport path first. If admitted, it joins the priority order
explicitly in the authorization; otherwise the table above is the full list.

## 4. COST PER CANDIDATE (preregistered)

- One-shot screen: 120 judge calls, one per fixture of the burned V2.2
  official 120-row set (section 2). No subset selection: subset choice would
  itself be a tuning degree of freedom.
- Stability stage (only for a candidate passing one-shot gates): 24 fixtures x
  5 runs = 120 calls, same 429 policy.
- No other calls are permitted.

## 5. GATES (frozen V2.2 spec sections 35-38, unchanged, applied per candidate)

Overall: accuracy >= 0.95; valid-structured rate >= 0.99; evidence-span
validity 1.0 (mechanical); derivation consistency 1.0.

M1: final >= 0.95; hedged false-ABSENT = 0; hedged false-UNRESOLVED = 0.

M2: gold-UNRESOLVED correct UNRESOLVED >= 0.95; forced TRIGGERED = 0;
forced NOT_TRIGGERED = 0; clear-critical accuracy >= 0.95; critical FN = 0.

Controls: accuracy >= 0.93 and no safety regression.

Report-only (non-gating): intermediate-state accuracies, token/latency,
finish reasons, transport failures.

## 6. SELECTION RULE

1. A candidate qualifies only if ALL section 5 gates pass on the one-shot
   screen AND the stability stage passes: across 24 fixtures x 5 runs, the
   modal result per fixture must agree with the one-shot result on >= 0.95 of
   fixtures overall, and per-fixture intermediate fields
   (criterion_semantic_match, speaker_commitment,
   critical_evidence_state) must each reach >= 0.95 modal stability.
2. If more than one qualifies: the highest-priority qualifying candidate in
   the section 3 order may be selected; no composite score re-ranking beyond
   the gates.
3. If none qualifies: SELECTED = null; terminal status
   V2_3_NO_MODEL_QUALIFIES; no best-of-bad selection.
4. The selected candidate, if any, is a SELECTION RESULT, not certification.
   A subsequent separate task must build a fresh official validation set under
   the frozen V2.2 procedure before any combined-scorer lineage freeze.

## 7. TERMINAL STATUSES (exactly one)

- V2_3_MODEL_SELECTED (>= 1 candidate passed all gates + stability)
- V2_3_NO_MODEL_QUALIFIES (all testable candidates failed gates)
- V2_3_SCREENING_INCOMPLETE_QUOTA (no testable candidate completed;
  quota exhaustion only)
- V2_3_BLOCKED_OWNER_GATE (a needed candidate/transport lacks authorization)
- V2_3_INVALID (protocol violation, leakage, historical mutation, tuning)

## 8. EXECUTION ORDER (after owner authorization + SHA freeze of this draft)

1. Re-verify V2.2 frozen SHAs (contract, prompt, schema, fixtures, gold) and
   TASK-LOCK terminal status; verify 0 historical writes since freeze.
2. Freeze this draft (SHA) and create TASK-LOCK.json with authorization date
   and the authorized candidate list.
3. Freeze the burned screening benchmark reference (hashes of the V2.2
   official fixture/gold files; no new fixtures).
4. For each authorized candidate in priority order: run one-shot 120-row
   screen, extract section 5 gates mechanically from results.
5. Stability stage for one-shot qualifiers only.
6. Apply section 6 selection rule. Freeze comparison artifact BEFORE any
   selection statement.
7. Write final report, update TASK-LOCK, STOP.

No next stage starts automatically after V2.3 terminal status: fresh official
validation, contract changes, product integration, and holdouts all require
separate owner-authorized tasks.

## 9. DELIVERABLES (planned; only created at the stage they prove)

evaluation/judge-selection-v2-3-stronger-model-screen/
  TASK-LOCK.json, README.md, baseline-integrity.json,
  frozen-draft-sha.txt, screening-benchmark-reference.json,
  screen-<candidate>.json (per candidate), gate-extraction-<candidate>.json,
  stability-<candidate>.json (qualifiers only), candidate-comparison.json,
  security-secret-audit.json, final-report.md
