# RC2 Age-Parser Audit

## Root cause (live-reproduced on frozen engine)

`extract_ages` (quote_aligner.py:148) matched digit ranges with an
optional year suffix. Any "N-M" sequence therefore parsed as an age
interval:

- "PRL § 4-3" -> interval [4, 3] (burned RC1B-0122)
- "FOR-2026-06-25-1361" -> [6, 25] (burned RC1B-0131)

`age_relation` then reported "disjoint" against a real age span
("fra 16 år"), and the polarity engine escalated to hard CONTRA. The
reviewer could not override a hard engine CONTRA, so semantic,
proof-safe, and product all failed simultaneously.

## Fix (Iteration A, rc2-development/engine/quote_aligner.py)

1. Range regex requires an explicit year word after the second number
   (negative-lookahead guard), so law citations never parse as ages.
2. Added positive age patterns: "mellom X og Y år", "fra X til Y år",
   "N-åringer".
3. "fra/fylt" patterns skip spans already captured by longer matches.
4. Under/over/fra age patterns reject quantity units (ganger, kr,
   kroner, prosent, %) via negative lookahead.

## Regression evidence

- regressions/run_regression.py: law_age_negative + age_positive
  groups pass (37/37 total).
- Post-fix burned outcomes: 0122 SUPPORTED (correct), 0131
  INSUFFICIENT_EVIDENCE (fail-closed, correct).
- id_guard confirms no case IDs in engine code; the fix is fully
  generalized (law-citation pattern class, not case-specific).

