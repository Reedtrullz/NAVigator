# Error Taxonomy - Quote Aligner v0.1 -> v0.2

Task: SEMANTIC-JUDGE-LEXICAL-COVERAGE-REPAIR. Scope: all 59 misses across
minimal-pairs (48), minimal-pairs-supplement (4), contra-insuff (69), modality (30),
actor-scope (30), locality (20), diagnostic-20 (20), ENT controls (4). Baseline results:
`results/qa05-summary.json` (frozen). Classifications grounded in claim+source text of each case.

## Category counts (59 misses)

| Category | Count | Share |
|---|---:|---:|
| ACTOR_ALIAS | 9 | 15.3 % |
| ANTONYM_GAP | 7 | 11.9 % |
| EXHAUSTIVENESS | 6 | 10.2 % |
| PREDICATE_PARAPHRASE | 5 | 8.5 % |
| MORPHOLOGY | 5 | 8.5 % |
| NEGATION_SCOPE | 4 | 6.8 % |
| TEMPORAL_BINDING | 4 | 6.8 % |
| NUMERIC_BINDING | 3 | 5.1 % |
| LEGAL_PHRASEOLOGY | 3 | 5.1 % |
| TOO_BROAD_MATCH | 3 | 5.1 % |
| MODALITY_STRENGTH | 3 | 5.1 % |
| SYNONYM_GAP | 3 | 5.1 % |
| COMPOUND_PREDICATE | 1 | 1.7 % |
| EXCEPTION_SCOPE | 1 | 1.7 % |
| CONDITIONAL_SCOPE | 1 | 1.7 % |
| PRONOUN_REFERENCE | 1 | 1.7 % |
| **Total** | **59** | 100 % |

Note: each case got one primary category; several also exercise secondary mechanisms
(e.g. exhaustive-list cases need predicate synonyms too). Counts reflect primary driver.

## Pareto analysis

Top-5 categories and cumulative share:

- ACTOR_ALIAS: 9 cases (cumulative 15.3 %)
- ANTONYM_GAP: 7 cases (cumulative 27.1 %)
- EXHAUSTIVENESS: 6 cases (cumulative 37.3 %)
- PREDICATE_PARAPHRASE: 5 cases (cumulative 45.8 %)
- MORPHOLOGY: 5 cases (cumulative 54.2 %)

**Answer to sec.3: the 5 largest general gaps explain 54 % of all misses
(37 % for top-3).** Five general mechanisms cover the Pareto:

1. Exhaustive-list membership (signer/referrer lists): CONTRA for non-listed actor,
   SUPPORT for listed actor; solo-use of listed actor is not exclusivity conflict.
2. Negation-scope / criteria negation: 'krever X, ikke bare Y' excludes Y; 'stiller ikke diagnoser' negates predicate for subject aliases.
3. Scalar binding: numeric bound conflicts (age, percent, duration, amount) and free/pay axis (gratis <-> koster/ma betale) with per-unit binding.
4. Predicate grounding via actor aliases: staff-membership pattern 'Tjeneste har faggruppe som gir X' grounds 'faggruppe i Tjeneste kan X'; destination-implies-processor; subset aliases (fastlege<lege, foreldre<familier, helsesykepleier<skolehelsetjeneste).
5. False-CONTRA guards: different predicates without explicit opposition, same-polarity cost/morphology confusions, recipient-subset non-conflict, object-scope for polarity.

Remaining long tail (MODALITY_STRENGTH, LEGAL_PHRASEOLOGY, CONDITIONAL_SCOPE,
EXCEPTION_SCOPE, SYNONYM_GAP, MORPHOLOGY, PRONOUN_REFERENCE, TEMPORAL_BINDING) is
addressed by the same mechanisms plus small canonicalization additions, not per-case rules.

## Per-case classification

Format: id | expected -> got | v0.1 rule | category | missing relation / fix direction.

