# Canonical Decomposition Contract (DECOMPOSITION_V1)

Input: claim text. Output: ordered canonical atoms with stable IDs:
{"atoms": [{"atom_id": "A1", "text": "...", "relation_to_parent": "CONJUNCT"}]}

Splitting is claim-logical only (spec 21), applied BEFORE evidence judgment
(spec 20) and never driven by evidence availability or expected labels:
- sentence boundaries in the claim
- conjunctions "og" / "og samtidig" joining independent propositions
  (test: each side must contain its own verb/predicate stem)
- list structures ("bade X og Y", comma/en-lists with repeated predicates)
- actor changes across a boundary
- temporal/stage changes ("etter at", "forst ... sa", "deretter")
- condition clauses ("hvis/dersom/bare dersom" as separate atom when they
  form an independent proposition; kept attached when they qualify exactly
  one neighboring proposition and carry no standalone predicate)
- negative compounds: negation scoped to one conjunct splits with it

"og" that does NOT join two propositions (shared predicate, one
proposition: "inntekt og formue tas med") does NOT split (spec 22 case).

Atom IDs are assigned by deterministic left-to-right order (A1, A2, ...);
same claim always yields the same decomposition (stability 100% target).
relation_to_parent: CONJUNCT | CONDITION | TEMPORAL_STAGE | NEGATED_CONJUNCT.

Compound pipeline: every atom runs the full proof/evidence pipeline
individually (spec 25); top-level aggregation is the frozen evaluation
contract's deterministic rules (spec 26). The reviewer may mark individual
atoms for review but cannot add, drop, or merge atoms (spec 27).

