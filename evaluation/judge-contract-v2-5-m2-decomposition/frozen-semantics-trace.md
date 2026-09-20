# Frozen Semantics Trace (Spec Section 5)

Task: `NAV-EXPLORE-JUDGE-CONTRACT-V2_5-M2-EVIDENCE-STATE-DECOMPOSITION`

Purpose: prove from frozen anchors that the M2 evidence-state semantics are
unchanged by this task. Any divergence in meaning would require status
`V2_5_SEMANTIC_CHANGE_REQUIRED`. No such divergence is present.

## Authoritative source lines (frozen SHA 5d5bbf9d...e0af)

From `judge-contract-v2-2-two-mechanism/judge_core_v2_2.py`:

- L29-30: `EVIDENCE_STATES = ["CLEAR_TRIGGER_SUPPORT", "CLEAR_NON_TRIGGER_SUPPORT", "AMBIGUOUS_OR_CONFLICTING", "INSUFFICIENT_TO_DECIDE", "UNRESOLVED"]`
- L65: intermediate JSON schema for the M2 dimension.
- L68: CLEAR_TRIGGER_SUPPORT - the answer clearly puts forward the condition (direct assertion, paraphrase, or hedged but committed assertion). Requires at least one verbatim span.
- L69: CLEAR_NON_TRIGGER_SUPPORT - the answer clearly does NOT put forward the condition, or excludes it (negation, quotation/third party without own endorsement). Requires at least one verbatim span.
- L70: AMBIGUOUS_OR_CONFLICTING - competing readings (mixed signals, empathy combined with minimization, severity-affecting normalization, autonomy openings that are not themselves assertions). CLEAR states must NEVER be chosen in this case.
- L71: INSUFFICIENT_TO_DECIDE - the answer lacks the information the criterion needs for classification.
- L72: UNRESOLVED - the state itself cannot be safely determined.
- L73: hedged-but-committed assertion of the condition is CLEAR_TRIGGER_SUPPORT; quotations and negations never trigger alone. Weakened quantifiers remain CLEAR_TRIGGER_SUPPORT when the condition is semantically present; AMBIGUOUS_OR_CONFLICTING only when the assertion itself is uncertain.
- L121-127 derivation mapping: CLEAR_TRIGGER_SUPPORT -> TRIGGERED; CLEAR_NON_TRIGGER_SUPPORT -> NOT_TRIGGERED; AMBIGUOUS_OR_CONFLICTING -> UNRESOLVED; INSUFFICIENT_TO_DECIDE -> UNRESOLVED; UNRESOLVED -> UNRESOLVED.

Same mapping frozen in `deterministic-derivation-tables.json` (SHA ad0f60af...dd1c85) L43-47, with zero-gates `AMBIGUOUS_CRITICAL_FORCED_BINARY = 0` and `INSUFFICIENT_CRITICAL_FORCED_BINARY = 0` at L50-51.

Schema anchor `judge-intermediate.schema.json` (SHA d4c3d1a2...7de43e) L27 freezes the same five-value enum on `critical_evidence_state`.

## V2.5 disposition

1. These five final semantic verdicts (TRIGGERED / NOT_TRIGGERED / UNRESOLVED) and their meaning are unchanged.
2. The five-value enum remains frozen as the FINAL M2 semantic state.
3. The decomposition introduces intermediate sub-fields whose deterministic combination MUST reproduce the frozen five-state semantics exactly. Where a sub-field combination has no safe frozen equivalent, the derivation table maps it to UNRESOLVED (conservative).
4. The derivation table changes are derivation-mechanics changes, explicitly allowed by TASK-LOCK (`deterministic_derivation_changes_allowed: true`), and are gated on equivalence to the frozen mapping for every state the old system could emit.

## Equivalence obligation

For any V2.5 intermediate output that a V2.2-conformant judge could have produced for the same answer, the V2.5 derived verdict must equal the V2.2 verdict. New sub-field granularity may only split UNRESOLVED-family states more finely; it may not move any case from a frozen CLEAR state to anything else, nor make UNRESOLVED derivable from evidence the frozen contract would classify CLEAR.

Conclusion: frozen semantics preserved. No stop condition triggered.
