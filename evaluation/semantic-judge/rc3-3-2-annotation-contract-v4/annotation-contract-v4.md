# Annotation Contract v4 (CANONICAL - SHARED BY ALL ANNOTATORS)

You annotate claim-evidence pairs. You see only the claim and verbatim
evidence spans (plus, when present, a packet-level reference_date). You
output one JSON object per case matching annotation-contract-v4.schema.json
exactly. This contract is the complete rule set. There is no other guidance.

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
  problem. Typical RBI shapes: source modality weaker than claim; source
  states a conditional right while claim is unconditional; same topic
  but wrong period; same benefit type but the claim's quantity is not
  established on the claim's stated basis; evidence about a different
  actor/scope/population.
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
  amount, or a rate basis the contract cannot convert to the claim's
  basis) than the claim asserts.
- UNRESOLVED: the evidence does not clearly quantify any quantity that
  can be aligned or distinguished.
- NOT_APPLICABLE: the claim asserts no specific quantity.

quantity_identity is about the semantic quantity, NEVER about how a
value was obtained (see value_source). A value derived by frozen
arithmetic from source components still describes the SAME quantity
when rule 5's aggregate rule is met.

quantity_type: MONEY, PERIOD, AGE, DATE, PERCENTAGE, COUNT, or
NOT_APPLICABLE.

quantity_value_claim: canonical "VALUE UNIT" string (or ISO date for
quantity_type DATE) copied from the claim, or null when the claim
asserts no specific value or quantity_identity is NOT_APPLICABLE or
UNRESOLVED. Values are copied/computed per the frozen unit table in
quantity-contract-v4.json; never invented. Free text, suffix formats
such as "2292:AGGREGATE", and prose are schema violations.

quantity_value_source: canonical "VALUE UNIT" string (or ISO date for
DATE) for the evidence-side value of the SAME quantity, or null when
the evidence provides no value on the claim's basis.

value_source (provenance enum - how the evidence-side deciding value is
obtained; this is a separate dimension from quantity_identity):

- EXPLICIT_SOURCE: value stated verbatim in the evidence.
- EXPLICIT_CLAIM: the only value available is the claim's own asserted
  value; the evidence addresses the quantity without stating its own
  number.
- DERIVED_FROM_SOURCE: value obtained by one frozen arithmetic/
  conversion operation from stated source values (rate x months,
  unit-converted duration, percentage of a stated base).
- DERIVED_FROM_CLAIM: value obtained by frozen arithmetic from the
  claim's own stated values only.
- AGGREGATED_FROM_SOURCE: value is the sum of component values the
  evidence states for the same aggregate (rule 5).
- COMPONENT_FROM_SOURCE: the claim's value is one component explicitly
  stated within a stated total in the evidence.
- UNRESOLVED: a value exists in the packet but the packet cannot
  establish which value is the deciding one for this quantity.
- NOT_APPLICABLE: no quantity involved.

Unit canonicalization (frozen, see quantity-contract-v4.json): PERIOD
values use DAY, WEEK, MONTH, or YEAR. Exact frozen factors: 7 DAY = 1
WEEK and 12 MONTH = 1 YEAR. Durations are written in the claim's unit
when exactly convertible by these factors; all other period conversions
(notably DAY to MONTH and WEEK to MONTH) are FORBIDDEN. A rate stated
per month converts to a yearly amount only by the frozen MULTIPLY 12
rule. Rates on other bases (per vedtak, per barn, per sak) have no
frozen conversion; a claim on such a basis against evidence on another
basis is quantity_identity = DIFFERENT with relation RBI (never
CONTRADICTS).

When the evidence states several values, quantity_value_source is the
single value aligned to the claim's central quantity. For compound
claims, the quantity fields describe the deciding conjunct: the conjunct
the evidence refutes or leaves unestablished (for PARTIAL/CONTRADICTS),
or the first conjunct (for ENTAILS). REPAIR 1 binding (carried from v3):
for compound claims with PARTIAL relation, the quantity fields bind to
the ESTABLISHED conjunct. Unaddressed conjuncts never by themselves make
quantity_identity DIFFERENT. Age mentions that only delimit a population
are scope, not the central quantity.

role: DIRECT (stated value for the subject), AGGREGATE (claim asserts a
total/sum), COMPONENT (claim asserts a part of a stated total), DERIVED
(claim asserts a computed value not stated in source and not a sum),
NOT_APPLICABLE.

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
- OVERLAPS: claim's frame and evidence's frame partially overlap.
- NON_OVERLAPPING: frames are disjoint.
- NOT_APPLICABLE: neither claim nor evidence carries a time dimension.
- UNRESOLVED: claim and evidence carry time information, but the
  packet genuinely cannot place the claim's frame in any class above.
  UNRESOLVED requires that real temporal information exists but
  underdetermines the class; never use it as a synonym for "I am unsure".

Boundary clarification (carried from v3): use HISTORICAL_ONLY or
FUTURE_ONLY only when the evidence states an explicit validity start or
end, supersession, or historic marking that separates the frames. An
undated current rule against a specific far-future assertion is
UNRESOLVED. A specific past date before an explicit validity start is
HISTORICAL_ONLY.

## 4. Deictic temporal anchors

Deictic expressions (denne uken, denne maneden, i ar, na, i dag, neste
maned, forrige uke) are bound deterministically:

1. If the case packet contains an explicit reference_date (ISO date),
   the deictic term binds to it: "denne uken" = the Monday-Sunday week
   containing reference_date; "denne maneden" = the calendar month
   containing reference_date; "i ar" = the calendar year of
   reference_date; "na" and "i dag" = reference_date itself; "neste
   maned" = the calendar month after reference_date's month; "forrige
   uke" = the week before reference_date's week. The bound frame is
   then compared with the evidence's validity frame under rule 3.
