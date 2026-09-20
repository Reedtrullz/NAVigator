# V2.4 Remaining-Candidate Judge Screening - TASK SPEC DRAFT

Status: DIAGNOSTIC_DRAFT / NOT_OWNER_AUTHORIZED / NOT_A_STAGE_START

This draft is prepared for explicit owner review. It does NOT authorize execution. No TASK-LOCK is created by this draft. No model calls, fixture authoring, or runtime changes are performed as part of drafting.

## 1. Prior State (SHA-verified 2026-09-13)

| Anchor | SHA-256 |
|---|---|
| V2.3 final-report.md (terminal V2_3_NO_MODEL_QUALIFIES) | b3b855e22027dbd1116742534a9b8306ca537051023c7270c77f5087aff19a20 |
| V2.3 transport-verification.json (deepseek VERIFIED, proxy 127.0.0.1:10100) | 5717d094b8242fda083142bc223f37466c2d3eb5df26108bb6d0e8bd15becf76 |
| V2.2 judge-contract-v2-2-manifest.json (frozen scoring + 120-row burned benchmark) | 5275a9e1891379c06ed13e0736d68e54dc4599a631dbdc3834b901ea05dba832 |
| A3 preclassifier-manifest-v1-6a3.json (boundary layer READY) | 0fedd38b5aa680a891dd9e16307e5de200cd3e06464789b8393580d4d71bcd00 |
| V1.6B TASK-LOCK.json (V1_6B_NO_JUDGE_QUALIFIES) | 95fa5ac79f8a991b6d4d962749b4012f8bb64f06d81e4f0c691f54b10f049fdf |
| V1.6C.1 TASK-LOCK.json (packet repair NOT_SUPPORTED) | a6e61924c1ce737f412bd28dd4c7b424c2be8220076aee0ee9968ef08279e6c7 |

## 2. Why a V2.4 Draft

Every sanctioned measurement lever is terminal:

- Boundary: A3 frozen and proven (1.0 fresh precision, 120 fixtures); A4 falsified further deterministic expansion (fresh precision 0.368 vs 0.99 gate); deterministic boundary expansion is banned without new authorization.
- Information flow: C1 packet repair measured NOT_SUPPORTED (-1.09 pp overall, uncertainty -7.14 pp); not reintroduced.
- Judge selection: V1.6B (2 candidates) and V2.3 (4 candidates, including the strongest structural performer deepseek-v4.1-flash at 6/14 gate failures) both ended with zero qualifiers. Dominant shared failure: forced-binary collapse on gold-UNRESOLVED evidence, plus M1 accuracy below gate.

The only remaining owner-authorized lever within the current measurement architecture is screening the remaining models on the AGENTS.md allowed list that have never been tested against the frozen V2.2 benchmark. This draft freezes that screening before any execution.

V2.3 evidence base (failure-taxonomy-report.md, SHA bbe7a31f6a74bbe05697b361cf10cef06956f6744696fd3db2c8a77d8d5f4e2c) is diagnostic input only: it motivates candidate breadth, it is not a target and confers no pass advantage.

## 3. Candidate Set (frozen at authorization, no expansion afterward)

Exactly the AGENTS.md allowed-list models not yet screened in V1.6B/V2.3 (deduped; LongCat excluded, already permanently banned in V2.3):

| # | Wire ID | Fallback chain (only if primary wire fails transport) |
|---|---|---|
| 1 | opencode-free/big-pickle | - |
| 2 | openrouter/dots-studio-dots-3-note-preview:free | - |
| 3 | openrouter/google-gemma-4-31b-it:free | - |
| 4 | openrouter/inclusionai-ling-3.0-flash-vl:free | opencode-free/ling-3.0-flash-fin-free |
| 5 | openrouter/liquid-lfm-2.5-2.6b:free | - |
| 6 | openrouter/nex-agi-nex-n2.5-mini:free | - |
| 7 | openrouter/nex-agi-nex-n2.5-pro:free | - |
| 8 | openrouter/poolside-laguna-xs-2.1:free | - |
| 9 | openrouter/thinkingmachines-inkling:free | - |
| 10 | openrouter/google-gemma-4-26b-a4b-it:free | - |
| 11 | opencode-go/deepseek-v4.1-flash | opencode-free/deepseek-v4-flash-free |
| 12 | opencode-free/mimo-v2.5-free | opencode-go/mimo-v2.5 |

