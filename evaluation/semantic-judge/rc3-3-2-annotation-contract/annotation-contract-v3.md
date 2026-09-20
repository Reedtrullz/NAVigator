# Annotation Contract v3 (CANONICAL - SHARED BY ALL ANNOTATORS)

You annotate claim-evidence pairs. You see only the claim and verbatim
evidence spans. You output one JSON object per case matching
annotation-contract-v3.schema.json exactly. This contract is the complete
rule set. There is no other guidance.

## Layer separation (hard rule)

This contract covers ONLY the semantic relation layer. Proof safety,
adjudication state, and product actions (AUTO_*, REVIEW_REQUIRED,
ABSTAIN_INSUFFICIENT) are different layers and MUST NOT appear in any
output field. The label REVIEW_REQUIRED is FORBIDDEN everywhere in this
schema.

## 1. semantic_relation (canonical enum)

- ENTAILS: the evidence, taken alone, establishes the claim's proposition
  as stated (same polarity, same scope, same modality or stronger).
- CONTRADICTS: the evidence positively and explicitly establishes the
  opposite of the claim's proposition for the same subject, scope, and
  time. Mere absence of support is NEVER contradiction.
- PARTIAL: the claim is compound under rule 6 and the evidence genuinely
  establishes at least one conjunct while another conjunct is
  contradicted or unestablished. PARTIAL is never used for uncertainty.
- RELATED_BUT_INSUFFICIENT (RBI): the evidence is topically relevant to
  the claim's proposition, does not establish it, does not positively
  refute it, PARTIAL's rule is not met, and ambiguity is not the main
  problem. Typical RBI shapes: source modality weaker than claim
  (source "kan/be oppfordret" vs claim "skal/har rett til"); source
  states a conditional right while claim is unconditional; same topic
  but wrong period; same benefit type but the claim's quantity is not
  established; evidence about a different actor/scope/population.
- AMBIGUOUS: at least two plausible semantic interpretations of the
  evidence remain open after applying this contract. Ordinary lack of
  proof is RBI, not AMBIGUOUS.

Decision order: check CONTRADICTS (positive refutation) first, then
ENTAILS (full establishment), then PARTIAL (rule 6), then RBI (default
for related-but-undecided), then AMBIGUOUS (only for the tie between
two live readings).

## 2. Quantity identity fields

quantity_identity classifies the claim's central quantity against the
quantity the evidence quantifies:

- SAME: both address one identifiable semantic quantity (same benefit,
  same actor class, same period instance where a period is part of the
  claim). Value equality is NOT required for SAME; value differences
  are handled by the comparator fields.
- DIFFERENT: the evidence quantifies a different semantic quantity
  instance (different period, different benefit, different actor's
  amount) than the claim asserts.
- UNRESOLVED: the evidence does not clearly quantify any quantity that
  can be aligned or distinguished.
- NOT_APPLICABLE: the claim asserts no specific quantity.

quantity_type: MONEY, PERIOD, AGE, DATE, PERCENTAGE, COUNT, or
NOT_APPLICABLE.

quantity_value_claim / quantity_value_source: canonical ASCII strings
"VALUE UNIT" (examples: "1286 NOK", "2292 NOK", "6 MONTH", "12 YEAR",
"3 WEEK"), or null when quantity_identity is NOT_APPLICABLE or
UNRESOLVED. Values must be copied/computed from claim and evidence
text; never invented. Free text, suffix formats such as
"2292:AGGREGATE", and prose are schema violations.

When the evidence states several values, quantity_value_source is the
single value aligned to the claim's central quantity. For an aggregate
claim whose evidence states only components, the deciding value is the
computed sum (after REQUIRED arithmetic); if the evidence states the
total directly, use that total. Equal numbers alone do not make
quantities the same: identity tracks the semantic quantity (same
benefit, actor class, period instance), not the numeral.

quantity_type: MONEY, PERIOD, AGE, DATE, PERCENTAGE, COUNT, or
NOT_APPLICABLE. For compound claims, the quantity fields describe the
deciding conjunct: the conjunct the evidence refutes or leaves
unestablished (for PARTIAL/CONTRADICTS), or the first conjunct (for
ENTAILS). Age mentions that only delimit a population (for example
"foreldre med barn under 16 ar") are scope, not the central quantity.

REPAIR 1 (binding clarification): for compound claims with PARTIAL
relation, the quantity fields bind to the ESTABLISHED conjunct - the
conjunct the evidence actually quantifies. quantity_identity is SAME
when the evidence quantifies that same semantic quantity (same
benefit, actor class, period instance), even though other conjuncts
are unaddressed. Unaddressed conjuncts never by themselves make
quantity_identity DIFFERENT; DIFFERENT still requires the evidence to
quantify a genuinely different instance of the same quantity type.

role classifies the claim's central quantity: DIRECT (stated value for
the subject), AGGREGATE (claim asserts a total/sum), COMPONENT (claim
asserts a part of a stated total), DERIVED (claim asserts a computed
value not stated in source and not a sum), NOT_APPLICABLE.