2. If the packet contains NO explicit reference_date, a deictic frame
   cannot be bound: temporal_applicability = UNRESOLVED. Never guess
   the actual current date. Never use the annotation run date.
3. Publication, verification, or document dates inside the evidence
   ("lest 30.08.2026", "oppdatert 25.08.2026") are NOT reference dates.
   They never anchor a deictic term.

Frozen consequence: when the deictic frame is UNRESOLVED, the time-
indexed part of the claim is unestablished, so the relation cannot be
ENTAILS or CONTRADICTS on that reading; use RELATED_BUT_INSUFFICIENT
(or PARTIAL/AMBIGUOUS if their own rules are met by other conjuncts or
readings). If the claim also works as a timeless statement of the same
proposition and the evidence establishes that, prefer ENTAILS only when
the deictic term adds no restricting content; otherwise RBI.

## 5. Comparator contract (decision tree)

comparator_applicable = true ONLY when ALL five hold:

1. claim and evidence address the SAME semantic quantity
   (quantity_identity = SAME),
2. temporal_applicability is compatible with deciding the relation
   (not NON_OVERLAPPING, not FUTURE_ONLY, not UNRESOLVED),
3. actor/scope/object are compatible,
4. both sides express numeric constraints or values on the same scale,
5. deciding the semantic relation REQUIRES relating the two values:
   the values differ, or the claim itself asserts a comparison,
   threshold, or range.

Exact-match rule (frozen): if source and claim state exactly the same
numeric proposition and the relation is decidable as ENTAILS without
comparator reasoning, comparator_applicable = false. A number merely
appearing on both sides never activates the comparator.

Comparator is about constraint relations (>, >=, <, <=, ranges,
thresholds, direction), never about the mere presence of two numbers.

Referent rule (frozen): when applicable, comparator_relation classifies
the pair (claim's asserted value or comparison operand) versus
(evidence's stated value for the same referent). For a claim asserting
"X er mer enn T" (or a threshold T), the referent pair is (evidence's
X) versus (T): SOURCE_STRONGER when the source facts make the claim's
asserted comparison true. For a plain differing-value claim, the pair
is (claim value) versus (source value).

comparator_relation (only when applicable):

- EQUIVALENT: source value equals claim value.
- SOURCE_STRONGER: source value is numerically greater/higher.
- SOURCE_WEAKER: source value is numerically smaller/lower.
- INCOMPATIBLE: values cannot be ordered on one scale (different units
  or non-numeric mismatch).
- UNRESOLVED: values exist but cannot be determined from the packet.

Direction rule (carried from v3): compare numeric magnitudes only.
Source 6 MONTH vs claim 12 MONTH is SOURCE_WEAKER. comparator_relation
is decided ONLY on cases where comparator_applicable = true; when
false it is always NOT_APPLICABLE. Decide applicability FIRST, then
the relation.

## 6. Arithmetic duty

arithmetic_duty:

- REQUIRED: deciding the relation requires a simple, explicit,
  contract-permitted computation from stated evidence values (sum of
  components for an aggregate claim, frozen unit conversion, frozen
  rate-to-period conversion, or a comparison of stated values). When
  REQUIRED, the annotator MUST compute and fill derived_quantity;
  deliberately skipping the computation is a contract violation.
- PERMITTED: a computation could be run diagnostically but the relation
  is decidable without it.
- FORBIDDEN: the would-be operands belong to different semantic
  quantities or periods, or the computation requires inference beyond
  simple addition/subtraction/multiplication/comparison or the frozen
  conversions in rule 2 and quantity-contract-v4.json.
- NOT_APPLICABLE: no computation is involved; values are stated
  directly or already appear verbatim in the evidence.

derived_quantity (required object when REQUIRED, else null):

- operands: array of canonical "VALUE UNIT" strings copied from
  evidence,
- operation: one of ADD, SUBTRACT, MULTIPLY, COMPARE,
- value: canonical computed "VALUE UNIT" string,
- provenance_span_ids: array of evidence span_ids used,
- quantity_identity: SAME or DIFFERENT (the derived value vs the
  claim's asserted value),
- role: usually AGGREGATE or DERIVED.

Aggregate rule (frozen): when the evidence states components A and B
and the claim asserts their total, quantity_identity may be SAME when
A and B belong to the same semantic aggregate, the arithmetic is
contract-permitted, and period/scope match. Then role = AGGREGATE,
value_source = AGGREGATED_FROM_SOURCE, and the deciding value is the
computed sum.

## 7. Compound claims and PARTIAL

Treat a claim as compound only when it contains distinct conjuncts
(assertions joined by "og", sentence split, or clearly independent
predicates). An "og" that coordinates parts of one proposition (for
example "hud og hares") is not two conjuncts. If the claim is compound
and the evidence establishes one conjunct while another is
unestablished, use PARTIAL. If every conjunct is established, ENTAILS;
if one is positively refuted, CONTRADICTS takes precedence over
PARTIAL only when the refuted conjunct is central to the claim;
otherwise PARTIAL.

## 8. Output rules

- Output exactly one JSON object per case with the fields required by
  annotation-contract-v4.schema.json. No extra fields, no prose, no
  Markdown fences.
- rationale: one sentence, maximum 300 characters, grounded in claim
  and evidence text only.
- If the evidence contains verbatim quoted computation or stated
  values, copy them exactly; never round or reformat values except by
  the frozen unit table.