### actor-scope
- **ACT-02** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **EXHAUSTIVENESS** | Exhaustive signer list 'av lege, psykolog eller barnevernsleder': non-listed actor + same predicate -> CONTRA
- **ACT-05** | INSUFFICIENT_EVIDENCE -> CONTRADICTED | rule `division_of_function` | **PREDICATE_PARAPHRASE** | Guard: division_of_function fired on 'stiller diagnose' vs 'utforer utredning'; different predicates without explicit opposition are INSUFF, not CONTRA
- **ACT-08** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **ACTOR_ALIAS** | Member-of-service: 'skolehelsetjenesten har lege ... som gir X' grounds 'lege ... kan foreta X' (staff membership + service-level predicate)
- **ACT-10** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **ACTOR_ALIAS** | fastlege in referrer enumeration grounds 'hovedhenviser' role; actor alias fastlege<=lege + enumeration membership
- **ACT-12** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **ACTOR_ALIAS** | foreldre subset of 'par og familier'; 'kan kontakte X direkte' <-> 'kan ta direkte kontakt'
- **ACT-13** | INSUFFICIENT_EVIDENCE -> SUPPORTED | rule `support_from_quote_alignment` | **ACTOR_ALIAS** | Support-gate actor check: barn not subset of 'par og familier' -> must not SUPPORT
- **ACT-19** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **PREDICATE_PARAPHRASE** | 'Soknad ... sendes til Husbanken' grounds 'Husbanken behandler soknad' (destination-implies-processor)
- **ACT-20** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ACTOR_ALIAS** | Same predicate, disjoint orgs (NAV vs Husbanken) -> CONTRA
- **ACT-23** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **COMPOUND_PREDICATE** | 'utreder' grounded by one part of compound 'utforer rettsmedisinsk undersokelse og samtale'
- **ACT-25** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **ACTOR_ALIAS** | psykolog in 'BUP har psykologer ... som gir behandling' grounds 'psykolog i BUP kan gi terapi' + terapi<behandling
- **ACT-29** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `self_agent_not_established` | **PREDICATE_PARAPHRASE** | Word-order: 'kan selv organisere X' == 'kan organisere X selv'

### contra-insuff
- **CI-004** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_candidate_span` | **NUMERIC_BINDING** | Age bound 20 vs 'under 18' -> numeric conflict
- **CI-007** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `exclusivity_unverified` | **EXHAUSTIVENESS** | Non-listed actor (laerer) vs exhaustive signer list -> CONTRA
- **CI-008** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_candidate_span` | **LEGAL_PHRASEOLOGY** | 'skal alltid innvilge' contradicted by 'individuell vurdering / ingen automatisk rett' (discretionary phraseology)
- **CI-009** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **NEGATION_SCOPE** | 'krever X, ikke bare psykiske plager' explicitly excludes plager-alone -> CONTRA
- **CI-011** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **TEMPORAL_BINDING** | Duration 12 maneder vs 'senest 3, utvidelse til 6' -> out of bound
- **CI-019** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ANTONYM_GAP** | gratis <-> ma betale axis, same subject -> CONTRA
- **CI-021** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **NUMERIC_BINDING** | 25 % vs minst 50 % -> numeric bound conflict
- **CI-023** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **TEMPORAL_BINDING** | maks 100 dager vs inntil 248 dager
- **CI-025** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ANTONYM_GAP** | 'uten aktivitetskrav' vs 'forutsetter aktivitetskravet' -> polarity opposition
- **CI-026** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ACTOR_ALIAS** | Disjoint application recipients (NAV vs Husbanken) same predicate -> CONTRA
- **CI-030** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **TEMPORAL_BINDING** | Klagefrist 12 vs 3 uker
- **CI-032** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ANTONYM_GAP** | midlertidig <-> varig criteria opposition
- **CI-046** | INSUFFICIENT_EVIDENCE -> CONTRADICTED | rule `recipient_disjoint` | **ACTOR_ALIAS** | Guard: fastlege subset of lege, so 'bare fra fastlege' vs 'fra lege eller spesialist' is not recipient-disjoint; enumeration w/o exclusivity -> INSUFF
- **CI-047** | INSUFFICIENT_EVIDENCE -> SUPPORTED | rule `support_from_quote_alignment` | **TOO_BROAD_MATCH** | Cost payee scope: 'gratis for foreldrene' says nothing about who pays -> must not SUPPORT 'skolen ma betale'
- **CI-048** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `claim_stronger_than_source` | **EXCEPTION_SCOPE** | 'kan unnta melding fra varsling' defeats claim 'ma varsle alltid'
- **CI-056** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **LEGAL_PHRASEOLOGY** | 'automatisk' vs 'krever soknad og vurdering' -> CONTRA

