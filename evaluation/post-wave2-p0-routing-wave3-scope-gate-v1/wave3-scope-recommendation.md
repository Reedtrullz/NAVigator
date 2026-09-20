# Wave-3 Scope Recommendation (for owner authorization)

## Recommended scope
WAVE3_ROUTE_SEMANTICS_FIRST

## Primary repair
W3-RC-A: Structured route-proposition construction with evidence binding (see wave3-repair-candidates.json). Expected reach: all 108 evaluated route criteria; removes the R0 bottleneck (89) and R1 fragment stage (19).

## Secondary (only after primary lands and re-baselines)
W3-RC-B: Renderer source-block deduplication (UX + contamination-surface reduction).

## Explicitly NOT in Wave 3
- No safety policy repair: zero REAL_PRODUCT_SAFETY_REGRESSION (0/8 P0 are product safety regressions; all are scorer sensitivity).
- No Measurement V3 changes (M-SENS-1/2/3 documented, separate authorization).
- No uncertainty-depth work (RC-04 stays open, sequenced after routes).
- No fresh holdout consumption.

## Safety blocker before Wave 3?
No. Decision rule applied: 0 real product safety regressions -> do not reopen safety policy.

## Gates proposed for Wave-3 acceptance (product-side, dev-only)
- Route-proposition schema validity 100 percent on 120 cases
- Structured route present in cases where prose asserts a route (mechanical divergence check)
- No junk labels (headings/URLs/negations) in routes[]
- Tier-1 + safety canaries + operator + quote-aligner regressions PASS
- Then a fresh one-shot measurement freeze under the CURRENT frozen scorer (noting M-SENS-1 will still grade absent-structured-route cases)
