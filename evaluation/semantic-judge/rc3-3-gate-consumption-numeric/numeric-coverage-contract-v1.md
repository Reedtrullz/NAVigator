# Numeric coverage contract v1 (RC3.3)

Frozen before implementation.

## Quantity model

Every number-like token in claim or evidence is parsed into a
NUMERIC_SEMANTIC_QUANTITY with: value (or range bounds), unit,
comparator, quantity type, period/window, object binding (nearest
shared content-token context, max 6 tokens), aggregate/component role,
direct/derived derivation, and provenance substring.

Quantity types: AGE, DATE, DURATION, MONEY, PERCENTAGE, RATE, COUNT,
THRESHOLD, PERIOD, AGGREGATE, COMPONENT, OTHER.

## Comparators and interval semantics

Comparators: = , > , >= , < , <= , BETWEEN, APPROXIMATE, UNKNOWN.
Each comparator maps to an interval: '=' [v,v]; '>' (v,inf);
'>=' [v,inf); '<' (-inf,v); '<=' (-inf,v]; BETWEEN inclusive [lo,hi];
APPROXIMATE [0.9v, 1.1v] (documented approximation, frozen); UNKNOWN
never entails or contradicts (unresolved).

'18+' parses as >= 18, never bare 18. 'over N' -> > N; 'under N' ->
< N; 'minst N' / 'N eller eldre' / 'N eller flere' -> >= N;
'maksimalt N' / 'opp til N' -> <= N; 'mer enn N' -> > N; 'mindre enn
N' -> < N; 'mellom A og B' -> BETWEEN [A,B].

## Frozen comparator lattice (directional entailment)

Source interval S entails claim interval C iff S subset of C
(closed/open boundaries respected). Examples: source >= 20 entails
claim >= 18; source >= 18 does NOT entail claim >= 20; source > 18
does NOT equal '18 eller eldre' (>= 18); source '18 eller eldre'
entails claim 'minst 18'. Reverse direction never entails. The
machine-readable lattice is comparator-lattice.json in this
directory; it is authoritative and hashed.

## Quantity identity (required for ENTAILS/CONTRADICTS)

Two quantities are the same semantic quantity iff ALL hold:
quantity_type equal; unit compatible (MONTH=MONTH, YEAR=YEAR, NOK=NOK,
PERCENT=PERCENT, DAY=DAY, none=none); period equal or both absent;
object bindings share a content token or both are unbound; roles are
compatible (same role, or one side role-less STANDALONE).

Mismatched period (e.g. 'per maned' vs 'per ar') or mismatched role
(aggregate vs component) is NOT the same quantity:
NUMERIC_RELEVANT_BUT_UNRESOLVED, never CONTRADICTS.

## Direct vs derived

DIRECT: source states the quantity directly. DERIVED: the quantity
follows only from an explicit addition/subtraction chain present in
the evidence (component provenance preserved: the derived result
records its component values). No implicit unit or period conversion
is allowed in derivation.

## Aggregate vs component

Component quantities (parts) and aggregate quantities (totals) are
different quantities. Evidence parts 4 and 6 with total 10 never
conflict with a claim about the total or about one part, provided the
role labels resolve; a claim total is entailed by component evidence
only through an explicit derived sum (DERIVED).

## Dates and law references

Explicit calendar dates (dd.mm.yyyy, '1. januar 2024' style) are
quantity type DATE: equality comparison only, no comparator
entailment, no range semantics. Law and regulation references
('paragraf N', 'kapittel N', 'lov N', 'forskrift N', section-sign N)
are NEVER parsed as quantities of any type.

## Age vs period disambiguation

'N ar' is AGE in age context (under/over/eldre/aring/fyller/mellom
... og), else PERIOD only in deadline/stop/per-period context (the
frozen boundary._periods context rule), else not a quantity.

## CONTRADICTION

CONTRADICTS requires: same semantic quantity identity (all five
fields), both comparators known, and disjoint intervals. Differing
numbers on non-identical quantities never contradict.

## Coverage obligation

A numeric relation proof may use a number only when source and claim
quantities match on the identity fields above. Otherwise:
NUMERIC_RELEVANT_BUT_UNRESOLVED. This state blocks R25/R23 numeric
auto-support in the relation layer.