Notes:
- Wire IDs 11/12 are the free/GO fallback wires of already-screened models. They are included because routing-tier changes can change behavior; their parent-tier results are burned context, not pass evidence.
- OPENROUTER_NEW_CANDIDATES_ALLOWED = false: the OpenRouter wire IDs above are the owner-authorized AGENTS.md list, frozen verbatim. Any other OpenRouter model requires a separate amendment.
- GPT-5.5 not used. GPT-5.6-Luna: excluded from this draft because its quota is empty per owner statement; if the owner reopens it, that is an owner amendment, not a default.

## 4. Preregistered Transport Verification

- Only wire IDs 1-12 require transport verification; command-code proxies for previously screened models are already verified in V2.3 transport-verification.json.
- Transport verification = at most 2 bounded non-benchmark probes per candidate through the existing local proxy (127.0.0.1:10100) or the documented OpenRouter/auth path, using the frozen V2.2 request shape.
- No provider repair, no account creation, no auth debugging, no key management. A candidate that fails transport is marked TRANSPORT_NOT_VERIFIED and skipped; screening continues with the remainder.
- If fewer than 1 candidate is transport-verified: terminal V2_4_TRANSPORT_BLOCKED, report and stop.

## 5. Frozen Procedure (inherited verbatim)

The authoritative procedure is the frozen V2.3 spec (evaluation/judge-selection-v2-3-draft/TASK-SPEC-DRAFT.md, frozen SHA 8b0be315... prefix recorded in judge-selection-v2-3-stronger-model-screen/frozen-draft-sha.txt), applied unchanged: same burned V2.2 120-row benchmark, same frozen scoring (run_official_v2_2.py semantics), same one-shot policy, same 429/5xx single-retry transport policy, same 14 gates, same stability-stage eligibility (all one-shot gates), same selection rule and tie-break, same no-best-of-bad rule. This draft does not restate or modify any threshold.

Execution order: Section 3 table order (1-12), one candidate fully scored before the next. No result-driven reordering.

Quota/429 mechanical policy (preregistered, no discretion): free-tier candidates may exhaust quota mid-run. Affected rows are invalid under the frozen transport policy and the candidate fails eligibility mechanically; execution continues to the next candidate in frozen order. If all remaining candidates are quota-dead before completing the order: terminal V2_4_SCREENING_INCOMPLETE_QUOTA with the comparison frozen over completed candidates only. No substitution, no next-day resume in this task; a resume is a separate owner-authorized task.

## 6. Terminal Statuses (exactly one)

- V2_4_MODEL_SELECTED - at least one candidate passes all gates; frozen tie-break picks the winner; SELECTED_FOR_FRESH_VALIDATION only (not certified, not production-ready).
- V2_4_NO_MODEL_QUALIFIES - zero qualifiers; no best-of-bad selection.
- V2_4_TRANSPORT_BLOCKED - no candidate transport-verified.
- V2_4_SCREENING_INCOMPLETE_QUOTA - remaining candidates quota-dead; comparison frozen over completed candidates.
- V2_4_INVALID - protocol violation, contamination, or historical mutation detected.

## 7. Hard Constraints

- Candidate set frozen at authorization; no additions after execution start, regardless of scores, transport failures, zero qualifiers, or interesting failure patterns.
- LongCat 2.0: 0 calls, 0 probes, 0 aliases. GPT-5.5: not used.
- Burned V2.2 benchmark used for screening only; no fixture reuse for anything fresh; no tuning of prompts, thresholds, or scoring; no contract changes.
- Historical lineages and terminal statuses (V2_2_REFERENCE_MODEL_NOT_READY, V2_3_NO_MODEL_QUALIFIES, V1_6B, A3, A4, C1) immutable; historical writes 0.
- No fresh validation, no product integration, no full SUT, no product holdout after terminal status, without a new explicit owner-authorized task.
- Determinism and stability stages run only for all-gate passers; no majority-vote repair.

## 8. What This Draft Does Not Claim

- No model has been called. No fixture has been authored. Nothing in this draft is evidence about any Section 3 candidate.
- The Section 2 motivation is diagnosis from burned data; it predicts nothing about candidate performance.
- A V2_4_MODEL_SELECTED outcome means only SELECTED_FOR_FRESH_VALIDATION on a new owner-authorized fresh official set.
