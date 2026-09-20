# V2.11 Final Report - NAV-EXPLORE-JUDGE-SELECTION-V2_11-FRESH-CANDIDATE-SCREENING

Terminal status: V2_11_NO_NON_M2_JUDGE_QUALIFIES

## Execution summary

1. Integrity gate: all pinned SHAs verified drift-free (draft spec b04e9621...df23; V2.10 lineage pins intact; disk 66 GiB free).
2. Smoke: both candidates PASS (HTTP 200, schema valid, evidence-span transport PASS).
3. Prompt-sensitivity probe: 6 rows x 2 prompts per candidate; both PROMPT_INERT = false (outputs respond to prompt changes), so both proceeded to calibration iterations per frozen protocol.
4. Calibration iteration 1 (25 fixtures, 12 traps):
   - ling: accuracy 0.80, trap overcommit 0 (forbidden 5/7, route 8/10, uncertainty 7/8)
   - laguna: accuracy 0.60, trap overcommit 1 (forbidden 6/7, route 5/10, uncertainty 4/8)
5. Calibration iteration 2 (same 25 fixtures, 12 traps; preregistered reordered prompt):
   - ling: accuracy 0.84, trap overcommit 0 (forbidden 6/7, route 10/10, uncertainty 5/8)
   - laguna: accuracy 0.80, trap overcommit 0 (forbidden 6/7, route 8/10, uncertainty 6/8)
6. Qualification gate (frozen): iter-1 shortcut >= 0.90 + 0 overcommit; iter-2 strict improvement AND >= 0.90 AND 0 overcommit. Neither candidate met >= 0.90. Both CALIBRATION_OUT.
7. Screening (180 rows) and stability: not run - no calibration qualifiers existed, so downstream stages are unreachable under the frozen protocol.
8. freeze: comparison-freeze-v2-11.json written; TASK-LOCK status set to V2_11_NO_NON_M2_JUDGE_QUALIFIES.

## Deviations

- TDD_SEQUENCE_DEVIATION = FALSE. No semantic patch was needed. The 3-line probe/gates harness fix was completed before any official candidate result was observed.
- No process duplication; single runner instance per stage, checkpointed rows.

## Transport notes

- Both command-code free-tier candidates exhibited long latencies and intermittent rate-limit backoffs during calibration but completed all 50 calibration calls with recorded verdicts. No persistent quota failure; no candidate marked TRANSPORT_INCOMPLETE.

## Branch decision

Per the owner's 2026-09-14 AFK MEASUREMENT-SYSTEM CAMPAIGN: Branch B (no qualifier) routes directly to Stage 2C - NAV-EXPLORE-MEASUREMENT-V2_12-UNCERTAINTY-HUMAN-REVIEW-LANE (pre-authorized).

## Observations for future R&D (non-gating)

- ling route dimension improved to 10/10 in iter-2 but uncertainty dropped to 5/8; no candidate is close to the 0.90 combined bar. Uncertainty remains the dominant failure dimension, consistent with V2.10. This supports the campaign's responsibility-decomposition direction (uncertainty to human review).
