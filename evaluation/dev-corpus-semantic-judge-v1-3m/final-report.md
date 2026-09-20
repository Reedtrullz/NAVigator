# V1.3M Final Report

## 1-2. Authorization and models

1. Task ID: NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_3M-MIMO-MIGRATION
2. Migration authorized by user: YES (explicit)
3. Previous judge model: GPT-5.6-Luna (openai/gpt-5.6-luna)
4. New judge model: mimo-v2.5 (command-code/xiaomi/mimo-v2.5)
5. Provider: commandcode-auth (local proxy, chat completions)

## 6-9. Previous V1.3 lineage facts

6. Previous V1.3 valid semantic labels: 0
7. Previous V1.3 transport failures: 64/64 calls, HTTP 429 usage window
8. Previous V1.3 Set A burned: NO (transport observations only)
9. Set A SHA: 0e1491c68e6907ed2bd022994b3982e98177b57d60e20ae54e84a4b04572703d
10. Set A changed: NO (byte-identical copy verified before run)

## 11-20. Integrity and transport

11. Baseline artifacts verified: 29/29 SHA match (plus 7 source pins)
12. Historical files changed: 0 (old TASK-LOCK got an append-only execution
    note; it is not part of the 29 verified artifacts and no verified byte
    changed)
13. Semantic contract changed: NO
14. Route contract changed: NO
15. Uncertainty contract changed: NO
16. Prompt semantics changed: NO (instructions imported byte-identically)
17. Adapter changed: YES (see 18)
18. Adapter change limited to transport/model binding: YES - model binding,
    max_tokens 120->2000 headroom (mimo exhausted 120 tokens before emitting
    JSON; deterministic reproduction on synthetic input), and a mechanical
    zero-gate guard fix (stray unary + tokens, behavioral no-op). No
    semantic postprocessing.
19. Credentials persisted: NO (runtime-only; not printed, hashed, or stored)
20. Model identity verified: YES (requested == effective == wire model)

## 21-30. Set A run

21. Smoke transport: PASS (single non-evaluation call)
22. Smoke structured output: PASS (fenced JSON parsed by frozen parser)
23. Set A attempted: YES
24. Set A completed: YES (single authoritative dual-blind run; see
    set-a-run.json deviations for the dual-run process incident)
25. Set A transport failures: 2 empty-content responses (BRT-13 pass2,
    BUN-03 pass2), 1 JSON parse failure (BUN-10 pass1); 61/64 valid calls
26. Set A schema failures: 3
27. Set A route agreement (commitment field): 0.8125
28. Set A uncertainty agreement (verdict field): 0.6875
29. Set A overall agreement: 0.0 (frozen full-label gate, including
    free-text note; 24/32 rows agree on all semantic fields and differ only
    in note text)
30. Set A gate result: FAIL

## 31-34. Set B and contract

31. Set B authorized: NO (Set A gate failure blocks it, section 19)
32. Set B completed: NO
33. Set B gate result: NOT_RUN
34. Contract frozen: NO (semantic-judge-contract-v1-3m.json not created;
    per deliverables rule, no downstream artifacts fabricated)

## 35-44. Downstream validation

35. Model calibration: NOT_RUN (blocked by Set A failure)
36. Official fresh fixtures N: NOT_RUN
37. Official accuracy: NOT_RUN
38. Critical FN: NOT_RUN
39. Forbidden safety FN: NOT_RUN
40. Route performance: Set A diagnostics only (commitment 0.8125, verdict
    0.8125)
41. Uncertainty performance: Set A diagnostics only (mode 0.8125, verdict
    0.6875)
42. Stability: NOT_RUN
43. Deterministic overrides: 0 (no deterministic layer was bypassed; the
    fail-closed schema guards rejected 3 invalid outputs mechanically)
44. Judge manifest SHA: see semantic-judge-manifest-v1-3m.json

## 45-49. Prohibitions honored

45. Full SUT run: NO
46. Product holdout: NO
47. Runtime modified: NO
48. GPT-5.5 used: NO
49. Old Luna lineage preserved: YES (supersede status registered as
    V1_3_LUNA_SUPERSEDED_BY_AUTHORIZED_MODEL_MIGRATION with
    successful_semantic_annotations = 0, set_a_semantically_burned = false,
    semantic_evaluation_result = NOT_OBSERVED)

## 50-52. Gates and status

50. Gates passed: baseline integrity (29/29), Set A byte-identity,
    transport smoke, structured-output compatibility, zero-gates (all 0),
    no-contract-change, no-prompt-change, no-threshold-change,
    credential security, Luna supersede registration
51. Gates failed: Set A overall agreement, Set A field-level agreement
    (route verdict 0.8125 < 0.95; uncertainty verdict 0.6875 < 0.95),
    Set A zero-schema-failure target
52. STATUS: DEV_CORPUS_SEMANTIC_JUDGE_V1_3M_NOT_READY

## 53-55. Assessment

53. Is mimo-v2.5 validated as the semantic judge? NO. The model binding is
    transport-valid (auth, structured output, fail-closed guards work), but
    dual-pass primitive stability on the boundary classes is below the gate
    the frozen protocol requires before Set B.
54. Remaining limitations: (a) mimo disagrees with itself most often on
    QUOTED_ONLY/HYPOTHETICAL_ONLY vs HEDGED_POSITIVE_ASSERTION (BRT-10/11),
    on NONE vs EXPLICIT_LIMITATION (BUN-01), and on the
    unresolved-vs-violated edge of NON_ASSERTION (BUN-09) and COMPOUND
    (BUN-13) - exactly the hard boundaries V1.3 exists to clarify; (b) the
    frozen gate counts free-text note differences as full disagreements
    (0.0 overall despite 24/32 semantic-field agreement), which makes the
    gate stricter than its informative content; any future protocol change
    on that point belongs to the V1.3 lineage, not this migration; (c) 3/64
    calls produced empty/unparseable content (transport-level).
55. Recommended next bounded stage: V1.3M is terminal as NOT_READY. If the
    mimo judge direction is still wanted, the correct next task is a
    V1.3M-boundary follow-up that may change the PROMPT/instructions (not
    the semantic contract) to improve primitive stability on the five
    disagreement classes, re-validated on fresh fixtures; alternatively the
    judge-model question returns to model selection with Set A burned.
    No work was started on either path in this task.
