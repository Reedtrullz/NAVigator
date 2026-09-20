# Repair Hypothesis - Frozen Before Implementation

**Task:** NAV-EXPLORE-DEV-CORPUS-SEMANTIC-JUDGE-V1_6A2-ROUTE-GROUNDING-REPAIR
**Frozen:** before any production code change in this lineage
**Evidence basis:** root-cause-trace.json (ADV-11, BURNED_DIAGNOSTIC_ONLY) +
working-counterexamples.json (contract section 8)

## Generalized mechanism hypothesis

Route commitment may only be grounded when the route/service noun being
classified is locally associated, within the same clause or proposition scope,
with the assertion / hedge / negation / retraction operator that licenses the
deterministic label. A commitment cue located in one clause must not ground a
service noun in another clause merely because both occur in the same output.

The ADV-11 failure is an instance of this mechanism: the assertion operator
("riktig inngang") lives in clause 0 together with the inventory noun
"fastlege", while clause 1 contains the out-of-inventory noun "ungdomssenteret"
with only vague capability wording ("kan hjelpe"). The frozen engine evaluates
all operators output-wide and suppresses the unknown-noun guard whenever any
inventory term exists, so the ungrounded second proposition becomes invisible
and the whole output inherits ASSERTED from clause 0.

## Design rule (preregistered, contract section 10)

Deterministic route classification requires, within the same clause/proposition
scope:

1. a route/service candidate (inventory term or independently grounded
   service noun), AND
2. a licensing commitment operator, AND
3. a valid grounding relation between them.

Cross-clause proximity alone is insufficient. If a clause contains a service
noun that cannot be locally grounded, the output-level verdict must be ABSTAIN
(conservative direction), because at least one route proposition in the output
is unresolved.

## Locality sub-principles (contract sections 13-16)

- **Negation locality:** a negation marker scopes only over the proposition
  whose clause contains it; it must not negate a route noun in another clause
  (and must not be ignored when sharing a clause with the noun).
- **Retraction locality:** a retraction/correction attaches to the proposition
  being withdrawn, not to every route noun in the output.
- **Quote locality:** a route noun inside quotation scope is not adopted as
  system commitment because assertion markers exist outside the quote.
- **Hedge locality:** a hedge marker only demotes the proposition it modifies;
  it does not hedge a bare assertion in a neighboring clause.

## Ambiguous grounding (contract section 12)

When two or more route nouns compete for the same operator and local grounding
cannot be decided with high precision, the classifier must ABSTAIN rather than
pick the nearest noun for coverage.

## Implementation direction (minimal, no new dependencies)

Segment the output into clauses at sentence boundaries and coordinating
conjunctions ("men", "og" between propositions where evidence supports it),
compute operator markers per clause, and require clause-local association
between candidate noun and operator for every deterministic rule. Fire a
new conservative ABSTAIN when any clause holds a service noun that cannot be
locally grounded by any high-precision mechanism. Keep V1.6A.1 behavior
(out-of-inventory guard, quote/hypothetical guards) for single-proposition
outputs intact.

## Expected RED evidence

At least one new dev fixture with an operator in one clause and an ungrounded
service noun in another clause will fail against the frozen engine (expected
ABSTAIN, engine emits a deterministic label), demonstrating the mechanism
reproduced on fresh text before any patch.

## What this hypothesis does NOT cover

- Critical/uncertainty dimension semantics (out of scope, contract section 2).
- Full NLP parsing; clause segmentation remains minimal and deterministic
  (punctuation + explicit conjunctions), fail-closed on ambiguity.
- Any change to route label vocabulary or scoring rules.
