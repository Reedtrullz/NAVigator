# Coverage fix spec - one implementation pass

Task: SEMANTIC-JUDGE-TIER1-COVERAGE-REPAIR. Governing constraints: max one
implementation pass (spec 8), no new operators, no new inference doctrine,
no case-ID patching (spec 14), validator not weakened (spec 12), every
general fix needs near-miss tests (spec 13), ENT-C/N-A4/N-R1 hard canaries
(spec 7).

## Pre-implementation proof-path audit (spec 3)

For each of the 7 cases the existing path that should produce the correct
auto verdict is recorded in known-coverage-gaps.json
(expected_existing_path). All 7 are constructible from existing evidence
spans, so none is reclassified as IMPLEMENTATION_ASSUMPTION_INVALID.

## Fixes (all general, all landed)

### F1. Longest-match-first concept polarity

File: quote-aligner/v0.2/polarity_engine_v02.py
(_concept_polarity). Match negated multi-word forms before bare positive
heads. "Ingen kostnad" must lex as free_of_charge=+, not as cost-bearing.
Generality: every negative_form vs positive_form overlap in the lexicon.
Near-miss: "kostnad" alone stays negative (test: LMF bare 'kostnad').

### F2. G-unit lexing with word boundary

File: quote-aligner/v0.2/polarity_engine_v02.py (_UNIT, _UNITS).
"4 G" now lexes as a G bound; the pattern ends in \b so "6 ganger" never
lexes as G. Near-miss: "ganger" claims abstain (test: G-word boundary).

### F3. Binding framing extension

File: quote-aligner/v0.2/polarity_engine_v02.py (_FRAMING_RE). Add
"inntekt|grense" so income-threshold claims carry binding framing.
Near-miss: framing is necessary but not sufficient; numeric operators
still require a same-unit bound pair (test: mixed conjuncts).

### F4. "Ingen henvisning" lexicon form

File: quote-aligner/v0.2/domain-lexicon.json (requires_referral
negative_forms). General form: negated referral is direct contact.
Covers: "ingen henvisning", "ingen henvisningnodvendighet" style
paraphrases. Not benchmark-specific (generic: true).

### F5. Fragment chaining for direct assertion

Files: tier1-proof/tier1_operators.py (direct_assertion,
_sentence_has_own_actor), tier1-proof/proof_validator.py. A no-actor
fragment premise is acceptable when it directly follows a bound sentence
with a shared subject; the validator independently re-checks the chain
from any preceding bound sentence. Near-miss: an orphan fragment with no
bound neighbour abstains (regression DA-FRAG-ORPHAN-NEARMISS).

### F6. Dummy-subject numeric eligibility

File: tier1-proof/tier1_operators.py (_DUMMY_RE, numeric_conflict).
"Det er ingen ... over 4 G" asserts the cutoff without a lexical actor,
so the same-subject requirement is vacuous for such claims. Near-miss:
non-dummy claims still need subject binding (test: NUM mixed conjuncts;
DA scope/time near-misses unchanged).

### F7. Exclusion-threshold conflict rule

Files: tier1-proof/tier1_operators.py (_EXCL_RE, _DIR_RE,
_exclusion_flag, _conflicting_pair), tier1-proof/proof_validator.py.
When claim and sentence both assert an exclusion ("ingen/ikke ... over/
under X") with same-kind same-unit bounds and different values, the
cutoffs conflict even though value spans overlap. Implemented once in a
shared helper used by both operator and validator, so the independent
re-derivation cannot drift. Near-miss: same cutoff abstains
(NUM-THRESH-SAME-NEARMISS), different unit abstains
(NUM-THRESH-UNIT-NEARMISS).

### F8. Mixed-conjunct eligibility pre-pass

File: tier1-proof/tier1_operators.py (numeric_conflict). The operator is
eligible only if every claim bound conflicts on one sentence axis;
partial conflicts are reviewer work. Near-miss: "100 kr per dag og
maksimalt 5000 kr totalt" vs "200 kr per dag" abstains
(NUM-MIXED-CONJ-NEARMISS).

### F9. Validator premise-count alignment

File: tier1-proof/proof_validator.py. DIRECT_ASSERTION accepts 1-2
premises per the frozen spec grammar (SIMPLE_ARITHMETIC already spans
multiple sentences); per-premise derived_fact span checks retained.
No premise reduction below spec grammar; spec 12 respected.

## Deliberately not changed

- _time_compatible unknown-time-axis rule (HOL014 blocker): doctrine
  boundary; relaxing it is a semantic change.
- hybrid numeric_support_binding multiword-actor guard (LOC-13 blocker):
  also gates CAL021/CAL023 misfires; relaxing trades one safe auto for
  two unsafe ones.
- No voluntariness concept added (MOD-14 blocker): a new rescue doctrine,
  not an alias.
- No multiplier-axis operator extension (HOL006 blocker): compound
  numeric gate is new inference.

## Case-ID patching check

No runtime file contains benchmark case IDs, full benchmark claims, or
ID-to-verdict mappings. All test/regression content lives in test corpora
only. id_guard = 0 verified after the pass.
