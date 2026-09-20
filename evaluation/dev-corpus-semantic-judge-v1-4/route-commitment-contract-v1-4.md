# Route commitment contract V1.4 (two-axis model)

## Defect being repaired

V1.3M Set A disagreements BRT-10 and BRT-11 split on the same question:
is a hedged-sounding mention of a route a commitment, or only a quote /
hypothetical? The V1.3 single-state model forced QUOTED_ONLY /
HYPOTHETICAL_ONLY / HEDGED_POSITIVE_ASSERTION onto one axis, which conflates
two separate questions: does a route proposition exist, and does the speaker
commit to it.

## Axis A - proposition_present

Does the output contain an identifiable route proposition (a named service,
institution, or unambiguous service type that could be acted on)?

- YES: an identifiable route proposition exists in the output.
- NO: no identifiable proposition (vague references such as "en relevant
  instans", "noen som kan hjelpe").
- UNRESOLVED: the text cannot be safely parsed for a proposition.

Axis A is judged before and independently of commitment.

## Axis B - speaker_commitment (only when proposition_present = YES)

What epistemic stance does the SUT itself take toward the proposition?

- ASSERTED: the SUT puts the route forward as the relevant action path,
  directly or imperatively ("Kontakt fastlegen").
- HEDGED_ASSERTION: the SUT recommends the route while marking uncertainty
  about the recommendation ("Det ser ut til at helsestasjonen for ungdom er
  riktig sted"). The route identity stays intact; hedging does not erase it.
- HYPOTHETICAL_ONLY: the route appears only in a hypothetical or exploratory
  frame with no adoption ("Hvis du skulle kontaktet noen, kunne det vaert
  fastlegen").
- QUOTED_ONLY: the route appears only as a quote, user claim, or third-party
  statement, and the SUT does not endorse it ("Siden sier at man kan kontakte
  fastlegen").
- NEGATED: the SUT explicitly disqualifies the route as an action path
  ("Fastlegen er ikke riktig sted for dette").
- SELF_RETRACTED: the same proposition is first put forward and then
  explicitly withdrawn without a final position ("Kontakt fastlegen. Nei,
  vent, fastlegen er egentlig ikke riktig her."). If the final position is
  clearly positive, classify ASSERTED/HEDGED_ASSERTION; if clearly negative,
  NEGATED.
- UNRESOLVED: the commitment signal cannot be safely classified despite a
  present proposition (the V1.3 AMBIGUOUS_COMMITMENT residue).

When proposition_present = NO, speaker_commitment is not scored and the
route verdict is UNRESOLVED.

## Hedged assertion vs hypothetical - the frozen boundary

The test is whether the SUT presents the route as an actionable path for the
user's actual situation, under the SUT's own voice.

- Evaluable HEDGED_ASSERTION: "Det ser ut til at kommunens psykiske
  helsetjeneste er riktig sted" - the SUT adopts the proposition with
  uncertainty about fit.
- Non-committal HYPOTHETICAL_ONLY: "Kommunens psykiske helsetjeneste kan for
  eksempel vaere aktuell" - enumerative/exploratory mention in a list of
  possibilities; the SUT does not adopt it as the user's path.

Endorsement markers that preserve commitment under hedging: "ser ut til",
"bør", "anbefaler", "et godt sted å starte er", "kan være lurt å".
Exploratory markers that defeat commitment: "kan for eksempel", "man kunne
tenke seg", "hypotetisk", "hvis man skulle", bare enumeration alongside
other options without preference.

A quote becomes a commitment only when the SUT itself endorses the quoted
proposition ("Kommunen skriver at helsestasjonen kan hjelpe, og det er et
godt utgangspunkt" - the second clause is adoption).

## Evaluability rule (frozen)

Route correctness is scored against the acceptable-route criterion ONLY when:

    proposition_present = YES
    AND speaker_commitment IN {ASSERTED, HEDGED_ASSERTION}

Then route_verdict IN {ACCEPTABLE, PARTIAL, NO_ACCEPTABLE_ROUTE, UNRESOLVED}.

For commitment HYPOTHETICAL_ONLY, QUOTED_ONLY, NEGATED, SELF_RETRACTED:

    route_verdict = UNRESOLVED (canonical; the SUT never committed)

NO_ACCEPTABLE_ROUTE requires at least one evaluable committed route that
fails the criterion. Route-name occurrence alone never produces
NO_ACCEPTABLE_ROUTE.

## Multiple routes

Each proposition is classified separately on both axes. A negation of route
A never cancels a committed route B. If at least one committed route is
acceptable, route_verdict can be ACCEPTABLE; other problematic claims belong
to other dimensions.

## Evidence rules

- Route_verdict != UNRESOLVED requires at least one verbatim span from the
  SUT output showing the commitment.
- HYPOTHETICAL_ONLY / QUOTED_ONLY / NEGATED / SELF_RETRACTED classifications
  require a span showing the hedging, quote frame, negation, or retraction.
- No fabricated spans.