## 3. Temporal contract

temporal_applicability compares the claim's time frame with the
evidence's validity frame:

- APPLICABLE: evidence's stated validity covers the claim's frame
  (undated current-rule claims match sources stating current rules).
- HISTORICAL_ONLY: claim is about a period entirely before the
  evidence's validity starts, or evidence explicitly marks the rule as
  historic/superseded while the claim treats it as current.
- FUTURE_ONLY: claim is about a period entirely after any validity the
  evidence can support.
- OVERLAPS: claim's frame and evidence's frame partially overlap;
  evidence covers part of what the claim asserts.
- NON_OVERLAPPING: frames are disjoint.
- NOT_APPLICABLE: neither claim nor evidence carries a time dimension.
- UNRESOLVED: claim and evidence carry time information, but the
  packet genuinely cannot place the claim's frame in any class above
  (for example an open-ended validity with no stated end against a
  claim asserting a far-future state). UNRESOLVED requires that real
  temporal information exists but underdetermines the class; never use
  it as a synonym for "I am unsure".

Boundary clarification (frozen): use HISTORICAL_ONLY or FUTURE_ONLY
only when the evidence states an explicit validity start/end,
supersession, or historic marking that separates the frames. When the
evidence is an undated current rule and the claim asserts a specific
future state or future date, use UNRESOLVED, because the packet cannot
establish which rule will apply then. When the claim asserts a specific
past date before an explicit validity start, use HISTORICAL_ONLY.

## 4. Comparator contract

comparator_applicable = true ONLY when all four hold:

1. claim and evidence address the SAME semantic quantity
   (quantity_identity = SAME),
2. temporal_applicability is compatible with deciding the relation
   (not NON_OVERLAPPING, not FUTURE_ONLY, not UNRESOLVED),
3. deciding the semantic relation actually requires comparing values
   (values differ, or the claim itself asserts a comparison), and
4. the quantities do not already fail on actor/scope/object identity.

Otherwise comparator_applicable = false and comparator_relation =
NOT_APPLICABLE. A number merely appearing in the evidence (for example
an age threshold in a rule about a different population) never makes a
comparator applicable.

comparator_relation (only when applicable):

- EQUIVALENT: source value equals claim value.
- SOURCE_STRONGER: source value is numerically greater/higher.
- SOURCE_WEAKER: source value is numerically smaller/lower.
- INCOMPATIBLE: values cannot be ordered on one scale (different units
  or non-numeric mismatch).
- UNRESOLVED: values exist but cannot be determined from the packet.

Direction rule (frozen): compare numeric magnitudes only. Source 6
MONTH vs claim 12 MONTH is SOURCE_WEAKER even if a longer validity
might intuitively feel "stronger". If the claim asserts a comparison
between two quantities both present in the evidence, classify the
evidence's actual relationship: it is SOURCE_STRONGER when the source
facts make the claim's asserted comparison true.

## 5. Arithmetic duty

arithmetic_duty:

- REQUIRED: deciding the relation requires a simple, explicit,
  contract-permitted computation from stated evidence values (example:
  component 1006 NOK + component 1286 NOK = claimed aggregate). When
  REQUIRED, the annotator MUST compute and fill derived_quantity;
  deliberately skipping the computation is a contract violation.
- PERMITTED: a computation could be run diagnostically but the relation
  is decidable without it.
- FORBIDDEN: the would-be operands belong to different semantic
  quantities or periods, or the computation requires inference beyond
  simple addition/subtraction/comparison of stated values.
- NOT_APPLICABLE: no computation is involved; values are stated
  directly or the computation already appears verbatim in the evidence
  (reading "2 012 / 2 = 1 006" from the source is not annotation
  arithmetic).

derived_quantity (required object when REQUIRED, else null):

- operands: array of canonical "VALUE UNIT" strings copied from
  evidence,
- operation: one of ADD, SUBTRACT, COMPARE,
- value: canonical computed "VALUE UNIT" string,
- provenance_span_ids: array of evidence span_ids used,
- quantity_identity: SAME or DIFFERENT (the derived value vs the
  claim's asserted value),
- role: usually AGGREGATE or DERIVED.

## 6. Compound claims and PARTIAL

Treat a claim as compound only when it contains distinct conjuncts
(assertions joined by "og", sentence split, or clearly independent
predicates). An "og" that coordinates parts of one proposition (for
example "hud og hares") is not two conjuncts. If the claim is compound
and the evidence establishes one conjunct while another is
unestablished, use PARTIAL. If every conjunct is established, ENTAILS;
if one is positively refuted, CONTRADICTS takes precedence over
PARTIAL only when the refuted conjunct is central to the claim;
otherwise PARTIAL.

## 7. Output rules

- Output exactly one JSON object per case with the fields required by
  annotation-contract-v3.schema.json. No extra fields, no prose, no
  Markdown fences.
- rationale: one sentence, maximum 300 characters, grounded in claim
  and evidence text only.
- If the evidence contains verbatim quoted computation or stated
  values, copy them exactly; never round or reformat values.
