# Measurement Sensitivity Non-Fixes (spec section 4)

Wave-2 measurement quirks that W3-RC-A deliberately does NOT code
around:

## PREMATURE_ABSENCE scorer quirk

The Wave-2 scorer treats certain absence verdicts as premature. RC-A
does not change abstention semantics or route states to convert those
criteria. Route states still downgrade only; absence of proof of
access is still UNRESOLVED, not absence of service.

## "garanti" keyword scorer quirk

The scorer's guarantee keyword handling is measurement-side. No runtime
string is added or removed to satisfy it, and no route wording was
tuned toward scorer keyword behavior.

## Truncation / span-shape sensitivity

Retrieval spans are verbatim lines (or <=400-char prefixes). Structured
row matching works on any prefix that still locates exactly one row, so
route identity survives prefix truncation, but self_referral reads
only markers inside the span. This is a documented ceiling (see
route-object-contract.md), not tuned against any expected label.
