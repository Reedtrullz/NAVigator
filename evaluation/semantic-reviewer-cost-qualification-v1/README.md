# NAV-EXPLORE-SEMANTIC-REVIEWER-COST-QUALIFICATION-V1

## STATUS: NO_LOW_COST_MODEL_QUALIFIES (terminal, valid experimental outcome)

Owner-authorized screening of low-cost semantic reviewer candidates for the
Measurement V3 human-review lane. Five candidates were tested against a frozen
benchmark and frozen gates. No candidate passed Stage 1 screening; Stage 2/3
were therefore not started (spec section 24 restricts them to survivors).

## What happened

1. Reference corpus frozen: 387 unique canonical inputs from the Wave-4
   lineage (Tier-A 375, Tier-B 12, 25 excluded, 0 conflicts).
2. Transport calibration frozen for 5 candidates; inkling permanently
   excluded (HTTP 403 route restricted to agentic harnesses).
3. One blind screening pass per active candidate (90 rows each: 53 forbidden
   + 37 critical), then a single bounded recovery pass for transient transport
   errors only (timeout/502/429; 402/503 not retried; invalid outputs never
   retried).
4. Frozen-gate scoring (schema_valid_rate_min = 1.0 per lane + catastrophic
   escape limits): all four candidates failed; zero catastrophic escapes
   anywhere.

## Screening outcomes (post-recovery)

| Candidate | OK/90 | Blocking mechanism | Classification |
|---|---|---|---|
| nemotron-3-ultra | 5 | 54x 429 + 30x 402 (credit exhaustion), 0/54 recovered | CHRONIC_429_CREDIT_EXHAUSTION |
| nex-n2.5-pro | 48 | 38 invalid model reviews + 4 residual timeouts; near-miss | EPISODIC_TIMEOUTS |
| gemma-4-31b-it | 16 | 72x chronic 429, 3/75 recovered | CHRONIC_429_CREDIT_EXHAUSTION |
| mimo-v2.5-pro | 32 | 21 unparseable JSON + 35 invalid model reviews; 1 critical under-escalation-direction error among valid rows | NO_TRANSPORT_FAILURES_INVALID_OUTPUT_DOMINANT |
| inkling | 0 | permanent 403 route restriction | TRANSPORT_NOT_VERIFIED_ROUTE_RESTRICTED |

## Key files

- final-report.md - full 56-point report
- screening-results.json + screening-progress-*.jsonl - frozen screening outputs
- screening-recovery-results.json - bounded recovery attempt history
- screening-scored.json - frozen-gate scoring
- disagreement-analysis.json - field-level disagreement families
- quota-operational-analysis.json / cost-analysis.json - viability and observed usage
- qualification-contract.json - frozen gates (never modified after outputs)
- benchmark-freeze-manifest.json - frozen benchmark pins
- candidate-configs.json - frozen wire IDs

## Hard invariants preserved

- No best-of-bad selection (spec section 28): the strongest near-miss
  (nex-n2.5-pro) was NOT advanced.
- Gates and thresholds unchanged after outputs were observed.
- No historical measurements mutated; no gold changed; no SUT changed;
  0 fresh cases consumed; 0 Astra/Sol calls.
- Scorer fixes during scoring (diagnostic-row guard, authoritative-fields-only
  comparison) are harness corrections mandated by the frozen spec/reference
  shape, not threshold or gate changes.

Activation of any reviewer router requires a separate owner-authorized task.
