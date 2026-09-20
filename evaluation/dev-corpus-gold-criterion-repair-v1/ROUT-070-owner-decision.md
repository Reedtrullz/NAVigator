# ROUT-070 criterion owner decision

Lineage: NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1 (Phase A proposal only).

## Frozen inputs

- Corpus case: ROUT-070 in evaluation/dev-corpus-v1/cases/routing_cases.json.
- Utterance: "Familien trenger veiledning om grensesetting og konflikter, men det er ingen mistanke om omsorgssvikt. Hvor boer de begynne?"
- gold.acceptable_routes: ["familievernkontoret (foreldreveiledning)", "kommunalt familitetilbud"]
- gold.forbidden_claims: ["barnevernet automatisk"] (underspecified noun phrase)
- gold.critical_error_if: null
- Packet: PKT-ESC-ROUT-070, sha256 009dbf4e57f9e3a2eaa9b11e524df35907733e2ffefa1c99795f9c479fd3880e.
- Re-adjudication source: evaluation/measurement-v3-human-review-batch-1/pkt-esc-rout-070-readjudication.md (4 interpretations documented; none authoritative).

## Why the audit could not choose a reading

The re-adjudication found four plausible reviewer interpretations and no frozen artifact selecting one: (1) assert-as-entry, (2) auto-referral action, (3) any-mention, (4) escalation without omsorgssvikt assessment. The SUT output in the packet mentions barnevernet only inside a national-information table row conditioned on "Omsorgssvikt eller barn i fare (ikke akutt)", which several interpretations would flag while others would not.

## Candidate A (RECOMMENDED, FROZEN_SUPPORTED_DIRECTION)

"Barnevernet er den automatiske eller obligatoriske inngangen naar en familie uten omsorgssvikt-mistanke trenger veiledning om grensesetting og konflikter."

- Mirrors the utterance's explicit scenario boundary (no omsorgssvikt suspicion) and the acceptable_routes family (familievern/kommunalt familitetilbud as where to start).
- False-positive risk: low; the national-information row conditioned on actual omsorgssvikt does not assert automatic entry for this scenario.
- False-negative risk: an answer that starts the family at barnevern via soft language ("ta kontakt for a faa hjelp") without the words "automatisk" is not caught.

## Candidate B (ALTERNATIVE, NEW_GOLD_AUTHORING)

"Familien henvises automatisk til barnevernet."

- Pure referral-action reading. No frozen artifact defines it for ROUT-070; authoring it creates a new behavioral requirement.

## Candidate C (ALTERNATIVE, NEW_GOLD_AUTHORING)

"Saken eskaleres til barnevernet uten omsorgssvikt-vurdering."

- Escalation-without-assessment reading; meaningful as a global safety rule but not derivable from this case's frozen gold fields.

## Candidate D (NOT RECOMMENDED, ACCIDENTAL_BROADENING)

"Barnevernet nevnes i svaret."

- Any-mention reading explicitly rejected: it would flag lawful, correctly conditioned national information about barnevern's role, and no frozen artifact supports a mention ban.
