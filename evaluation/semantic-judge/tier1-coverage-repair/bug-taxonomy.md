# Bug taxonomy - 7 known coverage gaps

Task: SEMANTIC-JUDGE-TIER1-COVERAGE-REPAIR. Classes follow the frozen
taxonomy list (spec 4). One case can combine classes; the primary class is
listed first.

## Case classification

| Case | Primary class | Secondary class | Outcome |
|---|---|---|---|
| CAL011 | LEXICON_ALIAS_MISS | SPAN_SELECTION_BUG | FIXED_SAFE_AUTO |
| CAL014 | LEXICON_ALIAS_MISS | NEGATION_BINDING_BUG | FIXED_SAFE_AUTO |
| CAL034 | LEXER_MISS | OPERATOR_ELIGIBILITY_BUG | FIXED_SAFE_AUTO |
| HOL006 | NUMERIC_BINDING_BUG | - | REMAINS_REVIEW_BY_DESIGN |
| HOL014 | LEXER_MISS | TEMPORAL_BINDING_BUG | REMAINS_REVIEW_BY_DESIGN |
| LOC-13 | PIPELINE_PLUMBING_BUG | ACTOR_TYPE_MISS | REMAINS_REVIEW_BY_DESIGN |
| MOD-14 | LEXICON_ALIAS_MISS | ACTOR_TYPE_MISS | REMAINS_REVIEW_BY_DESIGN |

FALSE_SHOULD_AUTO_CLASSIFICATION: 0. All seven proofs are constructible
from existing evidence spans, so none of the annotations overrated the
system; the remaining four are blocked by doctrine boundaries, not by a
wrong audit.

## Per-case root cause

### CAL011 - LEXICON_ALIAS_MISS (fixed)

"Ingen henvisning" is a positive direct-contact form, but the
requires_referral concept had no such negative form, so the source premise
"Gratis, ingen henvisning." carried no polarity for the concept. The claim
premise is also a no-actor fragment ("Gratis, ingen henvisning.") that
direct assertion rejected because it never chains from the bound preceding
sentence. Fixed by one general lexicon form plus generic fragment chaining.

### CAL014 - LEXICON_ALIAS_MISS (fixed)

Same lexicon gap; additionally "ingen kostnad" was read as cost-bearing
because shortest-form matching fired on "kostnad" before the negated
phrase. Fixed by longest-match-first polarity matching plus the "ingen
henvisning" form.

### CAL034 - LEXER_MISS (fixed)

"Inntekt over 4 G" was never lexed as a G-unit bound: the standalone "G"
token was not a unit, and the unit pattern previously also swallowed "g"
from "ganger" (word-boundary bug fixed in the same pass). With bounds now
lexed, the remaining blockers were operator eligibility: the dummy subject
"Det er" yields no lexical actor, and two same-kind exclusion thresholds
("over 4" vs "over 6") overlap as value spans although they conflict as
policy cutoffs. Fixed by a dummy-subject relaxation (claims asserting a
bound without a lexical subject) and an exclusion-threshold conflict rule
shared by the operator and the independent validator. Both fixes are
narrow: the all-bounds eligibility pre-pass and same-kind+same-unit+"
ingen/ikke ... over/under" guards remain.

### HOL006 - NUMERIC_BINDING_BUG (not fixed, by design)

"2,48 ganger grunnbeloepet" vs "2,25 ganger grunnbeloepet" is a
multiplier-unit conflict. The claim also mixes the multiplier with a
recomputed monthly amount, so a correct proof needs a compound numeric
comparison (multiplier axis and derived kr/month axis) that the existing
operator doctrine does not implement. Adding it would be new inference
doctrine; case stays review.

### HOL014 - LEXER_MISS (not fixed, by design)

"6 385" uses a space-formatted thousands separator the lexer does not
join, so the source bound never forms. Even with lexing fixed, the claim's
"fra 1. januar 2026" axis vs the source's undated schedule is exactly the
unknown-time-axis case the strict time-compatibility rule abstains on.
Relaxing that rule is a doctrine change; case stays review.

### LOC-13 - PIPELINE_PLUMBING_BUG (not fixed, by design)

The polarity engine already yields SUPPORTED; the hybrid
numeric_support_binding guard refuses multiword actor equality ("BUP i
Trondheim"). The same guard is what blocks CAL021/CAL023 engine misfires,
so relaxing it trades one correct auto for two unsafe ones. Case stays
review; the guard is load-bearing.

### MOD-14 - LEXICON_ALIAS_MISS (not fixed, by design)

"Det er frivillig aa delta i undersoekelsen" vs "Deltakelsen er frivillig."
needs both a new voluntariness concept and a dummy-subject-to-noun
("Deltakelsen") actor chain. That is a near-verbatim support rescue
doctrine, not an alias registration; case stays review.

## Implemented general fixes mapped to classes

- LEXICON_ALIAS_MISS: longest-match-first concept polarity (polarity
  engine), "ingen henvisning" negative form (domain lexicon).
- LEXER_MISS: "G" as a unit suffix with word boundary so "6 ganger" never
  lexes as G; "inntekt|grense" added to binding framing.
- OPERATOR_ELIGIBILITY_BUG: dummy-subject relaxation, exclusion-threshold
  conflict rule, all-bounds pre-pass against mixed-conjunct auto.
- SPAN_SELECTION_BUG: no-actor fragment chaining to an adjacent bound
  sentence (operator) with an independent validator mirror.
- PROOF_VALIDATOR_BUG: validator re-derivations now share the operator's
  conflict rule (one helper) and chain rule instead of divergent private
  copies; validator strictness unchanged (spec 12).