### diagnostic-20
- **D20-M1** | CONTRADICTED -> SUPPORTED | rule `support_from_quote_alignment` | **MODALITY_STRENGTH** | 'kan velge aa utelate' (option to omit) vs 'skal utbetale' (obligation) -> CONTRA
- **D20-A1** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **PREDICATE_PARAPHRASE** | signeres <-> underskrives synonym + listed-actor membership -> SUPPORT
- **D20-A2** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **EXHAUSTIVENESS** | fysioterapeut not in exhaustive signer list -> CONTRA
- **D20-A4** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `exclusivity_unverified` | **EXHAUSTIVENESS** | 'kun leger' exclusivity vs two-actor source list -> CONTRA
- **D20-A5** | SUPPORTED -> CONTRADICTED | rule `exclusivity_conflict` | **EXHAUSTIVENESS** | Guard: 'alene' by a listed actor is not exclusivity conflict; list without 'sammen med' allows solo signing -> SUPPORT
- **D20-C4** | INSUFFICIENT_EVIDENCE -> SUPPORTED | rule `support_from_quote_alignment` | **TOO_BROAD_MATCH** | 'utgifter til behandling' does not ground 'reiseutgifter' (object too broad) -> INSUFF
- **D20-C5** | INSUFFICIENT_EVIDENCE -> CONTRADICTED | rule `polarity_conflict` | **TOO_BROAD_MATCH** | Guard: polarity conflict requires same object; negating different object (reiseutgifter) is INSUFF

### ent
- **ENT-D** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ACTOR_ALIAS** | helsesykepleier in skolehelsetjenesten staff; source negates predicate for that subject ('stiller ikke diagnoser') -> CONTRA via alias+negation

### locality
- **LOC-04** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ANTONYM_GAP** | koster 300 vs gratis (free/pay axis) + RPH service alias
- **LOC-11** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **SYNONYM_GAP** | lavterskeltilbud <-> lavterskeltjenester; ha <-> tilby

### minimal-pairs-supplement
- **MP-015A** | SUPPORTED -> CONTRADICTED | rule `modifier_antonym` | **TEMPORAL_BINDING** | meldefristen == 1-ukesfristen domain alias; do not fire modifier_antonym

