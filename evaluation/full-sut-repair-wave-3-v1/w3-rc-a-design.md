# W3-RC-A Design (frozen candidate 1)

## Change surface

One runtime file: runtime/sut/phase2/routes.py. No planner, renderer,
finalize, schema, or safety changes were mechanically necessary: the
existing planner already emits PRIMARY_ROUTE/SECONDARY_ROUTE blocks for
every evaluable route and the renderer already consumes structured
routes. The Wave-2 failure was upstream: no structured route object was
minted from the primary national evidence tables.

## Mechanism

build_national_route_candidates now tries structured extraction before
the RC-07 lexical fallback:

1. _structured_service_name(claim, source_path) - verbatim row
   location in the source doc, separator+header scan upward, identity
   header gate, first-cell name, label validity. Fail-closed on every
   ambiguity.
2. On hit, self_referral = _self_referral_from_row(claim) (positive
   self-contact markers, negative/positive outranking, UNCLEAR default).
3. Fallback stays the RC-07 quoted/bold path, now additionally guarded
   by the shared metadata-label rejector.

Header whitelist is frozen at {"instans", "tjeneste", "service"}.
"tilbud" is deliberately excluded (doc 25 commune tables would mint
municipality names).

## Safety invariants preserved

- Acute/suppressed inputs skip S3 entirely, so no S4 records exist and
  no national routes can mint (test_06).
- RC-08 track scoping unchanged; structured extraction runs on
  per-track records only.
- RC-07 quoted/bold semantics unchanged (test_route_targets.py passes
  unmodified).

## Alternative rejected

Extending the lexical fallback with more markers (e.g. bare service
words) was rejected: it re-opens the RAW_KB_FRAGMENT gate the RC-07
tests pin shut. Table identity is the only structurally grounded new
path.
