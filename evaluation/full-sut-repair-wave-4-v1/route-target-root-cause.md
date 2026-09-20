# Route-Target Root Cause (R0 = 84)

## Observed failure

Wave 3 combined measurement: 84 of 108 route rows landed in R0 (no
structured route target matches the expected route concept). All R0 rows
come from national-track claims routed through build_national_route_candidates.

## Live probe evidence (session, frozen routes.py 29b0bd44...d7fa)

Source doc 25-kommunale-psykiske-tjenester-barn-unge.md:

- Headings: "### Skolehelsetjenesten", "### Helsestasjon for ungdom (HFU)",
  "### Helsestasjon for barn 0-5 ar", "## 6. Kommunale psykisk helse- og
  familieteam".
- Retrieved R0 claims are prose/justification lines under those headings.
  Their claims carry no quoted/bold segment and are not table rows.
- _national_service_name returns None for every one of them (no quote/
  bold). _structured_service_name returns None (not a table row).
- The claim's nearest enclosing heading IS the service name in the
  observed pattern, with numeric section prefixes and "(verifisert)"/
  "(delvis verifisert)" suffixes to strip.

## Mechanism

_iter_spans (knowledge.py) chunks source docs into lines and <=400-char
sentence pieces. Retrieval scores spans lexically; most winning spans are
prose, not the quoted-name or identity-table lines that the two existing
extraction paths require. Result: no candidate is minted for the majority
of national records. This is an extraction-coverage miss, not a scoring
or routing defect.

## Fix direction (Wave 4 Phase A)

Generic heading-context rescue inside build_national_route_candidates:
after quote/bold/table extraction fails, resolve the claim nearest
enclosing markdown heading in the frozen source doc via verbatim
substring match of the claim (fail-closed when ambiguous or missing),
strip section prefixes and verification suffixes, and validate the
resulting label through the same service-identity gates plus a generic
non-service marker list. Digits remain allowed on the heading path only
("Helsestasjon for barn 0-5 ar" is a legitimate target).

## Out of scope

RC-04/RC-06, no_route_asserted presentation, certainty-marker fixes, any
gold-aware target preference.