### minimal-pairs
- **MP-004B** | INSUFFICIENT_EVIDENCE -> CONTRADICTED | rule `division_of_function` | **PREDICATE_PARAPHRASE** | Guard: 'raadgivning' vs 'stille diagnose' are different predicates, no division_of_function opposition -> INSUFF
- **MP-005B** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `exclusivity_unverified` | **EXHAUSTIVENESS** | laerer not in exhaustive signer list -> CONTRA
- **MP-007A** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **MODALITY_STRENGTH** | 'normalt X' supported by flat 'er X'; modifier must not block numeric/predicate match
- **MP-008A** | SUPPORTED -> PARTIALLY_SUPPORTED | rule `polarity_conflict` | **NEGATION_SCOPE** | Near-verbatim: 'ingen automatisk rett' must match itself; spurious polarity_conflict on shared negation token
- **MP-008B** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_candidate_span` | **LEGAL_PHRASEOLOGY** | 'skal alltid innvilge' vs 'ingen automatisk rett' -> CONTRA
- **MP-009A** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `ambiguous_evidence` | **SYNONYM_GAP** | ordningen <-> regelen subject synonym
- **MP-012A** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `ambiguous_evidence` | **MORPHOLOGY** | NP tolerance: inserted relative clause 'som star i ordningen' inside subject
- **MP-013B** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **NEGATION_SCOPE** | 'reduserer ikke ... direkte' = indirect path exists; 'teller ikke i inntektsgrunnlag' contradicted; needs scoped-negation + indirect-channel rule (hard)
- **MP-014B** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **NUMERIC_BINDING** | claim 'over 1500' vs source 1006 per forelder -> numeric conflict with per-unit binding
- **MP-016A** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **CONDITIONAL_SCOPE** | Same predicate 'reduseres bidraget', different non-conflicting condition (nytt barn vs lav inntekt) -> SUPPORT
- **MP-017B** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **NEGATION_SCOPE** | 'ikke bare psykiske plager' excludes plager-alone -> CONTRA
- **MP-019A** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **MORPHOLOGY** | 'vurderer rettigheter' <-> 'rettighetsvurdering' compound/verbal noun
- **MP-024A** | SUPPORTED -> CONTRADICTED | rule `cost_axis_opposition` | **MORPHOLOGY** | krisesentrene <-> krisesenter definite/plural; cost_axis_opposition must not fire on same polarity
- **MP-024B** | INSUFFICIENT_EVIDENCE -> CONTRADICTED | rule `cost_axis_opposition` | **MORPHOLOGY** | Same as MP-024A + compound claim conjunction handling

### modality
- **MOD-08** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **SYNONYM_GAP** | vanligvis <-> normalt
- **MOD-13** | SUPPORTED -> INSUFFICIENT_EVIDENCE | rule `predicate_grounding_unverified` | **PRONOUN_REFERENCE** | 'rett til det' -> antecedent spesialundervisning (local resolution)
- **MOD-14** | SUPPORTED -> CONTRADICTED | rule `polarity_conflict` | **MORPHOLOGY** | 'frivillig a delta' <-> 'deltakelsen er frivillig' nominalization; polarity_conflict guard
- **MOD-23** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ANTONYM_GAP** | koster 250 vs gratis -> CONTRA
- **MOD-25** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **MODALITY_STRENGTH** | 'i alle saker' vs 'kan i saerlige tilfeller' -> universal vs special-case CONTRA
- **MOD-27** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ANTONYM_GAP** | 'uten signatur' vs 'skal vaere undertegnet' -> required/not-required opposition
- **MOD-29** | CONTRADICTED -> INSUFFICIENT_EVIDENCE | rule `no_deterministic_signal` | **ANTONYM_GAP** | ma betale leie vs kostnadsfritt -> CONTRA

## ENT-D root cause audit (sec.27)

- Claim: 'ADHD-diagnose kan stilles av helsesykepleier på skolen.'
- Source (KB 31): 'Skolehelsetjenesten er ikke et behandlingstilbud for psykiske lidelser; den yter ikke psykisk helsebehandling og stiller ikke diagnoser.'
- Why v0.1 failed (no_deterministic_signal): the negated predicate 'stiller ikke diagnoser' has subject 'Skolehelsetjenesten' while the claim's actor is 'helsesykepleier'. v0.1 negation detection requires subject overlap and v0.1 has no actor alias linking helsesykepleier to skolehelsetjenesten staff, so no contradiction proof obligation is established.
- Missing lexical/semantic relations:
  1. ACTOR_ALIAS: helsesykepleier is staff of skolehelsetjenesten (institutional staff-membership).
  2. NEGATION_SCOPE on service-level predicates: 'stiller ikke diagnoser' negates 'stiller ADHD-diagnose' for every staff member of that service; the claim asserts exactly that predicate for a staff member.
- General v0.2 rule (no ENT-specific patch): explicit negation of a canonical predicate P with subject S contradicts a claim asserting P (positive polarity) for any alias/staff-member actor A where A in staff_of(S). Staff-of relations come from a small generic domain map (helsesykepleier/lege -> skolehelsetjenesten; psykolog/lege -> BUP; etc.).

## Coverage observations for design (feeds iteration A)

- Confirmed-CONTRA cases show the contradiction proof structure works when spans are found; the misses are span/binding failures, not verdict-logic failures.
- All INSUFF-misses are 'proof not found' (no span/signal) -> the lexical normalizer must emit candidate spans for these patterns.
- All false-CONTRA cases are over-firing rules that lack a guard -> guard clauses, not new verdict paths.
- FP-SUP cases (CI-047, ACT-13, D20-C4, D20-M1) need the support gate to require payee/actor/object scope compatibility before quoting a matched span.
