# RC1 Blind Postmortem (post-RC2 root-cause repair)

Basis: official frozen score (SHA fff9b539...93d72 preserved,
RC1_NOT_CERTIFIED stands permanently) and the phase2 error-analysis.
Root causes were live-reproduced on the frozen RC1 engine and then
fixed in the RC2 development copy (rc2-development/engine/).

## Confirmed root causes (all reproduced, all fixed)

1. **Law-as-age false contradiction** (0122, 0131): range regex
   parsed "4-3" in a law citation as ages [4,3] -> age_disjoint ->
   hard CONTRA. Fix: year-word requirement + unit lookaheads.
2. **Cross-amount numeric conflict** (0005, 0086, and 0003 found
   during RC2): any-pair same-unit bound comparison ignored quantity
   qualifiers (full vs halved) and cross-subject value citations.
   Fix: qualifier-set equality + same-subject attestation skip.
3. **Runtime crash** (0112): set(...).values() AttributeError ->
   conservative default. Fix: iterate the set; robustness cases added.
4. **Fusion over-caution**: 103/120 rows routed to review; reviewer
   SUPPORT at >=0.90 was never auto-accepted (32/32 of those rows
   were label-correct). Fix (Iteration B): frozen asymmetric fusion
   policy (fusion.py).
5. **Compound decomposition**: engine atom granularity differs from
   annotation (36/41 failures); oracle test shows the binding
   constraint is atom-level support recall, not segmentation.

## What RC2 changes

- Deterministic unsoundness (false CONTRA) eliminated on the burned
  set: critical false autos 5 -> 0 in fused shadow; engine semantic
  42 -> 52; no regressions (10 fixed, 0 regressed).
- Auto precision on development: 13/13 fused + 0 deterministic-path
  autos = 100% (target >=99%).
- Overall blind-set score is NOT the target of this task and is not
  claimed; conservative fusion lowers raw agreement numbers while
  making the auto channel provably clean.

## What RC2 does NOT fix

- Atom-level support recall on fine-grained compound claims
  (documented in compound-audit.md; deferred with evidence).
- Label-audit sensitivities 0116/0165 (owner decision required).

