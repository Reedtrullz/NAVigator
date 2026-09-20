# Route Fragment Analysis (Wave 2)

20 cases emitted structured routes (24 entries, 14 distinct labels; 15/24 entries junk-like per Wave-2 mechanical count). Among the 108 evaluated route criteria, 19 criteria fall in R1_INVALID_ROUTE_OBJECT: structured objects exist, but every label is a non-actionable fragment.

## Observed label patterns (diagnostic, general)
- Section-heading fragments: "Hensikt" (x6 across cases), "Status", "Meldeplikt", "Praktisk betydning for skolehelse".
- Non-routes: "Ikke en ensartet tjeneste." (x2), "ikke hensiktsmessige" (x2) - negated/descriptive statements, not service propositions.
- Bare references: "URL" (x2), "Baerum" (place name), service-family fragments without an access path ("kommunal helsetjeneste", "Psykisk helseutredning", "Diagnostisk utredning (nevropsykiatrisk)", "Barn kan motta samtaler").
- SAF-012 labels ("Foreldreansvar bestemmer samtykke", "Akutt fare") are topic statements, not actionable contact/referral propositions.

## Mechanism
Labels appear to be extracted from document headings/section names or short status phrases rather than constructed as route propositions (target + access path + condition). Evidence binding is keyed by R-codes, not by route label, so label->evidence resolution is 0/20 (Wave-2 RC-07 analysis).

## ROUT-072 / ROUT-083 (named per spec as diagnostic examples only)
- ROUT-072 labels: ["Hensikt", "Praktisk betydning for skolehelse", "URL"] -> heading serialization + wrong target extraction (headings and a URL treated as routes).
- ROUT-083 labels: ["URL"] -> evidence fragment leakage into the route label field.
No runtime repair may special-case these IDs; the general defect is heading/fragment extraction inside route construction.

## Implication
R1 is eliminated only by constructing real propositions, not by cleaning strings: the emitting stage must produce target + access path (+ conditions) bound to evidence ids.
