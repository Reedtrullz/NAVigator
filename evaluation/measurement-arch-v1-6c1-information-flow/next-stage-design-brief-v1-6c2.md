# Next-stage design brief after V1.6C.1 (DIAGNOSTIC - NOT AUTHORIZED, NOT A STAGE START)

Status basis: A3 frozen (21047fda...f2563b) and abstains on 13/14 A/B
failure rows (see ab-failure-rows-a3-replay.json). V1.6A.4 deterministic
assertion-strength expansion is TERMINAL at V1_6A4_NOT_READY (fresh
non-ABSTAIN precision 0.368 vs >= 0.99 gate;
V1_6A4_LAST_PREAUTHORIZED_DETERMINISTIC_EXPANSION = true). V1.6B remains
V1_6B_NO_JUDGE_QUALIFIES. V1.6C.1 packet repair measured NOT_SUPPORTED.

## What the combined evidence now proves

1. More deterministic boundary rules are the wrong tool: the A4 attempt
   falsified the precision hypothesis, and further expansion is banned
   without new explicit authorization.
2. More information injection is the wrong tool for non-route dimensions:
   C1 measured the packet at -1.09 pp overall with uncertainty regression
   (M4). Only route_candidates showed positive signal (route +5.6 pp).
3. The boundary already abstains on almost all residual failures; the
   failures are judge-capacity failures, quantified as M1 (critical
   abstention recall: both arms 0-1 of 4 gold-UNRESOLVED critical rows),
   M2 (compound uncertainty PARTIAL semantics), M3 (forbidden paraphrase
   equivalence: 4/4 rows failed by both arms).
4. Abstention precision is high in both arms - the judge does not need
   permission to abstain, it needs the CAPACITY to recognize ambiguity.

## Recommended next bounded stage (pending user authorization)

Judge selection V2, targeted at the M1/M2/M3 sub-skills, exactly as the
V1.6B architecture review anticipated (stage 2), with C1 refinements:

- Fresh fixture families, frozen before any model call: critical
  UNRESOLVED-disposition (incl. hedged near-miss controls protecting
  precision), compound uncertainty PARTIAL, forbidden paraphrase
  equivalence (incl. non-equivalent controls). No text reuse from burned
  sets, V1.2 official, or C1 A/B rows.
- Dual-pass human labeling with agreement gates before any model call
  (V1.3/V1.6 precedent); disputed fixtures before gold freeze are
  DISCARDED and replaced, never repaired.
- One-shot screening of candidate models from the AGENTS.md allowed list
  with the frozen V1.6B gate architecture: hard safety gates unchanged
  (critical FN = 0, safety-critical forbidden FN = 0), sub-skill
  accuracy gates per family, no threshold changes, no best-of-bad.
- Burned data (the 14 rows, C1 A/B, V1.6B taxonomy) may motivate family
  design but never serves as validation or pass evidence.
- The packet is NOT reintroduced for non-route dimensions; route-candidate
  exposure may be tested later as a separate frozen variant on route
  families only.
- No C2 calibration-weighted screening and no combined scorer freeze
  until a judge qualifies.

Explicit non-goals: no boundary expansion (A4 ban), no lexical fallback,
no full SUT, no product runtime changes, no fresh product holdout.
