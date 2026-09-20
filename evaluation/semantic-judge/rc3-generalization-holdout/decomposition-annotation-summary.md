# Compound Decomposition Annotation

- CORE compound cases: 52; canonical atoms: 119 (all with atom_id,
  text, relation_to_parent=CONJUNCT, evidence_span_ids,
  required_inference, per-atom semantic target, top-level aggregation
  target).
- Decomposition happened at authoring time (claim-logical), before any
  evidence judgment; pass 2 independently decomposed and labeled atoms.
- Pre-adjudication agreement: atom count 52/52 (100%); atom semantic
  case-level 46/52 (88.5%); atom-level 114/119 (95.8%).
- The 5 compound disputes were adjudicated against the evidence; 4
  pass-2 atom corrections adopted (§-number mismatch, age-limit value,
  "under 14 maneder" vs "opptil 3 aar", one per-atom override where
  wholesale adoption contradicted the noted evidence). Final atom keys
  are complete for all 52 cases; no case has missing or extra atoms.
- Top-level aggregation for every compound follows the frozen runtime
  convention (uniform atoms keep class; any mix -> PARTIALLY_SUPPORTED).
