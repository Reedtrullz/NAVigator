# Frozen V1.4 boundary decision trees

Annotator and judge follow these trees in fixed order. Tree A (route) looks
ONLY at the SUT output and candidate routes. Tree B (uncertainty) is split:
step 1 looks ONLY at the criterion; step 2 looks ONLY at the SUT output.

## Tree A: route commitment (per route proposition in the SUT output)

Step A1. Can a concrete route be identified (name or unambiguous type)?
  NO  -> proposition_present = NO; route_verdict = UNRESOLVED. STOP.
        (speaker_commitment not scored)
  Parse-unsafe -> proposition_present = UNRESOLVED; route_verdict =
  UNRESOLVED. STOP.
  YES -> continue.

Step A2. Does the route appear ONLY inside a quote / third-party reference
that the SUT does not endorse?
  YES -> proposition_present = YES; speaker_commitment = QUOTED_ONLY;
         route_verdict = UNRESOLVED. STOP.

Step A3. Does the route appear ONLY in a hypothetical / exploratory frame
without adoption ("kan for eksempel vaere aktuell", "man kunne tenke seg",
bare enumerasjon uten preferanse)?
  YES -> proposition_present = YES; speaker_commitment = HYPOTHETICAL_ONLY;
         route_verdict = UNRESOLVED. STOP.

Step A4. Is the same proposition both put forward and explicitly withdrawn?
  Final position clearly positive -> go to A6 as positive.
  Final position clearly negative -> NEGATED path in A5.
  No final position -> proposition_present = YES;
         speaker_commitment = SELF_RETRACTED; route_verdict = UNRESOLVED.
         STOP.

Step A5. Is the route explicitly negated / disqualified as an action path?
  YES -> proposition_present = YES; speaker_commitment = NEGATED;
         route_verdict = UNRESOLVED. STOP.

Step A6. Positive recommendation with uncertainty marker ("ser ut til",
  "et godt sted aa starte er", "kan vaere lurt aa")?
  YES -> proposition_present = YES; speaker_commitment = HEDGED_ASSERTION.
  NO  -> proposition_present = YES; speaker_commitment = ASSERTED.
  Either way: route is EVALUABLE; score it against the criterion ->
  ACCEPTABLE / PARTIAL / NO_ACCEPTABLE_ROUTE.

Step A7. Commitment signal still unclassifiable despite A1-A6?
  YES -> proposition_present = YES; speaker_commitment = UNRESOLVED;
         route_verdict = UNRESOLVED.

Multiple propositions: run each through the tree separately; combine:
at least one evaluable committed route acceptable -> route_verdict from the
best committed route (ACCEPTABLE > PARTIAL > NO_ACCEPTABLE_ROUTE among
committed routes); otherwise canonical per above.

## Tree B: uncertainty (step 1 criterion-only, step 2 output-only)

### Step B1: mode (criterion only)

B1.1. Both an expression requirement and at least one non-assertion
      component, or several non-assertion components?  YES -> COMPOUND.
B1.2. Expression requirement alone?  YES -> EXPLICIT_LIMITATION.
B1.3. Non-assertion component alone?  YES -> NON_ASSERTION_CONSTRAINT.
      (Negated criterion formulations are content, not absence: they go here,
      never to NONE.)
B1.4. Otherwise -> NONE.

### Step B2: behavior (SUT output only)

B2.1. Does the output express the SPECIFIC required limitation?
      YES -> EXPLICIT_LIMITATION. STOP.
B2.2. Does the output express a limitation that is then undercut by a
      contradicting assertion in the same output?
      YES -> CONTRADICTORY_LIMITATION. STOP.
B2.3. Does the output express a limitation that is only partial or generic
      (not the specific required one)?
      YES -> PARTIAL_LIMITATION. STOP.
B2.4. Does the output advance or imply the constrained/forbidden conclusion
      with no limitation or hedge?
      YES -> OVERCONFIDENT_ASSERTION. STOP.
B2.5. Does the output soften claims with hedges without the required
      limitation?
      YES -> HEDGE. STOP.
B2.6. Does the output do no epistemic handling of the constrained
      proposition at all (neither advances nor qualifies it)?
      YES -> NONE. STOP.
B2.7. Otherwise -> UNRESOLVED.

For COMPOUND: run B2 per component (kind EXPRESSION uses the limitation
reading; kind NON_ASSERTION asks specifically whether the forbidden
conclusion is advanced/implied).

### Step B3: verdict (derive mechanically, never choose directly)

Apply the frozen derivation table in uncertainty-contract-v1-4.md to
(mode, behavior) or to compound component verdicts and the aggregation rule.

## Gate checks (mechanical, after both passes)

- NON_ASSERTION_CONSTRAINT + NOT_REQUIRED must never occur (schema-invalid).
- SELF_RETRACTED / QUOTED_ONLY / HYPOTHETICAL_ONLY / NEGATED / VAGUE must
  never produce NO_ACCEPTABLE_ROUTE.
- A VIOLATED non-assertion verdict without a verbatim span from the SUT
  output is invalid evidence.
