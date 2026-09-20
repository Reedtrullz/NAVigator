# W3-RC-A Route Object Contract (frozen)

## Four object types (spec section 8)

| Type | Carrier | May become route target? |
|---|---|---|
| Knowledge record | 'K-*' record, claim = verbatim source span | No (input only) |
| Evidence | 'E-*' id bound to record/claim | No (support only) |
| Service candidate | discovery service object / structured table identity | Yes, structured |
| Route proposition | RouteCandidate dict in ctx["_s6_routes"] | Is the route |

A route proposition is the only object the renderer may turn into a
user-facing route line. Knowledge text is never copied into the route
target field.

## Route target identity (spec section 9)

service_type is minted through exactly two gates:

1. Structured path (W3-RC-A): the claim is a verbatim (possibly
   truncated-prefix) row of a markdown table whose header row declares a
   service-identity column ("instans", "tjeneste", "service" - first
   column). The claim must locate exactly one row in the frozen source
   document (repo-root-relative path from source_reference); the name
   is the first cell of that row. Fail-closed: unreadable source,
   ambiguous location, non-identity header, or invalid label yields no
   structured target.
2. Lexical fallback (RC-07, preserved): quoted 'name' or bold
   **name** spans only, digit-free, label-valid.

Deliberately NOT an identity column: "tilbud" - doc 25 commune tables
use "| Kommune | Tilbud |" headers where first-column values are
municipality names.

## Route proposition minimum (spec section 10)

Existing RouteCandidate fields carry: active track (track_domain),
destination (service_type), access path (access_model, self_referral),
applicable conditions (age_eligible, scenario_relevant, scope),
epistemic state (route_state), and supporting evidence/provenance
(evidence_refs, provenance_refs). No schema expansion; existing
representation is sufficient.

## Access path (spec section 11)

self_referral is a lexical hint read from the claim span itself:
positive self-contact markers ("uten henvisning", "direkte kontakt",
"drop-in", ...) yield True; a bare "henvisning*" marker yields False;
nothing yields UNCLEAR. Negative markers outrank the bare referral
substring so "ingen henvisning" is not misread. Access uncertainty
never discards an otherwise useful route: UNCLEAR maps to
access_verified = UNRESOLVED in the existing dimension model.

## Conditions (spec section 12)

Age, severity, and scope flow through existing dimension fields only
(age_eligible, target_population, scope). No benchmark-specific
eligibility logic was added.

## Multiple routes (spec section 13)

Every passing record mints at most one route; multiple records and
multiple discovery services each keep their own route. Deterministic
ordering stays with the frozen planner sort.

## Track scoping (spec section 14)

Structured extraction runs only over records already scoped to their
track (RC-08 binding preserved). track_domain is mandatory on every
route; ROUTE_WITHOUT_TRACK_BINDING is a hard zero-gate.

## Provenance (spec section 15)

National routes keep evidence_refs = [record evidence_id] and
provenance_refs = [P-Knnn] (numbering after discovery services, full
record order). Municipal routes keep E-DISC-nn + discovery URL.
Provenance refs are resolvable against _provenance_records.

## Known ceilings (documented, not fixed)

- self_referral only reads markers inside the claim span. A row-prefix
  claim cut before the access cells mints the route with UNCLEAR
  access instead of inventing access semantics.
- Header-gate whitelist is frozen to the three identity words; other
  identity-ish headers would need a doctrine amendment.
- Structured extraction is lexical row matching; it does not understand
  table semantics beyond the identity-header gate.
