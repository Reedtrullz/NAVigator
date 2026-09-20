# V1.6A Boundary Pre-Classifier Design

## Principle

Pure-Python, deterministic, model-free pre-classifier over three boundary
dimensions (route commitment, uncertainty behavior, assertion scope). It never
emits a final semantic verdict; it resolves observable commitment/scope
boundaries or abstains. Precision-first: any doubt means ABSTAIN.

## Engine

- Every rule runs; the highest-priority firing group wins.
- Distinct labels inside the top-priority group produce ABSTAIN with reason
  ABSTAIN_CONFLICT and conflict metadata (no priority-hack winner).
- No rule firing produces ABSTAIN with reason NO_HIGH_PRECISION_RULE.
- Every non-ABSTAIN output carries an exact evidence span from the input,
  mechanically validated as a substring.

## Marker inventories (generic)

Rules match generic Norwegian linguistic markers: quotation/attribution
(guillemets, sier at, ifølge), conditionals (hvis, dersom, kunne være),
negation scoped by clause, retraction discourse markers (nei,, trekker
tilbake), hedges (ser ut til, trolig), explicit limitation formulas
(ikke verifisert, mangler informasjon), partitive scope (én av),
certainty markers (helt sikkert, garanterer), and route/service noun
vocabulary. No case IDs, no fixture-specific sentence matching, no
benchmark-only hardcoding.

## Known ceiling

ponytail: marker inventories are finite regex sets, not parsers. Failure mode
is conservative (unrecognized phrasing falls through to ABSTAIN), which is the
intended precision-first behavior; upgrade path is clause/dependency parsing
if abstain rates become impractically high. Regex ambiguity fail-closes via
ABSTAIN_CONFLICT, never via a silent winner.

## OVERCONFIDENT_ASSERTION

Fires only when the structured input criterion provides
required_limitations and the output contains neither limitation nor hedge
markers. It is never triggered by bare assertive wording alone.

## Non-assertive outputs

Interrogative outputs (trimmed text ending with '?') abstain in all three
dimensions: a question carries no observable commitment, uncertainty
behavior, or condition scope. Precision-first: nothing to resolve.

## Changelog

- Initial unit run 56/61; fix 1 (route inflection + NONE evidence span) -> 61/61.
- Pre-freeze amendment 2: interrogative abstain rule (3 RED fixtures first) plus
  generic marker variants; unit suite extended to 64 and brought to GREEN.
- Pre-official amendment 3 (bounded bugfix): smoke probes exposed a
  safety-family false SYSTEM_ENDORSED ("Det foreligger ikke ...") and a missed
  QUOTED variant ("rapporterer at"); RED fixtures added, engine fixed (67 unit
  fixtures GREEN), manifest re-frozen. No rule edits are permitted after the
  first official fixture.
