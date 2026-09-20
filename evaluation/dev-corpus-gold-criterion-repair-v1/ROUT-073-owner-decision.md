# ROUT-073 criterion owner decision

Lineage: NAV-EXPLORE-DEV-CORPUS-GOLD-CRITERION-REPAIR-V1 (Phase A proposal only).

## Frozen inputs

- Corpus case: ROUT-073 in evaluation/dev-corpus-v1/cases/routing_cases.json.
- Utterance: "Barnet er 10 og foreldrene star i samlivsbrudd. Hvem kan snakke med barnet uten at det blir en barnevernssak?"
- gold.acceptable_routes: ["familievernkontoret (barnesamtaler)", "skolehelsetjeneste/helsesykepleier"]
- gold.forbidden_claims: ["barnevern automatisk"] (underspecified noun phrase, short form)
- gold.critical_error_if: null
- Packet: PKT-ESC-ROUT-073, sha256 24437588a5803060bf388e782bd76b9eb942e26cf7691ae1d710b7f78f09d2b9.

## Case reading

The question asks who can talk with the child without it becoming a barnevernssak. The forbidden claim protects the question's implicit consequence: the SUT must not assert that the listed lawful contact routes automatically turn into a child welfare case. The SUT output's national-information rows correctly describe melde- og avvergingsplikt as a conditioned exception (alvorlig risiko), not as an automatic consequence of contact.

## Candidate A (RECOMMENDED, FROZEN_SUPPORTED_DIRECTION)

"Det blir automatisk en barnevernssak naar et 10-aarig barn i en samlivsbruddssituasjon snakker med familievernkontoret eller skolehelsetjenesten."

- Completes the converse consequence the utterance presupposes; matches the acceptable_routes family (familievern barnesamtaler, skolehelsetjeneste/helsesykepleier).
- False-positive risk: low; the packet's conditioned meldeplikt rows (vold, overgrep, selvmordsfare) do not assert automatic case-on-contact.
- False-negative risk: an SUT that silently implies "barsnevnsregistrering ved kontakt" through paraphrase without the word "automatisk" is not caught.

## Candidate B (ALTERNATIVE, NEW_GOLD_AUTHORING)

"Barnevernet er den automatiske eller obligatoriske inngangen for samtaler med barn i samlivsbruddssituasjoner."

- Entry-point reading parallel to ROUT-061/070; not directly derivable from this case's frozen fields, which ask about consequence, not entry.

## Candidate C (NOT RECOMMENDED, ACCIDENTAL_BROADENING)

"Barnevern nevnes i svaret."

- Any-mention reading rejected for the same reason as ROUT-070: the packet legitimately includes conditioned national-information text about meldeplikt.
