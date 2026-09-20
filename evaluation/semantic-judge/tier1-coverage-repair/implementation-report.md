# Implementation report

Task: SEMANTIC-JUDGE-TIER1-COVERAGE-REPAIR. Exactly one implementation
pass, executed after the audit and after these fixes were designed.
No git repository exists in this workspace; diff sizes are measured as
line deltas against the pre-pass frozen v0.4.1 runtime files.

## Files changed (runtime)

### evaluation/semantic-judge/quote-aligner/v0.2/polarity_engine_v02.py

- _concept_polarity: longest-match-first across negative+positive forms
  (fixes "ingen kostnad" misread) - ~6 lines reworked.
- _UNIT regex: appended "|g)\b" (word boundary; "6 ganger" no longer
  lexes as G) and _UNITS["g"] = "g" - 2 lines.
- _FRAMING_RE: added "|inntekt|grense" - 1 line.

### evaluation/semantic-judge/quote-aligner/v0.2/domain-lexicon.json

- requires_referral.negative_forms += "ingen henvisning" (generic: true)
  - 1 line.

### evaluation/semantic-judge/tier1-proof/tier1_operators.py

- _DUMMY_RE regex constant (dummy subjects "det er/den er/finnes/var/
  blir").
- _EXCL_RE, _DIR_RE regex constants.
- _exclusion_flag() and _conflicting_pair() shared helpers (~30 lines
  added); numeric_conflict refactored to use them plus the all-bounds
  eligibility pre-pass and the dummy-subject relaxation.
- direct_assertion: generic no-actor fragment propagation from an
  adjacent bound sentence; _sentence_has_own_actor() helper.
- Net: ~60 lines added, ~15 reworked.

### evaluation/semantic-judge/tier1-proof/proof_validator.py

- DIRECT_ASSERTION premise-count aligned to spec grammar (1-2); per-
  premise derived_fact span checks retained.
- Fragment chain check mirrors the operator rule (chain from any
  preceding bound sentence).
- NUMERIC_CONFLICT re-derivation now calls ops._conflicting_pair so
  operator and validator cannot drift - net ~10 lines.

## Files changed (test corpora only)

### evaluation/semantic-judge/tier1-proof/test_tier1_operators.py

- +10 checks: G-unit conflict positive, "ganger" word-boundary negative,
  mixed-conjunct abstain, dummy-subject positive, LMF x3, fragment
  propagation positive, own-actor fragment negative, "ingen henvisning"
  form. 43/43 PASS.

### evaluation/semantic-judge/operator-regression/cases.json

- +7 permanent regression cases (23 total, 23/23 PASS):
  NUM-THRESH-POS, NUM-THRESH-SAME-NEARMISS, NUM-THRESH-UNIT-NEARMISS,
  NUM-GWORD-NEARMISS, NUM-MIXED-CONJ-NEARMISS, DA-FRAG-CHAIN-POS,
  DA-FRAG-ORPHAN-NEARMISS.

## Totals

- Runtime files: 4. Test files: 2.
- Lines added: ~110 (runtime ~80, tests ~30).
- Lines removed/reworked: ~25.
- No existing report/result under quote-aligner/, hybrid/, v0.4.1/, or
  tier1-proof/results/ was edited; the tier1 gate re-run rewrites only
  its own live outputs (operator-impact-summary.json,
  results/gate-results.json, results/operator-impact.json), which are
  derived artifacts by design.

## Single-pass compliance

- No Iteration B/C was performed.
- No new proof operator: every fix tunes existing DIRECT_ASSERTION /
  NUMERIC_CONFLICT eligibility, lexing, or lexicon forms.
- No reviewer/prompt changes, no packet changes, no KB changes.
- No case IDs in runtime files (id_guard 0 verified after the pass).
