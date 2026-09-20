# Hybrid semantic judge (task SEMANTIC-JUDGE-HYBRID-EVIDENCE-REVIEW)

Architecture: deterministic quote-aligner v0.2 verdicts first, hard
auto-gates route unsafe/uncertain cases to an LLM semantic reviewer
(gpt-5.6-luna via local OpenCodex proxy), deterministic fidelity
checks + fusion decide the final verdict. Frozen roots v0.1-v0.4.1
and quote-aligner v0.1/v0.2 are read-only.

## Files

    TASK-LOCK.json          active task lock + constraints
    auto_gate.py            deterministic routing gates (v1.0, frozen)
    reviewer.py             packet builder, LLM call, fidelity, fusion
    run_hybrid_eval.py      full 389-claim harness -> results/hybrid-eval.json
    check_injections.py     prompt-injection battery (--live for real calls)
    stability_check.py      30 difficult claims x 3 runs (spec 28/30)
    reviewer-spec.md        reviewer config, FROZEN v1.1 (iteration B)
    fusion-spec.md          fusion rules, FROZEN
    architecture.md         architecture, FROZEN
    operating-thresholds.md class-based thresholds, FROZEN
    development-set.json    45 review-error cases, DEVELOPMENT_ONLY
    results/                auto-coverage, gated-coverage, hybrid-eval,
                            hybrid-eval-iterationA, stability, risk-coverage.md
    cost-model.md           cost accounting per 100 claims
    final-report.md         56-point report per spec SLUTTRAPPORT

## Reproduce

    python3 reviewer.py                       # offline self-check
    python3 check_injections.py --live        # 10/10 required
    python3 run_hybrid_eval.py                # full run, ~16 min, 268 calls
    python3 stability_check.py                # 90 calls, ~7 min

## Headline (iteration B)

Auto layer 121/389 at 100%/100% precision; hybrid selective accuracy
87.6% on 93.1% coverage; 0 unsupported-to-SUPPORTED FP; 0 safety,
numeric, or temporal FP; ENT-C/D PASS; novel-40 77.1% vs 90% gate ->
NOT_READY_FOR_HYBRID_BLIND_RECERTIFICATION (spec 43 stop rule).
Details in final-report.md.
